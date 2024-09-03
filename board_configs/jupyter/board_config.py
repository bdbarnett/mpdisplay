"""
Board configuration for Jupyter Notebook.

"""
from pyd_jndisplay import JNDisplay
from pyd_timer import refresh_timer


display_drv = JNDisplay(480, 320)
tim = refresh_timer(display_drv.show)
