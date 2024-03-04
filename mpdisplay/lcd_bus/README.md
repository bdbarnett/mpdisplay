# Generic Bus Drivers written in MicroPython

Note: DO NOT use these drivers if you are using LVGL_MicroPython on ESP32.  The lcd_bus drivers included there are written in C and use DMA memory access.  They are MUCH faster than these drivers.

This package provide generic SPIBus and I80Bus drivers.  Platform-specific drivers can be added, such as _spibus_rp2.py or _i80bus_eps32.py.  The I80Bus driver is slow, limited to only 8 bit bus widths, and requires a platform that uses pin numbers (ESP32, RP2, SAMD and NRF) instead of pin names (STM32, MIMXRT and Renesas-RA).  While it can be used if there are no other faster options, it is meant as a reference for future creation of platform-specific drivers.

If your board_config requires `reverse_bytes_in_word=True` to show the correct colors, you will have degraded performance in base MicroPython versus setting `reverse_bytes_in_word=False`.  lv_mpdisplay.py and gui_framework.py check to see if it is set true, and if it is, it uses lvgl's `lv.draw_sw_rgb565_swap` function in `_flush_cb` gui_framework.py's functions for byte swapping, and performance is much faster.
