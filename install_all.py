#!/usr/bin/micropython -i
import mip
import sys


TARGET = "."
LAUNCH = "calculator"

print("\nInstalling the mpdisplay library and optional libraries and examples.\n")

# Install the mpdisplay library.  Required.
mip.install("github:bdbarnett/mpdisplay", target=TARGET)
print("")

# Install sdl2_lib.  Comment out this line if you are only using lcd_bus.
mip.install("github:bdbarnett/sdl2_lib", target=TARGET)
print("")

# Install lcd_bus.  Comment out this line if you are only using sdl2_lib.
mip.install("github:bdbarnett/lcd_bus", target=TARGET)
print("")


### Optional libraries and examples.  Comment out any that you do not want to install. ###

mip.install("github:bdbarnett/shapes", target=TARGET)
print("")

mip.install("github:bdbarnett/framebuf_plus", target=TARGET)
print("")

mip.install("github:bdbarnett/binfont", target=TARGET)
print("")

mip.install("github:bdbarnett/displaybuf", target=TARGET)
print("")

mip.install("github:bdbarnett/direct_draw", target=TARGET)
print("")

mip.install("github:bdbarnett/console", target=TARGET)
print("")

mip.install("github:bdbarnett/timer", target=TARGET)
print("")

mip.install("github:bdbarnett/playing_cards", target=TARGET)
print("")

mip.install("github:bdbarnett/testris", target=TARGET)
print("")


# Install your board_config or prompt to install it.
if sys.platform == "linux":
    mip.install("github:bdbarnett/mpdisplay/board_configs/desktop", target=TARGET)
    print(f"\nInstallation complete.  To run the {LAUNCH} example, type the following:")
else:
    print(f"You must now install your board_config before running the {LAUNCH} example.\n",
          "Type the following, substituting `desktop` with your board:\n",
        f"""   mip.install("github:bdbarnett/mpdisplay/board_configs/desktop", target={TARGET})""")

print("    import path")
print(f"    import {LAUNCH}\n")
