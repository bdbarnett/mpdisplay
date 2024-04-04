""" CPython PyGame board configuration """

import lib.mpdisplay as mpdisplay
import sys


display_drv = mpdisplay.PGDisplay(
    width=320,
    height=480,
    title=f"{sys.implementation.name} on {sys.platform}",
    window_flags=mpdisplay.pg.SHOWN,
    color_depth=16,
    scale=1.0,
)
display_drv.quit_func = sys.exit

