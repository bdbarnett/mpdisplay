Getting Started

TL;DR - Download the repository, cd into the src directory and run the examples.  Be sure to import path.py first.  More on that later.

# Downloading:
## The repository:
To get the whole repository, you can download and extract the [zip file](https://github.com/PyDevices/pydisplay/archive/refs/heads/main.zip) or clone the repository with:
```bash
git clone https://github.com/PyDevices/pydisplay.git
```

## The packages:
To get only the packages for your use case, you can download the packages individually.  Currently only MicroPython MIP packages are available.  PIP packages will be released when the project is more mature, and CircuitPython `circup` packages may be provided in the future.  There is a [master package](package.json) that includes all the MIP packages except the examples.  To download the master package, either:
Type the following at the MicroPython REPL:
```python
import mip
mip.install("github:PyDevices/pydisplay", target=".")  # Does not include examples
mip.install("github:PyDevices/pydisplay/packages/examples.json", target=".")  # Optional examples
```
or type the following at your shell prompt:
```bash
mpremote mip install --target "." "github:PyDevices/pydisplay"
mpremote mip install --target "." "github:PyDevices/pydisplay/packages/examples.json"
```

Instead of using the master package, you may download the components individually.  The components are listed in the [packages](packages) directory.  The installation file [install.py](install.py) lists all the packages and can be modified to only download the packages you need or to use as a reference for downloading the packages individually.  `install.py` is a Python script that can be run from the (big) Python REPL of a machine connected to a microncontroller running MicroPython or directly from the MicroPython REPL.  Simply save it to your working directory and type `import install`.

# Running the examples:
If you downloaded the full repository, installed the master package or used the `install.py` file, your file system will be laid out like the src directory in the repository.  You will need to import the [path.py](src/path.py) file to set the path to the packages.  There will be an explanation of `path.py` in another part of this documentation that also explains how to eliminate it by installing all the packages into the `lib` directory of your MicroPython device.

## For Python and MicroPython on desktop OSes:
1.  Install PyGame and/or SDL2 (TODO: Explain this better)
2.  cd into the src directory or the directory where you installed the packages
3.  lauch the Python or MicroPython REPL
4.  `import path`
5.  `import mdisplay_touch_test` or whatever you want to run

## For MicroPython on microcontrollers:
You will need a `board_config.py` file that matches your hardware.  Many are provided in the [board_configs](board_configs) directory.  If you don't find one that matches your hardware, look for one that is similar.  For instance, using the same bus (SPI or I80), graphics controller (e.g. ILI9341), touchscreen (e.g. FT6X36) and microcontroller (e.g. ESP32-S3).  Matching all 4 may not happen, but put priority on the bus and graphics controller.

You can download the files manually, or you can download the packages with mip or mpremote.  The following example will put the files in the `lib` directory of your MicroPython device.  It doesn't matter where they are so long as they are in a directory that is on the path.
```bash
mpremote mip install "github:PyDevices/pydisplay/board_configs/<your_board>"
```
or
```Python
import mip
mip.install("github:PyDevices/pydisplay/board_configs/<your_board>")
```
Then you can run the examples directly from the `src` directory on your computer by running 
1. `mpremote mount .`
2. `import path`
3. `import mdisplay_touch_test` or whatever you want to run

To put the files on your microcontroller, you can copy them from your computer the same as you do any other files, or follow the directions above for downloading the packages.

See [WSL USB Manager](https://gitlab.com/alelec/wsl-usb-gui) for a way to access your microcontrolelr from Windows Subsystem for Linux.

## For CircuitPython:
First get your hardware working with the Adafruit libraries.  It will be much simpler if you get the hardware working with DisplayIO first.  There aren't any installers for CircuitPython yet, so you will need to copy the directories you need from the `src` directory to your board.  There aren't many board_configs for CircuitPython yet, so you will need to use the [CircuitPython examples in board_configs/circuitpython](board_configs/circuitpython) as a reference to create your `board_config.py` file.  Just make sure you place it somewhere on the path.

SPI and I80 based displays in CircuitPython will use `displaysys.busdisplay.BusDisplay`.  To force CircuitPython to load those files provided by displaysys instead of the ones provided by Adafruit, you will need to edit the graphics driver file to point to the displaysys version.  For instance, if you are using an ILI9341 display, you will need to edit the `adafruit_ili9341.py` file and change the line:
```
from busdisplay import BusDisplay
```
to 
```
try:
  from displaysys.busdisplay import BusDisplay
except ImportError:
  from busdisplay import BusDisplay
```

Framebuffer based devices such as hardware parallel buses (called RGB666 by Adafruit) and USB Video class devices won't need anything special after you get CircuitPython to see them.  They use displaysys's `displaysys.fbdisplay.FBDisplay`.  See the CircuitPython example board_configs for more information.

## For Jupyter Notebooks:
Note:  User input such emulating touchscreens and key input has not been implemented in displaysys for Jupyter Notebook yet.  Also, if your script has an endless loop, you will need to interrupt the kernel to stop it with `Ctrl+Shift+P` `Jupyter: Restart Kernel`.

Make sure you can run Jupyter Notebooks first.  That is beyond the scope of this document.  The author uses VS Code with the Python and Jupyter extensions.  Once you have done that, then just open the example [jupyter_notebook.ipynb](src/utils/jupyter_notebook.ipynb) and run the cells.  As always, start with `import path`.

## For PyScript:
The PyScript implementation of displaysys is very much a work in progress and is not currently a priority for the author.  As with all other parts of pydisplay, the author is open to pull requests for `displaysys.psdisplay.PSDisplay` and the files in the [html](html) directory.

PyScript uses `asyncio` and requires Python scripts that run in it to play nice with asyncio by either not having an endless looop or calling `await`.  Only a portion of the examples do that, but you can get an idea of how it works in the [calculator.py](src/examples/calculator.py) example.

Only touchscreen input has been implemented in displaysys for PyScript.  Key input will come later as time permits or as pull requests are submitted.

You can see and interact with PyScript on the web at [https://PyDevices.github.io/pydisplay/](https://PyDevices.github.io/pydisplay/).  You can also run it from your computer by cloning the repository, cd to the root of the repository (not the src directory) and running `python -m http.server`.  Then open your browser to [http://localhost:8000/](http://localhost:8000/).

# Minimum packages required:
If you don't need the graphics library and don't plan to run many of the examples, you only need a couple of the packages.  For instance, if you plan to use displaysys for another library such as LVGL or just the MicroPython framebuffer, you only need:
1.  [displaysys](src/lib/displaysys/) directory from [displaysys.json](packages/displaysys.json)
3.  The [eventsys](src/lib/eventsys/) directory from [eventsys.json](packages/eventsys.json) if you are using it to manage your touchscreen or other input devices
3.  A `board_config.py` file from [board_configs](board_configs/) that matches your hardware.
  -  Includes a display from [displaysys](src/lib/displaysys/), such as [busdisplay.py](src/lib/displaysys/busdisplay.py)
  -  Includes a bus from [lib](src/lib/) if you are using busdisplay in particular, such as [spibus.py](src/lib/spibus.py) or [i80bus.py](src/lib/i80bus.py)
4.  If you are using LVGL on MicroPython, you can use the [lv_config.py](src/examples/lv_config.py) file from [examples](src/examples/).  It has not been thoroughly tested, so please submit pull requests if you find and correct errors.

An example minimum download script for LVGL might look like this:
```python
import mip
mip.install("github:PyDevices/pydisplay/packages/displaysys.json")
mip.install("github:PyDevices/pydisplay/packages/eventsys.json")
mip.install("github:PyDevices/pydisplay/board_configs/<your_board>")
mip.install("github:PyDevices/pydisplay/src/examples/lv_config.py")
```
or
```bash
mpremote mip install "github:PyDevices/pydisplay/packages/displaysys.json"
mpremote mip install "github:PyDevices/pydisplay/packages/eventsys.json"
mpremote mip install "github:PyDevices/pydisplay/board_configs/<your_board>"
mpremote mip install "github:PyDevices/pydisplay/src/examples/lv_config.py"
```
See [this Wokwi project](https://wokwi.com/projects/404248867674669057) for an example of a minimum configuration.
