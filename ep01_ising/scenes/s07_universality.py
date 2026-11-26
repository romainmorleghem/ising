"""s07 · Universality: lattice gas = liquid-gas, critical opalescence (structure factor), shared exponents."""
from _common import Narrated, load, lattice_image, rgb_image, unpack, TC, np, LEFT, RIGHT, UP, DOWN
from common.style import FG, MUTED, CRITICAL, MEANFIELD, HOT, COLD, EXACT, UP_SPIN, DOWN_SPIN, GRID
from manim import (Group, VGroup, MathTex, Tex, FadeIn, FadeOut, Write, Create, LaggedStart, FadeTransform,
                   Table, DecimalNumber, Line, Rectangle)
from matplotlib import colormaps


def glow(S, vmin, vmax):
    x = np.clip((np.log10(S + 1e-3) - vmin) / (vmax - vmin), 0, 1)
    return (colormaps["magma"](x)[..., :3] * 255).astype(np.uint8)


class Universality(Narrated):
    def construct(self):
        self.chapter("7 · Universality")
        snaps = load("snapshots")
        k = int(np.argmin(np.abs(snaps["T"] - TC)))
        s = unpack(snaps["frames"][k])[:160, :160]
        mag = lattice_image(s, height=5.4).shift(3.2 * LEFT + 0.2 * DOWN)
        gas = np.where(s[..., None] > 0, np.array([235, 235, 235]), np.array([14, 17, 22])).astype(np.uint8)
        gasi = rgb_image(gas, height=5.4).shift(3.2 * RIGHT + 0.2 * DOWN)
        lm = VGroup(Tex(r"magnet: up / down", font_size=32, color=FG)).next_to(mag, UP, buff=0.25)
        lg = Tex(r"fluid: molecule / empty", font_size=32, color=FG).next_to(gasi, UP, buff=0.25)
        self.say("Now for the biggest surprise. Rename things: an up spin is a molecule, a down spin is empty space.",
                 FadeIn(mag), FadeIn(lm))
        self.say("Neighbouring molecules attract, exactly like aligned spins. The Ising model becomes a fluid, "
                 "and the transition becomes the line between liquid and vapour.", FadeIn(gasi), FadeIn(lg))
        co2 = Tex(r"CO$_2$ critical point: $31\,^\circ$C, $73$ atm", font_size=40, color=EXACT).to_edge(DOWN, buff=0.4)
        self.say("Real fluids have a critical point too. For carbon dioxide, it's thirty-one degrees Celsius, "
                 "and seventy-three atmospheres. And near it, something spectacular happens.", FadeIn(co2))
        self.say("The clear fluid turns milky, and scatters light in every direction. "
                 "It's called critical opalescence.")
        self.play(FadeOut(Group(mag, gasi, lm, lg, co2)), run_time=0.8)

        # structure factor
        op = load("opal")
        Ts, S = op["T"], op["S"]
        vmax = np.log10(S.max())
        vmin = -0.5
        thumb = lattice_image(op["thumbs"][0], height=4.2).shift(3.4 * LEFT + 0.1 * DOWN)
        sk = rgb_image(glow(S[0], vmin, vmax), height=4.2, smooth=True).shift(2.6 * RIGHT + 0.1 * DOWN)
        lt = Tex(r"the fluid", font_size=32, color=FG).next_to(thumb, UP, buff=0.25)
        ls = Tex(r"what light sees: $|\text{Fourier transform}|^2$", font_size=32, color=FG).next_to(sk, UP, buff=0.25)
        cen = Tex(r"centre = long wavelengths", font_size=26, color=MUTED).next_to(sk, DOWN, buff=0.2)
        tl = VGroup(MathTex("T=", font_size=40, color=FG), DecimalNumber(Ts[0], num_decimal_places=2, font_size=40,
                                                                          color=FG)).arrange(RIGHT, buff=0.1)
        tl.next_to(thumb, DOWN, buff=0.3)
        self.say("Why? Light is scattered by density fluctuations. Mathematically, what light sees is the "
                 "Fourier transform of the fluid: how much structure there is at each wavelength.",
                 FadeIn(thumb), FadeIn(sk), FadeIn(lt), FadeIn(ls), FadeIn(cen), FadeIn(tl))
        d = self.voice("Now approach the critical point. Fluctuations of every size appear, and the scattering "
                       "at long wavelengths, in the centre, lights up.")
        step = (d + 0.3) / (len(Ts) - 1)
        for i in range(1, len(Ts)):
            th2 = lattice_image(op["thumbs"][i], height=4.2).move_to(thumb)
            sk2 = rgb_image(glow(S[i], vmin, vmax), height=4.2, smooth=True).move_to(sk)
            self.play(FadeTransform(thumb, th2), FadeTransform(sk, sk2), tl[1].animate.set_value(Ts[i]), run_time=step)
            thumb, sk = th2, sk2
        self.say("That glow is the milkiness of the fluid. Same physics as our magnet.")
        self.play(FadeOut(Group(thumb, sk, lt, ls, cen, tl)), run_time=0.8)

        # universality table
        rows = [["Ising model, 3D", "0.326"], ["liquid-gas (CO$_2$, xenon)", "0.33"],
                ["binary mixtures", "0.33"], ["uniaxial magnets", "0.33"],
                ["mean field", "0.5"], ["Ising model, 2D", "1/8"]]
        tab = Table([[r, v] for r, v in rows], col_labels=[Tex("system", color=MUTED), MathTex(r"\beta", color=MUTED)],
                    element_to_mobject=lambda t: Tex(t, font_size=34, color=FG),
                    include_outer_lines=False, line_config=dict(color=GRID, stroke_width=2),
                    h_buff=0.8, v_buff=0.28).scale(0.85).shift(0.1 * DOWN)
        for i in range(2, 6):
            tab.get_rows()[i - 1].set_color(EXACT)
        tab.get_rows()[5].set_color(MEANFIELD)
        tab.get_rows()[6].set_color(MUTED)
        self.say("And here is the deepest part. Measure how the order vanishes near the critical point, "
                 "the exponent beta, our one eighth in two dimensions.", FadeIn(tab.get_rows()[0]), FadeIn(tab.get_horizontal_lines()))
        self.say("In three dimensions, the Ising model gives zero point three two six. Carbon dioxide, xenon, "
                 "mixtures of liquids, certain magnets: all the same number.",
                 LaggedStart(*[FadeIn(tab.get_rows()[i]) for i in range(1, 5)], lag_ratio=0.3),
                 FadeIn(tab.get_vertical_lines()))
        self.say("Near a critical point, the details don't matter. Only the dimension and the symmetry do. "
                 "This is universality, and the renormalisation group explains it.",
                 FadeIn(tab.get_rows()[5]), FadeIn(tab.get_rows()[6]))
        self.say("Oddly, the three-dimensional Ising model has never been solved exactly. A century later, "
                 "its exponents are known only numerically. It is still an open problem.")
        self.play(FadeOut(tab), FadeOut(self.chapter_tag), run_time=0.8)
