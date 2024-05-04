import mip

TARGET = "."

# Install your board_config.  Modify the path to match your board_config.
mip.install("github:bdbarnett/mpdisplay/board_configs/desktop", target=TARGET)

# Install sdl2_lib.  Comment out this line if you are only using lcd_bus.
mip.install("github:bdbarnett/sdl2_lib", target=TARGET)

# Install lcd_bus.  Comment out this line if you are only using sdl2_lib.
mip.install("github:bdbarnett/lcd_bus", target=TARGET)

# Install the mpdisplay library.  Required.
mip.install("github:bdbarnett/mpdisplay", target=TARGET)


### Optional libraries and examples.  Comment out any that you do not want to install. ###

mip.install("github:bdbarnett/framebuf", target=TARGET)

mip.install("github:bdbarnett/romfont", target=TARGET)

mip.install("github:bdbarnett/displaybuf", target=TARGET)

mip.install("github:bdbarnett/tft_graphics", target=TARGET)

mip.install("github:bdbarnett/console", target=TARGET)

mip.install("github:bdbarnett/timer", target=TARGET)

mip.install("github:bdbarnett/testris", target=TARGET)

mip.install("github:bdbarnett/testris", target=TARGET)
