#include "py/obj.h"
#include "py/runtime.h"

#include "mpdisplay_esp.h"
#include "mpdisplay_esp_spi_bus.h"

// spi_bus_print
STATIC void mpdisplay_spi_bus_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind) {
    (void) kind;
    mpdisplay_spi_bus_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_printf(print, "%s(sck=%d,mosi=%d, dc=%d, cs=%d, spi_mode=%d, pclk=%d, lcd_cmd_bits=%d, lcd_param_bits=%d, "
#if ESP_IDF_VERSION < ESP_IDF_VERSION_VAL(5, 0, 0)
        "dc_as_cmd_phase=%d, dc_low_on_data=%d, "

#endif
        "dc_low_on_data=%d, octal_mode=%d, lsb_first=%d)",

        self->name,
        self->bus_config.sclk_io_num,
        self->bus_config.mosi_io_num,
        self->io_config.dc_gpio_num,
        self->io_config.cs_gpio_num,
        self->io_config.spi_mode,
        self->io_config.pclk_hz,
        self->io_config.lcd_cmd_bits,
        self->io_config.lcd_param_bits,
#if ESP_IDF_VERSION < ESP_IDF_VERSION_VAL(5, 0, 0)
        self->io_config.flags.dc_as_cmd_phase,
#endif
        self->io_config.flags.dc_low_on_data,
        self->io_config.flags.octal_mode,
        self->io_config.flags.lsb_first
    );
}

/// spi_bus - Configure a SPI bus.
///
/// Parameters:
///   - spi_host: SPI host to use
///   - sclk: GPIO used for SCLK
///   - mosi: GPIO used for MOSI
///   - dc: GPIO used to select the D/C line, set this to -1 if the D/C line not controlled by manually pulling high/low GPIO
///   - cs: GPIO used for CS line
///   - spi_mode: Traditional SPI mode (0~3)
///   - pclk_hz: Frequency of pixel clock
///   - lcd_cmd_bits: Bit-width of LCD command
///   - lcd_param_bits: Bit-width of LCD parameter
///   - dc_idle_level: data/command pin level when idle
///   - dc_as_cmd_phase: D/C line value is encoded into SPI transaction command phase
///   - dc_low_on_data: If this flag is enabled, DC line = 0 means transfer data, DC line = 1 means transfer command; vice versa
///   - octal_mode: transmit with octal mode (8 data lines), this mode is used to simulate Intel 8080 timing
///   - lsb_first: transmit LSB bit first
STATIC mp_obj_t mpdisplay_spi_bus_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args) {
    enum {
        ARG_spi_host,           // SPI host to use
        ARG_sclk_io_num,        // GPIO used for SCLK
        ARG_mosi_io_num,        // GPIO used for MOSI
        ARG_dc,                 // GPIO used to select the D/C line, set this to -1 if the D/C line not controlled by manually pulling high/low GPIO
        ARG_cs,                 // GPIO used for CS line
        ARG_spi_mode,           // Traditional SPI mode (0~3)
        ARG_pclk_hz,            // Frequency of pixel clock
        ARG_lcd_cmd_bits,       // Bit-width of LCD command
        ARG_lcd_param_bits,     // Bit-width of LCD parameter
#if ESP_IDF_VERSION < ESP_IDF_VERSION_VAL(5, 0, 0)
        ARG_dc_as_cmd_phase,    // D/C line value is encoded into SPI transaction command phase
#endif
        ARG_dc_low_on_data,     // If this flag is enabled, DC line = 0 means transfer data, DC line = 1 means transfer command; vice versa
        ARG_octal_mode,         // transmit with octal mode (8 data lines), this mode is used to simulate Intel 8080 timing
        ARG_lsb_first,          // transmit LSB bit first
    };

    STATIC const mp_arg_t allowed_args[] = {
        { MP_QSTR_spi_host,         MP_ARG_INT  | MP_ARG_REQUIRED,                     },
        { MP_QSTR_sck,              MP_ARG_INT  | MP_ARG_REQUIRED,                     },
        { MP_QSTR_mosi,             MP_ARG_INT  | MP_ARG_REQUIRED,                     },
        { MP_QSTR_dc,               MP_ARG_INT  | MP_ARG_REQUIRED                      },
        { MP_QSTR_cs,               MP_ARG_INT  | MP_ARG_KW_ONLY, {.u_int = -1       } },
        { MP_QSTR_spi_mode,         MP_ARG_INT  | MP_ARG_KW_ONLY, {.u_int = 0        } },
        { MP_QSTR_pclk,             MP_ARG_INT  | MP_ARG_KW_ONLY, {.u_int = 20000000 } },
        { MP_QSTR_lcd_cmd_bits,     MP_ARG_INT  | MP_ARG_KW_ONLY, {.u_int = 8        } },
        { MP_QSTR_lcd_param_bits,   MP_ARG_INT  | MP_ARG_KW_ONLY, {.u_int = 8        } },
#if ESP_IDF_VERSION < ESP_IDF_VERSION_VAL(5, 0, 0)
        { MP_QSTR_dc_as_cmd_phase,  MP_ARG_INT  | MP_ARG_KW_ONLY, {.u_int = 0        } },
#endif
        { MP_QSTR_dc_low_on_data,   MP_ARG_INT  | MP_ARG_KW_ONLY, {.u_int = 0        } },
        { MP_QSTR_octal_mode,       MP_ARG_BOOL | MP_ARG_KW_ONLY, {.u_bool = false   } },
        { MP_QSTR_lsb_first,        MP_ARG_BOOL | MP_ARG_KW_ONLY, {.u_bool = false   } },
    };

    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    // create new spi_bus object
    mpdisplay_spi_bus_obj_t *self = m_new_obj(mpdisplay_spi_bus_obj_t);
    self->base.type = &mpdisplay_spi_bus_type;
    self->name = "mpdisplay.Spi_bus";

    self->spi_host = args[ARG_spi_host].u_int;

    // create spi bus config
    spi_bus_config_t bus_config = {
        .sclk_io_num = args[ARG_sclk_io_num].u_int,
        .mosi_io_num = args[ARG_mosi_io_num].u_int,
        .miso_io_num = -1,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 0,
    };
    self->bus_config = bus_config;

    // initialize spi bus
    ESP_ERROR_CHECK(spi_bus_initialize(self->spi_host, &bus_config, SPI_DMA_CH_AUTO));

    // create spi panel io config
    esp_lcd_panel_io_spi_config_t io_config = {
        .dc_gpio_num = args[ARG_dc].u_int,
        .cs_gpio_num = args[ARG_cs].u_int,
        .pclk_hz = args[ARG_pclk_hz].u_int,
        .spi_mode = args[ARG_spi_mode].u_int,
        .trans_queue_depth = 1,
        .lcd_cmd_bits = args[ARG_lcd_cmd_bits].u_int,
        .lcd_param_bits = args[ARG_lcd_param_bits].u_int,
        .on_color_trans_done = lcd_panel_done,
        .user_ctx = self,
#if ESP_IDF_VERSION < ESP_IDF_VERSION_VAL(5, 0, 0)
        .flags.dc_as_cmd_phase = args[ARG_dc_as_cmd_phase].u_int,
#endif
        .flags.dc_low_on_data = args[ARG_dc_low_on_data].u_int,
        .flags.octal_mode = args[ARG_octal_mode].u_int,
        .flags.lsb_first = args[ARG_lsb_first].u_bool
    };
    self->io_config = io_config;

    // create spi panel io handle
    esp_lcd_panel_io_handle_t io_handle = NULL;
    ESP_ERROR_CHECK(esp_lcd_new_panel_io_spi((esp_lcd_spi_bus_handle_t)self->spi_host, &io_config, &io_handle));
    self->io_handle = io_handle;

    return MP_OBJ_FROM_PTR(self);
}

/// spi_bus.deinit() - Deinitialize the SPI bus.
STATIC mp_obj_t mpdisplay_spi_bus_deinit(mp_obj_t self_in) {
    mpdisplay_spi_bus_obj_t *self = MP_OBJ_TO_PTR(self_in);
    esp_lcd_panel_io_del(self->io_handle);
    spi_bus_free(self->spi_host);
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mpdisplay_spi_bus_deinit_obj, mpdisplay_spi_bus_deinit);

STATIC const mp_rom_map_elem_t mpdisplay_spi_bus_locals_dict_table[] = {
    {MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&mpdisplay_spi_bus_deinit_obj)},
};
STATIC MP_DEFINE_CONST_DICT(mpdisplay_spi_bus_locals_dict, mpdisplay_spi_bus_locals_dict_table);

#if MICROPY_OBJ_TYPE_REPR == MICROPY_OBJ_TYPE_REPR_SLOT_INDEX

MP_DEFINE_CONST_OBJ_TYPE(
    mpdisplay_spi_bus_type,
    MP_QSTR_SPI_BUS,
    MP_TYPE_FLAG_NONE,
    print, mpdisplay_spi_bus_print,
    make_new, mpdisplay_spi_bus_make_new,
    locals_dict, &mpdisplay_spi_bus_locals_dict);

#else

const mp_obj_type_t mpdisplay_spi_bus_type = {
    {&mp_type_type},
    .name = MP_QSTR_SPI_BUS,
    .print = mpdisplay_spi_bus_print,
    .make_new = mpdisplay_spi_bus_make_new,
    .locals_dict = (mp_obj_dict_t *)&mpdisplay_spi_bus_locals_dict,
};

#endif