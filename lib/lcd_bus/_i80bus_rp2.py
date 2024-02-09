from ._i80bus import I80Bus as _I80Bus
from rp2 import PIO, StateMachine, asm_pio


class I80Bus(_I80Bus):
    """
    I80Bus for the RP2 using DMA transfers.
    """
    def __init__(self, *args, **kwargs) -> None:
        print("Using _i80bus_rp2.py")
        super().__init__(*args, **kwargs)

    @asm_pio(out_init=[PIO.OUT_LOW]*8, sideset_init=PIO.OUT_LOW, in_shiftdir=0, out_shiftdir=0,
             autopush=False, autopull=False, push_thresh=32, pull_thresh=8, fifo_join=PIO.JOIN_NONE)
    def _i80bus_pio() -> None:
        """
        PIO state machine for the I80 bus.
        """
        # set the state machine to the initial state
        wrap_target()
        pull(block)             .side(0)
        label("out8")
        out(pins, 8)            .side(0)
        jmp(osre, "continue")   .side(0)
        jmp("out8")             .side(0)
        label("continue")
        irq(rel(0))             .side(0)      # Tell the main process the transfer is complete
        wrap()

    def setup(self, pins: list[int]) -> None:
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
        self._sm = StateMachine(0, self._i80bus_pio, freq=freq, out_base=Pin(pins[0]), sideset_base=self._wr)
        self._sm.irq(None)
        self._sm.exec("set(x, 0)")
        self._sm.exec("set(y, 0)")
        self._sm.active(0)

    def _write(self, data: memoryview, length: int) -> None:
        """
        Write the data to the display.
        """
        while self._sm.tx_fifo():  # Wait for the fifo to become empty.
            pass
        if length == 1:
            self._sm.irq(None)
        else:
            self._sm.irq(self.trans_done)
        self._sm.put(data)
