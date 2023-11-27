# To do:
0) Learn Markdown so the documentation isn't hideous!!!!!
1) Change from SPI object being initialized in mpdisplay_esp.c to it being passed as an argement to mpdisplay.Spi_bus, eg:
    - spi = machine.SPI(1, mosi=35, sck=36)
    - bus = mpdisplay.Spi_bus(spi, dc=8, cs=17)
2) Move swap_color_bytes from bus constructor to Display constructor
3) use esp_lcd_panel_dev_config_t .data_endian in IDF > 5.0 to swap color bytes - should take place of lv.COLOR.NATIVE_REVERSED which was removed in v9.0
    - ESP-IDF v4.4.6 has swap_color_bytes in esp_lcd_panel_io_i80_config_t, but no equivalent for SPI
    - ESP-IDF v5.1.2 has the above, but also adds data_endian to esp_lcd_panel_dev_config_t, which applies to SPI and i80
4) Document `caps` argument to mpdisplay.allocate_buffers.  Defaults to MALLOC_CAP_DMA.
    - Options are in mpdisplay.CAPS: EXEC, 32BIT, 8BIT, DMA, SPIRAM, INTERNAL, DEFAULT, IRAM_8BIT, RETENTION, RTCRAM
    - must use a lambda in lvmp_devices, like:
    - display=Display(alloc_buf_func = lambda size: mpdisplay.allocate_buffer(size, mpdisplay.CAPS.SPIRAM)
5) create a flush_cb wrapper for blit in C instead of using Python flush_cb
    - Currently a Micropython function is required to convert the parameters LVGL sends to the arguments blit accepts:
    - coming in from LVGL:  display, area, color as bytearray
    - required by blit:  area.x1, area.y1, w:=(area.x2-area.x1+1), h:=(area.y2-area.y1+1), color as bytearray or memoryview
6) Consider adding I2c_bus
7) Consider adding Monochrome displays

