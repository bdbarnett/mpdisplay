"""Wi-Fi: on only while this app is open, so mpftp and Workbench can reach the
watch over WebREPL.

Opening it joins a known network (the one in ``secrets.py``, or one
``wifi_manager`` remembered) and starts WebREPL, whose password is the one in
``/webrepl_cfg.py``. Leaving it turns WebREPL and the radio off. With no known
network in range, "Set up" asks for one from a phone. While the app is open
the screen still goes dark, but the watch doesn't doze: that would drop the
link.

Needs ``wifi_manager``, which is part of the pydevices package::

    mip.install("pydevices", index="https://PyDevices.github.io/mip")
"""

import lvgl as lv
import micropython

from . import services as sv
from . import ui

HOSTNAME = "twatch"  # mpftp finds it as twatch.local


def main(scope):
    scr = ui.screen(scope, "Wi-Fi")
    lbl = ui.label(scr, "", sv.small)
    hint = ui.label(scr, "", sv.small, sv.MUTED)
    for t in (lbl, hint):
        t.set_width(lv.pct(90))
        t.set_long_mode(lv.label.LONG_MODE.WRAP)
    try:
        import wifi_manager
    except ImportError:
        ui.missing(scr, "wifi_manager")
        sv.use(scope)
        return
    import network
    import webrepl

    sta = network.WLAN(network.STA_IF)
    state = {"open": True, "busy": False}

    def off():
        try:
            webrepl.stop()
        except Exception:
            pass
        sta.active(False)
        sv.event("Wi-Fi off")

    def show(ip):
        if ip:
            lbl.set_text("%s.local\n%s" % (HOSTNAME, ip))
            hint.set_text("WebREPL is on. Leave this app to turn Wi-Fi off.")
        else:
            lbl.set_text("No known network")
            hint.set_text("Tap Set up, then follow the steps with a phone.")

    def job(setup):
        # Runs from micropython.schedule, outside every timer callback, so
        # wifi_manager's waits keep the screen and the crown going.
        def run(_):
            if not state["open"]:
                return
            state["busy"] = True
            ip = None
            try:
                if setup:
                    ip = wifi_manager.run(hostname=HOSTNAME)
                else:
                    ip = wifi_manager.connect(setup=False, hostname=HOSTNAME)
                if ip:
                    webrepl.start()
            except Exception as e:
                print("wifi app:", e)
            state["busy"] = False
            if not state["open"]:
                off()
                return
            sv.event("Wi-Fi " + (ip or "no network"))
            show(ip)

        return run

    def start(setup=False):
        if state["busy"]:
            return
        lbl.set_text("Setting up..." if setup else "Joining...")
        hint.set_text("")
        micropython.schedule(job(setup), None)

    def close():
        state["open"] = False
        sv.stay_awake = False
        if state["busy"]:
            wifi_manager.cancel()  # setup mode ends; the job turns the radio off
        else:
            off()

    r = ui.row(scr)
    ui.button(r, "Set up", lambda: start(True))
    sv.stay_awake = True
    scope.on_close(close)
    start()
    sv.use(scope)
