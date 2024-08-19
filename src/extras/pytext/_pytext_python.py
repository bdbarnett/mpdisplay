# SPDX-FileCopyrightText: 2024 Brad Barnett, 2023 Russ Hughes
#
# SPDX-License-Identifier: MIT

import struct


_BIT7 = 0x80
_BIT6 = 0x40
_BIT5 = 0x20
_BIT4 = 0x10
_BIT3 = 0x08
_BIT2 = 0x04
_BIT1 = 0x02
_BIT0 = 0x01

def _pack8(glyphs: memoryview, idx: int, fg_color: int, bg_color: int):
    buffer = bytearray(128)
    fg = struct.pack("<H", fg_color & 0xFFFF)
    bg = struct.pack("<H", bg_color & 0xFFFF)

    for i in range(0, 128, 16):
        byte = glyphs[idx]
        buffer[i: i+2] = fg if byte & _BIT7 else bg
        buffer[i+2: i+4] = fg if byte & _BIT6 else bg
        buffer[i+4: i+6] = fg if byte & _BIT5 else bg
        buffer[i+6: i+8] = fg if byte & _BIT4 else bg
        buffer[i+8: i+10] = fg if byte & _BIT3 else bg
        buffer[i+10: i+12] = fg if byte & _BIT2 else bg
        buffer[i+12: i+14] = fg if byte & _BIT1 else bg
        buffer[i+14: i+16] = fg if byte & _BIT0 else bg
        idx += 1

    return buffer

def _pack16(glyphs: memoryview, idx: int, fg_color: int, bg_color: int):
    buffer = bytearray(256)
    fg = struct.pack("<H", fg_color & 0xFFFF)
    bg = struct.pack("<H", bg_color & 0xFFFF)

    for i in range(0, 256, 16):
        byte = glyphs[idx]
        buffer[i: i+2] = fg if byte & _BIT7 else bg
        buffer[i+2: i+4] = fg if byte & _BIT6 else bg
        buffer[i+4: i+6] = fg if byte & _BIT5 else bg
        buffer[i+6: i+8] = fg if byte & _BIT4 else bg
        buffer[i+8: i+10] = fg if byte & _BIT3 else bg
        buffer[i+10: i+12] = fg if byte & _BIT2 else bg
        buffer[i+12: i+14] = fg if byte & _BIT1 else bg
        buffer[i+14: i+16] = fg if byte & _BIT0 else bg
        idx += 1

    return buffer
