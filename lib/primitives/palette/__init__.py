"""
A palette loader.
"""


def palette(palette_name: str, color_depth: int = 24):
    if palette_name == "material_design":
        from .material_design import Palette
        return Palette(color_depth)
    else:
        raise ValueError("Palette not found")
