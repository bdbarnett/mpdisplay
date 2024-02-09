from ._i80bus import I80Bus as _I80Bus
from rp2 import DMA, PIO, StateMachine, asm_pio


class I80Bus(_I80Bus):
    """
    I80Bus for the RP2 using DMA transfers.
    """
    def __init__(self, *args, **kwargs) -> None:
        print("Using _i80bus_rp2.py")
        super().__init__(*args, **kwargs)

    @asm_pio(set_init=PIO.OUT_LOW)
    def _i80bus_pio() -> None:
        """
        PIO state machine for the I80 bus.
        """
        # set the state machine to the initial state
        set(pins, 0)
        set(pins, 1)
        set(pins, 0)
        set(pins, 1)

        # wait for the data to be ready
        wait(1, pin, 0)

        # read the data
        in_(pins, 8)

        # wait for the data to be read
        wait(1, pin, 1)

        # set the state machine to the final state
        set(pins, 0)
        set(pins, 1)
        set(pins, 0)
        set(pins, 1)

    def setup(self, pins: list[int], wr: int) -> None:
        """
        Configure the rp2 PIO, DMA, and state machines to drive the data bus and control lines.
        """
        # verify there are exactly 8 pins
        if len(pins) != 8:
            raise ValueError("There must be exactly 8 data pins.")
        # verify that the pins are consecutive
        if not all(pins[i] + 1 == pins[i + 1] for i in range(len(pins) - 1)):
            raise ValueError("The pins must be consecutive.")
        
        # create the state machine
        self.sm = StateMachine(0, self._i80bus_pio, freq=100_000_000, set_base=PIO(0))
        self.sm.active(1)

        # create the DMA channel
        self.dma = DMA(0, self.sm, self._dma_channel)
        self.dma.start()

    def _write(self, data: memoryview, len: int) -> None:
        """
        Write the data to the display.
        """
        self.dma.write(data, len)
        self.dma.wait()