"""Imported first by every scene of episode 1: paths, style, narration, spin-lattice helpers."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
DATA = ROOT / "ep01_ising" / "data"

from common import style  # noqa: E402
style.setup()
from manim import config as _cfg  # noqa: E402
_cfg.disable_caching = True

import numpy as np  # noqa: E402
from manim import ImageMobject  # noqa: E402
from manim.constants import RESAMPLING_ALGORITHMS  # noqa: E402
from common.style import UP_SPIN, DOWN_SPIN  # noqa: E402
from common.narrative import Narrated, NarratedCamera  # noqa: E402,F401


def spin_image(s, height=6.0):
    """A ±1 array as a crisp pixel image (gold = up, blue = down)."""
    up = np.array(UP_SPIN.to_rgb()) * 255
    dn = np.array(DOWN_SPIN.to_rgb()) * 255
    rgb = np.where(s[..., None] > 0, up, dn).astype(np.uint8)
    img = ImageMobject(rgb)
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.set(height=height)


# --------------------------------------------------------------------------------------------
# Simulation movies (computed by compute/movies.py) and small widgets shared by the scenes
# --------------------------------------------------------------------------------------------
from manim import (VGroup, Square, Arrow, Line, Rectangle, RoundedRectangle, MathTex, Tex,  # noqa: E402
                   DecimalNumber, UpdateFromAlphaFunc, AnimationGroup, Rotate, interpolate_color,
                   linear, UP, DOWN, LEFT, RIGHT, PI)
from common.style import BG, FG, MUTED, HOT, COLD, CRITICAL  # noqa: E402

TC = 2 / np.log(1 + np.sqrt(2))
MEDIA_DATA = ROOT / "media" / "data"
_LUT = np.array([[*(np.array(DOWN_SPIN.to_rgb()) * 255), 255],
                 [*(np.array(UP_SPIN.to_rgb()) * 255), 255]], np.uint8)


class Movie:
    """Bit-packed frames of a simulation, by phase: movie["tc"] -> (frames, temperatures)."""

    def __init__(self, name):
        self.d = np.load(MEDIA_DATA / f"{name}.npz")

    def __getitem__(self, phase):
        return self.d[phase], self.d[phase + "_T"]

    def spins(self, phase, k):
        return np.unpackbits(self.d[phase][k], axis=1).astype(np.int8) * 2 - 1

    def rgba(self, phase, k):
        return _LUT[np.unpackbits(self.d[phase][k], axis=1)]

    def image(self, phase, k, height=6.4):
        img = ImageMobject(self.rgba(phase, k))
        img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        return img.set(height=height)

    def play(self, phase, img, therm=None, a0=0.0, a1=1.0):
        """Animation playing frames a0..a1 (fractions) of `phase` into `img` (and the thermometer)."""
        frames, temps = self[phase]
        n = len(frames)

        def idx(alpha):
            return int(round((a0 + (a1 - a0) * alpha) * (n - 1)))

        def upd_img(m, alpha):
            m.pixel_array = _LUT[np.unpackbits(frames[idx(alpha)], axis=1)]

        anims = [UpdateFromAlphaFunc(img, upd_img)]
        if therm is not None:
            anims.append(UpdateFromAlphaFunc(therm, lambda m, a: m.set_T(temps[idx(a)])))
        return AnimationGroup(*anims, rate_func=linear)


class Thermometer(VGroup):
    """Vertical thermometer, T in units of J/k_B, coloured from COLD to HOT."""

    def __init__(self, T=1.5, tmin=1.5, tmax=4.0, height=5.0):
        super().__init__()
        self.tmin, self.tmax, self.h = tmin, tmax, height
        self.tube = RoundedRectangle(corner_radius=0.17, width=0.42, height=height + 0.1,
                                     stroke_color=MUTED, stroke_width=2)
        self.fill = Rectangle(width=0.28, height=0.1, stroke_width=0, fill_opacity=1)
        self.num = DecimalNumber(T, num_decimal_places=2, font_size=36, color=FG)
        self.lab = VGroup(MathTex("T=", font_size=36, color=FG), self.num).arrange(RIGHT, buff=0.12)
        self.lab.next_to(self.tube, UP, buff=0.3)
        self.add(self.tube, self.fill, self.lab)
        self.set_T(T)

    def y_of(self, T):
        x = (T - self.tmin) / (self.tmax - self.tmin)
        return self.tube.get_bottom()[1] + 0.05 + max(0.02, min(1, x)) * self.h

    def set_T(self, T):
        x = min(1, max(0, (T - self.tmin) / (self.tmax - self.tmin)))
        top = self.y_of(T)
        bottom = self.tube.get_bottom()[1] + 0.05
        self.fill.stretch_to_fit_height(max(top - bottom, 0.02))
        self.fill.move_to([self.tube.get_center()[0], (top + bottom) / 2, 0])
        self.fill.set_fill(HOT)
        self.num.set_value(T)
        return self

    def tc_mark(self, label=r"T_c\approx 2.27"):
        y = self.y_of(TC)
        x0 = self.tube.get_left()[0]
        tick = Line([x0 - 0.15, y, 0], [self.tube.get_right()[0] + 0.15, y, 0], color=CRITICAL, stroke_width=3)
        lab = MathTex(label, font_size=30, color=CRITICAL).next_to(tick, LEFT, buff=0.15)
        return VGroup(tick, lab)


class SpinGrid(VGroup):
    """A small lattice of arrows on coloured squares; s[i, j] = ±1, row 0 at the top."""

    def __init__(self, s, size=0.6):
        super().__init__()
        self.s = np.array(s, dtype=int)
        self.size = size
        n, m = self.s.shape
        self.sq, self.ar = {}, {}
        for i in range(n):
            for j in range(m):
                sq = Square(size, stroke_color=BG, stroke_width=3, fill_opacity=1,
                            fill_color=UP_SPIN if self.s[i, j] > 0 else DOWN_SPIN)
                sq.move_to([(j - (m - 1) / 2) * size, ((n - 1) / 2 - i) * size, 0])
                ar = Arrow(DOWN * 0.3 * size, UP * 0.3 * size, buff=0, color=BG, stroke_width=5,
                           max_tip_length_to_length_ratio=0.42, max_stroke_width_to_length_ratio=20)
                ar.move_to(sq).set_z_index(1)       # stays above its square when the square is animated
                if self.s[i, j] < 0:
                    ar.rotate(PI)
                self.sq[i, j], self.ar[i, j] = sq, ar
                self.add(VGroup(sq, ar))

    def cell(self, i, j):
        return VGroup(self.sq[i, j], self.ar[i, j])

    def flip(self, i, j):
        self.s[i, j] *= -1
        col = UP_SPIN if self.s[i, j] > 0 else DOWN_SPIN
        return AnimationGroup(Rotate(self.ar[i, j], PI), self.sq[i, j].animate.set_fill(col))

    def neighbours(self, i, j):
        n, m = self.s.shape
        return [(a, b) for a, b in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)) if 0 <= a < n and 0 <= b < m]

    def edge(self, a, b, color, width=7):
        """The shared edge between neighbouring cells a and b, as a Line."""
        ca, cb = self.sq[a].get_center(), self.sq[b].get_center()
        mid, d = (ca + cb) / 2, cb - ca
        perp = np.array([-d[1], d[0], 0]) / np.linalg.norm(d) * self.size / 2
        return Line(mid - perp, mid + perp, color=color, stroke_width=width)

    def borders(self, color, width=7):
        """All edges between disagreeing neighbours: the domain walls."""
        n, m = self.s.shape
        out = VGroup()
        for i in range(n):
            for j in range(m):
                for a, b in ((i + 1, j), (i, j + 1)):
                    if a < n and b < m and self.s[i, j] != self.s[a, b]:
                        out.add(self.edge((i, j), (a, b), color, width))
        return out

    def delta_E(self, i, j):
        """Energy change (in units of J) if spin (i, j) flips (free boundaries)."""
        return 2 * self.s[i, j] * sum(self.s[a, b] for a, b in self.neighbours(i, j))


# --------------------------------------------------------------------------------------------
# Data files (compute/data.py) and plotting helpers
# --------------------------------------------------------------------------------------------
from manim import Axes  # noqa: E402
from common.style import GRID  # noqa: E402


def load(name):
    return np.load(MEDIA_DATA / f"{name}.npz")


def unpack(packed):
    return np.unpackbits(packed, axis=-1).astype(np.int8) * 2 - 1


def lattice_image(s, height=6.0):
    """±1 array (or bit-packed rows) -> crisp ImageMobject."""
    if s.dtype == np.uint8:
        s = unpack(s)
    img = ImageMobject(_LUT[(s > 0).astype(np.uint8)])
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.set(height=height)


def rgb_image(rgb, height=6.0, smooth=False):
    img = ImageMobject(np.asarray(rgb, np.uint8))
    if not smooth:
        img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.set(height=height)


def block2(s, rng):
    """Majority rule on 2x2 blocks, ties broken at random."""
    b = s.reshape(s.shape[0] // 2, 2, s.shape[1] // 2, 2).sum(axis=(1, 3))
    tie = rng.choice(np.array([-1, 1], np.int8), b.shape)
    return np.where(b == 0, tie, np.sign(b)).astype(np.int8)


def axes(x_range, y_range, x_length=6.5, y_length=4.2, x_label=None, y_label=None, tips=False, **kw):
    ax = Axes(x_range=x_range, y_range=y_range, x_length=x_length, y_length=y_length, tips=tips,
              axis_config=dict(color=MUTED, stroke_width=2, include_numbers=True, font_size=24,
                               decimal_number_config=dict(num_decimal_places=kw.pop("decimals", 1), color=MUTED)),
              **kw)
    labs = VGroup()
    if x_label:
        labs.add(MathTex(x_label, font_size=32, color=FG).next_to(ax.x_axis, DOWN, buff=0.45))
    if y_label:
        labs.add(MathTex(y_label, font_size=32, color=FG).next_to(ax.y_axis, UP, buff=0.2))
    return ax, labs
