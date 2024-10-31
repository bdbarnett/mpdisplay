import micropython 


@micropython.viper
def swap_bytes(buf: ptr8, buf_size_px: int):  # noqa: F821
    """
    Swap the bytes in a buffer of RGB565 data.

    Args:
        buf: The buffer to swap the bytes in.
        buf_size_px: The size of the buffer in pixels
    """
    for i in range(0, buf_size_px * 2, 2):
        tmp = buf[i]
        buf[i] = buf[i + 1]
        buf[i + 1] = tmp
