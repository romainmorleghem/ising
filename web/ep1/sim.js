// 2D Ising model on an L×L periodic lattice (J = k_B = 1): checkerboard Metropolis, Wolff clusters,
// painting, block spins and the structure factor. Spins live in an Int8Array (+1 / -1).
import { hexABGR } from "../assets/plot.js";

export const UP = hexABGR("#F2B544"), DOWN = hexABGR("#3F7FC8");

export class Ising {
  constructor(L = 256, seed = 12345) {
    this.x = seed | 1;                      // xorshift32 state
    this.T = 3; this.h = 0;
    this.setSize(L);
  }
  setSize(L) {
    this.L = L; this.N = L * L; this.lg = Math.log2(L);
    this.s = new Int8Array(this.N);
    this.stack = new Int32Array(this.N);
    this.mark = new Uint32Array(this.N); this.gen = 0;
    this.randomise();
  }
  rand() { let x = this.x; x ^= x << 13; x ^= x >>> 17; x ^= x << 5; this.x = x; return (x >>> 0) / 4294967296; }
  randomise() { for (let i = 0; i < this.N; i++) this.s[i] = this.rand() < 0.5 ? 1 : -1; }
  fill(v) { this.s.fill(v); }
  setParams(T, h) {
    this.T = T; this.h = h;
    // Metropolis acceptance thresholds (×2^32) indexed by [spin up?] * 5 + (neighbour sum + 4) / 2.
    // ΔE = 0 moves are accepted with probability 1/2 (still detailed balance): with probability 1, the
    // checkerboard order pushes diagonal domain walls deterministically and a quench orders far too fast.
    this.thr = new Float64Array(10);
    for (let up = 0; up < 2; up++) for (let k = 0; k < 5; k++) {
      const si = up ? 1 : -1, sum = 2 * k - 4, dE = 2 * si * (sum + h);
      this.thr[up * 5 + k] = dE < 0 ? 4294967296 : dE === 0 ? 2147483648 : Math.exp(-dE / T) * 4294967296;
    }
    this.pAdd = (1 - Math.exp(-2 / T)) * 4294967296;
  }
  // n checkerboard sweeps: every spin of one colour, then every spin of the other
  metropolis(n) {
    const L = this.L, s = this.s, thr = this.thr, m1 = L - 1;
    let x = this.x;
    for (let k = 0; k < n; k++) for (let par = 0; par < 2; par++) for (let i = 0; i < L; i++) {
      const row = i * L, up = ((i + m1) & m1) * L, dn = ((i + 1) & m1) * L;
      for (let j = (i + par) & 1; j < L; j += 2) {
        const idx = row + j, si = s[idx];
        const sum = s[up + j] + s[dn + j] + s[row + ((j + m1) & m1)] + s[row + ((j + 1) & m1)];
        x ^= x << 13; x ^= x >>> 17; x ^= x << 5;
        if ((x >>> 0) < thr[(si > 0 ? 5 : 0) + ((sum + 4) >> 1)]) s[idx] = -si;
      }
    }
    this.x = x;
  }
  // Wolff clusters until about `budget` spins have been visited. With a field h the cluster flip is
  // accepted with probability min(1, e^{-ΔE_h/T}), ΔE_h = 2 h s0 |cluster|.
  wolff(budget) {
    const L = this.L, N = this.N, s = this.s, st = this.stack, mark = this.mark, m1 = L - 1, lg = this.lg, pAdd = this.pAdd;
    let x = this.x, done = 0;
    while (done < budget) {
      if (++this.gen === 0xffffffff) { mark.fill(0); this.gen = 1; }
      const g = this.gen;
      x ^= x << 13; x ^= x >>> 17; x ^= x << 5;
      const a0 = (x >>> 0) % N, s0 = s[a0];
      let n = 0; st[n++] = a0; mark[a0] = g;
      for (let k = 0; k < n; k++) {
        const a = st[k], i = a >> lg, j = a & m1, row = i << lg;
        const nb0 = row + ((j + 1) & m1), nb1 = row + ((j + m1) & m1), nb2 = (((i + 1) & m1) << lg) + j, nb3 = (((i + m1) & m1) << lg) + j;
        if (s[nb0] === s0 && mark[nb0] !== g) { x ^= x << 13; x ^= x >>> 17; x ^= x << 5; if ((x >>> 0) < pAdd) { mark[nb0] = g; st[n++] = nb0; } }
        if (s[nb1] === s0 && mark[nb1] !== g) { x ^= x << 13; x ^= x >>> 17; x ^= x << 5; if ((x >>> 0) < pAdd) { mark[nb1] = g; st[n++] = nb1; } }
        if (s[nb2] === s0 && mark[nb2] !== g) { x ^= x << 13; x ^= x >>> 17; x ^= x << 5; if ((x >>> 0) < pAdd) { mark[nb2] = g; st[n++] = nb2; } }
        if (s[nb3] === s0 && mark[nb3] !== g) { x ^= x << 13; x ^= x >>> 17; x ^= x << 5; if ((x >>> 0) < pAdd) { mark[nb3] = g; st[n++] = nb3; } }
      }
      let accept = true;
      if (this.h !== 0) { const dE = 2 * this.h * s0 * n;
        if (dE > 0) { x ^= x << 13; x ^= x >>> 17; x ^= x << 5; accept = (x >>> 0) / 4294967296 < Math.exp(-dE / this.T); } }
      if (accept) for (let k = 0; k < n; k++) s[st[k]] = -s0;
      done += n + 4;
    }
    this.x = x;
    return done;
  }
  globalFlip() { const s = this.s; for (let i = 0; i < this.N; i++) s[i] = -s[i]; }
  // magnetisation and energy per spin
  stats() {
    const L = this.L, s = this.s, m1 = L - 1; let M = 0, B = 0;
    for (let i = 0; i < L; i++) { const row = i * L, dn = ((i + 1) & m1) * L;
      for (let j = 0; j < L; j++) { const v = s[row + j]; M += v; B += v * (s[row + ((j + 1) & m1)] + s[dn + j]); } }
    const m = M / this.N; return { m, e: -B / this.N - this.h * m };
  }
  // set spins to v inside a disc of radius r (lattice units) centred at (cx, cy), periodic
  paint(cx, cy, r, v) {
    const L = this.L, m1 = L - 1, r2 = r * r, R = Math.ceil(r);
    for (let di = -R; di <= R; di++) for (let dj = -R; dj <= R; dj++) if (di * di + dj * dj <= r2) {
      const i = (Math.floor(cy) + di + L) & m1, j = (Math.floor(cx) + dj + L) & m1; this.s[i * L + j] = v; }
  }
  render(img32) { const s = this.s; for (let i = 0; i < this.N; i++) img32[i] = s[i] > 0 ? UP : DOWN; }
}

// One majority-rule 2×2 coarse-graining of an n×n spin array (ties broken at random).
export function blockSpin(src, n, rand) {
  const h = n >> 1, out = new Int8Array(h * h);
  for (let i = 0; i < h; i++) for (let j = 0; j < h; j++) {
    const a = 2 * i * n + 2 * j, sum = src[a] + src[a + 1] + src[a + n] + src[a + n + 1];
    out[i * h + j] = sum > 0 ? 1 : sum < 0 ? -1 : (rand() < 0.5 ? 1 : -1);
  }
  return out;
}
export function crop(src, n, w) {             // top-left w×w window of an n×n array
  const out = new Int8Array(w * w);
  for (let i = 0; i < w; i++) out.set(src.subarray(i * n, i * n + w), i * w);
  return out;
}
export function paintSpins(img32, arr) { for (let i = 0; i < arr.length; i++) img32[i] = arr[i] > 0 ? UP : DOWN; }

// ---- 2D FFT (radix 2, in place) ----------------------------------------------------------------
export class FFT2 {
  constructor(n) {
    this.n = n; const lg = Math.log2(n);
    this.rev = new Uint32Array(n);
    for (let i = 0; i < n; i++) { let r = 0; for (let b = 0; b < lg; b++) r |= ((i >> b) & 1) << (lg - 1 - b); this.rev[i] = r; }
    this.cos = new Float64Array(n / 2); this.sin = new Float64Array(n / 2);
    for (let i = 0; i < n / 2; i++) { this.cos[i] = Math.cos(2 * Math.PI * i / n); this.sin[i] = -Math.sin(2 * Math.PI * i / n); }
    this.tr = new Float64Array(n); this.ti = new Float64Array(n);
  }
  fft1(re, im) {
    const n = this.n, rev = this.rev;
    for (let i = 0; i < n; i++) { const j = rev[i]; if (j > i) { let t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; } }
    for (let size = 2; size <= n; size <<= 1) {
      const half = size >> 1, step = n / size;
      for (let st = 0; st < n; st += size) for (let k = 0; k < half; k++) {
        const c = this.cos[k * step], s = this.sin[k * step], a = st + k, b = a + half;
        const xr = re[b] * c - im[b] * s, xi = re[b] * s + im[b] * c;
        re[b] = re[a] - xr; im[b] = im[a] - xi; re[a] += xr; im[a] += xi;
      }
    }
  }
  // re, im: n*n row-major, transformed in place
  run(re, im) {
    const n = this.n, tr = this.tr, ti = this.ti;
    for (let i = 0; i < n; i++) { const o = i * n;
      for (let j = 0; j < n; j++) { tr[j] = re[o + j]; ti[j] = im[o + j]; }
      this.fft1(tr, ti);
      for (let j = 0; j < n; j++) { re[o + j] = tr[j]; im[o + j] = ti[j]; } }
    for (let j = 0; j < n; j++) {
      for (let i = 0; i < n; i++) { tr[i] = re[i * n + j]; ti[i] = im[i * n + j]; }
      this.fft1(tr, ti);
      for (let i = 0; i < n; i++) { re[i * n + j] = tr[i]; im[i * n + j] = ti[i]; } }
  }
}

// Structure factor S(k) = |FFT(s - <s>)|² / Σw² of a Hann-windowed n×n window, smoothed over time.
export class Scatter {
  constructor(n) {
    this.n = n; this.fft = new FFT2(n);
    this.re = new Float64Array(n * n); this.im = new Float64Array(n * n); this.S = new Float64Array(n * n);
    this.w = new Float64Array(n); for (let i = 0; i < n; i++) this.w[i] = 0.5 - 0.5 * Math.cos(2 * Math.PI * (i + 0.5) / n);
    let w2 = 0; for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) w2 += (this.w[i] * this.w[j]) ** 2;
    this.norm = 1 / w2; this.fresh = true;
  }
  update(win, alpha = 0.35) {             // win: Int8Array n*n
    const n = this.n, re = this.re, im = this.im, w = this.w; let mean = 0;
    for (let i = 0; i < n * n; i++) mean += win[i]; mean /= n * n;
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { const a = i * n + j; re[a] = (win[a] - mean) * w[i] * w[j]; im[a] = 0; }
    this.fft.run(re, im);
    const S = this.S, f = this.fresh ? 1 : alpha; this.fresh = false;
    for (let a = 0; a < n * n; a++) S[a] += f * ((re[a] * re[a] + im[a] * im[a]) * this.norm - S[a]);
  }
  // mean S over the smallest nonzero wavevectors (|k| ≤ 3 · 2π/n)
  smallK() { const n = this.n; let t = 0, c = 0;
    for (let di = -3; di <= 3; di++) for (let dj = -3; dj <= 3; dj++) { const r = di * di + dj * dj;
      if (r > 0 && r <= 9) { t += this.S[((di + n) % n) * n + ((dj + n) % n)]; c++; } }
    return t / c; }
  // log-scaled image, fftshifted so long wavelengths sit in the centre
  render(img32, lut, lo = -0.5, hi = 2.5) {
    const n = this.n, h = n >> 1, S = this.S;
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
      const v = (Math.log10(S[i * n + j] + 1e-9) - lo) / (hi - lo);
      img32[((i + h) % n) * n + ((j + h) % n)] = lut[Math.max(0, Math.min(255, (v * 255) | 0))];
    }
  }
}
