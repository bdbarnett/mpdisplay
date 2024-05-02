import mip

TARGET = "."

# Install your board_config
mip.install("github:bdbarnett/mpdisplay/board_configs/desktop", target=TARGET)

# Install lcd_bus.  Comment out this line if you don't need it.
mip.install("github:bdbarnett/lcd_bus/lcd_bus", target=TARGET)

# Install the mpdisplay library
mip.install("github:bdbarnett/mpdisplay/mpdisplay", target=TARGET)

# Install the mpdisplay utils
mip.install("github:bdbarnett/mpdisplay/utils", target=TARGET)

# Install the mpdisplay examples
mip.install("github:bdbarnett/mpdisplay/examples", target=TARGET)
