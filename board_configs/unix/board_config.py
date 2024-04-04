""" Unix SDL2 board configuration """

import mpdisplay
import sys


display_drv = mpdisplay.SDL2Display(
    width=320,
    height=480,
    x=mpdisplay.SDL_WINDOWPOS_CENTERED,
    y=mpdisplay.SDL_WINDOWPOS_CENTERED,
    title=f"{sys.implementation.name} on {sys.platform}",
    window_flags=mpdisplay.SDL_WINDOW_SHOWN,
    render_flags=mpdisplay.SDL_RENDERER_ACCELERATED,
    color_depth=16,
    scale=1.5,
)
display_drv.quit_func = sys.exit

