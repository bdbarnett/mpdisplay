# SPDX-FileCopyrightText: 2023 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
An implementation of a SPI bus driver written in MicroPython.
"""

from machine import Pin, SPI # type: ignore
import struct
import micropython
from micropython import const


DC_CMD = const(0)
DC_DATA = const(1)
CS_ACTIVE = const(0)
CS_INACTIVE = const(1)


class Optional:  # For typing
    pass

class SPIBus():
    def __init__(
        self,
        *,
        id: int = 2,
        baudrate: int = 24_000_000,
        polarity: int = 0,
        phase: int = 0,
        bits: int = 8,
        lsb_first: bool = False,
        sck: int = -1,
        mosi: int = -1,
        miso: int = -1,
        dc: int = -1,
        cs: int = -1,
        ) -> None:

        if dc == -1:
            raise ValueError("DC pin must be specified")
        
        self._baudrate = baudrate
        self._polarity = polarity
        self._phase = phase
        self._bits = bits
        self._firstbit = SPI.LSB if lsb_first else SPI.MSB

        if mosi == -1 and miso == -1 and sck == -1:
            self._spi: SPI = SPI(
                id,
                baudrate=self._baudrate,
                polarity=self._polarity,
                phase=self._phase,
                bits=self._bits,
                firstbit=self._firstbit,
            )
        else:
            self._spi: SPI = SPI(
                id,
                baudrate=self._baudrate,
                polarity=self._polarity,
                phase=self._phase,
                bits=self._bits,
                firstbit=self._firstbit,
                sck=Pin(sck, Pin.OUT),
                mosi=Pin(mosi, Pin.OUT),
                miso=Pin(miso, Pin.IN) if miso > -1 else None,
            )

        # DC and CS pins must be set AFTER the SPI bus is initialized on some boards
        self._dc: Pin = Pin(dc, Pin.OUT, value=DC_DATA)
        self._cs: Pin = Pin(cs, Pin.OUT, value=CS_INACTIVE) if cs != -1 else lambda val: None

        self._buf1: bytearray = bytearray(1)

    @micropython.native
    def send(
        self,
        command: Optional[int] = None,
        data: Optional[memoryview] = None,
    ) -> None:
        self._spi.init(
            baudrate=self._baudrate,
            polarity=self._polarity,
            phase=self._phase,
            bits=self._bits,
            firstbit=self._firstbit,
        )

        self._cs(CS_ACTIVE)

        if command is not None:
            struct.pack_into("B", self._buf1, 0, command)
            self._dc(DC_CMD)
            self._spi.write(self._buf1)

        if data and len(data):
            self._dc(DC_DATA)
            self._spi.write(data)

        self._cs(CS_INACTIVE)

    def deinit(self):
        self._spi.deinit()

    def __del__(self):
        self.deinit()
