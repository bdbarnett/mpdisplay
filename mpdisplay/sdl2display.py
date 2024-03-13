# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
""" Unix SDL2 Display Driver """

import sdl2lcd

class SDL2Display(sdl2lcd.LCD):
    """
    Unix SDL2 display driver for MPDisplay.  Wraps sdl2lcd.LCD to provide a
    get_touch method, set the requires_byte_swap attribute, and to provide
    empty properties and methods required by MPDisplay.
    """
    display_name = "SDL2Display"

    def __init__(self, *args, **kwargs):
        """
        Initialize the SDL2Display driver.  Set requires_byte_swap to False
        and call the base class constructor
        
        :param args: positional arguments to pass to the base class constructor
        :param kwargs: keyword arguments to pass to the base class constructor
        """
        self.requires_byte_swap = False

        super().__init__(*args, **kwargs)

    def get_touch(self):
        """
        Get the touch position from the SDL2 event queue.  If the event is
        SDL_MOUSEBUTTONDOWN and the left button is pressed, return the
        mouse position.  Otherwise, return None.
        
        :return: (x, y) tuple of the mouse position or None
        :rtype: tuple or None
        """
        # NOTE: This discards all events except MOUSEBUTTONDOWN on the left button
        event = self.poll_event()
        if event:
            # if the event is SDL_MOUSEBUTTONDOWN, return the mouse position
            if event[sdl2lcd.TYPE] == sdl2lcd.SDL_MOUSEBUTTONDOWN and event[sdl2lcd.BUTTON] == sdl2lcd.SDL_BUTTON_LEFT:
                return (event[sdl2lcd.X], event[sdl2lcd.Y])
        return None

    @property
    def rotation(self):
        return 0

    @rotation.setter
    def rotation(self, value):
        return

    @property
    def power(self):
        return -1

    @power.setter
    def power(self, value):
        return

    @property
    def brightness(self):
        return -1

    @brightness.setter
    def brightness(self, value):
        return

    def reset(self):
        return

    def hard_reset(self):
        return

    def soft_reset(self):
        return

    def sleep_mode(self, value):
        return

    def init(self, render_mode_full=False):
        return

    def set_render_mode_full(self, render_mode_full=False):
        return
