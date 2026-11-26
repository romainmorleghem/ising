"""Fact sheet for the companion website: python web_data.py -> web/data/ep1.json (≈ 1 min, numba).

Swendsen-Wang simulations of the 2D Ising model (J = k_B = 1, periodic L x L, h = 0) for L = 32 and 64:
mean |m|, specific heat C, susceptibility chi and Binder cumulant U on 26 temperatures in [1.5, 3.5]
(denser near T_c), with error bars from 20 blocks. Plus the exact numbers quoted on the page.
"""
import json
import time
from pathlib import Path

import numba as nb
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "web" / "data" / "ep1.json"
TC = 2 / np.log(1 + np.sqrt(2))


@nb.njit(cache=True)
def find(p, i):
    while p[i] != i:
        p[i] = p[p[i]]
        i = p[i]
    return i


@nb.njit(cache=True)
def sw_run(L, T, n_therm, n_meas, seed):
    """Swendsen-Wang from a random start. Returns per-sweep total magnetisation M and energy E."""
    np.random.seed(seed)
    N = L * L
    s = np.empty((L, L), np.int8)
    for i in range(L):
        for j in range(L):
            s[i, j] = 1 if np.random.random() < 0.5 else -1
    pb = 1.0 - np.exp(-2.0 / T)
    p = np.empty(N, np.int64)
    flip = np.empty(N, np.bool_)
    Ms = np.empty(n_meas)
    Es = np.empty(n_meas)
    for t in range(n_therm + n_meas):
        for a in range(N):
            p[a] = a
        for i in range(L):
            for j in range(L):
                a = i * L + j
                j2 = (j + 1) % L
                i2 = (i + 1) % L
                if s[i, j] == s[i, j2] and np.random.random() < pb:
                    ra = find(p, a)
                    rb = find(p, i * L + j2)
                    if ra != rb:
                        p[ra] = rb
                if s[i, j] == s[i2, j] and np.random.random() < pb:
                    ra = find(p, a)
                    rb = find(p, i2 * L + j)
                    if ra != rb:
                        p[ra] = rb
        for a in range(N):
            flip[a] = np.random.random() < 0.5
        for a in range(N):
            if flip[find(p, a)]:
                s[a // L, a % L] = -s[a // L, a % L]
        if t >= n_therm:
            M = 0.0
            E = 0.0
            for i in range(L):
                for j in range(L):
                    M += s[i, j]
                    E -= s[i, j] * (s[i, (j + 1) % L] + s[(i + 1) % L, j])
            Ms[t - n_therm] = M
            Es[t - n_therm] = E
    return Ms, Es


@nb.njit(parallel=True, cache=True)
def sweep_temps(L, temps, n_therm, n_meas, seed):
    nT = temps.shape[0]
    Ms = np.empty((nT, n_meas))
    Es = np.empty((nT, n_meas))
    for k in nb.prange(nT):
        m, e = sw_run(L, temps[k], n_therm, n_meas, seed + 1000 * k + L)
        Ms[k] = m
        Es[k] = e
    return Ms, Es


def blocked(f, *series, nb_=20):
    """Estimate f(series) and its error from nb_ consecutive blocks."""
    n = len(series[0]) // nb_
    vals = np.array([f(*(x[b * n:(b + 1) * n] for x in series)) for b in range(nb_)])
    return float(f(*series)), float(vals.std(ddof=1) / np.sqrt(nb_))


def observables(L, T, M, E):
    N = L * L
    m = np.abs(M) / N
    out = {}
    out["m"], out["m_err"] = blocked(np.mean, m)
    out["C"], out["C_err"] = blocked(lambda e: e.var() / (N * T * T), E)
    out["chi"], out["chi_err"] = blocked(lambda a: N * (np.mean(a * a) - np.mean(a) ** 2) / T, m)
    out["U"], out["U_err"] = blocked(lambda a: 1 - np.mean(a ** 4) / (3 * np.mean(a * a) ** 2), m)
    out["e"], out["e_err"] = blocked(lambda e: e.mean() / N, E)
    return {k: round(v, 5) for k, v in out.items()}


def onsager_m(T):
    return (1 - np.sinh(2 / T) ** -4) ** 0.125 if T < TC else 0.0


def main():
    temps = np.unique(np.round(np.concatenate([
        np.linspace(1.5, 2.0, 4), np.linspace(2.1, 2.5, 13), np.linspace(2.6, 3.5, 8), [TC]]), 4))
    sims = {}
    t0 = time.time()
    for L, n_meas in [(32, 40000), (64, 20000)]:
        Ms, Es = sweep_temps(L, temps, 1000, n_meas, 12345)
        sims[str(L)] = {"sweeps": n_meas, "points": [
            {"T": float(T), **observables(L, T, Ms[k], Es[k])} for k, T in enumerate(temps)]}
        print(f"L = {L}: {time.time() - t0:.1f} s")

    facts = {
        "units": "J = k_B = 1, square lattice, periodic boundaries, h = 0",
        "Tc": TC, "Tc_mean_field": 4.0, "Tc_peierls_bound": 2 / np.log(3),
        "sinh_2_over_Tc": float(np.sinh(2 / TC)),
        "beta": {"2D": "1/8", "3D": 0.3265, "mean_field": "1/2"},
        "nu": {"2D": 1, "3D": 0.6300, "mean_field": "1/2"},
        "sle_kappa": 3, "interface_dimension": 11 / 8,
        "onsager_m": {f"{T:.2f}": onsager_m(T) for T in [1.0, 1.5, 2.0, 2.2, 2.25]},
        "algorithm": "Swendsen-Wang, 1000 thermalisation sweeps, errors from 20 blocks",
        "temperatures": [float(T) for T in temps],
        "sim": sims,
        # Video chapters: set "t" (seconds) once the final cut is known, and the page turns them into links.
        "chapters": [
            {"t": None, "title": "Cold open: melting and freezing"},
            {"t": None, "title": "The model: spins, energy, temperature"},
            {"t": None, "title": "1D: Ising gets it wrong (1925)"},
            {"t": None, "title": "2D: Peierls fixes it (1936)"},
            {"t": None, "title": "Mean field: the bowl splits"},
            {"t": None, "title": "Onsager (1944) and Yang (1952)"},
            {"t": None, "title": "At the critical point: no typical size"},
            {"t": None, "title": "Universality and critical opalescence"},
            {"t": None, "title": "Legacy: Hopfield's memories, recap"},
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(facts, indent=1))
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} kB) in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
