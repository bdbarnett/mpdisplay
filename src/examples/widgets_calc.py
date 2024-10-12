
import board_config
import widgets as w


numbers = "0123456789"
operands = "+-*/"
button_labels = [["CE", "C", "BS", "/"],
                 ["7", "8", "9", "*"],
                 ["4", "5", "6", "-"],
                 ["1", "2", "3", "+"],
                 ["+/-", "0", ".", "="]]

w.init_timer(10)  # Remove this line to use polled mode in a while loop

display = w.Display(board_config.display_drv, board_config.broker)
theme = display.theme
screen = w.Screen(display, visible=True)
top_box = w.Widget(screen, h=70, bg=theme.secondary)
readout = w.Widget(top_box, fg=theme.on_background, bg=theme.background, w=top_box.width-10, h=top_box.height-10, align=w.ALIGN.CENTER)
formula = w.TextBox(readout, align=w.ALIGN.TOP, scale=1)
entry = w.TextBox(readout, align=w.ALIGN.BOTTOM, scale=2)
button_box = w.Widget(screen, h=display.height-top_box.height, align=w.ALIGN.BOTTOM)

cols, rows = 4, 5
buttons = [[w.Button(button_box, label=button_labels[j][i], value=button_labels[j][i], radius=4,
    x=w.pct.Width(i*100/cols, button_box), y=w.pct.Height(j*100/rows, button_box),
    w=w.pct.Width(100/cols, button_box), h=w.pct.Height(100/rows, button_box),
    ) for i in range(cols)] for j in range(rows)]

def clear_everything():
    global showing_result
    entry.value = ""
    formula.value = ""
    showing_result = False

showing_result = False
def pressed(key):
    global showing_result
    if key in numbers:
        if showing_result:
            clear_everything()
        entry.value += key
    elif key == ".":
        if not showing_result and entry.value.find(".") == -1:
            entry.value += "."
    elif key == "BS":
        if not showing_result:
            entry.value = entry.value[:-1]
    elif key == "+/-":
        if entry.value[0] == "-":
            entry.value = entry.value[1:]
        else:
            entry.value = "-" + entry.value
    elif key == "C":
        if showing_result:
            clear_everything()
        else:
            entry.value = ""
    elif key == "CE":
        clear_everything()
    elif key in operands:
        if entry.value == "":
            if formula.value == "":
                return
            if formula.value[-1] in operands:
                formula.value = formula.value[:-1] + key
                return
            formula.value += key
            return
        if showing_result:
            formula.value = entry.value + key
        else:
            formula.value += entry.value + key
        entry.value = ""
        showing_result = False
    elif key == "=":
        if not showing_result:
            if entry.value == "":
                if formula.value[-1] in operands:
                    formula.value = formula.value[:-1]
            else:
                formula.value += entry.value
            try:
                result = eval(formula.value)
                entry.value = str(result)
                formula.value += "=" + entry.value
            except Exception:
                entry.value = "Error"
            showing_result = True
    else:
        print(f"Unknown key: {key}")

for row in buttons:
    for button in row:
        button.set_on_press(lambda sender: pressed(sender.value))

if not display.timer:
    print("Starting main loop")
    running = True
    while running:
        w.tick()
