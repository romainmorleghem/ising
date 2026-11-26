"""Shared visual identity for *Ising* (same dark look as Routes to Chaos and Rare Events)."""
from manim import config, TexTemplate, ManimColor

BG = ManimColor("#0E1116")
FG = ManimColor("#E6E6E6")
MUTED = ManimColor("#7A8291")
GRID = ManimColor("#262D38")

UP_SPIN = ManimColor("#F2B544")    # spin up   (= heads in Rare Events)
DOWN_SPIN = ManimColor("#3F7FC8")  # spin down (= tails in Rare Events)
CRITICAL = ManimColor("#C792EA")   # anything at T_c
MEANFIELD = ManimColor("#E85D75")  # Weiss mean-field theory
EXACT = ManimColor("#FFF4D6")      # Onsager / Yang exact results
HOT = ManimColor("#FF8A4C")
COLD = ManimColor("#6CCB8B")

TEX = TexTemplate()
TEX.add_to_preamble(r"\usepackage{amsmath,amssymb}")


def setup():
    config.background_color = BG
    config.tex_template = TEX
