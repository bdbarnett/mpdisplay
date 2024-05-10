# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
Device classes for MPDisplay's Event System.  May also be used
with other applications.  Devices are objects that poll for events
and return them.  They can be subscribed to and unsubscribed from
to receive events.

Devices can be created with Devices.create() or by calling the
constructor of the device class directly.  Devices can be
subscribed to with .subscribe() and unsubscribed from with
.unsubscribe().  Devices can be polled for events with .poll_event().
Devices can be registered with a broker device with .register_device()
and unregistered with .unregister_device().  Devices can be chained
together by setting the .broker property of a device to another device.

Devices can be created with the following types:
- Devices.BROKER: A device that polls multiple devices.
- Devices.QUEUE: A device that returns multiple types of events.
- Devices.TOUCH: A device that returns MOUSEBUTTONDOWN when touched,
    MOUSEMOTION when moved and MOUSEBUTTONUP when released.
- Devices.ENCODER: A device that returns MOUSEWHEEL events when turned,
    MOUSEBUTTONDOWN when pressed.
- Devices.KEYPAD: A device that returns KEYDOWN and KEYUP events when
    keys are pressed or released.
- Devices.JOYSTICK: A device that returns joystick events (not implemented).
"""

from micropython import const
from .events import Events


_DEFAULT_TOUCH_ROTATION_TABLE = (0b000, 0b101, 0b110, 0b011)

SWAP_XY = const(0b001)
REVERSE_X = const(0b010)
REVERSE_Y = const(0b100)


class Devices:
    UNDEFINED = const(-1)
    BROKER = const(0x00)
    QUEUE = const(0x01)
    TOUCH = const( 0x02)
    ENCODER = const(0x03)
    KEYPAD = const(0x04)
    JOYSTICK = const(0x05)

    @staticmethod
    def create(type, *args, **kwargs):
        if (cls := _mapping.get(type)):
            return cls(*args, **kwargs)
        raise ValueError("Invalid device type")
    
    @staticmethod
    def new_type(type_name: str, responses: list[int]):
        """
        Create a new device type with a list of responses.

        For example, to create the KEYPAD device type and KeypadDevice class:
        ```
        from eventsys.devices import Devices, Events

        KeypadDevice = Devices.new_type("KEYPAD", [Events.KEYDOWN, Events.KEYUP])
        KeypadDevice._poll = lambda: return Events.Key(Events.KEYDOWN, "a", 97, 0, 0, 0)
        ```
        Args:
        :param type_name: The name of the device type.
        :type type_name: str
        :param responses: A list of event types that the device can return.
        :type responses: list[int]
        """
        if not isinstance(type_name, str):
            raise ValueError("type_name must be a string")
        type_name = type_name.strip().upper()
        if not isinstance(responses, list):
            raise ValueError("responses must be a list")
        if not all(isinstance(event, int) for event in responses):
            raise ValueError("all responses must be integers")

        if hasattr(Devices, type_name):
            raise ValueError(f"Device type {type_name} already exists in Devices class.")
        class_name = type_name[0].upper() + type_name[1:].lower() + "Device"
        if class_name in [cls.__name__ for cls in _mapping.values()]:
            raise ValueError(f"Device class {class_name} already exists.")

        value = len(_mapping)
        setattr(Devices, type_name, value)
        NewClass = type(class_name, (_Device,), {"type": value, "responses": responses})
        _mapping[value] = NewClass
        return NewClass


class _Device:
    type = Devices.UNKNOWN
    responses = Events.filter
    _broker = None

    def __init__(self, read=None, data=None, read2=None, data2=None):
        self._event_callbacks = dict()

        self._read = read if read else lambda: None
        self._data = data
        self._read2 = read2 if read2 else lambda: None
        self._data2 = data2

        self._state = None
        self._user_data = None  # Can be set and retrieved by apps such as lv_mpdisplay
        self._read_cb = None  # Read callback - can be set by apps such as lv_mpdisplay

    def poll_event(self):
        if (event := self._poll()) is not None:
            if event.type in Events.filter:
                if event.type == Events.QUIT:
                    if self._broker:
                        self._broker.quit()
                if callback_list := self._event_callbacks.get(event.type):
                    for func in callback_list:
                        func(event)
                return event
        return None

    def subscribe(self, callback, event_types):
        if not callable(callback):
            raise ValueError("callback is not callable.")
        for event_type in event_types:
            if event_type not in self.responses:
                raise ValueError("the specified event_type is not a response from this device")
            callback_set = self._event_callbacks.get(event_type, set())
            callback_set.add(callback)
            self._event_callbacks[event_type] = callback_set

    def unsubscribe(self, callback, event_types):
        for event_type in event_types:
            if callback_set := self._event_callbacks.get(event_type):
                callback_set.remove(callback)

    @property
    def broker(self):
        return self._broker

    @broker.setter
    def broker(self, broker):
        self._broker = broker
        if broker is not None and self.type == Devices.TOUCH:
            self.rotation = broker.rotation

    @property
    def user_data(self):
        return self._user_data

    @user_data.setter
    def user_data(self, value):
        self._user_data = value

    def set_read_cb(self, callback):
        if callable(callback):
            self._read_cb = callback
        else:
            raise ValueError("callback must be callable")

    def read_cb(self, *args):
        """
        Used by lv_mpdisplay or other applications.
        Polls itself and passes the result to the read callback function
        saved by .set_read_cb().
        """
        if self._read_cb:
            self._read_cb(self.poll_event(), *args)


class Broker(_Device):
    type = Devices.BROKER
    responses = Events.filter

    def __init__(self):
        super().__init__()
        self.devices = []  # List of devices to poll
        self._device_callbacks = dict()

    def subscribe(self, callback, event_types=None, device_types=None):
        if not callable(callback):
            raise ValueError("callback is not callable.")
        if device_types is not None and event_types is not None:
            raise ValueError("set one of device_type or event_type but not both.")
        if device_types is None and event_types is None:
            raise ValueError("set one of device_type or event_type but not both.")
        if device_types is not None:
            for device_type in device_types:
                callback_set = self._device_callbacks.get(device_type, set())
                callback_set.add(callback)
                self._device_callbacks[device_type] = callback_set
        else:
            super().subscribe(callback, event_types)

    def unsubscribe(self, callback, event_types=None, device_types=None):
        if device_types is not None and event_types is not None:
            raise ValueError("set one of device_type or event_type but not both.")
        if device_types is None and event_types is None:
            raise ValueError("set one of device_type or event_type but not both.")
        if device_types is not None:
            for device_type in device_types:
                if callback_set := self._device_callbacks.get(device_type):
                    callback_set.remove(callback)
        else:
            super().unsubscribe(callback, event_types)

    def create_device(self, type=Devices.QUEUE, **kwargs):
        """
        Create a device object.

        :param type: The type of device to create.
        :type dev: int
        """
        dev = Devices.create(type, **kwargs)
        self.register_device(dev)
        return dev

    def register_device(self, dev):
        """
        Register a device to be polled.

        :param dev: The device object to register.
        :type dev: _Device
        """
        dev.broker = self
        self.devices.append(dev)

    def unregister_device(self, dev):
        """
        Unregister a device.

        :param dev: The device object to unregister.
        :type dev: _Device
        """
        if dev in self.devices:
            self.devices.remove(dev)
            dev.broker = None

    def _poll(self):
        for device in self.devices:
            if (event := device.poll_event()) is not None:
                if callback_list := self._device_callbacks.get(device.type):
                    for func in callback_list():
                        func(event)
                return event
        return None


class QueueDevice(_Device):
    type = Devices.QUEUE
    responses = Events.filter

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._data is None:
            self._data = Events.filter
        if hasattr(self._broker, "touch_scale"):
            self.scale = self._broker.touch_scale
        else:
            self.scale = 1

    def _poll(self):
        if (event := self._read()) is not None:
            if event.type in self._data:
                if (scale := self.scale) != 1:
                    if event.type in (Events.MOUSEMOTION, Events.MOUSEBUTTONDOWN, Events.MOUSEBUTTONUP):
                        event.pos = (int(event.pos[0] // scale), int(event.pos[1] // scale))
                        if event.type == Events.MOUSEMOTION:
                            event.rel = (event.rel[0] // scale, event.rel[1] // scale)
                return event
        return None


class TouchDevice(_Device):
    """
    Only reports mouse button 1.
    """
    type = Devices.TOUCH
    responses = (Events.MOUSEMOTION, Events.MOUSEBUTTONDOWN,  Events.MOUSEBUTTONUP)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._data is None:  # self._data is a rotation table
            self._data = _DEFAULT_TOUCH_ROTATION_TABLE

        self.rotation = self._broker.rotation if self._broker else 0

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value % 360

        # _mask is an integer from 0 to 7 (or 0b001 to 0b111, 3 bits)
        # Currently, bit 2 = invert_y, bit 1 is invert_x and bit 0 is swap_xy, but that may change.
        self._mask = self._data[self._rotation // 90]

    def _poll(self):
        # _read should return None, a point as a tuple (x, y), a point as a list [x, y] or
        # a tuple / list of points ((x1, y1), (x2, y2)), [(x1, y1), (x2, y2)], ([x1, y1], [x2, y2]),
        # or [[x1, y1], [x2, y2]].  If it doesn't, create a wrapper around your driver's read function
        # and set touch_callback to that wrapper, or subclass TouchDriver and override .get_touched()
        # with your own logic.  A point tuple/list may have additional values other than x and y that
        # are ignored.  x and y must come first.  Some multi-touch drivers may return extra data such
        # as the index of the touch point (1st, 2nd, etc).  Only the first point in the list will be
        # used and any extra data in that point will be ignored.

        try:  # If called too quickly, the touch driver may raise OSError: [Errno 116] ETIMEDOUT
            touched = self._read()
        except OSError:
            return None
        if touched:
            last_pos = self._state
            # If it looks like a point, use it, otherwise get the first point out of the list / tuple
            (x, y, *_) = touched if isinstance(touched[0], int) else touched[0]

            if self._mask & SWAP_XY:
                x, y = y, x
            if self._mask & REVERSE_X:
                x = self._broker.width - x - 1
            if self._mask & REVERSE_Y:
                y = self._broker.height - y - 1
            self._state = (x, y)
            if last_pos is not None:
                last_x, last_y = last_pos
                return Events.Motion(
                    Events.MOUSEMOTION,
                    self._state,
                    (x - last_x, y - last_y),
                    (1, 0, 0),
                    False,
                    None,
                )
            else:
                return Events.Button(Events.MOUSEBUTTONDOWN, self._state, 1, False, None)
        elif self._state is not None:
            last_pos = self._state
            self._state = None
            return Events.Button(Events.MOUSEBUTTONUP, last_pos, 1, False, None)
        return None


class EncoderDevice(_Device):
    type = Devices.ENCODER
    responses = (Events.MOUSEWHEEL, Events.MOUSEBUTTONDOWN, Events.MOUSEBUTTONUP)

    def __init__(self, *args, **kwargs):
        """
        self._data is the mouse button number to report for the switch.
        Default is 2 (middle mouse button).  If the mouse button number is even,
        the wheel will report vertical (y) movement.  If the mouse button number is odd,
        the wheel will report horizontal (x) movement.  This corresponds to a typical mouse
        wheel being button 2 and the wheel moving vertically.  It also correponds to
        scrolling horizontally on a touchpad with two-finger scrolling and using the right button.
        """
        super().__init__(*args, **kwargs)
        self._state = (0, False)  # (position, pressed)
        self._data = self._data if self._data else 2  # Default to middle mouse button

    def _poll(self):
        # _read should return a running total of steps turned.  For instance, if the current
        # position is 800 and it is moved 5 right then 3 left, the callback should return 802.
        # The event returned will have the delta, 2 in this example.
        # _read2 should also be callable and return truthy if the switch is pressed,
        # falsy if it is not.
        last_pos, last_pressed = self._state
        pressed = self._read2()
        if pressed != last_pressed:
            self._state = (last_pos, pressed)
            return Events.Button(
                Events.MOUSEBUTTONDOWN if pressed else Events.MOUSEBUTTONUP,
                (0, 0),
                self._data,
                False,
                None,
            )

        pos = self._read()
        if pos != last_pos:
            steps = pos - last_pos
            self._state = (pos, last_pressed)
            if self._data % 2 == 0:
                return Events.Wheel(Events.MOUSEWHEEL, False, 0, steps, 0, steps, False, None)
            return Events.Wheel(Events.MOUSEWHEEL, False, steps, 0, steps, 0, False, None)
        return None


class KeypadDevice(_Device):
    type = Devices.KEYPAD
    responses = (Events.KEYDOWN, Events.KEYUP)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = set()

    def _poll(self):
        # _read should return a list, tuple or set of keys pressed or None if no keys are pressed.
        # The keys should be integers representing the key code.  The callback should return
        # all keys currently pressed.  If a key is held down, it should be returned in every call to
        # the callback until it is released.
        # For example, see https://github.com/adafruit/Adafruit_CircuitPython_MatrixKeypad
        keys = set(self._read())
        released = self._state - keys
        if released:
            key = released.pop()
            self._state.remove(key)
            return Events.Key(Events.KEYUP, chr(key), key, 0, 0)
        pressed = keys - self._state
        if pressed:
            key = pressed.pop()
            self._state.add(key)
            return Events.Key(Events.KEYDOWN, chr(key), key, 0, 0)
        return None


class JoystickDevice(_Device):
    type = Devices.JOYSTICK
    responses = (Events.JOYAXISMOTION, Events.JOYBALLMOTION, Events.JOYHATMOTION,
                 Events.JOYBUTTONDOWN, Events.JOYBUTTONUP)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _poll(self):
        raise NotImplementedError("JoystickDevice.read() not implemented")


_mapping = {
    Devices.BROKER: Broker,
    Devices.QUEUE: QueueDevice,
    Devices.TOUCH: TouchDevice,
    Devices.ENCODER: EncoderDevice,
    Devices.KEYPAD: KeypadDevice,
    Devices.JOYSTICK: JoystickDevice,
}
