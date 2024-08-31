#!/usr/bin/micropython
"""
Install script for mpdisplay with control over each package.
Comment out the packages you don't want to install and 
change the target directories if needed.

Equivalent to copying the contents of the 'src' directory of the repository
to your working directory / microcontroller.

Also equivalent to running the following commands in the REPL:
```
import mip
mip.install("github:bdbarnett/mpdisplay", target=".")  # Does not include examples
mip.install("github:bdbarnett/mpdisplay/packages/examples.json", target=".")
```
"""
from sys import implementation
if implementation.name == "micropython":
    import mip # type: ignore
    def install(package, target):
        mip.install(package, target=target)
else:
    import os
    def install(package, target):
        os.system(f"mpremote mip install --target {target} {package}")


src_base = "github:bdbarnett/mpdisplay/packages/"
dest_base = "."

# List of package, target pairs
packages = [
    ("configs", ""),
    ("examples", ""),
    ("extras", ""),
    ("area", "/lib"),
    ("i80bus", "/lib/buses"),
    ("spibus", "/lib/buses"),
    ("basedisplay", "/lib/displays"),
    ("busdisplay", "/lib/displays"),
    ("dtdisplay", "/lib/displays"),
    ("fbdisplay", "/lib/displays"),
    ("jndisplay", "/lib/displays"),
    ("psdisplay", "/lib/displays"),
    ("eventsys", "/lib"),
    ("graphics", "/lib"),
    ("timer", "/lib"),
]

# Install each package
for name, path in packages:
    package = src_base + name + ".json"
    target = dest_base + path
    install(package, target)
