"""s08 · Legacy: Hopfield networks (Nobel 2024), other uses, recap table, outro."""
from _common import Narrated, load, lattice_image, np, LEFT, RIGHT, UP, DOWN
from common.style import FG, MUTED, CRITICAL, MEANFIELD, HOT, COLD, EXACT, UP_SPIN, GRID
from manim import (Group, VGroup, MathTex, Tex, FadeIn, FadeOut, Write, Create, LaggedStart, FadeTransform,
                   Rectangle, Table, UpdateFromAlphaFunc, linear, SurroundingRectangle)
from _common import _LUT


class Legacy(Narrated):
    def construct(self):
        self.chapter("8 · Legacy")
        hp = load("hopfield")
        pats = Group(*[lattice_image(p, height=1.6) for p in hp["patterns"]]).arrange(RIGHT, buff=0.35).to_edge(UP, buff=1.0)
        self.say("A century later, the Ising model is everywhere. Its most famous descendant is a model of memory.")
        eq = MathTex(r"H=-\sum_{i,j} W_{ij}\,s_i s_j", font_size=46, color=EXACT).next_to(pats, DOWN, buff=0.4)
        self.say("In 1982, John Hopfield noticed that a network of neurons, each one firing or silent, "
                 "is an Ising model, where the couplings are learned instead of fixed.", Write(eq),
                 speech="In 1982, John Hopfield noticed that a network of neurons, each one firing or silent, "
                        "is an Ising model, where the couplings between spins are learned instead of fixed.")
        self.say("Choose the couplings so that some pictures are low-energy configurations. Here, five symbols "
                 "are stored in a network of four thousand spins.", LaggedStart(*[FadeIn(p) for p in pats], lag_ratio=0.15))

        def recall(name, label, txt):
            frames = hp[name]
            img = lattice_image(frames[0], height=4.0).shift(1.5 * DOWN)
            cap = Tex(label, font_size=30, color=MUTED).next_to(img, RIGHT, buff=0.5)
            self.say(txt[0], FadeIn(img), FadeIn(cap))
            d = self.voice(txt[1])
            self.play(UpdateFromAlphaFunc(img, lambda m, a: setattr(
                m, "pixel_array", np.ascontiguousarray(
                    _LUT[(frames[int(round(a * (len(frames) - 1)))] > 0).astype(np.uint8)]))),
                run_time=d + 0.3, rate_func=linear)
            return img, cap

        img, cap = recall("pi", r"35\,\% of spins flipped",
                          ("Now give it a corrupted picture: a third of the spins flipped at random.",
                           "Let the dynamics run downhill in energy, and it falls back into the nearest memory."))
        best = int(np.argmax(hp["pi_overlap"][-1]))
        box = SurroundingRectangle(pats[best], color=COLD, buff=0.08, stroke_width=5)
        self.say("Recall, by physics.", Create(box))
        self.play(FadeOut(Group(img, cap, box)), run_time=0.6)
        img, cap = recall("psi", r"45\,\% of spins flipped",
                          ("Corrupt it too much, though,", "and it gets stuck in a false memory: a blend of several patterns."))
        self.say("Like ours, its memory has limits.")
        self.play(FadeOut(Group(img, cap, pats, eq)), run_time=0.8)

        nobel = Tex(r"Nobel Prize in Physics 2024\\John Hopfield \& Geoffrey Hinton", font_size=46, color=EXACT)
        sub = Tex(r"``for foundational discoveries and inventions that enable machine learning\\with artificial neural networks''",
                  font_size=28, color=MUTED).next_to(nobel, DOWN, buff=0.4)
        self.say("In 2024, Hopfield and Geoffrey Hinton, who turned the idea into Boltzmann machines, received "
                 "the Nobel prize in physics, for foundations of machine learning.", FadeIn(nobel), FadeIn(sub))
        uses = VGroup(*[Tex(t, font_size=34, color=FG) for t in
                        (r"opinions and voting models", r"cleaning noisy images", r"hard optimisation problems",
                         r"proteins, ecosystems, financial markets\ldots")]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        uses.shift(0.2 * DOWN)
        self.say("And the same equation shows up in models of opinions, in image processing, in hard optimisation "
                 "problems, and in many more places.", FadeOut(Group(nobel, sub)), LaggedStart(*[FadeIn(u) for u in uses], lag_ratio=0.3))
        self.play(FadeOut(uses), run_time=0.6)

        # recap
        rows = [["1925", "Ising", "1D: no transition"],
                ["1936", "Peierls", "2D: order survives (walls cost their length)"],
                ["1907", "Weiss", "mean field: right picture, wrong numbers"],
                ["1944", "Onsager", r"exact $T_c=2/\ln(1+\sqrt2)\approx 2.269$"],
                ["1952", "Yang", r"$m\propto(T_c-T)^{1/8}$"],
                ["1966--71", "Kadanoff, Wilson", "no scale at $T_c$: renormalisation"],
                ["", "universality", "same exponents for magnets and fluids"],
                ["1982", "Hopfield", "memories as energy minima"]]
        tab = Table(rows, element_to_mobject=lambda t: Tex(t, font_size=30, color=FG), include_outer_lines=False,
                    line_config=dict(color=GRID, stroke_width=1.5), h_buff=0.5, v_buff=0.22)
        tab.scale_to_fit_width(12.6).shift(0.1 * DOWN)
        for r in tab.get_rows():
            r[0].set_color(EXACT)
            r[1].set_color(MUTED)
        self.say("Let's recap a century of results.", FadeIn(tab.get_horizontal_lines()), FadeIn(tab.get_vertical_lines()))
        lines = ["In one dimension, walls are cheap: no order.",
                 "In two dimensions, walls cost their length: order survives.",
                 "Mean field gets the picture, but not the numbers.",
                 "Onsager gets the exact numbers.",
                 "Including the exponent one eighth.",
                 "At T c, there is no scale, and zooming out changes nothing.",
                 "Which is why magnets and fluids share the same exponents.",
                 "And the same mathematics describes memories."]
        for r, line in zip(tab.get_rows(), lines):
            self.say(line, FadeIn(r, shift=0.1 * RIGHT), run_time=0.8, pause=0.15)
        self.play(FadeOut(tab), run_time=0.8)

        end = Tex(r"magnets that only talk to their neighbours", font_size=46, color=FG)
        site = Tex(r"interactive simulations: \texttt{romainmorleghem.github.io/ising}", font_size=32, color=MUTED)
        VGroup(end, site).arrange(DOWN, buff=0.6)
        self.say("Arrows that only talk to their neighbours, and yet: order, a sharp transition, a world without "
                 "scale, and laws shared by magnets and boiling fluids. All from one rule.", FadeIn(end))
        self.say("You can play with every simulation of this video on the companion website. Thanks for watching.",
                 FadeIn(site))
        self.play(FadeOut(VGroup(end, site)), FadeOut(self.chapter_tag), run_time=1.2)
