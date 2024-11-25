"""
Board configuration for PyScript.
"""

from displaysys.psdisplay import PSDisplay, PSDevices
from eventsys import device

width = 320
height = 480

display_drv = PSDisplay("display_canvas", width, height)

broker = device.Broker()

touch_drv = PSDevices("display_canvas")

touch_dev = broker.create_device(
    type=device.Types.TOUCH,
    read=touch_drv.get_mouse_pos,
    data=display_drv,
)

display_drv.fill(0)
