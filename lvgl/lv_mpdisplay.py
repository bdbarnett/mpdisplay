# SPDX-FileCopyrightText: 2023 Brad Barnett and Kevin Schlosser
#
# SPDX-License-Identifier: MIT

'''
lv_mpdisplay.py - LVGL driver framework for MPDisplay
'''

import lvgl as lv
from time import ticks_ms, ticks_diff
from mpdisplay import Events


try:
    import lv_utils  # lv_micropython provides lv_utils
    if not lv_utils.event_loop.is_running():
        _eventloop = lv_utils.event_loop(asynchronous=False, exception_sink=None)
except ImportError:
    import task_handler  # lvgl_micropython provides task_handler
    _task_handler = task_handler.TaskHandler()


# When using RGBBus as the data bus the user is not able to allocate the
# frame buffers. The user can call RGBBus.get_frame_buffer(buffer_number)
# and pass the returned buffer(s) to the constructor for the display driver
# or they can leave the buffers(s) set to None and the display driver
# will collect the frame buffer for them. For the I80Bus, SPIBus and I2C bus
# the frame buffer(s) can either be be created by the user and passed to the
# constructor of the display driver or left as None and the driver will
# create the buffer(s) if it is able to. It will try to make 2 buffers with
# both in DMA SRAM and if that fails then it will try to make 2 buffers in
# DMA SPIRAM. If that fails it will try to make a single buffer in SRAM and
# if that fails it will try to make a single buffer in SPIRAM.
#
# For the ESP32 the allocation of the frame buffers can be done one of 2
# ways depending on what is wanted in terms of performance VS memory use
# If a single frame buffer is used then using a DMA transfer is pointless
# to do. The frame buffer in this case can be allocated as simple as
#
# buf = bytearray(buffer_size)
#
# If the user wants to be able to specify if the frame buffer is to be
# created in internal memory (SRAM) or in external memory (PSRAM/SPIRAM)
# this can be done using the heap_caps module.
#
# internal memory:
# buf = heap_caps.malloc(buffer_size, heap_caps.CAP_INTERNAL)
#
# external memory:
# buf = heap_caps.malloc(buffer_size, heap_caps.CAP_SPIRAM)
#
# If wanting to use DMA memory then use the bitwise OR "|" operator to add
# the DMA flag to the last parameter of the malloc function
#
# buf = heap_caps.malloc(buffer_size, heap_caps.CAP_INTERNAL | heap_caps.CAP_DMA)


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
            self.swap_color_bytes = self.display_drv.bus_swap_disable(True)
        else:
            self.swap_color_bytes = False

        if hasattr(display_drv, "display_bus") and "RGB" in repr(display_drv.display_bus):
            render_mode = lv.DISPLAY_RENDER_MODE.DIRECT
            self.display_drv.set_render_mode_full(True)
        elif (
            len(self._frame_buffer1)
            >= self.display_drv.width * self.display_drv.height * self._color_size
        ):
            render_mode = lv.DISPLAY_RENDER_MODE.FULL
            self.display_drv.set_render_mode_full(True)
        else:
            render_mode = lv.DISPLAY_RENDER_MODE.PARTIAL
            self.display_drv.set_render_mode_full(False)

        if not lv.is_initialized():
            lv.init()

        self.lv_display = lv.display_create(self.display_drv.width, self.display_drv.height)
        self.lv_display.set_color_format(color_format)
        self.lv_display.set_flush_cb(self._flush_cb)
        if not self._blocking:
            self.display_drv.register_callback(self.lv_display.flush_ready)
        self.lv_display.set_draw_buffers(
            self._frame_buffer1,
            self._frame_buffer2,
            len(self._frame_buffer1),
            render_mode,
        )

        # Create an input device and set its type and read callback function.
        self._indev = lv.indev_create()
        self._indev.set_type(lv.INDEV_TYPE.POINTER)
        self._indev.set_read_cb(self._touch_cb)
        self._indev.set_disp(lv.display_get_default())
        self._indev.set_group(lv.group_get_default())

    def _flush_cb(self, disp_drv, area, color_p):
        width = area.x2 - area.x1 + 1
        height = area.y2 - area.y1 + 1

        # Swap the bytes in the color buffer if necessary
        if self.swap_color_bytes:
            lv.draw_sw_rgb565_swap(color_p, width * height)

        # we have to use the __dereference__ method because this method is
        # what converts from the C_Array object the binding passes into a
        # memoryview object that can be passed to the bus drivers
        self.display_drv.blit(
            area.x1,
            area.y1,
            width,
            height,
            color_p.__dereference__(width * height * self._color_size),
        )
        if self._blocking:
            self.lv_display.flush_ready()

    def _touch_cb(self, touch_indev, data):
        # LVGL hands us an object called data.  We just change the state attributes when necessary.
        event = self.display_drv.poll_event()
        if event and event.type == Events.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            data.point = lv.point_t({"x": x, "y": y})
            data.state = lv.INDEV_STATE.PRESSED
        else:
            data.state = lv.INDEV_STATE.RELEASED


class EncoderDriver:
    """
    read_func:  Function to read the value of the encoder.  Value should be continuous, not incremental.
    pressed_func:  Function that returns a truthy value if the button is pressed, falsy if not.
                   If pressed_func isn't specified, it will be configured to always return False (never pressed).
                   If you are reading a Pin object that has a pullup and normally open switch,
                   create a function to change to the opposite value, for example:
                        def is_encoder_pressed(): not button_pin.value()
                   or
                        is_encoder_pressed = lambda : not button_pin.value()
    long_press_duration:  Number of milliseconds for button to be pressed before calling the long_pressed method
    """

    display_name = "EncoderDriver"

    def __init__(self, read_func, pressed_func=None, long_press_duration=500):
        self.value = read_func
        self.pressed = pressed_func if pressed_func else lambda: False
        self.long_press_duration = long_press_duration

        # Grab the initial state
        self._last_value = read_func()
        self._last_pressed = pressed_func()
        self._last_ticks = -1  # Set to a falsy value to indicate we aren't counting.

        # Create the input device, set it's type and read callback function.
        self._indev = lv.indev_create()
        self._indev.set_type(lv.INDEV_TYPE.ENCODER)
        self._indev.set_read_cb(self._read_cb)
        self._indev.set_disp(lv.display_get_default())
        self._indev.set_group(lv.group_get_default())

    def _read_cb(self, indev, data):
        # LVGL hands us an object called data.  We just change the enc_diff and/or state attributes if necessary.

        # Read the encoder
        value = self.value()
        if value != self._last_value:
            data.enc_diff = (
                value - self._last_value
            )  # <- Reverse these to change direction of all encoders
            self._last_value = value

        # Read the button.
        pressed = self.pressed()
        # Is it different than the last time we checked?
        if pressed != self._last_pressed:
            # Yes.  Is it now pressed?
            if pressed:
                # Yes.  Send the signal that it was pressed
                data.state = lv.INDEV_STATE.PRESSED
                # and start counting.
                self._last_ticks = ticks_ms()
            else:
                # No.  Send the signal that it was released
                data.state = lv.INDEV_STATE.RELEASED
                # and stop counting.
                self._last_ticks = -1
            # It changed, so update _last_pressed.
            self._last_pressed = pressed
        # If we fall through to this point, it hasn't changed.
        #
        # We're finished modifying the `data` object, but we can also perform an action for
        # a long button press.  If you don't want that, just set long_press_duration to a
        # large number of milliseconds.
        #
        # Was it pressed last time and still pressed now?
        elif self._last_pressed and pressed:
            # Yes.  If we're still counting and it has been longer than the long_press_duration
            if (
                self._last_ticks
                and ticks_diff(ticks_ms, self._last_ticks) > self.long_press_duration
            ):
                # do whatever we do for a long press
                self.long_pressed()
                # and stop counting.
                self._last_ticks = -1

    def long_pressed(self):
        # If we're in `editing` mode
        if self._indev.get_group().get_editing():
            # escape out of it.
            self._indev.get_group().set_editing(False)
        # Otherwise, if an object has focus
        elif focused_obj := self._indev.get_group().get_focused():
            # send a LONG_PRESSED event to that object.
            focused_obj.send_event(lv.EVENT.LONG_PRESSED, None)
