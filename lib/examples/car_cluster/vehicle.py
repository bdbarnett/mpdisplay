# SPDX-License-Identifier: MIT
"""An electric car for the cluster to show, driving a fixed course.

The course is a figure eight of two stacked rectangular blocks, 1.5 miles
east to west and 1.0 mile north to south each, ten miles round in all. The
car lives in a driveway on the middle street, the one the two blocks share.
Each lap it backs out of the driveway, heads east, and takes every corner
to the left: up the east side of the top block, west along the top road
(the fast one, 55 mph, where it shifts into S), south down the west side,
straight through the middle street and on down the west side of the bottom
block, east along the bottom, north up the east side and west along the
middle street back to the driveway, where it parks. There are stop signs at
the top-left and bottom-right corners, the two opposite corners of the
eight; the other corners are turns taken at 12 mph.

The car signals a few hundred feet before each corner and before the
driveway, brakes for stops and corners the way a driver would (regen shows
as negative power), and accelerates harder in S than in D. The physics is
metric underneath; the attributes the cluster reads are in the units an
American car shows: ``speed_mph``, ``power_kw``, ``gear``, ``trip_mi`` (the
distance driven this lap, which resets to zero as the car pulls back into
the driveway), ``mi_per_kwh``, ``left``, ``right``.

``tick(dt)`` advances the car by ``dt`` seconds of driving. The cluster
passes ten seconds of driving for every real one by default, so a lap
takes a couple of minutes instead of twenty.
"""

_MPH = 2.236936  # m/s per mph
_M_PER_MI = 1609.344

_MASS_KG = 1850.0
_DRAG = 0.5 * 1.2 * 0.62  # half air density times drag area
_ROLLING = 0.013 * _MASS_KG * 9.81
_ACCESSORY_KW = 1.5  # climate, electronics, pumps: there whenever the car is on
_MAX_KW = 200.0
_MAX_REGEN_KW = 70.0

# Driving manners: how hard the car pulls and brakes, by gear.
_ACCEL = {"D": 2.0, "S": 3.2, "R": 0.8}
_BRAKE = 2.2  # m/s^2, a firm but ordinary stop
_TURN_MPS = 12.0 / _MPH  # corners are taken at 12 mph
_SIGNAL_M = 120.0  # the indicator goes on this far before a corner
_STOP_DWELL_S = 2.0
_PARK_DWELL_S = 5.0
_DRIVEWAY_M = 14.0

# The blocks.
_W = 1.5 * _M_PER_MI
_H = 1.0 * _M_PER_MI

# Each straight: (length in metres, speed limit in mph, gear, what ends it).
# What ends it is "left" (a corner taken at 12 mph), "stop" (a stop sign,
# then the same corner), "through" (no corner) or "park" (the driveway).
_ROUTE = (
    (_W, 25, "D", "left"),  # middle street, eastbound
    (_H, 35, "D", "left"),  # east side of the top block, northbound
    (_W, 55, "S", "stop"),  # the top road, westbound: the fast one
    (_H, 35, "D", "through"),  # west side of the top block, southbound
    (_H, 35, "D", "left"),  # west side of the bottom block, southbound
    (_W, 30, "D", "stop"),  # the bottom road, eastbound
    (_H, 35, "D", "left"),  # east side of the bottom block, northbound
    (_W, 25, "D", "park"),  # middle street, westbound, home
)


def _clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


class Vehicle:
    def __init__(self):
        self.t = 0.0
        self.speed_mph = 0.0
        self.power_kw = 0.0
        self.gear = "P"
        self.trip_mi = 0.0
        self.mi_per_kwh = 3.7
        self.left = False
        self.right = False
        self.running = True
        # A press of the left or right arrow holds that indicator on until
        # the next press; the route's own signals are ignored meanwhile.
        self.manual_signal = None

        self._v = 0.0  # m/s along the direction of travel
        self._phase = "parked"  # parked, backing, driving, parking
        self._dwell = 1.0  # seconds left standing still
        self._s = 0.0  # metres along the current straight (or driveway)
        self._leg = 0
        self._stopped_here = False  # the stop sign on this leg is done
        self._signal = None
        self.lap = 0

    def toggle_signal(self, side):
        self.manual_signal = None if self.manual_signal == side else side

    # -- the plan: how fast the car wants to go right now --------------------

    def _target(self):
        """Speed the driver is aiming for, and the signal, in this instant."""
        if self._phase == "backing":
            left = _DRIVEWAY_M - self._s
            return min(4.0 / _MPH, self._stopping_speed(left, 0.0)), None
        if self._phase == "parking":
            left = _DRIVEWAY_M - self._s
            return min(5.0 / _MPH, self._stopping_speed(left, 0.0)), None

        length, limit, gear, end = _ROUTE[self._leg]
        left = length - self._s
        want = limit / _MPH
        signal = None
        if end == "through":
            pass
        elif end == "park":
            want = min(want, self._stopping_speed(left, 5.0 / _MPH))
            if left < _SIGNAL_M:
                signal = "right"
        else:
            corner = _TURN_MPS
            if end == "stop" and not self._stopped_here:
                corner = 0.0
            want = min(want, self._stopping_speed(left, corner))
            if left < _SIGNAL_M:
                signal = "left"
        # The straight after a corner starts slowly: still in the turn.
        if self._s < 12.0 and self._leg > 0:
            want = min(want, _TURN_MPS + 1.0)
        return want, signal

    @staticmethod
    def _stopping_speed(distance, v_end):
        """Fastest the car can go now and still be at ``v_end`` in ``distance``."""
        if distance <= 0:
            return v_end
        return (v_end * v_end + 2.0 * _BRAKE * distance) ** 0.5

    # -- the loop -----------------------------------------------------------

    def tick(self, dt):
        if not self.running or dt <= 0:
            return
        # Small steps keep stops landing where they should.
        while dt > 0:
            step = dt if dt < 0.05 else 0.05
            self._step(step)
            dt -= step

    def _step(self, dt):
        self.t += dt
        if self._dwell > 0:
            self._dwell -= dt
            self._settle(dt, 0.0)
            if self._dwell <= 0:
                self._after_dwell()
            return

        want, signal = self._target()
        self._signal = signal
        v = self._v
        if want > v + 0.01:
            a = min(_ACCEL[self.gear], (want - v) / dt)
        elif want < v - 0.01:
            a = max(-_BRAKE, (want - v) / dt)
        else:
            a = 0.0
        v = max(0.0, v + a * dt)
        moved = v * dt
        self._s += moved
        self._v = v
        self._settle(dt, a)
        self.speed_mph = v * _MPH
        self.trip_mi += moved / _M_PER_MI

        if self.manual_signal is None:
            self.left = signal == "left"
            self.right = signal == "right"
        else:
            self.left = self.manual_signal == "left"
            self.right = self.manual_signal == "right"

        self._advance()

    def _settle(self, dt, a):
        """Motor power and efficiency from what the car is doing."""
        v = self._v
        force = _MASS_KG * a + _DRAG * v * v + (_ROLLING if v > 0.1 else 0.0)
        kw = force * v / 1000.0
        if kw < 0:
            kw = max(-_MAX_REGEN_KW, kw * 0.7)
        else:
            kw = min(_MAX_KW, kw / 0.9)
        kw = _ACCESSORY_KW if v < 0.1 else kw + _ACCESSORY_KW
        self.power_kw += (kw - self.power_kw) * _clamp(dt * 6.0, 0.0, 1.0)
        if self.speed_mph > 6.0:
            wh_per_mi = _clamp(self.power_kw * 1000.0 / self.speed_mph, -500.0, 1500.0)
            now = 1000.0 / wh_per_mi if wh_per_mi > 100.0 else 9.9
            self.mi_per_kwh += (now - self.mi_per_kwh) * _clamp(dt / 20.0, 0.0, 1.0)
            self.mi_per_kwh = _clamp(self.mi_per_kwh, 1.2, 5.5)

    def _advance(self):
        """Move on when the end of a straight, the driveway or a stop is reached."""
        if self._phase == "backing":
            if self._s >= _DRIVEWAY_M - 0.2 and self._v < 0.2:
                self._v = 0.0
                self.speed_mph = 0.0
                self.gear = "D"
                self._dwell = 0.8
            return
        if self._phase == "parking":
            if self._s >= _DRIVEWAY_M - 0.2 and self._v < 0.2:
                self._v = 0.0
                self.speed_mph = 0.0
                self._phase = "parked"
                self.gear = "P"
                self.lap += 1
                self._dwell = _PARK_DWELL_S
            return

        length, limit, gear, end = _ROUTE[self._leg]
        if end == "stop" and not self._stopped_here:
            if length - self._s < 0.6 and self._v < 0.2:
                self._v = 0.0
                self.speed_mph = 0.0
                self._stopped_here = True
                self._dwell = _STOP_DWELL_S
            return
        if self._s >= length:
            self._s -= length
            self._leg += 1
            self._stopped_here = False
            if end == "park" or self._leg >= len(_ROUTE):
                self._phase = "parking"
                self._s = 0.0
                self._leg = 0
                self.trip_mi = 0.0
            else:
                self.gear = _ROUTE[self._leg][2]

    def _after_dwell(self):
        if self._phase == "parked":
            self._phase = "backing"
            self._s = 0.0
            self.gear = "R"
        elif self._phase == "backing":
            self._phase = "driving"
            self._s = 0.0
            self._leg = 0
            self._stopped_here = False
            self.gear = _ROUTE[0][2]

    def blink_on(self, wall_s):
        """Indicator lamps blink at 90 per minute, on for the first half."""
        return (wall_s * 1.5) % 1.0 < 0.5
