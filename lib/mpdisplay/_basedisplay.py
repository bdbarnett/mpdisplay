from ._devices import Devices

class _BaseDisplay:
    def __init__(self):
        self.devices = []

        # Function to call when the window close button is clicked.
        # Set it like `display_drv.quit_func = cleanup_func` where `cleanup_func` is a 
        # function that cleans up resources and calls `sys.exit()`.
        # .poll_event() must be called periodically to check for the quit event.
        self.quit_func = lambda: print(".quit_func not set")
        self._event = bytearray(56)  # The largest size of an SDL_Event struct

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
