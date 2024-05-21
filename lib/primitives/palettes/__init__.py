# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT


def get_palette(sender=None, name="material_design", color_depth=16, swapped=False, **kwargs):
    if name == "material_design":
        from .material_design import Palette
        return Palette(name, color_depth, swapped, **kwargs)
    else:
        raise ValueError("Palette not found")
