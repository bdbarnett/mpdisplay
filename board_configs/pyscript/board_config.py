""" board_config.py - board configuration for PyScript """

from psdisplay import PSDisplay
from psdisplay.psdevices import PSDevices
from eventsys.devices import Devices, Broker # type: ignore


display_drv = PSDisplay("display_canvas", 320, 240)

broker = Broker()

touch_drv = PSDevices("display_canvas")

touch_dev = broker.create_device(
    type=Devices.TOUCH,
    read=touch_drv.get_mouse_pos,
    data=None,
)

display_drv.fill(0xF000)
