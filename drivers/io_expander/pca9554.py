# SPDX-FileCopyrightText: 2023 Brad Barnett
#
# SPDX-License-Identifier: MIT

# A driver for the PCA9554 I2C I/O expander
import machine  # type: ignore


class PCA9554:
    """
    A driver for the PCA9554 I2C I/O expander.

    This class provides an interface to control the PCA9554, which is an 8-bit I/O expander. 
    It allows configuration of pins as inputs or outputs and facilitates reading from 
    and writing to the pins.

    Attributes:
        i2c (I2C): The I2C bus instance.
        address (int): The I2C address of the PCA9554 device.
        config (int): Configuration register to set pins as input or output.
        output_state (int): Output register state for the PCA9554 pins.

    Example:
        from pca9554 import PCA9554
        import machine


        # Initialize the I2C and PCA9554
        i2c = machine.I2C(0)
        iox = PCA9554(i2c, 0x38)

        # Create an input and output pin
        in_pin = iox.Pin(1, machine.Pin.IN)
        out_pin = iox.Pin(2, machine.Pin.OUT, value=1)

        # Read from input pin using value() method
        print("Input Pin State:", in_pin.value())

        # or use the __call__ method for similar behavior
        print("Input Pin State:", in_pin())

        # Write to output pin using value() method
        out_pin.value(0)

        # Or use the __call__ method for similar behavior
        out_pin(1)
    """

    def __init__(self, i2c, address):
        """
        Initializes the PCA9554 I/O expander.

        Args:
            i2c (I2C): An I2C bus instance.
            address (int): The I2C address of the PCA9554 device.
        """
        self.i2c = i2c
        self.address = address
        self.config = 0xFF  # Default all pins as inputs
        self._output_state = 0x00  # Default all outputs to low

    @property
    def config(self):
        """
        int: The configuration register for the PCA9554 pins.
        """
        return self._config
    
    @config.setter
    def config(self, config):
        """
        Writes to the configuration register to set pins as input or output.

        Args:
            config (int): Bitmask representing input/output configuration for pins.
        """
        self._config = config
        self.i2c.writeto_mem(self.address, 0x03, bytes([config]))

    def read_input(self):
        """
        Reads the current input state of the pins.

        Returns:
            int: Bitmask representing the input state of pins.
        """
        return self.i2c.readfrom_mem(self.address, 0x00, 1)[0]
    
    @property
    def output_state(self):
        """
        int: The output state of the pins, settable to update output register.
        """
        return self._output_state
    
    @output_state.setter
    def output_state(self, value):
        """
        Sets the output state of the pins and writes to the output register.

        Args:
            value (int): Bitmask representing the output state for pins.
        """
        self._output_state = value
        self.i2c.writeto_mem(self.address, 0x01, bytes([value]))

    class _Pin:
        """
        Represents a single pin on the PCA9554.

        Allows setting the pin as input or output and reading/writing its state.

        Attributes:
            parent (PCA9554): The parent PCA9554 instance.
            pin (int): The pin number (0-7).
            mode (int): The pin mode, either `machine.Pin.IN` or `machine.Pin.OUT`.
            value (int): The initial value for the pin, if it is set as an output.
        """

        def __init__(self, parent, pin, mode, value=0):
            """
            Initializes a PCA9554 pin.

            Args:
                parent (PCA9554): The PCA9554 instance that owns this pin.
                pin (int): The pin number (0-7).
                mode (int): The mode of the pin, either `machine.Pin.IN` or `machine.Pin.OUT`.
                value (int, optional): The initial value for the pin if set as output. Defaults to 0.
            """
            self.parent = parent
            self.pin = pin
            self.init(mode, value)

        def init(self, mode, value=0):
            """
            Sets up the pin as input or output based on the mode.
            """
            self.mode = mode
            if self.mode == machine.Pin.OUT:
                self.parent.config &= ~(1 << self.pin)
                self.value(value)
            else:
                self.parent.config |= (1 << self.pin)
        
        def value(self, val=None):
            """
            Sets or gets the pin value.

            If the pin is an output and a value is provided, it sets the pin state. 
            If the pin is an input, calling without an argument will return the current pin state.

            Args:
                val (int, optional): Value to set the pin state (0 or 1). If omitted, the pin state is read.

            Returns:
                int: The current pin state if no value is provided.

            Raises:
                ValueError: If attempting to write to an input pin or read from an output pin.
            """
            if val is None:
                if self.mode == machine.Pin.IN:
                    input_state = self.parent.read_input()
                    return (input_state >> self.pin) & 1
                else:
                    raise ValueError("Cannot read from an output pin")
            else:
                if self.mode == machine.Pin.OUT:
                    if val:
                        self.parent.output_state |= (1 << self.pin)
                    else:
                        self.parent.output_state &= ~(1 << self.pin)
                else:
                    raise ValueError("Cannot write to an input pin")

        def __call__(self, val=None):
            """
            Calls the `value` method, allowing `pin()` to get or set the state, like `machine.Pin`.

            Args:
                val (int, optional): Value to set the pin state (0 or 1). If omitted, the pin state is read.

            Returns:
                int: The current pin state if no value is provided.
            """
            return self.value(val)

    def Pin(self, pin, mode, value=0):
        """
        Factory method to create a new `_Pin` instance with self as the parent.

        Args:
            pin (int): The pin number (0-7).
            mode (int): The mode of the pin, either `machine.Pin.IN` or `machine.Pin.OUT`.
            value (int, optional): The initial value for the pin if set as output. Defaults to 0.

        Returns:
            PCA9554._Pin: An instance of the `_Pin` class.
        """
        return self._Pin(self, pin, mode, value)
