"""Somatic compartment on its own: leaky integrate-and-fire + spike-triggered adaptation.

This is step 1 of building the two-compartment neuron (docs/model.md §1).
The dendrite is not simulated here. Its effect on the soma, g_s * f(u_d),
is just a current, so you can fake it with `plateau()` to preview a burst.

    du_s/dt = -(u_s - E_L)/tau_s + (I_inj + I_noise + w_s)/C_s
    dw_s/dt = -w_s/tau_w_s
    spike when u_s > V_T  ->  u_s = E_L, w_s += b_w_s, refractory t_ref

Parameter values: docs/model.md §4 (Naud & Sprekeler 2018, via Vercruysse et al. 2021 code).
"""

import numpy as np
import brian2 as b2
from brian2 import ms, mV, pA, pF

# Pure-Python code generation: slower than Cython, but needs no C++ compiler (works out of the box on Windows).
b2.prefs.codegen.target = "numpy"

SOMA_PARAMS = {
    "tau_s": 16.0 * ms,     # membrane time constant
    "C_s": 370.0 * pF,      # capacitance
    "E_L": -70.0 * mV,      # resting / reset potential
    "V_T": -50.0 * mV,      # spike threshold
    "t_ref": 3.0 * ms,      # absolute refractory period
    "b_w_s": -200.0 * pA,   # adaptation jump per spike (negative = hyperpolarising brake)
    "tau_w_s": 100.0 * ms,  # adaptation decay time constant
}

DT = 0.1 * ms


# ---------------------------------------------------------------- input helpers
# All helpers return a plain numpy array of current in pA, one value per time step.

def n_steps(duration, dt=DT):
    return int(round(duration / dt))


def step(amplitude_pA, start, stop, duration, dt=DT):
    """Constant current of `amplitude_pA` between `start` and `stop`, zero elsewhere."""
    t = np.arange(n_steps(duration, dt)) * float(dt / ms)
    return np.where((t >= float(start / ms)) & (t < float(stop / ms)), amplitude_pA, 0.0)


def plateau(amplitude_pA, start, width, duration, dt=DT):
    """A rectangular current pulse standing in for the dendritic drive g_s*f(u_d).

    The real plateau sends up to g_s = 1300 pA for roughly 10-40 ms.
    """
    return step(amplitude_pA, start, start + width, duration, dt)


# ---------------------------------------------------------------- simulation

def simulate_soma(I_inj_pA, dt=DT, params=None, sigma_noise_pA=0.0, tau_ou=2.0 * ms, seed=0):
    """Simulate one somatic compartment.

    Parameters
    ----------
    I_inj_pA : 1-D array
        Injected current in pA, one value per time step (build it with step() / plateau()).
    params : dict, optional
        Overrides for SOMA_PARAMS, e.g. {"b_w_s": 0 * pA} to switch adaptation off.
    sigma_noise_pA : float
        Standard deviation of Ornstein-Uhlenbeck background noise (0 = deterministic).
    seed : int
        Random seed, so noisy runs are reproducible.

    Returns
    -------
    dict with numpy arrays: t (ms), u (mV), w (pA), I (pA), spikes (ms).
    """
    p = {**SOMA_PARAMS, **(params or {})}
    I_inj_pA = np.asarray(I_inj_pA, dtype=float)
    duration = len(I_inj_pA) * dt

    b2.start_scope()
    b2.seed(seed)
    b2.defaultclock.dt = dt

    I_inj = b2.TimedArray(I_inj_pA * pA, dt=dt)
    namespace = {**p, "I_inj": I_inj, "sigma": sigma_noise_pA * pA, "tau_ou": tau_ou}

    eqs = """
    du/dt = -(u - E_L)/tau_s + (I_inj(t) + I_noise + w)/C_s : volt (unless refractory)
    dw/dt = -w/tau_w_s : amp
    dI_noise/dt = -I_noise/tau_ou + sigma*sqrt(2/tau_ou)*xi : amp
    """
    neuron = b2.NeuronGroup(
        1, eqs,
        threshold="u > V_T",
        reset="u = E_L; w += b_w_s",
        refractory=p["t_ref"],
        method="euler",
        namespace=namespace,
    )
    neuron.u = p["E_L"]

    state = b2.StateMonitor(neuron, ["u", "w"], record=0)
    spikes = b2.SpikeMonitor(neuron)
    b2.run(duration, namespace=namespace)

    return {
        "t": np.asarray(state.t / ms),
        "u": np.asarray(state.u[0] / mV),
        "w": np.asarray(state.w[0] / pA),
        "I": I_inj_pA,
        "spikes": np.asarray(spikes.t / ms),
    }


# ---------------------------------------------------------------- small analysis helpers

def isis(spike_times_ms):
    """Inter-spike intervals in ms."""
    return np.diff(spike_times_ms)


def rheobase_pA(params=None):
    """Smallest constant current that ever reaches threshold (ignoring adaptation).

    Steady state of the leak: u = E_L + I*tau_s/C_s, so I_min = (V_T - E_L) * C_s / tau_s.
    """
    p = {**SOMA_PARAMS, **(params or {})}
    return float((p["V_T"] - p["E_L"]) * p["C_s"] / p["tau_s"] / pA)


def with_spikes_drawn(result, peak_mV=20.0):
    """Copy of the voltage trace with a vertical line drawn at each spike, for plotting only.

    An integrate-and-fire model has no spike shape: the voltage jumps from threshold
    straight back to reset. Drawing a spike makes the traces readable.
    """
    u = result["u"].copy()
    idx = np.searchsorted(result["t"], result["spikes"])
    u[idx[idx < len(u)]] = peak_mV
    return u
