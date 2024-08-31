# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
PSDisplay class for MPDisplay on PyScript
"""

from basedisplay import BaseDisplay, Area, color_rgb
from pyscript.ffi import create_proxy # type: ignore
from js import document, console # type: ignore


def log(*args):
    console.log(*args)


class PSDevices():
    def __init__(self, id):
        self.canvas = document.getElementById(id)
        self._mouse_pos = None

#         self.canvas.oncontextmenu = self._no_context

        # Proxy functions are required for javascript
        self.on_down = create_proxy(self._on_down)
        self.on_up = create_proxy(self._on_up)
        self.on_move = create_proxy(self._on_move)
        self.on_enter = create_proxy(self._on_enter)
        self.on_leave = create_proxy(self._on_leave)

        self.canvas.addEventListener("mousedown", self.on_down)
        self.canvas.addEventListener("mouseup", self.on_up)
        self.canvas.addEventListener("mousemove", self.on_move)
        self.canvas.addEventListener("mouseenter", self.on_enter)
        self.canvas.addEventListener("mouseleave", self.on_leave)

    def get_mouse_pos(self):
        return self._mouse_pos

    def _on_down(self, e):
        if e.button == 0: #left mouse button
            log(f"Mouse down {e.offsetX}, {e.offsetY}")
            self._mouse_pos = (e.offsetX, e.offsetY)
        else:
            return False

    def _on_up(self, e):
        if e.button == 0: #left mouse button
            log(f"Mouse up {e.offsetX}, {e.offsetY}")
            self._mouse_pos = None
        else:
            return False

    def _on_move(self, e):
        if e.buttons & 1:
            log(f"Mouse move {e.offsetX}, {e.offsetY}")
            self._mouse_pos = (e.offsetX, e.offsetY)

    def _on_enter(self, e):
        log("Mouse enter")

    def _on_leave(self, e):
        log("Mouse leave")
        self._mouse_pos = None
        
    def _no_context(self, e):
        e.preventDefault()
        e.stopPropagation()
        return False


class PSDisplay(BaseDisplay):
    '''
    A class to interface with canvas objects in PyScript.
    '''

    def __init__(self, id, width=None, height=None):
        """
        Initializes the display instance with the given parameters.
        """
        super().__init__()
        self._canvas = document.getElementById(id)
        self._ctx = self._canvas.getContext("2d")
        self._width = width or self._canvas.width
        self._height = height or self._canvas.height
        self._requires_byte_swap = False
        self._auto_byte_swap_enabled = self._requires_byte_swap
        self._rotation = 0
        self.color_depth = 16
        self._draw = self._ctx

        self.init()

    ############### Required API Methods ################

    def init(self):
        """
        Initializes the display instance.  Called by __init__ and rotation setter.
        """
        self._canvas.width = self.width
        self._canvas.height = self.height

    def fill_rect(self, x, y, w, h, c):
        r, g, b = color_rgb(c)
        self._ctx.fillStyle = f"rgb({r},{g},{b})"
        self._ctx.fillRect(x, y, w, h)
        return Area(x, y, w, h)

    def blit_rect(self, buf, x, y, w, h):
        BPP = self.color_depth // 8
        if x < 0 or y < 0 or x + w > self.width or y + h > self.height:
            raise ValueError("The provided x, y, w, h values are out of range")
        if len(buf) != w * h * BPP:
            raise ValueError("The source buffer is not the correct size")
        img_data = self._ctx.createImageData(w, h)
        for i in range(0, len(buf), BPP):
            r, g, b = color_rgb(buf[i: i + BPP])
            j = i * 2
            img_data.data[j] = r
            img_data.data[j+1] = g
            img_data.data[j+2] = b
            img_data.data[j+3] = 255
        self._ctx.putImageData(img_data, x, y)
        return Area(x, y, w, h)

    def pixel(self, x, y, c):
        self.fill_rect(x, y, 1, 1, c)
        return Area(x, y, 1, 1)
