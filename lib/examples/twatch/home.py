"""The home screen: one button per app. The crown goes back to the face."""

from . import services as sv
from . import ui

APPS = (
    ("Watch", "face"),
    ("Steps", "steps"),
    ("Remote", "remote"),
    ("Sound", "sound"),
    ("Power", "power"),
    ("LoRa", "lora"),
    ("Wi-Fi", "wifi"),
)


def main(scope):
    scr = ui.screen(scope)
    scr.set_style_pad_row(8, 0)
    grid = ui.row(scr)
    grid.set_style_pad_row(8, 0)
    w = sv.W // 2 - 14
    rows = (len(APPS) + 1) // 2
    h = (sv.H - 16 - (rows - 1) * 8) // rows
    for text, name in APPS:
        ui.button(grid, text, (lambda n: lambda: sv.go(n))(name), width=w, height=h)
    sv.use(scope)
