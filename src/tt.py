# An example of using the SDL2 library to create a timer
import sys
if sys.implementation.name == "micropython":
    import ffi

    _libSDL2 = ffi.open("libSDL2-2.0.so.0")
    SDL_Init = _libSDL2.func("i", "SDL_Init", "I")
    SDL_AddTimer = _libSDL2.func("P", "SDL_AddTimer", "IPP")

    def SDL_TimerCallback(func):
        return ffi.callback("I", func, "IP")

else:
    import ctypes
    if sys.platform == "win32":
        _libSDL2 = ctypes.CDLL("SDL2.dll")
    else:
        _libSDL2 = ctypes.CDLL("libSDL2-2.0.so.0")

    _libSDL2.SDL_Init.argtypes = [ctypes.c_uint]
    _libSDL2.SDL_Init.restype = ctypes.c_int
    SDL_Init = _libSDL2.SDL_Init

    _libSDL2.SDL_AddTimer.argtypes = [ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
    _libSDL2.SDL_AddTimer.restype = ctypes.c_void_p
    SDL_AddTimer = _libSDL2.SDL_AddTimer

    _libSDL2.SDL_RemoveTimer.argtypes = [ctypes.c_void_p]
    _libSDL2.SDL_RemoveTimer.restype = ctypes.c_int
    SDL_RemoveTimer = _libSDL2.SDL_RemoveTimer

    SDL_TimerCallback = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p)

SDL_INIT_TIMER = 0x00000001

def test_func(interval, param):
    print("Timer callback called with interval", interval)
    return interval

SDL_Init(SDL_INIT_TIMER)
tcb = SDL_TimerCallback(test_func)
SDL_AddTimer(1000, tcb, None)
