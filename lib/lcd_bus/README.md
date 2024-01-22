# Generic Bus Drivers written in MicroPython

Note: DO NOT use these drivers if you are using LVGL_MicroPython on ESP32.  The lcd_bus drivers included there are written in C and use DMA memory access.  They are MUCH faster than these drivers.

The lcd_bus.py driver provides a SPIBus driver that is not optimized for any particular platform.

The i80bus.py driver provides an I80 driver that is not optimized for any particular platform, but it is slow, limited to only 8 bit bus widths, and requires a platform that uses pin numbers (ESP32, RP2, SAMD and NRF) instead of pin names (STM32, MIMXRT and Renesas-RA).  While it can be used if there are no other faster options, it is meant as a reference for future creation of platform-specific drivers written in C.

If your board_config requires `reverse_bytes_in_word=True` to show the correct colors, you will have degraded performance in base MicroPython versus setting `reverse_bytes_in_word=False`.  lv_driver_framework.py checks to see if it is set true, and if it is, it uses lvgl's `lv.draw_sw_rgb565_swap` function in `_flush_cb`, and performance is much faster.

# Usage:
For displays with a SPI bus, save `lcd_bus.py` in your lib folder and follow the remaining directions at the root of this repository.  For displays with an 8-bit I80 bus on suppported platforms, you will also need `i80bus.py` and `gpio_registers.py` in your lib folder.
