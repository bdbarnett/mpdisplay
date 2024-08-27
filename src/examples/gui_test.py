from color_setup import ssd
from pbm import PBM
from graphics.palettes import get_palette
from micropython import const
from board_config import broker
from eventsys.events import Events
from graphics import Area


_image_path = "/home/brad/od/pbm/materialicons/"

OFF = const(0)
ON = const(1)
HIDDEN = const(2)
DISABLED = const(4)


p = get_palette()
BACKGROUND = p.BLUE
colors = {
    OFF: p.GREY,
    ON: p.GREEN,
    HIDDEN: BACKGROUND,
    DISABLED: p.YELLOW,
}


class Screen:
    def __init__(self, display: object, color: int = 0):
        self._display = display
        self._color = color
        self._state_changed = True
        self._children = set()

    def add_child(self, child: object):
        self._children.add(child)

    def remove_child(self, child: object):
        self._children.remove(child)

    def hit_test(self, x: int, y: int) -> object:
        something_touched = False
        for child in self._children:
            if child.hit_test(x, y):
                something_touched = True
                child.click()
        return something_touched

    def render(self):
        dirty = None
        if self._state_changed:
            dirty = self._display.fill(self._color)
            self._state_changed = False
        for child in self._children:
            if child.state_changed:
                if d := child.render(self._display):
                    if dirty:
                        dirty += d
                    else:
                        dirty = d
        return dirty
    
    def show(self, dirty: object = None):
        if dirty:
            self._display.show(dirty)
        else:
            self._display.show()


class IconButton:
    def __init__(self, parent: object, file: str, x: int, y: int, state: int = OFF):
        self._parent = parent
        self._file = file
        self._x = x
        self._y = y
        self._state = state
        self._state_changed = True
        self._image = PBM(file)
        self._width = self._image.width
        self._height = self._image.height
        self._parent.add_child(self)

    def hit_test(self, x: int, y: int) -> bool:
        return self._x <= x < self._x + self._width and self._y <= y < self._y + self._height
    
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
    def state_changed(self) -> bool:
        return self._state_changed
    
    def disable(self):
        self.state = DISABLED

    def enable(self):
        self.state = OFF

    def hide(self):
        self.state = HIDDEN

    def unhide(self):
        self.state = OFF

    def click(self):
        if self._state == DISABLED or self._state == HIDDEN:
            return False
        self.state = ON if self.state == OFF else OFF
        return True

    def render(self, display: object):
        if not self._state_changed:
            return None
        self._state_changed = False
        self._image.render(display, self._x, self._y, colors[self._state])
        return Area(self._x, self._y, self._width, self._height)


SETTINGS = _image_path + "action-settings.pbm"

def main():
    screen = Screen(ssd, BACKGROUND)

    btn1 = IconButton(screen, SETTINGS, 108, 108)  # noqa: F841

    while True:
        dirty = screen.render()
        if dirty:
            screen.show(dirty)
        if e := broker.poll():
            if e.type == Events.MOUSEBUTTONDOWN:
                screen.hit_test(*e.pos)

main()
