# SPDX-FileCopyrightText: 2024 Brad Barnett, 2023 Russ Hughes
#
# SPDX-License-Identifier: MIT

from micropython import const


# The following if statement is used to prevent errors when linting the code.
# It is not necessary to include it in your own code.
if 0:
    uint = int
    ptr16 = ptr8 = lambda x: x

    class micropython:

        @staticmethod
        def viper(func):
            return func

        @staticmethod
        def native(func):
            return func


_BIT7 = const(0x80)
_BIT6 = const(0x40)
_BIT5 = const(0x20)
_BIT4 = const(0x10)
_BIT3 = const(0x08)
_BIT2 = const(0x04)
_BIT1 = const(0x02)
_BIT0 = const(0x01)

@micropython.viper
def _pack8(glyphs, idx: uint, fg_color: uint, bg_color: uint):
    buffer = bytearray(128)
    bitmap = ptr16(buffer)
    glyph = ptr8(glyphs)

    for i in range(0, 64, 8):
        byte = glyph[idx]
        bitmap[i] = fg_color if byte & _BIT7 else bg_color
        bitmap[i + 1] = fg_color if byte & _BIT6 else bg_color
        bitmap[i + 2] = fg_color if byte & _BIT5 else bg_color
        bitmap[i + 3] = fg_color if byte & _BIT4 else bg_color
        bitmap[i + 4] = fg_color if byte & _BIT3 else bg_color
        bitmap[i + 5] = fg_color if byte & _BIT2 else bg_color
        bitmap[i + 6] = fg_color if byte & _BIT1 else bg_color
        bitmap[i + 7] = fg_color if byte & _BIT0 else bg_color
        idx += 1

    return buffer

@micropython.viper
def _pack16(glyphs, idx: uint, fg_color: uint, bg_color: uint):
    buffer = bytearray(256)
    bitmap = ptr16(buffer)
    glyph = ptr8(glyphs)

    for i in range(0, 128, 16):
        byte = glyph[idx]

        bitmap[i] = fg_color if byte & _BIT7 else bg_color
        bitmap[i + 1] = fg_color if byte & _BIT6 else bg_color
        bitmap[i + 2] = fg_color if byte & _BIT5 else bg_color
        bitmap[i + 3] = fg_color if byte & _BIT4 else bg_color
        bitmap[i + 4] = fg_color if byte & _BIT3 else bg_color
        bitmap[i + 5] = fg_color if byte & _BIT2 else bg_color
        bitmap[i + 6] = fg_color if byte & _BIT1 else bg_color
        bitmap[i + 7] = fg_color if byte & _BIT0 else bg_color
        idx += 1

        byte = glyph[idx]
        bitmap[i + 8] = fg_color if byte & _BIT7 else bg_color
        bitmap[i + 9] = fg_color if byte & _BIT6 else bg_color
        bitmap[i + 10] = fg_color if byte & _BIT5 else bg_color
        bitmap[i + 11] = fg_color if byte & _BIT4 else bg_color
        bitmap[i + 12] = fg_color if byte & _BIT3 else bg_color
        bitmap[i + 13] = fg_color if byte & _BIT2 else bg_color
        bitmap[i + 14] = fg_color if byte & _BIT1 else bg_color
        bitmap[i + 15] = fg_color if byte & _BIT0 else bg_color
        idx += 1

    return buffer
