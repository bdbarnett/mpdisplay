
class Touchpad():
    LEFT = 1
    DOWN = 2
    RIGHT = 3
    CW = 4
    UP = 5
    CCW = 6
    START = 7
    UNUSED = 8
    PAUSE = 9
    
    def __init__(self, touch_read_func, width, height, touch_rotation=0):
        self._touch_read = touch_read_func
        self.width=width
        self.height=height
        self.set_touch_rotation(touch_rotation)

    def set_touch_rotation(self, touch_rotation):
        # Touch_rotation is an integer from 0 to 7 (3 bits)
        # Currently, bit 0 = invert_y, bit 1 is invert_x and bit 2 is swap_xy, but that may change
        # if I learn displays are consistent with their rotations and this doesn't match them.
        # Your display driver should have a way to set rotation before you add it to Devices,
        # but your touch driver may not have a way to set its rotation.  You can call this function
        # any time after you've created devices to change the rotation.
        self._touch_rotation = touch_rotation // 8 if touch_rotation else None
        self._invert_y = True if touch_rotation & 1 else False
        self._invert_x = True if touch_rotation >> 1 & 1 else False
        self._swap_xy = True if touch_rotation >> 2 & 1 else False
        self._max_x = self.width - 1
        self._max_y = self.height - 1

    def get_touched(self):
        # touch_read_func should return None, a point as a tuple (x, y), a point as a list [x, y] or 
        # a tuple / list of points ((x1, y1), (x2, y2)), [(x1, y1), (x2, y2)], ([x1, y1], [x2, y2]),
        # or [[x1, x2], [y1, y2]].  If it doesn't, create a wrapper around your driver's read function
        if touched := self._touch_read():
            # If it looks like a point, use it, otherwise get the first point out of the list / tuple
            (x, y) = touched if isinstance(touched[0], int) else touched[0]
            if self._touch_rotation is not None:
                if self._swap_xy:
                    x, y = y, x
                if self._invert_x:
                    x = self._max_x - x
                if self._invert_y:
                    y = self._max_y - y
            return x, y
        return None

    def read(self):
        try:
            point = self.get_touched()
        except OSError as error:
            # Not ready to read yet
            return None
        if point:
            x, y = point
            if x < self.width // 3:
                if y < self.height // 3:
                    return 7
                elif y > self.height * 2 // 3:
                    return 1
                else:
                    return 4
            elif x > self.width * 2 // 3:
                if y < self.height // 3:
                    return 9
                elif y > self.height * 2 // 3:
                    return 3
                else:
                    return 6
            else:
                if y < self.height // 3:
                    return 8
                elif y > self.height * 2 // 3:
                    return 2
                else:
                    return 5
        return None

if __name__ == "__main__":
    from machine import I2C, Pin
    from ft6x36 import FT6x36
    
    i2c = I2C(0, sda=Pin(6), scl=Pin(5), freq=100000)
    touch_drv = FT6x36(i2c)
    keypad = Touchpad(touch_drv.get_positions, width=320, height=480, touch_rotation=0)
    print(f"Type `keypad.read()` to get current position.")
