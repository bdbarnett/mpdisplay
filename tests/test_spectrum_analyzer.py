# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""``Spectrum.start()`` paints only what the meter owns when it was placed.

A meter given ``y=`` shares the panel with the app's own UI (an LVGL screen
above it, say), so starting it must not clear the rest of the panel. A meter
left at its default place, at the bottom, clears the panel first, as the demo
wants. The drawing itself (``spectrum_view``, ``pygraphics``) is stood in for:
these tests are about which rows ``start()`` touches.
"""

import importlib.util
from pathlib import Path
import sys
import types
import unittest

import _env  # noqa: F401

_ANALYZER = (
    Path(__file__).resolve().parent.parent / "lib" / "examples" / "spectrum" / "analyzer.py"
)


class _View:
    def __init__(self, width, height, bands=None, style="smooth"):
        self.width, self.height, self.bands = width, height, bands or 8

    def strip(self, y, h):
        return bytearray(self.width * h * 2)

    def _build_bar_columns(self):
        pass


class _Display:
    width, height = 100, 60

    def __init__(self):
        self.fills = []
        self.blits = []

    def fill_rect(self, x, y, w, h, c):
        self.fills.append((x, y, w, h))

    def blit_rect(self, buf, x, y, w, h):
        self.blits.append((x, y, w, h))


class _App:
    def every(self, fn, period=None):
        return types.SimpleNamespace(deinit=lambda: None)


def _load_analyzer(test):
    try:
        import multimer  # noqa: F401
    except ImportError:
        test.skipTest("multimer is not importable")
    stubs = {
        "pygraphics": types.SimpleNamespace(RGB565=1, FrameBuffer=None),
        "spectrum_view": types.SimpleNamespace(SpectrumView=_View, band_count_for=lambda w: 16),
    }
    saved = {name: sys.modules.get(name) for name in stubs}
    sys.modules.update(stubs)
    try:
        spec = importlib.util.spec_from_file_location("_spectrum_analyzer_under_test", _ANALYZER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        for name, mod in saved.items():
            if mod is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = mod
    return module


class _Source:
    bands = 8

    def levels(self, t):
        return [0.0] * self.bands


class TestStartClears(unittest.TestCase):
    def setUp(self):
        self.analyzer = _load_analyzer(self)
        self.d = _Display()

    def _start(self, **kwargs):
        meter = self.analyzer.Spectrum(self.d, _Source(), height=30, **kwargs)
        meter.start(_App())
        return meter

    def test_placed_meter_leaves_the_rest_of_the_panel_alone(self):
        self._start(y=0)
        self.assertEqual([], self.d.fills, "start() cleared rows the meter doesn't own")
        self.assertEqual([(0, 0, 100, 30)], self.d.blits)

    def test_placed_at_the_bottom_still_leaves_the_rest_alone(self):
        self._start(y=30)
        self.assertEqual([], self.d.fills)
        self.assertEqual([(0, 30, 100, 30)], self.d.blits)

    def test_default_place_clears_the_panel_first(self):
        self._start()
        self.assertEqual([(0, 0, 100, 60)], self.d.fills)
        self.assertEqual([(0, 30, 100, 30)], self.d.blits)


class TestPlacedRectangle(unittest.TestCase):
    """A meter given ``x`` and ``width`` paints and presents only its own
    rectangle, so an app can put a small one beside its own widgets."""

    def setUp(self):
        self.analyzer = _load_analyzer(self)
        self.d = _Display()

    def test_start_paints_only_the_rectangle(self):
        meter = self.analyzer.Spectrum(self.d, _Source(), height=20, y=30, x=40, width=50)
        meter.start(_App())
        self.assertEqual([], self.d.fills)
        self.assertEqual([(40, 30, 50, 20)], self.d.blits)

    def test_columns_land_at_x(self):
        meter = self.analyzer.Spectrum(self.d, _Source(), height=20, y=30, x=40, width=50)
        meter._send = lambda buf, x, y, w, h: self.d.blits.append((x, y, w, h))
        meter._blit(b"", 3, 2, 4, 5)
        self.assertEqual([(43, 32, 4, 5)], self.d.blits)

    def test_width_defaults_to_the_rest_of_the_panel(self):
        meter = self.analyzer.Spectrum(self.d, _Source(), height=20, y=0, x=40)
        self.assertEqual(60, meter.view.width)


if __name__ == "__main__":
    unittest.main()
