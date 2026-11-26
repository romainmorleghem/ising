"""All simulation data used by scenes s02-s08 (cooling movie for s00-s01: movies.py).

    python data.py            # everything -> media/data/*.npz   (≈ 10 min on 4 cores)
    python data.py thermo pm  # only some items

Units J = k_B = 1. Swendsen-Wang (SW) for equilibrium samples, Metropolis for dynamics.
"""
import sys
import time
from pathlib import Path

import numba as nb
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "media" / "data"
TC = 2 / np.log(1 + np.sqrt(2))


# ---------------------------------------------------------------------------------------- kernels
@nb.njit(cache=True)
def _find(p, i):
    while p[i] != i:
        p[i] = p[p[i]]
        i = p[i]
    return i


@nb.njit(cache=True)
def sw(s, beta, n, lab):
    """n SW sweeps on a periodic LxL lattice. Returns (m, e) per sweep; lab = FK cluster roots (last sweep)."""
    L = s.shape[0]
    N = L * L
    pb = 1 - np.exp(-2 * beta)
    p = np.empty(N, np.int64)
    ms = np.empty(n)
    es = np.empty(n)
    for t in range(n):
        for a in range(N):
            p[a] = a
        for i in range(L):
            for j in range(L):
                a = i * L + j
                j2 = (j + 1) % L
                i2 = (i + 1) % L
                if s[i, j] == s[i, j2] and np.random.random() < pb:
                    ra, rb = _find(p, a), _find(p, i * L + j2)
                    if ra != rb:
                        p[ra] = rb
                if s[i, j] == s[i2, j] and np.random.random() < pb:
                    ra, rb = _find(p, a), _find(p, i2 * L + j)
                    if ra != rb:
                        p[ra] = rb
        fl = np.random.random(N) < 0.5
        for a in range(N):
            r = _find(p, a)
            lab[a] = r
            if fl[r]:
                s[a // L, a % L] = -s[a // L, a % L]
        m = 0
        e = 0
        for i in range(L):
            for j in range(L):
                m += s[i, j]
                e -= s[i, j] * (s[(i + 1) % L, j] + s[i, (j + 1) % L])
        ms[t] = m / N
        es[t] = e / N
    return ms, es


@nb.njit(cache=True)
def chain_metropolis(s, T, n):
    """n Metropolis sweeps of a periodic 1D chain."""
    L = s.shape[0]
    for _ in range(n * L):
        i = np.random.randint(L)
        dE = 2 * s[i] * (s[(i - 1) % L] + s[(i + 1) % L])
        if dE <= 0 or np.random.random() < np.exp(-dE / T):
            s[i] = -s[i]


@nb.njit(cache=True)
def seed(k):
    np.random.seed(k)


def equil(L, T, n, s=None, k=0):
    seed(k)
    if s is None:
        s = np.where(np.random.default_rng(k).random((L, L)) < 0.5, 1, -1).astype(np.int8)
    lab = np.empty(L * L, np.int64)
    sw(s, 1 / T, n, lab)
    return s, lab


def pack(s):
    return np.packbits(s > 0, axis=1)


# ---------------------------------------------------------------------------------------- items
def chain():
    """s02: space-time diagrams of a 1D chain (time downwards), starting fully ordered."""
    out = {}
    for name, T, L, rows, spr in (("cold", 0.7, 360, 200, 3), ("warm", 1.6, 360, 200, 1)):
        seed(1)
        s = np.ones(L, np.int8)
        st = np.empty((rows, L), np.int8)
        for r in range(rows):
            st[r] = s
            chain_metropolis(s, T, spr)
        out[name], out[name + "_T"] = st, T
    np.savez_compressed(OUT / "chain.npz", **out)


def snapshots():
    """s03/s05/s06: equilibrium 512² snapshots."""
    Ts = np.array([1.8, 2.0, 2.15, TC, 2.5, 3.0])
    frames = []
    s = None
    for k, T in enumerate(Ts):
        s, _ = equil(512, T, 150, None, 10 + k)
        if s.mean() < 0:
            s = -s                      # gauge: majority gold
        frames.append(pack(s))
    np.savez_compressed(OUT / "snapshots.npz", T=Ts, frames=np.array(frames))


def thermo():
    """s05: <|m|>(T) and C(T) for several sizes."""
    Ts = np.unique(np.concatenate([np.linspace(1.5, 3.5, 17), TC + np.linspace(-0.2, 0.2, 9)]))
    res = {"T": Ts}
    for L, n in ((32, 20000), (64, 6000), (128, 2500)):
        m, c = [], []
        s = None
        for k, T in enumerate(Ts):
            s, lab = equil(L, T, 200, s, 100 * L + k)
            ms, es = sw(s, 1 / T, n, lab)
            m.append(np.abs(ms).mean())
            c.append(L * L * es.var() / T ** 2)
        res[f"m{L}"], res[f"c{L}"] = np.array(m), np.array(c)
        print(f"   L={L} done", flush=True)
    np.savez_compressed(OUT / "thermo.npz", **res)


def pm():
    """s04: -(1/N) ln P(m) measured on a 16x16 lattice."""
    L, N = 16, 256
    Ts = np.array([3.0, 2.6, TC, 2.1, 1.9])
    edges = np.arange(-1 - 1 / N, 1 + 1.5 / N, 2 / N)
    x = (edges[1:] + edges[:-1]) / 2
    ys = []
    for k, T in enumerate(Ts):
        s, lab = equil(L, T, 2000, None, 20 + k)
        ms, _ = sw(s, 1 / T, 600_000, lab)
        h = np.histogram(ms, edges)[0].astype(float)
        h = np.convolve(h, [1, 2, 1], "same") / 4
        y = np.where(h >= 30, -np.log(np.maximum(h, 1) / h.sum()) / N, np.nan)
        ys.append(y - np.nanmin(y))
    np.savez_compressed(OUT / "pm.npz", T=Ts, x=x, y=np.array(ys))


def blocks():
    """s06: three 2048² configurations (below, at, above T_c) for the block-spin flow."""
    Ts = np.array([2.20, TC, 2.35])
    frames = []
    for k, T in enumerate(Ts):
        s, _ = equil(2048, T, 120, None, 30 + k)
        if s.mean() < 0:
            s = -s
        frames.append(pack(s))
    np.savez_compressed(OUT / "blocks.npz", T=Ts, frames=np.array(frames))


def clusters():
    """s06: FK clusters at T_c on 1024²: label map (renumbered by size) and size distribution."""
    s, lab = equil(1024, TC, 150, None, 4)
    roots, inv, cnt = np.unique(lab, return_inverse=True, return_counts=True)
    order = np.argsort(-cnt)
    rank = np.empty_like(order)
    rank[order] = np.arange(len(order))
    labels = rank[inv].reshape(1024, 1024).astype(np.int32)          # 0 = largest cluster
    sizes = np.sort(cnt)[::-1]
    # size distribution from several independent samples (log bins)
    allc = [cnt]
    for k in range(6):
        _, lab = equil(1024, TC, 10, s, 50 + k)
        allc.append(np.unique(lab, return_counts=True)[1])
    allc = np.concatenate(allc)
    bins = np.unique(np.round(np.logspace(0, np.log10(allc.max() + 1), 40)).astype(int))
    h = np.histogram(allc, bins)[0] / np.diff(bins) / 7 / 1024 ** 2
    np.savez_compressed(OUT / "clusters.npz", labels=labels, sizes=sizes, spins=pack(s),
                        bins=bins, density=h)


def opal():
    """s07: structure factor S(k) vs T (critical opalescence), with real-space thumbnails."""
    L, C, nconf = 256, 40, 24
    Ts = np.array([3.2, 2.9, 2.7, 2.55, 2.45, 2.38, 2.32, 2.29, TC])
    S_all, thumbs = [], []
    for k, T in enumerate(Ts):
        s, lab = equil(L, T, 100, None, 60 + k)
        S = np.zeros((L, L))
        for c in range(nconf):
            sw(s, 1 / T, 3, lab)
            x = s - s.mean()
            S += np.abs(np.fft.fft2(x)) ** 2 / (L * L)
        S_all.append(np.fft.fftshift(S / nconf)[L // 2 - C:L // 2 + C, L // 2 - C:L // 2 + C])
        thumbs.append(pack(s[:128, :128]))
    np.savez_compressed(OUT / "opal.npz", T=Ts, S=np.array(S_all), thumbs=np.array(thumbs))


def hopfield():
    """s08: Hopfield recall of corrupted glyphs (projection rule), frames every 128 updates."""
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 54)
    glyphs = ["π", "Σ", "ψ", "∞", "λ"]
    n = 64
    P = []
    for g in glyphs:
        im = Image.new("L", (n, n), 0)
        d = ImageDraw.Draw(im)
        bb = d.textbbox((0, 0), g, font=font)
        d.text(((n - bb[2] - bb[0]) / 2, (n - bb[3] - bb[1]) / 2), g, fill=255, font=font)
        P.append(np.where(np.array(im) > 127, 1, -1).ravel())
    X = np.array(P, float)
    W = np.linalg.pinv(X) @ X
    np.fill_diagonal(W, 0)
    rng = np.random.default_rng(3)
    out = {"patterns": X.astype(np.int8).reshape(-1, n, n)}
    # psi at 48 % noise (seed 3) falls into a spurious mixture state (overlap 0.89 with pi, not a memory)
    for name, k, noise, sweeps, r in (("pi", 0, 0.35, 2, rng), ("sigma", 1, 0.40, 2, rng),
                                      ("psi", 2, 0.48, 3, np.random.default_rng(3))):
        rng = r
        x = X[k].copy()
        x[rng.random(n * n) < noise] *= -1
        frames = [x.copy()]
        t = 0
        for _ in range(sweeps):
            for i in rng.permutation(n * n):
                x[i] = 1 if W[i] @ x >= 0 else -1
                t += 1
                if t % 128 == 0:
                    frames.append(x.copy())
        out[name] = np.array(frames, np.int8).reshape(-1, n, n)
        out[name + "_overlap"] = np.array(frames) @ X.T / (n * n)
    np.savez_compressed(OUT / "hopfield.npz", **out)


ITEMS = ["chain", "snapshots", "pm", "thermo", "blocks", "clusters", "opal", "hopfield"]

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or ITEMS:
        t = time.time()
        globals()[name]()
        print(f"{name:10s} {time.time() - t:6.0f}s", flush=True)
