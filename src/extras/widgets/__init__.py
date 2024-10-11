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
    return f"ID {obj.id}\t{obj.__class__.__name__: <12}" if hasattr(obj, "id") else f"{obj.__class__.__name__: <12}"


def tick(_=None):
    for display in Display.displays:
        display.tick()

def init_timer(period=10):
    if Display.timer is None:
        from timer import get_timer
        Display.timer = get_timer(tick, period)

_display_drv_get_attrs = {"set_vscroll", "tfa", "bfa", "vsa", "vscroll", "tfa_area", "bfa_area", "vsa_area", "scroll_by", "scroll_to", "translate_point"}
_display_drv_set_attrs = {"vscroll"}

_PAD = const(2)
DEFAULT_PADDING = (_PAD, _PAD, _PAD, _PAD)
DEFAULT_ICON_SIZE = const(36)
SMALL_ICON_SIZE = const(18)
DEFAULT_BUTTON_SIZE = DEFAULT_ICON_SIZE + 2 * _PAD
DEFAULT_TEXT_HEIGHT = const(16)
TEXT_WIDTH = const(8)
TEXT_HEIGHTS = (8, 14, 16)

_LEFT = const(1 << 0)
_RIGHT = const(1 << 1)
_TOP = const(1 << 2)
_BOT = const(1 << 3)
_OUTER = const(1 << 4)


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
    next_instance_id = 0
    def __init__(self, parent, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=None, padding=None):
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
        self.id = Widget.next_instance_id  # Currently only used in debugging
        Widget.next_instance_id += 1

        self._parent: Widget = None
        self.fg = fg if fg is not None else parent.fg if parent else -1
        self.bg = bg if bg is not None else parent.bg if parent else 0
        self._visible = visible
        self._value = value  # Value of the widget (e.g., text of a label)
        self.padding = padding if padding is not None else DEFAULT_PADDING

        self.children: list[Widget] = []
        self.dirty_widgets = set()
        self.dirty_descendants = set()
        self.invalidated = False
        self.on_change_callback = None
        self.on_press_callback = None
        self.on_release_callback = None

        self._x = self._y = self._w = self._h = self._align = self._align_to = None
        self.set_position(x, y, w or parent.width, h or parent.height,
                          align if align is not None else ALIGN.TOP_LEFT, align_to or parent)
        self.parent: Widget = parent

    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self, parent):
        if parent != self._parent:
            if self._parent:
                self._parent.remove_child(self)
            self._parent = parent
            if self._parent:
                self._parent.add_child(self)
            self.invalidate()

    @property
    def area(self):
        """
        Get the absolute area of the widget on the screen.

        :return: An Area object representing the absolute area.
        """
        return Area(self.x, self.y, self.width, self.height)

    @property
    def padded_area(self):
        return self.area.inset(*self.padding)

    @property
    def x(self):
        """Calculate the absolute x-coordinate of the widget based on align
        """
        align = self.align
        align_to = self.align_to or self.display

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

    @property
    def y(self):
        """Calculate the absolute y-coordinate of the widget based on align
        """
        align = self.align
        align_to = self.align_to or self.display

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

    @property
    def width(self):
        return int(self._w)

    @property
    def height(self):
        return int(self._h)

    @property
    def align(self):
        return self._align
    
    @property
    def align_to(self):
        return self._align_to

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
                self.parent.invalidate()

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
        log(f"Adding\t{name(child)}\tto\t{name(self)}")
        self.children.append(child)
        child.invalidate()

    def changed(self):
        """Called when the value of the widget changes.  May be overridden in subclasses.
        If overridden, the subclass should call this method to trigger the on_change_callback and invalidate.
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
        # log(f"Event on\t{name(self)}\tis\t{event})")
        # Propagate the event to the children of the widget
        for child in self.children:
            if child.visible:
                try:
                    child.handle_event(event)
                except Exception as e:
                    log(f"Error handling event on {name(child)}: {e}")

    def hide(self, hide=True):
        self.visible = not hide

    def invalidate(self):
        if not self.invalidated:
            self.invalidated = True
            if self.parent:
                self.parent.add_dirty_widget(self)
            for child in self.children:
                child.invalidate()

    def remove_child(self, widget):
        """Removes a child widget from the current widget."""
        self.children.remove(widget)
        widget.parent = None

    def set_position(self, x=None, y=None, w=None, h=None, align=None, align_to=None):
        changed = False
        if x is not None:
            self._x = x
            changed = True
        if y is not None:
            self._y = y
            changed = True
        if w is not None:
            self._w = w
            changed = True
        if h is not None:
            self._h = h
            changed = True
        if align is not None:
            self._align = align
            changed = True
        if align_to is not None:
            self._align_to = align_to
            changed = True
        if changed and self.parent is not None:
            self.parent.invalidate()

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
            log(f"Drawing\t{name(self)}\ton\t{name(self.parent)}\tat\t{self.area}")
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
        self.display_drv = display_drv
        super().__init__(None, 0, 0, display_drv.width, display_drv.height, fg=-1, bg=0, padding=(0, 0, 0, 0))
        display_drv.set_vscroll(tfa, bfa)
        display_drv.vscroll = 0
        self.broker = broker
        broker.quit_func = self.quit
        self._buffer = memoryview(bytearray(display_drv.width * display_drv.height * display_drv.color_depth // 8))
        self.framebuf = FrameBuffer(self._buffer, display_drv.width, display_drv.height, format)
        self._dirty_areas = []
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
    def parent(self):
        return None
    
    @parent.setter
    def parent(self, parent):
        if parent is not None:
            raise ValueError("Display object cannot have a parent.")

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def width(self):
        return self._w

    @property
    def height(self):
        return self._h

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

    def set_position(self, *args, **kwargs):
        self._x = 0
        self._y = 0
        self._w = self.display_drv.width
        self._h = self.display_drv.height
        self._align = ALIGN.TOP_LEFT
        self._align_to = None

    def add_task(self, callback, delay):
        new_task = Task(callback, delay)
        self._tasks.append(new_task)
        return new_task

    def refresh(self, area: Area):
        area = area.clip(self.area)
        log(f"Refreshing\t{area}\n")
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

        if self._dirty_areas:
            # combine overlapping areas in self._dirty_areas into a new list called dirty_areas
            dirty_areas = []
            while self._dirty_areas:
                area = self._dirty_areas.pop()
                for i, other in enumerate(self._dirty_areas):
                    if area.touches_or_intersects(other):
                        area += other
                        self._dirty_areas.pop(i)
                dirty_areas.append(area)

            for dirty in dirty_areas:
                self.refresh(dirty)
        else:
            if e := self.broker.poll():
                if e.type in Events.filter:
                    self.handle_event(e)

            t = ticks_ms()
            for task in self._tasks:
                if t >= task.next_run:
                    task.run(t)

            self.render_dirty_widgets()
        self._tick_busy = False

    def render_dirty_widgets(self):
        # Non-recursive redraw traversal using an explicit stack
        # Use a stack to avoid recursion / stack overflow
        stack = list(self.dirty_descendants)
        
        while stack:
            # Collect all widgets at the current level
            current_level = []
            while stack:
                widget = stack.pop()
                if widget.invalidated and widget.visible:
                    widget.render()
                    self._dirty_areas.append(widget.area)
                current_level.append(widget)
            
            # Now process the next level of descendants from current_level
            for widget in current_level:
                stack.extend(reversed(list(widget.dirty_widgets)))
                stack.extend(reversed(list(widget.dirty_descendants)))

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
        super().__init__(parent, 0, 0, parent.width, parent.height, fg=fg, bg=bg, visible=visible, padding=(0, 0, 0, 0))
        self.partitioned = self.display.tfa > 0 or self.display.bfa > 0

        if self.partitioned:
            self.top = Widget(self, *self.display.tfa_area, fg=parent.theme.on_primary, bg=parent.theme.primary)
            self.main = Widget(self, *self.display.vsa_area)
            self.bottom = Widget(self, *self.display.bfa_area, fg=parent.theme.on_primary, bg=parent.theme.primary)


class Button(Widget):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=None, padding=None,
                 radius=0, pressed_offset=2, pressed=False, label=None, label_color=None, label_height=DEFAULT_TEXT_HEIGHT):
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
            w = (len(label) +1) * TEXT_WIDTH + 2 * _PAD
        w = w or DEFAULT_BUTTON_SIZE
        h = h or DEFAULT_BUTTON_SIZE
        bg = bg if bg is not None else parent.theme.primary_variant
        fg = fg if fg is not None else parent.theme.on_primary
        label_color = label_color if label_color is not None else fg
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding)
        if label:
            if label_height not in TEXT_HEIGHTS:
                raise ValueError("Text height must be 8, 14 or 16 pixels.")
            label_color = label_color if label_color is not None else parent.theme.on_primary
            self.label = Label(self, value=label, fg=label_color, bg=self.bg, text_height=label_height)
        else:
            self.label = None

    def draw(self, _=None):
        """
        Draw the button background and shape only.
        """
        self.parent.draw(self.area)
        self.display.framebuf.round_rect(*self.padded_area, self.radius, self.bg, f=True)

    def handle_event(self, event: Events.Any):
        """
        Handle user input events like clicks.

        :param event: An event from the event system (e.g., mouse click).
        """
        if self.padded_area.contains(self.display.translate_point(event.pos)) and event.type == Events.MOUSEBUTTONDOWN:
            self.press()
        elif self._pressed and event.type == Events.MOUSEBUTTONUP:
            self.release()

        # Propagate the event to the children of the button
        super().handle_event(event)

    def press(self):
        log(f"Press\t{name(self)}")
        self._pressed = True
        self.display.framebuf.round_rect(*self.padded_area, self.radius, self.fg, f=False)
        if self.on_press_callback:
            self.on_press_callback(self)
        self.display.refresh(self.area)

    def release(self):
        log(f"Release\n{name(self)}")
        self._pressed = False
        self.display.framebuf.round_rect(*self.padded_area, self.radius, self.bg, f=False)
        if self.on_release_callback:
            self.on_release_callback(self)
        self.display.refresh(self.area)


class Label(Widget):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=None, padding=None,
                 text_height=DEFAULT_TEXT_HEIGHT, scale=1, inverted=False, font_file=None):
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
        if text_height not in TEXT_HEIGHTS:
            raise ValueError("Text height must be 8, 14 or 16 pixels.")
        padding = padding if padding is not None else (0, 0, 0, 0)
        w = w or len(value) * TEXT_WIDTH * scale + padding[0] + padding[2]
        h = h or text_height * scale + padding[1] + padding[3]
        align = align if align is not None else ALIGN.CENTER
        value = value if value is not None else ""
        self.text_height = text_height
        self._scale = scale
        self._inverted = inverted
        self._font_file = font_file
        bg = bg if bg is not None else parent.theme.transparent
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding)

    def draw(self, _=None):
        """
        Draw the label's text on the screen, using absolute coordinates.
        Optionally fills the background first if `bg` is set.
        """
        if self.bg is not self.parent.theme.transparent:
            self.display.framebuf.fill_rect(*self.padded_area, self.bg)  # Draw background if bg is specified
        x, y, _, _ = self.padded_area
        self.display.framebuf.text(self.value, x, y, self.fg, height=self.text_height, scale=self._scale, inverted=self._inverted, font_file=self._font_file)


class TextBox(Widget):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=None, padding=None,
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
        if text_height not in TEXT_HEIGHTS:
            raise ValueError("Text height must be 8, 14 or 16 pixels.")
        padding = padding if padding is not None else DEFAULT_PADDING
        w = w or self.parent.width
        h = h or text_height*scale + padding[1] + padding[3] + _PAD * 2
        value = value if value is not None else ""
        self.text_height = text_height
        self._scale = scale
        self._inverted = inverted
        self._font_file = font_file
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding)

    def draw(self, _=None):
        """
        Draw the label's text on the screen, using absolute coordinates.
        """
        pa = self.padded_area
        self.display.framebuf.fill_rect(*pa, self.bg)
        self.display.framebuf.text(self.value, pa.x + _PAD, pa.y + _PAD, self.fg, height=self.text_height,
                                   scale=self._scale, inverted=self._inverted, font_file=self._font_file)


class Icon(Widget):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=None, padding=None):
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
            raise ValueError("Icon value must be set the filename with path.")
        self.load_icon(value)
        padding = padding if padding is not None else DEFAULT_PADDING
        w = w or self._icon_width + padding[0] + padding[2]
        h = h or self._icon_height + padding[1] + padding[3]
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding)

    def load_icon(self, value):
        """Load icon file and store pixel data."""
        self._icon_width, self._icon_height, self._pixels, self._metadata = png.Reader(filename=value).read_flat()
        if not self._metadata["greyscale"] or self._metadata['bitdepth'] != 8:
            raise ValueError(f"Only 8-bit greyscale PNGs are supported {self.value}")

    def changed(self):
        """Update the icon when the value (file) changes."""
        self.display.framebuf.fill_rect(*self.padded_area, self.bg)
        self.load_icon(self.value)
        super().changed()

    def draw(self, _=None):
        """
        Draw the icon on the screen.
        """
        color = self.fg
        # pal = ShadesPalette(color=color)
        alpha = 1 if self._metadata["alpha"] else 0
        planes = self._metadata["planes"]
        pixels = self._pixels
        pos_x, pos_y, w, h = self.padded_area
        for y in range(0, h):
            for x in range(0, w):
                if (c := pixels[(y * w + x) * planes + alpha]) != 0:  # noqa: F841
                    # self.display.framebuf.pixel(pos_x + x, pos_y + y, pal[c])
                    self.display.framebuf.pixel(pos_x + x, pos_y + y, color)


class IconButton(Button):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=None, padding=None,
                 icon=None):
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
        w = w or SMALL_ICON_SIZE + 2 * _PAD
        h = h or SMALL_ICON_SIZE + 2 * _PAD
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding)
        self.icon = Icon(self, align=ALIGN.CENTER, fg=fg, bg=bg, value=icon, padding=(0, 0, 0, 0))



class CheckBox(IconButton):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=False, padding=None):
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
        w = w or DEFAULT_ICON_SIZE
        h = h or DEFAULT_ICON_SIZE
        self.on_icon = ICONS + "check_box_36dp.png"
        self.off_icon = ICONS + "check_box_outline_blank_36dp.png"
        # Set initial icon based on the value (checked state)
        icon = self.on_icon if value else self.off_icon
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding, icon)

    def handle_event(self, event):
        """Override handle_event to toggle the CheckBox when clicked."""
        if self.area.contains(self.display.translate_point(event.pos)) and event.type == Events.MOUSEBUTTONDOWN:
            self.toggle()
        Widget.handle_event(self, event)  # Propagate to children if necessary

    def toggle(self):
        """Toggle the checked state when the checkbox is pressed."""
        self.value = not self.value  # Toggle the boolean value

    def changed(self):
        """Update the icon based on the current checked state."""
        self.icon.value = self.on_icon if self.value else self.off_icon
        super().changed()  # Call the parent changed method


class ToggleButton(IconButton):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=False, padding=None):
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
        w = w or DEFAULT_ICON_SIZE
        h = h or DEFAULT_ICON_SIZE
        self.on_icon = ICONS + "toggle_on_36dp.png"
        self.off_icon = ICONS + "toggle_off_36dp.png"
        # Set initial icon based on the value (on/off state)
        icon = self.on_icon if value else self.off_icon
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding, icon)

    def handle_event(self, event):
        """Override handle_event to toggle the button when clicked."""
        if self.area.contains(self.display.translate_point(event.pos)) and event.type == Events.MOUSEBUTTONDOWN:
            self.toggle()  # Toggle the state when clicked
        Widget.handle_event(self, event)  # Propagate to children if necessary

    def toggle(self):
        """Toggle the on/off state of the button."""
        self.value = not self.value  # Invert the current state

    def changed(self):
        """Update the icon based on the current on/off state."""
        # Update the icon value based on the current toggle state
        self.icon.value = self.on_icon if self.value else self.off_icon
        super().changed()  # Call the parent changed method


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
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=False, padding=None,
        group: RadioGroup=None):
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
        if group is None:
            raise ValueError("RadioButton must be part of a RadioGroup.")
        self.group = group
        self.group.add(self)
        w = w or DEFAULT_ICON_SIZE
        h = h or DEFAULT_ICON_SIZE
        self.on_icon = ICONS + "radio_button_checked_36dp.png"
        self.off_icon = ICONS + "radio_button_unchecked_36dp.png"
        # Set initial icon based on the value (checked state)
        icon = self.on_icon if value else self.off_icon
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding, icon)

    def handle_event(self, event):
        """Override handle_event to toggle the RadioButton when clicked."""
        if self.area.contains(self.display.translate_point(event.pos)) and event.type == Events.MOUSEBUTTONDOWN:
            self.toggle()  # Toggle the state when clicked
        Widget.handle_event(self, event)  # Propagate to children if necessary

    def toggle(self):
        """Toggle the checked state to true when clicked and uncheck other RadioButtons in the group."""
        if not self.value:  # Only toggle if not already checked
            self.group.set_checked(self)  # Uncheck all other buttons in the group

    def changed(self):
        """Update the icon based on the current checked state."""
        # Update the icon value based on the current checked state
        self.icon.value = self.on_icon if self.value else self.off_icon
        super().changed()  # Call the parent changed method


class ProgressBar(Widget):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=0.0, padding=None,
                 vertical=False, reverse=False):
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
        w = w or (SMALL_ICON_SIZE if vertical else SMALL_ICON_SIZE * 4)
        h = h or (SMALL_ICON_SIZE if not vertical else SMALL_ICON_SIZE * 4)
        fg = fg if fg is not None else parent.theme.on_primary
        bg = bg if bg is not None else parent.theme.primary_variant
        self.vertical = vertical
        self.reverse = reverse
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding)
        self.end_radius = self.padded_area.w//2 if self.vertical else self.padded_area.h//2
        log("TODO:  ProgressBar - move draw_ends to __init__")

    def draw_ends(self):
        """
        Draw the circular ends of the progress bar.
        """
        pa = self.padded_area
        if self.vertical:
            self.display.framebuf.circle(pa.x + self.end_radius, pa.y + self.end_radius, self.end_radius, self.fg if self.reverse else self.bg, f=True)
            self.display.framebuf.circle(pa.x + self.end_radius, pa.y + pa.h - self.end_radius, self.end_radius, self.fg if not self.reverse else self.bg, f=True)
        else:
            self.display.framebuf.circle(pa.x + pa.w - self.end_radius, pa.y + self.end_radius, self.end_radius, self.fg if self.reverse else self.bg, f=True)
            self.display.framebuf.circle(pa.x + self.end_radius, pa.y + self.end_radius, self.end_radius, self.fg if not self.reverse else self.bg, f=True)

    def draw(self, _=None):
        """
        Draw the progress bar on the screen.
        """
        self.draw_ends()
        x, y, w, h = self.padded_area
        if self.vertical:
            y += self.end_radius
            h -= w
        else:
            x += self.end_radius
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


class Slider(ProgressBar):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=0.0, padding=None,
                 vertical=False, reverse=False, knob_color=None, step=0.1):
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
        if vertical:
            w = w or SMALL_ICON_SIZE
            h = h or parent.height if parent else 6 * SMALL_ICON_SIZE
            align = align if align is not None else ALIGN.RIGHT
        else:
            w = w or parent.width if parent else 6 * SMALL_ICON_SIZE
            h = h or SMALL_ICON_SIZE
            align = align if align is not None else ALIGN.BOTTOM
        self.knob_color = knob_color if knob_color is not None else parent.theme.secondary
        self.step = step  # Step size for value adjustments
        self.dragging = False  # Track whether the knob is being dragged
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding, vertical, reverse)
        self.knob_radius = self.end_radius

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

    def adjust_value(self, value):
        """Adjust the slider value by one step in the specified direction."""
        if self.reverse:
            value = -value
        self.value = max(0, min(1, self.value + value))

    def _get_knob_center(self):
        """Calculate the center coordinates for the knob based on the current value."""
        x, y, w, h = self.padded_area
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


class ScrollBar(Widget):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=0.0, padding=None,
                 vertical=False, reverse=False, knob_color=None, step=0.1):
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

        if vertical:
            w = w or SMALL_ICON_SIZE
            h = h or parent.height if parent else 6 * SMALL_ICON_SIZE
            align = align if align is not None else ALIGN.RIGHT
            icon_size = w
        else:
            w = w or parent.width if parent else 6 * SMALL_ICON_SIZE
            h = h or SMALL_ICON_SIZE
            align = align if align is not None else ALIGN.BOTTOM
            icon_size = h
        reverse = not reverse if vertical else reverse  # Reverse the direction for vertical sliders
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding)

        # Add IconButton on each end and Slider in the middle
        if vertical:
            self.pos_button = IconButton(self, w=icon_size, h=icon_size, icon=ICONS + "keyboard_arrow_up_18dp.png", fg=fg, bg=bg, align=ALIGN.TOP)
            self.neg_button = IconButton(self, w=icon_size, h=icon_size, icon=ICONS + "keyboard_arrow_down_18dp.png", fg=fg, bg=bg, align=ALIGN.BOTTOM)
            self.slider = Slider(self, w=icon_size, h=h-2*icon_size, vertical=True, align=ALIGN.CENTER, value=value, step=step, reverse=reverse, knob_color=knob_color, fg=fg, bg=bg)
        else:
            self.neg_button = IconButton(self, w=icon_size, h=icon_size, icon=ICONS + "keyboard_arrow_left_18dp.png", fg=fg, bg=bg, align=ALIGN.LEFT)
            self.pos_button = IconButton(self, w=icon_size, h=icon_size, icon=ICONS + "keyboard_arrow_right_18dp.png", fg=fg, bg=bg, align=ALIGN.RIGHT)
            self.slider = Slider(self, w=w-icon_size*2, h=icon_size, vertical=False, align=ALIGN.CENTER, value=value, step=step, reverse=reverse, knob_color=knob_color, fg=fg, bg=bg)

        # Set button callbacks to adjust slider value
        self.neg_button.set_on_press(lambda _: self.slider.adjust_value(-self.slider.step))
        self.pos_button.set_on_press(lambda _: self.slider.adjust_value(self.slider.step))


class DigitalClock(TextBox):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=None, padding=None,
                 text_height=DEFAULT_TEXT_HEIGHT):
        """
        Initialize a DigitalClock widget to display the current time.
        
        :param parent: The parent widget or screen that contains this digital clock.
        :param x: The x-coordinate of the digital clock.
        :param y: The y-coordinate of the digital clock.
        :param h: The height of the digital clock.
        :param fg: The color of the text (in a suitable color format).
        :param bg: The background color of the digital clock.
        """
        if text_height not in TEXT_HEIGHTS:
            raise ValueError("Text height must be 8, 14 or 16 pixels.")
        w = w or (TEXT_WIDTH +1) * 8
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding, text_height)
        self.task = self.display.add_task(self.update_time, 1000)

    def update_time(self):
        y, m, d, h, min, sec, *_ = localtime()
        self.value = f"{h:02}:{min:02}:{sec:02}"
