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
