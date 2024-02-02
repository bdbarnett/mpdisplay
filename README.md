# MPDisplay
Display, touch and encoder drivers for [MicroPython](https://github.com/micropython/micropython)

MPDisplay provides display, touch and encoder drivers as well as framework, config and test files for LV_MicroPython, LVGL_MicroPython, Nano-GUI and Micro-GUI.  It also provides drivers for SPI and I80 display buses using the included [lcd_bus](lib/lcd_bus) but also supports [mp_lcd_bus](https://github.com/kdschlosser/mp_lcd_bus) which are fast drivers written in C for SPI, I80 and RGB buses on ESP32.

# Supported platforms
## MicroPython
[MicroPython](https://github.com/micropython/micropython) doesn't include drivers for color displays nor display buses.  MPDisplay provides both display and bus drivers that will work with MicroPython's native `framebuf.FrameBuffer` and several other methods of creating buffer objects before they are sent to the display.

## LV_MicroPython
[LV_MicroPython](https://github.com/lvgl/lv_micropython) is the official repository of LVGL integrated into MicroPython.  The handful of drivers it has are all-in-one, not modular, and are generally written for a specific display on a specific bus on a specific architecture.  The drivers in MPDisplay are modular and work with LV_MicroPython.

## LVGL_MicroPython
[LVGL_MicroPython](https://github.com/kdschlosser/lvgl_micropython) is created by community member Kevin Schlosser.  It has several improvements over the official repo.  Most significant as far as drivers are concerned, it includes mp_lcd_bus, which are very fast SPI, i80 and RGB bus drivers written in C for ESP32 platforms.  MPDisplay works with the mp_lcd_bus bus drivers in LVGL_MicroPython.

## Nano-GUI on MicroPython
[Nano-GUI](https://github.com/peterhinch/micropython-nano-gui) is a graphics library written in MicroPython for MicroPython by longtime MicroPython coder Peter Hinch.  It provides its own drivers, but it is modular and may use the drivers provided by MPDisplay as well.  The benefit of using MPDisplay with Nano-Gui is that more displays are supported, particularly I80 and RGB Bus displays.  [Micro-GUI](https://github.com/peterhinch/micropython-micro-gui) uses Nano-GUI compatible drivers, so you may use MPDisplay with Micro-GUI as well.

# Quickstart
Flash your board with your preferred version of MicroPython listed above.

## Install with mip
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

## Manual installation
Download the following files and upload them to your board:
- The [lib](lib) folder
- [lv_config.py](lv_config.py) for use with LV_MicroPython or LVGL_MicroPython
- [color_setup.py](color_setup.py) for use with bare MicroPython, Nano-GUI or Micro-GUI

You will also need the folowing files that match your particular hardware:
- An appropriate `board_config.py` from [board_configs](board_configs).  If you don't find one that matches your hardware, try to find one with the same bus, display controller and MCU as yours.
- The driver for your display controller from [display_drivers](display_drivers)
- The driver for your touchscreen controller (if applicable) from [touch_drivers](touch_drivers)
- If your board uses an IO expander to communicate with the display, for example RGB displays like the ST7701 on the T-RGB board, get the driver from [io_expander_drivers](io_expander_drivers)
- If your board has an encoder, or if you want to add one, get the driver from [encoder_drivers](encoder_drivers).  See [t-embed](board_configs/t-embed) for an example.

# Suggested filesystem structure
Don't forget to put your display and optional touchscreen and encoder drivers somewhere on the path, preferably in /lib or /.
```
├── lib
│   │
│   ├── lcd_bus                 - required if mp_lcd_bus isn't compiled in, otherwise Optional
│   │   │
│   │   ├── __init__.py         - required
│   │   ├── _basebus.py         - required
│   │   ├── _spibus.py          - required for SPIBus
│   │   ├── _i80bus.py          - required for I80Bus
│   │   └── _gpio_registers.py  - required for I80Bus
│   │
│   ├── busdisplay.py           - required in all cases
│   ├── mpdisplay_simpletest.py - optional, does not require gui_framework.py or color_setup.py
│   │
│   ├── lv_driver_framework.py  - LVGL:  required
│   ├── lv_touch_test.py        - LVGL:  recommended
│   │
│   ├── gui_framework.py        - bare MicroPython:  recommended; Nano-GUI & Micro-GUI:  required
│   ├── nano_gui_simpletest.py  - Nano-GUI:  recommended
│   └── gui_simpletest.py       - bare MicroPython:  recommended, requires gui_framework.py 
│                                 and color_setup.py
│
├── board_config.py             - required in all cases
├── lv_config.py                - LVGL targets:  Required
└── color_setup.py              - bare MicroPython:  recommended, requires gui_framework.py;
                                  Nano-GUI:  required; Micro-GUI:  must be copied / renamed to
                                  hardware_setup.py and edited to include button Pin definitions
                                  and Display setup
```

You MAY want to edit your `board_config.py` to:
- Add `from machine import freq; freq(<Your MPU Speed Here>)`
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

For use in Nano-GUI, you MAY want to edit `color_setup.py` to:
- Change the mode to save RAM.  The fewer the number of colors, the less RAM is taken at the expense of a slight increase in refresh time.
  	- `mode = framebuf.RGB565` yields 65,536 colors; creates a frame buffer of size width * height * 2 bytes.  No bounce buffer is needed.  This is the fastest mode.
  	- `mode = framebuf.GS8` yields 256 colors; creates a frame buffer of size width * height bytes and a bounce buffer of size width * 2 bytes.  This is the slowest mode.
  	- `mode = framebuf.GS4_HMSB` yields 16 colors; creates a frame buffer of size width * height // 2 bytes and a bounce buffer of size width * 2 bytes.  This is somewhat slow.
- Rename it to hardware_setup.py, add pin definitions and configure `Display` for use with [Micro-GUI](https://github.com/peterhinch/micropython-micro-gui)

# Usage
## All graphics platforms
No matter which graphics platform you plan to use, it is recommended that you first try the [display_simpletest.py](lib/display_simpletest.py) program.  See the code from that program and [testris](https://github.com/bdbarnett/testris) for bare MicroPython usage examples.  It is also recommended that you try [gui_simpletest.py](lib/qui_simpletest.py), which uses [gui_framework.py](lib/gui_framework.py) and [color_setup.py](color_setup.py), but DOES NOT use Nano-GUI.  It demonstrates a simple way to get started with MPDisplay without using a graphics library that provides widgets.

## Nano-GUI
If you have downloaded the `gui` directory from [Nano-GUI](https://github.com/peterhinch/micropython-nano-gui) to your /lib folder, try [nano_gui_simpletest.py](lib/nano_gui_simpletest.py).  The color of the top-left square should be red, the diagonal line should be green, and the bottom-right square should be blue.

## LVGL
If you have LVGL compiled into your MicroPython binary, try [lv_touch_test.py](lib/lv_touch_test.py).  The color of the buttons should be blue when not selected, green when pressed and red when focused.  If the touch points don't line up with the buttons, it provides directions in the REPL on how to find the correct touch rotation masks.  From the REPL type:
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
