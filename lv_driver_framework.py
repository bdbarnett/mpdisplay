# SPDX-FileCopyrightText: 2023 Brad Barnett and Kevin Schlosser
#
# SPDX-License-Identifier: MIT

import lvgl as lv
import lcd_bus
from time import ticks_ms, ticks_diff


class DisplayDriver():

    display_name = 'DisplayDriver'

    def __init__(self, display, color_space, frame_buffer1, frame_buffer2=None):

        if not lv.is_initialized():
            lv.init()

        self._color_size = lv.color_format_get_size(color_space)

        self.display = display
        self._disp_drv = lv.display_create(self.display.width, self.display.height)
        self._disp_drv.set_color_format(color_space)

        self._disp_drv.set_flush_cb(self._flush_cb)

        if isinstance(self.display.display_bus, lcd_bus.RGBBus):
            self._disp_drv.set_draw_buffers(
                frame_buffer1,
                frame_buffer2,
                len(frame_buffer1),
                lv.DISP_RENDER_MODE.FULL
            )
        else:
            self._disp_drv.set_draw_buffers(
                frame_buffer1,
                frame_buffer2,
                len(frame_buffer1),
                lv.DISP_RENDER_MODE.PARTIAL
            )

        self.display.display_bus.register_callback(self._flush_ready_cb, self._disp_drv)

    def _flush_cb(self, disp_drv, area, color_p):
        # we have to use the __dereference__ method because this method is
        # what converts from the C_Array object the binding passes into a
        # memoryview object that can be passed to the bus drivers
        self.display.blit(area.x1, area.y1, w:=(area.x2-area.x1+1), h:=(area.y2-area.y1+1), color_p.__dereference__(w*h*self._color_size))

    # we always register this callback no matter what. This is what tells LVGL
    # that the buffer is able to be written to. If this callback doesn't get
    # registered then the flush function is going to block until the buffer
    # gets emptied. Everything is handeled internally in the bus driver if
    # using DMA and double buffer.
    def _flush_ready_cb(self, disp_drv):
        disp_drv.flush_ready()

class TouchDriver():

    display_name = 'TouchDriver'

    def __init__(self, touch_read_func, touch_rotation=0):
        self._touch_read_func = touch_read_func

        self._indev = lv.indev_create()
        self._indev.set_type(lv.INDEV_TYPE.POINTER)
        self._indev.set_read_cb(self._touch_cb)
        self._indev.set_disp(lv.disp_get_default())
        self._indev.set_group(lv.group_get_default())

        self.set_touch_rotation(touch_rotation)

    def _touch_cb(self, touch_indev, data):
        # LVGL hands us an object called data.  We just change the state attributes when necessary.
        if point := self.get_touched():
            data.point = lv.point_t( {'x': point[0], 'y': point[1]} )
        data.state = lv.INDEV_STATE.PRESSED if point else lv.INDEV_STATE.RELEASED

    def get_touched(self):
        # touch_read_func should return None, a point as a tuple (x, y), a point as a list [x, y] or 
        # a tuple / list of points ((x1, y1), (x2, y2)), [(x1, y1), (x2, y2)], ([x1, y1], [x2, y2]),
        # or [[x1, x2], [y1, y2]].  If it doesn't, create a wrapper around your driver's read function
        # and set touch_read_func to that wrapper, or subclass TouchDriver and override .get_touched()
        # with your own logic.
        if touched := self._touch_read_func():
            # If it looks like a point, use it, otherwise get the first point out of the list / tuple
            (x, y) = touched if isinstance(touched[0], int) else touched[0]
            if self._touch_rotation is not None:
                if self._swap_xy:
                    x, y = y, x
                if self._invert_x:
                    x = self._max_x - x
                if self._invert_y:
                    y = self._max_y - y
            return x, y
        return None

    def set_touch_rotation(self, touch_rotation):
        # Touch_rotation is an integer from 0 to 7 (3 bits)
        # Currently, bit 0 = invert_y, bit 1 is invert_x and bit 2 is swap_xy, but that may change
        # if I learn displays are consistent with their rotations and this doesn't match them.
        # Your display driver should have a way to set rotation before you add it to Devices,
        # but your touch driver may not have a way to set its rotation.  You can call this function
        # any time after you've created devices to change the rotation.
        self._touch_rotation = touch_rotation // 8 if touch_rotation else None
        self._invert_y = True if touch_rotation & 1 else False
        self._invert_x = True if touch_rotation >> 1 & 1 else False
        self._swap_xy = True if touch_rotation >> 2 & 1 else False
        self._max_x = self._indev.get_disp.get_hor_res() - 1
        self._max_y = self._indev.get_disp.get_ver_res() - 1

class EncoderDriver():
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

    display_name = 'EncoderDriver'

    def __init__(self, read_func, pressed_func=None, long_press_duration=500):
        
        self.value = read_func
        self.pressed = pressed_func if pressed_func else lambda : False
        self.long_press_duration = long_press_duration
        
        # Grab the initial state
        self._last_value = read_func()
        self._last_pressed = pressed_func()
        self._last_ticks = -1  # Set to a falsy value to indicate we aren't counting.

        # Create the input device, set it's type and read callback function.
        self._indev = lv.indev_create()
        self._indev.set_type(lv.INDEV_TYPE.ENCODER)
        self._indev.set_read_cb(self._read_cb)
        self._indev.set_disp(lv.disp_get_default())
        self._indev.set_group(lv.group_get_default())

    def _read_cb(self, indev, data):
        # LVGL hands us an object called data.  We just change the enc_diff and/or state attributes if necessary.

        # Read the encoder
        value = self.value()
        if value != self._last_value:
            data.enc_diff = value - self._last_value  # <- Reverse these to change direction of all encoders
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
            if self._last_ticks and ticks_diff(ticks_ms, self._last_ticks) > self.long_press_duration:
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
