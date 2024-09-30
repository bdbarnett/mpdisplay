from gfx import Area, Draw
from eventsys.events import Events
from micropython import const
import png
from palettes.shades import ShadesPalette

DEBUG = True


def log(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def name(obj):
    return obj.__class__.__name__

def drawing(obj):
    return f"{name(obj)} drawing at {obj.abs_area}"

_default_text_height = const(16)
_text_width = const(8)
_text_heights = (8, 14, 16)


class Display:
    def __init__(self, display_drv, broker):
        self.display_drv = display_drv
        self.broker = broker
        self.poll = broker.poll
        self.draw_obj = Draw(display_drv)
        self.active_screen: Screen = None
        self.x = 0
        self.y = 0
        self.width = display_drv.width
        self.height = display_drv.height
        self.parent = None
        self.dirty_widgets = []  # List to track areas that need to be redrawn

    def add_child(self, screen):
        self.active_screen = screen

    def update(self):
        """
        Update only the dirty areas of the screen and its children.

        Uses self.draw_obj for drawing.
        """
        # log(f"{name(self)}.update()")
        if self.active_screen is None:
            return
        
        if not self.dirty_widgets:
            return  # Nothing to redraw

        # Draw widgets that intersect with the dirty areas
        self.active_screen.draw_dirty_widgets()
        self.dirty_widgets.clear()

        # Update the display with the rendered content
        self.display_drv.show()

    def handle_event(self, event):
        """
        Handle an event and propagate it to child widgets.
        
        :param event: An event from the event system (e.g., mouse or keyboard event).
        """
        # log(f"{name(self)}.handle_event({event})")
        if self.active_screen is not None:
            self.active_screen.handle_event(event)


class Widget:
    def __init__(self, parent, x, y, w=0, h=0, fg=-1, bg=0, value=None):
        """
        Initialize a Widget.
        
        :param parent: The parent widget (either another Widget or None if no parent).
        :param x: The x-coordinate of the widget, relative to the parent.
        :param y: The y-coordinate of the widget, relative to the parent.
        :param w: The width of the widget.
        :param h: The height of the widget.
        """
        self.parent: Widget | Display = parent
        self.children: list[Widget] = []
        self._x = x if x is not None else (self.parent.width - w) // 2
        self._y = y if y is not None else (self.parent.height - h) // 2
        self.area = Area(0, 0, w, h)
        self._visible = True  # Default visibility
        self.fg = fg  # Foreground color of the widget
        self.bg = bg  # Background color of the widget
        self._value = value  # Value of the widget (e.g., text of a label)
        self.on_change_callback = None
        self.on_press_callback = None
        self.on_hold_callback = None
        self.on_release_callback = None

        self.parent.add_child(self)

        self.mark_dirty()

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

    def update_value(self):
        """
        Placeholder for updating the widget value. Should be overridden in subclasses.
        """
        log(f"{name(self)} has not overridden update_value method.")
        pass

    @property
    def dirty_widgets(self):
        return self.parent.dirty_widgets

    @property
    def draw_obj(self):
        return self.parent.draw_obj

    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
    
    @property
    def width(self):
        return self.area.w
    
    @property
    def height(self):
        return self.area.h
    
    @property
    def rel_area(self):
        """
        Returns the area of the widget relative to its parent's area.
        """
        return Area(self._x, self._y, self.area.w, self.area.h)

    @property
    def abs_area(self):
        """
        Get the absolute area of the widget on the screen.

        :return: An Area object representing the absolute area.
        """
        x_offset = self.x
        y_offset = self.y
        parent = self.parent

        # Traverse up the hierarchy and sum the offsets
        while parent is not None:
            x_offset += parent.x
            y_offset += parent.y
            parent = parent.parent

        return self.area.offset_by(x_offset, y_offset)

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self._value = value
        self.update_value()

    @property
    def visible(self):
        """Get widget visibility."""
        return self._visible

    @visible.setter
    def visible(self, visible):
        """Set widget visibility."""
        self._visible = visible

    def add_child(self, widget):
        """Adds a child widget to the current widget."""
        log(f"{name(self)}.add_child({name(widget)})")
        self.children.append(widget)

    def remove_child(self, widget):
        """Removes a child widget from the current widget."""
        self.children.remove(widget)

    def mark_dirty(self):
        """
        Mark a specific area of the widget as dirty (needing redraw).
        
        :param area: An Area object representing the dirty area.
        """
        log(f"{name(self)}.mark_dirty()")
        self.dirty_widgets.append(self)

    def draw_dirty_widgets(self):
        if self.visible and self in self.dirty_widgets:
            self.draw()
            self.dirty_widgets.remove(self)
            for child in self.children:
                child.mark_dirty()
        for child in self.children:
            child.draw_dirty_widgets()

    def set_on_press(self, callback):
        """Set the callback function for when the button is pressed."""
        self.on_press_callback = callback

    def set_on_release(self, callback):
        """Set the callback function for when the button is released."""
        self.on_release_callback = callback

    def set_on_hold(self, callback):
        """Set the callback function for when the button is held down."""
        self.on_hold_callback = callback

    def set_on_change(self, callback):
        """Set the callback function for when the value of the widget changes."""
        self.on_change_callback = callback


class Screen(Widget):
    def __init__(self, parent: Display | Widget, color):
        """
        Initialize a Screen widget, which acts as the top-level container for a Display.
        
        :param display: The Display object that this Screen is associated with.
        """
        super().__init__(parent, 0, 0, parent.width, parent.height, color, color)

    def draw(self):
        """
        Draw the screen and its children.
        """
        log(f"{drawing(self)}")
        self.draw_obj.fill_rect(*self.area, self.bg)


class Button(Widget):
    def __init__(self, parent: Widget, x=None, y=None, w=20, h=20, fg=0x0000FF, value=None, radius=0,
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
        self._pressed = False
        self.radius = radius
        self.pressed_offset = 1
        self.filled = True
        super().__init__(parent, x, y, w, h, fg, parent.bg, value)
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
        area = self.abs_area
        if self._pressed:
            self.draw_obj.fill_rect(*area, self.bg)
            area = Area(
                area.x + self.pressed_offset,
                area.y + self.pressed_offset,
                area.w - self.pressed_offset * 2,
                area.h - self.pressed_offset * 2,
            )
        log(f"{drawing(self)}")
        self.draw_obj.round_rect(*area, self.radius, self.fg, f=self.filled)

    def handle_event(self, event: Events.Any):
        """
        Handle user input events like clicks.

        :param event: An event from the event system (e.g., mouse click).
        """
        # log(f"{name(self)}.handle_event({event})")

        # Check if the event is within the button's area
        if event.type == Events.MOUSEBUTTONDOWN and self.abs_area.contains(event.pos):
            self._pressed = True
            if self.on_press_callback:
                self.on_press_callback(self)
            self.mark_dirty()

        elif event.type == Events.MOUSEBUTTONUP and self._pressed:
            self._pressed = False
            if self.on_release_callback:
                self.on_release_callback(self)
            self.mark_dirty()

        # Propagate the event to the children of the button
        super().handle_event(event)


class Label(Widget):
    def __init__(self, parent: Widget, x=None, y=None, h=_default_text_height, fg=-1, bg=None, value=""):
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
        super().__init__(parent, x, y, len(value) * _text_width, h, fg, parent.fg, value)
        self.bg = bg  # Store the optional background color

    def draw(self):
        """
        Draw the label's text on the screen, using absolute coordinates.
        Optionally fills the background first if `bg` is set.
        """
        log(f"{drawing(self)}")
        if self.bg:
            self.draw_obj.fill_rect(*self.abs_area, self.bg)  # Draw background if bg is specified
        x, y, _, _ = self.abs_area
        self.draw_obj.text(self.value, x, y, self.fg, height=self.height)


class TextBox(Widget):
    def __init__(self, parent: Widget, x=None, y=None, w=64, h=None,
                 fg=0, bg=-1, value="", text_height=_default_text_height):
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
        self.margin = 1
        h = h or self.text_height + 2 * self.margin
        super().__init__(parent, x, y, w, h, fg, bg, value)

    def draw(self):
        """
        Draw the label's text on the screen, using absolute coordinates.
        """
        log(f"{drawing(self)}")
        self.draw_obj.fill_rect(*self.abs_area, self.bg)
        x, y, _, _ = self.abs_area
        x += self.margin
        y += self.margin
        self.draw_obj.text(self.value, x, y, self.fg, height=self.text_height)

    def update_value(self):
        self.mark_dirty()


class ProgressBar(Widget):
    def __init__(self, parent: Widget, x=None, y=None, w=64, h=20, fg=0, bg=-1, value=0, vertical=False, reverse=False):
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
        super().__init__(parent, x, y, w, h, fg, bg, value)

    def draw(self):
        """
        Draw the progress bar on the screen.
        """
        log(f"{drawing(self)}")
        self.draw_obj.fill_rect(*self.abs_area, self.bg)
        x, y, w, h = self.abs_area

        # Ensure value is between 0 and 1
        if self.value < 0:
            self.value = 0
        elif self.value > 1:
            self.value = 1

        if self.value == 0:
            return  # Nothing to draw if value is 0

        if self.vertical:
            # Calculate the height of the filled part
            progress_height = int(self.value * h)
            if self.reverse:
                # Fill from top to bottom
                self.draw_obj.fill_rect(x, y, w, progress_height, self.fg)
            else:
                # Fill from bottom to top (default)
                self.draw_obj.fill_rect(x, y + h - progress_height, w, progress_height, self.fg)
        else:
            # Calculate the width of the filled part
            progress_width = int(self.value * w)
            if self.reverse:
                # Fill from right to left
                self.draw_obj.fill_rect(x + w - progress_width, y, progress_width, h, self.fg)
            else:
                # Fill from left to right (default)
                self.draw_obj.fill_rect(x, y, progress_width, h, self.fg)

    def update_value(self):
        if self.on_change_callback:
            self.on_change_callback(self)
        self.mark_dirty()


class Icon(Widget):
    def __init__(self, parent: Widget, x=None, y=None, fg=-1, bg=None, value=None):
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
        super().__init__(parent, x, y, self.icon_width, self.icon_height, fg, bg, value)

    def load_icon(self, value):
        """Load icon file and store pixel data."""
        self.icon_width, self.icon_height, self._pixels, self._metadata = png.Reader(filename=value).read_flat()
        if not self._metadata["greyscale"] or self._metadata['bitdepth'] != 8:
            raise ValueError(f"Only 8-bit greyscale PNGs are supported {self.value}")

    def update_value(self):
        """Update the icon when the value (file) changes."""
        self.load_icon(self.value)
        self.mark_dirty()

    def draw(self):
        """
        Draw the icon on the screen.
        """
        log(f"{drawing(self)}")
        pal = ShadesPalette(color=self.fg)
        alpha = 1 if self._metadata["alpha"] else 0
        planes = self._metadata["planes"]
        pixels = self._pixels
        pos_x, pos_y, w, h = self.abs_area
        for y in range(0, h):
            for x in range(0, w):
                if (c := pixels[(y * w + x) * planes + alpha]) != 0:
                    self.draw_obj.pixel(pos_x + x, pos_y + y, pal[c])


class IconButton(Button):
    def __init__(self, parent: Widget, x=None, y=None, w=20, h=20, fg=0, bg=-1, value=None, icon=None):
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
        :param icon: The icon to display on the button.
        """
        super().__init__(parent, x, y, w, h, bg, value)
        self.icon = Icon(self, fg=fg, bg=bg, value=icon)


class CheckBox(IconButton):
    def __init__(self, parent, x=None, y=None, w=20, h=20, fg=0x000000, bg=0xFFFFFF, value=False):
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
        self.checked_icon = "icons/18dp/check_box_18dp.png"
        self.unchecked_icon = "icons/18dp/check_box_outline_blank_18dp.png"
        
        # Set initial icon based on the value (checked state)
        icon = self.checked_icon if value else self.unchecked_icon
        
        super().__init__(parent, x=x, y=y, w=w, h=h, fg=fg, bg=bg, icon=icon)
        
        # Store the checked state in the value attribute
        self.value = value
        self.on_change_callback = None  # Callback for when the state changes

    def toggle(self):
        """Toggle the checked state when the checkbox is pressed."""
        self.value = not self.value  # Toggle the boolean value
        self.update_value()  # Update the icon based on the new state
        
        # If an external callback is registered, call it
        if self.on_change_callback:
            self.on_change_callback(self)

    def update_value(self):
        """Update the icon based on the current checked state."""
        self.icon.value = self.checked_icon if self.value else self.unchecked_icon
        self.icon.update_value()  # Call the update_value in the Icon to reload the file

    def handle_event(self, event):
        """Override handle_event to toggle the CheckBox when clicked."""
        if event.type == Events.MOUSEBUTTONDOWN and self.abs_area.contains(event.pos):
            self.toggle()
            self.mark_dirty()  # Redraw the widget
        super().handle_event(event)  # Propagate to children if necessary

    def set_on_change(self, callback):
        """Set the callback function for when the value of the checkbox changes."""
        self.on_change_callback = callback


class ToggleButton(IconButton):
    def __init__(self, parent, x=None, y=None, w=20, h=20, fg=0x000000, bg=0xFFFFFF, value=False):
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
        self.on_icon = "icons/18dp/toggle_on_18dp.png"
        self.off_icon = "icons/18dp/toggle_off_18dp.png"

        # Set initial icon based on the value (on/off state)
        icon = self.on_icon if value else self.off_icon
        
        super().__init__(parent, x=x, y=y, w=w, h=h, fg=fg, bg=bg, icon=icon)
        
        # Store the toggle state in the value attribute
        self.value = value
        self.on_change_callback = None  # Callback for when the state changes

    def toggle(self):
        """Toggle the on/off state of the button."""
        self.value = not self.value  # Invert the current state

        # Update the icon to reflect the new state
        self.update_value()

        # If an external callback is registered, call it
        if self.on_change_callback:
            self.on_change_callback(self)

    def update_value(self):
        """Update the icon based on the current on/off state."""
        # Update the icon value based on the current toggle state
        self.icon.value = self.on_icon if self.value else self.off_icon

        # Force the icon to reload and mark itself as dirty
        self.icon.draw()  # Force the redraw of the icon
        self.mark_dirty()  # Mark the toggle button as dirty to trigger a full redraw

    def handle_event(self, event):
        """Override handle_event to toggle the button when clicked."""
        if event.type == Events.MOUSEBUTTONDOWN and self.abs_area.contains(event.pos):
            self.toggle()  # Toggle the state when clicked
        super().handle_event(event)  # Propagate to children if necessary

    def set_on_change(self, callback):
        """Set the callback function for when the value of the toggle button changes."""
        self.on_change_callback = callback


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
            radio_button.update_value()


class RadioButton(IconButton):
    def __init__(self, parent, group, x=None, y=None, w=20, h=20, fg=0x000000, bg=0xFFFFFF, value=False):
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
        self.checked_icon = "icons/18dp/radio_button_checked_18dp.png"
        self.unchecked_icon = "icons/18dp/radio_button_unchecked_18dp.png"

        # Set initial icon based on the value (checked state)
        icon = self.checked_icon if value else self.unchecked_icon
        
        super().__init__(parent, x=x, y=y, w=w, h=h, fg=fg, bg=bg, icon=icon)
        
        # Store the checked state in the value attribute
        self.value = value
        self.group = group
        self.group.add(self)
        self.on_change_callback = None  # Callback for when the state changes

    def toggle(self):
        """Toggle the checked state to true when clicked and uncheck other RadioButtons in the group."""
        if not self.value:  # Only toggle if not already checked
            self.value = True  # A radio button is always checked when clicked
            self.group.set_checked(self)  # Uncheck all other buttons in the group

            # Update the icon to reflect the new state
            self.update_value()

            # If an external callback is registered, call it
            if self.on_change_callback:
                self.on_change_callback(self)

    def update_value(self):
        """Update the icon based on the current checked state."""
        # Update the icon value based on the current checked state
        self.icon.value = self.checked_icon if self.value else self.unchecked_icon

        # Force the icon to reload and mark itself as dirty
        self.icon.draw()  # Force the redraw of the icon
        self.mark_dirty()  # Mark the radio button as dirty to trigger a full redraw

    def handle_event(self, event):
        """Override handle_event to toggle the RadioButton when clicked."""
        if event.type == Events.MOUSEBUTTONDOWN and self.abs_area.contains(event.pos):
            self.toggle()  # Toggle the state when clicked
        super().handle_event(event)  # Propagate to children if necessary

    def set_on_change(self, callback):
        """Set the callback function for when the value of the radio button changes."""
        self.on_change_callback = callback


class Slider(ProgressBar):
    def __init__(self, parent, x=None, y=None, w=100, h=20, fg=0x000000, bg=0xFFFFFF, knob_color=0x000000, value=0, vertical=False, step=0.1):
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
        super().__init__(parent, x=x, y=y, w=w, h=h, fg=fg, bg=bg, value=value, vertical=vertical)
        self.knob_radius = (h // 3 if vertical else w // 10) // 2  # Halve the radius to fix size
        self._dragging = False  # Track whether the knob is being dragged
        self.step = step  # Step size for value adjustments
        self.knob_color = knob_color  # Color of the knob
        self.on_change_callback = None  # Callback for when the value changes

    def draw(self):
        """Draw the slider, including the progress bar and the circular knob."""
        super().draw()  # Draw the base progress bar

        # Calculate the position of the knob
        knob_center = self._get_knob_center()
        log(f"Drawing circular slider knob at {knob_center}")

        # Draw the knob as a filled circle with correct radius
        self.draw_obj.circle(knob_center[0], knob_center[1], self.knob_radius, self.knob_color, f=True)

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

    def update_value(self):
        """Update the slider value and redraw the knob."""
        super().update_value()
        self.mark_dirty()  # Mark the slider as dirty to trigger a full redraw

        # Call the external callback if registered
        if self.on_change_callback:
            self.on_change_callback(self)

    def handle_event(self, event):
        """Handle user input events like clicks, dragging, and mouse movements."""
        if event.type == Events.MOUSEBUTTONDOWN and self._point_in_knob(event.pos):
            self._dragging = True  # Start dragging the knob

        elif event.type == Events.MOUSEBUTTONUP:
            self._dragging = False  # Stop dragging when mouse is released

        elif event.type == Events.MOUSEMOTION and self._dragging:
            # Adjust the value based on mouse movement while dragging
            if self.vertical:
                relative_pos = (event.pos[1] - self.y) / self.height
                self.value = 1 - max(0, min(1, relative_pos))
            else:
                relative_pos = (event.pos[0] - self.x) / self.width
                self.value = max(0, min(1, relative_pos))
            self.update_value()

        elif event.type == Events.MOUSEBUTTONDOWN and not self._dragging:
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

    def _point_in_knob(self, pos):
        """Check if the given point is within the knob's circular area."""
        knob_center = self._get_knob_center()
        distance = ((pos[0] - knob_center[0]) ** 2 + (pos[1] - knob_center[1]) ** 2) ** 0.5
        return distance <= self.knob_radius

    def _adjust_value_by_step(self, direction):
        """Adjust the slider value by one step in the specified direction."""
        if self.vertical:
            if direction == 'up':
                self.value = min(1, self.value + self.step)
            elif direction == 'down':
                self.value = max(0, self.value - self.step)
        else:
            if direction == 'right':
                self.value = min(1, self.value + self.step)
            elif direction == 'left':
                self.value = max(0, self.value - self.step)

        self.update_value()

    def set_on_change(self, callback):
        """Set the callback function for when the slider value changes."""
        self.on_change_callback = callback


class LinearLayout(Widget):
    def __init__(self, parent, x=None, y=None, w=None, h=None, padding=0, spacing=0, direction="vertical", bg=0xFFFFFF):
        """
        Initialize a generic LinearLayout widget that arranges its child widgets either
        vertically (like a Column) or horizontally (like a Row).
        
        :param parent: The parent widget or screen that contains this layout.
        :param x: The x-coordinate of the layout (optional, can be centered if None).
        :param y: The y-coordinate of the layout (optional, can be centered if None).
        :param w: The width of the layout (can be None for dynamic width).
        :param h: The height of the layout (can be None for dynamic height).
        :param padding: The padding around the edges of the layout (optional).
        :param spacing: The spacing between child widgets (optional).
        :param direction: The layout direction - "vertical" or "horizontal".
        :param bg: The background color of the layout (default is white).
        """
        # Initialize dimensions as provided or set to 0 if not provided
        w = w if w is not None else 0
        h = h if h is not None else 0

        super().__init__(parent, x, y, w, h, bg=bg)
        self.padding = padding  # Padding around the layout
        self.spacing = spacing  # Spacing between child widgets
        self.direction = direction  # "vertical" for Column, "horizontal" for Row
        self._dynamic_width = w if w != 0 else 0
        self._dynamic_height = h if h != 0 else 0

    def add_child(self, widget):
        """
        Add a child widget to the layout and automatically arrange it.
        
        :param widget: The child widget to add to the layout.
        """
        super().add_child(widget)
        self.arrange_children()
        self.center_if_needed()  # Recalculate centering after arranging children

    def arrange_children(self):
        """
        Arrange the child widgets either vertically (like a Column) or horizontally (like a Row),
        adjusting the layout height and width dynamically if needed.
        """
        current_pos = self.padding  # Start at the top/left with padding
        max_opposite_dim = 0  # To track the largest width (in vertical) or height (in horizontal)

        for child in self.children:
            if self.direction == "vertical":
                # Vertically stack widgets inside the column
                child._x = self.padding  # Position relative to the column, not the screen
                child._y = current_pos  # Start from current_pos (accumulated vertical position)
                current_pos += child.height + self.spacing  # Update vertical position for next child
                max_opposite_dim = max(max_opposite_dim, child.width)  # Track the widest child

            elif self.direction == "horizontal":
                # Horizontally stack widgets inside the row
                child._x = current_pos  # Start from current_pos (accumulated horizontal position)
                child._y = self.padding  # Position relative to the row, not the screen
                current_pos += child.width + self.spacing  # Update horizontal position for next child
                max_opposite_dim = max(max_opposite_dim, child.height)  # Track the tallest child

        # Update the dynamic height or width based on the children arrangement
        if self.direction == "vertical":
            self._dynamic_height = current_pos + self.padding - self.spacing  # Calculate final height
            self.area.h = self._dynamic_height
            if self._dynamic_width == 0:
                self.area.w = max_opposite_dim + 2 * self.padding  # Adjust width based on widest child

        elif self.direction == "horizontal":
            self._dynamic_width = current_pos + self.padding - self.spacing  # Calculate final width
            self.area.w = self._dynamic_width
            if self._dynamic_height == 0:
                self.area.h = max_opposite_dim + 2 * self.padding  # Adjust height based on tallest child

        self.center_if_needed()  # Ensure the layout is centered after arranging

    def center_if_needed(self):
        """
        Recalculate the `x` and `y` coordinates to center the widget if needed.
        This is called after arranging children and determining the final width/height.
        """
        # Center horizontally if x is not provided
        if self._x is None:
            self._x = (self.parent.width - self._dynamic_width) // 2

        # Center vertically if y is not provided
        if self._y is None:
            self._y = (self.parent.height - self._dynamic_height) // 2

    @property
    def height(self):
        """Override the height property to return the dynamic height of the layout."""
        return self._dynamic_height

    @property
    def width(self):
        """Override the width property to return the dynamic width of the layout."""
        return self._dynamic_width

    def draw(self):
        """
        Draw the layout background and its child widgets.
        """
        # Draw the layout background
        self.draw_obj.fill_rect(self.x, self.y, self.width, self.height, self.bg)

        # Draw the child widgets
        log(f"Drawing {len(self.children)} children in {name(self)}.")
        for child in self.children:
            child.draw()


class Column(LinearLayout):
    def __init__(self, parent, x=None, y=None, w=None, padding=0, spacing=0, bg=0xFFFFFF):
        """
        Initialize a Column widget that arranges its child widgets vertically.
        
        :param parent: The parent widget or screen that contains this column.
        :param x: The x-coordinate of the column.
        :param y: The y-coordinate of the column.
        :param w: The fixed width of the column (if None, it will dynamically adjust to fit the widest child).
        :param padding: The padding around the edges of the column (optional).
        :param spacing: The vertical spacing between child widgets (optional).
        :param bg: The background color of the column (default is white).
        """
        super().__init__(parent, x, y, w, padding=padding, spacing=spacing, direction="vertical", bg=bg)


class Row(LinearLayout):
    def __init__(self, parent, x=None, y=None, h=None, padding=0, spacing=0, bg=0xFFFFFF):
        """
        Initialize a Row widget that arranges its child widgets horizontally.
        
        :param parent: The parent widget or screen that contains this row.
        :param x: The x-coordinate of the row.
        :param y: The y-coordinate of the row.
        :param h: The fixed height of the row (if None, it will dynamically adjust to fit the tallest child).
        :param padding: The padding around the edges of the row (optional).
        :param spacing: The horizontal spacing between child widgets (optional).
        :param bg: The background color of the row (default is white).
        """
        super().__init__(parent, x, y, h=h, padding=padding, spacing=spacing, direction="horizontal", bg=bg)


class VerticalScrollBar(Column):
    def __init__(self, parent, x=None, w=20, h=None, fg=0x000000, bg=0xFFFFFF):
        """
        Initialize a VerticalScrollBar widget, which contains a ProgressBar and two IconButtons (up and down).
        
        :param parent: The parent widget or screen that contains this scrollbar.
        :param x: The x-coordinate of the scrollbar (optional, defaults to the right edge of the parent).
        :param w: The width of the scrollbar (default is 20).
        :param h: The height of the scrollbar (default is parent's height).
        :param fg: The foreground color of the scrollbar (default is black).
        :param bg: The background color of the scrollbar (default is white).
        """
        # Default position to the right edge of the parent
        x = x if x is not None else parent.width - w
        h = h if h is not None else parent.height  # Set height dynamically to match parent's height if not specified

        # Set padding and spacing for the layout
        padding = 1
        spacing = 1

        # Adjust ProgressBar height to account for the two IconButtons and spacing
        icon_button_height = 18
        progress_bar_height = h - (2 * icon_button_height + 2 * padding + spacing)

        super().__init__(parent, x=x, y=0, w=w, padding=padding, spacing=spacing, bg=bg)

        # Create the IconButton for scrolling up
        self.icon_button_up = IconButton(self, w=18, h=18, fg=fg, bg=bg, icon="icons/18dp/keyboard_arrow_up_18dp.png")

        # Create the ProgressBar for tracking scroll progress, set it to vertical with reverse filling (top-to-bottom)
        self.progress_bar = ProgressBar(self, w=w-2, h=progress_bar_height, fg=fg, bg=bg, vertical=True, reverse=True)

        # Create the IconButton for scrolling down
        self.icon_button_down = IconButton(self, w=18, h=18, fg=fg, bg=bg, icon="icons/18dp/keyboard_arrow_down_18dp.png")

        # Set up default behavior for the buttons
        self.icon_button_up.set_on_press(self.scroll_up)
        self.icon_button_down.set_on_press(self.scroll_down)

    def scroll_up(self, sender):
        """Handle scrolling up."""
        self.progress_bar.value = max(0, self.progress_bar.value - 0.1)
        self.mark_dirty()

    def scroll_down(self, sender):
        """Handle scrolling down."""
        self.progress_bar.value = min(1, self.progress_bar.value + 0.1)
        self.mark_dirty()


class HorizontalScrollBar(Row):
    def __init__(self, parent, y=None, w=None, h=20, fg=0x000000, bg=0xFFFFFF):
        """
        Initialize a HorizontalScrollBar widget, which contains a ProgressBar and two IconButtons (left and right).
        
        :param parent: The parent widget or screen that contains this scrollbar.
        :param y: The y-coordinate of the scrollbar (optional, defaults to the bottom of the parent).
        :param w: The width of the scrollbar (default is parent's width).
        :param h: The height of the scrollbar (default is 20).
        :param fg: The foreground color of the scrollbar (default is black).
        :param bg: The background color of the scrollbar (default is white).
        """
        # Default position to the bottom of the parent
        y = y if y is not None else parent.height - h
        w = w if w is not None else parent.width  # Set width dynamically to match parent's width if not specified

        # Set padding and spacing for the layout
        padding = 1
        spacing = 1

        # Adjust ProgressBar width to account for the two IconButtons and spacing
        icon_button_width = 18
        progress_bar_width = w - (2 * icon_button_width + 2 * padding + spacing)

        super().__init__(parent, x=0, y=y, h=h, padding=padding, spacing=spacing, bg=bg)

        # Create the IconButton for scrolling left
        self.icon_button_left = IconButton(self, w=18, h=18, fg=fg, bg=bg, icon="icons/18dp/keyboard_arrow_left_18dp.png")

        # Create the ProgressBar for tracking scroll progress, set it to horizontal
        self.progress_bar = ProgressBar(self, w=progress_bar_width, h=h-2, fg=fg, bg=bg, vertical=False)

        # Create the IconButton for scrolling right
        self.icon_button_right = IconButton(self, w=18, h=18, fg=fg, bg=bg, icon="icons/18dp/keyboard_arrow_right_18dp.png")

        # Set up default behavior for the buttons
        self.icon_button_left.set_on_press(self.scroll_left)
        self.icon_button_right.set_on_press(self.scroll_right)

    def scroll_left(self, sender):
        """Handle scrolling left."""
        self.progress_bar.value = max(0, self.progress_bar.value - 0.1)
        self.mark_dirty()

    def scroll_right(self, sender):
        """Handle scrolling right."""
        self.progress_bar.value = min(1, self.progress_bar.value + 0.1)
        self.mark_dirty()


class ListView(Column):
    def __init__(self, parent, x=None, y=None, w=100, h=100, bg=None, selectable=False, spacing=5):
        """
        ListView initialization that inherits from Column to arrange ListItems vertically.
        """
        super().__init__(parent, x=x, y=y, w=w, padding=5, spacing=spacing, bg=bg)
        self._fixed_height = h
        self.selectable = selectable
        self.items = []
        self.selected_index = None
        self.scroll_offset = 0

    @property
    def height(self):
        return self._fixed_height

    def add_item(self, value, fg=0xFFFFFF, bg=None, selected_bg=0x0000FF):
        """
        Add a new ListItem to the ListView.
        """
        item = ListItem(self, value=value, fg=fg, bg=bg, selected_bg=selected_bg)
        self.items.append(item)
        self.arrange_children()
        self.mark_dirty()

    def draw(self):
        """
        Draw the ListView and its items, ensuring that items are clipped to the ListView's area.
        """
        listview_abs_area = self.abs_area  # ListView's absolute area on screen

        # Draw the background for the ListView
        if self.bg:
            self.draw_obj.fill_rect(*listview_abs_area, self.bg)

        for item in self.items:
            # Adjust each item's position based on scroll
            item_rel_area = item.rel_area.offset_by(0, self.scroll_offset)

            # Clip item drawing to the ListView area
            if listview_abs_area.intersects(item.abs_area):
                item.draw()  # Only draw the item if it's within bounds

    def arrange_children(self):
        """
        Arrange ListItems within the ListView, adjusting their positions vertically.
        """
        current_pos = self.padding
        for item in self.items:
            item._x = self.padding
            item._y = current_pos
            current_pos += item.height + self.spacing
        self._dynamic_height = min(current_pos, self._fixed_height)
        self.mark_dirty()

    def scroll(self, direction):
        """
        Scroll the ListView up or down by adjusting the scroll_offset.
        """
        if direction == 'up':
            self._scroll_up()
        elif direction == 'down':
            self._scroll_down()

    def _scroll_up(self):
        """
        Scroll the ListView upwards.
        """
        if self.scroll_offset < 0:
            self.scroll_offset += 20
            self.mark_dirty()

    def _scroll_down(self):
        """
        Scroll the ListView downwards.
        """
        total_height = sum(item.height + self.spacing for item in self.items)
        if self.scroll_offset + self.height < total_height:
            self.scroll_offset -= 20
            self.mark_dirty()

    def handle_event(self, event):
        """
        Handle events, such as clicking on items in the ListView.
        """
        super().handle_event(event)
        if self.selectable and event.type == Events.MOUSEBUTTONDOWN:
            for i, item in enumerate(self.items):
                if item.abs_area.contains(event.pos):
                    self.select_item(i)
                    break

    def select_item(self, index):
        """
        Select an item in the ListView.
        """
        if self.selected_index is not None:
            self.items[self.selected_index].set_selected(False)
        self.selected_index = index
        self.items[self.selected_index].set_selected(True)

        if self.on_change_callback:
            self.on_change_callback(self)


class ListItem(Label):
    def __init__(self, parent, value="", fg=0xFFFFFF, bg=None, selected_bg=0x0000FF, is_selected=False):
        """
        Initialize a ListItem widget that represents an item in the ListView.
        
        :param parent: The parent widget (usually the ListView).
        :param value: The text content of the ListItem.
        :param fg: The foreground (text) color.
        :param bg: The background color when not selected.
        :param selected_bg: The background color when selected.
        :param is_selected: Whether the item is selected initially.
        """
        super().__init__(parent, value=value, fg=fg, bg=bg)
        self.is_selected = is_selected
        self.default_bg = bg
        self.selected_bg = selected_bg

        self.update_selected_state()

    def update_selected_state(self):
        """
        Update the background of the ListItem based on its selected state.
        """
        if self.is_selected:
            self.bg = self.selected_bg
        else:
            self.bg = self.default_bg

        # Mark as dirty to redraw
        self.mark_dirty()

    def set_selected(self, selected):
        """
        Set the selection state of the ListItem.
        
        :param selected: Boolean indicating if the item should be selected.
        """
        self.is_selected = selected
        self.update_selected_state()


def main():
    from board_config import broker, display_drv
    from palettes import get_palette
    from displaybuf import DisplayBuffer
    from eventsys.events import Events
    import widgets as w
    import time


    pal = get_palette()
    display = w.Display(DisplayBuffer(display_drv), broker)
    screen = w.Screen(display, pal.SILVER)

    icon = w.Icon(screen, x=0, y=0, fg=pal.RED, value="icons/18dp/keyboard_arrow_down_18dp.png")  # noqa: F841
    label1 = w.Label(screen, y=2, value="Testing", fg=pal.WHITE)  # noqa: F841

    status = w.TextBox(screen, x=0, y=display.height-38, w=display.width-20)

    button1 = w.Button(screen, w=96, fg=pal.BLUE, value="button1", label="Click Me", label_color=pal.WHITE)
    button1.set_on_press(lambda sender: setattr(status, 'value', f"{sender.value} pressed!"))
    button1.set_on_release(lambda sender: setattr(status, 'value', f"{sender.value} released!"))

    # Simulate a scroll bar. Shows how to add an Icon to a Button. Also shows how to use an IconButton.
    pbar = w.ProgressBar(screen, y=display.height-60, w=display.width//2, value=0.5)
    pbar.set_on_change(lambda sender: setattr(status, 'value', f"Progress: {sender.value:.0%}"))
    pbtn1 = w.Button(screen, x=pbar.x-20, y=pbar.y, fg=pal.GREEN)
    pbtn1_icon = w.Icon(pbtn1, fg=pal.BLACK, value="icons/18dp/keyboard_arrow_left_18dp.png")  # noqa: F841
    pbtn2 = w.IconButton(screen, x=pbar.x+pbar.width, y=pbar.y, fg=pal.BLACK, bg=pal.GREEN, icon="icons/18dp/keyboard_arrow_right_18dp.png")
    pbtn1.set_on_press(lambda sender: setattr(pbar, 'value', pbar.value-0.1))
    pbtn2.set_on_press(lambda sender: setattr(pbar, 'value', pbar.value+0.1))

    # Create a column and add child widgets (buttons, labels, etc.)
    column = w.Column(screen, y=20, w=120, padding=10, spacing=5)
    
    label2 = w.Label(column, value="Label 2", fg=pal.BLUE)
    label3 = w.Label(column, value="Label 3", fg=pal.RED)
    button2 = w.Button(column, label="!", fg=pal.GREEN)
    
    # Create a row and add child widgets (buttons, labels, etc.)
    row = w.Row(screen, x=0, h=40, padding=5, spacing=10)
    
    button3 = w.Button(row, label="3", fg=pal.YELLOW)
    button4 = w.Button(row, label="4", fg=pal.CYAN)

    # Create a vertical scrollbar on the right edge of the screen
    vertical_scrollbar = w.VerticalScrollBar(screen, h=screen.height-20, fg=pal.BLUE, bg=pal.GREY)
    
    # Create a horizontal scrollbar at the bottom of the screen
    horizontal_scrollbar = w.HorizontalScrollBar(screen, w=screen.width-20, fg=pal.BLUE, bg=pal.GREY)


    # Create a CheckBox widget
    checkbox = w.CheckBox(screen, x=50, y=100, fg=pal.BLACK, bg=pal.WHITE, value=False)

    # Add a callback to print the state when the checkbox is toggled
    checkbox.set_on_change(lambda sender: setattr(status, 'value', f"{'checked' if sender.value else 'unchecked'}"))


    # Create a RadioGroup to manage the radio buttons
    radio_group = w.RadioGroup()

    # Create a couple of RadioButtons and add them to the RadioGroup
    radio1 = w.RadioButton(screen, group=radio_group, x=50, y=50, fg=pal.BLACK, bg=pal.WHITE, value=False)
    radio2 = w.RadioButton(screen, group=radio_group, x=50, y=80, fg=pal.BLACK, bg=pal.WHITE, value=True)

    # Set a callback to update the status when a radio button is checked
    radio1.set_on_change(lambda sender: setattr(status, 'value', f"RadioButton 1 is now {'checked' if sender.value else 'unchecked'}"))
    radio2.set_on_change(lambda sender: setattr(status, 'value', f"RadioButton 2 is now {'checked' if sender.value else 'unchecked'}"))

    # Create a ToggleButton
    toggle_button = w.ToggleButton(screen, x=150, y=150, fg=pal.BLACK, bg=pal.WHITE, value=False)

    # Set a callback to update the status when the toggle button changes state
    toggle_button.set_on_change(lambda sender: setattr(status, 'value', f"Toggle is now {'On' if sender.value else 'Off'}"))


    # Create a horizontal slider with a custom knob color
    slider = w.Slider(screen, y=380, w=200, fg=pal.BLACK, bg=pal.GREY, knob_color=pal.RED, value=0.5, step=0.05)

    # Set a callback to update the status when the slider changes
    slider.set_on_change(lambda sender: setattr(status, 'value', f"Slider value: {sender.value:.2f}"))


    # # Create a ListView widget and populate it with items
    # listview = w.ListView(screen, y=280, w=120, h=90, bg=pal.GREY, selectable=True)

    # # Add multiple items to the ListView
    # for i in range(20):
    #     listview.add_item(f"Item {i + 1}", fg=pal.WHITE, bg=pal.BLACK, selected_bg=pal.GREEN)

    # Draw the screen
    display.update()

    # Set the target frame rate (30 frames per second)
    frame_rate = 30
    frame_duration = 1 / frame_rate
    last_update_time = time.time()

    while True:
        current_time = time.time()
        if current_time - last_update_time >= frame_duration:
            display.update()
            last_update_time = current_time

        if e := display.poll():
            if e.type in [Events.MOUSEBUTTONDOWN, Events.MOUSEBUTTONUP, Events.MOUSEMOTION]:
                display.handle_event(e)
                display.update()

main()
