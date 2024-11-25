#!/usr/bin/env python3
"""
Universal MicroPython package installer for pydisplay.
=====================================================

Includes 2 functions that install from different sources:
- 'lib_install': Installs from the PyDevices fork of the micropython-lib library.
    - By default, installs all modules as precompiled bytecode (.mpy) files.
    - Includes:
        - 6 core packages:
            - displaybuf
            - displaysys
            - eventsys
            - graphics
            - palettes
            - timer
        - 6 display extensions for the displaysys package:
            - displaysys-busdisplay
            - displaysys-fbdisplay
            - displaysys-jndisplay
            - displaysys-pgdisplay
            - displaysys-psdisplay
        - pydisplay-bundle - Bundle package including all 6 core packages and 6 extensions.
        - pydisplay-board_config - The default board configuration file - for desktop environments.
        - Display drivers, for example:
            - gc9a01
            - ili9341
            - st7789
        - Touch drivers, for example:
            - ft6x36
            - cst226
            - xpt2046
        - Note the add_ons, examples, spibus and i80bus packages are not available from the PyDevices
          fork of the micropython-lib repository.  It isn't the correct place for add_ons and examples,
          and spibus and i80bus use micropython.viper, which is not supported by micropython-lib.
- 'repo_install': Installs from the PyDevices/pydisplay repository on GitHub.
    - Can retrieve any file from the repository, not just packages.
    - Retrieves files as is, without precompilation (no .mpy files).
    - Includes:
        - 6 core packages:
            - /packages/displaybuf.json
            - /packages/displaysys.json (includes all 6 display extensions)
            - /packages/eventsys.json
            - /packages/graphics.json
            - /packages/palettes.json
            - /packages/timer.json
        - /package.json (or simply '/') - Bundle package including all 6 core packages and 6 extensions.
        - 4 additional packages:
            - /packages/add_ons.json
            - /packages/examples.json
            - /packages/spibus.json
            - /packages/i80bus.json
        - Board package files for MicroPython boards from the 'board_configs' directory.
          Note: pointing to a directory implies using a package.json file in that directory.
            - These install:
                - a custom board_config.py for the specified board
                - any required display, touch or encoder drivers
                - the spibus or i80bus driver if required
            - Examples:
                - /board_configs/busdisplay/i80/wt32sc01-plus
                - /board_configs/busdisplay/spi/t-display-s3-pro
                - /board_configs/fbdisplay/qualia_tl040hds20
        - Can be used to get non-packaged files from the repository, useful for getting
            - /src/lib/board_config.py - The default board configuration file - for desktop environments.
            - A board-specific board_config.py without using the package to get the drivers:
                - /board_configs/busdisplay/i80/wt32sc01-plus/board_config.py
            - Note: there aren't any package files for individual drivers since they may be
              retrieved directly, for example:
                - /drivers/display/gc9a01.py
- Since micropython-lib packages will never have a '/' in their name and the PyDevices/pydisplay
  repository packages always have a '/', there is a third function that will determine which of the
  2 installers to use.  It is simply called 'install'.




Install script for pydisplay with control over each package.
Uses 'mip' to download directly to a MicroPython device or
uses 'mpremote' to download to an attached microcontroller
from Python.

To download this file to your device, run the following command:
```MicroPython
import mip
mip.install("github:PyDevices/pydisplay/install.py")
```
or
```bash
wget https://raw.githubusercontent.com/PyDevices/pydisplay/main/install.py
```

Comment out the packages you don't want to install and
change the target directories if needed.

Usage (MicroPython or CPython):
    import install

Equivalent to copying the contents of the 'src' directory of the repository
to your working directory / microcontroller.

Also equivalent to running the following commands in the REPL:
```
import mip
mip.install("github:PyDevices/pydisplay", target=".")  # Does not include examples
mip.install("github:PyDevices/pydisplay/packages/examples.json", target="examples")
```
"""


from sys import implementation


pkg_index = "https://PyDevices.github.io/micropython-lib/mip/PyDevices"
prefix = "github:PyDevices"


if implementation.name == "micropython":
    import mip
    def lib_install(package, **kwargs):
        """
        Installs 'library packages' from the PyDevices fork of micropython-lib.
        Runs on the MicroPython device.
        """
        mip.install(package, index=pkg_index, **kwargs)

    def repo_install(package, **kwargs):
        """
        Installs 'repository packages' (and files) from the PyDevices/pydisplay repository on GitHub.
        Runs on the MicroPython device.
        """
        mip.install(prefix + package, **kwargs)
else:
    import os
    def lib_install(package, target="", index=None, mpy=True):
        """
        Installs 'library packages' from the PyDevices fork of micropython-lib.
        Runs on the host computer.
        """
        if index:
            raise ValueError("The 'index' option is not supported for 'lib_install'.")
        option = "" if mpy else "--no-mpy"
        os.system(f"mpremote mip install {option} --index {pkg_index} --target={target} {package}")

    def repo_install(package, target="", index=None, mpy=False):
        """
        Installs 'repository packages' (and files) from the PyDevices/pydisplay repository on GitHub.
        Runs on the host computer.
        """
        if mpy:
            raise ValueError("The 'mpy' option is not supported for 'repo_install'.")
        if index:
            raise ValueError("The 'index' option is not supported for 'repo_install'.")
        os.system(f"mpremote mip install --target={target} {prefix+package}")


def install(package, **kwargs):
    if "/" in package:
        repo_install(package, **kwargs)
    else:
        lib_install(package, **kwargs)

####################################################################################################
# Library packages - install as precompiled bytecode (.mpy) files
####################################################################################################

## The bundle of all 6 core packages and 6 display extensions:
# install("pydisplay-bundle")

## The 6 core packages:
# install("displaybuf")
# install("displaysys")
# install("eventsys")
# install("graphics")
# install("palettes")
# install("timer")

## The 6 display extensions:
# install("displaysys-busdisplay")
# install("displaysys-fbdisplay")
# install("displaysys-jndisplay")
# install("displaysys-pgdisplay")
# install("displaysys-psdisplay")
# install("displaysys-sdldisplay")

## An example board configuration file for desktop environments
# install("board_config")

## Display drivers, for example:
# install("gc9a01")
# install("ili9341")
# install("st7789")

## Touch drivers, for example:
# install("ft6x36")
# install("cst226")
# install("xpt2046")


####################################################################################################
# Repository packages - contains no precompiled bytecode (.mpy) files
####################################################################################################

## The bundle of all 6 core packages and 6 display extensions:
# install("/")  # or install("/package.json")

## The 6 core packages:
# install("/packages/displaybuf.json")
# install("/packages/displaysys.json")  # Includes all 6 display extensions
# install("/packages/eventsys.json")
# install("/packages/graphics.json")
# install("/packages/palettes.json")
# install("/packages/timer.json")

## 4 additional packages:
# install("/packages/add_ons.json", target="add_ons")
# install("/packages/examples.json", target="examples")
# install("/packages/spibus.json")
# install("/packages/i80bus.json")

## Board package files for MicroPython boards from the 'board_configs' directory.
## For example:
# install("/board_configs/busdisplay/i80/wt32sc01-plus")
# install("/board_configs/busdisplay/spi/t-display-s3-pro")
# install("/board_configs/fbdisplay/qualia_tl040hds20")

## Non-packaged files from the repository:
## The default board configuration file - for desktop environments
# install("/src/lib/board_config.py")

####################################################################################################
# Recommended "full" installation
####################################################################################################

install("pydisplay-bundle")
install("/packages/add_ons.json", target="add_ons")
install("/packages/examples.json", target="examples")

##  Only one of the following should be uncommented
# install("board_config")  # Installs the default as a .mpy file (not editable)
install("/src/lib/board_config.py")  # Installs the default and remains editable
# install("/board_configs/busdisplay/i80/wt32sc01-plus") #  Change to match your hardware
