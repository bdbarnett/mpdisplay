<h1 align="center">MPDisplay<br></h1>

<h4 align="center">Universal Display and Event Drivers for *Python</h4>

<p align="center">
  <a href="#about">About</a> •
  <a href="#key-features">Key Features</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#running-your-first-app">Running Your First App</a> •
  <a href="#api">API</a> •
  <a href="#roadmap">Roadmap</a> •
  <a href="#contributing">Contributing</a> •
  <a href="screenshots">Screenshots</a>
</p>

| ![peterhinch's active.py](../screenshots/active.gif) | ![russhughes's tiny_toasters.py](../screenshots/tiny_toasters.gif) |
|-------------------------|--------------------------------|
| @peterhinch's active.py | @russhughes's tiny_toasters.py |

## About

MPDisplay is a universal display, event and device driver framework for multiple flavors of Python, including MicroPython, CircuitPython and CPython (big Python).  It may be used as-is to create graphic frontends to your apps, or may be used as a foundation with GUI libraries such as [LVGL](https://github.com/lvgl/lv_micropython), [MicroPython-touch](https://github.com/peterhinch/micropython-touch) or maybe even a GUI framework you've been thinking of developing.  Its primary purpose is to provide display and touch drivers for MicroPython, but it is equally useful for developers who may never touch MicroPython.

It is important to note that MPDisplay is meant to be a foundation for GUI libraries and is not itself a GUI library.  It doesn't provide widgets, such as buttons, checkboxes or sliders, and it doesn't provide a timing mechanism.  You will need a GUI library to provide those if necessary, although many apps won't need them.  (There is a cross-platform repository [timer](https://github.com/bdbarnett/timer) you can use if you want to used scheduled interrupts.  It works with CPython and MicroPython, but doesn't work with CircuitPython.  You can also use asyncio for timing.)

## Key Features

- May be used without additional libraries to add graphics capabilities to MicroPython, CircuitPython and CPython, with a consistent API across them all.
- Enables moving from one platform to another, for example MicroPython on ESP32-S3 to CPython on Windows without changing your code.  Do your graphics development on your desktop, laptop or ChromeBook and then move to a microcontroller when you are ready to interface with your sensors and devices.  CPython has much better error messages than MicroPython making it easier to troubleshoot when things go wrong!
- Built around devices available on microcontrollers but not necessarily available on desktop operating systems.  For instance, rotary encoders and mouse scroll wheels show up as the same device type and yield the same events.  Touchscreens on microcontrollers yield the same events as mice on desktops.  Likewise with keypads / keyboards.
- Easily extensible.  Use the primitives provided by MPDisplay and add your own libraries, classes and functions to have even greater functionality.
- Provides several built-in color palettes and a mechanism to generate your own palettes.
- Lots of examples included, whether developed specifically for MPDisplay or ported from [Russ Hughes's st7789py_mpy](https://github.com/russhughes/st7789py_mpy).  Also works with all of the examples from Peter Hinch's McroPython GUI libraries [MicroPython-Touch](https://github.com/peterhinch/micropython-touch) and [Nano-GUI](https://github.com/peterhinch/micropython-nano-gui) on MicroPython.
- Support MicroPython on microcontrollers and on Unix(-like) operating systems.
- On MicroPython, works with [kdschlosser's lvgl_micropython bus drivers](https://github.com/kdschlosser/lvgl_micropython), which are very fast bus drivers written in C.
- Works with CircuitPython's FourWire and ParallelBus bus drivers, as well as FrameBufferDisplay based interfaces such as dotclockframebuffer, usb_video and rgbmatrix

## Getting Started

On desktop operating systems, you will need [SDL2](https://github.com/libsdl-org/SDL/releases) or [PyGame](https://www.pygame.org/wiki/GettingStarted).   There's plenty of documentation as to how to install them online.  On microcontrollers, you need to have at least 256K RAM, 1MB flash (for the base library with examples) and a display with a supported bus.  It is highly recommended that you START with an ESP32 series or RP2040 microcontroller with either a SPI or i80 (parallel) bus.  Save yourself some grief and don't start with a display with an RGB bus!  CircuitPython supports SPI, ParallelBus (i80) and RGB buses.  The [lcd_bus](https://github.com/bdbarnett/lcd_bus) Python drivers that are included with the installer support only SPI and i80 buses, and have only been tested on ESP32 series and RP2040.  lcd_bus will likely support SPI on other microcontrollers, but i80 will likely need modification to work.  @kdschlosser's bus drivers in [lvgl_micropython](https://github.com/kdschlosser/lvgl_micropython) support SPI, i80 and RGB buses on ESP32.

There are 3 installers for different platforms in the [installers](../installers) directory.  The Unix and Windows installers will download MPDisplay and related Git repositories into a directory named `gh` and then copy the necessary files into a directory named `mp`.  The Unix installer requires bash and the Windows installer requires Powershell.  The MicroPython installer will use `mip` to download the necessary files only (not the full Github repositories) and may not download all examples for space saving reasons.  It is recommended you begin by using the Unix or Windows installers.  You may copy the files (except the `board_config.py`) directly from the `mp` directory to your microcontroller.  Currently, there isn't an installer for CircuitPython, but there likely will be soon.

NOTE:  You will need a `board_config.py` file from the [board_configs](../board_configs) directory that matches your hardware.  If you are running on a desktop OS, that file is provided for you, and you won't need any other files.  If you are running on a microcontroller such as ESP32 or RP2040, you will also need the [display](../drivers/display), [touch](../drivers/touch) and [encoder](../drivers/encoder) drivers referenced in your `board_config.py`.  Many of them can be found in the [drivers](../drivers) directory.  More details about the `board_config.py` at the end of this section.

### Unix (bash prompt)
```
wget https://raw.githubusercontent.com/bdbarnett/mpdisplay/main/installers/mpd_install.sh
chmod u+x mpd_install.sh
./mpd_install.sh
```

### Windows (PowerShell prompt as Administrator)
```
wget https://raw.githubusercontent.com/bdbarnett/mpdisplay/main/installers/mpd_install.ps1 -OutFile mpd_install.ps1
.\mpd_install.ps1
```

### MicroPython (REPL on a network connected Microcontroller or Unix)
```
import mip
mip.install("github:bdbarnett/mpdisplay/installers/mpd_install.json", target=".")
```

### board_config
As mentioned earlier, on CircuitPython or MicroPython on a microcontroller you will need a `board_config.py` file that matches your hardware.  Many are provided in the [board_configs](../board_configs) directory.  Find one that matches your hardware (or is close so you can modify it), then either download it manually or type the following command if your device is connected to the Internet, substituting <YOUR_BOARD_HERE> with the directory for your board:
```
mip.install("github:bdbarnett/mpdisplay/board_configs/<YOUR_BOARD_HERE>", target=".")
```

## Running your first app

You will need to import the `path.py` file before running any of the examples.

On desktop operating systems, `cd` into the `mp` directory (or wherever you have the files staged) and type:
```
python3 -i path.py
```
or 
```
micropython -i path.py
```

On microcontrollers, either add the following to your `boot.py` (MicroPython) or `code.py` (CircuitPython), or simply import it at the REPL before importing your desired app:
```
import path
```

The  [examples](../examples) directory will be on the system path, so to run an app from it, you just need to type:
```
import calculator  # substitute `calculator` with the file OR directory you want to run, omitting the .py extension
```

To run any of the examples from MicroPython-Touch (remember, its for MicroPython only) type:
```
import gui.demos.various  # substitute `various` with the file you want to run, omitting the .py extension
```

## API

Where possible, existing, proven APIs were used.

- There are currently 4 display classes, and hopefully another `EPaperDisplay` display class will be added soon, although I will need help from the community for this.
  - BusDisplay is for microcontrollers, both on MicroPython and CircuitPython.  CircuitPython provides the required bus drivers, as mentioned elsewhere in this README, but MicroPython doesn't have display bus drivers.  The [lcd_bus](https://github.com/bdbarnett/lcd_bus) repo from the author is included with the installer.  It is my hope that community members will create other C bus drivers similar to @kdschlosser's bus drivers in [lvgl_micropython](https://github.com/kdschlosser/lvgl_micropython).
  - SDL2Display is the preferred class for desktop operating systems as it is faster than PGDisplay.  It uses an SDL `texture` in place of an LCD's Graphics RAM (GRAM).
  - PGDisplay is an optional class for desktop operating systems.  It uses a pygame `surface` in place of an LCD's GRAM.  It can be benificial in a couple of instances:
    - SDL2Display "glitches" on my ChromeBook, but PGDisplay doesn't
    - On Windows, it is easier to install PyGame than SDL2
  - FBDisplay works with CircuitPython framebufferio.FramebufferDisplay objects, such as dotclockframebuffer (RGB displays), usb_video and rgbmatrix.  (usb_video may be the coolest thing you can do with MPDisplay, although I'm not sure how practical or useful it is.  It allows your board to function as a webcam, even without a camera, and to render the display through USB to any application on your host PC that can open a webcam!  My Windows machine sees it as an unsupported device, so it will not work, but it does work on my ChromeBook.  Currently it is limited to RP2040 only and is hardcoded to a 128 x 96 resolution, but that likely will change.  See the [screen capture](../examples/circuitpython_usb_video_chromebook.gif) and the [board_config.py](../board_configs/circuitpython/usb_video/board_config.py) for more details.)
- Names of Events and Devices in eventsys are taken from PyGame and/or SDL2 to keep the API consistent.
- All drawing targets, sometimes referred to as `canvas` in the code, may be written to using the API from MicroPython's framebuffer.FrameBuf API (except .blit())
  - CPython and CircuitPython don't have a `framebuf` module that is API compliant with MicroPython's `framebuf`, so [framebuf.py](../lib/framebuf.py) has been modified from [Adafruit CircuitPython framebuf](https://github.com/adafruit/Adafruit_CircuitPython_framebuf) and is provided for those platforms.  It is not used in MicroPython.
  - A `framebuf_plus` module is provided that subclasses `framebuf` (either built-in or from framebuf.py) and provides additional drawing tools, such as `round_rect`, `bitmap` and `write`.  All methods in framebuf_plus return an Area object with x, y, w and h attributes describing a bounding box of what was changed.  This can be used by applications to only update the part of the display that needs it.  That functionality is implemented in DisplayBuffer and will likely be required by EPaperDisplay when it is implemented.
  - Canvases include, but are not limited to, the display itself, framebuf bytearrays, bmp565 (16-bit Windows Bitmap files) and displaybuf.DisplayBuffer objects.
  - displaybuf.DisplayBuffer implements @peterhinch's API that represents the full display as a framebuffer and allows for 4-, 8- and 16-bit bytearrays while still drawing to the screen as 16-bit.  It is required for `MicroPython-Touch` and is very useful outside of that library as well, especially when memory is constrained.
- Display drivers for MicroPython BusDisplay use the constructor API of CircuitPython's DisplayIO drivers.  This includes rotation = 0, 90, 180, 270 instead of 0, 1, 2, 3.
- BusDisplay can communicate with the underlying bus driver using either CircuitPython's DisplayIO method calls or @kdschlosser's [lvgl_micropython] method calls.
- There are 3 primary mechanism's for fonts: the BinFont class, .text() and .write() methods.  All 3 of these return an Area object as mentioned earlier.  A fourth font mechanism called EZFont is included in the utils folder, but it doesn't return an Area object, which is why it isn't in the lib folder.
  - BinFont is derived from Tony DiCola's 5x7 font class and reads 8x8, 8x14 and 8x16 .bin files from [@spaceraces romfont repo](https://github.com/spacerace/romfont)
  - .text() is written by @russhughes and uses fonts generated by his [text_font_converter](https://github.com/russhughes/st7789py_mpy/blob/master/utils/text_font_converter.py)
  - .write() is written by @russhughes and uses fonts generated by his [write_font_converter](https://github.com/russhughes/st7789py_mpy/blob/master/utils/write_font_converter.py)
  - EZFont is a subclass of [@easytarget's microPyEZfonts](https://github.com/easytarget/microPyEZfonts) which uses fonts generated from [@peterhinch's font-to-py](https://github.com/peterhinch/micropython-font-to-py).
  - NOTE:  @peterhinch's Writer class is inlcuded in MicroPyton-Touch and may be used on MicroPython platforms, but, like EZFont, it doesn't return an Area object.
- Root files - All files that are intended for you to edit to customize your configuration are in the root of your installation:
  - `board_config.py` - required in all circumstances.  Feel free to add your own setup code here, such as for real-time clocks, wifi, sensors, etc.
  - `path.py` - required in all circumstances
  - `color_setup.py` - required for [Nano-GUI](https://github.com/peterhinch/micropython-nano-gui)
  - `hardware_setup.py` - required for [MicroPython-Touch](https://github.com/peterhinch/micropython-touch)
  - `lv_config.py` - required for LVGL
  - `tft_config.py` - required for @russhughes's examples

## Roadmap

- [ ] Much more documentation on Github
- [ ] Document the files to produce output for ReadTheDocs
- [ ] Optimize with more Numpy and Viper code
- [ ] Decrease the memory footprint where possible
- [ ] Test with frozen modules
- [ ] On MicroPython on Unix, the screen gets cleared when the display is rotated.  Microcontroller displays don't do this.  It's not an issue unless you want to draw to the display, rotate it, then draw more on top.  This functionality allow drawing text in all four 90 degree orientations.
- [ ] Scrolling vertically on desktop operating sytems works correctly, but not when rotated.  When rotated, it show scroll horizontally, but continues to scroll vertically.
- [ ] Scrolling on microcontrollers has issues when trying to write spanning the cutoff line.  For instance, if drawing a 16 pixel high image at the 8th line from the cutoff line, the bottom 8 lines don't end up where you expect.  See the [bmp565_sprite](../examples/bmp565_sprite.py) example.
- [ ] Ensure multiple displays work at the same time
- [ ] Implement color depths other than 16 bit
- [ ] Add a Joystick class to eventsys
- [ ] Implement opacity!!!!
- [ ] Create a `canvas.py` and test with [uctx](https://ctx.graphics/uctx/)
- [ ] Test with CircuitPython Blinka on SBC's such as Raspberry Pi 4
- [ ] Need C bus drivers from the community, especially for STM32H7 and MIMXRT

## Contributing

This is a community project and I need your help!  If you have a suggestion that would make this better, please fork the repo and create a pull request.
Don't forget to give the project a star! Thanks again!

1. Fork the project
2. Clone it open the repository in command line
3. Create your feature branch (`git checkout -b feature/amazing-feature`)
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a pull request from your feature branch from your repository into this repository main branch, and provide a description of your changes
