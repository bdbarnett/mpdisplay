""" Unix SDL2 board configuration """

import sdl2display
import sdl2_lcd
import sys


display_drv = sdl2display.SDL2Display(
    width=320,
    height=480,
    x=0, # sdl2bus.SDL_WINDOWPOS_CENTERED,
    y=0, # sdl2bus.SDL_WINDOWPOS_CENTERED,
    title="MicroPython",
    window_flags=sdl2_lcd.SDL_WINDOW_SHOWN,
    render_flags=sdl2_lcd.SDL_RENDERER_ACCELERATED,
    color_depth=16,
    scale=1.5,
)
display_drv.quit_func = sys.exit

touch_read_func=display_drv.get_touch
touch_rotation_table=None
