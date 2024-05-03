# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

from sys import implementation
if implementation.name == 'micropython':
    from ._micropython import *
else:
    from ._cpython import *