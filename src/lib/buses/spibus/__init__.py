# SPDX-FileCopyrightText: 2023 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
An implementation of a SPI bus driver written in MicroPython.
"""

from machine import Pin, SPI # type: ignore
import struct
import micropython  # type: ignore


class Optional:  # For typing
    pass


class SPIBus():
    """
    SPI bus implementation of the base bus.

    :param dc: The pin number for the data/command pin.
    :type dc: int
    :param host: The SPI host number. Defaults to 2.
    :type host: int, optional
    :param mosi: The pin number for the MOSI pin. Defaults to -1.
    :type mosi: int, optional
    :param miso: The pin number for the MISO pin. Defaults to -1.
    :type miso: int, optional
    :param sclk: The pin number for the SCLK pin. Defaults to -1.
    :type sclk: int, optional
    :param cs: The pin number for the CS pin. Defaults to -1.
    :type cs: int, optional
    :param freq: The SPI clock frequency in Hz. Defaults to -1.
    :type freq: int, optional
    :param tx_only: Whether to use transmit-only mode. Defaults to False.
    :type tx_only: bool, optional
    :param cmd_bits: The number of bits for command transmission. Defaults to 8.
    :type cmd_bits: int, optional
    :param param_bits: The number of bits for parameter transmission. Defaults to 8.
    :type param_bits: int, optional
    :param dc_low_on_data: Whether the data/command pin is low for data. Defaults to False.
    :type dc_low_on_data: bool, optional
    :param lsb_first: Whether to transmit LSB first. Defaults to False.
    :type lsb_first: bool, optional
    :param cs_high_active: Whether the CS pin is active high. Defaults to False.
    :type cs_high_active: bool, optional
    :param spi_mode: The SPI mode. Defaults to 0.
    :type spi_mode: int, optional
    :param wp: The pin number for the write protect pin. Not yet supported. Defaults to -1.
    :type wp: int, optional
    :param hd: The pin number for the hold pin. Not yet supported. Defaults to -1.
    :type hd: int, optional
    :param quad_spi: Whether to use quad SPI mode. Defaults to False.
    :type quad_spi: bool, optional
    :param sio_mode: Whether to use SIO mode. Defaults to False.
    :type sio_mode: bool, optional
    """
    name = "MicroPython SPIBus driver"

    def __init__(
        self,
        dc: int,
        host: int = 2,
        mosi: int = -1,
        miso: int = -1,
        sclk: int = -1,
        cs: int = -1,
        baudrate: int = 10_000_000,
        tx_only: bool = True,
        lsb_first: bool = False,
        spi_mode: int = 0,
        ) -> None:
        """
        Initialize the SPI bus with the given parameters.
        """
        self._buf1: bytearray = bytearray(1)

        self._dc_cmd: bool = False
        self._dc_data: bool = True

        self._cs_active: bool = False
        self._cs_inactive: bool = True

        self._baudrate: int = baudrate
        self._polarity = spi_mode & 0b10
        self._phase = spi_mode & 0b01
        self._bits = 8
        self._firstbit = SPI.LSB if lsb_first else SPI.MSB

        if mosi == -1 and miso == -1 and sclk == -1:
            self._spi: SPI = SPI(
                host,
                baudrate=self._baudrate,
                polarity=self._polarity,
                phase=self._phase,
                bits=8,
                firstbit=SPI.LSB if lsb_first else SPI.MSB,
            )
        else:
            self._spi: SPI = SPI(
                host,
                baudrate=baudrate,
                polarity=spi_mode & 0b10,
                phase=spi_mode & 0b01,
                bits=8,
                firstbit=SPI.LSB if lsb_first else SPI.MSB,
                sck=Pin(sclk, Pin.OUT),
                mosi=Pin(mosi, Pin.OUT),
                miso=Pin(miso, Pin.IN) if not tx_only else None,
            )

        # DC and CS pins must be set AFTER the SPI bus is initialized on some boards
        self._dc: Pin = Pin(dc, Pin.OUT, value=self._dc_data)
        self._cs: Pin = Pin(cs, Pin.OUT, value=self._cs_inactive) if cs != -1 else lambda val: None

    @micropython.native
    def send(self, cmd: Optional[int] = None, data: Optional[memoryview] = None) -> None:
        """
        Transmit parameters over the bus.

        :param cmd: Command to send before the data
        :type cmd: int
        :param data: Parameter data
        :type data: memoryview
        """

        self._spi.init(
            baudrate=self._spi.baudrate,
            polarity=self._spi.polarity,
            phase=self._spi.phase,
            bits=self._spi.bits,
            firstbit=self._spi.firstbit,
        )

        self._cs(self._cs_active)

        if cmd is not None:
            struct.pack_into("B", self._buf1, 0, cmd)
            self._dc(self._dc_cmd)
            self._spi.write(self._buf1)

        if data and len(data):
            self._dc(self._dc_data)
            self._spi.write(data)

        self._cs(self._cs_inactive)

    def deinit(self):
        """ Deinitialize the SPI bus. """
        self._spi.deinit()
        self._dc = None
        self._cs = None
        self._spi = None
        self._buf1 = None

    def __del__(self):
        """
        Deinitialize the bus.
        """
        self.deinit()
