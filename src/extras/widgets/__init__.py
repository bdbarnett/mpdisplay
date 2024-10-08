from gfx import Area
from eventsys.events import Events
from micropython import const
import png
from time import localtime
from gfx.framebuf_plus import FrameBuffer, RGB565
from palettes import get_palette
import sys
from random import getrandbits
from . import pct  # noqa: F401
# from palettes.shades import ShadesPalette
try:
    from time import ticks_ms, ticks_add
except ImportError:
    from adafruit_ticks import ticks_ms, ticks_add
try:
    from os import sep  # PyScipt doesn't have os.sep
except ImportError:
    sep = "/"

# get the path this module is in
ICONS = __file__.split(sep)[0:-1]
ICONS = sep.join(ICONS) + sep + "icons" + sep


DEBUG = False
MARK_UPDATES = False


def log(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def name(obj):
    return obj.__class__.__name__

def drawing(obj):
    return f"{name(obj)} drawing at {obj.area}"

def tick(_=None):
    for display in Display.displays:
        display.tick()

def init_timer(period=10):
    if Display.timer is None:
        from timer import get_timer
        Display.timer = get_timer(tick, period)

_display_drv_get_attrs = {"set_vscroll", "tfa", "bfa", "vsa", "vscroll", "tfa_area", "bfa_area", "vsa_area", "scroll_by", "scroll_to", "translate_point"}
_display_drv_set_attrs = {"vscroll"}

DEFAULT_ICON_SIZE = const(36)
DEFAULT_TEXT_HEIGHT = const(16)
TEXT_WIDTH = const(8)
TEXT_HEIGHTS = (8, 14, 16)

_LEFT = const(1 << 0)
_RIGHT = const(1 << 1)
_TOP = const(1 << 2)
_BOT = const(1 << 3)
_OUTER = const(1 << 4)


log(f"{__name__} module loaded.")


class ALIGN:
    CENTER = const(0)  # 0
    TOP_LEFT = const(_TOP | _LEFT)  # 5
    TOP = const(_TOP)  # 4
    TOP_RIGHT = const(_TOP | _RIGHT)  # 6
    LEFT = const(_LEFT)  # 1
    RIGHT = const(_RIGHT)  # 2
    BOTTOM_LEFT = const(_BOT | _LEFT)  # 9
    BOTTOM = const(_BOT)  # 8
    BOTTOM_RIGHT = const(_BOT | _RIGHT)  # 10
    OUTER_TOP_LEFT = const(_TOP | _LEFT | _OUTER)  # 21
    OUTER_TOP = const(_TOP | _OUTER)  # 20
    OUTER_TOP_RIGHT = const(_TOP | _RIGHT | _OUTER)  # 22
    OUTER_LEFT = const(_LEFT | _OUTER)  # 17
    OUTER_RIGHT = const(_RIGHT | _OUTER)  # 18
    OUTER_BOTTOM_LEFT = const(_BOT | _LEFT | _OUTER)  # 25
    OUTER_BOTTOM = const(_BOT | _OUTER)  # 24
    OUTER_BOTTOM_RIGHT = const(_BOT | _RIGHT | _OUTER)  # 26


class Theme:
    def __init__(self, pal):
        self.background = pal.white[0]
        self.on_background = pal.black[0]
        self.surface = pal.white[0]
        self.on_surface = pal.black[0]
        self.primary = pal.blue[4]
        self.on_primary = pal.white[0]
        self.secondary = pal.amber[0]
        self.on_secondary = pal.black[0]
        self.error = pal.red[0]
        self.on_error = pal.white[0]
        self.primary_variant = pal.blue[3]
        self.secondary_variant = pal.deep_purple[4]
        self.tertiary = pal.amber[0]
        self.on_tertiary = pal.black[0]
        self.tertiary_variant = pal.amber[4]
        self.transparent = False


class Task:
    def __init__(self, callback, delay):
        self.callback = callback
        self.delay = delay
        self.next_run = ticks_add(ticks_ms(), delay)

    def run(self, t):
        self.callback()
        self.next_run = ticks_add(t, self.delay)


class Widget:
    def __init__(self, parent, x=0, y=0, w=None, h=None, fg=None, bg=None, visible=True, align=None, align_to=None, value=None):
        """
        Initialize a Widget.
        
        :param parent: The parent widget (either another Widget or None if no parent).
        :param x: The x-coordinate of the widget, relative to the parent.
        :param y: The y-coordinate of the widget, relative to the parent.
        :param w: The width of the widget.
        :param h: The height of the widget.
        :param fg: The foreground color of the widget.
        :param bg: The background color of the widget.
        :param visible: Whether the widget is visible (default is True).
        :param value: The value of the widget (e.g., text of a label).
        :param align: The alignment of the widget relative to the parent (default is align.CENTER).
        """
        self.parent: Widget = parent
        self._x = x
        self._y = y
        self._w = w or parent.width
        self._h = h or parent.height
        self.fg = fg if fg is not None else parent.fg
        self.bg = bg if bg is not None else parent.bg
        self._visible = visible
        self.align = align if align is not None else ALIGN.TOP_LEFT
        self.align_to: Widget = align_to or parent
        self._value = value  # Value of the widget (e.g., text of a label)
        self.children: list[Widget] = []
        self.dirty_widgets = set()
        self.dirty_descendants = set()
        self.invalidated = False
        self.on_change_callback = None
        self.on_press_callback = None
        self.on_release_callback = None
        if parent:
            self.parent.add_child(self)

    @property
    def area(self):
        """
        Get the absolute area of the widget on the screen.

        :return: An Area object representing the absolute area.
        """

        return Area(self.x, self.y, self.width, self.height)

    @property
    def x(self):
        """Calculate the absolute x-coordinate of the widget based on align
        """
        align = self.align
        align_to = self.align_to

        x = align_to.x + int(self._x)

        if align & _LEFT:
            if align & _OUTER:
                x -= self.width
        elif align & _RIGHT:
            x += align_to.width
            if not align & _OUTER:
                x -= self.width
        else:
            x += (align_to.width - self.width) // 2

        return x

    @x.setter
    def x(self, x):
        if x != self._x:
            self._x = x
            self.invalidate()

    @property
    def y(self):
        """Calculate the absolute y-coordinate of the widget based on align
        """
        align = self.align
        align_to = self.align_to

        y = align_to.y + int(self._y)

        if align & _TOP:
            if align & _OUTER:
                y -= self.height
        elif align & _BOT:
            y += align_to.height
            if not align & _OUTER:
                y -= self.height
        else:
            y += (align_to.height - self.height) // 2

        return y

    @y.setter
    def y(self, y):
        if y != self._y:
            self._y = y
            self.invalidate()

    @property
    def width(self):
        return int(self._w)

    @width.setter
    def width(self, w):
        if w != self._w:
            self._w = w
            self.invalidate()

    @property
    def height(self):
        return int(self._h)

    @height.setter
    def height(self, h):
        if h != self._h:
            self._h = h
            self.invalidate()

    @property
    def display(self):
        return self.parent.display

    @property
    def theme(self):
        return self.display.theme

    @property
    def visible(self):
        """Get widget visibility."""
        return self._visible and self.parent.visible

    @visible.setter
    def visible(self, visible):
        """Set widget visibility."""
        if visible != self._visible:
            if not self.visible:
                self._visible = True
                self.invalidate()
            else:
                self._visible = False
                self.parent.draw(self.area)
                self.display.refresh(self.area)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value != self._value:
            self._value = value
            self.changed()

    def add_child(self, child):
        """Adds a child widget to the current widget."""
        log(f"{name(self)}.add_child({name(child)})")
        self.children.append(child)
        child.invalidate()

    def changed(self):
        """Called when the value of the widget changes.  May be overridden in subclasses.
        If overridden, the subclass should call this method to trigger the on_change_callback.
        """
        if self.visible:
            if self.on_change_callback:
                self.on_change_callback(self)
            self.invalidate()

    def draw(self, area=None):
        """
        Draw the widget on the screen.  Subclasses should override this method to draw the widget unless the widget is
        a container widget (like a screen) that contains other widgets.  Subclasses may call this method to draw the
        background of the widget before drawing other elements.
        """
        if self.bg is not None:
            area = area or self.area
            self.display.framebuf.fill_rect(*area, self.bg)

    def handle_event(self, event):
        """
        Handle an event and propagate it to child widgets.  Subclasses that need to handle events
        should override this method and call this method to propagate the event to children.
        
        :param event: An event from the event system (e.g., mouse or keyboard event).
        """
        # log(f"{name(self)}.handle_event({event})")
        # Propagate the event to the children of the screen
        for child in self.children:
            if child.visible:
                child.handle_event(event)

    def hide(self, hide=True):
        self.visible = not hide

    def remove_child(self, widget):
        """Removes a child widget from the current widget."""
        self.children.remove(widget)
        widget.parent = None

    def invalidate(self):
        if not self.invalidated:
            self.invalidated = True
            if self.parent:
                self.parent.add_dirty_widget(self)
    
    def add_dirty_widget(self, child):
        self.dirty_widgets.add(child)
        self.dirty_descendants.add(child)
        if self.parent:
            self.parent.add_dirty_descendant(self)
    
    def add_dirty_descendant(self, branch):
        self.dirty_descendants.add(branch)
        if self.parent:
            self.parent.add_dirty_descendant(self)

    def render(self):
        if self.invalidated:
            log(f"{drawing(self)}")
            self.draw()
            self.invalidated = False
            if self.parent:
                self.parent.remove_dirty_widget(self)
    
    def remove_dirty_widget(self, child):
        self.dirty_widgets.discard(child)
        if not self.dirty_widgets and not self.dirty_descendants:
            if self.parent:
                self.parent.remove_dirty_descendant(self)

    def remove_dirty_descendant(self, branch):
        self.dirty_descendants.discard(branch)

    def set_on_press(self, callback):
        """Set the callback function for when the button is pressed."""
        self.on_press_callback = callback

    def set_on_release(self, callback):
        """Set the callback function for when the button is released."""
        self.on_release_callback = callback

    def set_on_change(self, callback):
        """Set the callback function for when the value of the widget changes."""
        self.on_change_callback = callback

    def set_value(self, value):
        self.value = value


class Display(Widget):
    displays = []
    timer = None

    def __init__(self, display_drv, broker, tfa=0, bfa=0, format=RGB565):
        super().__init__(None, 0, 0, display_drv.width, display_drv.height, fg=-1, bg=0)
        self.display_drv = display_drv
        display_drv.set_vscroll(tfa, bfa)
        display_drv.vscroll = 0
        self.broker = broker
        broker.quit_func = self.quit
        self._buffer = memoryview(bytearray(display_drv.width * display_drv.height * display_drv.color_depth // 8))
        self.framebuf = FrameBuffer(self._buffer, display_drv.width, display_drv.height, format)
        self._tasks = []
        self._tick_busy = False
        if display_drv.requires_byte_swap:
            self.needs_swap = display_drv.disable_auto_byte_swap(True)
        else:
            self.needs_swap = False
        self.pal = get_palette("material_design", swapped=self.needs_swap, color_depth=display_drv.color_depth)
        self._theme = Theme(self.pal)
        Display.displays.append(self)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        raise ValueError("Cannot set x-coordinate of Display object.")

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        raise ValueError("Cannot set y-coordinate of Display object.")

    @property
    def width(self):
        return self._w

    @width.setter
    def width(self, w):
        raise ValueError("Cannot set width of Display object.")

    @property
    def height(self):
        return self._h

    @height.setter
    def height(self, h):
        raise ValueError("Cannot set height of Display object.")

    @property
    def display(self):
        return self

    @property
    def theme(self):
        return self._theme
    
    @property
    def visible(self):
        return True

    @visible.setter
    def visible(self, visible):
        raise ValueError("Cannot set visibility of Display object.")

    @property
    def active_screen(self):
        if self.children:
            return self.children[0]
        return None
    
    @active_screen.setter
    def active_screen(self, screen):
        for child in self.children:
            self.remove_child(child)
        super().add_child(screen)

    def add_child(self, screen):
        self.active_screen = screen

    def add_task(self, callback, delay):
        new_task = Task(callback, delay)
        self._tasks.append(new_task)
        return new_task

    def refresh(self, area: Area):
        area = area.clip(self.area)
        log(f"Refreshing {area}\n")
        x, y, w, h = area
        for row in range(y, y + h):
            buffer_begin = (row * self.width + x) * 2
            buffer_end = buffer_begin + w * 2
            self.display_drv.blit_rect(
                self._buffer[buffer_begin:buffer_end], x, row, w, 1
            )
        if MARK_UPDATES:
            c = getrandbits(16)
            self.display_drv.fill_rect(x, y, w, 2, c)
            self.display_drv.fill_rect(x, y + h - 2, w, 2, c)
            self.display_drv.fill_rect(x, y, 2, h, c)
            self.display_drv.fill_rect(x + w - 2, y, 2, h, c)

    def remove_task(self, task):
        self._tasks.remove(task)

    def quit(self):
        Display.displays.remove(self)
        self.display_drv.deinit()
        if Display.timer and not Display.displays:
            try:
                Display.timer.deinit()
            except Exception:
                pass
        sys.exit()

    def tick(self):
        if self._tick_busy:
            return
        self._tick_busy = True
        t = ticks_ms()
        if e := self.broker.poll():
            if e.type in Events.filter:
                self.handle_event(e)
        for task in self._tasks:
            if t >= task.next_run:
                task.run(t)
        self.render_dirty_widgets()
        self._tick_busy = False

    def render_dirty_widgets(self):
        # Non-recursive redraw traversal using an explicit stack
        # Use a stack to avoid recursion / stack overflow
        stack = list(self.dirty_descendants)
        dirty_area = None
        while stack:
            widget = stack.pop()
            if widget.invalidated:
                widget.render()
                if dirty_area is None:
                    dirty_area = widget.area
                else:
                    dirty_area += widget.area
            stack.extend(reversed(list(widget.dirty_widgets)))
            stack.extend(reversed(list(widget.dirty_descendants)))
        if dirty_area:
            self.refresh(dirty_area)

    def __getattr__(self, name):
        if name in _display_drv_get_attrs:
            return getattr(self.display_drv, name)
        raise AttributeError(f"{self.__class__.__name__} object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in _display_drv_set_attrs:
            return setattr(self.display_drv, name, value)
        super().__setattr__(name, value)


class Screen(Widget):
    def __init__(self, parent: Display | Widget, fg=None, bg=None, visible=True):
        """
        Initialize a Screen widget, which acts as the top-level container for a Display.
        
        :param display: The Display object that this Screen is associated with.
        """
        super().__init__(parent, 0, 0, parent.width, parent.height, fg, bg, visible)
        self.partitioned = self.display.tfa > 0 or self.display.bfa > 0

        if self.partitioned:
            self.top = Widget(self, *self.display.tfa_area, fg=parent.theme.on_primary, bg=parent.theme.primary)
            self.main = Widget(self, *self.display.vsa_area)
            self.bottom = Widget(self, *self.display.bfa_area, fg=parent.theme.on_primary, bg=parent.theme.primary)


class Button(Widget):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=DEFAULT_ICON_SIZE, fg=None, bg=None, visible=True, align=None, align_to=None, value=None,
                 radius=0, pressed_offset=2, pressed=False,
                 label=None, label_color=None, label_height=DEFAULT_TEXT_HEIGHT):
        """
        Initialize a Button widget.

        :param parent: The parent widget or screen that contains this button.
        :param x: The x-coordinate of the button.
        :param y: The y-coordinate of the button.
        :param width: The width of the button.
        :param height: The height of the button.
        :param bg: The background color of the button (default is blue).
        :param label: A Label widget (optional) to display inside the button.
        """
        self.radius = radius
        self.pressed_offset = pressed_offset
        self._pressed = pressed
        if w is None and label:
            w = len(label) * TEXT_WIDTH + 8
        w = w or DEFAULT_ICON_SIZE
        bg = bg if bg is not None else parent.theme.primary_variant
        fg = fg if fg is not None else parent.theme.on_primary
        label_color = label_color if label_color is not None else fg
        super().__init__(parent, x, y, w, h, fg, bg, visible, align, align_to, value)
        if label:
            if label_height not in TEXT_HEIGHTS:
                raise ValueError("Text height must be 8, 14 or 16 pixels.")
            label_color = label_color if label_color is not None else parent.theme.on_primary
            self.label = Label(self, value=label, fg=label_color, bg=self.bg, h=label_height)
        else:
            self.label = None

    def draw(self, _=None):
        """
        Draw the button background and any child widgets (like a label).
        """
        self.display.framebuf.round_rect(*self.area, self.radius, self.bg, f=True)

    def handle_event(self, event: Events.Any):
        """
        Handle user input events like clicks.

        :param event: An event from the event system (e.g., mouse click).
        """
        if self.area.contains(self.display.translate_point(event.pos)) and event.type == Events.MOUSEBUTTONDOWN:
            self.press()
        elif self._pressed and event.type == Events.MOUSEBUTTONUP:
            self.release()

        # Propagate the event to the children of the button
        super().handle_event(event)

    def press(self):
        log(f"{name(self)}.press()")
        self._pressed = True
        self.display.framebuf.round_rect(*self.area, self.radius, self.fg, f=False)
        if self.on_press_callback:
            self.on_press_callback(self)
        self.display.refresh(self.area)

    def release(self):
        log(f"{name(self)}.release()")
        self._pressed = False
        self.display.framebuf.round_rect(*self.area, self.radius, self.bg, f=False)
        if self.on_release_callback:
            self.on_release_callback(self)
        self.display.refresh(self.area)


class Label(Widget):
    def __init__(self, parent: Widget, x=0, y=0, h=DEFAULT_TEXT_HEIGHT, fg=None, bg=None,
                 visible=True, align=ALIGN.CENTER, align_to=None, value="", scale=1, inverted=False, font_file=None):  # , font=None):
        """
        Initialize a Label widget to display text.
        
        :param parent: The parent widget or screen that contains this label.
        :param x: The x-coordinate of the label.
        :param y: The y-coordinate of the label.
        :param h: The height of the label.
        :param fg: The color of the text (in a suitable color format).
        :param bg: Optional background color of the label. Default is None (no background).
        :param value: The text content of the label.
        """
        if h not in TEXT_HEIGHTS:
            raise ValueError("Text height must be 8, 14 or 16 pixels.")
        self._scale = scale
        self._inverted = inverted
        self._font_file = font_file
        bg = bg if bg is not None else parent.theme.transparent
        super().__init__(parent, x, y, len(value) * TEXT_WIDTH*scale, h*scale, fg, bg, visible, align, align_to, value)

    def draw(self, _=None):
        """
        Draw the label's text on the screen, using absolute coordinates.
        Optionally fills the background first if `bg` is set.
        """
        if self.bg:
            self.display.framebuf.fill_rect(*self.area, self.bg)  # Draw background if bg is specified
        x, y, _, _ = self.area
        self.display.framebuf.text(self.value, x, y, self.fg, height=self.height // self._scale,
                                   scale=self._scale, inverted=self._inverted, font_file=self._font_file)
        # text(self.display.framebuf, self.font, self.value, x, y, self.fg, self.bg)


class TextBox(Widget):
    def __init__(self, parent: Widget, x=0, y=0, w=64, h=None, fg=None, bg=None,
                 visible=True, align=None, align_to=None, value="", margin=1,
                 text_height=DEFAULT_TEXT_HEIGHT, scale=1, inverted=False, font_file=None):
        """
        Initialize a TextBox widget to display text.
        
        :param parent: The parent widget or screen that contains this label.
        :param text: The text content of the label.
        :param x: The x-coordinate of the label.
        :param y: The y-coordinate of the label.
        :param width: The width of the label.
        :param height: The height of the label.
        :param fg: The color of the text (in a suitable color format).
        """
        self.margin = margin
        self._scale = scale
        self._inverted = inverted
        self._font_file = font_file

        if text_height not in TEXT_HEIGHTS:
            raise ValueError("Text height must be 8, 14 or 16 pixels.")
        self.text_height = text_height
        h = h or text_height * scale + 2 * margin
        super().__init__(parent, x, y, w, h, fg, bg, visible, align, align_to, value)

    def draw(self, _=None):
        """
        Draw the label's text on the screen, using absolute coordinates.
        """
        self.display.framebuf.fill_rect(*self.area, self.bg)
        self.display.framebuf.text(self.value, self.x+self.margin, self.y+self.margin, self.fg, height=self.text_height,
                                   scale=self._scale, inverted=self._inverted, font_file=self._font_file)
        # text(self.display.framebuf, self.font, self.value, self.x+self.margin, self.y+self.margin, self.fg, self.bg)


class ProgressBar(Widget):
    def __init__(self, parent: Widget, x=0, y=0, w=64, h=DEFAULT_ICON_SIZE, fg=None, bg=None,
                 visible=True, align=None, align_to=None, value=0.5, vertical=False, reverse=False):
        """
        Initialize a ProgressBar widget to display a progress bar.

        :param parent: The parent widget or screen.
        :param x: The x-coordinate.
        :param y: The y-coordinate.
        :param width: The width of the progress bar.
        :param height: The height of the progress bar.
        :param fg: The foreground color of the progress bar.
        :param bg: The background color.
        :param value: The initial value of the progress bar (0 to 1).
        :param vertical: If True, the progress bar will fill vertically.
        :param reverse: If True, the progress bar will fill in the reverse direction (top-to-bottom for vertical, right-to-left for horizontal).
        """
        self.vertical = vertical
        self.reverse = reverse
        fg = fg if fg is not None else parent.theme.on_primary
        bg = bg if bg is not None else parent.theme.primary_variant
        super().__init__(parent, x, y, w, h, fg, bg, visible, align, align_to, value)
        self._end_radius = self.width//2 if self.vertical else self.height//2
        print("TODO:  move draw_ends to __init__")

    def draw_ends(self):
        """
        Draw the circular ends of the progress bar.
        """
        if self.vertical:
            self.display.framebuf.circle(self.x + self._end_radius, self.y + self._end_radius, self._end_radius, self.fg if self.reverse else self.bg, f=True)
            self.display.framebuf.circle(self.x + self._end_radius, self.y + self.height - self._end_radius, self._end_radius, self.fg if not self.reverse else self.bg, f=True)
        else:
            self.display.framebuf.circle(self.x + self.width - self._end_radius, self.y + self._end_radius, self._end_radius, self.fg if self.reverse else self.bg, f=True)
            self.display.framebuf.circle(self.x + self._end_radius, self.y + self._end_radius, self._end_radius, self.fg if not self.reverse else self.bg, f=True)

    def draw(self, _=None):
        """
        Draw the progress bar on the screen.
        """
        self.draw_ends()
        x, y, w, h = self.area
        if self.vertical:
            y += self._end_radius
            h -= w
        else:
            x += self._end_radius
            w -= h
        self.display.framebuf.fill_rect(x, y, w, h, self.bg)

        if self.value == 0:
            return

        if self.vertical:
            progress_height = int(self.value * h)
            if self.reverse:
                self.display.framebuf.fill_rect(x, y, w, progress_height, self.fg)
            else:
                self.display.framebuf.fill_rect(x, y + h - progress_height, w, progress_height, self.fg)
        else:
            progress_width = int(self.value * w)
            if self.reverse:
                self.display.framebuf.fill_rect(x + w - progress_width, y, progress_width, h, self.fg)
            else:
                self.display.framebuf.fill_rect(x, y, progress_width, h, self.fg)

    def changed(self):
        # Ensure value is between 0 and 1
        if self.value < 0:
            self.value = 0
        elif self.value > 1:
            self.value = 1
        super().changed()


class Icon(Widget):
    def __init__(self, parent: Widget, x=0, y=0, fg=None, bg=None, visible=True, align=None, align_to=None, value=None):
        """
        Initialize an Icon widget to display an icon.
        
        :param parent: The parent widget or screen that contains this icon.
        :param x: The x-coordinate of the icon.
        :param y: The y-coordinate of the icon.
        :param width: The width of the icon.
        :param height: The height of the icon.
        :param fg: The color of the icon (in a suitable color format).
        :param bg: The background color of the icon.
        :param value: The icon file to display.
        """
        if not value:
            raise ValueError("Icon value must be set.")
        self.load_icon(value)
        super().__init__(parent, x, y, self.icon_width, self.icon_height, fg, bg, visible, align, align_to, value)

    def load_icon(self, value):
        """Load icon file and store pixel data."""
        self.icon_width, self.icon_height, self._pixels, self._metadata = png.Reader(filename=value).read_flat()
        if not self._metadata["greyscale"] or self._metadata['bitdepth'] != 8:
            raise ValueError(f"Only 8-bit greyscale PNGs are supported {self.value}")

    def changed(self):
        """Update the icon when the value (file) changes."""
        self.display.framebuf.fill_rect(*self.area, self.bg)
        self.load_icon(self.value)
        # super().changed()

    def draw(self, _=None):
        """
        Draw the icon on the screen.
        """
        color = self.fg
        # pal = ShadesPalette(color=color)
        alpha = 1 if self._metadata["alpha"] else 0
        planes = self._metadata["planes"]
        pixels = self._pixels
        pos_x, pos_y, w, h = self.area
        for y in range(0, h):
            for x in range(0, w):
                if (c := pixels[(y * w + x) * planes + alpha]) != 0:  # noqa: F841
                    # self.display.framebuf.pixel(pos_x + x, pos_y + y, pal[c])
                    self.display.framebuf.pixel(pos_x + x, pos_y + y, color)


class IconButton(Button):
    def __init__(self, parent: Widget, x=0, y=0, w=DEFAULT_ICON_SIZE, h=DEFAULT_ICON_SIZE, fg=None, bg=None,
                 visible=True, align=None, align_to=None, value=None, icon=None):
        """
        Initialize an IconButton widget to display an icon on a button.
        
        :param parent: The parent widget or screen that contains this icon button.
        :param x: The x-coordinate of the icon button.
        :param y: The y-coordinate of the icon button.
        :param width: The width of the icon button.
        :param height: The height of the icon button.
        :param fg: The color of the icon button (in a suitable color format).
        :param bg: The background color of the icon button.
        :param value: The value of the icon button.
        :param icon: The icon file to display on the button.
        """
        fg = fg if fg is not None else parent.fg
        bg = bg if bg is not None else parent.bg
        super().__init__(parent, x, y, w, h, fg, bg, visible, align, align_to, value)
        self.icon = Icon(self, fg=fg, bg=bg, value=icon, align=ALIGN.CENTER)


class CheckBox(IconButton):
    def __init__(self, parent, x=0, y=0, w=DEFAULT_ICON_SIZE, h=DEFAULT_ICON_SIZE, fg=None, bg=None,
                 visible=True, align=None, align_to=None, value=False):
        """
        Initialize a CheckBox widget that toggles between checked and unchecked states.
        
        :param parent: The parent widget or screen that contains this checkbox.
        :param x: The x-coordinate of the checkbox.
        :param y: The y-coordinate of the checkbox.
        :param w: The width of the checkbox (default is 20).
        :param h: The height of the checkbox (default is 20).
        :param fg: The foreground color of the checkbox (default is black).
        :param bg: The background color of the checkbox (default is white).
        :param value: The initial checked state of the checkbox (default is False).
        """
        self.on_icon = ICONS + "check_box_36dp.png"
        self.off_icon = ICONS + "check_box_outline_blank_36dp.png"
        
        # Set initial icon based on the value (checked state)
        icon = self.on_icon if value else self.off_icon
        super().__init__(parent, x, y, w, h, fg, bg, visible, align, align_to, value, icon)
        
    def toggle(self):
        """Toggle the checked state when the checkbox is pressed."""
        self.value = not self.value  # Toggle the boolean value

    def changed(self):
        """Update the icon based on the current checked state."""
        self.icon.value = self.on_icon if self.value else self.off_icon
        super().changed()  # Call the parent changed method

    def handle_event(self, event):
        """Override handle_event to toggle the CheckBox when clicked."""
        if self.area.contains(self.display.translate_point(event.pos)) and event.type == Events.MOUSEBUTTONDOWN:
            self.toggle()
        Widget.handle_event(self, event)  # Propagate to children if necessary


class ToggleButton(IconButton):
    def __init__(self, parent, x=0, y=0, w=DEFAULT_ICON_SIZE, h=DEFAULT_ICON_SIZE, fg=None, bg=None,
                 visible=True, align=None, align_to=None, value=False):
        """
        Initialize a ToggleButton widget.
        
        :param parent: The parent widget or screen that contains this toggle button.
        :param x: The x-coordinate of the toggle button.
        :param y: The y-coordinate of the toggle button.
        :param w: The width of the toggle button (default is 20).
        :param h: The height of the toggle button (default is 20).
        :param fg: The foreground color of the toggle button (default is black).
        :param bg: The background color of the toggle button (default is white).
        :param value: The initial state of the toggle button (default is False, meaning off).
        """
        self.on_icon = ICONS + "toggle_on_36dp.png"
        self.off_icon = ICONS + "toggle_off_36dp.png"

        # Set initial icon based on the value (on/off state)
        icon = self.on_icon if value else self.off_icon
        
        super().__init__(parent, x, y, w, h, fg, bg, visible, align, align_to, value, icon)

    def toggle(self):
        """Toggle the on/off state of the button."""
        self.value = not self.value  # Invert the current state

    def changed(self):
        """Update the icon based on the current on/off state."""
        # Update the icon value based on the current toggle state
        self.icon.value = self.on_icon if self.value else self.off_icon
        super().changed()  # Call the parent changed method

    def handle_event(self, event):
        """Override handle_event to toggle the button when clicked."""
        if self.area.contains(self.display.translate_point(event.pos)) and event.type == Events.MOUSEBUTTONDOWN:
            self.toggle()  # Toggle the state when clicked
        Widget.handle_event(self, event)  # Propagate to children if necessary


class RadioGroup:
    def __init__(self):
        """
        Initialize a RadioGroup to manage a group of RadioButtons.
        """
        self.radio_buttons = []

    def add(self, radio_button):
        """
        Add a RadioButton to the group.
        
        :param radio_button: The RadioButton to add to this group.
        """
        self.radio_buttons.append(radio_button)

    def set_checked(self, selected_button):
        """
        Ensure only the selected button is checked in the group.
        
        :param selected_button: The RadioButton that should be checked.
        """
        for radio_button in self.radio_buttons:
            radio_button.value = (radio_button == selected_button)


class RadioButton(IconButton):
    def __init__(self, parent, group: RadioGroup, x=0, y=0, w=DEFAULT_ICON_SIZE, h=DEFAULT_ICON_SIZE, fg=None, bg=None,
                 visible=True, align=None, align_to=None, value=False):
        """
        Initialize a RadioButton widget that is part of a RadioGroup.
        
        :param parent: The parent widget or screen that contains this radio button.
        :param group: The RadioGroup this button belongs to.
        :param x: The x-coordinate of the radio button.
        :param y: The y-coordinate of the radio button.
        :param w: The width of the radio button (default is 20).
        :param h: The height of the radio button (default is 20).
        :param fg: The foreground color of the radio button (default is black).
        :param bg: The background color of the radio button (default is white).
        :param value: The initial checked state of the radio button (default is False).
        """
        self.on_icon = ICONS + "radio_button_checked_36dp.png"
        self.off_icon = ICONS + "radio_button_unchecked_36dp.png"

        # Set initial icon based on the value (checked state)
        icon = self.on_icon if value else self.off_icon

        # Store the checked state in the value attribute
        self.group = group
        self.group.add(self)
        
        super().__init__(parent, x, y, w, h, fg, bg, visible, align, align_to, value, icon)

    def toggle(self):
        """Toggle the checked state to true when clicked and uncheck other RadioButtons in the group."""
        if not self.value:  # Only toggle if not already checked
            self.group.set_checked(self)  # Uncheck all other buttons in the group

    def changed(self):
        """Update the icon based on the current checked state."""
        # Update the icon value based on the current checked state
        self.icon.value = self.on_icon if self.value else self.off_icon
        super().changed()  # Call the parent changed method

    def handle_event(self, event):
        """Override handle_event to toggle the RadioButton when clicked."""
        if self.area.contains(self.display.translate_point(event.pos)) and event.type == Events.MOUSEBUTTONDOWN:
            self.toggle()  # Toggle the state when clicked
        Widget.handle_event(self, event)  # Propagate to children if necessary


class Slider(ProgressBar):
    def __init__(self, parent, x=0, y=0, w=None, h=None, fg=None, bg=None, visible=True,
                 align=None, align_to=None, value=0.5, vertical=False, reverse=False, knob_color=None, step=0.1):
        """
        Initialize a Slider widget with a circular knob that can be dragged.
        
        :param parent: The parent widget or screen that contains this slider.
        :param x: The x-coordinate of the slider.
        :param y: The y-coordinate of the slider.
        :param w: The width of the slider.
        :param h: The height of the slider.
        :param fg: The foreground color of the slider (progress bar).
        :param bg: The background color of the slider.
        :param knob_color: The color of the knob.
        :param value: The initial value of the slider (0 to 1).
        :param vertical: Whether the slider is vertical (True) or horizontal (False).
        :param step: The step size for adjusting the slider value (default is 0.1).
        """
        self.dragging = False  # Track whether the knob is being dragged
        if vertical and w is None:
            w = DEFAULT_ICON_SIZE
        elif not vertical and h is None:
            h = DEFAULT_ICON_SIZE
        self.knob_radius = (w if vertical else h) // 2  # Halve the radius to fix size
        self.knob_color = knob_color if knob_color is not None else parent.theme.secondary
        self.step = step  # Step size for value adjustments
        super().__init__(parent, x, y, w, h, fg, bg, visible, align, align_to, value, vertical, reverse)

    def draw(self, _=None):
        """Draw the slider, including the progress bar and the circular knob."""
        super().draw()  # Draw the base progress bar

        # Calculate the position of the knob
        knob_center = self._get_knob_center()

        # Draw the knob as a filled circle with correct radius
        self.display.framebuf.circle(*knob_center, self.knob_radius, self.knob_color, f=True)

    def handle_event(self, event):
        """Handle user input events like clicks, dragging, and mouse movements."""
        if self.dragging:
            if event.type == Events.MOUSEBUTTONUP:
                self.dragging = False
            elif event.type == Events.MOUSEMOTION:
                # Adjust the value based on mouse movement while dragging
                if self.vertical:
                    relative_pos = (self._get_knob_center()[1]- self.display.translate_point(event.pos)[1]) / self.height
                else:
                    relative_pos = (self.display.translate_point(event.pos)[0] - self._get_knob_center()[0]) / self.width
                self.adjust_value(relative_pos)

        elif self._point_in_knob(self.display.translate_point(event.pos)) and event.type == Events.MOUSEBUTTONDOWN:
            self.dragging = True
        elif self.area.contains(self.display.translate_point(event.pos)) and event.type == Events.MOUSEBUTTONDOWN:
            # Clicking outside the knob moves the slider by one step
            positive = True
            if self.vertical:
                if self.display.translate_point(event.pos)[1] > self._get_knob_center()[1]:
                    positive = False
            else:
                if self.display.translate_point(event.pos)[0] < self._get_knob_center()[0]:
                    positive = False
            self.adjust_value(self.step if positive else -self.step)

        super().handle_event(event)

    def _get_knob_center(self):
        """Calculate the center coordinates for the knob based on the current value."""
        x, y, w, h = self.area
        if self.reverse:
            value = 1 - self.value
        else:
            value = self.value
        if self.vertical:
            knob_y = int(y + value * (h-w)) + self.knob_radius
            knob_center = (x + self.knob_radius, knob_y)
        else:
            knob_x = int(x + value * (w-h)) + self.knob_radius
            knob_center = (knob_x, y + self.knob_radius)
        return knob_center

    def _point_in_knob(self, pos):
        """Check if the given point is within the knob's circular area."""
        knob_center = self._get_knob_center()
        distance = ((pos[0] - knob_center[0]) ** 2 + (pos[1] - knob_center[1]) ** 2) ** 0.5
        return distance <= self.knob_radius

    def adjust_value(self, value):
        """Adjust the slider value by one step in the specified direction."""
        if self.reverse:
            value = -value
        self.value = max(0, min(1, self.value + value))


class DigitalClock(TextBox):
    def __init__(self, parent, x=0, y=0, h=DEFAULT_TEXT_HEIGHT, fg=None, bg=None, visible=True, align=None, align_to=None):
        """
        Initialize a DigitalClock widget to display the current time.
        
        :param parent: The parent widget or screen that contains this digital clock.
        :param x: The x-coordinate of the digital clock.
        :param y: The y-coordinate of the digital clock.
        :param h: The height of the digital clock.
        :param fg: The color of the text (in a suitable color format).
        :param bg: The background color of the digital clock.
        """
        super().__init__(parent, x, y, TEXT_WIDTH * 8, h, fg, bg, visible, align, align_to, text_height=h)
        self.task = self.display.add_task(self.update_time, 1000)

    def update_time(self):
        y, m, d, h, min, sec, *_ = localtime()
        self.value = f"{h:02}:{min:02}:{sec:02}"


class ScrollBar(Widget):
    def __init__(self, parent, x=0, y=0, w=None, h=None, fg=None, bg=None, visible=True,
                 align=None, align_to=None, vertical=False, value=0.5, step=0.1, knob_color=None, reverse=False):
        """
        Initialize a ScrollBar widget with two arrow IconButtons and a Slider.

        :param parent: The parent widget or screen that contains this scrollbar.
        :param x: The x-coordinate of the scrollbar.
        :param y: The y-coordinate of the scrollbar.
        :param w: The width of the scrollbar (only applies if horizontal).
        :param h: The height of the scrollbar (only applies if vertical).
        :param fg: The foreground color.
        :param bg: The background color.
        :param visible: Whether the scrollbar is visible.
        :param align: The alignment of the scrollbar relative to the parent.
        :param align_to: The widget to align to (default is the parent).
        :param vertical: Whether the scrollbar is vertical (True) or horizontal (False).
        :param value: The initial value of the scrollbar slider (0 to 1).
        :param step: The step size for each arrow button press.
        :param knob_color: The color of the slider knob.
        :param reverse: Whether the scrollbar is reversed (default is False).
        """
        self.vertical = vertical
        self.step = step

        if self.vertical:
            w = w or DEFAULT_ICON_SIZE  # For vertical, set width and auto-calculate height
            h = h or 3 * DEFAULT_ICON_SIZE
        else:
            w = w or 3 * DEFAULT_ICON_SIZE
            h = h or DEFAULT_ICON_SIZE
        reverse = not reverse if vertical else reverse  # Reverse the direction for vertical sliders
        super().__init__(parent, x, y, w, h, fg, bg, visible, align, align_to)

        # Add IconButton on each end and Slider in the middle
        if self.vertical:
            self.pos_button = IconButton(self, icon=ICONS + "keyboard_arrow_up_18dp.png", fg=fg, bg=bg, align=ALIGN.TOP)
            self.neg_button = IconButton(self, icon=ICONS + "keyboard_arrow_down_18dp.png", fg=fg, bg=bg, align=ALIGN.BOTTOM)
            self.slider = Slider(self, fg=fg, bg=bg, h=(h - self.neg_button.height - self.pos_button.height), vertical=True, value=value, step=step, align=ALIGN.CENTER, knob_color=knob_color, reverse=reverse)
        else:
            self.neg_button = IconButton(self, icon=ICONS + "keyboard_arrow_left_18dp.png", fg=fg, bg=bg, align=ALIGN.LEFT)
            self.pos_button = IconButton(self, icon=ICONS + "keyboard_arrow_right_18dp.png", fg=fg, bg=bg, align=ALIGN.RIGHT)
            self.slider = Slider(self, fg=fg, bg=bg, w=(w - self.neg_button.width - self.pos_button.width), vertical=False, value=value, step=step, align=ALIGN.CENTER, knob_color=knob_color, reverse=reverse)

        # Set button callbacks to adjust slider value
        self.neg_button.set_on_press(lambda _: self.slider.adjust_value(-self.step))
        self.pos_button.set_on_press(lambda _: self.slider.adjust_value(self.step))
