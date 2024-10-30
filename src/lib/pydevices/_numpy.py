try:
    import numpy as np 
except ImportError:
    from ulab import numpy as np 


def swap_bytes(buf, buf_size_pix):
    npbuf = np.frombuffer(buf, dtype=np.uint16)
    npbuf.byteswap(inplace=True)
