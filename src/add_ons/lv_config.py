# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
lv_config.py - LVGL driver configuration for displaysys.
"""

from board_config import display_drv, broker
from eventsys import Events
from eventsys.device import Types
import gc
import lvgl as lv
import lv_utils


def main():
    gc.collect()
    if not lv.is_initialized():
        lv.init()
    if not lv_utils.event_loop.is_running():
        lv_utils.event_loop()

    DisplayDriver(
        display_drv,
        broker.devices,
    )


def _touch_cb(event, indev, data):
    # LVGL hands us an object called data.  We just change the state attributes when necessary.
    if event is None:
        return
    if event.type == Events.MOUSEBUTTONDOWN and event.button == 1:
        x, y = event.pos
        data.point = lv.point_t({"x": x, "y": y})
        data.state = lv.INDEV_STATE.PRESSED
    elif event.type == Events.MOUSEBUTTONUP and event.button == 1:
        data.state = lv.INDEV_STATE.RELEASED


def _encoder_cb(event, indev, data):
    # LVGL hands us an object called data.  We just change the enc_diff and/or state attributes if necessary.
    if event is None:
        return
    if event.type == Events.MOUSEWHEEL:
        data.enc_diff = event.x if event.flipped is False else -event.x
    elif event.type == Events.MOUSEBUTTONDOWN and event.button == 3:
        data.state = lv.INDEV_STATE.PRESSED
    elif event.type == Events.MOUSEBUTTONUP and event.button == 3:
        data.state = lv.INDEV_STATE.RELEASED


def _keypad_cb(event, indev, data):
    # LVGL hands us an object called data.  We just change the state attributes when necessary.
    if event is None:
        return
    if event.type == Events.KEYDOWN:
        data.state = lv.INDEV_STATE.PRESSED
        data.key = event.key
    elif event.type == Events.KEYUP:
        data.state = lv.INDEV_STATE.RELEASED
        data.key = event.key


class DisplayDriver:
    def __init__(
        self,
        display_drv,
        devices=[],
        color_format=lv.COLOR_FORMAT.RGB565,
        blocking=True,
    ):
        gc.collect()
        draw_buf1 = lv.draw_buf_create(
            display_drv.width, display_drv.height // 10, color_format, 0
        )
        draw_buf2 = lv.draw_buf_create(
            display_drv.width, display_drv.height // 10, color_format, 0
        )
        # If byte swapping is required and the display bus is capable of having byte swapping disabled,
        # disable it and set a flag so we can swap the color bytes as they are created.
        if display_drv.requires_byteswap:
            self._needs_swap = display_drv.disable_auto_byteswap(True)
        else:
            self._needs_swap = False
        self._color_size = lv.color_format_get_size(color_format)
        self._blocking = blocking

        self._lv_display = lv.display_create(display_drv.width, display_drv.height)
        self._lv_display.set_flush_cb(self._flush_cb)
        self._lv_display.set_color_format(color_format)
        if not self._blocking:
            display_drv.display_bus.register_callback(self._lv_display.flush_ready)
        self._lv_display.set_draw_buffers(draw_buf1, draw_buf2)
        self._lv_display.set_render_mode(lv.DISPLAY_RENDER_MODE.PARTIAL)

        # Create an input device for each device in the 'devices' list
        # and set its type and read callback function.  Save a reference to the indev object
        # in the device's user_data attribute to enable changing the indev's group or display
        # later with:
        #     indev = device.user_data
        #     indev.set_group(new_group)
        #     indev.set_display(new_display)
        for device in devices:
            if device.type in (Types.TOUCH, Types.ENCODER, Types.KEYPAD):
                indev = lv.indev_create()
                indev.set_display(self._lv_display)
                indev.set_group(lv.group_get_default())
                device.user_data = indev
                if device.type == Types.TOUCH:
                    device.subscribe(_touch_cb)  # Called by device
                    indev.set_type(lv.INDEV_TYPE.POINTER)
                elif device.type == Types.ENCODER:
                    device.subscribe(_encoder_cb)  # Called by device
                    indev.set_type(lv.INDEV_TYPE.ENCODER)
                elif device.type == Types.KEYPAD:
                    device.subscribe(_keypad_cb)  # Called by device
                    indev.set_type(lv.INDEV_TYPE.KEYPAD)
                indev.set_read_cb(device.poll)  # Called by lv task handler

    def _flush_cb(self, disp_drv, area, color_p):
        width = area.x2 - area.x1 + 1
        height = area.y2 - area.y1 + 1

        # Swap the bytes in the color buffer if necessary
        if self._needs_swap:
            lv.draw_sw_rgb565_swap(color_p, width * height)

        # we have to use the __dereference__ method because this method
        # converts from the C_Array object the binding passes into a
        # memoryview object that can be passed to the bus drivers
        data = color_p.__dereference__(width * height * self._color_size)
        display_drv.blit_rect(data, area.x1, area.y1, width, height)
        if self._blocking:
            self._lv_display.flush_ready()


main()
