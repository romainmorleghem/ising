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
