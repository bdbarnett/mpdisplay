
#ifndef __MPDISPLAY_H__
#define __MPDISPLAY_H__

#include "mpdisplay_esp.h"

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
    mp_obj_t bus;
    bus_handle_t bus_handle;
    esp_lcd_panel_io_handle_t io_handle;
    esp_lcd_panel_handle_t panel_handle;
    bool inversion_mode;
    uint16_t width;                         // logical width (after rotation)
    uint16_t height;                        // logical height (after rotation)
    uint8_t rotation;                       // current rotation
    mpdisplay_display_rotation_t *rotations;            // list of rotation tuples
    mp_obj_t custom_init;                   // custom init sequence
    uint8_t rotations_len;                  // number of rotations
    gpio_num_t rst;
    bool swap_color_bytes;                  // swap color bytes (SPI only, I80 is builtin)
} mpdisplay_obj_t;

mp_obj_t mpdisplay_display_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args);

#endif // __MPDISPLAY_H__
