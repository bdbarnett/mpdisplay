from machine import Pin as _Pin


def _init_module():
    from sys import platform, implementation
    from . import gpio_data

    data = gpio_data[platform.lower()]
    if "BSRR" in data:
        GPIO_Pin.BSRR = data["BSRR"]
    else:
        GPIO_Pin.SET = data["SET"]
        GPIO_Pin.CLR = data["CLR"]
    
    if hasattr(_Pin, "gpio"):  # If the gpio method is already implemented
        return

    # Convert to lowercase and remove - and _ from sys.implementation._machine
    # which is in the format "Generic ESP32S3 module with ESP32S3"
    machine = implementation._machine.lower().replace("-", "").replace("_", "")
    for mcu, gpios in data["gpios"].items():  # Find the GPIOs for the current machine
        if mcu in machine:  # If the mcu is in the machine name
            GPIO_Pin._gpios = gpios  # Set the GPIOs and break
            break
    if GPIO_Pin._gpios is None:  # If the GPIOs are not set
        if "*" in data["gpios"].keys():  # If there is a wildcard
            GPIO_Pin._gpios = data["gpios"]["*"]  # Set the GPIOs to the wildcard
        else:
            raise NotImplementedError(
                f"class GPIO_Pin not implemented for {platform} on {machine}"
            )


class GPIO_Pin(_Pin):
    PPP = None
    SET = None
    CLR = None
    BSRR = None
    _gpios = None

    def __init__(self, id, *args, **kwargs):
        if hasattr(id, "names"):
            id = id.names()[1]
        super().__init__(id, *args, **kwargs)
        self._id = id if isinstance(id, int) else None
        if self.BSRR is None:
            self.PPP = 32
        else:
            self.PPP = 16

    def pin(self):
        if hasattr(super(), "pin"):
            return super().pin()
        if isinstance(self._id, int):
            return self._id & (self.PPP - 1)
        raise NotImplementedError("GPIO_Pin.pin not implemented for this platform")

    def port(self):
        if hasattr(super(), "port"):
            return super().port()
        if isinstance(self._id, int):
            return self._id // self.PPP
        raise NotImplementedError("GPIO_Pin.port not implemented for this platform")

    def gpio(self):
        if hasattr(super(), "gpio"):
            x = super().gpio()  # returns as signed int
            if x < 0:  # if it is negative
                x = x + (1 << 31)  # convert it to unsigned int
            return x
        return self._gpios[self.port()]


_init_module()