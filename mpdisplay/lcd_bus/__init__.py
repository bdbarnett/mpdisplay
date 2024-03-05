# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

'''
lcd_bus - Provides MicroPython drivers for SPI and I80 display buses similiar to the
https://github.com/kdschlosser/lcd_bus written in C.

Attempts to load a platform-specific module such as _i80bus_rp2 or _spibus_esp32 first,
then falls back to a generic module such as _i80bus or _spibus if the platform-specific
module doesn't exist.  This prevents loading unused modules.

Lazy loader for on the fly loading of attributes.  See:
https://peps.python.org/pep-0562/
and 
https://github.com/peterhinch/micropython-samples/blob/master/import/IMPORT.md#2-python-packages-and-the-lazy-loader
'''
from sys import platform
from micropython import const


# Memory capabilities.  Maintains compatibility with mp_lcd_bus's allocate_framebuffer
MEMORY_32BIT = const(2)
MEMORY_8BIT = const(4)
MEMORY_DMA = const(8)
MEMORY_SPIRAM = const(1024)
MEMORY_INTERNAL = const(2048)
MEMORY_DEFAULT = const(4096)


def __getattr__(attr):
    # Lazy loader, effectively does:
    #   global attr
    #   try:
    #       from ._module_platform import attr
    #   except ImportError:
    #       from ._module import attr
    if attr not in ("SPIBus", "I80Bus", "SDL2Bus"):
        raise AttributeError(f"{attr} not provided by lcd_bus")
    
    # module is the module name, e.g. "_i80bus_rp2" or "_i80bus"
    try:
        # Try to load the platform-specific module
        module = "".join(["_", attr.lower(), "_", platform])
        value = getattr(__import__(module, None, None, [], 1), attr)
    except ImportError:
        # If the platform-specific module doesn't exist, then use the generic module
        module = "".join(["_", attr.lower()])
        value = getattr(__import__(module, None, None, [], 1), attr)
    globals()[attr] = value

    # Print a message to the console indicating which module the attribute was imported from
    # Comment out the following line to disable the message
    print(f"Imported {value} from {module}.py")

    return value