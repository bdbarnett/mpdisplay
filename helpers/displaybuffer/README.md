# DisplayBuffer
DisplayBuffer class for MPDisplay - presents the display as a FrameBuffer object. Provides compatibility with Nano-GUI, Micro-GUI and MicroPython-GUI, but is not limited to those libraries.

For use in Nano-GUI, you MAY want to edit `color_setup.py` to:
- Change the mode to save RAM.  The fewer the number of colors, the less RAM is taken at the expense of a slight increase in refresh time.
  	- `mode = framebuf.RGB565` yields 65,536 colors; creates a frame buffer of size width * height * 2 bytes.  No bounce buffer is needed.  This is the fastest mode.
  	- `mode = framebuf.GS8` yields 256 colors; creates a frame buffer of size width * height bytes and a bounce buffer of size width * 2 bytes.  This is the slowest mode.
  	- `mode = framebuf.GS4_HMSB` yields 16 colors; creates a frame buffer of size width * height // 2 bytes and a bounce buffer of size width * 2 bytes.  This is somewhat slow.
- Rename it to hardware_setup.py, add pin definitions and configure `Display` for use with [Micro-GUI](https://github.com/peterhinch/micropython-micro-gui)

For use in MicroPython-GUI, you may want to make the `mode` change mentioned above to `hardware_setup.py`.
