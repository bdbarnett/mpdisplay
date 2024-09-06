# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
This module provides the SDL2 library implementation for MicroPython and CPython.

The module checks the implementation name and imports the appropriate module
based on whether the current Python implementation is MicroPython or CPython.
"""

from sys import implementation

if implementation.name == "micropython":
    from ._micropython import *  # noqa: F403
else:
    from ._cpython import *  # noqa: F403
