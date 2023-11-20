/*
 * Modifications and additions Copyright (c) 2020-2023 Russ Hughes
 * Modifications and additions Copyright (c) 2023 Brad Barnett
 *
 * This file licensed under the MIT License and incorporates work covered by
 * the following copyright and permission notice:
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2019 Ivan Belokobylskiy
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <string.h>

#include "esp_err.h"

#include "esp_lcd_panel_commands.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_vendor.h"
#include "esp_lcd_panel_ops.h"

#include "py/obj.h"
#include "py/runtime.h"
#include "extmod/machine_spi.h"

#include "py/stackctrl.h"
#include "py/gc.h"

#include "mpdisplay.h"

//
// flag to indicate an esp_lcd_panel_draw_bitmap operation is in progress
//

STATIC volatile bool lcd_panel_active = false;

//
// EXPERIMENTAL - NOT WORKING YET
// a function and argument saved with .register_cb() to call from lcd_panel_done()
//

mp_obj_t ready_cb_func = mp_const_none;
mp_obj_t ready_cb_arg = mp_const_none;

///
/// .reset()
/// Reset the display.
///

mp_obj_t mpdisplay_display_reset(mp_obj_t self_in) {
    mpdisplay_obj_t *self = MP_OBJ_TO_PTR(self_in);
    esp_lcd_panel_reset(self->panel_handle);
    return mp_const_none;
}

///
/// .inversion_mode(value)
/// Set inversion mode
/// required parameters:
/// -- value: True to enable inversion mode, False to disable.
///

mp_obj_t mpdisplay_display_inversion_mode(mp_obj_t self_in, mp_obj_t value) {
    mpdisplay_obj_t *self = MP_OBJ_TO_PTR(self_in);
    self->inversion_mode = mp_obj_is_true(value);
    esp_lcd_panel_invert_color(self->panel_handle, self->inversion_mode);
    return mp_const_none;
}

//
// set rotation
//

STATIC void set_rotation(mpdisplay_obj_t *self) {
    mpdisplay_display_rotation_t *rotation = &self->rotations[self->rotation % self->rotations_len];
    esp_lcd_panel_swap_xy(self->panel_handle, rotation->swap_xy);
    esp_lcd_panel_mirror(self->panel_handle, rotation->mirror_x, rotation->mirror_y);
    esp_lcd_panel_set_gap(self->panel_handle, rotation->x_gap, rotation->y_gap);

    self->width = rotation->width;
    self->height = rotation->height;
}

///
/// .rotation(rotation)
/// Set the display rotation.
/// required parameters:
/// -- rotation: 0=Portrait, 1=Landscape, 2=Reverse Portrait (180), 3=Reverse Landscape (180)
///

mp_obj_t mpdisplay_display_rotation(mp_obj_t self_in, mp_obj_t value) {
    mpdisplay_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_int_t rotation = mp_obj_get_int(value) % 4;

    self->rotation = rotation;
    set_rotation(self);
    return mp_const_none;
}

///
/// .get_buf(size)
/// Create a buffer using heap_caps_malloc and return it as a bytearray
/// required parameters:
///  -- size: size of buffer
///

mp_obj_t mpdisplay_display_get_buf(mp_obj_t self_in, mp_obj_t size_in) {
//    mpdisplay_obj_t *self = MP_OBJ_TO_PTR(self_in);
    size_t size = (size_t)mp_obj_get_int(size_in);
    void* buffer = heap_caps_malloc(size, MALLOC_CAP_DMA);
    if (buffer == NULL) {
        mp_raise_msg(&mp_type_OSError, MP_ERROR_TEXT("Failed to allocate DMA buffer"));
    }
    memset(buffer, rand()&0xFF, size);
    return mp_obj_new_bytearray_by_ref(size, buffer);
}

///
/// .blit(x, y, w, h, buf)
/// Send the buffer to the display.
/// required parameters:
///  -- x: start column
///  -- y: start row
///  -- w: width
///  -- h: height
///  -- buf: buffer
///

mp_obj_t mpdisplay_display_blit(size_t n_args, const mp_obj_t *args) {
    mpdisplay_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    mp_int_t x = mp_obj_get_int(args[1]);
    mp_int_t y = mp_obj_get_int(args[2]);
    mp_int_t w = mp_obj_get_int(args[3]);
    mp_int_t h = mp_obj_get_int(args[4]);
    mp_buffer_info_t buf_info;
    mp_get_buffer_raise(args[5], &buf_info, MP_BUFFER_READ);
    u_int16_t *buf = buf_info.buf;

    lcd_panel_active = true;
//    mp_printf(&mp_plat_print, "Blitting: x_start=%u, y_start=%u, x_end=%u, y_end=%u, len=%u\n", x, y, x + w, y + h, buf_info.len);
    esp_lcd_panel_draw_bitmap(self->panel_handle, x, y, x + w, y + h, buf);
    // if ready_cb_func wasn't registered, wait for esp_lcd_panel_draw_bitmap to complete.
    // esp_lcd_panel_draw_bitmap calls lcd_panel_done when complete, which sets lcd_panel_active = False
    // and calls ready_cb_func if it is registered.  SEE cb_isr COMMENTS BELOW!!!!
    if (ready_cb_func == mp_const_none) { 
        while (lcd_panel_active) {
        }
    }
    return mp_const_none;
}

//
// !!!!!!!NOT WORKING, NOT WORKING, NOT WORKING!!!!!!!
// ! It never calls the callback as intended.  Left here for future development.
//
// The following cb_isr function is taken directly from 
// https://github.com/lvgl/lv_binding_micropython/blob/master/driver/esp32/espidf.c
// Requires CONFIG_FREERTOS_INTERRUPT_BACKTRACE=n in sdkconfig
//
// Can't use mp_sched_schedule because lvgl won't yield to give micropython a chance to run
// Must run Micropython in ISR itself.
// Called in ISR context!
//

STATIC inline void cb_isr(mp_obj_t cb, mp_obj_t arg) {
    if (cb != NULL && cb != mp_const_none) {

        volatile uint32_t sp = (uint32_t)get_sp();

        // Calling micropython from ISR
        // See: https://github.com/micropython/micropython/issues/4895

        void *old_state = mp_thread_get_state();

        mp_state_thread_t ts; // local thread state for the ISR
        mp_thread_set_state(&ts);
        mp_stack_set_top((void*)sp); // need to include in root-pointer scan
        mp_stack_set_limit(configIDLE_TASK_STACK_SIZE - 1024); // tune based on ISR thread stack size
        mp_locals_set(mp_state_ctx.thread.dict_locals); // use main thread's locals
        mp_globals_set(mp_state_ctx.thread.dict_globals); // use main thread's globals

        mp_sched_lock(); // prevent VM from switching to another MicroPython thread
        gc_lock(); // prevent memory allocation

        nlr_buf_t nlr;
        if (nlr_push(&nlr) == 0) {
            mp_call_function_1(cb, arg);
            nlr_pop();
        } else {
            ets_printf("Uncaught exception in IRQ callback handler!\n");
            mp_obj_print_exception(&mp_plat_print, MP_OBJ_FROM_PTR(nlr.ret_val));  // changed first parameter to fit this context
        }

        gc_unlock();
        mp_sched_unlock();

        mp_thread_set_state(old_state);

        mp_hal_wake_main_task_from_isr();
    }
}

//
// called when esp_lcd_panel_draw_bitmap is completed
//

STATIC bool lcd_panel_done(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_io_event_data_t *edata, void *user_ctx) {
//    mp_printf(&mp_plat_print, "Blit complete\n");
    lcd_panel_active = false;
    if (mp_obj_is_callable(ready_cb_func)) {
        // WARNING:  This isn't working!  Hangs or crashes!
        // Call the registered callback with argument
        cb_isr(ready_cb_func, ready_cb_arg);
    }
    return false;
}

//
// run custom_init
//

STATIC void custom_init(mpdisplay_obj_t *self) {
    size_t init_len;
    mp_obj_t *init_list;

    mp_obj_get_array(self->custom_init, &init_len, &init_list);
    for (int idx = 0; idx < init_len; idx++) {
        size_t init_cmd_len;
        mp_obj_t *init_cmd;
        mp_obj_get_array(init_list[idx], &init_cmd_len, &init_cmd);
        mp_buffer_info_t init_cmd_data_info;
        if (mp_get_buffer(init_cmd[0], &init_cmd_data_info, MP_BUFFER_READ)) {
            uint8_t *init_cmd_data = (uint8_t *)init_cmd_data_info.buf;
            if (init_cmd_data_info.len > 1) {
                esp_lcd_panel_io_tx_param(self->io_handle, init_cmd_data[0], &init_cmd_data[1], init_cmd_data_info.len - 1);
            } else {
                esp_lcd_panel_io_tx_param(self->io_handle, init_cmd_data[0], NULL, 0);
            }
            mp_hal_delay_ms(10);
            // check for delay
            if (init_cmd_len > 1) {
                mp_int_t delay = mp_obj_get_int(init_cmd[1]);
                if (delay > 0) {
                    mp_hal_delay_ms(delay);
                }
            }
        }
    }
}

///
/// .init()
/// Initialize the display, This method must be called before any other methods.
///

mp_obj_t mpdisplay_display_init(mp_obj_t self_in) {
    mpdisplay_obj_t *self = MP_OBJ_TO_PTR(self_in);

    if (mp_obj_is_type(self->bus, &mpdisplay_i80_bus_type)) {
        mpdisplay_i80_bus_obj_t *config = MP_OBJ_TO_PTR(self->bus);
        self->swap_color_bytes = false;
        self->bus_handle.i80 = NULL;
        esp_lcd_i80_bus_config_t bus_config = {
            .dc_gpio_num = config->dc_gpio_num,
            .wr_gpio_num = config->wr_gpio_num,
            .data_gpio_nums = {
                config->data_gpio_nums[0],
                config->data_gpio_nums[1],
                config->data_gpio_nums[2],
                config->data_gpio_nums[3],
                config->data_gpio_nums[4],
                config->data_gpio_nums[5],
                config->data_gpio_nums[6],
                config->data_gpio_nums[7],
            },
            .bus_width = config->bus_width,
            .max_transfer_bytes = 65536,
        };
        ESP_ERROR_CHECK(esp_lcd_new_i80_bus(&bus_config, &self->bus_handle.i80));

        esp_lcd_panel_io_handle_t io_handle = NULL;
        esp_lcd_panel_io_i80_config_t io_config = {
            .cs_gpio_num = config->cs_gpio_num,
            .pclk_hz = config->pclk_hz,
            .trans_queue_depth = 10,
            .on_color_trans_done = lcd_panel_done,
            .user_ctx = self,
            .dc_levels = {
                .dc_idle_level = config->dc_levels.dc_idle_level,
                .dc_cmd_level = config->dc_levels.dc_cmd_level,
                .dc_dummy_level = config->dc_levels.dc_dummy_level,
                .dc_data_level = config->dc_levels.dc_data_level,
            },
            .lcd_cmd_bits = config->lcd_cmd_bits,
            .lcd_param_bits = config->lcd_param_bits,
            .flags = {
                .cs_active_high = config->flags.cs_active_high,
                .reverse_color_bits = config->flags.reverse_color_bits,
                .swap_color_bytes = config->flags.swap_color_bytes,
                .pclk_active_neg = config->flags.pclk_active_neg,
                .pclk_idle_low = config->flags.pclk_idle_low,
            }
        };

        ESP_ERROR_CHECK(esp_lcd_new_panel_io_i80(self->bus_handle.i80, &io_config, &io_handle));
        self->io_handle = io_handle;
    } else if (mp_obj_is_type(self->bus, &mpdisplay_spi_bus_type)) {
         mpdisplay_spi_bus_obj_t *config = MP_OBJ_TO_PTR(self->bus);
        self->swap_color_bytes = config->flags.swap_color_bytes;
        spi_bus_config_t buscfg = {
            .sclk_io_num = config->sclk_io_num,
            .mosi_io_num = config->mosi_io_num,
            .miso_io_num = -1,
            .quadwp_io_num = -1,
            .quadhd_io_num = -1,
            .max_transfer_sz = 65536,
        };
        ESP_ERROR_CHECK(spi_bus_initialize(config->spi_host, &buscfg, SPI_DMA_CH_AUTO));
        esp_lcd_panel_io_handle_t io_handle = NULL;
        esp_lcd_panel_io_spi_config_t io_config = {
            .dc_gpio_num = config->dc_gpio_num,
            .cs_gpio_num = config->cs_gpio_num,
            .pclk_hz = config->pclk_hz,
            .spi_mode = 0,
            .trans_queue_depth = 10,
            .lcd_cmd_bits = config->lcd_cmd_bits,
            .lcd_param_bits = config->lcd_param_bits,
            .on_color_trans_done = lcd_panel_done,
            .user_ctx = self,
            .flags.dc_as_cmd_phase = config->flags.dc_as_cmd_phase,
            .flags.dc_low_on_data = config->flags.dc_low_on_data,
            .flags.octal_mode =config->flags.octal_mode,
            .flags.lsb_first = config->flags.lsb_first
        };

        ESP_ERROR_CHECK(esp_lcd_new_panel_io_spi((esp_lcd_spi_bus_handle_t)config->spi_host, &io_config, &io_handle));
        self->io_handle = io_handle;
    }

    esp_lcd_panel_handle_t panel_handle = NULL;
    esp_lcd_panel_dev_config_t panel_config = {
        .reset_gpio_num = self->rst,
        .bits_per_pixel = 16,
    };

    ESP_ERROR_CHECK(esp_lcd_new_panel_st7789(self->io_handle, &panel_config, &panel_handle));
    self->panel_handle = panel_handle;

    esp_lcd_panel_reset(panel_handle);
    if (self->custom_init == MP_OBJ_NULL) {
        esp_lcd_panel_init(panel_handle);
    } else {
        custom_init(self);
    }
    esp_lcd_panel_invert_color(panel_handle, self->inversion_mode);
    set_rotation(self);

    // esp_lcd_panel_io_tx_param(self->io_handle, 0x13, NULL, 0);

    return mp_const_none;
}

///
/// .deinit()
/// Deinitialize the mpdisplay object and frees allocated memory.
///

mp_obj_t mpdisplay_display_deinit(mp_obj_t self_in) {
    mpdisplay_obj_t *self = MP_OBJ_TO_PTR(self_in);

    esp_lcd_panel_del(self->panel_handle);
    self->panel_handle = NULL;

    esp_lcd_panel_io_del(self->io_handle);
    self->io_handle = NULL;

    if (mp_obj_is_type(self->bus, &mpdisplay_i80_bus_type)) {
        esp_lcd_del_i80_bus(self->bus_handle.i80);
        self->bus_handle.i80 = NULL;
    } else if (mp_obj_is_type(self->bus, &mpdisplay_spi_bus_type)) {
        mpdisplay_spi_bus_obj_t *config = MP_OBJ_TO_PTR(self->bus);
        spi_bus_free(config->spi_host);
        self->bus_handle.spi = NULL;
    }

    return mp_const_none;
}
