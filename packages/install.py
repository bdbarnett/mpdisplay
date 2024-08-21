import mip

# List of package, target pairs
packages = [
    ("configs", "configs"),
    ("examples", "examples"),
    ("extras", "extras"),
    ("busdisplay", "lib/displays"),
    ("dtdisplay", "lib/displays"),
    ("fbdisplay", "lib/displays"),
    ("jndisplay", "lib/displays"),
    ("psdisplay", "lib/displays"),
    ("area", ""),
    ("eventsys", ""),
    ("framebuf", ""),
    ("graphics", ""),
    ("palettes", ""),
    ("timer", ""),
]

# Install each package
for package, target in packages:
    mip.install(package, target=target)