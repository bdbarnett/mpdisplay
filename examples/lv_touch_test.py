# SPDX-FileCopyrightText: 2023 Brad Barnett
#
# SPDX-License-Identifier: MIT
#
# Test touchscreen and allows changing touch driver rotation
# to find a rotation that matches the display rotation.

import lv_config
import lvgl as lv

alignments = (
    (lv.ALIGN.TOP_LEFT, 0, 0),
    (lv.ALIGN.TOP_MID, 0, 0),
    (lv.ALIGN.TOP_RIGHT, 0, 0),
    (lv.ALIGN.LEFT_MID, 0, 0),
    (lv.ALIGN.CENTER, 0, 0),
    (lv.ALIGN.RIGHT_MID, 0, 0),
    (lv.ALIGN.BOTTOM_LEFT, 0, 0),
    (lv.ALIGN.BOTTOM_MID, 0, 0),
    (lv.ALIGN.BOTTOM_RIGHT, 0, 0),
)

style_base = lv.style_t()
style_base.init()
style_base.set_width(lv.pct(33))
style_base.set_height(lv.pct(33))

style_pressed = lv.style_t()
style_pressed.init()
style_pressed.set_transform_width(-10)
style_pressed.set_transform_height(-10)

style_focused = lv.style_t()
style_focused.init()
style_focused.set_bg_color(lv.palette_main(lv.PALETTE.RED))

parent = lv.scr_act()

for alignment in alignments:
    btn = lv.btn(parent)
    btn.align(*alignment)
    btn.add_style(style_base, 0)
    btn.add_style(style_pressed, lv.STATE.PRESSED)
    btn.add_style(style_focused, lv.STATE.FOCUSED)
    
print("To test different touch rotations, type `touch_drv.set_touch_rotation(x)` where x is 0 to 7")
