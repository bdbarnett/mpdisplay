# SPDX-FileCopyrightText: 2023 Brad Barnett and Kevin Schlosser
#
# SPDX-License-Identifier: MIT

"""
lv_mpdisplay.py - LVGL driver shim for MPDisplay
"""

import lvgl as lv
from eventsys.events import Events
from eventsys.devices import Devices


if not lv.is_initialized():
    lv.init()


try:
    import lv_utils  # lv_micropython provides lv_utils

    if not lv_utils.event_loop.is_running():
        _eventloop = lv_utils.event_loop()
except ImportError:
    import task_handler  # lvgl_micropython provides task_handler

    _task_handler = task_handler.TaskHandler()


class DisplayDriver:
    name = "DisplayDriver"

    def __init__(
        self,
        display_drv,
        frame_buffer1,
        frame_buffer2,
        color_format=lv.COLOR_FORMAT.RGB565,
        *,
        blocking=True,
    ):
        self.display_drv = display_drv
        self._color_size = lv.color_format_get_size(color_format)
        self._frame_buffer1 = frame_buffer1
        self._frame_buffer2 = frame_buffer2
        self._blocking = blocking

        # If byte swapping is required and the display bus is capable of having byte swapping disabled,
        # disable it and set a flag so we can swap the color bytes as they are created.
        if self.display_drv.requires_byte_swap:
            self.needs_swap = self.display_drv.bus_swap_disable(True)
        else:
            self.needs_swap = False

        if hasattr(display_drv, "display_bus") and "RGB" in repr(
            display_drv.display_bus
        ):
            render_mode = lv.DISPLAY_RENDER_MODE.DIRECT
            self.display_drv.set_render_mode_full(True)
        elif (
            self._frame_buffer1.data_size
            >= self.display_drv.width * self.display_drv.height * self._color_size
        ):
            render_mode = lv.DISPLAY_RENDER_MODE.FULL
            self.display_drv.set_render_mode_full(True)
        else:
            render_mode = lv.DISPLAY_RENDER_MODE.PARTIAL
            self.display_drv.set_render_mode_full(False)

        self.lv_display = lv.display_create(
            self.display_drv.width, self.display_drv.height
        )
        self.lv_display.set_flush_cb(self._flush_cb)
        self.lv_display.set_color_format(color_format)
        if not self._blocking:
            self.display_drv.register_callback(self.lv_display.flush_ready)
        self.lv_display.set_draw_buffers(self._frame_buffer1, self._frame_buffer2)
        self.lv_display.set_render_mode(render_mode)

        # Create an input device for each device of known type registered to display_drv
        # and set its type and read callback function.  Save a reverence to the indev object
        # in the device's user_data attribute to enable changing the indev's group or display
        # later with:
        #     indev = device.user_data
        #     indev.set_group(new_group)
        #     indev.set_display(new_display)
        for device in broker.devices:
            if device.type in (Devices.TOUCH, Devices.ENCODER, Devices.KEYPAD):
                indev = lv.indev_create()
                indev.set_display(self.lv_display)
                indev.set_group(lv.group_get_default())
                device.user_data = indev
                if device.type == Devices.TOUCH:
                    device.set_read_cb(self._touch_cb)
                    indev.set_type(lv.INDEV_TYPE.POINTER)
                elif device.type == Devices.ENCODER:
                    device.set_read_cb(self._encoder_cb)
                    indev.set_type(lv.INDEV_TYPE.ENCODER)
                elif device.type == Devices.KEYPAD:
                    device.set_read_cb(self._keypad_cb)
                    indev.set_type(lv.INDEV_TYPE.KEYPAD)
                indev.set_read_cb(device.read_cb)

    def _flush_cb(self, disp_drv, area, color_p):
        width = area.x2 - area.x1 + 1
        height = area.y2 - area.y1 + 1

        # Swap the bytes in the color buffer if necessary
        if self.needs_swap:
            lv.draw_sw_rgb565_swap(color_p, width * height)

        # we have to use the __dereference__ method because this method is
        # what converts from the C_Array object the binding passes into a
        # memoryview object that can be passed to the bus drivers
        data = color_p.__dereference__(width * height * self._color_size)
        self.display_drv.blit_rect(data, area.x1, area.y1, width, height)
        if self._blocking:
            self.lv_display.flush_ready()

    def _touch_cb(self, event, indev, data):
        # LVGL hands us an object called data.  We just change the state attributes when necessary.
        if event is None:
            return
        if event.type == Events.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            data.point = lv.point_t({"x": x, "y": y})
            data.state = lv.INDEV_STATE.PRESSED
        elif event.type == Events.MOUSEBUTTONUP and event.button == 1:
            data.state = lv.INDEV_STATE.RELEASED

    def _encoder_cb(self, event, indev, data):
        # LVGL hands us an object called data.  We just change the enc_diff and/or state attributes if necessary.
        if event is None:
            return
        if event.type == Events.MOUSEWHEEL:
            data.enc_diff = event.x if event.flipped is False else -event.x
        elif event.type == Events.MOUSEBUTTONDOWN and event.button == 3:
            data.state = lv.INDEV_STATE.PRESSED
        elif event.type == Events.MOUSEBUTTONUP and event.button == 3:
            data.state = lv.INDEV_STATE.RELEASED

    def _keypad_cb(self, event, indev, data):
        # LVGL hands us an object called data.  We just change the state attributes when necessary.
        if event is None:
            return
        if event.type == Events.KEYDOWN:
            data.state = lv.INDEV_STATE.PRESSED
            data.key = event.key
        elif event.type == Events.KEYUP:
            data.state = lv.INDEV_STATE.RELEASED
            data.key = event.key
