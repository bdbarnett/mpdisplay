from busdisplay import (
    BusDisplay,
    PORTRAIT,
    LANDSCAPE,
    REVERSE_PORTRAIT,
    REVERSE_LANDSCAPE,
)
from time import sleep_ms
from micropython import const


_SWRESET = const(0x01)
_SLPOUT = const(0x11)
_CSCON = const(0xF0)
_MADCTL = const(0x36)
_COLMOD = const(0x3A)
_DIC = const(0xB4)
_DFC = const(0xB6)
_DOCA = const(0xE8)
_PWR2 = const(0xC1)
_PWR3 = const(0xC2)
_VCMPCTL = const(0xC5)
_PGC = const(0xE0)
_NGC = const(0xE1)
_DISPON = const(0x29)


class ST7796(BusDisplay):
    # The st7795 display controller has an internal framebuffer
    # arranged in 320 x 480
    # configuration. Physical displays with pixel sizes less than
    # 320 x 480 must supply a start_x and
    # start_y argument to indicate where the physical display begins
    # relative to the start of the
    # display controllers internal framebuffer.

    # this display driver supports RGB565 and also RGB666. RGB666 is going to
    # use twice as much memory as the RGB565. It is also going to slow down the
    # frame rate by 1/3, This is becasue of the extra byte of data that needs
    # to get sent. To use RGB666 the color depth MUST be set to 32.
    # so when compiling
    # make sure to have LV_COLOR_DEPTH=32 set in LVFLAGS when you call make.
    # For RGB565 you need to have LV_COLOR_DEPTH=16

    # the reason why we use a 32 bit color depth is because of how the data gets
    # written. The entire 8 bits for each byte gets sent. The controller simply
    # ignores the lowest 2 bits in the byte to make it a 6 bit color channel
    # We just have to tell lvgl that we want to use

    display_name = "ST7796"

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)

    def init(self):
        param_buf = bytearray(14)
        param_mv = memoryview(param_buf)

        self.set_params(_SWRESET)

        sleep_ms(120)

        self.set_params(_SLPOUT)

        sleep_ms(120)

        param_buf[0] = 0xC3
        self.set_params(_CSCON, param_mv[:1])

        param_buf[0] = 0x96
        self.set_params(_CSCON, param_mv[:1])

        param_buf[0] = self._madctl(self._bgr, self._rotation, self.rotation_table)
        self.set_params(_MADCTL, param_mv[:1])

        if self._color_depth // 8 == 2:  # NOQA
            pixel_format = 0x55
        elif self._color_depth // 8 == 3:
            pixel_format = 0x77
        else:
            raise RuntimeError(
                "ST7796 IC only supports "
                "lv.COLOR_FORMAT.RGB565 or lv.COLOR_FORMAT.RGB888"
            )

        param_buf[0] = pixel_format
        self.set_params(_COLMOD, param_mv[:1])

        param_buf[0] = 0x01
        self.set_params(_DIC, param_mv[:1])

        param_buf[0] = 0x80
        param_buf[1] = 0x02
        param_buf[2] = 0x3B
        self.set_params(_DFC, param_mv[:3])

        param_buf[:8] = bytearray([0x40, 0x8A, 0x00, 0x00, 0x29, 0x19, 0xA5, 0x33])
        self.display_bus.tx_param(_DOCA, param_mv[:8])

        param_buf[0] = 0x06
        self.set_params(_PWR2, param_mv[:1])

        param_buf[0] = 0xA7
        self.set_params(_PWR3, param_mv[:1])

        param_buf[0] = 0x18
        self.set_params(_VCMPCTL, param_mv[:1])

        sleep_ms(120)

        param_buf[:14] = bytearray(
            [
                0xF0,
                0x09,
                0x0B,
                0x06,
                0x04,
                0x15,
                0x2F,
                0x54,
                0x42,
                0x3C,
                0x17,
                0x14,
                0x18,
                0x1B,
            ]
        )
        self.set_params(_PGC, param_mv[:14])

        param_buf[:14] = bytearray(
            [
                0xE0,
                0x09,
                0x0B,
                0x06,
                0x04,
                0x03,
                0x2B,
                0x43,
                0x42,
                0x3B,
                0x16,
                0x14,
                0x17,
                0x1B,
            ]
        )
        self.set_params(_NGC, param_mv[:14])

        sleep_ms(120)

        param_buf[0] = 0x3C
        self.set_params(_CSCON, param_mv[:1])

        param_buf[0] = 0x69
        self.set_params(_CSCON, param_mv[:1])

        sleep_ms(120)

        self.set_params(_DISPON)

        sleep_ms(120)

        super().init()
