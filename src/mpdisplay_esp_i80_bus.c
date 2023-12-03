#include "py/obj.h"
#include "py/runtime.h"

#include "mpdisplay_esp.h"
#include "mpdisplay_esp_i80_bus.h"

// i80_bus_print
STATIC void mpdisplay_i80_bus_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind) {
    (void) kind;
    mpdisplay_i80_bus_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_printf(print, "%s((<data_gpio_nums>), dc=%d, wr=%d, cs=%d, pclk=%d, lcd_cmd_bits=%d, lcd_param_bits=%d, dc_idle_level=%d, dc_cmd_level=%d, dc_dummy_level=%d, dc_data_level=%d, cs_active_high=%d, reverse_color_bits=%d, swap_color_bytes=%d, pclk_active_neg=%d, pclk_idle_low=%d)",
        self->name,
        self->bus_config.dc_gpio_num,
        self->bus_config.wr_gpio_num,
        self->io_config.cs_gpio_num,
        self->io_config.pclk_hz,
        self->io_config.lcd_cmd_bits,
        self->io_config.lcd_param_bits,
        self->io_config.dc_levels.dc_idle_level,
        self->io_config.dc_levels.dc_cmd_level,
        self->io_config.dc_levels.dc_dummy_level,
        self->io_config.dc_levels.dc_data_level,
        self->io_config.flags.cs_active_high,
        self->io_config.flags.reverse_color_bits,
        self->io_config.flags.swap_color_bytes,
        self->io_config.flags.pclk_active_neg,
        self->io_config.flags.pclk_idle_low
    );
}

/// i80_bus
/// Configure a i8080 parallel bus.
///
/// Parameters:
///   - data: tuple list of data pins
///   - dc: data/command pin number
///   - wr: write pin number
///   - cs: chip select pin number
///   - pclk: pixel clock frequency in Hz
///   - bus_width: bus width in bits
///   - lcd_cmd_bits: number of bits used to send commands to the LCD
///   - lcd_param_bits: number of bits used to send parameters to the LCD
///   - dc_idle_level: data/command pin level when idle
///   - dc_cmd_level: data/command pin level when sending commands
///   - dc_dummy_level: data/command pin level when sending dummy data
///   - dc_data_level: data/command pin level when sending data
///   - cs_active_high: chip select pin level when active
///   - reverse_color_bits: reverse the order of color bits
///   - swap_color_bytes: swap the order of color bytes
///   - pclk_active_neg: pixel clock is active negative
///   - pclk_idle_low: pixel clock is idle low
STATIC mp_obj_t mpdisplay_i80_bus_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args) {
    enum {
        ARG_data,
        ARG_dc,
        ARG_wr,
        ARG_cs,
        ARG_pclk,
        ARG_lcd_cmd_bits,
        ARG_lcd_param_bits,
        ARG_dc_idle_level,
        ARG_dc_cmd_level,
        ARG_dc_dummy_level,
        ARG_dc_data_level,
        ARG_cs_active_high,
        ARG_reverse_color_bits,
        ARG_swap_color_bytes,
        ARG_pclk_active_neg,
        ARG_pclk_idle_low,
    };

    STATIC const mp_arg_t allowed_args[] = {
        { MP_QSTR_data,                 MP_ARG_OBJ  | MP_ARG_REQUIRED                      },
        { MP_QSTR_dc,                   MP_ARG_INT  | MP_ARG_REQUIRED                      },
        { MP_QSTR_wr,                   MP_ARG_INT  | MP_ARG_REQUIRED                      },
        { MP_QSTR_cs,                   MP_ARG_INT  | MP_ARG_KW_ONLY, {.u_int = -1       } },
        { MP_QSTR_pclk,                 MP_ARG_INT  | MP_ARG_KW_ONLY, {.u_int = 10000000 } },
        { MP_QSTR_lcd_cmd_bits,         MP_ARG_INT  | MP_ARG_KW_ONLY, {.u_int = 8        } },
        { MP_QSTR_lcd_param_bits,       MP_ARG_INT  | MP_ARG_KW_ONLY, {.u_int = 8        } },
        { MP_QSTR_dc_idle_level,        MP_ARG_INT  | MP_ARG_KW_ONLY, {.u_int = 0        } },
        { MP_QSTR_dc_cmd_level,         MP_ARG_INT  | MP_ARG_KW_ONLY, {.u_int = 0        } },
        { MP_QSTR_dc_dummy_level,       MP_ARG_INT  | MP_ARG_KW_ONLY, {.u_int = 0        } },
        { MP_QSTR_dc_data_level,        MP_ARG_INT  | MP_ARG_KW_ONLY, {.u_int = 1        } },
        { MP_QSTR_cs_active_high,       MP_ARG_BOOL | MP_ARG_KW_ONLY, {.u_bool = false   } },
        { MP_QSTR_reverse_color_bits,   MP_ARG_BOOL | MP_ARG_KW_ONLY, {.u_bool = false   } },
        { MP_QSTR_swap_color_bytes,     MP_ARG_BOOL | MP_ARG_KW_ONLY, {.u_int = 0        } },
        { MP_QSTR_pclk_active_neg,      MP_ARG_BOOL | MP_ARG_KW_ONLY, {.u_bool = false   } },
        { MP_QSTR_pclk_idle_low,        MP_ARG_BOOL | MP_ARG_KW_ONLY, {.u_bool = false   } },
    };

    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    // create new i80 bus object
    mpdisplay_i80_bus_obj_t *self = m_new_obj(mpdisplay_i80_bus_obj_t);
    self->base.type = &mpdisplay_i80_bus_type;
    self->name = "mpdisplay.I80_bus";

    // data gpio numbers from tuple
    mp_obj_tuple_t *data_gpio_nums = MP_OBJ_TO_PTR(args[ARG_data].u_obj);
    int bus_width = data_gpio_nums->len;
    if (bus_width < 8) {
        mp_raise_ValueError(MP_ERROR_TEXT("too few data pins"));
    }
    if (bus_width > SOC_LCD_I80_BUS_WIDTH) {
        mp_raise_ValueError(MP_ERROR_TEXT("too many data pins"));
    }
    if (bus_width % 8 != 0) {
        mp_raise_ValueError(MP_ERROR_TEXT("data pins must be a multiple of 8"));
    }

    // create i80 bus config
    esp_lcd_i80_bus_config_t bus_config = {
        .dc_gpio_num = args[ARG_dc].u_int,
        .wr_gpio_num = args[ARG_wr].u_int,
        .clk_src = LCD_CLK_SRC_PLL160M, // same as default in IDF5 and 0 in the enum of IDF4.4
        .bus_width = bus_width,
        //  What is the impact if max_transfer_bytes is arbitrarily large?
        .max_transfer_bytes = 1048576, // "this determines the length of internal DMA link"
    };
    for (size_t i = 0; i < SOC_LCD_I80_BUS_WIDTH; i++) {
        bus_config.data_gpio_nums[i] = (i < bus_width) ? mp_obj_get_int(data_gpio_nums->items[i]) : -1;
    }
    self->bus_config = bus_config;

    // create i80 bus handle
    esp_lcd_i80_bus_handle_t bus_handle = NULL;
    ESP_ERROR_CHECK(esp_lcd_new_i80_bus(&bus_config, &bus_handle));
    self->bus_handle = bus_handle;

    // create i80 panel io config
    esp_lcd_panel_io_i80_config_t io_config = {
        .cs_gpio_num = args[ARG_cs].u_int,
        .pclk_hz = args[ARG_pclk].u_int,
        .trans_queue_depth = 1,
        .on_color_trans_done = lcd_panel_done,
        .user_ctx = self,
        .dc_levels = {
            .dc_idle_level = args[ARG_dc_idle_level].u_int,
            .dc_cmd_level = args[ARG_dc_cmd_level].u_int,
            .dc_dummy_level = args[ARG_dc_dummy_level].u_int,
            .dc_data_level = args[ARG_dc_data_level].u_int,
        },
        .lcd_cmd_bits = args[ARG_lcd_cmd_bits].u_int,
        .lcd_param_bits = args[ARG_lcd_param_bits].u_int,
        .flags = {
            .cs_active_high = args[ARG_cs_active_high].u_bool,
            .reverse_color_bits = args[ARG_reverse_color_bits].u_bool,
            .swap_color_bytes = args[ARG_swap_color_bytes].u_bool,
            .pclk_active_neg = args[ARG_pclk_active_neg].u_bool,
            .pclk_idle_low = args[ARG_pclk_idle_low].u_bool,
        }
    };
    self->io_config = io_config;

    // create i80 panel io handle
    esp_lcd_panel_io_handle_t io_handle = NULL;
    ESP_ERROR_CHECK(esp_lcd_new_panel_io_i80(bus_handle, &io_config, &io_handle));
    self->io_handle = io_handle;
   
    return MP_OBJ_FROM_PTR(self);
}

/// i80_bus_deinit
/// Deinitialize the i80 bus.
STATIC mp_obj_t mpdisplay_i80_bus_deinit(mp_obj_t self_in) {
    mpdisplay_i80_bus_obj_t *self = MP_OBJ_TO_PTR(self_in);
    esp_lcd_panel_io_del(self->io_handle);
    esp_lcd_del_i80_bus(self->bus_handle);
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mpdisplay_i80_bus_deinit_obj, mpdisplay_i80_bus_deinit);

// locals_dict
STATIC const mp_rom_map_elem_t mpdisplay_i80_bus_locals_dict_table[] = {
    {MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&mpdisplay_i80_bus_deinit_obj)},
};
STATIC MP_DEFINE_CONST_DICT(mpdisplay_i80_bus_locals_dict, mpdisplay_i80_bus_locals_dict_table);

#if MICROPY_OBJ_TYPE_REPR == MICROPY_OBJ_TYPE_REPR_SLOT_INDEX

MP_DEFINE_CONST_OBJ_TYPE(
    mpdisplay_i80_bus_type,
    MP_QSTR_I80_bus,
    MP_TYPE_FLAG_NONE,
    print, mpdisplay_i80_bus_print,
    make_new, mpdisplay_i80_bus_make_new,
    locals_dict, &mpdisplay_i80_bus_locals_dict);

#else

const mp_obj_type_t mpdisplay_type = {
    {&mp_type_type},
    .name = MP_QSTR_I80_BUS,
    .print = mpdisplay_print,
    .make_new = mpdisplay_make_new,
    .locals_dict = (mp_obj_dict_t *)&mpdisplay_i80_bus_locals_dict,
};

#endif
