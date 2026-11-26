// Hopfield network on n×n binary neurons (±1). Couplings W = (1/N) Ξ C⁻¹ Ξᵀ with C = ΞᵀΞ / N
// (pseudo-inverse / projection rule) or C = identity (Hebb's rule). W is never built: the local field
// h_i = Σ_μ ξ_i^μ (C⁻¹ q)_μ − W_ii s_i is computed from the overlaps q_μ = (1/N) Σ_j ξ_j^μ s_j.

function invert(A, P) {                       // Gauss-Jordan with a tiny ridge for duplicate patterns
  const M = A.map((r, i) => [...r.map((v, j) => v + (i === j ? 1e-9 : 0)), ...Array.from({ length: P }, (_, j) => +(i === j))]);
  for (let c = 0; c < P; c++) {
    let p = c; for (let r = c + 1; r < P; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
    [M[c], M[p]] = [M[p], M[c]];
    const d = M[c][c] || 1e-12; for (let k = 0; k < 2 * P; k++) M[c][k] /= d;
    for (let r = 0; r < P; r++) if (r !== c) { const f = M[r][c]; if (f) for (let k = 0; k < 2 * P; k++) M[r][k] -= f * M[c][k]; }
  }
  return M.map(r => r.slice(P));
}

export class Hopfield {
  constructor(n = 64) { this.n = n; this.N = n * n; this.pats = []; this.rule = "pinv"; this.s = new Int8Array(this.N).fill(-1); this.rebuild(); }
  rebuild() {
    const P = this.pats.length, N = this.N;
    const Q = Array.from({ length: P }, (_, a) => Array.from({ length: P }, (_, b) => {
      let t = 0; const x = this.pats[a], y = this.pats[b]; for (let i = 0; i < N; i++) t += x[i] * y[i]; return t / N; }));
    this.Ci = this.rule === "pinv" && P ? invert(Q, P) : Array.from({ length: P }, (_, a) => Array.from({ length: P }, (_, b) => +(a === b)));
    this.syncOverlaps();
  }
  syncOverlaps() {
    const N = this.N; this.q = this.pats.map(x => { let t = 0; for (let i = 0; i < N; i++) t += x[i] * this.s[i]; return t / N; });
  }
  overlaps() { return this.q.slice(); }
  setState(s) { this.s.set(s); this.syncOverlaps(); this.order = null; this.quiet = 0; }
  // k asynchronous updates in a random order; returns the number of flips
  step(k, rand) {
    const P = this.pats.length, N = this.N, s = this.s; if (!P) return 0;
    if (!this.order || this.pos >= N) {          // fresh random permutation every sweep
      this.order = this.order || new Uint32Array(N).map((_, i) => i);
      for (let i = N - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [this.order[i], this.order[j]] = [this.order[j], this.order[i]]; }
      this.pos = 0;
    }
    let flips = 0; const a = new Float64Array(P);
    const recompute = () => { for (let m = 0; m < P; m++) { let t = 0; for (let v = 0; v < P; v++) t += this.Ci[m][v] * this.q[v]; a[m] = t; } };
    recompute();
    for (let c = 0; c < k && this.pos < N; c++) {
      const i = this.order[this.pos++]; let h = 0, wii = 0;
      for (let m = 0; m < P; m++) { const xi = this.pats[m][i]; h += xi * a[m];
        for (let v = 0; v < P; v++) wii += xi * this.Ci[m][v] * this.pats[v][i]; }
      h -= wii / N * s[i];
      const ns = h > 0 ? 1 : h < 0 ? -1 : s[i];
      if (ns !== s[i]) { s[i] = ns; flips++; for (let m = 0; m < P; m++) this.q[m] += 2 * ns * this.pats[m][i] / N; recompute(); }
    }
    this.quiet = flips ? 0 : this.quiet + k;
    return flips;
  }
  converged() { return this.quiet >= this.N; }
}
