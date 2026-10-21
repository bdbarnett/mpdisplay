# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""The Roku, HLS and Miracast displays register with PyDevices' backend registry.

A config that ``require``s one gets it from ``AutoDisplay``. Without the
registry (PyDevices before 0.7.7) the modules still import and the displays
still work as they did. Nothing here touches a TV: the Roku display is built
against a loopback address and the encoders are replaced with fakes.
"""

import os
from pathlib import Path
import runpy
import sys
import types
import unittest
from unittest import mock

import _env  # noqa: F401

_LIB = Path(__file__).resolve().parent.parent / "lib"
for _p in (_LIB, _LIB / "examples" / "cast", _LIB / "examples" / "roku_hls"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

try:
    import backends
except ImportError:  # PyDevices before 0.7.7
    backends = None


class _Fake:
    """Stands in for an encoder: takes any arguments and does nothing."""

    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        return lambda *a, **k: {}


def _import_displays():
    """Import the three displays, with a stand-in ``framebuf`` where CPython has none."""
    stub = None
    try:
        import framebuf  # noqa: F401
    except ImportError:
        stub = types.ModuleType("framebuf")
        stub.RGB565 = 1
        stub.FrameBuffer = _Fake
        sys.modules["framebuf"] = stub
    try:
        import cast_display
        import hls_display
        from utils import roku_companion
    finally:
        if stub is not None:
            sys.modules.pop("framebuf", None)
    return cast_display, hls_display, roku_companion


if backends is not None:
    from displaydev.auto import AutoDisplay

    cast_display, hls_display, roku_companion = _import_displays()


@unittest.skipIf(backends is None, "needs PyDevices with the backend registry (0.7.7)")
class TestCastBackends(unittest.TestCase):
    def setUp(self):
        self._required = {k: list(v) for k, v in backends._required.items()}
        self._env = os.environ.get("PYDEVICES_DISPLAY")
        os.environ.pop("PYDEVICES_DISPLAY", None)
        self.addCleanup(self._restore)

    def _restore(self):
        backends._required.clear()
        backends._required.update(self._required)
        if self._env is not None:
            os.environ["PYDEVICES_DISPLAY"] = self._env

    def test_each_display_is_registered_where_its_class_lives(self):
        self.assertEqual(backends.spec("display", "roku"), "utils.roku_companion:RokuDisplay")
        self.assertEqual(backends.spec("display", "hls"), "hls_display:HlsDisplay")
        self.assertEqual(backends.spec("display", "cast"), "cast_display:CastDisplay")
        for name in ("roku", "hls", "cast"):
            self.assertIn(name, backends.names("display"))

    def test_none_of_them_is_picked_unless_asked_for(self):
        order = [name for name, _spec, _builtin in backends.candidates("display")]
        for name in ("roku", "hls", "cast"):
            self.assertNotIn(name, order)

    def test_roku_comes_from_auto_display_once_required(self):
        backends.require("display", "roku", module="utils.roku_companion")
        display = AutoDisplay(240, 135, tv="127.0.0.1")
        self.assertIsInstance(display, roku_companion.RokuDisplay)
        self.assertEqual((display.width, display.height), (240, 135))
        self.assertEqual(display.tv.host, "127.0.0.1")

    def test_hls_comes_from_auto_display_once_required(self):
        backends.require("display", "hls", module="hls_display")
        with mock.patch("shutil.which", return_value="/usr/bin/ffmpeg"), mock.patch.object(
            hls_display, "_FfmpegHls", _Fake
        ), mock.patch.object(hls_display.HlsDisplay, "_local_ip", return_value="127.0.0.1"):
            display = AutoDisplay(64, 64, tv=None, log=lambda *a: None)
        self.assertIsInstance(display, hls_display.HlsDisplay)
        self.assertEqual((display.width, display.height), (64, 64))

    def test_hls_is_skipped_where_there_is_no_encoder(self):
        backends.require("display", "hls", module="hls_display")
        with mock.patch.object(hls_display, "castif", None), mock.patch(
            "shutil.which", return_value=None
        ), mock.patch.dict(os.environ, {"FFMPEG": ""}):
            names = [name for name, _spec, _builtin in backends.candidates("display")]
        self.assertNotIn("hls", names)

    def test_cast_comes_from_auto_display_once_required(self):
        backends.require("display", "cast", module="cast_display")
        with mock.patch("shutil.which", return_value="/usr/bin/ffmpeg"), mock.patch.object(
            cast_display, "pycast", mock.Mock(FfmpegCaster=_Fake)
        ), mock.patch.object(cast_display, "castfast", None), mock.patch.object(
            cast_display.CastDisplay, "_start", lambda self: None
        ):
            display = AutoDisplay(64, 64, sink="127.0.0.1", kind="roku")
        self.assertIsInstance(display, cast_display.CastDisplay)
        self.assertEqual(display.sink, "127.0.0.1")

    def test_the_environment_can_name_one_without_a_config(self):
        os.environ["PYDEVICES_DISPLAY"] = "roku"
        display = AutoDisplay(240, 135, tv="127.0.0.1")
        self.assertIsInstance(display, roku_companion.RokuDisplay)

    def test_roku_config_requires_the_roku_display(self):
        saved = audiodev_pcm_out()
        argv = sys.argv
        sys.argv = ["board_config.py", "127.0.0.1"]
        try:
            ns = runpy.run_path(str(_LIB / "examples" / "roku" / "board_config.py"))
        finally:
            sys.argv = argv
            restore_pcm_out(saved)
        self.assertIsInstance(ns["display_drv"], roku_companion.RokuDisplay)
        self.assertIn("roku", backends._required["display"])


def audiodev_pcm_out():
    import audiodev.auto

    return audiodev.auto.pcm_out


def restore_pcm_out(fn):
    import audiodev.auto

    audiodev.auto.pcm_out = fn


class TestWithoutTheRegistry(unittest.TestCase):
    """PyDevices before 0.7.7 has no ``backends`` module: nothing may break."""

    def test_the_modules_import_and_the_roku_config_runs(self):
        names = ("utils.roku_companion", "cast_display", "hls_display")
        saved = {n: sys.modules.pop(n, None) for n in names}
        had = sys.modules.get("backends", False)
        sys.modules["backends"] = None  # an import of it now raises ImportError
        saved_pcm = None
        argv = sys.argv
        try:
            _import_displays()
            saved_pcm = audiodev_pcm_out()
            sys.argv = ["board_config.py", "127.0.0.1"]
            ns = runpy.run_path(str(_LIB / "examples" / "roku" / "board_config.py"))
            self.assertEqual(type(ns["display_drv"]).__name__, "RokuDisplay")
        finally:
            sys.argv = argv
            if saved_pcm is not None:
                restore_pcm_out(saved_pcm)
            if had is False:
                sys.modules.pop("backends", None)
            else:
                sys.modules["backends"] = had
            for n in names:
                sys.modules.pop(n, None)
                if saved[n] is not None:
                    sys.modules[n] = saved[n]


if __name__ == "__main__":
    unittest.main()
