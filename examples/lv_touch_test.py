# SPDX-FileCopyrightText: 2023 Brad Barnett
#
# SPDX-License-Identifier: MIT
#
# Test touchscreen and allows changing touch driver rotation
# to find a rotation that matches the display rotation.

import lv_config
import lvgl as lv

touch_rotation = lambda x: lv_config.touch.set_touch_rotation(x)

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

style_default = lv.style_t()
style_default.init()
style_default.set_width(lv.pct(33))
style_default.set_height(lv.pct(33))
style_default.set_bg_color(lv.palette_main(lv.PALETTE.BLUE))

style_pressed = lv.style_t()
style_pressed.init()
style_pressed.set_transform_width(-10)
style_pressed.set_transform_height(-10)
style_pressed.set_bg_color(lv.palette_main(lv.PALETTE.GREEN))

style_focused = lv.style_t()
style_focused.init()
style_focused.set_bg_color(lv.palette_main(lv.PALETTE.RED))

parent = lv.screen_active()

i = 0
for alignment in alignments:
    i +=1
    btn = lv.button(parent)
    btn.align(*alignment)
    btn.add_style(style_default, 0)
    btn.add_style(style_pressed, lv.STATE.PRESSED)
    btn.add_style(style_focused, lv.STATE.FOCUSED)
    label = lv.label(btn)
    label.set_text(f"Btn{i}")
    label.center()
    
print(
    "To test different touch rotations:\n",
    "    if you ran `import lv_touch_test`\n",
    "        type `lv_touch_test.touch_rotation(x)`\n",
    "    if you ran the script directly, such as with Thonny\n",
    "        type `touch_rotation(x)`\n",
    "    where x is 0 to 7 for binary values, -1 to -4 for index values."
    )
