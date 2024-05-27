# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT


def get_palette(sender=None, name="material_design", **kwargs):
    if name == "wheel":
        from .wheel import WheelPalette as Palette
    elif name == "material_design":
        from .material_design import MDPalette as Palette
    elif name == "cube":
        from .cube import CubePalette as Palette
    else:
        from ._palette import Palette
    return Palette(name, **kwargs)
