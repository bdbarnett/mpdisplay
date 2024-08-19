from timer import Timer
from sys import platform

def show_timer(object=None, period=33):
    """
    Creates and returns a timer to periodically call the .show() method on an object
    """

    if object is None:
        from board_config import display_drv as object
    tim = Timer(-1 if platform == "rp2" else 1)
    tim.init(mode = Timer.PERIODIC, period=period, callback=lambda t: object.show())
    return tim
