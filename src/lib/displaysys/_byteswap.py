# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
`displaysys._byteswap`
====================================================

A function to swap the bytes of a buffer in place.  3 implementations are provided:
- numpy:  The preferred implementation using numpy, which is usually available in Python
          and CircuitPython, and may be available in MicroPython with the numpy module.
- viper:  A viper implementation for MicroPython only
- default:  A default implementation with no dependencies
"""

try:
    # import byteswap from MicroPython if available
    from byteswap import byteswap
except ImportError:
    try:
        # import numpy if available
        try:
            # import numpy for CPython
            import numpy as np
        except ImportError:
            # import numpy for CircuitPython or MicroPython with numpy module
            from ulab import numpy as np

        def byteswap(buf):
            """
            Swap the bytes of a 16-bit buffer in place using numpy.
            """
            npbuf = np.frombuffer(buf, dtype=np.uint16)
            npbuf.byteswap(inplace=True)
    except Exception:
        try:
            # import byteswap_viper if available
            from ._byteswap_viper import byteswap_viper

            def byteswap(buf):
                """
                Swap the bytes of a 16-bit buffer in place using viper.
                """
                byteswap_viper(buf, len(buf))
        except Exception:

            def byteswap(buf):
                """
                Swap the bytes of a 16-bit buffer in place with no dependencies.
                """
                buf[::2], buf[1::2] = buf[1::2], buf[::2]
