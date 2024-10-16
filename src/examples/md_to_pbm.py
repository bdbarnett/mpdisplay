"""
Convert material design icons from png to pbm format
"""
from board_config import display_drv
from displays.displaybuf import DisplayBuffer, Area
from framebuf import FrameBuffer, MONO_HLSB, RGB565
import png
import os

image_size = "48dp"
src_path = f"../icons/src/{image_size}/"
dst_path = f"../icons/{image_size}/"


def list_files(directory, ext):
    """
    Iterator to list all .ext files in a single directory (no recursion)
    """
    for file in sorted(os.listdir(directory)):
        if file.endswith(ext):
            yield directory, file

def png_to_framebuffer(filename, threshold=127):
    """
    Read an 8-bit greyscale PNG file into a mono FrameBuffer
    """
    # Read the file
    width, height, pixels, metadata = png.Reader(filename=filename).read_flat()
    if not metadata["greyscale"] or metadata['bitdepth'] != 8:
        print(f"Only 8-bit greyscale PNGs are supported {filename}")
        return None

    # Create the FrameBuffer
    bytes_per_row = (width + 7) // 8
    array_size = bytes_per_row * height
    buffer = memoryview(bytearray(array_size))
    fbuf = FrameBuffer(buffer, width, height, MONO_HLSB)

    # Convert the pixels
    alpha = 1 if metadata["alpha"] else 0
    planes = metadata["planes"]
    for y in range(0, height):
        for x in range(0, width):
            if pixels[(y * width + x) * planes + alpha] > threshold:
                c = 1
            else:
                c = 0
            fbuf.pixel(x, y, c)
    return fbuf, buffer, width, height

def buffer_to_pbm(buffer, width, height, filename):
    """
    Save a MONO_HLSB buffer to a PBM file
    """
    with open(filename, "wb") as f:
        f.write(b"P4\n")
        f.write(f"{width} {height}\n".encode())
        f.write(buffer)

def pbm_to_framebuffer(filename):
    """
    Convert a PBM file to a MONO_HLSB FrameBuffer
    """
    with open(filename, "rb") as f:
        lines = f.readlines()
        if lines[0] != b"P4\n":
            raise ValueError(f"Invalid PBM file {filename}")
        width, height = map(int, lines[1].split())
        buffer = memoryview(bytearray((width + 7) // 8 * height))
        fbuf = FrameBuffer(buffer, width, height, MONO_HLSB)
        buffer[:] = b"".join(lines[2:])
    return fbuf, buffer, width, height

def main(test_writes=False):
    canvas = DisplayBuffer(display_drv)
    canvas.fill(0x001F)
    canvas.show()
    palette = FrameBuffer(memoryview(bytearray(4)), 2, 1, RGB565)
    palette.pixel(0, 0, 0x0000)
    palette.pixel(1, 0, 0xFFFF)
    key = 0x0000

    try:
        os.stat(dst_path)
    except OSError:
        os.mkdir(dst_path)

    x = 0
    y = 0
    for path, png_file in list_files(src_path, ".png"):
        data = png_to_framebuffer(path + png_file)
        if data is None:
            continue
        fbuf, buffer, width, height = data
        pbm_file = png_file.replace(".png", ".pbm")
        print(f"{pbm_file}")
        buffer_to_pbm(buffer, width, height, dst_path + pbm_file)

        if test_writes:
            fbuf, buffer, width, height = pbm_to_framebuffer(dst_path + pbm_file)

        # Display the icon
        canvas.blit(fbuf, x, y, key, palette)
        canvas.show(Area(x, y, width, height))

        x += width
        if x + width >= canvas.width:
            x = 0
            y += height
            if y + height >= canvas.height:
                y = 0
            canvas.fill_rect(0, 0, canvas.width, canvas.height, 0x001F)
        
main(True)
