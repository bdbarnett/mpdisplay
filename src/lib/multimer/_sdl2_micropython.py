# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
Timer using SDL2 for CPython with the same API as machine.Timer in MicroPython.
"""

from ._timerbase import _TimerBase
import ffi


# Load the SDL2 shared library using ffi
_libSDL2 = ffi.open("libSDL2-2.0.so.0")

SDL_INIT_TIMER = 0x00000001

SDL_Init = _libSDL2.func("i", "SDL_Init", "I")
SDL_AddTimer = _libSDL2.func("P", "SDL_AddTimer", "IPP")
SDL_RemoveTimer = _libSDL2.func("i", "SDL_RemoveTimer", "P")

def SDL_TimerCallback(func):
    return ffi.callback("I", func, "IP")


class Timer(_TimerBase):
    """SDL2 Timer class"""

    def _start(self):
        SDL_Init(SDL_INIT_TIMER)
        self._handler_ref = self._handler
        self._tcb = SDL_TimerCallback(self._handler_ref)
        self._timer = SDL_AddTimer(self._interval, self._tcb, None)

    def _stop(self):
        if self._timer:
            SDL_RemoveTimer(self._timer)
            self._timer = None
            self._tcb = None
            self._handler_ref = None
