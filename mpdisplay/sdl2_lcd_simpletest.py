# sdl_lcd_simpletest.py - Simple test/demo of the SDL2 LCD module.
# Description: Test the sdl2_lcd module EXCEPT for the LCD class.
# Demonstrates copying a buffer to a texture, rendering a filled rectangle to the texture,
# and rendering the texture to the window, both as a whole and as a part.
# Also demonstrates handling events such as key presses and mouse movement.

from sdl2_lcd import *
from time import sleep_ms

width = 640
height = 480
px_format = SDL_PIXELFORMAT_RGB565

########### Step 1: Initialize SDL2, create a window and a renderer ###########

SDL_Init(SDL_INIT_EVERYTHING)
win = SDL_CreateWindow("Hello World", 100, 100, width, height, SDL_WINDOW_SHOWN)
renderer = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC)

# Set the logical size to half the window size (scaling)
SDL_RenderSetLogicalSize(renderer, width//2, height//2)

# Create a texture to render to; same size as the logical size
texture = SDL_CreateTexture(renderer, px_format, SDL_TEXTUREACCESS_TARGET, width//2, height//2)
SDL_SetTextureBlendMode(texture, SDL_BLENDMODE_NONE)

# create a bytearray filled with green (little endian)
green_buffer = bytearray([0x11100000, 0x00000111] * (width//4) * (height//4))


########### Step 2: Fill the screen with red ###########

# Fill the window with red and wait for 2 seconds
SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255)
SDL_RenderClear(renderer)
SDL_RenderPresent(renderer)
sleep_ms(2000)


########### Step 3: Update the texture with a green and render it to the window ###########

# Update the texture with the centered green_buffer (similar to a blit) and wait for 2 seconds
# Render the texture to the window, only showing the part of the texture that is green (showRect)
showRect = SDL_Rect(width//8, height//8, width//4, height//4)
SDL_UpdateTexture(texture, showRect, green_buffer, 100 * 2)
SDL_RenderCopy(renderer, texture, showRect, showRect)
SDL_RenderPresent(renderer)
sleep_ms(2000)


########### Step 4: Draw a blue rectangle on the texture using Fill Rect ###########

# Use SDL_RenderFillRect to render a blue rectangle on the texture
# Render only the blue rectangle to the window and wait for 2 seconds
fillRect = SDL_Rect(0, 0, width//8, height//8)
SDL_SetRenderTarget(renderer, texture)
SDL_SetRenderDrawColor(renderer, 0, 0, 255, 255)
SDL_RenderFillRect(renderer, fillRect)
SDL_RenderPresent(renderer)
SDL_SetRenderTarget(renderer, None)
SDL_RenderCopy(renderer, texture, fillRect, fillRect)
SDL_RenderPresent(renderer)
sleep_ms(2000)


########### Step 5: Clear the window with white  ###########

# Clear the window with white and wait for 2 seconds
SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255)
SDL_RenderClear(renderer)
SDL_RenderPresent(renderer)
sleep_ms(2000)


########### Step 6: Render the texture to the window again ###########

# Render the texture to the window again, showing the entire texture
# It stretches the texture to the window size
# Note the background is black because we didn't write red to the entire texture
SDL_RenderCopy(renderer, texture, None, None)
SDL_RenderPresent(renderer)

e = bytearray(56)
while True:
    if SDL_PollEvent(e):
        event_type = int.from_bytes(e[:4], 'little')
        if event_type in (
            SDL_QUIT,
            SDL_KEYDOWN,
            SDL_KEYUP,
            SDL_MOUSEMOTION,
            SDL_MOUSEBUTTONDOWN,
            SDL_MOUSEBUTTONUP,
            SDL_MOUSEWHEEL,
            ):
            event = Events.to_struct(e)
            print(f"{event.type=:#010x}")
            if event.type == SDL_QUIT:
                SDL_DestroyTexture(texture)
                SDL_DestroyRenderer(renderer)
                SDL_DestroyWindow(win)
                SDL_Quit()
                break
            elif event.type == SDL_KEYDOWN or event.type == SDL_KEYUP:
                keyname = SDL_GetKeyName(event.key.keysym.sym)
                print(f"{event.type=}, {keyname=}, {event.key.keysym.scancode=:#04x}, {event.key.keysym.sym=:#04x}, {event.key.keysym.mod=:#04x}")
            elif event.type == SDL_MOUSEMOTION:
                print(f"{event.type=}, {event.motion.x=}, {event.motion.y=}, {event.motion.xrel=}, {event.motion.yrel=}, {event.motion.state=}")
            elif event.type == SDL_MOUSEBUTTONDOWN or event.type == SDL_MOUSEBUTTONUP:
                print(f"{event.type=}, {event.button.x=}, {event.button.y=}, {event.button.button=}")
            elif event.type == SDL_MOUSEWHEEL:
                print(f"{event.type=}, {event.wheel.x=}, {event.wheel.y=}, {event.wheel.direction=}")
