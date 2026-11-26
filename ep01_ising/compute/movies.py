"""Simulation movies played back in the scenes (Metropolis dynamics, so the evolution looks physical).

    python movies.py        # -> media/data/cooling.npz (≈ 1 min, 4 cores)

Each phase stores bit-packed frames (n, L, L/8) and the temperature of each frame. Scenes map a phase
onto the duration of the matching voice line, so the playback speed adapts to the narration.
"""
import time
from pathlib import Path

import numba as nb
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "media" / "data"
TC = 2 / np.log(1 + np.sqrt(2))


@nb.njit(parallel=True, cache=True)
def metropolis(s, T, n):
    """n checkerboard Metropolis sweeps at temperature T (J = k_B = 1), periodic LxL lattice."""
    L = s.shape[0]
    a4, a8 = np.exp(-4.0 / T), np.exp(-8.0 / T)
    for _ in range(n):
        for parity in range(2):
            for i in nb.prange(L):
                for j in range((i + parity) % 2, L, 2):
                    h = s[(i - 1) % L, j] + s[(i + 1) % L, j] + s[i, (j - 1) % L] + s[i, (j + 1) % L]
                    dE = 2 * s[i, j] * h
                    if dE <= 0 or np.random.random() < (a4 if dE == 4 else a8):
                        s[i, j] = -s[i, j]


def run_phase(s, temps, sweeps_per_frame):
    frames = np.empty((len(temps), s.shape[0], s.shape[1] // 8), np.uint8)
    for k, T in enumerate(temps):
        metropolis(s, T, sweeps_per_frame)
        frames[k] = np.packbits(s > 0, axis=1)
    return frames, np.asarray(temps, float)


def cooling(L=512, seed=0):
    np.random.seed(seed)
    s = np.ones((L, L), np.int8)
    x = lambda n: np.linspace(0, 1, n)
    phases = {
        "cold": (np.full(60, 1.5), 2),                               # ordered, a few thermal flips
        "heat": (1.5 + 2.5 * x(150), 2),                             # melts into noise
        "cool": (TC + (4.0 - TC) * (1 - x(300)) ** 2, 15),           # slow cooling, slowing near T_c
        "tc": (np.full(400, TC), 50),                                # hold at T_c: structures of all sizes
        "below": (TC - (TC - 1.9) * x(400), 30),                     # domains win territory
    }
    out = {}
    for name, (temps, spf) in phases.items():
        t = time.time()
        f, T = run_phase(s, temps, spf)
        out[name], out[name + "_T"] = f, T
        print(f"{name:6s} {len(temps)} frames x {spf} sweeps  ({time.time() - t:.0f}s)", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT / "cooling.npz", L=L, **out)


if __name__ == "__main__":
    cooling()
