import mip

TARGET = "."

# Install your board_config.  Modify the path to match your board_config.
mip.install("github:bdbarnett/mpdisplay/board_configs/desktop", target=TARGET)
print("")

# Install sdl2_lib.  Comment out this line if you are only using lcd_bus.
mip.install("github:bdbarnett/sdl2_lib", target=TARGET)
print("")

# Install lcd_bus.  Comment out this line if you are only using sdl2_lib.
mip.install("github:bdbarnett/lcd_bus", target=TARGET)
print("")

# Install the mpdisplay library.  Required.
mip.install("github:bdbarnett/mpdisplay", target=TARGET)
print("")


### Optional libraries and examples.  Comment out any that you do not want to install. ###

mip.install("github:bdbarnett/framebuf", target=TARGET)
print("")

mip.install("github:bdbarnett/romfont", target=TARGET)
print("")

mip.install("github:bdbarnett/displaybuf", target=TARGET)
print("")

mip.install("github:bdbarnett/tft_graphics", target=TARGET)
print("")

mip.install("github:bdbarnett/console", target=TARGET)
print("")

mip.install("github:bdbarnett/timer", target=TARGET)
print("")

mip.install("github:bdbarnett/testris", target=TARGET)
