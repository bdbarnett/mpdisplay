from ._devices import Devices

class _BaseDisplay:
    def __init__(self):
        self.devices = []

    def register_device(self, dev, *args, **kwargs):
        """
        Register a device to be polled.

        :param dev: The type of device to register or an instance of a device.
        :type dev: int or _Device
        """
        if isinstance(dev, int):
            dev = Devices.create(dev, *args, display=self, **kwargs)

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
