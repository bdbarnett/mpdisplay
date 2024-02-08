from ._spibus import SPIBus as _SPIBus


class SPIBus(_SPIBus):
    def __init__(self, *args, **kwargs):
        print("Using _spibus_rp2.py")
        super().__init__(*args, **kwargs)
