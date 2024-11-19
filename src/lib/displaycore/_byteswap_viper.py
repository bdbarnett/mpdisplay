import micropython

if 0:
    class ptr8:
        pass

@micropython.viper
def byteswap_viper(buf: ptr8, buf_size: int):  # noqa: F821
    """
    Swap the bytes in a buffer of 16-bit values in place.

    Args:
        buf: The buffer to swap the bytes in.
        buf_size: The size of the buffer in bytes
    """
    for i in range(0, buf_size, 2):
        tmp = buf[i]
        buf[i] = buf[i + 1]
        buf[i + 1] = tmp
