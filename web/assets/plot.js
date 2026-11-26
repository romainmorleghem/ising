// Small helpers shared by the pages: HiDPI canvas with a data frame, colours, exact Ising maths.
export const C = {
  bg: "#0E1116", fg: "#E6E6E6", muted: "#7A8291", line: "#262D38",
  up: "#F2B544", down: "#3F7FC8", crit: "#C792EA", mf: "#E85D75", exact: "#FFF4D6", hot: "#FF8A4C", cold: "#6CCB8B",
};
export const TC = 2 / Math.log(1 + Math.SQRT2);           // 2.269185...

// A canvas with a data frame [x0,x1]×[y0,y1] and margins for tick labels.
export class Plot {
  constructor(canvas, { x, y, aspect = 0.56, margin = [12, 14, 30, 52] } = {}) {
    this.cv = canvas; this.ctx = canvas.getContext("2d");
    this.x = x; this.y = y; this.aspect = aspect; this.m = margin;   // top right bottom left
    new ResizeObserver(() => this.resize()).observe(canvas);
    this.resize(false);
  }
  resize(redraw = true) {
    const dpr = window.devicePixelRatio || 1, w = this.cv.clientWidth || 600;
    this.asp = typeof this.aspect === "function" ? this.aspect(w) : this.aspect;
    this.cv.style.height = `${Math.round(w * this.asp)}px`;
    this.cv.width = Math.round(w * dpr); this.cv.height = Math.round(w * this.asp * dpr);
    this.dpr = dpr; this.W = w; this.H = w * this.asp;
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    if (redraw && this.onresize) this.onresize();
  }
  get iw() { return this.W - this.m[1] - this.m[3]; }
  get ih() { return this.H - this.m[0] - this.m[2]; }
  px(v) { return this.m[3] + (v - this.x[0]) / (this.x[1] - this.x[0]) * this.iw; }
  py(v) { return this.m[0] + (this.y[1] - v) / (this.y[1] - this.y[0]) * this.ih; }
  clear() { const c = this.ctx; c.fillStyle = C.bg; c.fillRect(0, 0, this.W, this.H); }
  axes({ xt = 4, yt = 4, xl = "", yl = "", yfmt = null, xfmt = null, yv = null } = {}) {
    const c = this.ctx; c.strokeStyle = C.muted; c.lineWidth = 1; c.fillStyle = C.muted;
    c.font = "11px system-ui, sans-serif";
    c.beginPath(); c.moveTo(this.m[3], this.m[0]); c.lineTo(this.m[3], this.H - this.m[2]);
    c.lineTo(this.W - this.m[1], this.H - this.m[2]); c.stroke();
    const fmt = v => Math.abs(v) < 1e-12 ? "0" : +v.toPrecision(4) + "";
    c.textAlign = "center"; c.textBaseline = "top";
    for (let i = 0; i <= xt; i++) { const v = this.x[0] + i / xt * (this.x[1] - this.x[0]);
      c.fillText((xfmt || fmt)(v), this.px(v), this.H - this.m[2] + 5); }
    c.textAlign = "right"; c.textBaseline = "middle";
    const yvals = yv || (yt ? Array.from({ length: yt + 1 }, (_, i) => this.y[0] + i / yt * (this.y[1] - this.y[0])) : []);
    for (const v of yvals) c.fillText((yfmt || fmt)(v), this.m[3] - 5, this.py(v));
    c.font = "italic 13px Georgia, serif"; c.fillStyle = C.fg;
    if (xl) { c.textAlign = "right"; c.textBaseline = "bottom"; c.fillText(xl, this.W - this.m[1], this.H - this.m[2] - 3); }
    if (yl) { c.textAlign = "left"; c.textBaseline = "top"; c.fillText(yl, this.m[3] + 6, this.m[0]); }
  }
  clip(draw) { const c = this.ctx; c.save(); c.beginPath(); c.rect(this.m[3], this.m[0], this.iw, this.ih); c.clip(); draw(); c.restore(); }
  line(pts, color, width = 1.5, alpha = 1, dash = null) {
    this.clip(() => { const c = this.ctx; c.strokeStyle = color; c.lineWidth = width; c.globalAlpha = alpha;
      if (dash) c.setLineDash(dash);
      c.beginPath(); pts.forEach(([a, b], i) => i ? c.lineTo(this.px(a), this.py(b)) : c.moveTo(this.px(a), this.py(b)));
      c.stroke(); c.globalAlpha = 1; c.setLineDash([]); });
  }
  fill(pts, color, alpha = 0.5, base = null) {
    base = base ?? this.y[0];
    this.clip(() => { const c = this.ctx; c.fillStyle = color; c.globalAlpha = alpha; c.beginPath();
      c.moveTo(this.px(pts[0][0]), this.py(base));
      pts.forEach(([a, b]) => c.lineTo(this.px(a), this.py(b)));
      c.lineTo(this.px(pts[pts.length - 1][0]), this.py(base)); c.closePath(); c.fill(); c.globalAlpha = 1; });
  }
  // markers: filled or hollow circles, optional vertical error bars [x, y, err]
  dots(pts, color, r = 3, hollow = false) {
    this.clip(() => { const c = this.ctx; c.strokeStyle = color; c.fillStyle = color; c.lineWidth = 1.5;
      for (const [a, b, e] of pts) {
        const X = this.px(a), Y = this.py(b);
        if (e) { c.beginPath(); c.moveTo(X, this.py(b - e)); c.lineTo(X, this.py(b + e)); c.stroke(); }
        c.beginPath(); c.arc(X, Y, r, 0, 2 * Math.PI); hollow ? c.stroke() : c.fill();
      } });
  }
  vline(x, color, dash = [4, 4], label = "", width = 1.5) {
    this.line([[x, this.y[0]], [x, this.y[1]]], color, width, 1, dash);
    if (label) { const c = this.ctx; c.fillStyle = color; c.font = "12px system-ui, sans-serif";
      c.textAlign = "left"; c.textBaseline = "top"; c.fillText(label, this.px(x) + 4, this.m[0] + 2); }
  }
  text(s, x, y, color, align = "left", base = "middle", font = "12px system-ui, sans-serif") {
    const c = this.ctx; c.fillStyle = color; c.font = font; c.textAlign = align; c.textBaseline = base;
    c.fillText(s, this.px(x), this.py(y));
  }
}

// ---- exact Ising maths (J = k_B = 1) ------------------------------------------------------
// Onsager–Yang spontaneous magnetisation
export const mExact = T => T < TC ? Math.pow(1 - Math.pow(Math.sinh(2 / T), -4), 0.125) : 0;
// mean field m = tanh(4m/T), largest root
export function mMF(T, h = 0) {
  if (T >= 4 && h === 0) return 0;
  let m = 1; for (let i = 0; i < 2000; i++) { const n = Math.tanh((4 * m + h) / T); if (Math.abs(n - m) < 1e-12) break; m = n; }
  return m;
}
// complete elliptic integral of the first kind K(k) via the arithmetic-geometric mean
export function ellipK(k) { let a = 1, b = Math.sqrt(1 - k * k);
  for (let i = 0; i < 40 && Math.abs(a - b) > 1e-15; i++) [a, b] = [(a + b) / 2, Math.sqrt(a * b)];
  return Math.PI / (2 * a); }
// Onsager's internal energy per spin and specific heat (numerical derivative)
export function uExact(T) {
  const b = 1 / T, k = 2 * Math.sinh(2 * b) / Math.cosh(2 * b) ** 2, t = Math.tanh(2 * b);
  return -(1 / t) * (1 + (2 / Math.PI) * (2 * t * t - 1) * ellipK(Math.min(k, 1 - 1e-16)));
}
export const cExact = T => { const d = 1e-4; return (uExact(T + d) - uExact(T - d)) / (2 * d); };
// mean-field free energy per spin f(m) = -2 m^2 - h m - T s(m)
export function fMF(m, T, h = 0) {
  const a = (1 + m) / 2, b = (1 - m) / 2, xl = x => x > 0 ? x * Math.log(x) : 0;
  return -2 * m * m - h * m + T * (xl(a) + xl(b));
}

// seeded PRNG (mulberry32) so that runs are reproducible
export function rng(seed = 1) {
  let a = seed >>> 0;
  return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
}

// magma-like colormap: 256 packed ABGR (little-endian RGBA) entries
export const MAGMA = (() => {
  const s = [[0, 0, 4], [28, 16, 68], [79, 18, 123], [129, 37, 129], [181, 54, 122], [229, 80, 100],
             [251, 135, 97], [254, 194, 135], [252, 253, 191]];
  const out = new Uint32Array(256);
  for (let i = 0; i < 256; i++) {
    const x = i / 255 * (s.length - 1), k = Math.min(s.length - 2, Math.floor(x)), f = x - k;
    const [r, g, b] = [0, 1, 2].map(j => Math.round(s[k][j] + f * (s[k + 1][j] - s[k][j])));
    out[i] = 0xff000000 | b << 16 | g << 8 | r;
  }
  return out;
})();
export const hexABGR = h => { const v = parseInt(h.slice(1), 16); return (0xff000000 | (v & 0xff) << 16 | (v & 0xff00) | (v >> 16)) >>> 0; };
