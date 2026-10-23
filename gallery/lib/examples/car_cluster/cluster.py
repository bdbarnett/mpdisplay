# SPDX-License-Identifier: MIT
"""The cluster's screen: status line, indicators, two dials, the road, PRNDS."""

import lvgl as lv

from ring import Ring, _color, plain, scaled_font

_CIRCLE = getattr(lv, "RADIUS_CIRCLE", 0x7FFF)

BG = 0x05080F
TRACK = 0x0E1E33
CYAN = 0x3DF0FF
GREEN = 0x3FE878
DIM = 0x5E6E8C
TEXT = 0xE6ECF7

SPEED_STOPS = ((0.0, 0x35F2C8), (0.45, 0x3DE0FF), (1.0, 0x2E7BFF))
POWER_STOPS = ((0.0, 0x3DE0FF), (0.5, 0x4E8DFF), (1.0, 0xA05CFF))

GEARS = ("P", "R", "N", "D", "S")


def _hood(parent, w, y, h, curves):
    """Faint lines curving like a dash hood, on a strip canvas ``w`` by ``h``.

    Each curve is ``(crest_y, drop, opa, width)``: highest at the centre, and
    ``drop`` pixels lower at the edges. Drawn as short straight pieces, which
    is far cheaper than an arc the size of several screens.
    """
    strip = lv.canvas(parent)
    strip.set_size(w, h)
    strip.set_pos(0, y)
    plain(strip)
    buf = lv.draw_buf_create(w, h, lv.COLOR_FORMAT.ARGB8888, 0)
    strip.set_draw_buf(buf)
    strip.fill_bg(_color(0x000000), lv.OPA.TRANSP)
    layer = lv.layer_t()
    strip.init_layer(layer)
    line = lv.draw_line_dsc_t()
    line.init()
    line.color = _color(CYAN)
    pieces = 32
    half = w / 2.0
    for crest, drop, opa, width in curves:
        line.opa = opa
        line.width = width
        prev = None
        for i in range(pieces + 1):
            x = w * i / pieces
            cy = crest - y + drop * ((x - half) / half) ** 2
            if prev is not None:
                line.p1 = lv.point_precise_t({"x": prev[0], "y": prev[1]})
                line.p2 = lv.point_precise_t({"x": x, "y": cy})
                lv.draw_line(layer, line)
            prev = (x, cy)
    strip.finish_layer(layer)
    return strip, buf


class Road:
    """The centre: a lit lane that narrows to the horizon, and the car's marker."""

    def __init__(self, parent, x, y, w, h):
        self.obj = lv.obj(parent)
        self.obj.set_pos(x, y)
        self.obj.set_size(w, h)
        plain(self.obj)

        # Lane edges, converging upward, drawn once on a small canvas.
        self.canvas = lv.canvas(self.obj)
        self.canvas.set_size(w, h)
        self.canvas.center()
        plain(self.canvas)
        self._buf = lv.draw_buf_create(w, h, lv.COLOR_FORMAT.ARGB8888, 0)
        self.canvas.set_draw_buf(self._buf)
        self.canvas.fill_bg(_color(0x000000), lv.OPA.TRANSP)
        layer = lv.layer_t()
        self.canvas.init_layer(layer)
        line = lv.draw_line_dsc_t()
        line.init()
        line.width = 2
        line.round_start = True
        line.round_end = True
        top = h // 6
        vx = w // 2
        for sx, ex in ((w * 5 // 100, vx - w // 9), (w * 95 // 100, vx + w // 9)):
            # Each edge is a few straight pieces that fade toward the horizon.
            pieces = 5
            for i in range(pieces):
                t0 = i / pieces
                t1 = (i + 1) / pieces
                line.color = _color(CYAN)
                line.opa = int(30 + 110 * (1 - t0))
                line.p1 = lv.point_precise_t({"x": sx + (ex - sx) * t0, "y": h - (h - top) * t0})
                line.p2 = lv.point_precise_t({"x": sx + (ex - sx) * t1, "y": h - (h - top) * t1})
                lv.draw_line(layer, line)
        self.canvas.finish_layer(layer)

        # The beam: a soft column of light from the marker up the lane.
        beam_h = h * 58 // 100
        beam_w = max(10, w // 9)
        self.beam = lv.obj(self.obj)
        self.beam.set_size(beam_w, beam_h)
        self.beam.align(lv.ALIGN.TOP_MID, 0, h * 18 // 100)
        plain(self.beam)
        self.beam.set_style_radius(beam_w // 2, 0)
        self.beam.set_style_bg_color(_color(CYAN), 0)
        self.beam.set_style_bg_grad_color(_color(CYAN), 0)
        self.beam.set_style_bg_grad_dir(lv.GRAD_DIR.VER, 0)
        self.beam.set_style_bg_opa(0, 0)
        self.beam.set_style_bg_grad_opa(200, 0)
        if hasattr(self.beam, "set_style_blur_radius"):
            self.beam.set_style_blur_radius(max(3, beam_w // 3), 0)

        core_w = max(3, beam_w // 4)
        self.core = lv.obj(self.obj)
        self.core.set_size(core_w, beam_h)
        self.core.align(lv.ALIGN.TOP_MID, 0, h * 18 // 100)
        plain(self.core)
        self.core.set_style_radius(core_w // 2, 0)
        self.core.set_style_bg_color(_color(0xDDFBFF), 0)
        self.core.set_style_bg_grad_color(_color(0xDDFBFF), 0)
        self.core.set_style_bg_grad_dir(lv.GRAD_DIR.VER, 0)
        self.core.set_style_bg_opa(0, 0)
        self.core.set_style_bg_grad_opa(255, 0)

        # The marker: a glowing ring with the car's green dot in it.
        my = h * 18 // 100 + beam_h
        ring = max(24, w // 3)
        self.halo = lv.obj(self.obj)
        self.halo.set_size(min(w - 4, ring * 5 // 2), ring * 2 // 5)
        self.halo.align(lv.ALIGN.TOP_MID, 0, my + ring * 3 // 5)
        plain(self.halo)
        self.halo.set_style_radius(_CIRCLE, 0)
        self.halo.set_style_bg_color(_color(CYAN), 0)
        self.halo.set_style_bg_opa(90, 0)
        if hasattr(self.halo, "set_style_blur_radius"):
            self.halo.set_style_blur_radius(ring // 3, 0)

        self.ring = lv.obj(self.obj)
        self.ring.set_size(ring, ring)
        self.ring.align(lv.ALIGN.TOP_MID, 0, my)
        plain(self.ring)
        self.ring.set_style_radius(_CIRCLE, 0)
        self.ring.set_style_border_width(max(2, ring // 14), 0)
        self.ring.set_style_border_color(_color(CYAN), 0)
        self.ring.set_style_border_opa(230, 0)
        self.ring.set_style_shadow_color(_color(CYAN), 0)
        self.ring.set_style_shadow_width(ring, 0)
        self.ring.set_style_shadow_opa(160, 0)

        dot = max(8, ring // 3)
        self.dot = lv.obj(self.ring)
        self.dot.set_size(dot, dot)
        self.dot.center()
        plain(self.dot)
        self.dot.set_style_radius(_CIRCLE, 0)
        self.dot.set_style_bg_color(_color(GREEN), 0)
        self.dot.set_style_bg_opa(lv.OPA.COVER, 0)
        self.dot.set_style_shadow_color(_color(GREEN), 0)
        self.dot.set_style_shadow_width(dot, 0)
        self.dot.set_style_shadow_opa(200, 0)


class Cluster:
    def __init__(self, vehicle, scr=None):
        self.vehicle = vehicle
        scr = scr or lv.screen_active()
        self.scr = scr
        W = scr.get_width()
        H = scr.get_height()
        self.W, self.H = W, H
        self._blink = None
        self._gear = None
        self._clock = None

        scr.set_style_bg_color(_color(BG), 0)
        scr.set_style_bg_opa(lv.OPA.COVER, 0)
        scr.set_style_pad_all(0, 0)
        scr.remove_flag(lv.obj.FLAG.SCROLLABLE)

        # A lift of blue at the top of the dash, fading to black at the feet.
        wash = lv.obj(scr)
        wash.set_size(W, H)
        wash.set_pos(0, 0)
        plain(wash)
        wash.set_style_radius(0, 0)
        wash.set_style_bg_color(_color(0x0C1736), 0)
        wash.set_style_bg_grad_color(_color(BG), 0)
        wash.set_style_bg_grad_dir(lv.GRAD_DIR.VER, 0)
        wash.set_style_bg_opa(lv.OPA.COVER, 0)
        wash.set_style_bg_main_stop(0, 0)
        wash.set_style_bg_grad_stop(170, 0)

        # The dash's own curves above and below the dials.
        drop = H * 9 // 100
        self._hoods = (
            _hood(scr, W, H * 15 // 100, drop + H * 8 // 100, ((H * 17 // 100, drop, 46, 2), (H * 21 // 100, drop, 22, 1))),
            _hood(scr, W, H * 82 // 100, drop + H * 4 // 100, ((H * 84 // 100, drop, 36, 2),)),
        )

        # Status line: date, clock, outside temperature.
        self.date = self._text(scr, "9/30", lv.font_montserrat_16, DIM)
        self.clock = self._text(scr, "9:59 PM", lv.font_montserrat_24, TEXT)
        self.temp = self._text(scr, "54~61\u00b0F", lv.font_montserrat_16, DIM)
        self.clock.align(lv.ALIGN.TOP_MID, 0, H * 5 // 100)
        self.date.align_to(self.clock, lv.ALIGN.OUT_LEFT_MID, -W * 5 // 100, 0)
        self.temp.align_to(self.clock, lv.ALIGN.OUT_RIGHT_MID, W * 5 // 100, 0)

        # Turn indicators.
        self.left = self._text(scr, "<<<", lv.font_montserrat_24, CYAN)
        self.right = self._text(scr, ">>>", lv.font_montserrat_24, CYAN)
        self.left.align(lv.ALIGN.TOP_MID, -W * 13 // 100, H * 18 // 100)
        self.right.align(lv.ALIGN.TOP_MID, W * 13 // 100, H * 18 // 100)
        for lamp in (self.left, self.right):
            lamp.set_style_text_letter_space(-3, 0)

        # The dials.
        size = min(H * 62 // 100, W * 34 // 100)
        cy = H * 50 // 100
        self.speed = Ring(
            scr,
            size,
            SPEED_STOPS,
            120,
            track=TRACK,
            bg=BG,
            unit="mph",
            caption="13488 mi",
        )
        self.speed.set_pos(W * 27 // 100 - size // 2, cy - size // 2)
        self.power = Ring(
            scr,
            size,
            POWER_STOPS,
            200,
            track=TRACK,
            bg=BG,
            unit="kW",
            caption="3.7 mi/kWh",
        )
        self.power.set_pos(W * 73 // 100 - size // 2, cy - size // 2)

        # The road between them.
        road_w = W * 18 // 100
        road_h = size * 92 // 100
        self.road = Road(scr, W // 2 - road_w // 2, cy - road_h // 2 - H // 50, road_w, road_h)

        # P R N D S along the bottom.
        self.gears = {}
        self.gear_box = lv.obj(scr)
        box = max(22, H // 15)
        self.gear_box.set_size(box, box)
        plain(self.gear_box)
        self.gear_box.set_style_radius(max(3, box // 7), 0)
        self.gear_box.set_style_border_width(2, 0)
        self.gear_box.set_style_border_color(_color(GREEN), 0)
        self.gear_box.set_style_border_opa(200, 0)
        self.gear_box.set_style_shadow_color(_color(GREEN), 0)
        self.gear_box.set_style_shadow_width(box // 2, 0)
        self.gear_box.set_style_shadow_opa(90, 0)
        pitch = max(30, W * 55 // 1000)
        for i, g in enumerate(GEARS):
            lbl = self._text(scr, g, lv.font_montserrat_24, DIM)
            lbl.set_style_text_letter_space(0, 0)
            lbl.align(lv.ALIGN.BOTTOM_MID, (i - 2) * pitch, -H * 4 // 100)
            self.gears[g] = lbl

        self.update()

    def _text(self, parent, text, font, color):
        lbl = lv.label(parent)
        lbl.set_text(text)
        lbl.set_style_text_font(font, 0)
        lbl.set_style_text_color(_color(color), 0)
        lbl.set_style_text_letter_space(1, 0)
        return lbl

    def set_clock(self, text):
        if text != self._clock:
            self._clock = text
            self.clock.set_text(text)

    def update(self):
        v = self.vehicle
        self.speed.set_value(v.speed_mph)
        self.power.set_value(abs(v.power_kw))
        self.speed.set_caption("%d mi" % int(v.odometer_mi))
        self.power.set_caption("%.1f mi/kWh" % v.mi_per_kwh)
        self.power.unit.set_text("kW regen" if v.power_kw < -0.5 else "kW")

        on = v.blink_on()
        state = (v.left and on, v.right and on)
        if state != self._blink:
            self._blink = state
            self.left.set_style_text_opa(255 if state[0] else 70, 0)
            self.right.set_style_text_opa(255 if state[1] else 70, 0)

        if v.gear != self._gear:
            self._gear = v.gear
            for g, lbl in self.gears.items():
                lbl.set_style_text_color(_color(GREEN if g == v.gear else DIM), 0)
            self.gear_box.align_to(self.gears[v.gear], lv.ALIGN.CENTER, 0, 0)
