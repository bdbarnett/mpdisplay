from gfx import Area, Draw
from eventsys.events import Events
DEBUG = True


def log(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def name(obj):
    return obj.__class__.__name__

_text_width = 8
_text_heights = (8, 14, 16)
_default_text_height = 16


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

    def add_child(self, screen):
        self.active_screen = screen

    def update(self):
        """
        Update only the dirty areas of the screen and its children.

        Uses self.draw_obj for drawing.
        """
        log(f"{name(self)}.update()")
        if self.active_screen is None:
            return
        
        if (dirty_area := self.active_screen.dirty_area) is None:
            return  # Nothing to redraw

        # Clear the dirty areas only
        # print(f"Clearing dirty area {dirty_area}")
        # self.display.fill_rect(*dirty_area, self.bg)

        # Draw widgets that intersect with the dirty areas
        self.active_screen.draw_dirty_widgets(dirty_area)

        # Update the display with the rendered content
        self.display_drv.show(dirty_area)

        # Clear the dirty areas list after updating
        self.active_screen.dirty_areas.clear()

    def handle_event(self, event):
        """
        Handle an event and propagate it to child widgets.
        
        :param event: An event from the event system (e.g., mouse or keyboard event).
        """
        log(f"{name(self)}.handle_event({event})")
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
        self.dirty_areas = []  # List to track areas that need to be redrawn
        self.fg = fg  # Foreground color of the widget
        self.bg = bg  # Background color of the widget
        self._value = value  # Value of the widget (e.g., text of a label)
        self.on_change_callback = None

        self.parent.add_child(self)

        self.mark_dirty(self.area)

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
        log(f"{name(self)}.handle_event({event})")
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
    def dirty_area(self):
        """
        Merge dirty areas into a single area for efficient redrawing.
        
        :return: A merged Area object.
        """
        if not self.dirty_areas:
            return None
        merged_area = self.dirty_areas[0]
        for area in self.dirty_areas[1:]:
            merged_area += area
        return merged_area

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

    def mark_dirty(self, area: Area):
        """
        Mark a specific area of the widget as dirty (needing redraw).
        
        :param area: An Area object representing the dirty area.
        """
        log(f"{name(self)}.mark_dirty({area})")
        self.dirty_areas.append(area)
        if type(self.parent) is not Display:
            rel_area = area.offset_by(self.x, self.y)  # Relative to the parent
            self.parent.mark_dirty(rel_area)  # Propagate up the hierarchy

    def draw_dirty_widgets(self, dirty_area):
        """
        Recursively draw widgets that intersect with dirty areas.

        :param dirty_area: The merged dirty areas (a list of Area objects).
        """
        if self.visible: #  and dirty_area.intersects(Area(self.x, self.y, self.width, self.height)):
            self.draw()  # Draw this widget if it intersects with dirty area

            # Draw child widgets if they intersect with dirty areas
            for child in self.children:
                child.draw_dirty_widgets(dirty_area)

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
        log(f"{name(self)}.draw()")
        if self.visible:
            self.draw_obj.fill_rect(*self.area, self.bg)


class Button(Widget):
    def __init__(self, parent: Widget, x=None, y=None, w=18, h=18, fg=0x0000FF, value=None,
                 radius=1, label=None, label_color=None, label_height=_default_text_height):
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
        self.on_press_callback = None
        self.on_hold_callback = None
        self.on_release_callback = None
        self.radius = radius
        self.pressed_offset = 1
        self.filled = True
        super().__init__(parent, x, y, w, h, fg, parent.bg, value)
        if label:
            if label_height not in _text_heights:
                raise ValueError("Text height must be 8, 14 or 16 pixels.")
            self.label = Label(self, value=label, fg=label_color or self.bg, h=label_height)

    def draw(self):
        """
        Draw the button background and any child widgets (like a label).
        """
        log(f"{name(self)}.draw()")
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
            log(f"{name(self)}.draw() - Drawing area: {area}")
            self.draw_obj.round_rect(*area, self.radius, self.fg, f=self.filled)

    def handle_event(self, event: Events.Any):
        """
        Handle user input events like clicks.

        :param event: An event from the event system (e.g., mouse click).
        """
        log(f"{name(self)}.handle_event({event})")

        # Check if the event is within the button's area
        if event.type == Events.MOUSEBUTTONDOWN and self.abs_area.contains(event.pos):
            self._pressed = True
            if self.on_press_callback:
                self.on_press_callback(self)
            self.mark_dirty(self.area)

        elif event.type == Events.MOUSEBUTTONUP and self._pressed:
            self._pressed = False
            if self.on_release_callback:
                self.on_release_callback(self)
            self.mark_dirty(self.area)

        # Propagate the event to the children of the button
        super().handle_event(event)


class Label(Widget):
    def __init__(self, parent: Widget, x=None, y=None, h=_default_text_height, fg=-1, value=""):
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
        if h not in _text_heights:
            raise ValueError("Text height must be 8, 14 or 16 pixels.")
        super().__init__(parent, x, y, len(value)*_text_width, h, fg, parent.fg, value)

    def draw(self):
        """
        Draw the label's text on the screen, using absolute coordinates.
        """
        log(f"{name(self)}.draw()")
        if self.visible:
            x, y, _, _ = self.abs_area
            log(f"{name(self)}.draw() - Drawing at: {x}, {y}")
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
        log(f"{name(self)}.draw()")
        if self.visible:
            x, y, _, _ = self.abs_area
            log(f"{name(self)}.draw() - Drawing at: {x}, {y}")
            self.draw_obj.fill_rect(*self.abs_area, self.bg)
            x += self.margin
            y += self.margin
            self.draw_obj.text(self.value, x, y, self.fg, height=self.text_height)

    def update_value(self):
        self.mark_dirty(self.area)


class ProgressBar(Widget):
    def __init__(self, parent: Widget, x=None, y=None, w=64, h=18, fg=0, bg=-1, value=0):
        """
        Initialize a ProgressBar widget to display a progress bar.
        
        :param parent: The parent widget or screen.
        :param x: The x-coordinate.
        :param y: The y-coordinate.
        :param width: The width.
        :param height: The height.
        :param fg: The color of the text (in a suitable color format).
        :param bg: The background color.
        :param value: The initial value of the progress bar (0 to 1).
        """
        super().__init__(parent, x, y, w, h, fg, bg, value)

    def draw(self):
        """
        Draw the progress bar on the screen.
        """
        log(f"{name(self)}.draw()")
        if self.visible:
            x, y, w, h = self.abs_area
            log(f"{name(self)}.draw() - Drawing at: {x}, {y}")
            self.draw_obj.fill_rect(*self.abs_area, self.bg)
            progress_width = int(self.value * self.width)
            self.draw_obj.fill_rect(x, y, progress_width, h, self.fg)

    def update_value(self):
        if self.on_change_callback:
            self.on_change_callback(self)
        self.mark_dirty(self.area)


def main():
    from board_config import broker # , display_drv
    from color_setup import ssd as display_drv
    # from eventsys.events import Events
    from palettes import get_palette
    # from widgets import Screen, Label, Button


    # Create the screen and button
    pal = get_palette()
    print(dir(pal))
    display = Display(display_drv, broker)
    screen = Screen(display, pal.SILVER)
    status = TextBox(screen, y=display.height-18, w=display.width)

    button1 = Button(screen, w=96, fg=pal.BLUE, value="button1")
    label = Label(button1, value="Click Me", fg=pal.WHITE)  # noqa: F841
    button1.set_on_press(lambda sender: setattr(status, 'value', f"{sender.value} pressed!"))
    button1.set_on_release(lambda sender: setattr(status, 'value', f"{sender.value} released!"))

    pbar = ProgressBar(screen, y=display.height-40, w=display.width//2, value=0.5)
    pbar.set_on_change(lambda sender: setattr(status, 'value', f"Progress: {sender.value:.0%}"))
    pbtn1 = Button(screen, x=pbar.x-18, y=pbar.y, fg=pal.GREEN, label="<")
    pbtn2 = Button(screen, x=pbar.x+pbar.width, y=pbar.y, fg=pal.GREEN, label=">")
    pbtn1.set_on_press(lambda sender: setattr(pbar, 'value', pbar.value-0.1))
    pbtn2.set_on_press(lambda sender: setattr(pbar, 'value', pbar.value+0.1))

    display.update()

    while True:
        if e := display.poll():
            if e.type in [Events.MOUSEBUTTONDOWN, Events.MOUSEBUTTONUP]:
                display.handle_event(e)
                display.update()

main()
