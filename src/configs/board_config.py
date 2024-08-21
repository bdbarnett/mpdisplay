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

width = 480
height = 320

if _ps:
    from psdisplay import PSDisplay
    from psdisplay.psdevices import PSDevices
    from eventsys.devices import Devices, Broker # type: ignore


    display_drv = PSDisplay("display_canvas", width, height)

    broker = Broker()

    touch_drv = PSDevices("display_canvas")

    touch_dev = broker.create_device(
        type=Devices.TOUCH,
        read=touch_drv.get_mouse_pos,
        data=None,
    )
elif _jn:
    from jndisplay import JNDisplay
    from timer import refresh_timer

    display_drv = JNDisplay(width, height)
    tim = refresh_timer(display_drv.show)
else:
    from dtdisplay import DTDisplay, poll # type: ignore
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

    broker = Broker()

    events_dev = broker.create_device(
        type=Devices.QUEUE,
        read=poll,
        # data=Events.filter,
    )

try:
    from splash import splash
    splash(display_drv)
except Exception:
    pass
