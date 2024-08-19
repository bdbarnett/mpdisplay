# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
SDL2 event polling module.
"""
from .sdl2_lib import (
    SDL_PollEvent, SDL_GetKeyName, SDL_Event, SDL_QUIT, SDL_BUTTON_LMASK, SDL_BUTTON_MMASK, 
    SDL_BUTTON_RMASK, SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP, SDL_MOUSEMOTION, SDL_MOUSEWHEEL,
    SDL_KEYDOWN, SDL_KEYUP
)
from eventsys.events import Events
from sys import implementation
if implementation.name == 'cpython':
    is_cpython = True
else:
    is_cpython = False

_event = SDL_Event()

def poll():
    """
    Polls for an event and returns the event type and data.

    :return: The event type and data.
    :rtype: tuple
    """
    global _event
    if SDL_PollEvent(_event):
        if is_cpython:
            if _event.type in Events.filter:
                return _convert(SDL_Event(_event))
        else:
            if int.from_bytes(_event[:4], 'little') in Events.filter:
                return _convert(SDL_Event(_event))
    return None

def _convert(e):
    # Convert an SDL event to a Pygame event
    if e.type == SDL_MOUSEMOTION:
        l = 1 if e.motion.state & SDL_BUTTON_LMASK else 0  # noqa: E741
        m = 1 if e.motion.state & SDL_BUTTON_MMASK else 0
        r = 1 if e.motion.state & SDL_BUTTON_RMASK else 0
        evt = Events.Motion(e.type, (e.motion.x, e.motion.y), (e.motion.xrel, e.motion.yrel), (l, m, r), e.motion.which != 0, e.motion.windowID)
    elif e.type in (SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP):
        evt = Events.Button(e.type, (e.button.x, e.button.y), e.button.button, e.button.which != 0, e.button.windowID)
    elif e.type == SDL_MOUSEWHEEL:
        evt = Events.Wheel(e.type, e.wheel.direction != 0, e.wheel.x, e.wheel.y, e.wheel.preciseX, e.wheel.preciseY, e.wheel.which != 0, e.wheel.windowID)
    elif e.type in (SDL_KEYDOWN, SDL_KEYUP):
        name = SDL_GetKeyName(e.key.keysym.sym)
        evt = Events.Key(e.type, name, e.key.keysym.sym, e.key.keysym.mod, e.key.keysym.scancode, e.key.windowID)
    elif e.type == SDL_QUIT:
        evt = Events.Quit(e.type)
    else:
        evt = Events.Unknown(e.type)
    return evt
