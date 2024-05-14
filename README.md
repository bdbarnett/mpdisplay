# MPDisplay
Display, touch and encoder drivers for [MicroPython](https://github.com/micropython/micropython)

MPDisplay provides display, touch and encoder drivers as well as framework, config and test files for MicroPython and can be used in LV_MicroPython, LVGL_MicroPython, TFT Graphics, Nano-GUI and Micro-GUI.  It provides SDL2 LCD drivers for Unix as well as SPI and I80 display buses in the included [lcd_bus](mpdisplay/lcd_bus) but also supports [mp_lcd_bus](https://github.com/kdschlosser/mp_lcd_bus) which are fast drivers written in C for SPI, I80 and RGB buses on ESP32.

# Supported platforms
## MicroPython
[MicroPython](https://github.com/micropython/micropython) doesn't include drivers for color displays nor display buses.  MPDisplay provides both display and bus drivers that will work with MicroPython's native `framebuf.FrameBuffer` and several other methods of creating buffer objects before they are sent to the display.  Here are directions for [compiling in mp_lcd_bus](docs/compiling.md) if you have an ESP32 target.

## LV_MicroPython
[LV_MicroPython](https://github.com/lvgl/lv_micropython) is the official repository of LVGL integrated into MicroPython.  The handful of drivers it has are all-in-one, not modular, and are generally written for a specific display on a specific bus on a specific architecture.  The drivers in MPDisplay are modular and work with LV_MicroPython.

## LVGL_MicroPython
[LVGL_MicroPython](https://github.com/kdschlosser/lvgl_micropython) is created by community member Kevin Schlosser.  It has several improvements over the official repo.  Most significant as far as drivers are concerned, it includes mp_lcd_bus, which are very fast SPI, i80 and RGB bus drivers written in C for ESP32 platforms.  MPDisplay works with the mp_lcd_bus bus drivers in LVGL_MicroPython.

## TFT Graphics
[TFT Graphics](https://github.com/bdbarnett/direct_draw) is a port I created of Russ Hughes's st7789mpy_py library to demonstrate MPDisplay's usefullness with other libraries.  It is fully functional and very powerful.  It includes all the examples provided in the original library.  It draws directly to the screen, only creating small buffers for individual characters in text or for bitmap images.

## DisplayBuffer
[DisplayBuffer](https://github.com/bdbarnett/displaybuffer) is a class I wrote based on the drivers Peter Hinch wrote in Nano-GUI and Micro-GUI.  I initially wrote it to make MPDisplay compatible with those libraries, but it is very useful on its own.  It is a framebuffer based on the number of pixels on the display, but can be sized to 2 bytes per pixel, 1 byte per pixel or 2 pixels per byte depending on whether the user wants all 65k (RGB565), only 256 (RGB332) or even only 16 (RGB565 in a lookup table) colors.

## Nano-GUI on MicroPython
[Nano-GUI](https://github.com/peterhinch/micropython-nano-gui) is a graphics library written in MicroPython for MicroPython by longtime MicroPython coder Peter Hinch.  It provides its own drivers, but it is modular and may use the drivers provided by MPDisplay as well.  The benefit of using MPDisplay with Nano-Gui is that more displays are supported, particularly Unix, I80 and RGB Bus displays.  [Micro-GUI](https://github.com/peterhinch/micropython-micro-gui) uses Nano-GUI compatible drivers, so you may use MPDisplay with Micro-GUI as well.

# Quickstart
Flash your board with your preferred version of MicroPython listed above.  If using the Unix port of MicroPython, put the follwing files in your `lib` folder and skip to `Using popular graphics libraries`.  Note the Unix drivers included with lv_micropython are recommended over these drivers because these drivers discard all keyboard events.  These drivers will work for other graphics libraries on the Unix port of MicroPython.
- sdl2lcd.py, sdl2display.py, mpdisplay_simpletest.py and board_configs/unix/board_config.py

## Install on an MCU with mip
Replace YOUR_BOARD_HERE with your the directory from [board_configs](board_configs) that matches your installation OR leave that line out and manually install the board_config.py and drivers per the Manual installation directions.

### On a network connected board, at the REPL:
```
import mip
mip.install("github:bdbarnett/mpdisplay", target="/")
mip.install("github:bdbarnett/mpdisplay/board_configs/YOUR_BOARD_HERE", target="/")
```

### On a non-network connected board, use mpremote from your computer's command line:
```
mpremote mip install --target=/ "github:bdbarnett/mpdisplay"
mpremote mip install --target=/ "github:bdbarnett/mpdisplay/board_configs/YOUR_BOARD_HERE"
```

## Manual installation on an MCU
Download the following files and upload them to your board:
- Put the contents of the [mpdisplay](mpdisplay) folder in your `lib` folder

You will also need the folowing files that match your particular hardware:
- An appropriate `board_config.py` from [board_configs](board_configs).  If you don't find one that matches your hardware, try to find one with the same bus, display controller and MCU as yours.
- The driver for your display controller from [display_drivers](display_drivers)
- The driver for your touchscreen controller (if applicable) from [touch_drivers](touch_drivers)
- If your board uses an IO expander to communicate with the display, for example RGB displays like the ST7701 on the T-RGB board, get the driver from [io_expander_drivers](io_expander_drivers)
- If your board has an encoder, or if you want to add one, get the driver from [encoder_drivers](encoder_drivers).  See [t-embed](board_configs/t-embed) for an example.


## Using popular graphics libraries
If you have LVGL compiled into MicroPython, also get:
- the contents of the [lvgl](lvgl) folder

To use Nano-GUI or Micro-GUI, [see DisplayBuffer](https://github.com/bdbarnett/displaybuffer)

To use [direct_draw](https://github.com/bdbarnett/direct_draw), see its directions.


# Suggested filesystem structure
Don't forget to put your display and optional touchscreen and encoder drivers somewhere on the path, preferably in /lib or /.
```
├── mpdisplay/  (put each of these, not the mpdisplay directory, in your machine's lib directory)
│   │
│   ├── lcd_bus/                - required if C bus drivers aren't compiled in, otherwise Optional
│   │   ├── __init__.py         - required
│   │   ├── _basebus.py         - required
│   │   ├── _spibus.py          - required for SPIBus only
│   │   ├── _i80bus.py          - required for I80Bus only
│   │   └── _gpio_registers.py  - required for I80Bus only
│   │
│   ├── busdisplay.py           - required for all SPI, I80 and RGB LCD buses
│   ├── mpdisplay_simpletest.py - optional for all Unix, SPI, I80 and RGB targets
│   │
│   ├── sdl2_display.py         - required for Unix / Linux targets (same API as busdisplay)
│   ├── sdl2lcd.py             - required for Unix / Linux targets (same FUNCTION as lcd_bus)
│   └── sdl2lcd_simpletest.py  - Not needed.  Only useful for Unix developer purposes.
|                                              May be removed from the repo in the future.
│   
├── lvgl/  (put each of these, not the lvgl directory, in your machine's lib directory)
│   ├── lv_mpdisplay.py         - LVGL:  required
│   └── lv_touch_test.py        - LVGL:  recommended
│
├── board_config.py             - required in all cases (put at the root of your machine's fs)
└── lv_config.py                - LVGL targets:  required (put at the root of your machine's fs)
```

You MAY want to edit your `board_config.py` to:
- Add `from machine import freq; freq(<Your MCU Speed Here>)`
- Adjust the bus frequency for possible higher throughput.  Some board_configs have a conservative setting.  Note: the bus frequency setting is only used in mp_lcd_bus, not MPDisplay's lcd_bus.
- Set the initial brightness of the backlight if backlight_pin is set
- Set the rotation of the display
- Enable an encoder if you add one.  See [t-embed](board_configs/t-embed) for an example.
- Add other non-display related drivers, such as SD card reader or real time clock (not provided)
- Correct any settings that may be necessary for your setup

For use in LVGL, you MAY want to edit `lv_config.py` to:
- Adjust the buffer size, type and quantity to match your needs
- Set your color format if "lv.COLOR_FORMAT.NATIVE" doesn't work
- Change from blocking mode to non-blocking mode (currently has issues in mp_lcd_bus drivers)
- Enable encoder(s) if you are using them.  Simply uncomment the last line.

# Usage
## All graphics platforms
No matter which graphics platform you plan to use, it is recommended that you first try the [display_simpletest.py](mpdisplay/mpdisplay_simpletest.py) program.  See the code from that program and [testris](https://github.com/bdbarnett/testris) for bare MicroPython usage examples.  It is also recommended that you try `displaybuf_simpletest.py` from [DisplayBuffer](https://github.com/bdbarnett/displaybuffer).  It demonstrates a simple way to get started with MPDisplay without using a graphics library that provides widgets.

## Nano-GUI
If you have downloaded the `gui` directory from [Nano-GUI](https://github.com/peterhinch/micropython-nano-gui) to your /lib folder, try `nano_gui_simpletest.py` from [DisplayBuffer](https://github.com/bdbarnett/displaybuffer).  The color of the top-left square should be red, the diagonal line should be green, and the bottom-right square should be blue.

## LVGL
If you have LVGL compiled into your MicroPython binary, try [lv_touch_test.py](lvgl/lv_touch_test.py).  The color of the buttons should be blue when not selected, green when pressed and red when focused.  If the touch points don't line up with the buttons, it provides directions in the REPL on how to find the correct touch rotation masks.  From the REPL type:
```
from lv_touch_test import mask, rotation
```

After getting everything working with the above tests, you're ready to start writing your own code.  Here is an LVGL usage example:
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
Please note, I am only providing configs for boards that have an integrated display or, on occasion, boards and displays that may be directly plugged into one another, such as Feather, EYE-SPI, Qualia or QT-Py.  I will not create configs for any setup that requires wiring.  Those setups are generally custom built, but you may use the board configs here as an example.  Please consider contributing your board_config.py if your hardware doesn't require custom wiring.

I am considering creating board configs by request IF you provide a gift certificate to pay for the board from Adafruit, DigiKey, Amazon, Pimoroni or wherever your board is stocked.  I'll post that here if I decide to do that.

# Coexistence with mp_lcd_bus (C bus drivers)
Note, if you have mp_lcd_bus compiled in, whether from LVGL_MicroPython or if you added it yourself, and also have lcd_bus in your /lib folder, the former takes precedence.  In this case, if you want to force MicroPython to use lib/lcd_bus, change the include line in your board_config.py from
```
from lcd_bus include ...
```
to
```
from lib.lcd_bus include ...
```

# TODO
- Document how to create custom board_configs, display_drivers and touch_drivers.
- I80bus assumes pins will be non-sequential and on multiple ports.  Create a version that doesn't, so lookup tables aren't necessary in order to increase speed.
- Create RP2 platform-specific bus drivers.
- Add keypad support to be subclassed in LVGL and Micro-GUI
	- hardware pins
   	- matrix of pins
   	- capacitive touch pins
   	- capacitive touch chips
   	- io expander
- Create a throughput comparison chart
- Create better documentation with readthedocs
- Test boards with RGB buses using [mp_lcd_bus](https://github.com/kdschlosser/mp_lcd_bus) and [LVGL_MicroPython](https://github.com/kdschlosser/lvgl_micropython):
	- qualia
   	- t-rgb_2.1in_full_circle
   	- esp32-s3-lcd-4.3
- Implement color OLED display drivers in `busdisplay.py` for ssd1331 and ssd1351
