"""
Testris game implemented in MicroPython by Brad Barnett.
"""

from time import ticks_ms, ticks_diff  # For timing
from random import choice, randint  # For random piece selection
from json import load, dump  # For saving the high score
from machine import reset  # For restarting the game
from micropython import const  # For constant values
from framebuf import FrameBuffer, RGB565  # For drawing text
from display_config import display_drv, touch_drv  # For the display driver
from heap_caps import malloc, CAP_DMA  # For allocating buffers for the blocks and text

swap_color_bytes = True

# Define the draw_block function
draw_block = lambda x, y, index: display_drv.blit(x, y, block_size, block_size, blocks[index])

# Get the display dimensions
display_width = display_drv.width
display_height = display_drv.height

# Setup the keypad, in this case a touchscreen keypad emulator
# keypad should have a .read() method that returns the values 
# keypad.LEFT, .DOWN, .RIGHT, .CCW, .CW, .START and .PAUSE
from touchpad import Touchpad
keypad = Touchpad(touch_drv.get_positions, width=display_width, height=display_height, touch_rotation=0)

# Define RGB565 colors
BLACK = const(0x0000)
CYAN = const(0x07ff)
YELLOW = const(0xffe0)
PURPLE = const(0x780f)
GREEN = const(0x07e0)
BLUE = const(0x001f)
RED = const(0xf800)
ORANGE = const(0xfda0)
GRAY = const(0x8410)
WHITE = const(0xffff)

# Define other constants
SPLASH_ENABLED = const(1)  # Set to 1 to show the splash screen, 0 to skip it
DELAY = const(150)  # Delay in ms so we don't read the keypad too quickly
SPEEDUP = const(25)  # Amount of time in ms to reduce the drop time by when a row is cleared (Difficulty)
BAG_SIZE = const(7)  # Number of random unique pieces to add to the bag at a time, min 1, max 7
GRID_WIDTH = const(10)
GRID_HEIGHT = const(20)
BACKGROUND_INDEX = const(0)  # Index of the background block (black)
BORDER_INDEX = const(8)  # Index of the border block (gray)
TOUCH_TARGET_INDEX = const(9)  # Index of the touch target block (white).  Only used if keypad is a Touchpad.
CW = const(1)
CCW = const(-1)

# Define the blocks
block_size = min(display_width//(GRID_WIDTH+2), display_height//(GRID_HEIGHT+4))  # Size in pixels
block_bevel = block_size // 5  # Width of the beveled edge in pixels

# Calculate the border dimensions in pixels
border_width = (GRID_WIDTH + 2) * block_size
border_height = (GRID_HEIGHT + 2) * block_size

# Calculate the offsets for the border and grid in pixels
border_x_offset = (display_width - border_width) // 2  # Center the grid horizontally
border_y_offset = display_height - border_height  # Align the bottom of the grid with the bottom of the display
grid_x_offset = border_x_offset + block_size
grid_y_offset = border_y_offset + block_size

# Calculate the banner dimensions in pixels
banner_width = border_width - (block_size * 4)  # Width of the banner in pixels, leave room for next piece
banner_height = block_size * 2  # Height of the banner in pixels

# Define the game pieces and their rotations
pieces = [
    [[1, 1, 1, 1]],  # I piece (cyan)
    [[2, 2], [2, 2]],  # O piece (yellow)
    [[0, 3, 0], [3, 3, 3]],  # T piece (purple)
    [[4, 4, 0], [0, 4, 4]],  # S piece (blue)
    [[0, 5, 5], [5, 5, 0]],  # Z piece (green)
    [[6, 0, 0], [6, 6, 6]],  # J piece (red)
    [[0, 0, 7], [7, 7, 7]],  # L piece (orange)
    ]

# Define the splash screen
splash = [
    [0,0,0,3,3,0,0,0,0,0,0,0],
    [0,0,0,3,4,4,4,0,0,6,0,0],
    [1,1,1,3,3,4,5,5,0,6,0,0],
    [0,1,2,2,3,4,5,0,5,6,7,7],
    [0,1,2,3,3,4,5,5,0,6,7,0],
    [0,1,2,2,0,4,5,0,5,6,7,7],
    [0,1,2,0,0,0,5,0,5,0,0,7],
    [0,0,2,2,0,0,0,0,0,0,7,7],
]

# Create the blocks: black for background, 7 piece colors, gray for border, white for touch targets
blocks = []
for color in [BLACK, CYAN, YELLOW, PURPLE, GREEN, BLUE, RED, ORANGE, GRAY, WHITE]:
    block = malloc(block_size*block_size*2, CAP_DMA) # Allocate a buffer for the block, 2 bytes per pixel
    for y in range(block_size):  # Working top to bottom
        for x in range(block_size):  # Then left to right
            if color == BLACK:
                pixel_color = BLACK  # No border or bevel for black
            elif x == 0 or x == block_size - 1 or y == 0 or y == block_size - 1: # Pixel on the border
                pixel_color = BLACK  # Draw a black border around the block
            # Left or top bevel pixel with even x on even rows, odd x on odd rows
            elif (x < block_bevel or y < block_bevel) and (x & 1 == y & 1):
                pixel_color = WHITE  # Dither with white on the top and left bevels
            # Right or bottom bevel pixel with even x on even rows, odd x on odd rows
            elif (x > block_size - block_bevel - 1 or y > block_size - block_bevel - 1) and (x & 1 == y & 1):
                pixel_color = BLACK  # Dither with black on the bottom and right bevels
            else:
                pixel_color = color  # Fill the block with the specified color
            address = (x + (y * block_size)) * 2  # Address of the pixel in the buffer, 2 bytes per pixel
            block[address] = pixel_color & 0xff  if not swap_color_bytes else pixel_color >> 8 # Least significant byte
            block[address + 1] = pixel_color >> 8  if not swap_color_bytes else pixel_color & 0xff # Most significant byte
    blocks.append(block)

# Create a frame buffer for text
text_buffer = malloc(banner_width*banner_height*2, CAP_DMA)
text_fb = FrameBuffer(text_buffer, banner_width, banner_height, RGB565)


def draw_banner(text, x=border_x_offset, y=0, color=WHITE, bg_color=BLACK):
    """
    Draw text on the banner.

    Parameters:
    text (str): The text to draw.
    x (int, optional): The horizontal position at which to draw the text.
    y (int, optional): The vertical position at which to draw the text.
    color (int, optional): The color of the text. Defaults to WHITE.
    bg_color (int, optional): The background color of the text. Defaults to BLACK.
    """
    text_fb.fill(bg_color)  # Clear the text buffer
    text_lines = text.split("\n")  # Split the text into lines
    text_y = 4  # Leave a 4 pixel margin at the top
    for text_line in text_lines:  # For each line of text
        text_fb.text(text_line, 0, text_y, color)  # Draw the text in the text buffer
        text_y += 8  # Move down 8 pixels
    display_drv.blit(x, y, banner_width, banner_height, text_buffer)  # Draw the text buffer on the display

def show_score(message=""):
    """
    Show the score.

    Parameters:
        message (str, optional): The message to display. Defaults to "".

    Returns:
        None
    """
    draw_banner(f"{message}\nScore: {score:,}\nLines cleared: {lines}\nDrop time: {drop_time:,} ms")  # Draw the score

def show_splash():
    """
    Show the splash screen.
    """
    splash_x = (display_width - len(splash[0]) * block_size) // 2  # Center the splash screen horizontally
    splash_y = (display_height - len(splash) * block_size) // 2  # Center the splash screen vertically
    draw_piece(splash, [0, 0], offset_x=splash_x, offset_y=splash_y)  # Draw the splash screen

def clear_screen():
    """
    Clear the screen.
    """
    for x in range(0, display_width, block_size):
        for y in range(0, display_height, block_size):
            draw_block(x, y, BACKGROUND_INDEX)

def draw_border():
    """
    Draw the border.
    """
    for x in range(border_x_offset, border_x_offset + border_width, block_size):
        draw_block(x, border_y_offset, BORDER_INDEX)  # Top border
        draw_block(x, border_y_offset + border_height - block_size, BORDER_INDEX)  # Bottom border
    for y in range(border_y_offset, border_y_offset + border_height, block_size):
        draw_block(border_x_offset, y, BORDER_INDEX)  # Left border
        draw_block(border_x_offset + border_width - block_size, y, BORDER_INDEX)  # Right border

def draw_touch_targets():
    """
    Draw the touch targets.
    """
    draw_piece([[TOUCH_TARGET_INDEX]*4], [GRID_WIDTH // 2 - 2, GRID_HEIGHT])
    for x in [-1, GRID_WIDTH]:
        for y in [-1, (GRID_HEIGHT // 2) - 3, GRID_HEIGHT - 5]:
            draw_piece([[TOUCH_TARGET_INDEX]]*4, [x, y])

def save_high_score(score):
    """
    Save the high score to a JSON file.

    Args:
        score (int): The high score to be saved.

    Returns:
        None
    """
    with open('high_score.json', 'w') as f:
        dump(score, f)

def load_high_score():
    """
    Load the high score from the 'high_score.json' file.
    
    Returns:
        int: The high score value if the file exists, otherwise 0.
    """
    try:
        with open('high_score.json', 'r') as f:
            return load(f)
    except:
        return 0

def wait_for_key(key=None, exclude=[]):
    """
    Waits for the user to press a key.

    Parameters:
        key (str, optional): The key to wait for. If not specified, any key will be accepted. Defaults to None.
        exclude (list, optional): List of keys to exclude. Defaults to [].

    Returns:
        str: The key that was pressed.
    """
    while True:  # Wait for the user to press a key
        if (pressed := keypad.read()) and pressed not in exclude:  # If a key was pressed and it's not excluded
            if key is None or pressed == key:  # If no key was specified or the key pressed matches the specified key
                break  # Exit the loop
    return pressed

def sample(population, k):
    """
    Randomly select k items from population without replacement.
    MicroPython doesn't have random.sample(), so approximate it.

    Parameters:
    population (list): The list from which to select items.
    k (int): The number of items to select, <= len(population).

    Returns:
    list: A list of k items randomly selected from the population.
    """
    results = []
    for _ in range(k):
        result = choice(population)
        results.append(result)
        population.remove(result)
    return results

def rotate(piece, dir):
    """
    Rotate a piece in the specified direction.

    Parameters:
    piece (list): The piece to rotate.
    dir (int): The direction to rotate the piece. 1 for clockwise, -1 for counter-clockwise.

    Returns:
    list: The rotated piece.
    """
    piece = list(zip(*piece))  # Transpose the piece (swap rows with columns)
    # Reverse rows for clockwise rotation, or columns for counter-clockwise
    return [list(reversed(row)) for row in piece] if dir > 0 else [list(row) for row in reversed(piece)]

def collision(piece, pos, dx, dy, rotation=0):
    """
    Check if moving or rotating a piece would cause a collision.

    Parameters:
    piece (list): The piece to check.
    pos (list): The current position of the piece.
    dx (int): The horizontal displacement to check.
    dy (int): The vertical displacement to check.
    rotation (int, optional): The rotation to check. Defaults to 0.

    Returns:
    bool: True if a collision would occur, False otherwise.
    """
    piece = rotate(piece, rotation) if rotation else piece
    for y, row in enumerate(piece):  # For each row in the piece
        for x, block in enumerate(row):  # For each block in the row
            if block:  # If the block is non-zero
                if not (0 <= pos[0] + x + dx < GRID_WIDTH) or \
                        not (0 <= pos[1] + y + dy < GRID_HEIGHT) or \
                        grid[pos[1] + y + dy][pos[0] + x + dx] != 0:
                    return True
    return False

def draw_piece(piece, piece_position, index=-1, offset_x=grid_x_offset, offset_y=grid_y_offset):
    """
    Draw a piece at a specified position.

    Parameters:
    piece (list): The piece to draw.
    piece_position (list): The position at which to draw the piece.
    index (int): The index of the piece in the blocks list.
    offset_x (int, optional): The horizontal offset at which to draw the piece. Defaults to grid_x_offset, in pixels.
    offset_y (int, optional): The vertical offset at which to draw the piece. Defaults to grid_y_offset, in pixels.
    """
    for y, row in enumerate(piece):
        for x, block in enumerate(row):
            if block:
                draw_block(offset_x + (piece_position[0] + x) * block_size, 
                           offset_y + (piece_position[1] + y) * block_size, 
                           index if index >=0 else block)


high_score = load_high_score()  # Load the high score

if SPLASH_ENABLED:  # Show the splash screen and wait for the user to press a key
    clear_screen()  # Clear the screen
    show_splash()  # Show the splash screen
    draw_banner(f"High Score {high_score:,}\n\nPress any key\nto continue.",
                x=(display_width - 5 * block_size) // 2, y=(display_height - 2 * block_size))
    wait_for_key()  # Wait for the user to press a key

while True:  # Outer loop - play the game repeatedly
    print("Outer loop")
    # Initialize game state
    # grid is a 2D list of block indices, 0 for empty, 1-7 indicates block color
    # grid is y, x, not x, y, so grid[y][x] is the block at (x, y).
    # Allows for easy row clearing with grid[y] = [0 for _ in range(GRID_WIDTH)]
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]  # GRID_HEIGHT x GRID_WIDTH grid
    bag = []  # Bag of pieces to draw from
    next_piece = choice(pieces)  # Select the first piece
    score = 0  # Start with a score of 0
    lines = 0  # Start with 0 lines cleared
    drop_time = 1000  # Time between automatic drops in ms, decreases by SPEEDUP as lines are cleared
    last_read = 0  # The last time the keypad was read
    hard_drop = False  # Flag to indicate a hard drop

    # Initialize the game display and wait for the user to press START
    clear_screen()  # Clear the screen
    draw_border()  # Draw the border
    draw_banner(f"High Score {high_score:,}\n\nPress START\nto play.")
    if str(type(keypad)).find("Touchpad"):  # If we're using the touchpad
        draw_touch_targets()  # Draw the touch targets
    wait_for_key(keypad.START)  # Wait for the user to press START

    # Play the game
    show_score()  # Show the score
    while True:  # Main game loop
        print("Main game loop")
        current_piece = next_piece  # Set the next piece to the current piece
        current_position = [GRID_WIDTH // 2 - len(current_piece[0]) // 2, 0]  # Start position for the piece
        if collision(current_piece, current_position, 0, 0):  # Check for game over
            break # Game over, exit the main loop
        if not bag:  # If the bag is empty, refill it
            bag = sample(pieces.copy(), BAG_SIZE) # Fill the bag with random pieces
        next_piece = bag.pop()  # Pull the next piece out of the bag
        draw_piece(next_piece, [7, -3])  # Draw the next piece beside the banner
        last_drop = ticks_ms()  # Time of last automatic drop

        while current_piece:  # Middle loop - while the piece is in play
            print("Redraw piece loop")
            draw_piece(current_piece, current_position)  # Draw the current piece
            old_piece = current_piece.copy()  # Save the previous piece
            old_position = current_position.copy()  # Save the previous position

            while current_piece == old_piece and current_position == old_position:  # Inner loop - while the piece hasn't moved
                # If it has been DELAY ms since the last keypad read, then read the keypad
                if (ticks_diff(ticks_ms(), last_read) >= DELAY) and (key := keypad.read()):  # If a key was pressed
                    last_read = ticks_ms()  # Save the time of the last read
                    if key == keypad.LEFT and not collision(current_piece, current_position, -1, 0):
                        current_position[0] -= 1  # Move the piece left
                    elif key == keypad.RIGHT and not collision(current_piece, current_position, 1, 0):
                        current_position[0] += 1  # Move the piece right
                    elif key == keypad.DOWN and not collision(current_piece, current_position, 0, 1):
                        current_position[1] += 1  # Move the piece down
                        last_drop = ticks_ms()  # Reset the last drop time
                    elif key == keypad.UP and not collision(current_piece, current_position, 0, 1):
                        hard_drop = True  # Hard drop the piece
                    elif key == keypad.CCW and not collision(current_piece, current_position, 0, 0, CCW):
                        current_piece = rotate(current_piece, CCW)  # Rotate the piece counter-clockwise
                    elif key == keypad.CW and not collision(current_piece, current_position, 0, 0, CW):
                        current_piece = rotate(current_piece, CW)  # Rotate the piece clockwise
                    elif key == keypad.PAUSE:  # Pause the game
                        draw_banner("Paused.\n\nPress START to reset.\nAny key to resume.")
                        key = wait_for_key(exclude=[keypad.PAUSE])  # Wait for the user to press a key, excluding PAUSE
                        if key == keypad.START:
                            clear_screen()  # Clear the screen
                            reset()  # Reset the machine
                        else:  # Resume the game
                            show_score()  # Show the score

                if hard_drop:  # Hard drop the piece
                    while not collision(current_piece, current_position, 0, 1):  # While the piece hasn't hit bottom
                        current_position[1] += 1  # Move the piece down
                    hard_drop = False  # Reset the hard drop flag
                    last_drop = 0  # Unset the last drop time
                elif ticks_diff(ticks_ms(), last_drop) >= drop_time:  # Automatic drop
                    if not collision(current_piece, current_position, 0, 1):
                        current_position[1] += 1  # Move the piece down
                        last_drop = ticks_ms()  # Reset the last drop time
                    else:  # Piece hit bottom
                        # Add the piece to the grid
                        for y, row in enumerate(current_piece):
                            for x, block in enumerate(row):
                                if block:
                                    grid[current_position[1] + y][current_position[0] + x] = block  # Add the piece to the grid
                        current_piece = None  # Piece is no longer in play; its now part of the grid
                        # Check for full lines
                        full_lines = []
                        for y, row in enumerate(grid):  # Check each row
                            if all(row):  # If each block in the row is non-zero
                                full_lines.append(y)  # Add the row to the list of full lines
                        if full_lines:
                            score += [100, 200, 400, 800][len(full_lines)-1]  # Update the score
                            lines += len(full_lines)  # Update the number of lines cleared
                            drop_time = max(DELAY, drop_time - SPEEDUP)  # Decrease the drop time, but not below DELAY time
                            show_score()  # Show the score
                            old_grid = [row[:] for row in grid]  # Keep a copy of the grid before making any changes
                            # Shift the remaining lines down
                            for full_line in full_lines:  # For each full line
                                for y in range(full_line, 0, -1):  # Working from the full line up to the top
                                    grid[y] = list(grid[y-1])  # Copy the line above it
                                grid[0] = [0 for _ in range(GRID_WIDTH)]  # Clear the top line
                            # Redraw only the lines that have changed
                            for y in range(GRID_HEIGHT):  # For each line
                                if grid[y] != old_grid[y]:  # If the line has changed
                                    for x in range(GRID_WIDTH):  # For each block in the line
                                        draw_block(x*block_size+grid_x_offset, y*block_size+grid_y_offset, grid[y][x])

            if current_piece: # If the piece hasn't hit bottom, erase it from its previous position
                draw_piece(old_piece, old_position, BACKGROUND_INDEX)

        draw_piece(next_piece, [7, -3], BACKGROUND_INDEX)  # Erase the previous next piece

    # Game over - show the score and wait for the user to press a key
    if score > high_score:
        save_high_score(score)
        high_score = score
        message = "New high score!"
    else:
        message = "Game over!"
    show_score(message)  # Show the score
    wait_for_key(keypad.START)  # Wait for the user to press START
