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

#include "esp_lcd_types.h"
#include "esp_lcd_panel_commands.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_vendor.h"
#include "esp_lcd_panel_ops.h"

#include "py/obj.h"
#include "py/runtime.h"

#include "py/stackctrl.h"
#include "py/gc.h"

#include "mpdisplay.h"

// Fix for MicroPython > 1.21 https://github.com/ricksorensen
#if MICROPY_VERSION_MAJOR >= 1 && MICROPY_VERSION_MINOR > 21
#include "extmod/modmachine.h"
#else
#include "extmod/machine_spi.h"
#endif

// flag to indicate an esp_lcd_panel_draw_bitmap operation is in progress
STATIC volatile bool lcd_panel_active = false;

// cb_isr function taken directly from:
// https://github.com/lvgl/lv_binding_micropython/blob/master/driver/esp32/espidf.c
// Requires CONFIG_FREERTOS_INTERRUPT_BACKTRACE=n in sdkconfig
//
// Can't use mp_sched_schedule because lvgl won't yield to give micropython a chance to run
// Must run Micropython in ISR itself.
// Called in ISR context!
STATIC inline void cb_isr(mp_obj_t cb) { // removed mp_obj_t arg
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
            mp_call_function_0(cb);  // changed to mp_call_function_0 and removed the arg
            nlr_pop();
        } else {
            ets_printf("Uncaught exception in IRQ callback handler!\n");
            mp_obj_print_exception(&mp_plat_print, MP_OBJ_FROM_PTR(nlr.ret_val));  // changed to &mp_plat_print to fit this context
        }

        gc_unlock();
        mp_sched_unlock();

        mp_thread_set_state(old_state);

        mp_hal_wake_main_task_from_isr();
    }
}

// called when esp_lcd_panel_draw_bitmap is completed
STATIC bool lcd_panel_done(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_io_event_data_t *edata, void *user_ctx) {
//    mp_printf(&mp_plat_print, "Blit complete\n");
    mpdisplay_display_obj_t *self = (mpdisplay_display_obj_t *)user_ctx;
    lcd_panel_active = false;
    if (mp_obj_is_callable(self->ready_cb_func)) {
        // Call the registered callback
        cb_isr(self->ready_cb_func);
    }
    return false;
}

// transmit custom init_sequence
STATIC void custom_init(mpdisplay_display_obj_t *self) {
    size_t init_len;
    mp_obj_t *init_list;

    mp_obj_get_array(self->init_sequence, &init_len, &init_list);
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

/// .rotation(rotation)
/// Set the display rotation.
/// required parameters:
/// -- rotation: 0=Portrait, 1=Landscape, 2=Reverse Portrait (180), 3=Reverse Landscape (180)
mp_obj_t mpdisplay_display_rotation(mp_obj_t self_in, mp_obj_t value) {
    mpdisplay_display_obj_t *self = MP_OBJ_TO_PTR(self_in);

    if (value != mp_const_none) {
        mp_int_t rotation_val = mp_obj_get_int(value) % 4;
        self->rotation = rotation_val;
    }
    
    mpdisplay_display_rotation_t *rotation = &self->rotations[self->rotation % self->rotations_len];
    esp_lcd_panel_swap_xy(self->panel_handle, rotation->swap_xy);
    esp_lcd_panel_mirror(self->panel_handle, rotation->mirror_x, rotation->mirror_y);
    esp_lcd_panel_set_gap(self->panel_handle, rotation->x_gap, rotation->y_gap);

    self->width = rotation->width;
    self->height = rotation->height;

    return mp_const_none;
}

/// .blit(x, y, w, h, buf)
/// Send the buffer to the display.
/// required parameters:
///  -- x: start column
///  -- y: start row
///  -- w: width
///  -- h: height
///  -- buf: buffer
mp_obj_t mpdisplay_display_blit(size_t n_args, const mp_obj_t *args) {
    mpdisplay_display_obj_t *self = MP_OBJ_TO_PTR(args[0]);
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
    if (self->ready_cb_func == mp_const_none) { 
        while (lcd_panel_active) {
        }
    }
    return mp_const_none;
}

/// .init() (not exposed to Micropython)
/// Initialize the display, This method must be called before any other methods.
mp_obj_t mpdisplay_display_init(mp_obj_t self_in) {
    mpdisplay_display_obj_t *self = MP_OBJ_TO_PTR(self_in);

    if (mp_obj_is_type(self->bus, &mpdisplay_i80_bus_type)) {
        mpdisplay_i80_bus_obj_t *config = MP_OBJ_TO_PTR(self->bus);
        self->bus_handle.i80 = NULL;
        esp_lcd_i80_bus_config_t bus_config = {
            .dc_gpio_num = config->dc_gpio_num,
            .wr_gpio_num = config->wr_gpio_num,
            .clk_src = LCD_CLK_SRC_PLL160M, // same as default in IDF5 and 0 in the enum of IDF4.4
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
            .max_transfer_bytes = 1048576,
        };
        ESP_ERROR_CHECK(esp_lcd_new_i80_bus(&bus_config, &self->bus_handle.i80));

        esp_lcd_panel_io_handle_t io_handle = NULL;
        esp_lcd_panel_io_i80_config_t io_config = {
            .cs_gpio_num = config->cs_gpio_num,
            .pclk_hz = config->pclk_hz,
            .trans_queue_depth = 1,
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
        spi_bus_config_t buscfg = {
            .sclk_io_num = config->sclk_io_num,
            .mosi_io_num = config->mosi_io_num,
            .miso_io_num = -1,
            .quadwp_io_num = -1,
            .quadhd_io_num = -1,
            .max_transfer_sz = 0,
        };
        ESP_ERROR_CHECK(spi_bus_initialize(config->spi_host, &buscfg, SPI_DMA_CH_AUTO));
        esp_lcd_panel_io_handle_t io_handle = NULL;
        esp_lcd_panel_io_spi_config_t io_config = {
            .dc_gpio_num = config->dc_gpio_num,
            .cs_gpio_num = config->cs_gpio_num,
            .pclk_hz = config->pclk_hz,
            .spi_mode = 0,
            .trans_queue_depth = 1,
            .lcd_cmd_bits = config->lcd_cmd_bits,
            .lcd_param_bits = config->lcd_param_bits,
            .on_color_trans_done = lcd_panel_done,
            .user_ctx = self,
#if ESP_IDF_VERSION < ESP_IDF_VERSION_VAL(5, 0, 0)
            .flags.dc_as_cmd_phase = config->flags.dc_as_cmd_phase,
#endif
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
        .bits_per_pixel = self->bpp,
#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
        .rgb_ele_order = (self->bgr ? LCD_RGB_ELEMENT_ORDER_BGR : LCD_RGB_ELEMENT_ORDER_RGB), // IDF-v5.1
//        .data_endian = (self->swap_color_bytes ? LCD_RGB_DATA_ENDIAN_BIG : LCD_RGB_DATA_ENDIAN_LITTLE), // No equivalent before IDF-v5.0
#else
        .color_space = (self->bgr ? ESP_LCD_COLOR_SPACE_BGR : ESP_LCD_COLOR_SPACE_RGB)  // IDF-v4.4
#endif
    };

    ESP_ERROR_CHECK(esp_lcd_new_panel_st7789(self->io_handle, &panel_config, &panel_handle));
    self->panel_handle = panel_handle;

    esp_lcd_panel_reset(panel_handle);
    if (self->init_sequence == mp_const_none) {
        esp_lcd_panel_init(panel_handle);
#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
        esp_lcd_panel_disp_on_off(panel_handle,true); //switch lcd on, not longer a part of init
#endif
    } else {
        custom_init(self);
    }
    esp_lcd_panel_invert_color(panel_handle, self->invert_color);
    mpdisplay_display_rotation(self, mp_const_none);

    // esp_lcd_panel_io_tx_param(self->io_handle, 0x13, NULL, 0);

    return mp_const_none;
}

/// .deinit()
/// Deinitialize the mpdisplay object and frees allocated memory.
mp_obj_t mpdisplay_display_deinit(mp_obj_t self_in) {
    mpdisplay_display_obj_t *self = MP_OBJ_TO_PTR(self_in);

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

/// .allocate_buffer(size, cap)
/// Create a buffer using heap_caps_malloc and return it as a bytearray
/// required parameters:
///  -- size: size of buffer
/// optional parameters:
///  -- caps: DMA capability (default=MALLOC_CAP_DMA)
mp_obj_t mpdisplay_allocate_buffer(size_t n_args, const mp_obj_t *args) {
    mp_int_t size = mp_obj_get_int(args[0]);
    mp_int_t caps = (n_args == 2) ? mp_obj_get_int(args[1]) : MALLOC_CAP_DMA;

//    if (size > 65536) {
    if (false) {
        mp_raise_msg(&mp_type_OSError, MP_ERROR_TEXT("Buffer size too large. Must be <= 65536."));
    }
    void* buffer = heap_caps_malloc(size, caps);
    if (buffer == NULL) {
        mp_raise_msg(&mp_type_OSError, MP_ERROR_TEXT("Failed to allocate DMA buffer"));
    }
    memset(buffer, 0xFF, size);
//    return mp_obj_new_memoryview(1, size, buffer); // TypeError: 'memoryview' object doesn't support item assignment
    return mp_obj_new_bytearray_by_ref(size, buffer); // needs to return a memoryview instead of bytearray
}

/// .CAPS
STATIC const mp_rom_map_elem_t mpdisplay_caps_locals_dict_table[] = {
    // DMA capabilities from esp_heap_caps.h
    {MP_ROM_QSTR(MP_QSTR_EXEC), MP_ROM_INT(MALLOC_CAP_EXEC)},
    {MP_ROM_QSTR(MP_QSTR_32BIT), MP_ROM_INT(MALLOC_CAP_32BIT)},
    {MP_ROM_QSTR(MP_QSTR_8BIT), MP_ROM_INT(MALLOC_CAP_8BIT)},
    {MP_ROM_QSTR(MP_QSTR_DMA), MP_ROM_INT(MALLOC_CAP_DMA)},
    {MP_ROM_QSTR(MP_QSTR_SPIRAM), MP_ROM_INT(MALLOC_CAP_SPIRAM)},
    {MP_ROM_QSTR(MP_QSTR_INTERNAL), MP_ROM_INT(MALLOC_CAP_INTERNAL)},
    {MP_ROM_QSTR(MP_QSTR_DEFAULT), MP_ROM_INT(MALLOC_CAP_DEFAULT)},
    {MP_ROM_QSTR(MP_QSTR_IRAM_8BIT), MP_ROM_INT(MALLOC_CAP_IRAM_8BIT)},
    {MP_ROM_QSTR(MP_QSTR_RETENTION), MP_ROM_INT(MALLOC_CAP_RETENTION)},
    {MP_ROM_QSTR(MP_QSTR_RTCRAM), MP_ROM_INT(MALLOC_CAP_RTCRAM)},
};

STATIC MP_DEFINE_CONST_DICT(mpdisplay_caps_locals_dict, mpdisplay_caps_locals_dict_table);

MP_DEFINE_CONST_OBJ_TYPE(
    mpdisplay_caps_type,
    MP_QSTR_CAPS,
    MP_TYPE_FLAG_NONE,
    locals_dict, &mpdisplay_caps_locals_dict);
