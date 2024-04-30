from board_config import display_drv
from mpdisplay import Events


while True:
    e = display_drv.poll_event()
    if e:
        print(e)
        if e == Events.QUIT:
            break