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

#include "mpdisplay_esp_i80_bus.h"
#include "mpdisplay_esp_spi_bus.h"

typedef union _bus_handle_t {
    esp_lcd_i80_bus_handle_t i80;
    esp_lcd_spi_bus_handle_t spi;
} bus_handle_t;

mp_obj_t ready_cb_func;
mp_obj_t ready_cb_arg;

mp_obj_t mpdisplay_display_reset(mp_obj_t self_in);
mp_obj_t mpdisplay_display_inversion_mode(mp_obj_t self_in, mp_obj_t value);
mp_obj_t mpdisplay_display_rotation(mp_obj_t self_in, mp_obj_t value);
mp_obj_t mpdisplay_display_get_buf(mp_obj_t self_in, mp_obj_t size_in);
mp_obj_t mpdisplay_display_blit(size_t n_args, const mp_obj_t *args);
mp_obj_t mpdisplay_display_init(mp_obj_t self_in);
mp_obj_t mpdisplay_display_deinit(mp_obj_t self_in);
