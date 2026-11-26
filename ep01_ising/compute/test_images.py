"""Test images for episode 1 (top-6 simulations): python test_images.py 1 3 4 7 9 12 -> media/tests/"""
import sys, time, numpy as np, numba as nb
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, hsv_to_rgb
from pathlib import Path
OUT = str(Path(__file__).resolve().parents[2] / "media" / "tests") + "/"
Path(OUT).mkdir(parents=True, exist_ok=True)
BG, FG, MUTED = "#0E1116", "#E6E6E6", "#7A8291"
UPC, DNC = "#F2B544", "#3F7FC8"
SPIN = ListedColormap([DNC, UPC])
TC = 2 / np.log(1 + np.sqrt(2))
plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "text.color": FG, "axes.labelcolor": FG,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.edgecolor": MUTED, "font.size": 13})

@nb.njit(cache=True)
def find(p, i):
    while p[i] != i:
        p[i] = p[p[i]]; i = p[i]
    return i

@nb.njit(cache=True)
def sw(s, beta, n, seed, lab):
    """n Swendsen-Wang sweeps on LxL periodic s (int8). Returns m per sweep; lab = FK cluster roots of last sweep."""
    np.random.seed(seed)
    L = s.shape[0]; N = L * L; pb = 1 - np.exp(-2 * beta)
    p = np.empty(N, np.int64); ms = np.empty(n)
    for t in range(n):
        for a in range(N): p[a] = a
        for i in range(L):
            for j in range(L):
                a = i * L + j
                j2 = (j + 1) % L; i2 = (i + 1) % L
                if s[i, j] == s[i, j2] and np.random.random() < pb:
                    ra = find(p, a); rb = find(p, i * L + j2)
                    if ra != rb: p[ra] = rb
                if s[i, j] == s[i2, j] and np.random.random() < pb:
                    ra = find(p, a); rb = find(p, i2 * L + j)
                    if ra != rb: p[ra] = rb
        fl = np.random.random(N) < 0.5
        tot = 0
        for a in range(N):
            r = find(p, a); lab[a] = r
            if fl[r]: s[a // L, a % L] = -s[a // L, a % L]
            tot += s[a // L, a % L]
        ms[t] = tot / N
    return ms

def equil(L, T, n, s=None, seed=0):
    if s is None: s = np.where(np.random.default_rng(seed).random((L, L)) < .5, 1, -1).astype(np.int8)
    lab = np.empty(L * L, np.int64); sw(s, 1 / T, n, seed, lab); return s, lab

def spin_ax(ax, s, title=None):
    ax.imshow(s, cmap=SPIN, vmin=-1, vmax=1, interpolation="nearest"); ax.set_axis_off()
    if title: ax.set_title(title, color=FG, fontsize=13)

def fig1():  # cooling snapshots
    Ts = [3.5, 2.6, 2.35, TC, 2.15, 1.8]; L = 512; s = None
    f, axs = plt.subplots(2, 3, figsize=(12, 8.4))
    for k, (T, ax) in enumerate(zip(Ts, axs.flat)):
        s, _ = equil(L, T, 150, s, k); spin_ax(ax, s.copy(), f"T = {T:.3f}" + ("  (T$_c$)" if T == TC else ""))
    f.suptitle("1 · Cooling through the transition (512², equilibrium snapshots)", color=FG)
    f.savefig(OUT + "1_cooling.png", dpi=110, bbox_inches="tight")

def block(s, rng):
    b = s.reshape(s.shape[0] // 2, 2, s.shape[1] // 2, 2).sum(axis=(1, 3))
    tie = rng.choice(np.array([-1, 1], np.int8), b.shape)
    return np.where(b == 0, tie, np.sign(b)).astype(np.int8)

def fig3():  # block-spin RG flow
    L, W = 2048, 128; Ts = [(2.20, "T = 2.20 (below T$_c$)"), (TC, "T = T$_c$"), (2.35, "T = 2.35 (above T$_c$)")]
    rng = np.random.default_rng(1)
    f, axs = plt.subplots(3, 5, figsize=(15, 9.6))
    for r, (T, lbl) in enumerate(Ts):
        s, _ = equil(L, T, 120, None, 10 + r)
        for c in range(5):
            spin_ax(axs[r, c], s[:W, :W], (f"zoom-out ×{2**c}" if r == 0 else None))
            s = block(s, rng)
        axs[r, 0].text(-12, W / 2, lbl, color=FG, rotation=90, va="center", ha="right", fontsize=13)
    f.suptitle("3 · Block spins: same 128² window after k majority-rule 2×2 coarse-grainings", color=FG)
    f.savefig(OUT + "3_blockspin.png", dpi=110, bbox_inches="tight")

def fig4():  # coloured FK clusters at Tc
    L = 1024; s, lab = equil(L, TC, 150, None, 4)
    roots, inv, cnt = np.unique(lab, return_inverse=True, return_counts=True)
    rng = np.random.default_rng(7); n = len(roots)
    hsv = np.stack([rng.random(n), rng.uniform(.45, .85, n), rng.uniform(.55, 1, n)], 1)
    small = cnt < 30; hsv[small, 1] = .15; hsv[small, 2] = .22   # dust stays dark
    order = np.argsort(-cnt)
    for k, h in zip(order[:4], [.11, .58, .95, .33]): hsv[k] = [h, .8, 1]
    img = hsv_to_rgb(hsv)[inv].reshape(L, L, 3)
    f, ax = plt.subplots(figsize=(10, 10)); ax.imshow(img, interpolation="nearest"); ax.set_axis_off()
    ax.set_title(f"4 · Clusters at T$_c$ (1024², {n} clusters, largest = {cnt.max()/L/L:.1%} of spins)", color=FG)
    f.savefig(OUT + "4_clusters.png", dpi=110, bbox_inches="tight")

def fig7():  # free-energy landscape from P(m)
    L = 16; N = L * L; Ts = [3.0, 2.6, TC, 2.1, 1.9]
    cols = ["#5A6B85", "#8C86B8", "#C792EA", "#E98AA8", "#F2B544"]   # sequential, hot -> cold
    f, ax = plt.subplots(figsize=(10, 6)); edges = np.arange(-1 - 1 / N, 1 + 1.5 / N, 2 / N)
    x = (edges[1:] + edges[:-1]) / 2
    for k, (T, c) in enumerate(zip(Ts, cols)):
        s, lab = equil(L, T, 2000, None, 20 + k)
        ms = sw(s, 1 / T, 1_000_000, 30 + k, lab)
        h, _ = np.histogram(ms, edges); h = h.astype(float)
        h = np.convolve(h, [1, 2, 1], "same") / 4          # parity: only every other bin is reachable
        y = np.where(h >= 30, -np.log(np.where(h > 0, h, 1) / h.sum()) / N, np.nan); y -= np.nanmin(y)
        ax.plot(x, y, color=c, lw=2.2, label=("T = T$_c$ = 2.27" if T == TC else f"T = {T:.1f}"))
    ax.set_xlabel("magnetisation per spin  m"); ax.set_ylabel(r"$-\frac{1}{N}\ln P(m)$  (shifted)")
    ax.grid(color="#262D38", lw=.8); [ax.spines[k].set_visible(False) for k in ("top", "right")]
    ax.legend(frameon=False, loc="upper center", ncol=5, fontsize=11, bbox_to_anchor=(.5, -0.12))
    ax.set_ylim(-0.003, None)
    ax.set_title("7 · The bowl splits in two: measured from simulations (16×16, Swendsen–Wang)", color=FG, pad=12)
    f.savefig(OUT + "7_double_well.png", dpi=110, bbox_inches="tight")

def fig9():  # critical opalescence: structure factor
    L = 512; Ts = [3.0, 2.6, 2.4, TC]; nconf = 16; C = 64
    f, axs = plt.subplots(2, 4, figsize=(16, 8.6)); S_all = []; snaps = []
    for k, T in enumerate(Ts):
        s, lab = equil(L, T, 100, None, 40 + k); S = np.zeros((L, L))
        for c in range(nconf):
            sw(s, 1 / T, 4, 100 * k + c, lab); x = s - s.mean()
            S += np.abs(np.fft.fft2(x)) ** 2 / (L * L)
        S_all.append(np.fft.fftshift(S / nconf)[L//2-C:L//2+C, L//2-C:L//2+C]); snaps.append(s[:128, :128].copy())
    vmax = np.log10(max(S.max() for S in S_all))
    for k, T in enumerate(Ts):
        spin_ax(axs[0, k], snaps[k], f"T = {T:.2f}" if T != TC else "T = T$_c$")
        axs[1, k].imshow(np.log10(S_all[k] + 1e-3), cmap="magma", vmin=-0.5, vmax=vmax, interpolation="bilinear"); axs[1, k].set_axis_off()
    axs[1, 0].set_title("what light sees: |Fourier transform|² (centre = long wavelengths)", color=MUTED, fontsize=11, loc="left")
    f.suptitle("9 · Critical opalescence: the long-wavelength glow explodes at T$_c$", color=FG)
    f.savefig(OUT + "9_opalescence.png", dpi=110, bbox_inches="tight")

def fig12():  # Hopfield memory
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 54)
    glyphs = ["π", "Σ", "ψ", "∞", "λ"]; n = 64; P = []
    for g in glyphs:
        im = Image.new("L", (n, n), 0); d = ImageDraw.Draw(im)
        bb = d.textbbox((0, 0), g, font=font); d.text(((n - bb[2] - bb[0]) / 2, (n - bb[3] - bb[1]) / 2), g, fill=255, font=font)
        P.append(np.where(np.array(im) > 127, 1, -1).ravel())
    X = np.array(P, float); W = np.linalg.pinv(X) @ X; np.fill_diagonal(W, 0)   # projection rule: memories = fixed points
    rng = np.random.default_rng(3); rows = [(0, .35), (2, .45)]
    f, axs = plt.subplots(len(rows), 6, figsize=(15, 5.4))
    for r, (k, noise) in enumerate(rows):
        x = X[k].copy(); flip = rng.random(n * n) < noise; x[flip] *= -1
        shots = {0: x.copy()}; marks = [0, 400, 1000, 2000, 4096 * 2]; t = 0
        for sweep in range(2):
            for i in rng.permutation(n * n):
                x[i] = 1 if W[i] @ x >= 0 else -1; t += 1
                if t in marks: shots[t] = x.copy()
        spin_ax(axs[r, 0], X[k].reshape(n, n), "stored memory" if r == 0 else None)
        for c, tt in enumerate(marks):
            spin_ax(axs[r, c + 1], shots[tt].reshape(n, n), (f"{int(noise*100)}% corrupted" if tt == 0 else f"{tt} updates") )
    f.suptitle("12 · A Hopfield network (an Ising model with learned couplings) remembers: 5 glyphs stored, 4096 spins", color=FG)
    f.savefig(OUT + "12_hopfield.png", dpi=110, bbox_inches="tight")

if __name__ == "__main__":
    for name in sys.argv[1:]:
        t = time.time(); globals()["fig" + name](); print(f"fig{name}: {time.time()-t:.0f}s", flush=True)
