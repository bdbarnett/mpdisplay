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

#ifndef __mpdisplay_esp_H__
#define __mpdisplay_esp_H__

#include "py/obj.h"
#include "esp_lcd_panel_io.h"

mp_obj_t mpdisplay_display_rotation(mp_obj_t self_in, mp_obj_t value);
mp_obj_t mpdisplay_display_blit(size_t n_args, const mp_obj_t *args);
mp_obj_t mpdisplay_display_flush(size_t n_args, const mp_obj_t *args);
mp_obj_t mpdisplay_display_init(mp_obj_t self_in);
mp_obj_t mpdisplay_display_deinit(mp_obj_t self_in);

mp_obj_t mpdisplay_allocate_buffer(size_t n_args, const mp_obj_t *args);

extern const mp_obj_type_t mpdisplay_caps_type;

extern bool lcd_panel_done(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_io_event_data_t *edata, void *user_ctx);

#endif /* __mpdisplay_esp_H__ */
