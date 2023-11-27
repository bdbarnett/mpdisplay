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

#include "py/obj.h"
#include "py/runtime.h"

#include "mpdisplay.h"

// Default mpdisplay display orientation tables
// can be overridden during init()
//
// typedef struct _mpdisplay_display_rotation_t {
//     uint16_t width;     // width of the display in this rotation
//     uint16_t height;    // height of the display in this rotation
//     uint16_t x_gap;     // gap on x axis, in pixels
//     uint16_t y_gap;     // gap on y axis, in pixels
//     bool swap_xy;       // set MADCTL_MV bit 0x20
//     bool mirror_x;      // set MADCTL MX bit 0x40
//     bool mirror_y;      // set MADCTL MY bit 0x80
// } mpdisplay_display_rotation_t;
//
// { width, height, x_gap, y_gap, swap_xy, mirror_x, mirror_y }

mpdisplay_display_rotation_t ROTATIONS_320x480[4] = {
    {320, 480, 0, 0, false, true,  false},
    {480, 320, 0, 0, true,  false, false},
    {320, 480, 0, 0, false, false, true},
    {480, 320, 0, 0, true,  true,  true}
};

mpdisplay_display_rotation_t ROTATIONS_240x320[4] = {
    {240, 320, 0, 0, false, false, false},
    {320, 240, 0, 0, true,  true,  false},
    {240, 320, 0, 0, false, true,  true},
    {320, 240, 0, 0, true,  false, true}
};

mpdisplay_display_rotation_t ROTATIONS_170x320[4] = {
    {170, 320, 35, 0, false, false, false},
    {320, 170, 0, 35, true,  true,  false},
    {170, 320, 35, 0, false, true,  true},
    {320, 170, 0, 35, true,  false, true}
};

mpdisplay_display_rotation_t ROTATIONS_240x240[4] = {
    {240, 240, 0, 0, false, false, false},
    {240, 240, 0, 0, true,  true,  false},
    {240, 240, 0, 80, false, true,  true},
    {240, 240, 80, 0, true,  false, true}
};

mpdisplay_display_rotation_t ROTATIONS_135x240[4] = {
    {135, 240, 52, 40, false, false, false},
    {240, 135, 40, 53, true,  true,  false},
    {135, 240, 53, 40, false, true,  true},
    {240, 135, 40, 52, true,  false, true}
};

mpdisplay_display_rotation_t ROTATIONS_128x160[4] = {
    {128, 160, 0, 0, false, false, false},
    {160, 128, 0, 0, true,  true,  false},
    {128, 160, 0, 0, false, true,  true},
    {160, 128, 0, 0, true,  false, true}
};

mpdisplay_display_rotation_t ROTATIONS_80x160[4] = {
    {80, 160, 26, 1, false, false, false},
    {160, 80, 1, 26, true, true, false},
    {80, 160, 26, 1, false, true,  true},
    {160, 80, 1, 26, true,  false, true}
};

mpdisplay_display_rotation_t ROTATIONS_128x128[4] = {
    {128, 128, 2, 1, false, false, false},
    {128, 128, 1, 2, true,  true,  false},
    {128, 128, 2, 3, false, true,  true},
    {128, 128, 3, 2, true,  false, true}
};

mpdisplay_display_rotation_t *ROTATIONS[] = {
    ROTATIONS_240x320,              // default if no match
    ROTATIONS_320x480,
    ROTATIONS_170x320,
    ROTATIONS_240x240,
    ROTATIONS_135x240,
    ROTATIONS_128x160,
    ROTATIONS_80x160,
    ROTATIONS_128x128,
    NULL
};

// print function called in place of Micropython's __repr__ dunder method
STATIC void mpdisplay_display_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind) {
    (void)kind;
    mpdisplay_display_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_printf(print, "Display(bus, width=%u, height=%u, bpp=%u, reset=%u, rotation=%u, bgr=%s, invert_color=%s, init_sequence=(...), rotations=(...), backlight=Backlight(...)", 
        self->width, self->height, self->bpp, self->rst, self->rotation, 
        self->bgr ? "True" : "False", self->invert_color ? "True" : "False");
}

/// .width()
/// Returns the width of the display in pixels.
STATIC mp_obj_t mpdisplay_display_width(mp_obj_t self_in) {
    mpdisplay_display_obj_t *self = MP_OBJ_TO_PTR(self_in);
    return mp_obj_new_int(self->width);
}

/// .height()
/// Returns the height of the display in pixels.
STATIC mp_obj_t mpdisplay_display_height(mp_obj_t self_in) {
    mpdisplay_display_obj_t *self = MP_OBJ_TO_PTR(self_in);
    return mp_obj_new_int(self->height);
}

/// .register_cb(function)
/// Register the ready callback function and argument to be called from lcd_panel_done()
/// e.g. function(argument)
/// required parameters:
/// -- function: called when blit is completed
STATIC mp_obj_t mpdisplay_display_register_cb(mp_obj_t self_in, mp_obj_t function) {
    mpdisplay_display_obj_t *self = self_in;
    if (mp_obj_is_callable(function)) {
        self->ready_cb_func = function;
    } else {
        mp_raise_TypeError("Callback is not callable");
    }
    return mp_const_none;
}

// Find the Rotation table for the given width and height
// return the first rotation table if no match is found.
STATIC mpdisplay_display_rotation_t *set_default_rotations(uint16_t width, uint16_t height) {;
    for (int i=0; i < MP_ARRAY_SIZE(ROTATIONS); i++) {
        mpdisplay_display_rotation_t *rotation;
        if ((rotation = ROTATIONS[i]) != NULL) {
            if (rotation->width == width && rotation->height == height) {
                return rotation;
            }
        }
    }
    return ROTATIONS[0];
}

// Define the Display class

// bindings for Display class functions in this file
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mpdisplay_display_width_obj, mpdisplay_display_width);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mpdisplay_display_height_obj, mpdisplay_display_height);
STATIC MP_DEFINE_CONST_FUN_OBJ_2(mpdisplay_display_register_cb_obj, mpdisplay_display_register_cb);

// bindings for Display class functions provided in architechture specific files
STATIC MP_DEFINE_CONST_FUN_OBJ_2(mpdisplay_display_rotation_obj, mpdisplay_display_rotation);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(mpdisplay_display_blit_obj, 6, 6, mpdisplay_display_blit);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mpdisplay_display_deinit_obj, mpdisplay_display_deinit);

STATIC const mp_rom_map_elem_t mpdisplay_display_locals_dict_table[] = {
    {MP_ROM_QSTR(MP_QSTR_width), MP_ROM_PTR(&mpdisplay_display_width_obj)},
    {MP_ROM_QSTR(MP_QSTR_height), MP_ROM_PTR(&mpdisplay_display_height_obj)},
    {MP_ROM_QSTR(MP_QSTR_register_cb), MP_ROM_PTR(&mpdisplay_display_register_cb_obj)},
    {MP_ROM_QSTR(MP_QSTR_rotation), MP_ROM_PTR(&mpdisplay_display_rotation_obj)},
    {MP_ROM_QSTR(MP_QSTR_blit), MP_ROM_PTR(&mpdisplay_display_blit_obj)},
    {MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&mpdisplay_display_deinit_obj)},
};
STATIC MP_DEFINE_CONST_DICT(mpdisplay_display_locals_dict, mpdisplay_display_locals_dict_table);

MP_DEFINE_CONST_OBJ_TYPE(
    mpdisplay_display_type,
    MP_QSTR_Display,
    MP_TYPE_FLAG_NONE,
    print, mpdisplay_display_print,
    make_new, mpdisplay_display_make_new,
    locals_dict, &mpdisplay_display_locals_dict);

/// .__init__(bus, width, height, bpp, reset, rotation, bgr, invert_color, init_sequence, rotations)
/// required parameters:
/// -- bus: bus
/// -- width: width of the display
/// -- height: height of the display
/// optional keyword parameters:
/// -- bpp: color depth - bits per pixel
/// -- reset: reset pin
/// -- rotation: rotation
/// -- bgr: color order, True = BGR, False = RGB
/// -- invert_color: invert color data lines (polarity)
/// -- init_sequence: sequence of commands to initialize the display
/// -- rotations: list of rotation tuples
mp_obj_t mpdisplay_display_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args) {
    enum {
        ARG_bus,
        ARG_width,
        ARG_height,
        ARG_bpp,
        ARG_reset,
        ARG_rotation,
        ARG_bgr,
        ARG_invert_color,
        ARG_init_sequence,
        ARG_rotations,
    };

    STATIC const mp_arg_t allowed_args[] = {
        {MP_QSTR_bus, MP_ARG_OBJ | MP_ARG_REQUIRED, {.u_obj = MP_OBJ_NULL}},
        {MP_QSTR_width, MP_ARG_INT | MP_ARG_REQUIRED | MP_ARG_KW_ONLY, {.u_int = 0}},
        {MP_QSTR_height, MP_ARG_INT | MP_ARG_REQUIRED | MP_ARG_KW_ONLY, {.u_int = 0}},
        {MP_QSTR_bpp, MP_ARG_INT | MP_ARG_KW_ONLY, {.u_int = 16}},
        {MP_QSTR_reset, MP_ARG_INT | MP_ARG_KW_ONLY, {.u_int = -1}},
        {MP_QSTR_rotation, MP_ARG_INT | MP_ARG_KW_ONLY, {.u_int = 0}},
        {MP_QSTR_bgr, MP_ARG_BOOL | MP_ARG_KW_ONLY, {.u_bool = false}},
        {MP_QSTR_invert_color, MP_ARG_BOOL | MP_ARG_KW_ONLY, {.u_bool = true}},
        {MP_QSTR_init_sequence, MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_obj = mp_const_none}},
        {MP_QSTR_rotations, MP_ARG_OBJ | MP_ARG_KW_ONLY, {.u_obj = mp_const_none}},
    };

    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    mpdisplay_display_obj_t *self = m_new_obj(mpdisplay_display_obj_t);
    self->base.type = &mpdisplay_display_type;
    self->bus = args[ARG_bus].u_obj;
    self->width = args[ARG_width].u_int;
    self->height = args[ARG_height].u_int;
    self->bpp = args[ARG_bpp].u_int;
    self->rst = args[ARG_reset].u_int;
    self->bgr = args[ARG_bgr].u_bool;
    self->invert_color = args[ARG_invert_color].u_bool;
    self->init_sequence = args[ARG_init_sequence].u_obj;

    self->rotations = set_default_rotations(self->width, self->height);
    
    self->rotations_len = 4;
    self->ready_cb_func = mp_const_none;
    if (args[ARG_rotations].u_obj != mp_const_none) {
        size_t len;
        mp_obj_t *rotations_array = MP_OBJ_NULL;
        mp_obj_get_array(args[ARG_rotations].u_obj, &len, &rotations_array);
        self->rotations_len = len;
        self->rotations = m_new(mpdisplay_display_rotation_t, self->rotations_len);
        for (int i = 0; i < self->rotations_len; i++) {
            mp_obj_t *rotation_tuple = NULL;
            size_t rotation_tuple_len = 0;
            mp_obj_tuple_get(rotations_array[i], &rotation_tuple_len, &rotation_tuple);
            if (rotation_tuple_len != 7) {
                mp_raise_ValueError(MP_ERROR_TEXT("rotations tuple must have 7 elements"));
            }
            self->rotations[i].width = mp_obj_get_int(rotation_tuple[0]);
            self->rotations[i].height = mp_obj_get_int(rotation_tuple[1]);
            self->rotations[i].x_gap = mp_obj_get_int(rotation_tuple[2]);
            self->rotations[i].y_gap = mp_obj_get_int(rotation_tuple[3]);
            self->rotations[i].swap_xy = mp_obj_is_true(rotation_tuple[4]);
            self->rotations[i].mirror_x = mp_obj_is_true(rotation_tuple[5]);
            self->rotations[i].mirror_y = mp_obj_is_true(rotation_tuple[6]);
        }
    }

    self->rotation = args[ARG_rotation].u_int % self->rotations_len;

    mpdisplay_display_init(self);

    return MP_OBJ_FROM_PTR(self);
}

// Define the mpdisplay module

// bindings for mpdisplay module functions in other files
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(mpdisplay_allocate_buffer_obj, 1, 2, mpdisplay_allocate_buffer);

STATIC const mp_map_elem_t mpdisplay_module_globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_mpdisplay)},
    {MP_ROM_QSTR(MP_QSTR_Display), (mp_obj_t)&mpdisplay_display_type},
    {MP_ROM_QSTR(MP_QSTR_I80_bus), (mp_obj_t)&mpdisplay_i80_bus_type},
    {MP_ROM_QSTR(MP_QSTR_Spi_bus), (mp_obj_t)&mpdisplay_spi_bus_type},
    {MP_ROM_QSTR(MP_QSTR_CAPS), (mp_obj_t)&mpdisplay_caps_type},
    {MP_ROM_QSTR(MP_QSTR_allocate_buffer), (mp_obj_t)&mpdisplay_allocate_buffer_obj},
};

STATIC MP_DEFINE_CONST_DICT(mp_module_mpdisplay_globals, mpdisplay_module_globals_table);

const mp_obj_module_t mp_module_mpdisplay = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t *)&mp_module_mpdisplay_globals,
};

MP_REGISTER_MODULE(MP_QSTR_mpdisplay, mp_module_mpdisplay);
