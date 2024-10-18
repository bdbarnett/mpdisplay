import board_config
import pywidgets as pw


pw.DEBUG = False
pw.MARK_UPDATES = False
pw.init_timer(10)  # Remove this line to use polled mode in a while loop


display = pw.Display(board_config.display_drv, board_config.broker, 40, 40)
screen = pw.Screen(display, visible=False)

if screen.partitioned:
    top, bottom, main = screen.top, screen.bottom, screen.main
else:
    top = bottom = main = screen

s_left = pw.ScrollBar(main, value=0.5, vertical=True, align=pw.ALIGN.LEFT, reverse=True)
s_right = pw.ScrollBar(main, value=0.5, vertical=True, align=pw.ALIGN.RIGHT)
s_top = pw.ScrollBar(top, value=0.5, align=pw.ALIGN.BOTTOM, reverse=True)
s_bottom = pw.ScrollBar(bottom, value=0.5, align=pw.ALIGN.TOP)



screen.visible = True

if not display.timer:
    print("Starting main loop")
    running = True
    while running:
        pw.tick()
