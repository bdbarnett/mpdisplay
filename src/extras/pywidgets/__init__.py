from gfx import Area
from eventsys.events import Events
from micropython import const
from time import localtime
from gfx.framebuf_plus import FrameBuffer, RGB565
from palettes import get_palette
import sys
from random import getrandbits
from . import pct  # noqa: F401
from .__constants__ import ICON_SIZE, ALIGN, POSITION, TEXT_SIZE
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
DEFAULT_BUTTON_SIZE = ICON_SIZE.LARGE + 2 * _PAD
TEXT_WIDTH = const(8)


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
        self._event_callbacks = {}
        self._change_callback = None

        self._x = self._y = self._w = self._h = self._align = self._align_to = None
        self.set_position(x, y, w or parent.width, h or parent.height,
                          align if align is not None else ALIGN.TOP_LEFT, align_to or parent)
        self.parent: Widget = parent
        self._register_callbacks()

    def __str__(self):
        return f"ID {self.id} {self.__class__.__name__}"
    
    def __format__(self, format_spec):
        return f"ID {self.id} {self.__class__.__name__:{format_spec}}"

    def _register_callbacks(self):
        """
        Register event callbacks for the widget.  Subclasses should override this method to register event callbacks.
        """
        pass

    def add_event_cb(self, event_type: int, callback: callable, data=None):
        # Look in self._event_callbacks for the event_type.  The value is a dictionary.
        # Each item's key is the callback and value is the optional data.  If the event_type is not found,
        # add it to the dictionary with the callback and data.
        data = data or self
        if event_type not in self._event_callbacks:
            self._event_callbacks[event_type] = {}
        self._event_callbacks[event_type][callback] = data

    def remove_event_cb(self, event_type: int, callback: callable):
        # Look in self._event_callbacks for the event_type.  If found, remove the callback from the dictionary.
        if event_type in self._event_callbacks:
            self._event_callbacks[event_type].pop(callback, None)

    def handle_event(self, event, condition=None):
        """
        Handle an event and propagate it to child widgets.  Subclasses that need to handle events
        should override this method and call this method to propagate the event to children.
        
        :param event: An event from the event system (e.g., mouse or keyboard event).
        """
        if condition is None:
            if event.type in (Events.MOUSEBUTTONDOWN, Events.MOUSEBUTTONUP, Events.MOUSEMOTION):
                condition = lambda child, e: child.padded_area.contains(self.display.translate_point(e.pos))  # noqa: E731
            else:
                condition = lambda child, e: True  # noqa: E731
        for child in self.children:
            if child.visible:
                if condition(child, event):
                    for callback, data in child._event_callbacks.get(event.type, {}).items():
                        callback(data, event)
                child.handle_event(event, condition)

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
                if self.align_to is None:
                    self.set_position(align_to=parent)

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

        if align & POSITION.LEFT:
            if align & POSITION.OUTER:
                x -= self.width
        elif align & POSITION.RIGHT:
            x += align_to.width
            if not align & POSITION.OUTER:
                x -= self.width
        else:
            x += (align_to.width - self.width) // 2

        return x

    @x.setter
    def x(self, x):
        self.set_position(x=x)

    @property
    def y(self):
        """Calculate the absolute y-coordinate of the widget based on align
        """
        align = self.align
        align_to = self.align_to or self.display

        y = align_to.y + int(self._y)

        if align & POSITION.TOP:
            if align & POSITION.OUTER:
                y -= self.height
        elif align & POSITION.BOTTOM:
            y += align_to.height
            if not align & POSITION.OUTER:
                y -= self.height
        else:
            y += (align_to.height - self.height) // 2

        return y

    @y.setter
    def y(self, y):
        self.set_position(y=y)

    @property
    def width(self):
        return int(self._w)

    @width.setter
    def width(self, w):
        self.set_position(w=w)

    @property
    def height(self):
        return int(self._h)

    @height.setter
    def height(self, h):
        self.set_position(h=h)

    @property
    def align(self):
        return self._align

    @align.setter
    def align(self, align):
        self.set_position(align=align)

    @property
    def align_to(self):
        return self._align_to

    @align_to.setter
    def align_to(self, align_to):
        self.set_position(align_to=align_to)

    @property
    def display(self):
        return self.parent.display

    @property
    def theme(self) -> Theme:
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
        log("Adding", child, "to", self)
        self.children.append(child)
        child.invalidate()

    def changed(self):
        """Called when the value of the widget changes.  May be overridden in subclasses.
        If overridden, the subclass should call this method to trigger the on_change_callback and invalidate.
        """
        if self.visible:
            if self._change_callback:
                self._change_callback(self)
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
        self.invalidate()

    def set_change_cb(self, callback):
        self._change_callback = callback

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
            log("Drawing", self, "on", self.parent, "at", self.area)
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
        log("Refreshing", area)
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
                 radius=0, pressed_offset=2, pressed=False, label=None, text_color=None, text_height=TEXT_SIZE.LARGE, icon_file=None, icon_color=None):
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
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding)
        if icon_file:
            icon_align = ALIGN.CENTER if not label else ALIGN.LEFT
            icon_color = icon_color if icon_color is not None else parent.theme.on_primary
            self.icon = Icon(self, align=icon_align, fg=icon_color, bg=self.bg, value=icon_file)
        if label:
            if text_height not in TEXT_SIZE:
                raise ValueError("Text height must be 8, 14 or 16 pixels.")
            label_align = ALIGN.CENTER if not icon_file else ALIGN.OUTER_RIGHT
            label_align_to = self.icon if icon_file else self
            text_color = text_color if text_color is not None else parent.theme.on_primary
            self.label = Label(self, value=label, align=label_align, align_to=label_align_to, fg=text_color, bg=self.bg, text_height=text_height)
        else:
            self.label = None

    def _register_callbacks(self):
        self.add_event_cb(Events.MOUSEBUTTONDOWN, self.press)
        self.add_event_cb(Events.MOUSEBUTTONUP, self.release)

    def draw(self, _=None):
        """
        Draw the button background and shape only.
        """
        self.parent.draw(self.area)
        self.display.framebuf.round_rect(*self.padded_area, self.radius, self.bg, f=True)

    def press(self, data=None, event=None):
        self._pressed = True
        self.display.framebuf.round_rect(*self.padded_area, self.radius, self.fg, f=False)
        self.display.refresh(self.area)

    def release(self, data=None, event=None):
        self._pressed = False
        self.display.framebuf.round_rect(*self.padded_area, self.radius, self.bg, f=False)
        self.display.refresh(self.area)


class Label(Widget):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=None, padding=None,
                 text_height=TEXT_SIZE.LARGE, scale=1, inverted=False, font_file=None):
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
        if text_height not in TEXT_SIZE:
            raise ValueError("Text height must be 8, 14 or 16 pixels.")
        padding = padding if padding is not None else (0, 0, 0, 0)
        w = w or len(value) * TEXT_WIDTH * scale + padding[0] + padding[2]
        h = h or text_height * scale + padding[1] + padding[3]
        align = align if align is not None else ALIGN.CENTER
        value = value if value is not None else ""
        self.text_height = text_height
        self.scale = scale
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
        self.display.framebuf.text(self.value, x, y, self.fg, height=self.text_height, scale=self.scale, inverted=self._inverted, font_file=self._font_file)

    @property
    def char_width(self):
        return TEXT_WIDTH * self.scale
    
    @property
    def char_height(self):
        return self.text_height * self.scale


class TextBox(Widget):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=None, padding=None,
                 format="", text_height=TEXT_SIZE.LARGE, scale=1, inverted=False, font_file=None):
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
        if text_height not in TEXT_SIZE:
            raise ValueError("Text height must be 8, 14 or 16 pixels.")
        padding = padding if padding is not None else DEFAULT_PADDING
        w = w or parent.width if parent else 60
        h = h or text_height*scale + padding[1] + padding[3]
        value = value if value is not None else ""
        self.format = format
        self.text_height = text_height
        self.scale = scale
        self._inverted = inverted
        self._font_file = font_file
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding)

    def draw(self, _=None):
        """
        Draw the label's text on the screen, using absolute coordinates.
        """
        pa = self.padded_area
        self.display.framebuf.fill_rect(*pa, self.bg)
        y = pa.y + (pa.h - self.text_height * self.scale) // 2
        self.display.framebuf.text(f"{self.value:{self.format}}", pa.x + _PAD, y, self.fg, height=self.text_height,
                                   scale=self.scale, inverted=self._inverted, font_file=self._font_file)

    @property
    def char_width(self):
        return TEXT_WIDTH * self.scale
    
    @property
    def char_height(self):
        return self.text_height * self.scale


class Icon(Widget):
    cache = {}
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
            raise ValueError("Icon value must be set to the filename with path.")
        self.load_icon(value)
        padding = padding if padding is not None else DEFAULT_PADDING
        w = w or self._icon_width + padding[0] + padding[2]
        h = h or self._icon_height + padding[1] + padding[3]
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding)

    def load_icon(self, value):
        """Load icon file and store pixel data."""
        if value in Icon.cache:
            self._fbuf = Icon.cache[value]
        else:
            self._fbuf = FrameBuffer.from_file(value)
            Icon.cache[value] = self._fbuf
        self._icon_width, self._icon_height = self._fbuf.width, self._fbuf.height

    def changed(self):
        """Update the icon when the value (file) changes."""
        self.display.framebuf.fill_rect(*self.padded_area, self.bg)
        self.load_icon(self.value)
        super().changed()

    def draw(self, _=None):
        """
        Draw the icon on the screen.
        """
        pal = FrameBuffer(memoryview(bytearray(4)), 2, 1, RGB565)
        if self.bg is self.parent.theme.transparent:
            key = ~self.fg
            pal.pixel(0, 0, key)
        else:
            key = -1
            pal.pixel(0, 0, self.bg)
        pal.pixel(1, 0, self.fg)
        self.display.framebuf.blit(self._fbuf, self.padded_area.x, self.padded_area.y, key, pal)


class IconButton(Button):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=None, padding=None,
                 icon_file=None):
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
        :param icon_file: The icon file to display on the button.
        """
        fg = fg if fg is not None else parent.fg
        bg = bg if bg is not None else parent.bg
        self.icon = Icon(None, align=ALIGN.CENTER, fg=fg, bg=bg, value=icon_file)
        w = w or self.icon.width
        h = h or self.icon.height
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding)
        self.icon.parent = self


class Toggle(IconButton):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=False, padding=None,
                 on_file=None, off_file=None):
        """
        An IconButton that toggles between two states (on and off).  Serves as a base widget for 
        ToggleButton, CheckBox, and RadioButton widgets but may be used on its own.  Requires an
        on_file and optionally an off_file.  If only a single file is provided, the widget will 
        change colors when toggled.
        
        :param parent: The parent widget or screen that contains this toggle button.
        :param x: The x-coordinate of the toggle button.
        :param y: The y-coordinate of the toggle button.
        :param w: The width of the toggle button (default is 20).
        :param h: The height of the toggle button (default is 20).
        :param fg: The foreground color of the toggle button (default is black).
        :param bg: The background color of the toggle button (default is white).
        :param value: The initial state of the toggle button (default is False, meaning off).
        :param on_file: The icon file to display when the button is toggled on.  Required.
        :param off_file: The icon file to display when the button is toggled off.  Optional.
        """
        if not on_file:
            raise ValueError("An on_file file must be provided.")
        self.on_file = on_file
        self.off_file = off_file
        icon_file = self.off_file if self.off_file and not value else self.on_file
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding, icon_file)
        self.changed()

    def _register_callbacks(self):
        self.add_event_cb(Events.MOUSEBUTTONDOWN, self.toggle)

    def toggle(self, data=None, event=None):
        """Toggle the on/off state of the button."""
        self.value = not self.value  # Invert the current state

    def changed(self):
        """Update the icon based on the current on/off state."""
        # Update the icon value based on the current toggle state
        if self.off_file:
            self.icon.value = self.on_file if self.value else self.off_file
        else:
            self.icon.fg = self.fg if self.value else self.theme.tertiary
        super().changed()  # Call the parent changed method


class ToggleButton(Toggle):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=False, padding=None,
                 size=ICON_SIZE.LARGE):
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
        on_file = ICONS + "toggle_on_" + str(size) + "dp.pbm"
        off_file = ICONS + "toggle_off_" + str(size) + "dp.pbm"
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding, on_file, off_file)


class CheckBox(Toggle):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=False, padding=None,
                 size=ICON_SIZE.LARGE):
        """
        Initialize a CheckBox widget.
        
        :param parent: The parent widget or screen that contains this toggle button.
        :param x: The x-coordinate of the toggle button.
        :param y: The y-coordinate of the toggle button.
        :param w: The width of the toggle button (default is 20).
        :param h: The height of the toggle button (default is 20).
        :param fg: The foreground color of the toggle button (default is black).
        :param bg: The background color of the toggle button (default is white).
        :param value: The initial state of the toggle button (default is False, meaning off).
        """
        on_file = ICONS + "check_box_" + str(size) + "dp.pbm"
        off_file = ICONS + "check_box_outline_blank_" + str(size) + "dp.pbm"
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding, on_file, off_file)


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


class RadioButton(Toggle):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=False, padding=None,
                 size=ICON_SIZE.LARGE, group: RadioGroup=None):
        """
        Initialize a RadioButton widget.
        
        :param parent: The parent widget or screen that contains this toggle button.
        :param x: The x-coordinate of the toggle button.
        :param y: The y-coordinate of the toggle button.
        :param w: The width of the toggle button (default is 20).
        :param h: The height of the toggle button (default is 20).
        :param fg: The foreground color of the toggle button (default is black).
        :param bg: The background color of the toggle button (default is white).
        :param value: The initial state of the toggle button (default is False, meaning off).
        """
        if group is None:
            raise ValueError("RadioButton must be part of a RadioGroup.")
        self.group = group
        self.group.add(self)
        on_file = ICONS + "radio_button_checked_" + str(size) + "dp.pbm"
        off_file = ICONS + "radio_button_unchecked_" + str(size) + "dp.pbm"
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding, on_file, off_file)

    def toggle(self, data=None, event=None):
        """Toggle the checked state to true when clicked and uncheck other RadioButtons in the group."""
        if not self.value:  # Only toggle if not already checked
            self.group.set_checked(self)  # Uncheck all other buttons in the group


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
        w = w or (ICON_SIZE.SMALL if vertical else ICON_SIZE.SMALL * 4)
        h = h or (ICON_SIZE.SMALL if not vertical else ICON_SIZE.SMALL * 4)
        fg = fg if fg is not None else parent.theme.on_primary
        bg = bg if bg is not None else parent.theme.primary_variant
        self.vertical = vertical
        self.reverse = reverse
        self.end_radius = w//2 if self.vertical else h//2
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding)
        self.end_radius = self.padded_area.w//2 if self.vertical else self.padded_area.h//2

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
            w = w or ICON_SIZE.SMALL
            h = h or parent.height if parent else 6 * ICON_SIZE.SMALL
            align = align if align is not None else ALIGN.RIGHT
        else:
            w = w or parent.width if parent else 6 * ICON_SIZE.SMALL
            h = h or ICON_SIZE.SMALL
            align = align if align is not None else ALIGN.BOTTOM
        self.knob_color = knob_color if knob_color is not None else parent.theme.secondary
        self.step = step  # Step size for value adjustments
        self.dragging = False  # Track whether the knob is being dragged
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding, vertical, reverse)
        self.knob_radius = self.end_radius

    def _register_callbacks(self):
        self.add_event_cb(Events.MOUSEBUTTONDOWN, self.event_callback)
        self.add_event_cb(Events.MOUSEBUTTONUP, self.event_callback)
        self.add_event_cb(Events.MOUSEMOTION, self.event_callback)

    def draw(self, _=None):
        """Draw the slider, including the progress bar and the circular knob."""
        super().draw()  # Draw the base progress bar

        # Calculate the position of the knob
        knob_center = self._get_knob_center()

        # Draw the knob as a filled circle with correct radius
        self.display.framebuf.circle(*knob_center, self.knob_radius, self.knob_color, f=True)

    def event_callback(self, data, event):
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
        value = self.value if self.reverse == self.vertical else 1 - self.value
        if self.vertical:
            span = h - w
            knob_y = int(y + value * span) + self.knob_radius
            knob_center = (x + self.knob_radius, knob_y)
        else:
            span = w - h
            knob_x = int(x + value * span) + self.knob_radius
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
            w = w or ICON_SIZE.SMALL
            h = h or parent.height if parent else 6 * ICON_SIZE.SMALL
            align = align if align is not None else ALIGN.RIGHT
            icon_size = w
        else:
            w = w or parent.width if parent else 6 * ICON_SIZE.SMALL
            h = h or ICON_SIZE.SMALL
            align = align if align is not None else ALIGN.BOTTOM
            icon_size = h
        reverse = not reverse if vertical else reverse  # Reverse the direction for vertical sliders
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value, padding)

        # Add IconButton on each end and Slider in the middle
        if vertical:
            self.pos_button = IconButton(self, w=icon_size, h=icon_size, icon_file=ICONS + "keyboard_arrow_up_18dp.pbm", fg=fg, bg=bg, align=ALIGN.TOP)
            self.neg_button = IconButton(self, w=icon_size, h=icon_size, icon_file=ICONS + "keyboard_arrow_down_18dp.pbm", fg=fg, bg=bg, align=ALIGN.BOTTOM)
            self.slider = Slider(self, w=icon_size, h=h-2*icon_size, vertical=True, align=ALIGN.CENTER, value=value, step=step, reverse=reverse, knob_color=knob_color, fg=fg, bg=bg)
        else:
            self.neg_button = IconButton(self, w=icon_size, h=icon_size, icon_file=ICONS + "keyboard_arrow_left_18dp.pbm", fg=fg, bg=bg, align=ALIGN.LEFT)
            self.pos_button = IconButton(self, w=icon_size, h=icon_size, icon_file=ICONS + "keyboard_arrow_right_18dp.pbm", fg=fg, bg=bg, align=ALIGN.RIGHT)
            self.slider = Slider(self, w=w-icon_size*2, h=icon_size, vertical=False, align=ALIGN.CENTER, value=value, step=step, reverse=reverse, knob_color=knob_color, fg=fg, bg=bg)

        # Set button callbacks to adjust slider value
        self.neg_button.add_event_cb(Events.MOUSEBUTTONDOWN, lambda _, e: self.slider.adjust_value(-self.slider.step))
        self.pos_button.add_event_cb(Events.MOUSEBUTTONDOWN, lambda _, e: self.slider.adjust_value(self.slider.step))


class DigitalClock(Label):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, value=None, padding=None,
                 text_height=TEXT_SIZE.LARGE, scale=1):
        """
        Initialize a DigitalClock widget to display the current time.
        
        :param parent: The parent widget or screen that contains this digital clock.
        :param x: The x-coordinate of the digital clock.
        :param y: The y-coordinate of the digital clock.
        :param h: The height of the digital clock.
        :param fg: The color of the text (in a suitable color format).
        :param bg: The background color of the digital clock.
        """
        if text_height not in TEXT_SIZE:
            raise ValueError("Text height must be 8, 14 or 16 pixels.")
        w = w or (TEXT_WIDTH) * 8 * scale
        super().__init__(parent, x, y, w, h, align, align_to, parent.fg, parent.bg, visible, value, padding, text_height, scale)
        self.task = self.display.add_task(self.update_time, 1000)

    def update_time(self):
        if self.visible:
            y, m, d, h, min, sec, *_ = localtime()
            self.value = f"{h:02}:{min:02}:{sec:02}"


class ListView(Widget):
    def __init__(self, parent: Widget, x=0, y=0, w=None, h=None, align=None, align_to=None, fg=None, bg=None, visible=True, padding=None):
        """
        Initialize a ListView widget to display a list of items.
        
        :param parent: The parent widget or screen that contains this list view.
        :param x: The x-coordinate of the list view.
        :param y: The y-coordinate of the list view.
        :param h: The height of the list view.
        :param fg: The color of the text (in a suitable color format).
        :param bg: The background color of the list view.
        """
        fg = fg if fg is not None else parent.theme.on_primary
        bg = bg if bg is not None else parent.theme.primary
        super().__init__(parent, x, y, w, h, align, align_to, fg, bg, visible, value=0, padding=padding)
        self.scrollbar = ScrollBar(parent, vertical=True, h=h, fg=fg, bg=bg, visible=False, align_to=self, align=ALIGN.OUTER_RIGHT)
        self.scrollbar.slider.set_change_cb(self.scroll)

    def add_child(self, child: Widget):
        """Adds a child widget to the current widget."""
        self.children.append(child)
        self.reassign_positions()

    def remove_child(self, child: Widget):
        """Removes a child widget from the current widget."""
        self.children.remove(child)
        self.reassign_positions()

    def reassign_positions(self):
        """Reassign the positions of all children after one is removed."""
        self._value = min(self._value, len(self.children) - 1)
        for i, child in enumerate(self.children):
            child.visible = False
            if i == 0:
                child.set_position(0, 0, self.width, None, align=ALIGN.TOP_LEFT, align_to=self)
            else:
                child.set_position(0, child.height, self.width, None, align=ALIGN.BOTTOM_LEFT, align_to=self.children[i-1])
        self.config_scrollbar()

    def config_scrollbar(self):
        """Configure the scrollbar based on the number of children."""
        if len(self.children) > 1:
            self.scrollbar.slider.step = 1 / (len(self.children) - 1)
        self.changed()

    def scroll(self, sender):
        """Read the value of the scrollbar and scroll the list view accordingly."""
        self.value = int(self.scrollbar.slider.value * (len(self.children)-1))

    def scroll_up(self):
        """Scroll the list view up by one item."""
        self.value -= 1

    def scroll_down(self):
        """Scroll the list view down by one item."""
        self.value += 1

    def changed(self):
        """Update the list view when the value changes."""
        if self.value < 0:
            self._value = 0
        elif self.value >= len(self.children):
            self._value = len(self.children) - 1

        for child in self.children:
            child.visible = False

        sb_visible = False
        if len(self.children):
            self.children[0].y = -sum([child.height for child in self.children[:self.value]])
            for child in self.children:
                if self.area.contains_area(child.area):
                    child.visible = True
                else:
                    sb_visible = True
        self.scrollbar.visible = sb_visible
        if sb_visible:
            self.scrollbar.slider.value = self.value / (len(self.children) - 1)
        super().changed()
