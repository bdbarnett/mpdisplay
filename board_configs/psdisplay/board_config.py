"""
Combination board configuration for desktop, pyscript and jupyter notebook platforms.
"""

width = 320
height = 480
rotation = 0
scale = 2.0

_ps = _jn = False
try:
    import pyscript

    _ps = True
except ImportError:
    try:
        get_ipython()
        _jn = True
    except NameError:
        pass

if _ps:
    from displaysys.psdisplay import PSDisplay, PSDevices
    from eventsys import device

    display_drv = PSDisplay("display_canvas", width, height)

    broker = device.Broker()

    touch_drv = PSDevices("display_canvas")

    touch_dev = broker.create_device(
        type=device.Types.TOUCH,
        read=touch_drv.get_mouse_pos,
        data=display_drv,
    )
elif _jn:
    from displaysys.jndisplay import JNDisplay
    from eventsys import device

    broker = device.Broker()

    display_drv = JNDisplay(width, height)
else:
    from eventsys import device
    import sys
    try:
        from displaysys.pgdisplay import PGDisplay as DTDisplay, poll
    except ImportError:
        from displaysys.sdldisplay import SDLDisplay as DTDisplay, poll


    display_drv = DTDisplay(
        width=width,
        height=height,
        rotation=rotation,
        color_depth=16,
        title=f"{sys.implementation.name} on {sys.platform}",
        scale=scale,
    )

    broker = device.Broker()

    events_dev = broker.create_device(
        type=device.Types.QUEUE,
        read=poll,
        data=display_drv,
        # data2=Events.filter,
    )

display_drv.fill(0)
