# SPDX-License-Identifier: MIT
"""An electric car for the cluster to show.

The car drives itself round a 90 second loop: out of a parking space in
reverse, into town, a fast stretch, an exit with the indicator on, back to a
stop. Speed follows the loop's targets with believable acceleration, motor
power comes from the physics of pushing the car along, and regenerative
braking shows as negative power. The odometer and the efficiency figure
follow from those.

``tick(dt)`` advances the car by ``dt`` seconds. Everything the cluster
draws is an attribute, in the units an American car shows: ``speed_mph``,
``power_kw``, ``gear``, ``odometer_mi``, ``mi_per_kwh``, ``left``, ``right``.
The physics underneath is metric.
"""

import math

_CYCLE_S = 90.0

# (end of the segment in seconds, gear, target speed in mph, left, right)
_PROFILE = (
    (3.0, "P", 0, 0, 0),
    (7.0, "R", 4, 0, 0),
    (9.0, "N", 0, 0, 0),
    (17.0, "D", 28, 1, 0),
    (28.0, "D", 37, 0, 0),
    (38.0, "S", 75, 0, 0),
    (48.0, "S", 86, 0, 0),
    (58.0, "D", 50, 0, 1),
    (70.0, "D", 19, 0, 0),
    (78.0, "D", 0, 0, 0),
    (84.0, "P", 0, 0, 0),
    (90.0, "P", 0, 0, 0),
)

_MPH = 2.236936  # m/s to mph
_KM_PER_MI = 1.609344

_MASS_KG = 1850.0
_DRAG = 0.5 * 1.2 * 0.62  # half air density times drag area
_ROLLING = 0.011 * _MASS_KG * 9.81
_ACCEL = 2.6  # m/s^2, flat out
_BRAKE = 4.2
_MAX_KW = 200.0
_MAX_REGEN_KW = 70.0


def _clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def _segment(t):
    u = t % _CYCLE_S
    for end, gear, target, left, right in _PROFILE:
        if u <= end:
            return gear, target, left, right
    return "P", 0, 0, 0


class Vehicle:
    def __init__(self):
        self.t = 0.0
        self.speed_mph = 0.0
        self.power_kw = 0.0
        self.gear = "P"
        self.odometer_mi = 13488.0
        self.mi_per_kwh = 3.7
        self.left = False
        self.right = False
        self.running = True
        # A press of the left or right arrow holds that indicator on until
        # the next press; the drive loop's own signals are ignored meanwhile.
        self.manual_signal = None

    def toggle_signal(self, side):
        self.manual_signal = None if self.manual_signal == side else side

    def tick(self, dt):
        if not self.running or dt <= 0:
            return
        self.t += dt
        gear, target, left, right = _segment(self.t)
        self.gear = gear
        if self.manual_signal is None:
            self.left = bool(left)
            self.right = bool(right)
        else:
            self.left = self.manual_signal == "left"
            self.right = self.manual_signal == "right"

        v = self.speed_mph / _MPH
        want = target / _MPH
        if want > v:
            # Pull harder from a standstill, ease off near the target.
            a = _ACCEL * _clamp((want - v) / 8.0 + 0.25, 0.3, 1.0)
            v = min(want, v + a * dt)
        elif want < v:
            a = _BRAKE * _clamp((v - want) / 10.0 + 0.2, 0.25, 1.0)
            v = max(want, v - a * dt)
            a = -a
        else:
            a = 0.0
        if v < 0.05:
            v = 0.0

        # Power to move the car: inertia plus drag plus rolling resistance.
        force = _MASS_KG * a + _DRAG * v * v + _ROLLING * (1.0 if v > 0 else 0.0)
        kw = force * v / 1000.0
        if kw < 0:
            kw = max(-_MAX_REGEN_KW, kw * 0.7)
        else:
            kw = min(_MAX_KW, kw / 0.9)
        if v == 0.0:
            kw = 0.0
        # The motor can't change its mind instantly.
        self.power_kw += (kw - self.power_kw) * _clamp(dt * 6.0, 0.0, 1.0)

        self.speed_mph = v * _MPH
        self.odometer_mi += v * dt / 1000.0 / _KM_PER_MI
        # Efficiency: miles per kWh at the motor's draw right now, averaged
        # over the last half minute or so, so a hard pull shows but doesn't
        # own the number, and regen brings it back up.
        if self.speed_mph > 6.0:
            wh_per_mi = _clamp(self.power_kw * 1000.0 / self.speed_mph, -500.0, 1500.0)
            now = 1000.0 / wh_per_mi if wh_per_mi > 100.0 else 9.9
            self.mi_per_kwh += (now - self.mi_per_kwh) * _clamp(dt / 20.0, 0.0, 1.0)
            self.mi_per_kwh = _clamp(self.mi_per_kwh, 1.2, 6.5)

    def blink_on(self):
        """Indicator lamps blink at 90 per minute, on for the first half."""
        return (self.t * 1.5) % 1.0 < 0.5
