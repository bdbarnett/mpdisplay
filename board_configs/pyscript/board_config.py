"""board_config.py - board configuration for PyScript"""

from psdisplay import PSDisplay, PSDevices
import eventsys.device as device


display_drv = PSDisplay("display_canvas", 480, 320)

broker = device.Broker()

touch_drv = PSDevices("display_canvas")

touch_dev = broker.create_device(
    type=device.Types.TOUCH,
    read=touch_drv.get_mouse_pos,
    data=display_drv,
)
