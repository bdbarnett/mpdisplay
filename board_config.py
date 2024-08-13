"""
Combination board configuration for desktop, pyscript and jupyter notebook platforms.
"""
_ps = _jn = False

try:
    import pyscript  # type: ignore # noqa: F401
    _ps = True
except ImportError:
    try:
        get_ipython()  # type: ignore # noqa: F821
        _jn = True
    except NameError:
        pass

width = 320
height = 240

if _ps:
    from mpdisplay.psdisplay import PSDisplay
    from mpdisplay.psdisplay.psdevices import PSDevices
    from eventsys.devices import Devices, Broker # type: ignore


    display_drv = PSDisplay("display_canvas", width, height)

    display_drv.broker = Broker()

    touch_drv = PSDevices("display_canvas")

    touch_dev = display_drv.broker.create_device(
        type=Devices.TOUCH,
        read=touch_drv.get_mouse_pos,
        data=None,
    )
elif _jn:
    from mpdisplay.jndisplay import JNDisplay

    display_drv = JNDisplay(width, height)

    import showtimer  # noqa: F401
else:
    from mpdisplay.dtdisplay import DTDisplay, poll # type: ignore
    from eventsys.devices import Devices, Broker # type: ignore
    import sys


    display_drv = DTDisplay(
        width=width,
        height=height,
        rotation=0,
        color_depth=16,
        title=f"{sys.implementation.name} on {sys.platform}",
        scale=1.0,
    )

    display_drv.broker = Broker()

    events_dev = display_drv.broker.create_device(
        type=Devices.QUEUE,
        read=poll,
        # data=Events.filter,
    )

try:
    import mpdisplay_logo  # noqa: F401
except Exception:
    pass