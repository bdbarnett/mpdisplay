import mip

TARGET = "."

# Install your board_config
mip.install("github:bdbarnett/mpdisplay/board_configs/desktop", target=TARGET)

# Install the mpdisplay library
mip.install("github:bdbarnett/mpdisplay/mpdisplay", target=TARGET)

# Install the mpdisplay utils
mip.install("github:bdbarnett/mpdisplay/utils", target=TARGET)

# Install the mpdisplay examples
mip.install("github:bdbarnett/mpdisplay/examples", target=TARGET)

# Install the mpdisplay LVGL examples
mip.install("github:bdbarnett/mpdisplay/examples/lvgl", target=TARGET)
