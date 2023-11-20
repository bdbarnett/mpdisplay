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


#include "py/runtime.h"

#include "mpdisplay.h"
#include "mpdisplay_common.h"

//
// function called in place of Micropython's __repr__ dunder method
//

void mpdisplay_display_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind) {
    (void)kind;
    mpdisplay_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_printf(print, "Display(bus, width=%u, height=%u, rotation=%u)", self->width, self->height, self->rotation);
}

///
/// .width()
/// Returns the width of the display in pixels.
///

mp_obj_t mpdisplay_display_width(mp_obj_t self_in) {
    mpdisplay_obj_t *self = MP_OBJ_TO_PTR(self_in);
    return mp_obj_new_int(self->width);
}

///
/// .height()
/// Returns the height of the display in pixels.
///

mp_obj_t mpdisplay_display_height(mp_obj_t self_in) {
    mpdisplay_obj_t *self = MP_OBJ_TO_PTR(self_in);
    return mp_obj_new_int(self->height);
}

///
/// .register_cb(function, argument)
/// Register the ready callback function and argument to be called from lcd_panel_done()
/// e.g. function(argument)
/// required parameters:
/// -- function: called when blit is completed
/// -- argument: argument to function
///

mp_obj_t mpdisplay_display_register_cb(mp_obj_t self_in, mp_obj_t function, mp_obj_t argument) {
//    mpdisplay_obj_t *self = self_in;
    if (mp_obj_is_callable(function)) {
        ready_cb_func = function;
        ready_cb_arg = argument;
    } else {
        mp_raise_TypeError("Callback is not callable");
    }
    return mp_const_none;
}
