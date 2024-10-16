# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
try:
    from micropython import const, schedule
except ImportError:

    def const(x):
        return x

    def schedule(cb, interval):
        cb(interval)


class _TimerBase:
    """
    A class to create a timer with the same API and similar functionality to
    MicroPython's machine.Timer class.
    """

    PERIODIC = const(0)
    ONE_SHOT = const(1)

    def __init__(self, id=-1, **kwargs):
        """
        Initializes the timer with the given parameters.

        :param id: The timer ID (default is -1).
        :type id: int
        """
        self.id = id
        self._busy = False
        self._timer = None
        if kwargs:
            self.init(**kwargs)

    def init(self, *, mode, freq=-1, period=-1, callback=None):
        """
        Initialize the timer.
        :param mode: Timer mode (Timer.ONE_SHOT or Timer.PERIODIC)
        :param freq: Timer frequency in Hz (optional)
        :param period: Timer period in milliseconds (optional, ignored if freq is specified)
        :param callback: Callable to execute upon timer expiration
        """
        if mode in (self.ONE_SHOT, self.PERIODIC):
            self._mode = mode
        else:
            raise ValueError("Invalid timer mode")

        self._interval = int(1000 / freq) if freq > 0 else period
        if self._interval < 1:
            raise ValueError("Invalid freq or period")

        self._callback = callback
        self._start()  # _start() is implemented in subclasses

    def deinit(self):
        """
        Deinitializes the timer.
        """
        while self._busy:
            pass

        self._stop()  # _stop() is implemented in subclasses
        self._mode = None
        self._interval = 0
        self._callback = None
        self._timer = None

    def _handler(self, interval, param=None):
        """
        Internal callback function called when the timer expires.
        SDL2 timers call the handler with the interval and a user-defined parameter,
        while librt timers call the handler with the interval only.
        They are ignored here.
        """
        if self._busy:
            return

        self._busy = True
        try:
            schedule(self._callback, 0)
        except RuntimeError:  # MicroPython raises RuntimeError if the schedule queue is full
            pass
        self._busy = False

        if self._mode == self.ONE_SHOT:
            self.deinit()
            return 0  # SDL2 expects the callback to return the next interval, 0 for one-shot
        return self._interval

    def _start(self):
        raise NotImplementedError("Subclasses must implement this method")

    def _stop(self):
        raise NotImplementedError("Subclasses must implement this method")
