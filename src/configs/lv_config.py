# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
lv_config.py - LVGL driver configuration for MPDisplay
"""

from board_config import display_drv, broker
from eventsys.events import Events
from eventsys.devices import Devices
import lvgl as lv # type: ignore
import gc

def main(warn=True):
    if warn:
        print("\n\n\nlv_config.py - This file has not been thoroughly tested and may need to be modified.",
            "Please create a pull request for any changes you make that are not unique to your configuration",
            "and may help others.\n\n\n")
    gc.collect()
    if not lv.is_initialized():
        lv.init()

    try:
        # lv_micropython provides 'lv_utils'
        import lv_utils # type: ignore

        if not lv_utils.event_loop.is_running():
            _eventloop = lv_utils.event_loop()
    except ImportError:
        # lvgl_micropython provides 'task_handler'
        import task_handler # type: ignore

        _task_handler = task_handler.TaskHandler()

    display = DisplayDriver(  # noqa: F841
        display_drv,
        lv.COLOR_FORMAT.RGB565,
        blocking=True,
        devices=broker.devices,
    )


class DisplayDriver:

    def __init__(
        self,
        display_drv,
        color_format=lv.COLOR_FORMAT.RGB565,
        blocking=True,
        devices=[],  
    ):
        draw_buf1 = lv.draw_buf_create(display_drv.width, display_drv.height // 10, color_format, 0)
        draw_buf2 = lv.draw_buf_create(display_drv.width, display_drv.height // 10, color_format, 0)

        self.display_drv = display_drv
        self._color_size = lv.color_format_get_size(color_format)
        self._blocking = blocking
        self.needs_swap = self.display_drv.requires_byte_swap
        
        self.lv_display = lv.display_create(self.display_drv.width, self.display_drv.height)
        self.lv_display.set_flush_cb(self._flush_cb)
        self.lv_display.set_color_format(color_format)
        if not self._blocking:
            self.display_drv.display_bus.register_callback(self.lv_display.flush_ready)
        self.lv_display.set_draw_buffers(draw_buf1, draw_buf2)
        self.lv_display.set_render_mode(lv.DISPLAY_RENDER_MODE.PARTIAL)

        self.create_indevs(devices)

    def create_indevs(self, devices):
        # Create an input device for each device in the 'devices' list
        # and set its type and read callback function.  Save a reference to the indev object
        # in the device's user_data attribute to enable changing the indev's group or display
        # later with:
        #     indev = device.user_data
        #     indev.set_group(new_group)
        #     indev.set_display(new_display)
        for device in devices:
            if device.type in (Devices.TOUCH, Devices.ENCODER, Devices.KEYPAD):
                indev = lv.indev_create()
                indev.set_display(self.lv_display)
                indev.set_group(lv.group_get_default())
                device.user_data = indev
                if device.type == Devices.TOUCH:
                    device.set_read_cb(self._touch_cb)  # Called by device
                    indev.set_type(lv.INDEV_TYPE.POINTER)
                elif device.type == Devices.ENCODER:
                    device.set_read_cb(self._encoder_cb)  # Called by device
                    indev.set_type(lv.INDEV_TYPE.ENCODER)
                elif device.type == Devices.KEYPAD:
                    device.set_read_cb(self._keypad_cb)  # Called by device
                    indev.set_type(lv.INDEV_TYPE.KEYPAD)
                indev.set_read_cb(device.read_cb)  # Called by lv task handler

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


main()
