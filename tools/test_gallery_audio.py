#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Brad Barnett
# SPDX-License-Identifier: MIT
"""Prove the audio cards play on the direct-WebAssembly gallery.

A browser keeps Web Audio muted until the page has had a user gesture, so an
audio card has to load without a gesture, wait, and then start its sound once
the visitor touches the page. For each card this loads it in headless
Chromium, asserts it reaches ``runtimeState=ready`` with no traceback, clicks
the canvas the way a visitor would (a play button, a key, or just the page),
and then asserts that the host's Web Audio output received non-silent frames, with the audio device
starting a moment after the gesture, as a real one does.

The host exposes no sample counter, so the page is instrumented: an init
script wraps ``AudioBuffer.copyToChannel``, which the host calls once per
block it queues, and tallies the frames and the loudest sample.

    .venv/bin/python tools/test_gallery_audio.py                 # serves this checkout
    .venv/bin/python tools/test_gallery_audio.py piano           # one card
    .venv/bin/python tools/test_gallery_audio.py --base https://pydevices.github.io/pydevices-examples

Locally the gallery needs the wasm runtime, which the site serves from its own
root at ``/vendor/micropython/``; point ``--vendor`` at a checkout of that
folder (default: ``../PyDevices.github.io/vendor``). Needs ``playwright``.
"""

import argparse
import asyncio
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]

# name -> (query string, where to click on the canvas as (x, y) fractions,
# what the click is). The click is held for HOLD_MS so a key keeps sounding.
CARDS = {
    "audio_arpeggio": ("modules=audio_arpeggio", (0.5, 0.5), "the page"),
    "piano": ("modules=piano", (0.5, 0.75), "a key"),
    "drum_machine": ("manifests=drum_machine", (0.075, 0.07), "PLAY"),
    "audiolive_rack": ("modules=audiolive_rack&manifests=audiolive", (0.5, 0.5), "the page"),
}
HOLD_MS = 1200
SOUND_WAIT_MS = 10000
PEAK_FLOOR = 0.01  # full scale is 1.0; silence is exactly 0

RESUME_DELAY_MS = 400
INIT_SCRIPT = """
window.__audio = {writes: 0, frames: 0, peak: 0};
// A real audio device takes a moment to start, so the host's enableAudio()
// settles some time after the gesture that asked for it. Headless Chromium
// resumes at once, which hides the race a visitor hits on the first tap.
const resume = AudioContext.prototype.resume;
AudioContext.prototype.resume = async function () {
    await new Promise((done) => setTimeout(done, RESUME_DELAY_MS));
    return resume.apply(this, arguments);
};
const copyToChannel = AudioBuffer.prototype.copyToChannel;
AudioBuffer.prototype.copyToChannel = function (source, channel) {
    if (channel === 0) {
        const a = window.__audio;
        a.writes += 1;
        a.frames += source.length;
        for (let i = 0; i < source.length; i++) {
            const v = Math.abs(source[i]);
            if (v > a.peak) a.peak = v;
        }
    }
    return copyToChannel.apply(this, arguments);
};
"""


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve_checkout(vendor):
    """Serve this checkout's .site plus the runtime at the site root."""
    tmp = tempfile.TemporaryDirectory()
    site = Path(tmp.name)
    (site / "gallery").symlink_to(ROOT / ".site" / "gallery")
    (site / "pyscript").symlink_to(ROOT / ".site" / "pyscript")
    (site / "vendor").symlink_to(Path(vendor).resolve())
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(site)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return tmp, server, f"http://127.0.0.1:{server.server_port}"


async def load(page, url, attempts=3):
    """Open a card and wait for it to settle; retry a flapping network."""
    for attempt in range(attempts):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_function(
                "['ready', 'failed'].includes(document.body.dataset.runtimeState)",
                timeout=120000,
            )
            return
        except Exception as error:  # net::ERR_NETWORK_CHANGED and friends
            if attempt == attempts - 1:
                raise
            print(f"  load retry after: {str(error).splitlines()[0]}")


async def check_card(browser, base, name):
    query, (fx, fy), what = CARDS[name]
    page = await browser.new_page(viewport={"width": 1000, "height": 900})
    await page.add_init_script(INIT_SCRIPT.replace("RESUME_DELAY_MS", str(RESUME_DELAY_MS)))
    problems = []
    try:
        await load(page, f"{base}/gallery/micropython.html?{query}")
        await page.wait_for_timeout(1500)
        state = await page.evaluate("document.body.dataset.runtimeState")
        log = await page.inner_text("#log")
        if state != "ready":
            problems.append(f"runtimeState={state}")
        if "Traceback" in log:
            problems.append("traceback in the console log")
        before = await page.evaluate("window.__audio")

        box = await (await page.query_selector("#display_canvas")).bounding_box()
        x, y = box["x"] + box["width"] * fx, box["y"] + box["height"] * fy
        await page.mouse.move(x, y)
        await page.mouse.down()
        loop = asyncio.get_running_loop()
        deadline = loop.time() + SOUND_WAIT_MS / 1000
        held_until = loop.time() + HOLD_MS / 1000
        released = False
        after = before
        while loop.time() < deadline:
            await page.wait_for_timeout(200)
            if not released and loop.time() >= held_until:
                await page.mouse.up()
                released = True
            after = await page.evaluate("window.__audio")
            if after["peak"] > PEAK_FLOOR and after["frames"] > 4800:
                break
        if not released:
            await page.mouse.up()
        if after["peak"] <= PEAK_FLOOR or after["frames"] <= 4800:
            problems.append("no sound reached Web Audio after the click")
        late = await page.inner_text("#log")
        if "Traceback" in late and "Traceback" not in log:
            problems.append("traceback after the click")
        print(
            f"{name:15} state={state:6} before: frames={before['frames']} "
            f"after click on {what}: writes={after['writes']} frames={after['frames']} "
            f"peak={after['peak']:.3f}  {'FAIL: ' + '; '.join(problems) if problems else 'ok'}"
        )
    finally:
        await page.close()
    return not problems


async def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("cards", nargs="*", help="card names (default: all)")
    parser.add_argument("--base", help="test this site instead of serving the checkout")
    parser.add_argument(
        "--vendor",
        default=str(ROOT.parent / "PyDevices.github.io" / "vendor"),
        help="folder holding micropython/micropython.mjs (local serving only)",
    )
    args = parser.parse_args()
    names = args.cards or list(CARDS)
    unknown = [n for n in names if n not in CARDS]
    if unknown:
        parser.error(f"unknown card {unknown}; choose from {', '.join(CARDS)}")

    from playwright.async_api import async_playwright

    tmp = server = None
    base = args.base
    if base is None:
        tmp, server, base = serve_checkout(args.vendor)
    ok = True
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            for name in names:  # one at a time: each card boots a 16 MB heap
                ok = await check_card(browser, base.rstrip("/"), name) and ok
            await browser.close()
    finally:
        if server:
            server.shutdown()
            tmp.cleanup()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
