"""
framebuf.py - for compatibility with the MicroPython framebuf module
in CPython and CircuitPython.
"""

from graphics._framebuf import (
    FrameBuffer,
    MONO_VLSB,
    MONO_HLSB,
    MONO_HMSB,
    GS2_HMSB,
    GS4_HMSB,
    GS8,
    RGB565,
)

__all__ = [
    "FrameBuffer",
    "MONO_VLSB",
    "MONO_HLSB",
    "MONO_HMSB",
    "GS2_HMSB",
    "GS4_HMSB",
    "GS8",
    "RGB565",
]
