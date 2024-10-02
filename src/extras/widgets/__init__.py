from gfx import Area, Draw
from eventsys.events import Events
from micropython import const
import png
from palettes.shades import ShadesPalette
from time import time, localtime
from displaybuf import DisplayBuffer
from palettes import get_palette
import sys

DEBUG = False


def log(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def name(obj):
    return obj.__class__.__name__

def drawing(obj):
    return f"{name(obj)} drawing at {obj.abs_area}"

_black = const(0)
_white = const(-1)

default_icon_size = const(36)
_default_text_height = const(16)
_text_width = const(8)
_text_heights = (8, 14, 16)


class Display:
    displays = []
    _timer = None
    use_timer = False

    @classmethod
    def _tick(cls, mode):
        for display in cls.displays:
            display.tick()
        if cls._timer:
            cls._timer.init(mode=mode, period=10, callback=lambda t: cls._tick(mode))

    @classmethod
    def start_timer(cls):
        if cls._timer:
            print("Display:  timer already enabled")
            return
        
        if cls.use_timer:
            from timer import Timer
            cls._timer = Timer(-1 if sys.platform == "rp2" else 1)
            cls._tick(Timer.ONE_SHOT)
            print("Display:  timer enabled")
            return
        
        print("Display:  timer not enabled")

    @classmethod
    def stop_timer(cls):
        if cls._timer:
            cls._timer = None
            print("Display:  timer disabled")
        else:
            print("Display:  timer not enabled")

    def __init__(self, display_drv, broker, use_timer=None):
        self.display_drv = display_drv
        self.broker = broker
        self.display_buf = DisplayBuffer(display_drv)
        self.draw_buf = Draw(self.display_buf)
        self.pal = get_palette(swapped=self.display_buf.needs_swap, color_depth=self.display_buf.color_depth)
        self._active_screen: Screen = None
        self._last_refresh = time()
        self._tasks = []
        if use_timer is not None:
            Display.use_timer = use_timer
        Display.displays.append(self)
        Display.start_timer()

    def tick(self):
        t = time()
        for task in self._tasks:
            if t >= task.next_run:
                task.run()
        if e := self.broker.poll():
            if e.type in Events.filter:
                if self._active_screen is not None:
                    self._active_screen.handle_event(e)
        if t - self._last_refresh > .033:
            self._last_refresh = t
            self.display_drv.show()

    def add_child(self, screen):
        self.active_screen = screen

    def add_task(self, callback, delay):
        new_task = Task(callback, delay)
        self._tasks.append(new_task)
        return new_task

    def remove_task(self, task):
        self._tasks.remove(task)

    @property
    def active_screen(self):
        return self._active_screen
    
    @active_screen.setter
    def active_screen(self, screen):
        self._active_screen = screen

    @property
    def show(self):
        return self.display_buf.show

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
        return self.display_buf.width
    
    @property
    def height(self):
        return self.display_buf.height
    
    @property
    def visible(self):
        return True


class Task:
    def __init__(self, callback, delay):
        self.callback = callback
        self.delay = delay
        self.next_run = time() + delay

    def run(self):
        self.callback()
        self.next_run = time() + self.delay


class Widget:
    def __init__(self, parent, x, y, w=0, h=0, fg=_white, bg=_black, visible=True, value=None):
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
        """
        self.parent: Widget | Display = parent
        self._x = x if x is not None else (self.parent.width - w) // 2
        self._y = y if y is not None else (self.parent.height - h) // 2
        self._w = w
        self._h = h
        self.fg = fg  # Foreground color of the widget
        self.bg = bg  # Background color of the widget
        self._value = value  # Value of the widget (e.g., text of a label)
        self._visible = visible
        self.children: list[Widget] = []
        self.on_change_callback = None
        self.on_press_callback = None
        self.on_release_callback = None

        self.parent.add_child(self)
        self.render()

    def draw(self):
        """
        Placeholder for the actual drawing logic of the widget.
        Should be overridden in subclasses.
        """
        log(f"{name(self)} has not overridden draw method.")
        pass

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
    def area(self):
        return Area(0, 0, self._w, self._h)
    
    @property
    def rel_area(self):
        """
        Returns the area of the widget relative to its parent's area.
        """
        return Area(self._x, self._y, self._w, self._h)

    @property
    def abs_area(self):
        """
        Get the absolute area of the widget on the screen.

        :return: An Area object representing the absolute area.
        """
        x = self._x
        y = self._y
        parent = self.parent

        # Traverse up the hierarchy and sum the offsets
        while parent is not None:
            x += parent.x
            y += parent.y
            parent = parent.parent

        return Area(x, y, self._w, self._h)

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        if value != self._value:
            self._value = value
            self.value_changed()

    def value_changed(self):
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
                log(f"Showing {self.abs_area}\n")
                self.display.show(self.abs_area)

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
    def __init__(self, parent: Display | Widget, color=_black, visible=True):
        """
        Initialize a Screen widget, which acts as the top-level container for a Display.
        
        :param display: The Display object that this Screen is associated with.
        """
        super().__init__(parent, 0, 0, parent.width, parent.height, color, color, visible)

    def draw(self):
        """
        Draw the screen and its children.
        """
        self.display.draw_buf.fill_rect(*self.area, self.bg)


class Button(Widget):
    def __init__(self, parent: Widget, x=None, y=None, w=default_icon_size, h=default_icon_size, fg=_white, visible=True, value=None,
                 filled=True, radius=0, pressed_offset=1, pressed=False,
                 label=None, label_color=None, label_height=_default_text_height):
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
        super().__init__(parent, x, y, w, h, fg, parent.bg, visible, value)
        if label:
            if label_height not in _text_heights:
                raise ValueError("Text height must be 8, 14 or 16 pixels.")
            self.label = Label(self, value=label, fg=label_color or self.bg, h=label_height)
        else:
            self.label = None

    def draw(self):
        """
        Draw the button background and any child widgets (like a label).
        """
        # Adjust size if the button is pressed
        draw_area = self.abs_area
        if self._pressed:
            self.display.draw_buf.fill_rect(*draw_area, self.bg)
            draw_area = Area(
                draw_area.x + self.pressed_offset,
                draw_area.y + self.pressed_offset,
                draw_area.w - self.pressed_offset * 2,
                draw_area.h - self.pressed_offset * 2,
            )
        self.display.draw_buf.round_rect(*draw_area, self.radius, self.fg, f=self.filled)

    def handle_event(self, event: Events.Any):
        """
        Handle user input events like clicks.

        :param event: An event from the event system (e.g., mouse click).
        """
        # log(f"{name(self)}.handle_event({event})")

        if self.abs_area.contains(event.pos) and event.type == Events.MOUSEBUTTONDOWN:
            self._pressed = True
            self.render()
            if self.on_press_callback:
                self.on_press_callback(self)
        elif self._pressed and event.type == Events.MOUSEBUTTONUP:
            self._pressed = False
            self.render()
            if self.on_release_callback:
                self.on_release_callback(self)

        # Propagate the event to the children of the button
        super().handle_event(event)


class Label(Widget):
    def __init__(self, parent: Widget, x=None, y=None, h=_default_text_height, fg=_white, bg=None,
                 visible=True, value=""):
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
        if h not in _text_heights:
            raise ValueError("Text height must be 8, 14 or 16 pixels.")
        super().__init__(parent, x, y, len(value) * _text_width, h, fg, bg, visible, value)

    def draw(self):
        """
        Draw the label's text on the screen, using absolute coordinates.
        Optionally fills the background first if `bg` is set.
        """
        if self.bg is not None:
            self.display.draw_buf.fill_rect(*self.abs_area, self.bg)  # Draw background if bg is specified
        x, y, _, _ = self.abs_area
        self.display.draw_buf.text(self.value, x, y, self.fg, height=self.height)


class TextBox(Widget):
    def __init__(self, parent: Widget, x=None, y=None, w=64, h=None, fg=_black, bg=_white,
                 visible=True, value="", text_height=_default_text_height, margin=1):
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
        if text_height not in _text_heights:
            raise ValueError("Text height must be 8, 14 or 16 pixels.")
        self.text_height = text_height
        self.margin = margin
        h = h or text_height + 2 * margin
        super().__init__(parent, x, y, w, h, fg, bg, visible, value)

    def draw(self):
        """
        Draw the label's text on the screen, using absolute coordinates.
        """
        self.display.draw_buf.fill_rect(*self.abs_area, self.bg)
        self.display.draw_buf.text(self.value, self.x+self.margin, self.y+self.margin, self.fg, height=self.text_height)


class ProgressBar(Widget):
    def __init__(self, parent: Widget, x=None, y=None, w=64, h=default_icon_size, fg=_black, bg=_white,
                 visible=True, value=0.5, vertical=False, reverse=False):
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
        super().__init__(parent, x, y, w, h, fg, bg, visible, value)

    def draw(self):
        """
        Draw the progress bar on the screen.
        """
        self.display.draw_buf.fill_rect(*self.abs_area, self.bg)

        if self.value == 0:
            return  # Nothing more to draw if value is 0

        if self.vertical:
            # Calculate the height of the filled part
            progress_height = int(self.value * self.height)
            if self.reverse:
                # Fill from top to bottom
                self.display.draw_buf.fill_rect(self.x, self.y, self.width, progress_height, self.fg)
            else:
                # Fill from bottom to top (default)
                self.display.draw_buf.fill_rect(self.x, self.y + self.height - progress_height, self.width, progress_height, self.fg)
        else:
            # Calculate the width of the filled part
            progress_width = int(self.value * self.width)
            if self.reverse:
                # Fill from right to left
                self.display.draw_buf.fill_rect(self.x + self.width - progress_width, self.y, progress_width, self.height, self.fg)
            else:
                # Fill from left to right (default)
                self.display.draw_buf.fill_rect(self.x, self.y, progress_width, self.height, self.fg)

    def value_changed(self):
        # Ensure value is between 0 and 1
        if self.value < 0:
            self.value = 0
        elif self.value > 1:
            self.value = 1
        super().value_changed()


class Icon(Widget):
    def __init__(self, parent: Widget, x=None, y=None, fg=_white, bg=None, visible=True, value=None):
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
        bg = bg or parent.fg
        super().__init__(parent, x, y, self.icon_width, self.icon_height, fg, bg, visible, value)

    def load_icon(self, value):
        """Load icon file and store pixel data."""
        self.icon_width, self.icon_height, self._pixels, self._metadata = png.Reader(filename=value).read_flat()
        if not self._metadata["greyscale"] or self._metadata['bitdepth'] != 8:
            raise ValueError(f"Only 8-bit greyscale PNGs are supported {self.value}")

    def value_changed(self):
        """Update the icon when the value (file) changes."""
        self.load_icon(self.value)
        super().value_changed()

    def draw(self):
        """
        Draw the icon on the screen.
        """
        pal = ShadesPalette(color=self.fg)
        alpha = 1 if self._metadata["alpha"] else 0
        planes = self._metadata["planes"]
        pixels = self._pixels
        pos_x, pos_y, w, h = self.abs_area
        for y in range(0, h):
            for x in range(0, w):
                if (c := pixels[(y * w + x) * planes + alpha]) != 0:
                    self.display.draw_buf.pixel(pos_x + x, pos_y + y, pal[c])


class IconButton(Button):
    def __init__(self, parent: Widget, x=None, y=None, w=default_icon_size, h=default_icon_size, fg=_black, bg=_white,
                 visible=True, value=None, icon=None):
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
        super().__init__(parent, x, y, w, h, bg, visible, value)
        self.icon = Icon(self, fg=fg, bg=bg, value=icon)


class CheckBox(IconButton):
    def __init__(self, parent, x=None, y=None, w=default_icon_size, h=default_icon_size, fg=_black, bg=_white,
                 visible=True, value=False):
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
        super().__init__(parent, x, y, w, h, fg, bg, visible, value, icon)
        
    def toggle(self):
        """Toggle the checked state when the checkbox is pressed."""
        self.value = not self.value  # Toggle the boolean value

    def value_changed(self):
        """Update the icon based on the current checked state."""
        self.icon.value = self.on_icon if self.value else self.off_icon
        super().value_changed()  # Call the parent value_changed method

    def handle_event(self, event):
        """Override handle_event to toggle the CheckBox when clicked."""
        if self.abs_area.contains(event.pos) and event.type == Events.MOUSEBUTTONDOWN:
            self.toggle()
        Widget.handle_event(self, event)  # Propagate to children if necessary


class ToggleButton(IconButton):
    def __init__(self, parent, x=None, y=None, w=default_icon_size, h=default_icon_size, fg=_black, bg=_white,
                 visible=True, value=False):
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
        
        super().__init__(parent, x, y, w, h, fg, bg, visible, value, icon)

    def toggle(self):
        """Toggle the on/off state of the button."""
        self.value = not self.value  # Invert the current state

    def value_changed(self):
        """Update the icon based on the current on/off state."""
        # Update the icon value based on the current toggle state
        self.icon.value = self.on_icon if self.value else self.off_icon
        super().value_changed()  # Call the parent value_changed method

    def handle_event(self, event):
        """Override handle_event to toggle the button when clicked."""
        if self.abs_area.contains(event.pos) and event.type == Events.MOUSEBUTTONDOWN:
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
    def __init__(self, parent, group: RadioGroup, x=None, y=None, w=default_icon_size, h=default_icon_size, fg=_black, bg=_white,
                 visible=True, value=False):
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
        
        super().__init__(parent, x, y, w, h, fg, bg, visible, value, icon)

    def toggle(self):
        """Toggle the checked state to true when clicked and uncheck other RadioButtons in the group."""
        if not self.value:  # Only toggle if not already checked
            self.value = True  # A radio button is always checked when clicked
            self.group.set_checked(self)  # Uncheck all other buttons in the group

    def value_changed(self):
        """Update the icon based on the current checked state."""
        # Update the icon value based on the current checked state
        self.icon.value = self.on_icon if self.value else self.off_icon
        super().value_changed()  # Call the parent value_changed method

    def handle_event(self, event):
        """Override handle_event to toggle the RadioButton when clicked."""
        if self.abs_area.contains(event.pos) and event.type == Events.MOUSEBUTTONDOWN:
            self.toggle()  # Toggle the state when clicked
        Widget.handle_event(self, event)  # Propagate to children if necessary


class Slider(ProgressBar):
    def __init__(self, parent, x=None, y=None, w=100, h=default_icon_size, fg=_black, bg=_white, visible=True,
                 value=0.5, vertical=False, reverse=False, knob_color=_black, step=0.1):
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
        super().__init__(parent, x, y, w, h, fg, bg, visible, value, vertical, reverse)

    def draw(self):
        """Draw the slider, including the progress bar and the circular knob."""
        super().draw()  # Draw the base progress bar

        # Calculate the position of the knob
        knob_center = self._get_knob_center()

        # Draw the knob as a filled circle with correct radius
        self.display.draw_buf.circle(*knob_center, self.knob_radius, self.knob_color, f=True)

    def handle_event(self, event):
        """Handle user input events like clicks, dragging, and mouse movements."""
        if self.dragging:
            if event.type == Events.MOUSEBUTTONUP:
                self.dragging = False
            elif event.type == Events.MOUSEMOTION:
                # Adjust the value based on mouse movement while dragging
                if self.vertical:
                    relative_pos = (event.pos[1] - self.y) / self.height
                    self.value = 1 - max(0, min(1, relative_pos))
                else:
                    relative_pos = (event.pos[0] - self.x) / self.width
                    self.value = max(0, min(1, relative_pos))
        elif self._point_in_knob(event.pos) and event.type == Events.MOUSEBUTTONDOWN:
            self.dragging = True
        elif self.abs_area.contains(event.pos) and event.type == Events.MOUSEBUTTONDOWN:
            # Clicking outside the knob moves the slider by one step
            if self.vertical:
                if event.pos[1] < self._get_knob_center()[1]:
                    self._adjust_value_by_step('down')
                elif event.pos[1] > self._get_knob_center()[1]:
                    self._adjust_value_by_step('up')
            else:
                if event.pos[0] < self._get_knob_center()[0]:
                    self._adjust_value_by_step('left')
                elif event.pos[0] > self._get_knob_center()[0]:
                    self._adjust_value_by_step('right')

        super().handle_event(event)

    def _get_knob_center(self):
        """Calculate the center coordinates for the knob based on the current value."""
        x, y, w, h = self.abs_area
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
    def __init__(self, parent, x=None, y=None, h=_default_text_height, fg=_white, bg=None, visible=True):
        """
        Initialize a DigitalClock widget to display the current time.
        
        :param parent: The parent widget or screen that contains this digital clock.
        :param x: The x-coordinate of the digital clock.
        :param y: The y-coordinate of the digital clock.
        :param h: The height of the digital clock.
        :param fg: The color of the text (in a suitable color format).
        :param bg: The background color of the digital clock.
        """
        super().__init__(parent, x, y, h=h, fg=fg, bg=bg, visible=visible)
        self.task = self.display.add_task(self.update, 1)

    def update(self):
        y, m, d, h, min, sec, *_ = localtime()
        self.value = f"{h:02}:{min:02}:{sec:02}"
