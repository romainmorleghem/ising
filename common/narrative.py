"""Voice-over narration (Kokoro TTS, voice `af_heart`), no captions on screen.

Every scene of an episode inherits from `Narrated`. Two ways to speak:

    self.say("Each spin wants to agree with its neighbours.", FadeIn(grid))
        # speak, play the animations meanwhile, wait until the sentence is over

    d = self.voice("Now watch what happens as we cool it down.")
    self.play(anneal, run_time=d)          # choreograph freely with the duration d (seconds)

`speech=` overrides what is *said* when it differs from what is written (maths, pronunciation):
    self.say(r"$H=-J\\sum s_i s_j$", speech="H equals minus J times the sum of s i s j.")

Audio is synthesised once and cached in media/voice/<hash>.wav, so re-renders are free.
Model files: ~/.cache/kokoro/{kokoro-v1.0.onnx,voices-v1.0.bin} (see README).
"""
import hashlib
import os
import re
from pathlib import Path

from manim import Scene, MovingCameraScene, Tex, FadeIn, FadeTransform, UL
from common.style import MUTED

VOICE = "af_heart"
SPEED = 1.0                  # Kokoro speed factor (1.0 = natural pace)
PAUSE = 0.35                 # silence after each sentence, seconds
MODEL_DIR = Path(os.environ.get("KOKORO_DIR", Path.home() / ".cache" / "kokoro"))
CACHE = Path(__file__).resolve().parents[1] / "media" / "voice"

# Respellings applied before synthesis (the TTS reads English spelling).
PRONOUNCE = {
    r"\bIsing\b": "Eezing",          # Ernst Ising was German: "EE-zing"
    r"\bT_c\b": "T c",
    r"\bOnsager\b": "Onsahger",
}

_kokoro = None


def _engine():
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(str(MODEL_DIR / "kokoro-v1.0.onnx"), str(MODEL_DIR / "voices-v1.0.bin"))
    return _kokoro


def spoken(text):
    """Text as it will be read aloud: maths stripped, respellings applied."""
    t = re.sub(r"\$[^$]*\$", " ", text)
    for pat, rep in PRONOUNCE.items():
        t = re.sub(pat, rep, t)
    return re.sub(r"\s+", " ", t).strip()


def synth(text):
    """Return (wav path, duration in s) for `text`, synthesising it only if not cached."""
    import soundfile as sf
    words = spoken(text)
    key = hashlib.sha1(f"{VOICE}|{SPEED}|{words}".encode()).hexdigest()[:16]
    path = CACHE / f"{key}.wav"
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        samples, sr = _engine().create(words, voice=VOICE, speed=SPEED, lang="en-us")
        sf.write(path, samples, sr)
    info = sf.info(path)
    return path, info.frames / info.samplerate


class NarrationMixin:
    chapter_tag = None

    def voice(self, text, speech=None):
        """Start speaking now (does not wait). Returns the duration of the sentence."""
        path, dur = synth(speech or text)
        self.add_sound(str(path))
        return dur

    def say(self, text, *anims, speech=None, run_time=None, pause=PAUSE):
        """Speak, play `anims` meanwhile (default: over the whole sentence), then wait it out."""
        dur = self.voice(text, speech)
        left = dur + pause
        if anims:
            rt = dur if run_time is None else run_time
            self.play(*anims, run_time=max(rt, 0.1))
            left -= rt
        if left > 0.05:
            self.wait(left)

    def chapter(self, label, animate=True):
        tag = Tex(label, font_size=26, color=MUTED).to_corner(UL, buff=0.35)
        if self.chapter_tag is None:
            if animate:
                self.play(FadeIn(tag), run_time=0.6)
            else:
                self.add(tag)
        else:
            self.play(FadeTransform(self.chapter_tag, tag), run_time=0.6)
        self.chapter_tag = tag


class Narrated(NarrationMixin, Scene):
    pass


class NarratedCamera(NarrationMixin, MovingCameraScene):
    pass
