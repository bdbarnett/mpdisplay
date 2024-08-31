#!/usr/bin/micropython
"""
NOTE:  This file may be removed from the repository in the future
and it's contents will be put into a documenation file such as INSTALL.md.

mip install script for mpdisplay with control over each package.
Comment out the packages you don't want to install and 
change the target directory if needed.

Equivalent to copying the contents of the 'src' directory of the repository
to your working directory / microcontroller.

Also equivalent to running the following commands in the REPL:
```
import mip
mip.install("github:bdbarnett/mpdisplay", target=".")  # Does not include examples
mip.install("github:bdbarnett/mpdisplay/packages/examples.json", target=".")
```
"""

import mip # type: ignore


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
    mip.install(package, target=target)
