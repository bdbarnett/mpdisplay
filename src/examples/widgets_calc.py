
import board_config
import widgets as w


w.DEBUG = False
w.MARK_UPDATES = False
w.init_timer(10)  # Remove this line to use polled mode in a while loop

def pressed(button):
    print("Pressed", button.value)
    readout.value = button.value

display = w.Display(board_config.display_drv, board_config.broker, 80, 0)
screen = w.Screen(display, visible=False)

top, bottom, main = screen.top, screen.bottom, screen.main

readout = w.TextBox(top, w=w.pct.Width(100, top), h=w.pct.Height(100, top), scale=2, value="Status: loaded.")

button_labels = [["CE", "C", "BS", "/"],
                 ["7", "8", "9", "X"],
                 ["4", "5", "6", "-"],
                 ["1", "2", "3", "+"],
                 ["+/-", "0", ".", "="]]
cols=4
rows=5
buttons = [[w.Button(
    main,
    label=button_labels[j][i],
    value=button_labels[j][i],
    x=w.pct.Width(i*100/cols, main),
    y=w.pct.Height(j*100/rows, main),
    w=w.pct.Width(100/cols, main),
    h=w.pct.Height(100/rows, main),
    radius=4,
    ) for i in range(cols)] for j in range(rows)]

# Call ".set_on_press(pressed)" for each button
for row in buttons:
    for button in row:
        button.set_on_press(pressed)

screen.visible = True


if not display.timer:
    print("Starting main loop")
    running = True
    while running:
        w.tick()
