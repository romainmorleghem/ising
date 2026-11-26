import { C, TC, Plot, mExact, mMF, cExact, fMF, rng, MAGMA } from "../assets/plot.js";
import { Ising, blockSpin, crop, paintSpins, Scatter } from "./sim.js";
import { Hopfield } from "./hopfield.js";

const $ = id => document.getElementById(id);
const segValue = (seg, attr) => seg.querySelector("button.on").dataset[attr];
function wireSeg(seg, cb) {
  seg.querySelectorAll("button").forEach(b => b.onclick = () => {
    seg.querySelectorAll("button").forEach(x => { x.classList.toggle("on", x === b); x.setAttribute("aria-pressed", x === b); });
    cb(b);
  });
}
const fmtS = (v, d = 3) => (v < 0 ? "−" : v > 0 ? "+" : "") + Math.abs(v).toFixed(d);
// visibility of each widget (pause what is offscreen)
const visible = new Set();
const io = new IntersectionObserver(es => es.forEach(e => e.isIntersecting ? visible.add(e.target.id) : visible.delete(e.target.id)),
  { rootMargin: "100px" });
["sim-widget", "mT-widget", "blk-widget", "fft-widget", "hop-widget"].forEach(id => io.observe($(id)));
let DATA = null;

// ================================================================ 1. live simulator
const sim = new Ising(256, 20251126);
const lat = $("lat"), lctx = lat.getContext("2d");
let img = lctx.createImageData(sim.L, sim.L), img32 = new Uint32Array(img.data.buffer);
let T = TC, h = 0, paused = false, prevSign = 0;
const trace = new Float32Array(480); let traceN = 0;
const tracePlot = new Plot($("trace"), { x: [0, trace.length], y: [-1, 1], aspect: 0.3, margin: [8, 8, 8, 34] });

function setT(v, fromSlider = false) {
  T = v; if (!fromSlider) $("T").value = v.toFixed(2);
  const atTc = Math.abs(T - TC) < 1e-6;
  $("T-o").textContent = atTc ? "2.269 = T_c" : T.toFixed(2);
  sim.setParams(T, h);
}
function setH(v) { h = v; $("h").value = v; $("h-o").textContent = fmtS(h, 2).replace("+0.00", "0").replace("−0.00", "0"); sim.setParams(T, h); }
function placeTick() {           // T_c mark above the slider (thumb ≈ 16 px)
  const r = $("T"), f = (TC - r.min) / (r.max - r.min);
  $("tc-tick").style.left = `calc(8px + (100% - 16px) * ${f} - 1px)`;
}
$("T").oninput = e => setT(+e.target.value, true);
$("snap").onclick = () => setT(TC);
$("h").oninput = e => setH(+e.target.value);
$("spf").oninput = () => $("spf-o").textContent = $("spf").value;
$("rad").oninput = () => $("rad-o").textContent = $("rad").value;
wireSeg($("algo"), () => { prevSign = 0; });
wireSeg($("brush"), () => lat.classList.toggle("paint", segValue($("brush"), "b") !== "0"));
$("rand").onclick = () => { sim.randomise(); traceN = 0; };
$("allup").onclick = () => { sim.fill(1); traceN = 0; };
$("quench").onclick = () => { sim.randomise(); traceN = 0; setT(1.5); };
$("pause").onclick = () => { paused = !paused; $("pause").textContent = paused ? "Play" : "Pause"; $("pause").setAttribute("aria-pressed", paused); };
$("size").onchange = () => {
  sim.setSize(+$("size").value); sim.setParams(T, h);
  lat.width = lat.height = sim.L; img = lctx.createImageData(sim.L, sim.L); img32 = new Uint32Array(img.data.buffer);
  traceN = 0; resetBlocks(); resetScatter();
};

// painting
let painting = false;
function paintAt(ev) {
  const b = +segValue($("brush"), "b"); if (!b) return;
  const r = lat.getBoundingClientRect(), x = (ev.clientX - r.left) / r.width * sim.L, y = (ev.clientY - r.top) / r.height * sim.L;
  sim.paint(x, y, +$("rad").value * sim.L / 256, b);
}
lat.addEventListener("pointerdown", e => { if (+segValue($("brush"), "b")) { painting = true; lat.setPointerCapture(e.pointerId); paintAt(e); e.preventDefault(); } });
lat.addEventListener("pointermove", e => { if (painting) paintAt(e); });
["pointerup", "pointercancel"].forEach(t => lat.addEventListener(t, () => painting = false));

let stats = { m: 0, e: 0 }, fps = 60, lastT = 0, frame = 0, simMs = 0;
function stepSim() {
  const t0 = performance.now(), spf = +$("spf").value, wolff = segValue($("algo"), "a") === "wolff";
  if (wolff) {
    // spread the work in chunks and stop early if the frame budget (≈ 12 ms) is spent
    for (let k = 0; k < spf; k++) { sim.wolff(sim.N / 2); if (performance.now() - t0 > 12) break; }
    if (h === 0) {      // global spin flip is an exact symmetry at h = 0: keep the colours steady
      const m = sim.stats().m, sg = Math.sign(m);
      if (Math.abs(m) > 0.3) { if (prevSign && sg === -prevSign) sim.globalFlip(); else prevSign = sg; }
    }
  } else {
    for (let k = 0; k < spf; k++) { sim.metropolis(1); if (performance.now() - t0 > 12) break; }
  }
  simMs += 0.1 * (performance.now() - t0 - simMs);
}
function drawTrace() {
  const P = tracePlot; P.clear();
  const c = P.ctx; c.fillStyle = C.muted; c.font = "11px system-ui, sans-serif"; c.textAlign = "right"; c.textBaseline = "middle";
  [[1, "+1"], [0, "0"], [-1, "−1"]].forEach(([v, s]) => c.fillText(s, P.m[3] - 6, P.py(v)));
  P.line([[0, 0], [trace.length, 0]], C.line, 1);
  if (traceN < 2) return;
  const n = Math.min(traceN, trace.length), pts = [];
  for (let k = 0; k < n; k++) pts.push([trace.length - n + k, trace[(traceN - n + k) % trace.length]]);
  P.line(pts, stats.m >= 0 ? C.up : C.down, 1.5);
  c.fillStyle = C.fg; c.font = "italic 12px Georgia, serif"; c.textAlign = "left"; c.textBaseline = "top";
  c.fillText("m(t)", P.m[3] + 4, P.m[0]);
}
function updateReadouts() {
  $("st-T").textContent = Math.abs(T - TC) < 1e-6 ? "T_c" : T.toFixed(2);
  $("st-m").textContent = fmtS(stats.m);
  $("st-e").textContent = fmtS(stats.e);
  $("st-x").textContent = h === 0 ? mExact(T).toFixed(3) : "h ≠ 0";
  $("sim-hint").textContent = `${sim.L}×${sim.L} lattice · ${Math.round(fps)} fps · simulation ${simMs.toFixed(1)} ms per frame`;
}

function loop(now) {
  requestAnimationFrame(loop);
  const live = visible.has("sim-widget") || visible.has("mT-widget") || visible.has("blk-widget") || visible.has("fft-widget");
  if (lastT) fps += 0.05 * (1000 / Math.max(1, now - lastT) - fps);
  lastT = now;
  if (!live) { lastT = 0; return; }
  frame++;
  if (!paused) stepSim();
  stats = sim.stats();
  if (!paused) { trace[traceN % trace.length] = stats.m; traceN++; }
  if (visible.has("sim-widget")) {
    sim.render(img32); lctx.putImageData(img, 0, 0);
    if (frame % 2 === 0) drawTrace();
    if (frame % 6 === 0) updateReadouts();
  }
  if (visible.has("mT-widget") && frame % 4 === 0) drawMT();
  if (visible.has("blk-widget") && frame % 8 === 0) drawBlocks();
  if (visible.has("fft-widget") && frame % 5 === 0) drawScatter();
}
window.__ising = { get fps() { return fps; }, get simMs() { return simMs; }, sim };

// ================================================================ 2. m(T)
const mTPlot = new Plot($("mT"), { x: [0.5, 5], y: [0, 1.05], aspect: w => w < 600 ? 0.75 : 0.5 });
const Ts = Array.from({ length: 451 }, (_, i) => 0.5 + 4.5 * i / 450);
const curves = {
  mEx: Ts.map(t => [t, mExact(t)]).concat([[TC, 0], [5, 0]]).sort((a, b) => a[0] - b[0]),
  mMF: Ts.map(t => [t, mMF(t)]),
  cEx: Ts.filter(t => Math.abs(t - TC) > 2e-3).map(t => [t, cExact(t)]),
  cMF: Ts.map(t => { const d = 1e-3; if (t >= 4) return [t, 0];
    const e = x => -2 * mMF(x) ** 2; return [t, (e(Math.min(t + d, 4 - 1e-9)) - e(t - d)) / (Math.min(t + d, 4 - 1e-9) - t + d)]; }),
};
// Onsager's C diverges at T_c: split the curve there so the line does not jump across
const cExL = curves.cEx.filter(p => p[0] < TC), cExR = curves.cEx.filter(p => p[0] > TC);
function drawMT() {
  const P = mTPlot, q = segValue($("mT-seg"), "q");
  P.y = q === "m" ? [0, 1.05] : [0, 2.8];
  const narrow = P.W < 600;
  P.clear(); P.axes({ xt: narrow ? 3 : 9, yv: q === "m" ? [0, 0.2, 0.4, 0.6, 0.8, 1] : [0, 0.5, 1, 1.5, 2, 2.5],
    xl: "temperature T", yl: q === "m" ? "|m|" : "C per spin", xfmt: v => v.toFixed(1), yfmt: v => v.toFixed(1) });
  P.vline(TC, C.crit, [4, 4], narrow ? "T_c" : "T_c ≈ 2.269");
  P.vline(4, C.mf, [2, 5], narrow ? "MF" : "mean-field T_c = 4");
  if (q === "m") { P.line(curves.mMF, C.mf, 2); P.line(curves.mEx, C.exact, 2.5); }
  else {
    const mf = curves.cMF; P.line(mf.filter(p => p[0] < 4), C.mf, 2); P.line(mf.filter(p => p[0] >= 4), C.mf, 2);
    P.line(cExL, C.exact, 2.5); P.line(cExR, C.exact, 2.5);
  }
  if (DATA) {
    const key = q === "m" ? "m" : "C";
    P.dots(DATA.sim["32"].points.map(p => [p.T, p[key], p[key + "_err"]]), C.up, 3, true);
    P.dots(DATA.sim["64"].points.map(p => [p.T, p[key], p[key + "_err"]]), C.up, 3);
  }
  if (q === "m" && T >= P.x[0]) {
    const c = P.ctx, X = P.px(T), Y = P.py(Math.abs(stats.m));
    c.fillStyle = C.hot; c.strokeStyle = C.bg; c.lineWidth = 2;
    c.beginPath(); c.arc(X, Y, 6, 0, 2 * Math.PI); c.fill(); c.stroke();
    c.font = "12px system-ui, sans-serif"; c.textAlign = X > P.W - 80 ? "right" : "left"; c.textBaseline = "bottom";
    c.fillText(`live ${sim.L}×${sim.L}`, X + (X > P.W - 80 ? -9 : 9), Y - 4);
  }
}
wireSeg($("mT-seg"), drawMT);
mTPlot.onresize = drawMT;

// ================================================================ 3. free energy
const fePlot = new Plot($("fe"), { x: [-1, 1], y: [-1.9, 2.3], aspect: w => w < 600 ? 0.7 : 0.45 });
function drawFE() {
  const t = +$("feT").value, hh = +$("feh").value, P = fePlot;
  $("feT-o").textContent = t.toFixed(2); $("feh-o").textContent = hh.toFixed(2);
  const f0 = fMF(0, t, 0), ms = Array.from({ length: 801 }, (_, i) => -1 + 2 * i / 800);
  const pts = ms.map(m => [m, fMF(m, t, hh) - f0]);
  P.clear(); P.axes({ xt: 4, yt: 0, xl: "magnetisation m", yl: "f(m) − f(0)" });
  P.line([[-1, 0], [1, 0]], C.line, 1);
  P.fill(pts, t < 4 ? C.crit : C.hot, 0.12, P.y[1]);
  P.line(pts, t < 4 ? C.crit : C.hot, 2.5);
  // local minima
  const mins = [];
  for (let i = 1; i < pts.length - 1; i++) if (pts[i][1] < pts[i - 1][1] && pts[i][1] <= pts[i + 1][1]) mins.push(pts[i]);
  const best = Math.min(...mins.map(p => p[1]));
  mins.forEach(p => P.dots([p], p[0] > 0.005 ? C.up : p[0] < -0.005 ? C.down : C.fg, p[1] === best ? 6 : 4, p[1] !== best));
  const mstar = mMF(t, 0);
  $("fe-read").innerHTML = t >= 4
    ? `T = <b>${t.toFixed(2)}</b> ≥ 4: one bowl, the most likely magnetisation is ${hh ? `<b>${fmtS(mins[0]?.[0] ?? 0, 2)}</b> (pushed by the field)` : "<b>0</b>"}.`
    : hh === 0 ? `T = <b>${t.toFixed(2)}</b> &lt; 4: two valleys at m = <b>±${mstar.toFixed(3)}</b> (the solutions of m = tanh(4m/T)). Which one the lattice picks is up to chance.`
    : `T = <b>${t.toFixed(2)}</b> &lt; 4, the field tilts the landscape: ${mins.length > 1
      ? `valleys at m = ${mins.map(p => `<b>${fmtS(p[0], 2)}</b>`).join(" and ")}; the ${hh > 0 ? "gold" : "blue"} one wins, the other survives as a <em>metastable</em> state.`
      : `a single valley left, at m = <b>${fmtS(mins[0][0], 2)}</b>.`}`;
}
["feT", "feh"].forEach(id => $(id).oninput = drawFE);
fePlot.onresize = drawFE;
drawFE();

// ================================================================ 4. block spins
const bctx = [0, 1, 2, 3].map(k => $("b" + k).getContext("2d"));
let bimg;
const brand = rng(7);
function resetBlocks() {
  const W = sim.L / 8;
  bimg = bctx.map((c, k) => { $("b" + k).width = $("b" + k).height = W; return c.createImageData(W, W); });
  [0, 1, 2, 3].forEach(k => { const n = W << k;
    $("b" + k + "-c").textContent = k === 0 ? `original, ${n}×${n} window` : `${k} step${k > 1 ? "s" : ""}: ${n}×${n} spins → ${W}×${W}`; });
}
function drawBlocks() {
  const W = sim.L / 8;
  let a = sim.s, n = sim.L;
  const lv = [a];
  for (let k = 1; k <= 3; k++) { a = blockSpin(a, n, brand); n >>= 1; lv.push(a); }
  lv.forEach((arr, k) => { const win = crop(arr, sim.L >> k, W); paintSpins(new Uint32Array(bimg[k].data.buffer), win); bctx[k].putImageData(bimg[k], 0, 0); });
  $("blk-T").textContent = `now T = ${Math.abs(T - TC) < 1e-6 ? "T_c" : T.toFixed(2)}, ${segValue($("algo"), "a") === "wolff" ? "Wolff" : "Metropolis"}`;
}
const useWolff = () => $("algo").querySelector('[data-a="wolff"]').click();
$("blk-tc").onclick = () => { setT(TC); useWolff(); };
$("blk-lo").onclick = () => { setT(2.0); useWolff(); };
$("blk-hi").onclick = () => { setT(2.6); useWolff(); };
resetBlocks();

// ================================================================ 5. structure factor
let scat, fimg, simg;
const fctx = $("fft").getContext("2d"), sctx = $("fsp").getContext("2d");
function resetScatter() {
  const n = Math.min(128, sim.L); scat = new Scatter(n);
  $("fft").width = $("fft").height = $("fsp").width = $("fsp").height = n;
  fimg = fctx.createImageData(n, n); simg = sctx.createImageData(n, n);
  $("fsp-c").textContent = `spins: ${n}×${n} window of the live lattice`;
}
function drawScatter() {
  const n = scat.n, win = crop(sim.s, sim.L, n);
  scat.update(win);
  scat.render(new Uint32Array(fimg.data.buffer), MAGMA); fctx.putImageData(fimg, 0, 0);
  paintSpins(new Uint32Array(simg.data.buffer), win); sctx.putImageData(simg, 0, 0);
  $("fft-T").textContent = Math.abs(T - TC) < 1e-6 ? "T_c" : T.toFixed(2);
  $("fft-g").textContent = scat.smallK().toFixed(0);
}
$("cbar").style.background = `linear-gradient(90deg, ${Array.from({ length: 9 }, (_, i) => {
  const v = MAGMA[Math.round(i * 255 / 8)]; return `rgb(${v & 255},${v >> 8 & 255},${v >> 16 & 255})`; }).join(",")})`;
$("fft-tc").onclick = () => { setT(TC); useWolff(); };
$("fft-hi").onclick = () => setT(3.5);
$("fft-lo").onclick = () => setT(1.8);
resetScatter();

// ================================================================ 6. Hopfield
const NH = 64, hop = new Hopfield(NH), hrand = rng(2024);
const hcv = $("hop"), hctx = hcv.getContext("2d"), himg = hctx.createImageData(NH, NH), h32 = new Uint32Array(himg.data.buffer);
let recalling = false;
function glyph(name) {
  const cv = document.createElement("canvas"); cv.width = cv.height = NH;
  const c = cv.getContext("2d"); c.fillStyle = "#fff"; c.strokeStyle = "#fff"; c.lineCap = "round";
  if (name === "smile") {
    c.lineWidth = 5; c.beginPath(); c.arc(32, 32, 25, 0, 2 * Math.PI); c.stroke();
    c.beginPath(); c.arc(23, 25, 4.5, 0, 2 * Math.PI); c.arc(41, 25, 4.5, 0, 2 * Math.PI); c.fill();
    c.beginPath(); c.arc(32, 34, 14, 0.15 * Math.PI, 0.85 * Math.PI); c.stroke();
  } else if (name === "heart") {
    c.beginPath(); c.moveTo(32, 56);
    c.bezierCurveTo(4, 36, 4, 12, 20, 10); c.bezierCurveTo(27, 9, 31, 14, 32, 19);
    c.bezierCurveTo(33, 14, 37, 9, 44, 10); c.bezierCurveTo(60, 12, 60, 36, 32, 56); c.fill();
  } else {
    c.lineWidth = 7; c.beginPath(); c.moveTo(10, 16); c.quadraticCurveTo(14, 11, 22, 12); c.lineTo(54, 12); c.stroke();
    c.beginPath(); c.moveTo(24, 13); c.quadraticCurveTo(24, 40, 14, 54); c.stroke();
    c.beginPath(); c.moveTo(42, 13); c.quadraticCurveTo(39, 44, 46, 53); c.quadraticCurveTo(51, 56, 55, 50); c.stroke();
  }
  const d = c.getImageData(0, 0, NH, NH).data, out = new Int8Array(NH * NH);
  for (let i = 0; i < NH * NH; i++) out[i] = d[4 * i + 3] > 100 ? 1 : -1;
  return out;
}
const GLYPHS = { smile: glyph("smile"), heart: glyph("heart"), pi: glyph("pi") };
const names = [];
function drawHop() { paintSpins(h32, hop.s); hctx.putImageData(himg, 0, 0); drawMems(); }
function drawMems() {
  const q = hop.overlaps(), best = q.length ? q.indexOf(Math.max(...q)) : -1;
  $("mems").innerHTML = hop.pats.map((_, k) => `<figure><canvas class="px" width="${NH}" height="${NH}" data-k="${k}"></canvas>
    <div style="color:${k === best && q[k] > 0.9 ? "var(--cold)" : "var(--muted)"}">${names[k]} · ${fmtS(q[k], 2)}</div>
    <div class="bar"><i style="width:${Math.max(0, q[k]) * 100}%"></i></div>
    <button data-del="${k}" aria-label="forget ${names[k]}">forget</button></figure>`).join("") ||
    `<p class="hint">No memories yet: draw something (or load a preset) and press Store.</p>`;
  $("mems").querySelectorAll("canvas").forEach(cv => { const c = cv.getContext("2d"), im = c.createImageData(NH, NH);
    paintSpins(new Uint32Array(im.data.buffer), hop.pats[+cv.dataset.k]); c.putImageData(im, 0, 0); });
  $("mems").querySelectorAll("button[data-del]").forEach(b => b.onclick = () => {
    const k = +b.dataset.del; hop.pats.splice(k, 1); names.splice(k, 1); hop.rebuild(); refreshHop(); });
}
function refreshHop(msg) {
  $("store").disabled = hop.pats.length >= 5;
  $("recall").disabled = !hop.pats.length;
  if (msg !== undefined) $("hop-read").innerHTML = msg;
  drawHop();
}
function store(s, name) { if (hop.pats.length >= 5) return; hop.pats.push(Int8Array.from(s)); names.push(name); hop.rebuild(); }
function stopRecall() { recalling = false; $("recall").textContent = "Recall"; }
function hopStep() {
  if (!recalling) return;
  if (visible.has("hop-widget")) {
    hop.step(Math.ceil(hop.N / 30), hrand);
    drawHop();
    if (hop.converged()) { stopRecall();
      const q = hop.overlaps(), k = q.indexOf(Math.max(...q));
      refreshHop(q[k] > 0.98 ? `Converged to <b style="color:var(--cold)">${names[k]}</b> (overlap ${q[k].toFixed(2)}).`
        : `Stuck in a valley that is not a stored memory: a <em>spurious state</em> (best overlap ${q[k].toFixed(2)} with ${names[k]}).`); return; }
  }
  requestAnimationFrame(hopStep);
}
// drawing
let hpaint = false;
function hopPaint(e) {
  const r = hcv.getBoundingClientRect(), x = (e.clientX - r.left) / r.width * NH, y = (e.clientY - r.top) / r.height * NH;
  const v = +segValue($("pen"), "p"), R = 2.2;
  for (let i = Math.floor(y - R); i <= y + R; i++) for (let j = Math.floor(x - R); j <= x + R; j++)
    if (i >= 0 && j >= 0 && i < NH && j < NH && (i + 0.5 - y) ** 2 + (j + 0.5 - x) ** 2 <= R * R) hop.s[i * NH + j] = v;
  hop.syncOverlaps(); drawHop();
}
hcv.addEventListener("pointerdown", e => { stopRecall(); hpaint = true; hcv.setPointerCapture(e.pointerId); hopPaint(e); e.preventDefault(); });
hcv.addEventListener("pointermove", e => { if (hpaint) hopPaint(e); });
["pointerup", "pointercancel"].forEach(t => hcv.addEventListener(t, () => hpaint = false));
wireSeg($("pen"), () => {});
wireSeg($("rule"), b => { hop.rule = b.dataset.r; hop.rebuild(); refreshHop(`Rule: ${b.dataset.r === "pinv" ? "pseudo-inverse" : "Hebb"}. Corrupt a memory and recall it.`); });
document.querySelectorAll("[data-g]").forEach(b => b.onclick = () => { stopRecall(); hop.setState(GLYPHS[b.dataset.g]); refreshHop(`Loaded the ${b.dataset.g} preset.`); });
$("hclear").onclick = () => { stopRecall(); hop.setState(new Int8Array(hop.N).fill(-1)); refreshHop(""); };
$("store").onclick = () => { let k = 1; while (names.includes(`#${k}`)) k++;
  const g = Object.keys(GLYPHS).find(n => GLYPHS[n].every((v, i) => v === hop.s[i]) && !names.includes(n));
  store(hop.s, g || `#${k}`); refreshHop(`Stored as <b>${names[names.length - 1]}</b>: ${hop.pats.length} memor${hop.pats.length > 1 ? "ies" : "y"}.`); };
$("corrupt").onclick = () => { stopRecall();
  const idx = Uint32Array.from({ length: hop.N }, (_, i) => i);
  for (let i = hop.N - 1; i > 0; i--) { const j = Math.floor(hrand() * (i + 1)); [idx[i], idx[j]] = [idx[j], idx[i]]; }
  const s = Int8Array.from(hop.s); for (let i = 0; i < Math.round(0.3 * hop.N); i++) s[idx[i]] = -s[idx[i]];
  hop.setState(s); refreshHop("30% of the pixels flipped at random. Press Recall."); };
$("recall").onclick = () => { if (recalling) { stopRecall(); return; }
  recalling = true; hop.quiet = 0; $("recall").textContent = "Stop"; $("hop-read").textContent = "Each pixel, in random order, aligns with its local field…"; requestAnimationFrame(hopStep); };
$("forget").onclick = () => { stopRecall(); hop.pats = []; names.length = 0; hop.rebuild(); refreshHop("All memories erased."); };
// start: three presets stored, a corrupted smile on the canvas
Object.entries(GLYPHS).forEach(([n, g]) => store(g, n));
hop.setState(GLYPHS.smile); $("corrupt").click();

// ================================================================ boot
setT(TC); setH(0); placeTick();
$("spf-o").textContent = $("spf").value; $("rad-o").textContent = $("rad").value;
// start near equilibrium at T_c with a few Wolff sweeps so the first picture already shows critical clusters
for (let k = 0; k < 30; k++) sim.wolff(sim.N);
sim.render(img32); lctx.putImageData(img, 0, 0); stats = sim.stats(); updateReadouts(); drawTrace(); drawBlocks(); drawScatter();
requestAnimationFrame(loop);
fetch("../data/ep1.json").then(r => r.json()).then(F => {
  DATA = F; drawMT();
  if (F.chapters) F.chapters.forEach((ch, i) => {
    const li = $("chapters").children[i]; if (!li || typeof ch.t !== "number") return;
    const a = document.createElement("a"); a.href = "#"; a.textContent = ch.title;
    a.onclick = e => { e.preventDefault(); const v = document.querySelector("video"); v.currentTime = ch.t; v.play(); v.scrollIntoView({ behavior: "smooth" }); };
    const m = Math.floor(ch.t / 60), s = String(Math.floor(ch.t % 60)).padStart(2, "0");
    li.textContent = ""; li.append(`${m}:${s} `, a);
  });
}).catch(() => {});
drawMT();
