import micropython


@micropython.viper
def _bounce8(dest: ptr8, source: ptr8, length: int, swap: bool):  # noqa: F821
    # Convert a line in 8 bit RGB332 format to 16 bit RGB565 format.
    # Each byte becomes 2 in destination. Source format:
    # <R2 R1 R0 G2 G1 G0 B1 B0>
    # dest:
    # swap==False: <R2 R1 R0 00 00 G2 G1 G0> <00 00 00 B1 B0 00 00 00>
    # swap==True:  <00 00 00 B1 B0 00 00 00> <R2 R1 R0 00 00 G2 G1 G0>

    if swap:
        lsb = 0
        msb = 1
    else:
        lsb = 1
        msb = 0
    n = 0
    for x in range(length):
        c = source[x]
        dest[n + lsb] = (c & 0xE0) | ((c & 0x1C) >> 2)  # Red Green
        dest[n + msb] = (c & 0x03) << 3  # Blue
        n += 2


@micropython.viper
def _bounce4(dest: ptr16, source: ptr8, length: int, lut: ptr16):  # noqa: F821
    # Convert a line in 4+4 bit index format to two * 16 bit RGB565 format
    # using a color lookup table. Each byte becomes 4 in destination.
    # Source format:  <C03 C02 C01 C00 C13 C12 C11 C10>
    # Dest format: the same as self.rgb * 2
    n = 0
    for x in range(length):
        c = source[x]  # Get the indices of the 2 pixels
        dest[n] = lut[c >> 4]  # lookup top 4 bits for even pixels
        n += 1
        dest[n] = lut[c & 0x0F]  # lookup bottom 4 bits for odd pixels
        n += 1
