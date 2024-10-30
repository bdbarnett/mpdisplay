""" board_config.py - board configuration for PyScript """

from psdisplay import PSDisplay, PSDevices
from pydevices.devices import DeviceTypes, Broker # type: ignore


display_drv = PSDisplay("display_canvas", 480, 320)

broker = Broker()

touch_drv = PSDevices("display_canvas")

touch_dev = broker.create_device(
    type=DeviceTypes.TOUCH,
    read=touch_drv.get_mouse_pos,
    data=display_drv,
)
