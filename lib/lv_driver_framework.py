# SPDX-FileCopyrightText: 2023 Brad Barnett and Kevin Schlosser
#
# SPDX-License-Identifier: MIT

import lvgl as lv
from time import ticks_ms, ticks_diff

_DEFAULT_TOUCH_ROTATION_TABLE = (0b000, 0b101, 0b110, 0b011)

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
    display_name = "DisplayDriver"

    def __init__(
        self,
        display,
        color_format=lv.COLOR_FORMAT.NATIVE,
        frame_buffer1=None,
        frame_buffer2=None,
        *,
        factor=10,
        blocking=True,
    ):
        self.display = display
        self._color_size = lv.color_format_get_size(color_format)
        self._frame_buffer1, self._frame_buffer2 = self._allocate_buffers(
            frame_buffer1, frame_buffer2, factor
        )
        self._blocking = blocking

        self._swap_enabled = False
        # If the display bus is a MicroPython bus and it has byte swapping enabled, disable it and 
        # set a flag so we can call lv_draw_sw_rgb565_swap in _flush_cb
        if hasattr(self.display.display_bus, "name") and "MicroPython" in self.display.display_bus.name:
            if self.display.display_bus.rgb565_byte_swap:
                self._swap_enabled = True
                self.display.display_bus.enable_swap(False)

        if (
            len(self._frame_buffer1)
            >= display.width * display.height * self._color_size
        ):
            render_mode = lv.DISPLAY_RENDER_MODE.FULL
            self.display.set_render_mode_full(True)
        else:
            render_mode = lv.DISPLAY_RENDER_MODE.PARTIAL
            self.display.set_render_mode_full(False)

        if not lv.is_initialized():
            lv.init()

        self._disp_drv = lv.display_create(self.display.width, self.display.height)
        self._disp_drv.set_color_format(color_format)
        self._disp_drv.set_flush_cb(self._flush_cb)
        if not self._blocking:
            self.display.display_bus.register_callback(self._disp_drv.flush_ready)
        self._disp_drv.set_draw_buffers(
            self._frame_buffer1,
            self._frame_buffer2,
            len(self._frame_buffer1),
            render_mode,
        )

    def _flush_cb(self, disp_drv, area, color_p):
        width = area.x2 - area.x1 + 1
        height = area.y2 - area.y1 + 1

        # Swap the bytes in the color buffer if necessary
        if self._swap_enabled:
            lv.draw_sw_rgb565_swap(color_p, width * height)

        # we have to use the __dereference__ method because this method is
        # what converts from the C_Array object the binding passes into a
        # memoryview object that can be passed to the bus drivers
        self.display.blit(
            area.x1,
            area.y1,
            width,
            height,
            color_p.__dereference__(width * height * self._color_size),
        )
        if self._blocking:
            self._disp_drv.flush_ready()

    def _allocate_buffers(self, frame_buffer1, frame_buffer2, factor):
        if frame_buffer1 is None:
            if "RGB" in repr(self.display.display_bus):
                frame_buffer1 = self.display.display_bus.get_frame_buffer(1)
                frame_buffer2 = self.display.display_bus.get_frame_buffer(2)
            else:
                from sys import platform

                buf_size = int(
                    self.display.width
                    * self.display.height
                    * self._color_size
                    // factor
                )
                if platform == "esp32":
                    import gc
                    import heap_caps  # NOQA

                    gc.collect()

                    frame_buffer1 = heap_caps.malloc(
                        buf_size, heap_caps.CAP_DMA | heap_caps.CAP_INTERNAL
                    )
                    frame_buffer2 = heap_caps.malloc(
                        buf_size, heap_caps.CAP_DMA | heap_caps.CAP_INTERNAL
                    )

                    if frame_buffer2 is None:
                        if frame_buffer1 is not None:
                            heap_caps.free(frame_buffer1)

                        frame_buffer1 = heap_caps.malloc(
                            buf_size, heap_caps.CAP_DMA | heap_caps.CAP_SPIRAM
                        )
                        frame_buffer2 = heap_caps.malloc(
                            buf_size, heap_caps.CAP_DMA | heap_caps.CAP_SPIRAM
                        )

                    if frame_buffer1 is None:
                        if frame_buffer2 is not None:
                            heap_caps.free(frame_buffer2)
                            frame_buffer2 = None

                        frame_buffer1 = heap_caps.malloc(
                            buf_size, heap_caps.CAP_INTERNAL
                        )

                        if frame_buffer1 is None:
                            frame_buffer1 = heap_caps.malloc(
                                buf_size, heap_caps.CAP_SPIRAM
                            )
                else:
                    frame_buffer1 = bytearray(buf_size)
                    frame_buffer2 = bytearray(buf_size)

        if frame_buffer1 is None:
            raise RuntimeError("Not enough memory available to create frame buffer(s)")

        return frame_buffer1, frame_buffer2


class TouchDriver:
    display_name = "TouchDriver"

    def __init__(self, read_func, rotation, rotation_table):
        self._touch_read_func = read_func
        self._touch_rotation_table = (
            rotation_table if rotation_table else _DEFAULT_TOUCH_ROTATION_TABLE
        )

        self._indev = lv.indev_create()
        self._indev.set_type(lv.INDEV_TYPE.POINTER)
        self._indev.set_read_cb(self._touch_cb)
        self._indev.set_disp(lv.display_get_default())
        self._indev.set_group(lv.group_get_default())

        self.set_touch_rotation(rotation)

    def _touch_cb(self, touch_indev, data):
        # LVGL hands us an object called data.  We just change the state attributes when necessary.
        point = self.get_touched()
        if point:
            data.point = lv.point_t({"x": point[0], "y": point[1]})
        data.state = lv.INDEV_STATE.PRESSED if point else lv.INDEV_STATE.RELEASED

    def get_touched(self):
        # touch_read_func should return None, a point as a tuple (x, y), a point as a list [x, y] or
        # a tuple / list of points ((x1, y1), (x2, y2)), [(x1, y1), (x2, y2)], ([x1, y1], [x2, y2]),
        # or [[x1, x2], [y1, y2]].  If it doesn't, create a wrapper around your driver's read function
        # and set touch_read_func to that wrapper, or subclass TouchDriver and override .get_touched()
        # with your own logic.
        touched = self._touch_read_func()
        if touched:
            # If it looks like a point, use it, otherwise get the first point out of the list / tuple
            (x, y) = touched if isinstance(touched[0], int) else touched[0]
            if self._touch_swap_xy:
                x, y = y, x
            if self._touch_invert_x:
                x = self._touch_max_x - x
            if self._touch_invert_y:
                y = self._touch_max_y - y
            return x, y
        return None

    def set_touch_rotation(self, rotation):
        index = (rotation // 90) % len(self._touch_rotation_table)
        mask = self._touch_rotation_table[index]
        self.set_touch_rotation_mask(mask)

    def set_touch_rotation_mask(self, mask):
        # mask is an integer from 0 to 7 (or 0b001 to 0b111, 3 bits)
        # Currently, bit 2 = invert_y, bit 1 is invert_x and bit 0 is swap_xy, but that may change.
        # Your display driver should have a way to set rotation, but your touch driver may not have a way to set
        # its rotation.  You can call this function any time after you've created devices to change the rotation.
        mask = mask & 0b111
        self._touch_invert_y = True if mask >> 2 & 1 else False
        self._touch_invert_x = True if mask >> 1 & 1 else False
        self._touch_swap_xy = True if mask >> 0 & 1 else False
        self._touch_max_x = self._indev.get_disp().get_horizontal_resolution() - 1
        self._touch_max_y = self._indev.get_disp().get_vertical_resolution() - 1


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
