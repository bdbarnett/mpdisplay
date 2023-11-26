0) Add an mpdisplay_simpletest.py file to test the display without using LVGL
1) Change from SPI object being initialized in mpdisplay_esp.c to it being passed as an argement to mpdisplay.Spi_bus, eg:
    spi = machine.SPI(1, mosi=35, sck=36)
    bus = mpdisplay.Spi_bus(spi, dc=8, cs=17)
2) Move swap_color_bytes from bus constructor to Display constructor
ESP-IDF v4.4.6 has swap_color_bytes in esp_lcd_panel_io_i80_config_t, but no equivalent for SPI
ESP-IDF v5.1.2 has the above, but also adds data_endian to esp_lcd_panel_dev_config_t, which applies to SPI and i80
3) use esp_lcd_panel_dev_config_t .data_endian in IDF > 5.0 to swap color bytes - should take place of lv.COLOR.NATIVE_REVERSED which was removed in v9.0
4) Add an arg for CAP.  Currently hardcoded to MALLOC_CAP_DMA
Options are: MALLOC_CAP_DMA, _32bit, _8bit, _DMA, _SPIRAM, _INTERNAL, _DEFAULT, _IRAM_8BIT, _TCM
5) Possibly switch to heap_caps_aligned_alloc (32-bit / 4 byte alignment).
Not sure if this is necessary.  Currently hardcoded to heap_caps_alloc
6) create a flush_cb wrapper for blit in C instead of using Python flush_cb
7) Consider adding I2c_bus
8) Consider adding Monochrome displays
9) Move lvmp_devices to its own repo for use with other display drivers
10) add encoders to example display_driver.py
