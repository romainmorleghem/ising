# Ising

A video (YouTube, English voice-over) and an interactive companion website on **the Ising model**:
how magnets that only talk to their neighbours decide, all together, to point the same way, and
what happens at the precise temperature where they hesitate. No background needed.

Same format as [Routes to Chaos](https://github.com/romainmorleghem/routes-to-chaos) and
[Rare Events](https://github.com/romainmorleghem/rare-events): Manim Community scenes, LaTeX maths,
a static website, everything computed from scratch in this repository.

Website: <https://romainmorleghem.github.io/ising/> (the video + interactive widgets).

| Ep | Title | Length | Video | Web page |
|----|-------|--------|-------|----------|
| 1 | The Ising model: the key results | ≈ 15 min | `web/ep1/ep01_1080p.mp4` | [ep1](https://romainmorleghem.github.io/ising/ep1/) |

## Episode 1 in a nutshell
| Seq | Result | How it is shown |
|-----|--------|-----------------|
| s00 | Cold open: a lattice melts, then freezes through $T_c\approx2.27$ | Metropolis movie, 512² |
| s01 | The model: energy = length of the borders; Boltzmann; energy vs entropy; Metropolis | 8×8 arrow grid |
| s02 | 1D (Ising 1925): a wall costs $2J$ but can sit anywhere, so no order | space-time diagrams of a chain |
| s03 | 2D (Peierls 1936): a wall costs its length, ≤ 3^ℓ walls, order below 2/ln 3 | island + contour counting |
| s04 | Mean field (Weiss): $m=\tanh(4m/T)$, the bowl $-2m^2+T\,I(m)$ splits in two; $T_c^{MF}=4$ | graphical solution, measured $-\ln P(m)/N$ |
| s05 | Onsager 1944, Yang 1952: $T_c=2/\ln(1+\sqrt2)$, $m\propto(T_c-T)^{1/8}$, log-divergent $C$ | simulations vs exact vs mean field |
| s06 | No typical size at $T_c$: block spins (Kadanoff), fixed point (Wilson), power-law clusters | 2048² block-spin flow, FK clusters |
| s07 | Universality: lattice gas = fluid, critical opalescence, shared exponent β ≈ 0.326 in 3D | structure factor vs $T$ |
| s08 | Legacy: Hopfield memories (Nobel 2024), recap | recall and a false memory |

Every number comes from `ep01_ising/compute/` (`movies.py`, `data.py`, `web_data.py`).

## Repository layout
```
common/                  shared style (palette, LaTeX) and voice-over narration (narrative.py)
ep01_ising/compute/      simulations (numba): movies.py, data.py -> media/data/; web_data.py -> web/data/ep1.json
ep01_ising/scenes/       Manim Community scenes, one file per sequence (sNN_*.py)
ep01_ising/render.py     renders all sequences and concatenates them
ep01_ising/storyboard.md plan of the episode
media/                   render outputs and voice cache (not published)
```

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # Manim needs LaTeX + pango/cairo system libraries
mkdir -p ~/.cache/kokoro && cd ~/.cache/kokoro
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  curl -sSfLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f; done
```
The voice is [Kokoro-82M](https://github.com/thewh1teagle/kokoro-onnx) (Apache-2.0), run locally on the CPU
(≈ 3× faster than real time). Voice, speed and pronunciation fixes (`PRONOUNCE`) live in
`common/narrative.py`; each sentence is synthesised once and cached in `media/voice/`.

## Render
```bash
cd ep01_ising
python compute/movies.py && python compute/data.py   # simulation data -> media/data/ (≈ 12 min)
python compute/web_data.py                   # website data -> web/data/ep1.json (≈ 2 min)
python render.py                             # 480p preview  -> media/ep01/ep01_480p15.mp4
python render.py -q f                        # 1080p30 final -> media/ep01/ep01_1080p30.mp4
python render.py --only s03                  # re-render one sequence and re-assemble
cd scenes && manim -ql s99_voice_check.py VoiceCheck   # 15 s check of the voice pipeline
```
Videos published on the site must stay under ~95 MB (GitHub's 100 MB file limit).

## Website
Static, no build step: `cd web && python -m http.server 8000`. GitHub Pages: `.github/workflows/pages.yml` deploys `web/` on every
push to `main` (enable it once in the repository settings: Pages → Source: GitHub Actions).
