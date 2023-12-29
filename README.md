# mpdisplay
Display, touch and encoder drivers for MicroPython and lv_bindings_micropython

Better documentation coming soon!

The display drivers here currently support SPI and I8080 displays on ESP32 boards using the lcd_bus C drivers in [lv_binding_micropython](https://github.com/kdschlosser/lv_binding_micropython/tree/MicroPython_1.21.0_Update).  They also support SPI displays on ANY MicroPython microcontroller such as RP2040 and STM32 using [lcd_bus.py](bus_drivers/lcd_bus.py).  The touch and encoder drivers, as well as the `lv_driver_framework.py` and `lv_config.py`, aren't limited to any specific microcontroller.

The graphics engine these drivers are targeted toward is LVGL on MicroPython, but they are structured so they may support any graphics engine on MicroPython.  See [display_simple_test.py](lib/display_simpletest.py) and [testris](https://github.com/bdbarnett/testris) for examples using these drivers without LVGL.

# Quickstart
To use a SPI display on MicroPython without LVGL, you only need to add lcd_bus.py to the list of files in your /lib folder.  It should work with any recent version of MicroPython, but only version 1.21 (the current version) has been tested.

To use with LVGL on MicroPython, compile and flash your board with the latest [lv_binding_micropython](https://github.com/kdschlosser/lv_binding_micropython/tree/MicroPython_1.21.0_Update).  See the directions on that page for more details.  It is a work in progress and may have issues that need to be resolved.

Download the following files and upload them to the /lib folder on your board:
- The [lib](lib) folder, which includes the required files `busdisplay.py`, `lv_driver_framework` and `lv_config.py`, as well as the optional test files `lv_touch_test.py` and `display_simpletest.py`
- If your board isn't an ESP32 or you aren't on lv_binding_micropython, you will the `lcd_bus.py` from [bus_drivers](bus_drivvers).  (It won't hurt to have this file in your /lib folder anyway, so you may as well grab it.)
- The `board_config.py` from [board_configs](board_configs)
- The driver for your display controller from [display_drivers](display_drivers)
- The driver for your touchscreen controller from [touch_drivers](touch_drivers)
- If your board uses an IO expander to communicate with the display, for example RGB displays like the ST7701 on the T-RGB board, get the driver from [io_expander_drivers](io_expander_drivers)
- If your board has an encoder, or if you want to add one, get the driver from [encoder_drivers](encoder_drivers).  See [t-embed](board_configs/t-embed) for an example.

You MAY want to edit the `board_config.py` to:
- Adjust the bus frequency for possible higher throughput
- Set the initial brightness of the backlight if backlight_pin is set
- Set the rotation of the display
- Correct any settings that may be necessary for your setup
- Enable an encoder if you add one.  See [t-embed](board_configs/t-embed) for an example.
- Add other non-display related drivers, such as SD card reader or real time clock (not provided)

For use in LVGL, you MAY want to edit the `lv_config.py` to:
- Adjust the buffer size, type and quantity to match your needs
- Set your color format if "lv.COLOR_FORMAT.NATIVE" doesn't work
- Change from blocking mode to non-blocking mode (currently has issues in the C display bus drivers)
- Enable encoder(s) if you are using them.  Simply uncomment the last line.

It is recommended that you first try the [display_simpletest.py](lib/display_simpletest.py) program.  See the code from that program and [testris](https://github.com/bdbarnett/testris) for non-LVGL usage examples.

If you have lv_binding_micropython, next try [lv_touch_test.py](lib/lv_touch_test.py).  The color of the buttons should be blue when not selected, green when pressed and red when focused.  If the touch points don't line up with the buttons, it provides directions on how to find the correct touch rotation masks.  From the REPL type:
```
from lv_touch_test import mask, rotation
```

Here is an LVGL usage example:
```
import lv_config
import lvgl as lv

scr = lv.screen_active()
button = lv.button(scr)
button.center()
label = lv.label(button)
label.set_text("Test")
```

# My board isn't listed
I have several more boards that I will add over the next couple weeks.  Please note, I am only providing configs for boards that have an integrated display or, on occasion, boards and displays that may be directly plugged into one another, such as Feather, EYE-SPI, Qualia or QT-Py.  I will not create configs for any setup that requires wiring.  Those setups are generally custom built, but you may use the board configs here as an example.

# My board isn't on your list to create
I am considering creating board configs by request IF you provide a gift certificate to pay for the board from Adafruit, DigiKey, Amazon, Pimoroni or wherever your board is stocked.  I'll post that here if I decide to do that.  Remember, only ESP32 boards are supported at this time.

# What else?
[Kevin Schlosser](https://github.com/kdschlosser) has put in a tremendous amount of time improving the lv_binding_micropython.  Please consider supporting him in some way.
