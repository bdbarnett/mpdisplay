from board_config import display_drv
from eventsys.events import Events


while True:
    e = display_drv.broker.poll()
    if e:
        print(e)
        if e == Events.QUIT:
            break
