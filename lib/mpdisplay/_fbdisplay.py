# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
FBDisplay class for MPDisplay.
"""

from . import _BaseDisplay


class FBDisplay(_BaseDisplay):
    '''
    A class to emulate an LCD using pygame.
    Provides scrolling and rotation functions similar to an LCD.  The .texture
    object functions as the LCD's internal memory.
    '''
    def __init__(self, buffer, width=None, height=None, stride=None, reverse_bytes_in_word=False,):
        """
        Initializes the display instance with the given parameters.

        :param fb: The CircuitPython FrameBuffer object.
        :type width: FrameBuffer
        """
        super().__init__()
        self._raw_buffer = buffer
        self._buffer = memoryview(buffer)
        self._width = width if width else buffer.width
        self._height = height if height else buffer.height
        self._stride = stride if stride else buffer.row_stride
        self.requires_byte_swap = reverse_bytes_in_word
        self._rotation = 0
        self.color_depth = 16

        self.init()

    ############### Required API Methods ################

    def init(self):
        """
        Initializes the display instance.  Called by __init__ and rotation setter.
        """
        pass