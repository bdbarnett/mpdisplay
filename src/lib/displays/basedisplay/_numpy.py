try:
    import numpy as np  # type: ignore
except ImportError:
    from ulab import numpy as np  # type: ignore


def swap_bytes(buf, buf_size_pix):
    npbuf = np.frombuffer(buf, dtype=np.uint16)
    npbuf.byteswap(inplace=True)
