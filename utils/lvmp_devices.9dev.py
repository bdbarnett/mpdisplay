"""
Note: most LVGL Micropython examples have `import display_driver` as their first line.
      You can change that to any file you want.  I'm leaving it at that in this example
      to make it work with those examples.

Example display_driver.py:
#
# This example display_driver.py references display_config, i2c_config and encoders_config.
# In this example, those files import the Micropython device drivers and create the devices.
# Those are your files, and you can combine them if you want and name them what you want.
#
import lvgl as lv                        # Not needed in this file unless you also create lv objects below
from display_config import display_drv   # Your display config file here, display_drv already setup
from i2c_config import touch_drv, rtc    # Your i2c config file here, `rtc` is just an example
from encoders_config import enc1, enc2,  # Your encoders and encoder buttons config file here
    enc_btn1_pressed, enc_btn2_pressed   # These are functions, not devices or drivers
from lvmp_devices import Devices         # The star of the show :)

devices = Devices(display_drv=display_drv, bgr=False, factor=4,
                  blit_func=display_drv.blit, get_buf_func=display_drv.get_buf,
                  touch_read_func=touch_drv.touch_read, touch_rotation=3,
                  encoder_read_funcs=[enc1.value, enc2.value],  # Assumes encoder driver has a `value` method
                  encoder_pressed_funcs=[enc_btn1_pressed, enc_btn2_pressed]
                  )

# You can add other non-LVGL devices and even functions now if you want.  The above i2c_config file
# creates an rtc, which could be an external Real Time Clock included on your dev board.  Add it to
# `devices` like the following and you'll be able to access it in main.py:

devices.rtc = rtc

Example main.py

import display_driver
import lvgl as lv

devices = display_driver.devices  # Or change the first line to `from display_driver import devices`.

# All encoders created in display_driver.devices are set to the same group.  Not very useful.
# If you have more than one encoder, you'll want to add and assign groups like this:

group1 = lv.group_get_default()
devices.encoders[0].indev.set_group(group1)

group2 = lv.group_create()
devices.encoders[1].indev.set_group(group2)

# If your dev board has an external realtime clock as in the example display_driver,
# Here is an example of how you might access it:

print(f"RTC time:     {devices.rtc.datetime()}")

# You can list all of the objects and methods available in `devices` like this:

devices.list()

# That's it.  You're ready to add more code below!  Try copying some examples from:
# https://docs.lvgl.io
        
"""

import lvgl as lv
import lv_utils

class Devices():
    """
    Note:  If display_drv is specified, blit_func MUST also be specified!!!!!!
    All other arguments are optional and should match your hardware / drivers.
    
    In version 9.0-dev, LVGL dropped reversing color byte order for SPI transactions,
    so lv.COLOR_FORMAT.NATIVE_REVERSED doesn't exist.  BGR is ignored for now.
    """

    def __init__(self, *, display_drv=None, bgr=False, factor=10, double_buffer=True,
                 blit_func=None, register_ready_cb_func=None, get_buf_func=None,
                 height=None, width=None, render_mode=lv.DISPLAY_RENDER_MODE.PARTIAL,
                 wrap_flush=True, touch_read_func=None, touch_rotation=None,
                 encoder_read_funcs=None, encoder_pressed_funcs=None,
                 init=True, asynchronous=False, exception_sink=None, default_group=True):

        self.event_loop = self._init_lv(asynchronous, exception_sink) if init else None
        self.display = self._attach_display(display_drv, bgr, factor, double_buffer,
                                            blit_func, register_ready_cb_func, get_buf_func,
                                            height, width, render_mode, wrap_flush,
                                            ) if blit_func else None
        self.initial_group = self._create_group(default_group)
        self.touch_indev = self._attach_touch(touch_read_func, touch_rotation) if touch_read_func else None
        self.encoders = self._attach_encoders(encoder_read_funcs, encoder_pressed_funcs) if encoder_read_funcs else None

####################### Generic methods

    @staticmethod
    def _init_lv(asynchronous, exception_sink):        
        if not lv.is_initialized():
            lv.init()
        if not lv_utils.event_loop.is_running():
            return lv_utils.event_loop(asynchronous=asynchronous, exception_sink=exception_sink)
        return None

    @staticmethod
    def _create_group(default_group):
        group = lv.group_create()
        if default_group: group.set_default()
        return group
        
    def _indev_setup(self, indev):
        indev.set_group(self.initial_group if self.initial_group else lv.group_get_default())
        indev.set_disp(self.display if self.display else lv.display_get_default())

####################### Display methods

    def _attach_display(self, display_drv, bgr, factor, double_buffer,
                        blit_func, register_ready_cb_func, get_buf_func,
                        height, width, render_mode, wrap_flush):
        self.display_drv = display_drv
        self._blit = blit_func
        self._blit_is_blocking = True
        
        width = width if width else self.display_drv.width()
        height = height if height else self.display_drv.height()
        
        self._get_buffers(width, height, factor, double_buffer, get_buf_func)
        
        display = lv.display_create(width, height)
        if register_ready_cb_func:
            self._blit_is_blocking = False
            register_ready_cb_func(display.flush_ready, display)
        display.set_flush_cb(self._flush_cb if wrap_flush else self._blit)
        display.set_draw_buffers(self._buf1, self._buf2, len(self._buf1), render_mode)
        display.set_color_format(lv.COLOR_FORMAT.NATIVE)
        return display

    def _flush_cb(self, display, area, color):
#        print(f"Blitting ({area.x1}, {area.y1}) to ({area.x2}, {area.y2})")
        self._blit(area.x1, area.y1, w:=(area.x2-area.x1+1), h:=(area.y2-area.y1+1), color.__dereference__(lv.color_t.__SIZE__*w*h))
        if self._blit_is_blocking: self.display.flush_ready()

    def _get_buffers(self, width, height, factor, double_buffer, get_buf_func):
        buf_size = (width * height * lv.color_t.__SIZE__) // factor
        self._buf1 = get_buf_func(buf_size) if get_buf_func else bytearray(buf_size)
        self._buf2 = get_buf_func(buf_size) if get_buf_func else bytearray(buf_size) if double_buffer else None

    def deinit(self):
        raise NotImplementedError(".deinit() has not been implemented yet.")

####################### Touch methods

    def _attach_touch(self, touch_read_func, touch_rotation):
        self._touch_read = touch_read_func
        self.set_touch_rotation(touch_rotation)

        touch_indev = lv.indev_create()
        touch_indev.set_type(lv.INDEV_TYPE.POINTER)
        touch_indev.set_read_cb(self._touch_cb)
        self._indev_setup(touch_indev)
        return touch_indev

    def _touch_cb(self, touch_indev, data):
        # LVGL hands us an object called data.  We just change the state attributes when necessary.
        if point := self.get_touched():
            data.point = lv.point_t( {'x': point[0], 'y': point[1]} )
        data.state = lv.INDEV_STATE.PRESSED if point else lv.INDEV_STATE.RELEASED

    def get_touched(self):
        # touch_read_func should return None, a point as a tuple (x, y), a point as a list [x, y] or 
        # a tuple / list of points ((x1, y1), (x2, y2)), [(x1, y1), (x2, y2)], ([x1, y1], [x2, y2]),
        # or [[x1, x2], [y1, y2]].  If it doesn't, create a wrapper around your driver's read function
        # and set touch_read_func to that wrapper, or subclass Devices and override .get_touched()
        # with your own logic.
        if touched := self._touch_read():
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
        self._max_x = self.display_drv.width() - 1         ########### Change to self.display.width()
        self._max_y = self.display_drv.height() - 1         ########### Change to self.display.height()
        if self._swap_xy:
            self._max_x, self._max_y = self._max_y, self._max_x

####################### Encoder methods

    def _attach_encoders(self, encoder_read_funcs, encoder_pressed_funcs):
        """
        encoder_read_funcs:  List of functions to read encoder(s) values
        encoder_pressed_funcs: List of functions to read encoder button(s) values.
        len(encoder_read_funcs) will be created. If there are fewer encoder_pressed_funcs, the
        remaining encoders will be created without buttons.  If there are more encoder_pressed_funcs,
        the remaining buttons will be ignored.  See the notes on Encoder class for more details.
        """
        encoders = []
        for i, read_func in enumerate(encoder_read_funcs):
            if len(encoder_pressed_funcs) > i:
                pressed_func = encoder_pressed_funcs[i]
            else:
                pressed_func = None
            encoder = Encoder(read_func, pressed_func)
            self._indev_setup(encoder.indev)
            encoders.append(encoder)
        return encoders

####################### Utility methods
        
    def list(self):
        return sorted([x for x in dir(self) if not x.startswith("_")])

    
class Encoder():
    """
    read_func:  Function to read the value of the encoder.  Value should be continuous, not incremental.
    pressed_func:  Function that returns a truthy value if the button is pressed, falsy if not.
                   If pressed_func isn't specified, it will be configured to always return False (never pressed).
                   If you are reading a Pin object that has a pullup and normally open switch,
                   create a function to change to the opposite value, for example:
                        def is_encoder_pressed(): not button_pin.value(), or
                        is_encoder_pressed = lambda : not button_pin.value()
    long_press_duration:  Number of milliseconds for button to be pressed before calling the long_pressed method
    """
    def __init__(self, read_func, pressed_func=None, long_press_duration=500):
        from time import ticks_diff, ticks_ms
        
        self.value = read_func
        self.pressed = pressed_func if pressed_func else lambda : False
        self.long_press_duration = long_press_duration
        
        # Grab the initial state
        self._last_value = read_func()
        self._last_pressed = pressed_func()
        self._last_ticks = -1  # Set to a falsy value to indicate we aren't counting.

        # Create the input device, set it's type and read callback function.
        self.indev = lv.indev_create()
        self.indev.set_type(lv.INDEV_TYPE.ENCODER)
        self.indev.set_read_cb(self._read_cb)

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
        if self.indev.get_group().get_editing():
            # escape out of it.
            self.indev.get_group().set_editing(False)
        # Otherwise, if an object has focus
        elif focused_obj := self.indev.get_group().get_focused():
            # send a LONG_PRESSED event to that object.
            focused_obj.send_event(lv.EVENT.LONG_PRESSED, None)

