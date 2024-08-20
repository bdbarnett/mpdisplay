"""
Board configuration for Jupyter Notebook.

"""
from jndisplay import JNDisplay
from show_timer import show_timer


display_drv = JNDisplay(320, 240)
tim = show_timer(display_drv)
