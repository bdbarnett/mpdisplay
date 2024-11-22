"""
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

if implementation.name == "micropython":
    import mip

    def install(package, target):
        mip.install(package, target=target)
else:
    import os

    def install(package, target):
        os.system(f"mpremote mip install --target {target} {package}")


src_base = "github:PyDevices/pydisplay/packages/"
dest_base = "./"

# List of package, target pairs
packages = [
    ("configs", "configs"),
    ("displays", "displays"),
    ("examples", "examples"),
    ("extras", "extras"),
    ("displaybuf", "lib"),
    ("displaysys", "lib"),
    ("eventsys", "lib"),
    ("graphics", "lib"),
    ("palettes", "lib"),
    ("timer", "lib"),
    ("path.py", ""),
]

# Install each package
for name, path in packages:
    package = src_base + name + ".json"
    target = dest_base + path
    install(package, target)
