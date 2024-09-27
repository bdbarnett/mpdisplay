from gfx import Area, Draw
DEBUG = True

def log(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def name(obj):
    return obj.__class__.__name__

class Widget:
    def __init__(self, parent, x, y, w=0, h=0, fg=-1, bg=0):
        """
        Initialize a Widget.
        
        :param parent: The parent widget (either another Widget or None if no parent).
        :param x: The x-coordinate of the widget, relative to the parent.
        :param y: The y-coordinate of the widget, relative to the parent.
        :param w: The width of the widget.
        :param h: The height of the widget.
        """
        self.parent = parent
        self.children = []
        self._x = x if x is not None else (parent.width - w) // 2
        self._y = y if y is not None else (parent.height - h) // 2
        self.area = Area(0, 0, w, h)
        self._visible = True  # Default visibility
        self._dirty_areas = []  # List to track areas that need to be redrawn
        self.fg = fg  # Foreground color of the widget
        self.bg = bg  # Background color of the widget

        # If this widget has a parent, inherit the parent's draw_obj
        if self.parent:
            self.draw_obj = self.parent.draw_obj
        else:
            self.draw_obj = None

        # Only call add_child if the parent is a Widget instance
        if isinstance(self.parent, Widget):
            self.parent.add_child(self)

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

    def add_child(self, widget):
        """Adds a child widget to the current widget."""
        log(f"{name(self)}.add_child({name(widget)})")
        self.children.append(widget)

    def remove_child(self, widget):
        """Removes a child widget from the current widget."""
        self.children.remove(widget)

    def mark_dirty(self, area):
        """
        Mark a specific area of the widget as dirty (needing redraw).
        
        :param area: An Area object representing the dirty area.
        """
        log(f"{name(self)}.mark_dirty({area})")
        self._dirty_areas.append(area)
        if self.parent:
            rel_area = area.offset_by(self.x, self.y)  # Relative to the parent
            self.parent.mark_dirty(rel_area)  # Propagate up the hierarchy

    @property
    def dirty_area(self):
        """
        Merge dirty areas into a single area for efficient redrawing.
        
        :return: A merged Area object.
        """
        if not self._dirty_areas:
            return None

        merged_area = self._dirty_areas[0]
        for area in self._dirty_areas[1:]:
            merged_area += area

        return merged_area

    def _draw_dirty_widgets(self, dirty_area):
        """
        Recursively draw widgets that intersect with dirty areas.

        :param dirty_area: The merged dirty areas (a list of Area objects).
        """
        if self.visible: #  and dirty_area.intersects(Area(self.x, self.y, self.width, self.height)):
            self.on_draw()  # Draw this widget if it intersects with dirty area

            # Draw child widgets if they intersect with dirty areas
            for child in self.children:
                child._draw_dirty_widgets(dirty_area)

    def on_draw(self):
        """
        Placeholder for the actual drawing logic of the widget.
        Should be overridden in subclasses.
        """
        log(f"{name(self)} has not overridden on_draw method.")
        pass

    def handle_event(self, event):
        """
        Handle events such as mouse clicks or key presses.

        :param event: An event from the event system (e.g., mouse or keyboard event)
        """
        # Override in subclass for specific event handling logic
        log(f"{name(self)} has not overridden handle_event method.")
        pass

    def draw(self):
        """
        Draw the widget and its children, typically overridden by subclasses.
        Can be combined with dirty area optimization logic.
        """
        log(f"{name(self)} has not overridden draw method.")
        pass

    @property
    def visible(self):
        """Get widget visibility."""
        return self._visible

    @visible.setter
    def visible(self, visible):
        """Set widget visibility."""
        self.visible = visible


class Screen(Widget):
    def __init__(self, display, color):
        """
        Initialize a Screen widget, which acts as the top-level container for a Display.
        
        :param display: The Display object that this Screen is associated with.
        """
        super().__init__(None, 0, 0, display.width, display.height, color, color)
        self.display = display
        self.draw_obj = Draw(display)  # Create the draw object for the screen

    def draw(self):
        """
        Draws only the dirty areas of the screen and its children.

        Uses self.draw_obj for drawing.
        """
        log(f"{name(self)}.draw()")
        if (dirty_area := self.dirty_area) is None:
            return  # Nothing to redraw

        # Clear the dirty areas only
        print(f"Clearing dirty area {dirty_area}")
        self.display.fill_rect(*dirty_area, self.bg)

        # Draw widgets that intersect with the dirty areas
        self._draw_dirty_widgets(dirty_area)

        # Update the display with the rendered content
        self.display.show()

        # Clear the dirty areas list after updating
        self._dirty_areas.clear()

    def handle_event(self, event):
        """
        Handle an event and propagate it to child widgets.
        
        :param event: An event from the event system (e.g., mouse or keyboard event).
        """
        log(f"{name(self)}.handle_event({event})")
        # Propagate the event to the children of the screen
        for child in self.children:
            child.handle_event(event)


class Button(Widget):
    def __init__(self, parent, x=None, y=None, w=16, h=16, fg=0x0000FF):
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
        super().__init__(parent, x, y, w, h, fg, parent.bg)
        self._pressed = False
        self.on_press_callback = None
        self.on_hold_callback = None
        self.on_release_callback = None
        self.radius = 4
        self.pressed_offset = 2
        self.filled = True

        self.mark_dirty(self.area)

    def on_draw(self):
        """
        Draw the button background and any child widgets (like a label).
        """
        log(f"{name(self)}.on_draw()")
        if self.visible:
            # Adjust size if the button is pressed
            area = self.abs_area
            if self._pressed:
                area = Area(
                    area.x + self.pressed_offset,
                    area.y + self.pressed_offset,
                    area.w - self.pressed_offset * 2,
                    area.h - self.pressed_offset * 2,
                )
            log(f"{name(self)}.on_draw() - Drawing area: {area}")
            self.draw_obj.round_rect(*area, self.radius, self.fg, f=self.filled)

    def handle_event(self, event):
        """
        Handle user input events like clicks.

        :param event: An event from the event system (e.g., mouse click).
        """
        log(f"{name(self)}.handle_event({event})")

        # Check if the event is within the button's area
        if event.type == "mousedown" and self.abs_area.contains(event.pos):
            self._pressed = True
            if self.on_press_callback:
                self.on_press_callback(self)
            self.mark_dirty(self.area)

        elif event.type == "mouseup" and self._pressed:
            self._pressed = False
            if self.on_release_callback:
                self.on_release_callback(self)
            self.mark_dirty(self.area)

    def set_on_press(self, callback):
        """Set the callback function for when the button is pressed."""
        self.on_press_callback = callback

    def set_on_release(self, callback):
        """Set the callback function for when the button is released."""
        self.on_release_callback = callback

    def set_on_hold(self, callback):
        """Set the callback function for when the button is held down."""
        self.on_hold_callback = callback


class Label(Widget):
    def __init__(self, parent, text="", x=None, y=None, fg=-1):
        """
        Initialize a Label widget to display text.
        
        :param parent: The parent widget or screen that contains this label.
        :param text: The text content of the label.
        :param x: The x-coordinate of the label.
        :param y: The y-coordinate of the label.
        :param width: The width of the label.
        :param height: The height of the label.
        :param fg: The color of the text (in a suitable color format).
        """
        w = len(text) * 8  # Assume 8 pixels per character
        h = 8  # Fixed height for a single line of text
        super().__init__(parent, x, y, w, h, fg, parent.fg)
        self.text = text
        self.mark_dirty(self.area)

    def on_draw(self):
        """
        Draw the label's text on the screen, using absolute coordinates.
        """
        log(f"{name(self)}.on_draw()")
        if self.visible:
            abs_x, abs_y, _, _ = self.abs_area
            log(f"{name(self)}.on_draw() - Drawing at: {abs_x}, {abs_y}")
            self.draw_obj.text(self.text, abs_x, abs_y, self.fg)


def main():
    from board_config import display_drv, broker
    from eventsys.events import Events
    from palettes import get_palette
    # from widgets import Screen, Label, Button

    # Example usage of the widgets

    def on_button_press(button):
        print("Button pressed!")

    def on_button_release(button):
        print("Button released!")

    # Create the screen and button
    pal = get_palette()
    screen = Screen(display_drv, pal.RED)
    button = Button(screen, w=96, h=16, fg=pal.BLUE)
    label = Label(button, text="Click Me", fg=pal.GREEN)  # noqa: F841

    # Set button callbacks
    button.set_on_press(on_button_press)
    button.set_on_release(on_button_release)

    screen.draw()

    while True:
        if e := broker.poll():
            if e.type == Events.MOUSEBUTTONDOWN:
                screen.handle_event(e)

main()
