from ._devices import Devices, Events

class _BaseDisplay:
    def __init__(self):
        self.devices = []

        # Function to call when the window close button is clicked.
        # Set it like `display_drv.quit_func = cleanup_func` where `cleanup_func` is a 
        # function that cleans up resources and calls `sys.exit()`.
        # .poll_event() must be called periodically to check for the quit event.
        self.quit_func = lambda: print(".quit_func not set")

    def register_device(self, dev, *args, **kwargs):
        """
        Register a device to be polled.

        :param dev: The type of device to register or an instance of a device.
        :type dev: int or _Device
        """
        if isinstance(dev, int):
            dev = Devices.create(dev, *args, display=self, **kwargs)
        else:
            dev.display = self

        self.devices.append(dev)
        return dev

    def unregister_device(self, dev):
        """
        Unregister a device.

        :param dev: The device object to unregister.
        :type dev: _Device
        """
        if dev in self.devices:
            self.devices.remove(dev)
            dev.display = None

    def poll_event(self):
        """
        Provides a similar interface to PyGame's and SDL2's event queues.
        The returned event is a namedtuple from the Events class.
        The type of event is in the .type field.

        Currently returns as soon as an event is found and begins with the first
        device registered the next time called, placing priority on the first
        device registered.  Register less frequently fired or higher priority devices
        first if you have problems with this.  This may change in the future.

        It is recommended to run poll_event repeatedly until all events have been
        processed on a timed schedule.  For instance, schedule the following on a recurring basis:

            while (event := display_drv.poll_event()):
                ...
        """
        for device in self.devices:
            if (event := device.read()) is not None:
                if event.type in Events.types:
                    if self._event.type == Events.QUIT:
                        self.quit_func()
                    return self._event
        return None
