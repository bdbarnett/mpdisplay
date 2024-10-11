from micropython import const

class STATE:
    DEFAULT = const(0)
    CHECKED = const(0b1)
    FOCUSED = const(0b10)
    FOCUS_KEY = const(0b100)
    EDITED = const(0b1000)
    HOVERED = const(0b10000)
    PRESSED = const(0b100000)
    SCROLLED = const(0b1000000)
    DISABLED = const(0b10000000)

class EVENT:
    ALL = const(0)
    PRESSED = const(0b1)
    PRESSING = const(0b10)
    PRESS_LOST = const(0b100)
    SHORT_CLICKED = const(0b1000)
    LONG_PRESSED = const(0b10000)
    LONG_PRESSED_REPEAT = const(0b100000)
    CLICKED = const(0b1000000)
    RELEASED = const(0b10000000)
    DELETE = const(0b100000000)
    SIZE_CHANGED = const(0b1000000000)
    REFRESH = const(0b10000000000)



class FLAG:
    HIDDEN = const(0b1)
    CLICKABLE = const(0b10)
    CLICK_FOCUSABLE = const(0b100)
    CHECKABLE = const(0b1000)
    SCROLLABLE = const(0b10000)
    SCROLL_ELASTIC = const(0b100000)
    SCROLL_MOMENTUM = const(0b1000000)
    SCROLL_ONE = const(0b10000000)
