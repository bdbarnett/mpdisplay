import sys


if sys.platform == "pyboard":
    import stm
    gpio_data = {
        "pyboard": {
            "BSRR": stm.GPIO_BSRR,
            }
        }
else:
    gpio_data = {
        "esp32": {
            "SET": 0x8,
            "CLR": 0xC,
            "gpios": {
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
            "SET": 0x18,
            "CLR": 0x14,
            "gpios": {
                "samd21": (0x41004400, 0x41004480),
                "samd51": (0x41008000, 0x41008080, 0x41008100, 0x41008180),
            },
        },
        "rp2": {  # See 3.1.11 at https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf
            "SET": 0x14,
            "CLR": 0x18,
            "gpios": {
                "rp2040": (0xD0000000,),  # The SIO registers start at a base address of 0xd0000000 (defined as SIO_BASE in SDK).
            },
        },
        "nrf": {
            "SET": 0x8,
            "CLR": 0xC,
            "gpios": {
                "nrf5": (0x50000000, 0x50000300),
                "nrf9": (0x40842000,),
            },
        },
        "mimxrt": {
            "SET": 0x84,
            "CLR": 0x88,
            "gpios": {
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
            "BSRR": 0x8,
            "gpios": {
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
    }
