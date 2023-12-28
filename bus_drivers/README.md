# Generic Bus Drivers written in MicroPython

Note: DO NOT use this driver if you are using lv_binding_micropython on ESP32.  The lcd_bus drivers included in the binding are written in C and use DMA memory access.  They are MUCH faster than these drivers.

The lcd_bus.py driver provides a SPIBus (and future I80Bus) driver that is not optimized for any particular platform.  Use this driver if you are not using an ESP32 on lv_binding_micropython.

The rgb565_swap_bytes function is particularly slow in MicroPython.  If your board_config requires `reverse_bytes_in_word=True` to show the correct colors, you will have degraded performance versus setting `reverse_bytes_in_word=False`. 

# Usage:
Save `lcd_bus.py` in your lib folder and follow the remaining directions at the root of this repository.
