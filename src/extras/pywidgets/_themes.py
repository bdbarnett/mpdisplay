# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
from ._constants import ICON_SIZE
from palettes import get_palette  # noqa: F401
try:
    from os import sep  # PyScript doesn't have os.sep
except ImportError:
    sep = "/"


class IconTheme:
    _suffix = "dp.pbm"
    _home = "home_filled_"
    _up_arrow = "keyboard_arrow_up_"
    _down_arrow = "keyboard_arrow_down_"
    _left_arrow = "keyboard_arrow_left_"
    _right_arrow = "keyboard_arrow_right_"
    _check_box_checked = "check_box_"
    _check_box_unchecked = "check_box_outline_blank_"
    _radio_button_checked = "radio_button_checked_"
    _radio_button_unchecked = "radio_button_unchecked_"
    _toggle_on = "toggle_on_"
    _toggle_off = "toggle_off_"

    def __init__(self, path):
        """
        A class to manage icon themes.  The path is the directory where the icons are stored.
        Icon file names are in the format "icon_name_18dp.pbm" where 18dp is the size of the icon.
        Valid sizes are in the ICON_SIZE enumeration, which are 18, 24, 36, and 48 pixels.

        Args:
            path (str): The path to the directory containing the icon files.

        Usage:
            from pywidgets import IconTheme, ICON_SIZE
            icon_theme = IconTheme("/path/to/icons/")
            ...
            icon_button = IconButton(screen, icon_file=icon_theme.home(ICON_SIZE.LARGE), ...)
        """
        try:
            from os import sep  # PyScipt doesn't have os.sep
        except ImportError:
            sep = "/"
        if path[-1] != sep:
            path += sep
        self._path = path

    def _icon(self, name, size):
        if size not in ICON_SIZE:
            raise ValueError("Invalid icon size.")
        return f"{self._path}{getattr(self, "_" + name)}{size}{self._suffix}"
    
    def __getattr__(self, name):
        if name.startswith("_"):
            return super().__getattr__(name)
        return lambda size: self._icon(name, size)
icon_theme = IconTheme(sep.join(__file__.split(sep)[0:-1]) + sep + "icons" + sep)


class ColorTheme:
    def __init__(self, pal):
        self.background = pal.white[0]
        self.on_background = pal.black[0]
        self.surface = pal.white[0]
        self.on_surface = pal.black[0]
        self.primary = pal.blue[4]
        self.on_primary = pal.white[0]
        self.secondary = pal.amber[0]
        self.on_secondary = pal.black[0]
        self.error = pal.red[0]
        self.on_error = pal.white[0]
        self.primary_variant = pal.blue[3]
        self.secondary_variant = pal.deep_purple[4]
        self.tertiary = pal.amber[0]
        self.on_tertiary = pal.black[0]
        self.tertiary_variant = pal.amber[4]
        self.transparent = False
