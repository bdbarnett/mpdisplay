
#ifndef __MPDISPLAY_H__
#define __MPDISPLAY_H__

#include "py/obj.h"
#include "mphalport.h"
#include "esp_lcd_types.h"
#include "esp_lcd_panel_io.h"

typedef struct _mpdisplay_display_rotation_t {
    uint16_t width;     // width of the display in this rotation
    uint16_t height;    // height of the display in this rotation
    uint16_t x_gap;     // gap on x axis, in pixels
    uint16_t y_gap;     // gap on y axis, in pixels
    bool swap_xy;       // set MADCTL_MV bit 0x20
    bool mirror_x;      // set MADCTL MX bit 0x40
    bool mirror_y;      // set MADCTL MY bit 0x80
} mpdisplay_display_rotation_t;

typedef struct _mpdisplay_display_obj_t {
    mp_obj_base_t base;
    esp_lcd_panel_io_handle_t io_handle;        // io handle
    esp_lcd_panel_handle_t panel_handle;        // panel handle
    mp_obj_t ready_cb_func;                     // callback function
    uint8_t rotations_len;                      // number of rotations
    mp_obj_t bus;                               // bus object
    uint16_t width;                             // logical width (after rotation)
    uint16_t height;                            // logical height (after rotation)
    uint16_t bpp;                               // bits per pixel
    gpio_num_t rst;                             // reset pin
    uint8_t rotation;                           // current rotation
    bool bgr;                                   // color order
    bool invert_color;                          // invert color
    mp_obj_t init_sequence;                     // custom init sequence
    mpdisplay_display_rotation_t *rotations;    // list of rotation tuples
} mpdisplay_display_obj_t;

mp_obj_t mpdisplay_display_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args);

#endif // __MPDISPLAY_H__
