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
#include "mpdisplay_common.h"

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

STATIC MP_DEFINE_CONST_FUN_OBJ_1(mpdisplay_display_width_obj, mpdisplay_display_width);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mpdisplay_display_height_obj, mpdisplay_display_height);
STATIC MP_DEFINE_CONST_FUN_OBJ_3(mpdisplay_display_register_cb_obj, mpdisplay_display_register_cb);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mpdisplay_display_reset_obj, mpdisplay_display_reset);
STATIC MP_DEFINE_CONST_FUN_OBJ_2(mpdisplay_display_inversion_mode_obj, mpdisplay_display_inversion_mode);
STATIC MP_DEFINE_CONST_FUN_OBJ_2(mpdisplay_display_rotation_obj, mpdisplay_display_rotation);
STATIC MP_DEFINE_CONST_FUN_OBJ_2(mpdisplay_display_get_buf_obj, mpdisplay_display_get_buf);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(mpdisplay_display_blit_obj, 6, 6, mpdisplay_display_blit);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mpdisplay_display_init_obj, mpdisplay_display_init);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mpdisplay_display_deinit_obj, mpdisplay_display_deinit);

//
// Define the Display class
//

STATIC const mp_rom_map_elem_t mpdisplay_display_locals_dict_table[] = {
    {MP_ROM_QSTR(MP_QSTR_reset), MP_ROM_PTR(&mpdisplay_display_reset_obj)},
    {MP_ROM_QSTR(MP_QSTR_inversion_mode), MP_ROM_PTR(&mpdisplay_display_inversion_mode_obj)},
    {MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&mpdisplay_display_init_obj)},
    {MP_ROM_QSTR(MP_QSTR_rotation), MP_ROM_PTR(&mpdisplay_display_rotation_obj)},
    {MP_ROM_QSTR(MP_QSTR_width), MP_ROM_PTR(&mpdisplay_display_width_obj)},
    {MP_ROM_QSTR(MP_QSTR_height), MP_ROM_PTR(&mpdisplay_display_height_obj)},
    {MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&mpdisplay_display_deinit_obj)},
    {MP_ROM_QSTR(MP_QSTR_get_buf), MP_ROM_PTR(&mpdisplay_display_get_buf_obj)},
    {MP_ROM_QSTR(MP_QSTR_register_cb), MP_ROM_PTR(&mpdisplay_display_register_cb_obj)},
    {MP_ROM_QSTR(MP_QSTR_blit), MP_ROM_PTR(&mpdisplay_display_blit_obj)},
};
STATIC MP_DEFINE_CONST_DICT(mpdisplay_display_locals_dict, mpdisplay_display_locals_dict_table);

#if MICROPY_OBJ_TYPE_REPR == MICROPY_OBJ_TYPE_REPR_SLOT_INDEX

MP_DEFINE_CONST_OBJ_TYPE(
    mpdisplay_display_type,
    MP_QSTR_Display,
    MP_TYPE_FLAG_NONE,
    print, mpdisplay_display_print,
    make_new, mpdisplay_display_make_new,
    locals_dict, &mpdisplay_display_locals_dict);

#else

const mp_obj_type_t mpdisplay_display_type = {
    {&mp_type_type},
    .name = MP_QSTR_Display,
    .print = mpdisplay_display_print,
    .make_new = mpdisplay_display_make_new,
    .locals_dict = (mp_obj_dict_t *)&mpdisplay_display_locals_dict,
};

#endif

//
// Find the Rotation table for the given width and height
// return the first rotation table if no match is found.
//

mpdisplay_display_rotation_t *set_rotations(uint16_t width, uint16_t height) {;
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

///
/// .__init__(bus, width, height, reset, rotations, rotation, custom_init, inversion_mode)
/// required parameters:
/// -- bus: bus
/// -- width: width of the display
/// -- height: height of the display
/// optional keyword parameters:
/// -- reset: reset pin
/// -- rotations: number of rotations
/// -- rotation: rotation
/// -- inversion_mode: inversion
///

mp_obj_t mpdisplay_display_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args) {
    enum {
        ARG_bus,
        ARG_width,
        ARG_height,
        ARG_reset,
        ARG_rotations,
        ARG_rotation,
        ARG_custom_init,
        ARG_inversion_mode,
    };

    STATIC const mp_arg_t allowed_args[] = {
        {MP_QSTR_bus, MP_ARG_OBJ | MP_ARG_REQUIRED, {.u_obj = MP_OBJ_NULL}},
        {MP_QSTR_width, MP_ARG_INT | MP_ARG_REQUIRED, {.u_int = 0}},
        {MP_QSTR_height, MP_ARG_INT | MP_ARG_REQUIRED, {.u_int = 0}},
        {MP_QSTR_reset, MP_ARG_INT | MP_ARG_KW_ONLY, {.u_int = -1}},
        {MP_QSTR_rotations, MP_ARG_OBJ | MP_ARG_KW_ONLY, {.u_obj = MP_OBJ_NULL}},
        {MP_QSTR_rotation, MP_ARG_INT | MP_ARG_KW_ONLY, {.u_int = 0}},
        {MP_QSTR_custom_init, MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL}},
        {MP_QSTR_inversion_mode, MP_ARG_BOOL | MP_ARG_KW_ONLY, {.u_bool = true}},
    };

    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    mpdisplay_obj_t *self = m_new_obj(mpdisplay_obj_t);
    self->base.type = &mpdisplay_display_type;
    self->bus = args[ARG_bus].u_obj;
    self->width = args[ARG_width].u_int;
    self->height = args[ARG_height].u_int;
    self->rst = args[ARG_reset].u_int;
    self->custom_init = args[ARG_custom_init].u_obj;
    self->inversion_mode = args[ARG_inversion_mode].u_bool;

    if (args[ARG_rotations].u_obj != MP_OBJ_NULL) {
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
    return MP_OBJ_FROM_PTR(self);
}

//
// Define the mpdisplay module
//

STATIC const mp_map_elem_t mpdisplay_module_globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_mpdisplay)},
    {MP_ROM_QSTR(MP_QSTR_Display), (mp_obj_t)&mpdisplay_display_type},
    {MP_ROM_QSTR(MP_QSTR_I80_bus), (mp_obj_t)&mpdisplay_i80_bus_type},
    {MP_ROM_QSTR(MP_QSTR_Spi_bus), (mp_obj_t)&mpdisplay_spi_bus_type},
};

STATIC MP_DEFINE_CONST_DICT(mp_module_mpdisplay_globals, mpdisplay_module_globals_table);

const mp_obj_module_t mp_module_mpdisplay = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t *)&mp_module_mpdisplay_globals,
};

//
// Register the mpdisplay module
//

MP_REGISTER_MODULE(MP_QSTR_mpdisplay, mp_module_mpdisplay);
