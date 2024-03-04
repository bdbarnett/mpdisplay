""" Unix SDL2 Display Driver """

import sdl2_lcd

class SDL2Display(sdl2_lcd.LCD):
    """
    Unix SDL2 display driver for MPDisplay
    """
    display_name = "SDL2Display"

    def __init__(self, *args, **kwargs):
        self.requires_byte_swap = False

        super().__init__(*args, **kwargs)

    def get_touch(self):
        # NOTE: This discards all events except MOUSEBUTTONDOWN on the left button
        event = self.poll_event()
        if event:
            # if the event is SDL_MOUSEBUTTONDOWN, return the mouse position
            if event[sdl2_lcd.TYPE] == sdl2_lcd.SDL_MOUSEBUTTONDOWN and event[sdl2_lcd.BUTTON] == sdl2_lcd.SDL_BUTTON_LEFT:
                return (event[sdl2_lcd.X], event[sdl2_lcd.Y])
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
