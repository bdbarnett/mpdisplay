
@micropython.viper
def swap_bytes_viper(buf: ptr8, buf_size_px: int):
    """
    Swap the bytes in a buffer of RGB565 data.

    :param buf: Buffer of RGB565 data
    :type buf: ptr8
    :param buf_size_px: Size of the buffer in pixels
    :type buf_size_px: int
    """
    for i in range(0, buf_size_px * 2, 2):
        tmp = buf[i]
        buf[i] = buf[i + 1]
        buf[i + 1] = tmp
