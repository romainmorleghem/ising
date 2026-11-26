# Ising

A video (YouTube, English voice-over) and an interactive companion website on **the Ising model**:
how magnets that only talk to their neighbours decide, all together, to point the same way, and
what happens at the precise temperature where they hesitate. No background needed.

Same format as [Routes to Chaos](https://github.com/romainmorleghem/routes-to-chaos) and
[Rare Events](https://github.com/romainmorleghem/rare-events): Manim Community scenes, LaTeX maths,
a static website, everything computed from scratch in this repository.

| Ep | Title | Status |
|----|-------|--------|
| 1 | The Ising model: the key results | storyboard (`ep01_ising/storyboard.md`) |

## Repository layout
```
common/                  shared style (palette, LaTeX) and voice-over narration (narrative.py)
ep01_ising/compute/      simulations (numba, Swendsen-Wang); test_images.py -> media/tests/
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
python compute/test_images.py 1 3 4 7 9 12   # simulation test images -> media/tests/ (≈ 6 min)
python render.py                             # 480p preview  -> media/ep01/ep01_480p15.mp4
python render.py -q f                        # 1080p30 final -> media/ep01/ep01_1080p30.mp4
python render.py --only s03                  # re-render one sequence and re-assemble
cd scenes && manim -ql s99_voice_check.py VoiceCheck   # 15 s check of the voice pipeline
```
Videos published on the site must stay under ~95 MB (GitHub's 100 MB file limit).

## Website
Static, no build step (`web/`, to come). GitHub Pages: `.github/workflows/pages.yml` deploys `web/` on every
push to `main` (enable it once in the repository settings: Pages → Source: GitHub Actions).
