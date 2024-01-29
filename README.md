# MPDisplay
Display, touch and encoder drivers for [MicroPython](https://github.com/micropython/micropython), [LV_MicroPython](https://github.com/lvgl/lv_micropython) and [LVGL_MicroPython](https://github.com/kdschlosser/lvgl_micropython)

MPDisplay supports SPIBus displays using the included [lcd_bus.py](bus_drivers/lcd_bus.py).  There is also an implementation of I80Bus written in MicroPython in the [bus_drivers](bus_drivers) directory, but it has limitations and is meant for reference rather than production use.  See the notes in bus_drivers for more details about the I80 implementation.  MPDisplay provides touch and encoder drivers, as well as `lv_driver_framework.py` and `lv_config.py` files for use in LV_MicroPython and LVGL_MicroPython.

# Supported platforms
## MicroPython
[MicroPython](https://github.com/micropython/micropython) doesn't include drivers for color displays nor display buses.  The files in [bus_drivers](bus_drivers) provide SPI and I8080 bus drivers written in MicroPython.  The drivers will work with MicroPython's native `framebuf.FrameBuffer` and other methods of creating buffer objects before they are sent to the display.  If you have an ESP32 and are comfortable compiling MicroPython, you may want to use Kevin Schlosser's [lcd_bus](https://github.com/kdschlosser/lcd_bus) C bus drivers with the display drivers in MPDisplay.

## LV_MicroPython
[LV_MicroPython](https://github.com/lvgl/lv_micropython) is the official repository of LVGL integrated into MicroPython.  It does not include bus drivers separated from display drivers and is more difficult to use if your exact display isn't already supported.  The bus and display drivers in MPDisplay work with LV_MicroPython.

## LVGL_MicroPython
[LVGL_MicroPython](https://github.com/kdschlosser/lvgl_micropython) is created by community member Kevin Schlosser.  It has several improvements over the official repo.  Most significant as far as drivers are concerned, it includes very fast SPI, i80 and RGB bus drivers written in C for ESP32 platforms.  You won't need the files in [bus_drivers](bus_drivers) in this case, but it doesn't hurt to have them on your board.  The compiled-in drivers take precedence over the drivers in the filesystem.  The display drivers in MPDisplay will work with the bus drivers from LVGL_MicroPython.

## Nano-GUI on MicroPython
[Nano-GUI](https://github.com/peterhinch/micropython-nano-gui) is a graphics platform written in MicroPython for MicroPython.  It provides its own drivers, but it is modular and may use the drivers provided by MPDisplay as well.  The benefit of using MPDisplay with Nano-Gui is that more displays are supported, particularly I80 and RGB Bus displays.  Also, the same board_config.py will work with both LVGL and Nano-GUI.

# Quickstart
Flash your board with your preferred version of MicroPython listed above.

Download the following files and upload them to the /lib folder on your board:
- The [lib](lib) folder, which includes these files:
  	- `busdisplay.py` (required)
  	- `display_simpletest.py` (optional)
- If you are using either LV_MicroPython or LVGL_MicroPython:
  	- `lv_config.py` (required for LVGL targets)
  	- `lv_driver_framework.py` (required for LVGL targets)
  	- `lv_touch_test.py` (optional for LVGL targets)
- If you are using Nano-GUI (or Micro-GUI):
  	- `color_setup.py` (required for Nano-GUI targets)
  	- `nano_gui_framework.py` (required for Nano-GUI targets)
  	- `nano_gui_simpletest.py` (optional for Nano-GUI targets)
- The `lcd_bus.py` file from [bus_drivers](bus_drivers).  (Not required if you have [lcd_bus](https://github.com/kdschlosser/lcd_bus) or [LVGL_MicroPython](https://github.com/kdschlosser/lvgl_micropython) on ESP32, but it won't hurt to have this file in your /lib folder anyway, so you may as well grab it.)
  	- If your board has an I80 bus, you will also need `i80bus.py` from [bus_drivers](bus_drivers).
- An appropriate `board_config.py` from [board_configs](board_configs).  If you don't find one that matches your hardware, try to find one with the same bus, display controller and MCU as yours.
- The driver for your display controller from [display_drivers](display_drivers)
- The driver for your touchscreen controller (if applicable) from [touch_drivers](touch_drivers)
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
- Change from blocking mode to non-blocking mode (currently has issues in the C lcd_bus bus drivers)
- Enable encoder(s) if you are using them.  Simply uncomment the last line.

For use in Nano-GUI, you MAY want to edit the `color_setup.py` to:
- Change the mode to save RAM.  The fewer the number of colors, the less RAM is taken at the expense of a slight increase in refresh time.
  	- `mode = framebuf.RGB565` yields 65,536 colors; creates a frame buffer of size width * height * 2.  No bounce buffer is needed.
  	- `mode = framebuf.GS8` yields 256 colors; creates a frame buffer of size width * height and a bounce buffer of size width * 2
  	- `mode = framebuf.GS4_HMSB` yields 16 colors; creates a frame buffer of size width * height // 2 and a bounce buffer of size width * 2
- Rename it to hardware_setup.py and add pin definitions for use with [Micro-Gui](https://github.com/peterhinch/micropython-micro-gui)

# Coexistence with lcd_bus (C bus drivers)
Note, if you have lcd_bus compiled in, whether from LVGL_MicroPython or if you added it yourself, and also have lcd_bus.py in your /lib folder,
the former takes precedence.  In this case, if you want to force MicroPython to use lcd_bus.py, change the include line in your board_config.py from
```
from lcd_bus include ...
```
to
```
from lib.lcd_bus include ...
```

# Usage
## All graphics platforms
No matter which graphics platform you plan to use, it is recommended that you first try the [display_simpletest.py](lib/display_simpletest.py) program.  See the code from that program and [testris](https://github.com/bdbarnett/testris) for non-LVGL usage examples.

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
## Nano-GUI
TODO 

# Throughput comparison

Running display_simpletest.py, which allocates ten 64x64 blocks and writes them to the screen at random.								
There are 18.75 blocks per screen on the ILI9341 with 320x240 resolution.
Test boards:
- ESP32 without PSRAM (BOARD=ESP32_GENERIC_S3), freq=80,000,000											
- RP2040 (BOARD=ADAFRUIT_QTPY_RP2040), freq=62,500,000											
				
											
Board	|	Bus Driver	|	Byte Swap	|	Alloc	        |	Block/sec	|	FPS	    |
----	|	--------	|	---	        |	---     	|	---	        |	---	    |
ESP32	|	C	        |	false           |	heap_caps	|	825	        |	44.0        |
ESP32	|	C	        |	false	        |	bytearray	|	783	        |	41.8	    |
ESP32	|	C	        |	true	        |	heap_caps	|	495	        |	26.4	    |
ESP32	|	C        	|	true	        |	bytearray	|	487	        |	26.0	    |
ESP32	|	Python	        |	false	        |	heap_caps	|	578	        |	30.8	    |
ESP32	|	Python	        |	false	        |	bytearray	|	549	        |	29.3	    |
ESP32	|	Python	        |	true	        |	heap_caps	|	24	        |	1.3	    |
ESP32	|	Python	        |	true	        |	bytearray	|	24	        |	1.3	    |
RP2040	|	Python	        |	false	        |	bytearray	|	402	        |	21.4	    |
rp2040	|	Python	        |	true	        |	bytearray	|	13	        |	0.7	    |

# My board isn't listed
Please note, I am only providing configs for boards that have an integrated display or, on occasion, boards and displays that may be directly plugged into one another, such as Feather, EYE-SPI, Qualia or QT-Py.  I will not create configs for any setup that requires wiring.  Those setups are generally custom built, but you may use the board configs here as an example.  Please consider contributing your board_config if your hardware doesn't require custom wiring.

I am considering creating board configs by request IF you provide a gift certificate to pay for the board from Adafruit, DigiKey, Amazon, Pimoroni or wherever your board is stocked.  I'll post that here if I decide to do that.

# TODO
Short term
- Create a micro_gui_framework.py for Micro-GUI similar to `lv_driver_framework.py`
- Document how to create custom board_configs, display_drivers and touch_drivers.
- Use a factory method in lcd_bus/__init__.py to choose the appropriate bus driver.  Other files in the lcd_bus folder would be _spibus.py, _i80bus.py and possibly platform specific versions of those.
  	- `from lcd_bus import I80Bus` would then load the appropriate I80bus class without taking up unnecesary RAM by loading unneeded classes.
  	- See the [lazy loader](https://github.com/peterhinch/micropython-samples/blob/master/import/IMPORT.md#2-python-packages-and-the-lazy-loader) from [PEP 562](https://peps.python.org/pep-0562/) and an [example](https://github.com/micropython/micropython/blob/master/extmod/asyncio/__init__.py)
- I80bus assumes pins will be non-sequential and on multiple ports.  Create a version that doesn't, so lookup tables aren't necessary in order to increase speed.
- Add keypad support to be subclassed in lv_driver_framework.py and micro_gui_framework.py
	- hardware pins
   	- matrix of pins
   	- capacitive touch pins
   	- capacitive touch chips
   	- io expander
- Enable installation from mip.install
- Create documentation with readthedocs
- Test boards with RGB buses using [lcd_bus](https://github.com/kdschlosser/lcd_bus) and [LVGL_MicroPython](https://github.com/kdschlosser/lvgl_micropython):
	- qualia
   	- t-rgb_2.1in_full_circle
   	- esp32-s3-lcd-4.3

Long term
- Add I2CBus
- Implement color OLED display drivers in `busdisplay.py`:
  	- ssd1331, ssd1351
- Implement mono I2C bus drivers in `lcd_bus.py` and `busdisplay.py`
	- sh1106, ssd1305, ssd1306, ssd1325, ssd1327
- Implement ePaper support.
