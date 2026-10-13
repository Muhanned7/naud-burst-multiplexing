"""Behavioural checks for the soma-only model. Run with:  pytest -q"""

import sys
from pathlib import Path

import numpy as np
from brian2 import ms, pA

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from soma import simulate_soma, step, plateau, isis, rheobase_pA  # noqa: E402


def test_rheobase_value():
    # (V_T - E_L) * C_s / tau_s = 20 mV * 370 pF / 16 ms
    assert abs(rheobase_pA() - 462.5) < 1e-6


def test_silent_below_rheobase_fires_above():
    below = simulate_soma(step(rheobase_pA() - 20, 0 * ms, 500 * ms, 500 * ms))
    above = simulate_soma(step(rheobase_pA() + 100, 0 * ms, 500 * ms, 500 * ms))
    assert len(below["spikes"]) == 0
    assert len(above["spikes"]) > 0


def test_adaptation_lengthens_intervals():
    r = simulate_soma(step(1000, 0 * ms, 500 * ms, 500 * ms))
    d = isis(r["spikes"])
    assert d[-1] > d[0] * 1.5


def test_no_adaptation_means_regular_firing():
    r = simulate_soma(step(1000, 0 * ms, 500 * ms, 500 * ms), params={"b_w_s": 0 * pA})
    d = isis(r["spikes"])
    assert np.ptp(d) < 0.5  # all intervals equal within 0.5 ms


def test_fake_plateau_produces_burst_intervals():
    duration = 300 * ms
    I = step(500, 0 * ms, 300 * ms, duration) + plateau(1300, 150 * ms, 25 * ms, duration)
    sp = simulate_soma(I)["spikes"]
    during = sp[(sp >= 150) & (sp < 175)]
    assert len(during) >= 2
    assert np.all(np.diff(during) < 16)  # paper's burst criterion
