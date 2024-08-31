print("This is a proof of concept for a GUI system for the author's use.")
print("It is not likely to be useful to anyone else.")
print("It is a work in progress and is not complete.")
print("Please do not report errors or request changes.")

############## file:  __init__.py
from graphics.palettes import get_palette

colors = get_palette()


class Styles(dict):
    def get(self, obj: object, part: int, state: int) -> int:
        return self[obj][part][state]


STYLES = Styles()


############## file:  states.py
from micropython import const  # noqa: E402


class states:
    DEFAULT = const(-1)
    OFF = const(0)
    ON = const(1)
    HIDDEN = const(2)
    DISABLED = const(4)


############## file:  parts.py
class parts:
    BG = const(0)
    FG = const(1)


############## file:  screen.py
from graphics import Area  # noqa: E402


class Screen:
    def __init__(self, display: object, styles: Styles = None):
        self._display = display
        self._styles = styles or STYLES
        self._state_changed = True
        self._children = set()

    @property
    def width(self) -> int:
        return self._display.width
    
    @property
    def height(self) -> int:
        return self._display.height
    
    def add_child(self, child: object):
        self._children.add(child)

    def remove_child(self, child: object):
        self._children.remove(child)

    def hit_test(self, x: int, y: int) -> bool:
        hit = False
        for child in self._children:
            if child.hit_test(x, y):
                hit = True
                child.click(x, y)
        return hit

    def render(self) -> Area:
        dirty_list = []
        if self._state_changed:
            if d := self._display.fill(self._styles.get(Screen, parts.BG, states.DEFAULT)):
                dirty_list.append(d)
            self._state_changed = False
        for child in self._children:
            if child.state_changed:
                if d := child.render(self._display):
                    dirty_list.append(d)
        return dirty_list
    
    def redraw(self, area: Area):
        dirty_list = [area]
        for child in self._children:
            if area.intersects(Area(child.x, child.y, child.width, child.height)):
                if d:= child.render(self._display):
                    dirty_list.append(d)
        for area in dirty_list:
            self.show(area)

    def show(self, dirty: object = None):
        if dirty:
            self._display.show(dirty)
        else:
            self._display.show()


STYLES[Screen] = {parts.BG: {states.DEFAULT: colors.WHITE}}


############## file:  icon_button.py
from pbm import PBM  # noqa: E402


class IconButton:
    def __init__(
        self,
        parent: Screen,
        image: PBM,
        x: int,
        y: int,
        state: int = states.OFF,
        styles: Styles = None,
    ):
        self._parent = parent
        self._x = x
        self._y = y
        self._state = state
        self._state_changed = True
        self._image = image
        self._width = self._image.width
        self._height = self._image.height
        self._parent.add_child(self)
        self._styles = styles or self._parent._styles

    @property
    def state_changed(self) -> bool:
        return self._state_changed

    @property
    def state(self) -> int:
        return self._state

    @state.setter
    def state(self, value: int):
        if value == self._state:
            return
        self._state = value
        self._state_changed = True
        return

    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    @property
    def x(self) -> int:
        return self._x
    
    @property
    def y(self) -> int:
        return self._y
    
    def render(self, display: object):
        self._state_changed = False
        self._image.fg = self._styles.get(IconButton, parts.FG, self._state)
        # display.blit(self._image, self._x, self._y, self._image.bg, self._image.palette)
        self._image.render(display, self._x, self._y, self._image.fg)
        return Area(self._x, self._y, self._width, self._height)

    def hit_test(self, x: int, y: int) -> bool:
        return (
            self._x <= x < self._x + self._width
            and self._y <= y < self._y + self._height
        )

    def click(self, x, y):
        if self._state == states.DISABLED or self._state == states.HIDDEN:
            return False
        self.state = states.ON if self.state == states.OFF else states.OFF
        return True

    def on(self, state=True):
        self.state = states.ON if state else states.OFF

    def disable(self, state=True):
        self.state = states.DISABLED if state else states.ON

    def hide(self, state=True):
        self.state = states.HIDDEN if state else states.OFF


STYLES[IconButton] = {
    parts.FG: {
        states.OFF: colors.RED,
        states.ON: colors.GREEN,
        states.HIDDEN: colors.BLUE,
        states.DISABLED: colors.YELLOW,
    }
}


############## file:  main.py
# from color_setup import ssd as display  # noqa: E402
from board_config import display_drv  as display  # noqa: E402
from board_config import broker  # noqa: E402
from eventsys.events import Events  # noqa: E402
try:
    from time import ticks_ms, ticks_diff  # noqa: E402
except ImportError:
    from adafruit_ticks import ticks_ms, ticks_diff

_image_path = "/home/brad/od/pbm/materialicons/"
settings = _image_path + "action-settings.pbm"
heart = _image_path + "action-favorite.pbm"
screen = Screen(display)
btn1 = IconButton(screen, p := PBM(settings, colors.BLACK, colors.WHITE), 0, screen.height - p.height)  # noqa: F841
btn2 = IconButton(screen, p := PBM(heart, colors.BLACK, colors.WHITE), screen.width - p.width, screen.height - p.height)  # noqa: F841

busy = False
# count = line = 0
def tick():
    global busy # , count, line
    if busy:
        return
    busy = True

    # screen.redraw(display.pixel(count, line, colors[count % 256]))
    # count += 1
    # if count >= display.width:
    #     count = 0
    #     line += 1
    #     if line >= display.height:
    #         line = 0

    if e := broker.poll():
        if e.type == Events.MOUSEBUTTONDOWN:
            screen.hit_test(*e.pos)
    if dirty_list := screen.render():
        for area in dirty_list:
            screen.show(area)
    busy = False

def main():
    state = False
    def toggle():
        nonlocal state
        state = not state
        return state

    heartbeact = 1000
    last = ticks_ms()
    print("Press Ctrl+C to exit")
    try:
        while True:
            tick()
            if ticks_diff(ticks_ms(), last) > heartbeact:
                last = ticks_ms()
                btn2.on(toggle())
    except KeyboardInterrupt:
        print("Exiting")

main()
