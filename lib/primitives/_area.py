
class Area:
    def __init__(self, x, y, w, h):
        self._x = x
        self._y = y
        self._w = w
        self._h = h

    def __repr__(self):
        return f"Area({self.x}, {self.y}, {self.w}, {self.h})"
    
    def __str__(self):
        return f"Area({self.x}, {self.y}, {self.w}, {self.h})"
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __add__(self, other):
        return Area(
            min(self.x, other.x),
            min(self.y, other.y),
            max(self.x + self.w, other.x + other.w) - min(self.x, other.x),
            max(self.y + self.h, other.y + other.h) - min(self.y, other.y)
        )
    
    def __len__(self):
        return 4

    def __iter__(self):
        return iter((self.x, self.y, self.w, self.h))

    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
    
    @property
    def w(self):
        return self._w
    
    @property
    def h(self):
        return self._h
 
