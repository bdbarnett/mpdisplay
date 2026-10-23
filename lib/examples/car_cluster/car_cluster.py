# gallery: newwindow
# deps: lvgl
# SPDX-License-Identifier: MIT
"""
car_cluster
====================================================
An electric car's instrument cluster, 800x480, in LVGL.

Two neon dials, speed in mph on the left and motor power in kW on the right,
with the odometer and the miles per kWh under them; the clock, the date and
the outside temperature along the top; the turn indicators; a lit lane
running to the horizon with the car's marker at its foot; and P R N D S
along the bottom.

The car drives itself round a 90 second loop (see ``vehicle.py``). Keys:

  Left / Right  hold that turn indicator on; press again to cancel
  Enter         pause and resume the drive

The dials are art drawn once on a canvas (a colour sweep made of many short
arc segments, a tick ring, a hairline) with three cheap moving parts over it
(see ``ring.py``). Everything is sized from the screen, so it also fits a
smaller landscape display, though it is drawn for 800x480.
"""

import sys
import time

_file = __file__.replace("\\", "/")
_PKG = _file.rsplit("/", 1)[0]
_parts = _file.split("/")
# lib/ is the parent of examples/ (the package lives in examples/car_cluster/).
if "examples" in _parts:
    _idx = _parts.index("examples")
    _src = "/".join(_parts[:_idx]) if _idx else "."
else:
    _src = "."
if not _src:
    _src = "."
if _src not in sys.path:
    sys.path.insert(0, _src)
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

from boarddev import env_bool, env_get, env_set  # noqa: E402

env_set("PYDEVICES_WIDTH", "800")
env_set("PYDEVICES_HEIGHT", "480")
if env_get("PYDEVICES_SCALE") is None:
    env_set("PYDEVICES_SCALE", "1")

import display_driver  # noqa: E402 — wires LVGL into the shared app
import lvgl as lv  # noqa: E402
from display_driver import app  # noqa: E402, F401

from cluster import Cluster  # noqa: E402
from vehicle import Vehicle  # noqa: E402

_ui = None
_vehicle = None
_last_ms = None
_timer = None
_keys = None


def _now_ms():
    try:
        return time.ticks_ms()
    except AttributeError:
        return int(time.time() * 1000)


def _dt_s(now):
    global _last_ms
    if _last_ms is None:
        _last_ms = now
        return 0.04
    try:
        dt = time.ticks_diff(now, _last_ms) / 1000.0
    except AttributeError:
        dt = (now - _last_ms) / 1000.0
    _last_ms = now
    if dt < 0:
        dt = 0.04
    if dt > 0.25:
        dt = 0.25
    return dt


def _clock_text():
    try:
        t = time.localtime()
        hour = t[3] % 12 or 12
        return "%d:%02d %s" % (hour, t[4], "PM" if t[3] >= 12 else "AM")
    except Exception:
        return "9:59 PM"


# Set CAR_CLUSTER_FREEZE=1 to hold the dials still for layout work at the REPL.
_FREEZE = env_bool("CAR_CLUSTER_FREEZE", False)


def _on_tick(timer):
    if _ui is None or _vehicle is None or _FREEZE:
        return
    _vehicle.tick(_dt_s(_now_ms()))
    _ui.set_clock(_clock_text())
    _ui.update()


def freeze(static=True):
    """Hold or resume the drive (a design helper for the REPL)."""
    global _FREEZE
    _FREEZE = bool(static)
    if _FREEZE and _ui is not None and _vehicle is not None:
        _vehicle.speed_mph = 51
        _vehicle.power_kw = 138
        _vehicle.gear = "N"
        _ui.update()
    return _FREEZE


def _on_key(e):
    key = e.get_key()
    if key == lv.KEY.LEFT:
        _vehicle.toggle_signal("left")
    elif key == lv.KEY.RIGHT:
        _vehicle.toggle_signal("right")
    elif key == lv.KEY.ENTER:
        _vehicle.running = not _vehicle.running


def _listen_for_keys(scr):
    """A focused, invisible object in the default group receives the keypad."""
    global _keys
    group = lv.group_get_default()
    if group is None:
        group = lv.group_create()
        group.set_default()
    _keys = lv.obj(scr)
    _keys.set_size(1, 1)
    _keys.set_pos(0, 0)
    _keys.set_style_bg_opa(lv.OPA.TRANSP, 0)
    _keys.set_style_border_width(0, 0)
    _keys.set_style_outline_width(0, lv.STATE.FOCUSED)
    _keys.set_style_outline_width(0, lv.STATE.FOCUS_KEY)
    _keys.remove_flag(lv.obj.FLAG.SCROLLABLE)
    group.add_obj(_keys)
    lv.group_focus_obj(_keys)
    _keys.add_event_cb(_on_key, lv.EVENT.KEY, None)


def build_ui():
    global _ui, _vehicle, _timer, _last_ms

    inst = display_driver.event_loop.current_instance()
    if inst is not None:
        inst.disable()
    try:
        _vehicle = Vehicle()
        scr = lv.screen_active()
        _ui = Cluster(_vehicle, scr)
        _ui.set_clock(_clock_text())
        _listen_for_keys(scr)
        _last_ms = _now_ms()
        _timer = lv.timer_create(_on_tick, 40, None)
        if _FREEZE:
            freeze(True)
    finally:
        if inst is not None:
            inst.enable()


build_ui()

# The app keeps itself alive past the end of this script, and stays live under
# a REPL ``import`` (design session) on signal-driven backends too.
