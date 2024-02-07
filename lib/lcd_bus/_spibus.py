# SPDX-FileCopyrightText: 2023 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
lcd_bus.py - a MicroPython library for interfacing with displays using SPI or I80

Provides similar functionality to lcd_bus from lv_binding_micropython for platforms
other than ESP32
"""

import micropython
import machine
import struct
from ._basebus import BaseBus, Optional


class SPIBus(BaseBus):
    """
    SPI bus implementation of the base bus.

    Args:
        dc (int): The pin number for the data/command pin.
        host (int, optional): The SPI host number. Defaults to 2.
        mosi (int, optional): The pin number for the MOSI pin. Defaults to -1.
        miso (int, optional): The pin number for the MISO pin. Defaults to -1.
        sclk (int, optional): The pin number for the SCLK pin. Defaults to -1.
        cs (int, optional): The pin number for the CS pin. Defaults to -1.
        freq (int, optional): The SPI clock frequency in Hz. Defaults to -1.
        tx_only (bool, optional): Whether to use transmit-only mode. Defaults to False.
        cmd_bits (int, optional): The number of bits for command transmission. Defaults to 8.
        param_bits (int, optional): The number of bits for parameter transmission. Defaults to 8.
        dc_low_on_data (bool, optional): Whether the data/command pin is low for data. Defaults to False.
        lsb_first (bool, optional): Whether to transmit LSB first. Defaults to False.
        cs_high_active (bool, optional): Whether the CS pin is active high. Defaults to False.
        spi_mode (int, optional): The SPI mode. Defaults to 0.
        wp (int, optional): The pin number for the write protect pin. Not yet supported. Defaults to -1.
        hd (int, optional): The pin number for the hold pin. Not yet supported. Defaults to -1.
        quad_spi (bool, optional): Whether to use quad SPI mode. Defaults to False.
        sio_mode (bool, optional): Whether to use SIO mode. Defaults to False.
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
        freq: int = -1,
        *,
        tx_only: bool = False,
        cmd_bits: int = 8,
        param_bits: int = 8,
        dc_low_on_data: bool = False,
        lsb_first: bool = False,
        cs_high_active: bool = False,
        spi_mode: int = 0,
        wp: int = -1,  # Not yet suppported
        hd: int = -1,  # Not yet supported
        quad_spi: bool = False,  # Not yet supported
        sio_mode: bool = False,  # Not yet supported
    ) -> None:
        """
        Initialize the SPI bus with the given parameters.
        """
        super().__init__()

        self._dc_cmd: bool = dc_low_on_data
        self._dc_data: bool = not dc_low_on_data

        self._cs_active: bool = cs_high_active
        self._cs_inactive: bool = not cs_high_active

        self.dc: machine.Pin = machine.Pin(dc, machine.Pin.OUT, value=self._dc_cmd)
        self.cs: machine.Pin = (
            machine.Pin(cs, machine.Pin.OUT, value=self._cs_inactive) if cs != -1 else lambda val: None
        )

        if mosi == -1 and miso == -1 and sclk == -1:
            self.spi: machine.SPI = machine.SPI(
                host,
                baudrate=freq,
                polarity=spi_mode & 0b10,
                phase=spi_mode & 0b01,
                bits=max(cmd_bits, param_bits),
                firstbit=machine.SPI.LSB if lsb_first else machine.SPI.MSB,
            )
        else:
            self.spi: machine.SPI = machine.SPI(
                host,
                baudrate=freq,
                polarity=spi_mode & 0b10,
                phase=spi_mode & 0b01,
                bits=max(cmd_bits, param_bits),
                firstbit=machine.SPI.LSB if lsb_first else machine.SPI.MSB,
                sck=machine.Pin(sclk, machine.Pin.OUT),
                mosi=machine.Pin(mosi, machine.Pin.OUT),
                miso=machine.Pin(miso, machine.Pin.IN) if not tx_only else None,
            )

        self._write = self.spi.write

    @micropython.native
    def tx_param(
        self,
        cmd: Optional[int] = None,
        data: Optional[memoryview] = None,
    ) -> None:
        """
        Transmit parameters over the SPI bus.
        """
        self.cs(self._cs_active)

        if cmd is not None:
            struct.pack_into("B", self.buf1, 0, cmd)
            self.dc(self._dc_cmd)
            self._write(self.buf1)
        if data and len(data):
            self.dc(self._dc_data)
            self._write(data)

        self.cs(self._cs_inactive)
