from board_config import display_drv
from keypins import KeyPins, Keys, Events


buttons = KeyPins(
    left=Keys.K_LEFT,
    right=Keys.K_RIGHT,
    go=Keys.K_UP,
    stop=Keys.K_DOWN,
    fire=Keys.K_SPACE,
)

print("\nDetails of the buttons (KeyPins) object:")
print(f"\n{buttons=}")
print(f"\n{str(buttons)=}")
print(f"\n{dir(buttons)=}\n")

print("\nFour ways to read the value: ")
print(f"{buttons.fire.value()=}")
print(f"{buttons.fire()=}")
print(f"{buttons['fire'].value()=}")
print(f"{buttons['fire']()=}\n")

print("\nOther attributes:")
print(f"{buttons.fire.name=}")
print(f"{buttons.fire.key=}")
print(f"{buttons.fire.keyname=}\n")

# Subscribe the to the display driver so _KeyPin states are updated
# on KEYDOWN and KEYUP events when display_drv.poll() is called.
display_drv.subscribe(buttons, event_types=[Events.KEYDOWN, Events.KEYUP])

print(f"Press any of these keys:  {[button.keyname for button in buttons]}")
while True:
    # Call display_drv.poll() frequently.  We don't need the return
    # value because the information we need is in the buttons object.
    _ = display_drv.poll()
    for button in buttons:
        if button.value() == True:
            print(f"{button.name} ({button.keyname}) pressed")
