"""
Checks if all the colors in a palette are present in larger palettes.
"""
from pygfx.palettes import get_palette

cube8 = get_palette("cube", size=2)
cube27 = get_palette("cube", size=3)
cube64 = get_palette("cube", size=4)
cube125 = get_palette("cube", size=5)
win16 = get_palette("wheel")  # Wheel uses the Windows 16 color list regardless of length
md = get_palette("material_design")  # Material Design uses its own color list

misses = 0
def compare(pal1, pal2):
    global misses
    for x in dir(pal1):
        if x[0] == "_":  # Skip private attributes
            continue
        if x.upper() != x:  # Skip attributes that are not color names (all caps)
            continue
        if x not in dir(pal2):
            print(f"Miss:  {x} in {pal1.name} but not in {pal2.name}")
            misses += 1


compare(cube8, win16)
compare(cube8, cube27)
compare(cube8, cube64)
compare(cube8, cube125)
compare(win16, cube27)
compare(win16, cube64)
compare(win16, cube125)
compare(cube27, cube64)
compare(cube27, cube125)
compare(md, cube64)
compare(md, cube125)

nisses = "No" if misses == 0 else misses
print(f"\n{nisses} misses found.")
