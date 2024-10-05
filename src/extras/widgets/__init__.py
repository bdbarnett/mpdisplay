from gfx import Area
from eventsys.events import Events
from micropython import const
import png
from palettes.shades import ShadesPalette
from time import time, localtime
from gfx.framebuf_plus import FrameBuffer, RGB565
from palettes import get_palette
import sys
from random import getrandbits
# from tft_text import text

# try:
#     from os import sep  # PyScipt doesn't have os.sep
# except ImportError:
#     sep = "/"
# font_dir = ".".join(text.__globals__["__file__"].split(sep)[:-1]) + ".fonts"
# # font_dir = sep.join(tft_text.__file__.split(sep)[:-1]) + sep + "fonts"
# print(f"font_dir: {font_dir}")
# _default_font = "vga1_8x16"


DEBUG = False
MARK_UPDATES = True


def log(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def name(obj):
    return obj.__class__.__name__

def drawing(obj):
    return f"{name(obj)} drawing at {obj.area}"

BLACK = const(0)
WHITE = const(-1)

DEFAULT_ICON_SIZE = const(36)
DEFAULT_TEXT_HEIGHT = const(16)
TEXT_WIDTH = const(8)
TEXT_HEIGHTS = (8, 14, 16)


_display_drv_get_attrs = {"set_vscroll", "tfa", "bfa", "vsa", "vscroll", "tfa_area", "bfa_area", "vsa_area",}
_display_drv_set_attrs = {"vscroll"}


def tick(_=None):
    for display in Display.displays:
        display.tick()

timer = None
def get_timer():
    global timer
    if timer:
        print("Widgets:  timer already started")
    else:
        from timer import Timer
        timer = Timer(-1 if sys.platform == "rp2" else 1)
        timer.init(mode=Timer.PERIODIC, period=20, callback=tick)
        print("Widgets:  timer started")
    return timer

def stop_timer():
    global timer
    if timer:
        timer.deinit()
        timer = None
        print("Widgets:  timer disabled")
    else:
        print("Widgets:  timer already disabled")

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


class event:
    NONE = const(0)
    PRESS = const(1 << 0)
    RELEASE = const(2 << 1)
    ANY = PRESS | RELEASE


class Display:
    displays = []

    @classmethod
    def quit(cls):
        for display in cls.displays:
            display.display_drv.deinit()
        try:
            stop_timer()
        except Exception:
            pass
        sys.exit()

    # @classmethod
    # def load_font(cls, font_name=_default_font):
    #     print(f"Loading font: {font_name} from {font_dir}")
    #     font_module = __import__(font_dir + "." + font_name, globals(), locals(), [font_name], 0)
    #     setattr(cls, font_name, font_module)
    #     print(f"Loaded font: {font_module=}; {dir(font_module)=}")

    def __init__(self, display_drv, broker, start_timer=False, format=RGB565):
        self.display_drv = display_drv
        display_drv.vscrdef(0, display_drv.height, 0)
        self.broker = broker
        broker.quit_func = self.quit
        self._buffer = memoryview(bytearray(display_drv.width * display_drv.height * display_drv.color_depth // 8))
        self.framebuf = FrameBuffer(self._buffer, display_drv.width, display_drv.height, format)
        if display_drv.requires_byte_swap:
            self.needs_swap = display_drv.disable_auto_byte_swap(True)
        else:
            self.needs_swap = False
        self.pal = get_palette(swapped=self.needs_swap, color_depth=display_drv.color_depth)
        self._active_screen: Screen = None
        self._tasks = []
        Display.displays.append(self)
        self.add_task(self.display_drv.show, 0.033)
        if start_timer and timer is None:
            get_timer()

    def tick(self):
        t = time()
        if e := self.broker.poll():
            if e.type in Events.filter:
                if self._active_screen is not None:
                    self._active_screen.handle_event(e)
        for task in self._tasks:
            if t >= task.next_run:
                task.run(t)

    def add_child(self, screen):
        self.active_screen = screen

    def add_task(self, callback, delay):
        new_task = Task(callback, delay)
        self._tasks.append(new_task)
        return new_task

    def remove_task(self, task):
        self._tasks.remove(task)

    def get_point(self, pos):
        return self.display_drv.translate_point(pos)

    @property
    def active_screen(self):
        return self._active_screen
    
    @active_screen.setter
    def active_screen(self, screen):
        self._active_screen = screen

    def update(self, area):
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

    @property
    def display(self):
        return self

    @property
    def parent(self):
        return None

    @property
    def x(self):
        return 0
    
    @property
    def y(self):
        return 0
    
    @property
    def width(self):
        return self.display_drv.width
    
    @property
    def height(self):
        return self.display_drv.height
    
    @property
    def visible(self):
        return True

    def __getattr__(self, name):
        if name in _display_drv_get_attrs:
            return getattr(self.display_drv, name)
        raise AttributeError(f"{self.__class__.__name__} object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in _display_drv_set_attrs:
            return setattr(self.display_drv, name, value)
        super().__setattr__(name, value)


class Task:
    def __init__(self, callback, delay):
        self.callback = callback
        self.delay = delay
        self.next_run = time() + delay

    def run(self, t):
        self.callback()
        self.next_run = t + self.delay


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
        self.parent: Widget | Display = parent
        self._x = x
        self._y = y
        self._w = w or parent.width
        self._h = h or parent.height
        self.fg = fg  # Foreground color of the widget
        self.bg = bg  # Background color of the widget
        self._value = value  # Value of the widget (e.g., text of a label)
        self._visible = visible
        self.children: list[Widget] = []
        self.on_change_callback = None
        self.on_press_callback = None
        self.on_release_callback = None
        self.align = align if align is not None else ALIGN.TOP_LEFT  # default to align.TOP_LEFT
        self.align_to: Widget = align_to or parent

        self.parent.add_child(self)
        self.render()

    def draw(self, area=None):
        """
        Draw the widget on the screen.  Subclasses should override this method to draw the widget unless the widget is
        a container widget (like a screen) that contains other widgets.  Subclasses may call this method to draw the
        background of the widget before drawing other elements.
        """
        print(f"Drawing {area} with {self.fg=}, {self.bg=}")
        if self.bg is not None:
            if area:
                self.display.framebuf.fill_rect(*area, self.bg)
            else:
                self.display.framebuf.fill_rect(*self.area, self.bg)

    def handle_event(self, event):
        """
        Handle an event and propagate it to child widgets.  Subclasses that need to handle events
        should override this method and call this method to propagate the event to children.
        
        :param event: An event from the event system (e.g., mouse or keyboard event).
        """
        # log(f"{name(self)}.handle_event({event})")
        # Propagate the event to the children of the screen
        for child in self.children:
            child.handle_event(event)

    @property
    def x(self):
        """Calculate the absolute x-coordinate of the widget based on align
        """
        align = self.align
        align_to = self.align_to

        x = align_to.x + self._x

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
        align_to = self.align_to

        y = align_to.y + self._y

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
    
    @x.setter
    def x(self, x):
        self._x = x

    @y.setter
    def y(self, y):
        self._y = y

    @property
    def width(self):
        return self._w

    @width.setter
    def width(self, w):
        self._w = w

    @property
    def height(self):
        return self._h

    @height.setter
    def height(self, h):
        self._h = h

    @property
    def area(self):
        """
        Get the absolute area of the widget on the screen.

        :return: An Area object representing the absolute area.
        """

        return Area(self.x, self.y, self.width, self.height)

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        if value != self._value:
            self._value = value
            self.changed()

    def changed(self):
        """Called when the value of the widget changes.  May be overridden in subclasses.
        If overridden, the subclass should call this method to trigger the on_change_callback.
        """
        if self.on_change_callback:
            self.on_change_callback(self)
        self.render()

    def set_value(self, value):
        self.value = value

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
                self.render()
            else:
                self._visible = False
                self.parent.draw(self.area)
                self.display.update(self.area)

    def hide(self, hide=True):
        self.visible = not hide

    @property
    def display(self):
        return self.parent.display
    
    def add_child(self, widget):
        """Adds a child widget to the current widget."""
        log(f"{name(self)}.add_child({name(widget)})")
        self.children.append(widget)

    def remove_child(self, widget):
        """Removes a child widget from the current widget."""
        self.children.remove(widget)

    def render(self, show=True):
        if self.visible:
            log(f"{drawing(self)}, show={show}")
            self.draw()
            for child in self.children:
                child.render(show=False)
            if show:
                log(f"Showing {self.area}\n")
                self.display.update(self.area)

    def set_on_press(self, callback):
        """Set the callback function for when the button is pressed."""
        self.on_press_callback = callback

    def set_on_release(self, callback):
        """Set the callback function for when the button is released."""
        self.on_release_callback = callback

    def set_on_change(self, callback):
        """Set the callback function for when the value of the widget changes."""
        self.on_change_callback = callback


class Screen(Widget):
    def __init__(self, parent: Display | Widget, color=BLACK, visible=True):
        """
        Initialize a Screen widget, which acts as the top-level container for a Display.
        
        :param display: The Display object that this Screen is associated with.
        """
        super().__init__(parent, 0, 0, parent.width, parent.height, color, color, visible)


class Button(Widget):
    def __init__(self, parent: Widget, x=0, y=0, w=DEFAULT_ICON_SIZE, h=DEFAULT_ICON_SIZE, fg=None, bg=None, visible=True, align=None, align_to=None, value=None,
                 filled=True, radius=0, pressed_offset=1, pressed=False,
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
        self.filled = filled
        self.radius = radius
        self.pressed_offset = pressed_offset
        self._pressed = pressed
        fg = fg if fg is not None else BLACK
        bg = bg if bg is not None else WHITE
        super().__init__(parent, x, y, w, h, fg, bg, visible, align, align_to, value)
        if label:
            if label_height not in TEXT_HEIGHTS:
                raise ValueError("Text height must be 8, 14 or 16 pixels.")
            self.label = Label(self, value=label, fg=label_color or self.bg, h=label_height)
        else:
            self.label = None

    def draw(self):
        """
        Draw the button background and any child widgets (like a label).
        """
        # Adjust size if the button is pressed
        draw_area = self.area
        if self._pressed:
            if self.bg is not None:
                self.display.framebuf.fill_rect(*draw_area, self.bg)
            draw_area = Area(
                draw_area.x + self.pressed_offset,
                draw_area.y + self.pressed_offset,
                draw_area.w - self.pressed_offset * 2,
                draw_area.h - self.pressed_offset * 2,
            )
        self.display.framebuf.round_rect(*draw_area, self.radius, self.fg, f=self.filled)

    def handle_event(self, event: Events.Any):
        """
        Handle user input events like clicks.

        :param event: An event from the event system (e.g., mouse click).
        """
        # log(f"{name(self)}.handle_event({event})")

        was_pressed = self._pressed
        if self.area.contains(self.display.get_point(event.pos)) and event.type == Events.MOUSEBUTTONDOWN:
            self._pressed = True
            if self.on_press_callback:
                self.on_press_callback(self)
        elif self._pressed and event.type == Events.MOUSEBUTTONUP:
            self._pressed = False
            if self.on_release_callback:
                self.on_release_callback(self)
        if was_pressed != self._pressed:
            self.render()

        # Propagate the event to the children of the button
        super().handle_event(event)


class Label(Widget):
    def __init__(self, parent: Widget, x=0, y=0, h=DEFAULT_TEXT_HEIGHT, fg=WHITE, bg=None,
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
        super().__init__(parent, x, y, len(value) * TEXT_WIDTH*scale, h*scale, fg, bg, visible, align, align_to, value)
        # bg = bg or parent.fg
        # font = font or _default_font
        # if not hasattr(parent.display, font):
        #     parent.display.load_font(font)
        # self.font = getattr(parent.display, font)
        # super().__init__(parent, x, y, self.font.WIDTH * len(value), self.font.HEIGHT, fg, bg, visible, value)

    def draw(self):
        """
        Draw the label's text on the screen, using absolute coordinates.
        Optionally fills the background first if `bg` is set.
        """
        if self.bg is not None:
            self.display.framebuf.fill_rect(*self.area, self.bg)  # Draw background if bg is specified
        x, y, _, _ = self.area
        self.display.framebuf.text(self.value, x, y, self.fg, height=self.height // self._scale,
                                   scale=self._scale, inverted=self._inverted, font_file=self._font_file)
        # text(self.display.framebuf, self.font, self.value, x, y, self.fg, self.bg)


class TextBox(Widget):
    def __init__(self, parent: Widget, x=0, y=0, w=64, h=None, fg=BLACK, bg=WHITE,
                 visible=True, align=None, align_to=None, value="", margin=1,
                 text_height=DEFAULT_TEXT_HEIGHT, scale=1, inverted=False, font_file=None):
                #  font=None):
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
        # font = font or _default_font
        # if not hasattr(parent.display, font):
        #     parent.display.load_font(font)
        # self.font = getattr(parent.display, font)
        # h = h or self.font.HEIGHT + 2 * margin
        if text_height not in TEXT_HEIGHTS:
            raise ValueError("Text height must be 8, 14 or 16 pixels.")
        self.text_height = text_height
        h = h or text_height * scale + 2 * margin
        super().__init__(parent, x, y, w, h, fg, bg, visible, align, align_to, value)

    def draw(self):
        """
        Draw the label's text on the screen, using absolute coordinates.
        """
        self.display.framebuf.fill_rect(*self.area, self.bg)
        self.display.framebuf.text(self.value, self.x+self.margin, self.y+self.margin, self.fg, height=self.text_height,
                                   scale=self._scale, inverted=self._inverted, font_file=self._font_file)
        # text(self.display.framebuf, self.font, self.value, self.x+self.margin, self.y+self.margin, self.fg, self.bg)


class ProgressBar(Widget):
    def __init__(self, parent: Widget, x=0, y=0, w=64, h=DEFAULT_ICON_SIZE, fg=BLACK, bg=WHITE,
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
        super().__init__(parent, x, y, w, h, fg, bg, visible, align, align_to, value)

    def draw(self):
        """
        Draw the progress bar on the screen.
        """
        self.display.framebuf.fill_rect(*self.area, self.bg)

        if self.value == 0:
            return  # Nothing more to draw if value is 0

        if self.vertical:
            # Calculate the height of the filled part
            progress_height = int(self.value * self.height)
            if self.reverse:
                # Fill from top to bottom
                self.display.framebuf.fill_rect(self.x, self.y, self.width, progress_height, self.fg)
            else:
                # Fill from bottom to top (default)
                self.display.framebuf.fill_rect(self.x, self.y + self.height - progress_height, self.width, progress_height, self.fg)
        else:
            # Calculate the width of the filled part
            progress_width = int(self.value * self.width)
            if self.reverse:
                # Fill from right to left
                self.display.framebuf.fill_rect(self.x + self.width - progress_width, self.y, progress_width, self.height, self.fg)
            else:
                # Fill from left to right (default)
                self.display.framebuf.fill_rect(self.x, self.y, progress_width, self.height, self.fg)

    def changed(self):
        # Ensure value is between 0 and 1
        if self.value < 0:
            self.value = 0
        elif self.value > 1:
            self.value = 1
        super().changed()


class Icon(Widget):
    def __init__(self, parent: Widget, x=0, y=0, fg=WHITE, bg=None, visible=True, align=None, align_to=None, value=None):
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
        fg = fg if fg is not None else WHITE
        bg = bg if bg is not None else parent.fg
        super().__init__(parent, x, y, self.icon_width, self.icon_height, fg, bg, visible, align, align_to, value)

    def load_icon(self, value):
        """Load icon file and store pixel data."""
        self.icon_width, self.icon_height, self._pixels, self._metadata = png.Reader(filename=value).read_flat()
        if not self._metadata["greyscale"] or self._metadata['bitdepth'] != 8:
            raise ValueError(f"Only 8-bit greyscale PNGs are supported {self.value}")

    def changed(self):
        """Update the icon when the value (file) changes."""
        self.load_icon(self.value)
        super().changed()

    def draw(self):
        """
        Draw the icon on the screen.
        """
        pal = ShadesPalette(color=self.fg)
        alpha = 1 if self._metadata["alpha"] else 0
        planes = self._metadata["planes"]
        pixels = self._pixels
        pos_x, pos_y, w, h = self.area
        for y in range(0, h):
            for x in range(0, w):
                if (c := pixels[(y * w + x) * planes + alpha]) != 0:
                    self.display.framebuf.pixel(pos_x + x, pos_y + y, pal[c])


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
        bg = bg if bg is not None else BLACK
        super().__init__(parent, x, y, w, h, bg, fg, visible, align, align_to, value)
        self.icon = Icon(self, fg=fg, bg=bg, value=icon)


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
        self.on_icon = "icons/36dp/check_box_36dp.png"
        self.off_icon = "icons/36dp/check_box_outline_blank_36dp.png"
        
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
        if self.area.contains(self.display.get_point(event.pos)) and event.type == Events.MOUSEBUTTONDOWN:
            self.toggle()
        Widget.handle_event(self, event)  # Propagate to children if necessary


class ToggleButton(IconButton):
    def __init__(self, parent, x=0, y=0, w=DEFAULT_ICON_SIZE, h=DEFAULT_ICON_SIZE, fg=BLACK, bg=WHITE,
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
        self.on_icon = "icons/36dp/toggle_on_36dp.png"
        self.off_icon = "icons/36dp/toggle_off_36dp.png"

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
        if self.area.contains(self.display.get_point(event.pos)) and event.type == Events.MOUSEBUTTONDOWN:
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
    def __init__(self, parent, group: RadioGroup, x=0, y=0, w=DEFAULT_ICON_SIZE, h=DEFAULT_ICON_SIZE, fg=BLACK, bg=WHITE,
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
        self.on_icon = "icons/36dp/radio_button_checked_36dp.png"
        self.off_icon = "icons/36dp/radio_button_unchecked_36dp.png"

        # Set initial icon based on the value (checked state)
        icon = self.on_icon if value else self.off_icon

        # Store the checked state in the value attribute
        self.group = group
        self.group.add(self)
        
        super().__init__(parent, x, y, w, h, fg, bg, visible, align, align_to, value, icon)

    def toggle(self):
        """Toggle the checked state to true when clicked and uncheck other RadioButtons in the group."""
        if not self.value:  # Only toggle if not already checked
            self.value = True  # A radio button is always checked when clicked
            self.group.set_checked(self)  # Uncheck all other buttons in the group

    def changed(self):
        """Update the icon based on the current checked state."""
        # Update the icon value based on the current checked state
        self.icon.value = self.on_icon if self.value else self.off_icon
        super().changed()  # Call the parent changed method

    def handle_event(self, event):
        """Override handle_event to toggle the RadioButton when clicked."""
        if self.area.contains(self.display.get_point(event.pos)) and event.type == Events.MOUSEBUTTONDOWN:
            self.toggle()  # Toggle the state when clicked
        Widget.handle_event(self, event)  # Propagate to children if necessary


class Slider(ProgressBar):
    def __init__(self, parent, x=0, y=0, w=100, h=DEFAULT_ICON_SIZE, fg=BLACK, bg=WHITE, visible=True,
                 align=None, align_to=None, value=0.5, vertical=False, reverse=False, knob_color=BLACK, step=0.1):
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
        self.knob_radius = (w if vertical else h) // 2  # Halve the radius to fix size
        self.knob_color = knob_color  # Color of the knob
        self.step = step  # Step size for value adjustments
        super().__init__(parent, x, y, w, h, fg, bg, visible, align, align_to, value, vertical, reverse)

    def draw(self):
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
                    relative_pos = (self.display.get_point(event.pos)[1] - self.y) / self.height
                    self.value = 1 - max(0, min(1, relative_pos))
                else:
                    relative_pos = (self.display.get_point(event.pos)[0] - self.x) / self.width
                    self.value = max(0, min(1, relative_pos))
        elif self._point_in_knob(self.display.get_point(event.pos)) and event.type == Events.MOUSEBUTTONDOWN:
            self.dragging = True
        elif self.area.contains(self.display.get_point(event.pos)) and event.type == Events.MOUSEBUTTONDOWN:
            # Clicking outside the knob moves the slider by one step
            if self.vertical:
                if self.display.get_point(event.pos)[1] < self._get_knob_center()[1]:
                    self._adjust_value_by_step('down')
                elif self.display.get_point(event.pos)[1] > self._get_knob_center()[1]:
                    self._adjust_value_by_step('up')
            else:
                if self.display.get_point(event.pos)[0] < self._get_knob_center()[0]:
                    self._adjust_value_by_step('left')
                elif self.display.get_point(event.pos)[0] > self._get_knob_center()[0]:
                    self._adjust_value_by_step('right')

        super().handle_event(event)

    def _get_knob_center(self):
        """Calculate the center coordinates for the knob based on the current value."""
        x, y, w, h = self.area
        if self.vertical:
            # Knob moves along the vertical axis, center the knob horizontally
            knob_y = int(y + (1 - self.value) * h)
            knob_center = (x + w // 2, knob_y)
        else:
            # Knob moves along the horizontal axis, center the knob vertically
            knob_x = int(x + self.value * w)
            knob_center = (knob_x, y + h // 2)
        return knob_center

    def _point_in_knob(self, pos):
        """Check if the given point is within the knob's circular area."""
        knob_center = self._get_knob_center()
        distance = ((pos[0] - knob_center[0]) ** 2 + (pos[1] - knob_center[1]) ** 2) ** 0.5
        return distance <= self.knob_radius

    def _adjust_value_by_step(self, direction):
        """Adjust the slider value by one step in the specified direction."""
        new_value = self.value
        if self.vertical:
            if direction == 'up':
                new_value = min(1, self.value + self.step)
            elif direction == 'down':
                new_value = max(0, self.value - self.step)
        else:
            if direction == 'right':
                new_value = min(1, self.value + self.step)
            elif direction == 'left':
                new_value = max(0, self.value - self.step)
        if new_value != self.value:
            self.value = new_value


class DigitalClock(TextBox):
    def __init__(self, parent, x=0, y=0, h=DEFAULT_TEXT_HEIGHT, fg=WHITE, bg=None, visible=True, align=None, align_to=None):
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
        self.task = self.display.add_task(self.update, 1)

    def update(self):
        y, m, d, h, min, sec, *_ = localtime()
        self.value = f"{h:02}:{min:02}:{sec:02}"
