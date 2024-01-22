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


def __getattr__(attr):
    # Lazy loader, effectively does:
    #   global attr
    #   try:
    #       from ._module_platform import attr
    #   except ImportError:
    #       from ._module import attr
    if attr not in ("SPIBus", "I80Bus"):
        raise AttributeError(attr)
    # module is the module name, e.g. "_i80bus_rp2" or "_i80bus"
    try:
        # Try to load the platform-specific module
        module = "".join(["_", attr.lower(), "_", platform])
        value = getattr(__import__(module), attr)
    except ImportError:
        # If the platform-specific module doesn't exist, then use the generic module
        module = "".join(["_", attr.lower()])
        value = getattr(__import__(module, None, None, [], 1), attr)
    globals()[attr] = value
    return value