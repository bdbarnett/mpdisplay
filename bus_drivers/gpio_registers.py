import sys


_hal_gpio_registers = {
    "esp32": {
        "odr_offset": 0x4,
        "set_offset": 0x8,
        "clr_offset": 0xC,
        "pins_per_port": 32,
        "port_regs": {
            "esp32s3": (0x60004000, 0x6000400C),
            "esp32c3": (0x60004000, 0x6000400C),
            "esp32c2": (0x60004000, 0x6000400C),
            "esp32p4": (0x60091000, 0x6009100C),
            "esp32c6": (0x60091000, 0x6009100C),
            "esp32c5": (0x60091000, 0x6009100C),
            "esp32h2": (0x60091000, 0x6009100C),
            "esp32s2": (0x3F404000, 0x3F40400C),
            "*": (0x3FF44000, 0x3FF4400C),
        },
    },
    "samd": {
        "odr_offset": 0x10,
        "set_offset": 0x18,
        "clr_offset": 0x14,
        "pins_per_port": 32,
        "port_regs": {
            "samd21": (0x41004400, 0x41004480),
            "samd51": (0x41008000, 0x41008080, 0x41008100, 0x41008180),
        },
    },
    "rp2": {
        "odr_offset": 0x10,
        "set_offset": 0x14,
        "clr_offset": 0x18,
        "pins_per_port": 32,
        "port_regs": {
            "rp2040": (0x50200000,),
        },
    },
    "nrf": {
        "odr_offset": 0x4,
        "set_offset": 0x8,
        "clr_offset": 0xC,
        "pins_per_port": 32,
        "port_regs": {
            "nrf5": (0x50000000, 0x50000300),
            "nrf9": (0x40842000,),
        },
    },
    "mimxrt": {
        "odr_offset": 0x0,
        "set_offset": 0x84,
        "clr_offset": 0x88,
        "pins_per_port": 32,
        "port_regs": {
            "mimxrt10": (
                0x401B8000,
                0x401BC000,
                0x401C0000,
                0x401C4000,
                0x400C0000,
                0x42000000,
                0x42004000,
                0x42008000,
                0x4200C000,
            ),
            "mimxrt11": (
                0x4012C000,
                0x40130000,
                0x40134000,
                0x40138000,
                0x4013C000,
                0x40140000,
                0x40C5C000,
                0x40C60000,
                0x40C64000,
                0x40C68000,
                0x40C6C000,
                0x40C70000,
                0x40CA0000,
            ),
        },
    },
    "renasas-ra": {
        "odr_offset": 0x0,  # lower 16 bits = direction, upper 16 bits = output
        "set_reset_offset": 0x8,  # lower 16 bits set, upper 16 bits reset
        "pins_per_port": 16,
        "port_regs": {
            "ra6m5": (
                0x40080000,
                0x40080020,
                0x40080040,
                0x40080060,
                0x40080080,
                0x400800A0,
                0x400800C0,
                0x400800E0,
                0x40080100,
                0x40080120,
                0x40080140,
                0x40080160,
            ),
            "*": (
                0x40040000,
                0x40040020,
                0x40040040,
                0x40040060,
                0x40040080,
                0x400400A0,
                0x400400C0,
                0x400400E0,
                0x40040100,
                0x40040120,
            ),
        },
    },
    "stm32": {
        "odr_offset": 0x14,  # 16 bits only
        "set_reset_offset": 0x18,  # lower 16 bits set, upper 16 bits reset
        "pins_per_port": 16,
        "port_regs": {
            "*": (
                0x50000000,
                0x50000400,
                0x50000800,
                0x50000C00,
                0x50001000,
                0x50001400,
                0x50001800,
                0x50001C00,
                0x50002000,
            ),
        },
    },
}


class GPIO_SET_CLR_REGISTERS:
    def __init__(self):
        platform = sys.platform.lower()
        _machine = sys.implementation._machine.lower().replace("-", "").replace("_", "")

        platform_data = _hal_gpio_registers[platform]
        self._port_regs = None

        for mcu, port_regs in platform_data["port_regs"].items():
            if mcu in _machine:
                self._port_regs = port_regs
                break

        if self._port_regs is None:
            if "*" in platform_data["port_regs"].keys():
                self._port_regs = platform_data["port_regs"]["*"]
            else:
                raise NotImplementedError(
                    f"GPIO_SET_CLR_REGISTERS not implemented for {platform} on {_machine}"
                )

        self.pins_per_port = platform_data["pins_per_port"]
        self._set_offset = (
            platform_data["set_offset"] if self.pins_per_port == 32 else None
        )
        self._clr_offset = (
            platform_data["clr_offset"] if self.pins_per_port == 32 else None
        )
        self._set_reset_offset = (
            platform_data["set_reset_offset"] if self.pins_per_port == 16 else None
        )

    def _port_reg(self, pin):
        return self._port_regs[pin // self.pins_per_port]

    def get_set_clr_regs(self, pin, active_high=True):
        if self.pins_per_port != 32:
            return (self.set_reset_reg(pin), self.set_reset_reg(pin))
        else:
            if active_high:
                return (self.set_reg(pin), self.clr_reg(pin))
            else:
                return (self.clr_reg(pin), self.set_reg(pin))

    def get_set_clr_masks(self, pin, active_high=True):
        if self.pins_per_port == 32:
            return (self.mask(pin), self.mask(pin))
        else:
            if active_high:
                return (self.mask_set(pin), self.mask_clr(pin))
            else:
                return (self.mask_clr(pin), self.mask_set(pin))

    ############################### 32-bit ports ###############################

    def set_reg(self, pin):
        if self._set_offset is None:
            return None
        return self._port_reg(pin) + self._set_offset

    def clr_reg(self, pin):
        if self._clr_offset is None:
            return None
        return self._port_reg(pin) + self._clr_offset

    def mask(self, pin):
        return 1 << (pin % self.pins_per_port)
    
    ############################### 16-bit ports ###############################

    def set_reset_reg(self, pin):
        if self._set_reset_offset is None:
            return None
        return self._port_reg(pin)[0] + self._set_reset_offset

    def mask_set(self, pin):
        return (1 << (pin % self.pins_per_port)) & 0xFFFF

    def mask_clr(self, pin):
        return 1 << ((pin % self.pins_per_port) + 16)
