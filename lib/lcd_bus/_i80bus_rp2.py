from ._i80bus import I80Bus as _I80Bus
from rp2 import DMA


class I80Bus(_I80Bus):
    """
    I80Bus for the RP2 using DMA transfers.
    """
    def __init__(self, *args, **kwargs) -> None:
        print("Using _i80bus_rp2.py")
        super().__init__(*args, **kwargs)

    def setup(self, pins: list[int], wr: int) -> None:
        raise NotImplementedError("This method has not been implemented yet.")

    def _write(self, data: memoryview, len: int) -> None:
        raise NotImplementedError("This method has not been implemented yet.")