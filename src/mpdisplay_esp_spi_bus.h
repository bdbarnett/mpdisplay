/*
 * Copyright (c) 2023 Russ Hughes
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

#ifndef __mpdisplay_spi_bus_H__
#define __mpdisplay_spi_bus_H__

#include "py/obj.h"
#include "esp_lcd_panel_io.h"

// Fix for MicroPython > 1.21 https://github.com/ricksorensen
#if MICROPY_VERSION_MAJOR >= 1 && MICROPY_VERSION_MINOR > 21
#include "extmod/modmachine.h"
#else
#include "extmod/machine_spi.h"
#endif


// spi Configuration

typedef struct _mpdisplay_spi_bus_obj_t {
    mp_obj_base_t base;                     // base class
    char *name;                             // name of the display
    int spi_host;                           // SPI host
    spi_bus_config_t bus_config;  // bus configuration
    esp_lcd_panel_io_spi_config_t io_config;    // IO configuration
    esp_lcd_panel_io_handle_t io_handle;    // IO handle
} mpdisplay_spi_bus_obj_t;

extern const mp_obj_type_t mpdisplay_spi_bus_type;

#endif /* __spi_bus_H__ */
