from micropython import const


class _CONSTANTS:
    """
    A base class for creating a struct-like class.  The class may be used to check if a value is one of the built-in values, for instance:
    ```
    CONSTANTS = _CONSTANTS()
    if value in CONSTANTS:
        print("Value is valid")
    ```
    May also be used to iterate over the values:
    ```
    CONSTANTS = _CONSTANTS()
    for value in CONSTANTS:
        print(value)
    ```
    """
    
    @classmethod
    def __contains__(cls, item):
        return item in cls.__dict__.values()
    
    @classmethod
    def __iter__(cls):
        return iter(cls.__dict__.values())


class _ICON_SIZE(_CONSTANTS):
    SMALL = const(18)
    MEDIUM = const(24)
    LARGE = const(36)
    XLARGE = const(48)

ICON_SIZE = _ICON_SIZE()

class _TEXT_SIZE(_CONSTANTS):
    SMALL = const(8)
    MEDIUM = const(14)
    LARGE = const(16)

TEXT_SIZE = _TEXT_SIZE()

class _POSITION(_CONSTANTS):
    LEFT = const(1 << 0)
    RIGHT = const(1 << 1)
    TOP = const(1 << 2)
    BOTTOM = const(1 << 3)
    OUTER = const(1 << 4)

POSITION = _POSITION()


class _ALIGN(_CONSTANTS):
    CENTER = const(0)  # 0
    TOP_LEFT = const(POSITION.TOP | POSITION.LEFT)  # 5
    TOP = const(POSITION.TOP)  # 4
    TOP_RIGHT = const(POSITION.TOP | POSITION.RIGHT)  # 6
    LEFT = const(POSITION.LEFT)  # 1
    RIGHT = const(POSITION.RIGHT)  # 2
    BOTTOM_LEFT = const(POSITION.BOTTOM | POSITION.LEFT)  # 9
    BOTTOM = const(POSITION.BOTTOM)  # 8
    BOTTOM_RIGHT = const(POSITION.BOTTOM | POSITION.RIGHT)  # 10
    OUTER_TOP_LEFT = const(POSITION.TOP | POSITION.LEFT | POSITION.OUTER)  # 21
    OUTER_TOP = const(POSITION.TOP | POSITION.OUTER)  # 20
    OUTER_TOP_RIGHT = const(POSITION.TOP | POSITION.RIGHT | POSITION.OUTER)  # 22
    OUTER_LEFT = const(POSITION.LEFT | POSITION.OUTER)  # 17
    OUTER_RIGHT = const(POSITION.RIGHT | POSITION.OUTER)  # 18
    OUTER_BOTTOM_LEFT = const(POSITION.BOTTOM | POSITION.LEFT | POSITION.OUTER)  # 25
    OUTER_BOTTOM = const(POSITION.BOTTOM | POSITION.OUTER)  # 24
    OUTER_BOTTOM_RIGHT = const(POSITION.BOTTOM | POSITION.RIGHT | POSITION.OUTER)  # 26

ALIGN = _ALIGN()



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
