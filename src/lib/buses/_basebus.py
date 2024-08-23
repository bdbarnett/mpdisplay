# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

'''
lcd_bus - Provides MicroPython drivers for SPI and I80 display buses similiar to the
https://github.com/kdschlosser/lcd_bus written in C.

Attempts to load a platform-specific module such as _i80bus_rp2 or _spibus_esp32 first,
then falls back to a generic module such as _i80bus or _spibus if the platform-specific
module doesn't exist.  This prevents loading unused modules.

Lazy loader for on the fly loading of attributes.  See:
https://peps.python.org/pep-0562/
and 
https://github.com/peterhinch/micropython-samples/blob/master/import/IMPORT.md#2-python-packages-and-the-lazy-loader
'''
import struct
import micropython


class Optional:  # For typing
    pass


class BaseBus:
    """
    Base class for bus communication. This class is meant to be subclassed by 
    specific bus implementations.
    """
    name = "MicroPython bus driver"
    warn_byte_swap = True

    def __init__(self) -> None:
        """
        Initialize the base bus.
        """
        self.buf1: bytearray = bytearray(1)
        self.buf2: bytearray = bytearray(2)
        self.callback: callable = lambda : None
        self.swap_bytes: callable = self._no_swap
        self.trans_done: bool = True
        self._swap_enabled: bool = False

    def init(
        self,
        width: int,  # Not used; maintained for compatibility with mp_lcd_bus C driver
        height: int,  # Not used; maintained for compatibility with mp_lcd_bus C driver
        bpp: int,
        buffer_size: int,  # Not used; maintained for compatibility with mp_lcd_bus C driver
        rgb565_byte_swap: bool,
        ) -> None:
        """
        Initialize the bus with the given parameters.

        :param width: Width of the display in pixels
        :type width: int
        :param height: Height of the display in pixels
        :type height: int
        :param bpp: Bits per pixel
        :type bpp: int
        :param buffer_size: Size of the buffer in bytes
        :type buffer_size: int
        :param rgb565_byte_swap: Enable or disable color byte swapping
        :type rgb565_byte_swap: bool
        """
        self._bpp = bpp
        self.enable_swap(rgb565_byte_swap or self._swap_enabled)

    def enable_swap(self, enable: Optional[bool] = None) -> bool:
        """
        Enable or disable color byte swapping.  Returns the current state of the setting.

        :param enable: Enable or disable color byte swapping
        :type enable: bool
        :return: Current state of the setting
        :rtype: bool
        """
        if enable is not None:
            if enable and self._bpp == 16:
                self._swap_enabled = True
                self.swap_bytes = self._swap_bytes
                if self.warn_byte_swap:
                    print("\nWARNING: Bus driver byte swap is enabled. This may be slow.")
            else:
                self._swap_enabled = False
                self.swap_bytes = self._no_swap
                if self.warn_byte_swap:
                    print("Bus driver byte swap has been disabled.")
        return self._swap_enabled

    @micropython.viper
    def _swap_bytes(self, buf: ptr8, buf_size_px: int):  # type: ignore # noqa: F821
        """
        Swap the bytes in a buffer of RGB565 data.

        :param buf: Buffer of RGB565 data
        :type buf: ptr8
        :param buf_size_px: Size of the buffer in pixels
        :type buf_size_px: int
        """
        for i in range(0, buf_size_px * 2, 2):
            tmp = buf[i]
            buf[i] = buf[i + 1]
            buf[i + 1] = tmp

    @micropython.viper
    def _no_swap(self, buf: ptr8, buf_size_px: int):  # type: ignore # noqa: F821
        """
        Do nothing.  This function is used when byte swapping is disabled.

        :param buf: Buffer of RGB565 data
        :type buf: ptr8
        :param buf_size_px: Size of the buffer in pixels
        :type buf_size_px: int
        """
        return

    def register_callback(self, callback: callable) -> None:
        """
        Register a callback function to be called when a transaction is done.

        :param callback: Callback function
        :type callback: callable
        """
        self.callback = callback

    @micropython.viper
    def _tx_color_done_cb(self) -> bool:
        """
        Callback function to be called when a transaction is done.

        :return: False
        """
        self.callback()
        self.trans_done = True
        return False  # Returns false for compatibility with mp_lcd_bus C driver

    @micropython.native
    def tx_color(self, cmd: int, data: memoryview, x_start: int, y_start: int, x_end: int, y_end: int) -> None:
        """
        Transmit color data over the bus.

        :param cmd: Command to send before the data
        :type cmd: int
        :param data: Color data
        :type data: memoryview
        :param x_start: Starting x coordinate
        :type x_start: int
        :param y_start: Starting y coordinate
        :type y_start: int
        :param x_end: Ending x coordinate
        :type x_end: int
        :param y_end: Ending y coordinate
        :type y_end: int
        """
        self.trans_done = False
        self.swap_bytes(data, len(data) // 2)
        self.tx_param(cmd, data)
        self._tx_color_done_cb()

    @micropython.native
    def tx_param(self, cmd: Optional[int] = None, data: Optional[memoryview] = None) -> None:
        """
        Transmit parameters over the bus.

        :param cmd: Command to send before the data
        :type cmd: int
        :param data: Parameter data
        :type data: memoryview
        """

        self.cs(self._cs_active)

        if cmd is not None:
            struct.pack_into("B", self.buf1, 0, cmd)
            self.dc(self._dc_cmd)
            self._write(self.buf1, 1)

        if data and len(data):
            self.dc(self._dc_data)
            self._write(data, len(data))

        self.cs(self._cs_inactive)

    def rx_param(self, cmd: int, data: memoryview) -> int:
        """
        Receive parameters. Not yet implemented.

        :param cmd: Command to send before the data
        :type cmd: int
        :param data: Parameter data
        :type data: memoryview
        """
        raise NotImplementedError("rx_param not implemented.  Drivers are write-only.")

    def allocate_framebuffer(self, size: int, caps: int):
        """
        Allocate a framebuffer of the given size and memory capabilities.

        Note:  This function in mp_lcd_bus will throw an exception if more than 2 buffers are allocated,
        so do not use it for more than 2 buffers if you want your code to be compatible with mp_lcd_bus.

        :param size: Size of the buffer in bytes
        :type size: int
        :param caps: Memory capabilities.  Not used.  Maintains compatibility with mp_lcd_bus's allocate_framebuffer
        :type caps: int
        """
        return memoryview(bytearray(size))

    def deinit(self):
        """
        Deinitialize the bus.
        """
        self.buf1 = None
        self.buf2 = None
        self.callback = None
        self.swap_bytes = None
        self.trans_done = None
        self._swap_enabled = None
    
    def __del__(self):
        """
        Deinitialize the bus.
        """
        self.deinit()
