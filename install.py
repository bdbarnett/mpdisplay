"""
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

import mip


src_base = "github:bdbarnett/mpdisplay/packages/"
dest_base = "."

# List of package, target pairs
packages = [
    ("configs", ""),
    ("examples", ""),
    ("extras", ""),
    ("busdisplay", "/lib/displays"),
    ("dtdisplay", "/lib/displays"),
    ("fbdisplay", "/lib/displays"),
    ("jndisplay", "/lib/displays"),
    ("psdisplay", "/lib/displays"),
    ("area", "/lib"),
    ("eventsys", "/lib"),
    ("framebuf", "/lib"),
    ("graphics", "/lib"),
    ("palettes", "/lib"),
    ("timer", "/lib"),
]

# Install each package
for name, path in packages:
    package = src_base + name + ".json"
    target = dest_base + path
    mip.install(package, target=target)
