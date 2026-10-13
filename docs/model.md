# Model: two-compartment burst-multiplexing neuron

Reference model for reproducing Naud & Sprekeler (2018), *Sparse bursts optimize information transmission in a multiplexed neural code*, PNAS 115(27):E6329 ([PubMed 29934400](https://pubmed.ncbi.nlm.nih.gov/29934400/)).

## Where these values come from

The main text of the PNAS paper (read Oct 7) gives the equations (Eqs. 5–6) but no parameter values. It puts all values in **SI Appendix, Computational Methods** and **SI Appendix, Table S1**, which we don't have yet. The values below come from two later codebases by the same groups. The 2018 paper does not cite either one, since both are from 2021:

| Source | What it gives | Status |
| --- | --- | --- |
| **[S1]** Vercruysse, Naud & Sprekeler (2021), PLOS Comp Biol, code: [sprekelerlab/SourceCode_Vercruysse21](https://github.com/sprekelerlab/SourceCode_Vercruysse21), `Fig 1.ipynb`, `pyramidal_model()` | All neuron equations and parameters, in Brian2. The code says: *"Unless otherwise stated, the neuron models are identical to the ones defined in Naud et al. 2018 (… PNAS)"* | ✅ Primary source for the neuron |
| **[S2]** Payeur, Guerguiev, Zenke, Richards & Naud (2021), Nat Neurosci, code: [apayeur/spikingburstprop](https://github.com/apayeur/spikingburstprop), `sim/sim_propagation.cpp`, `src/STPeTMConnection.cpp` | STD and STF synapse parameters (extended Tsodyks–Markram) | ⚠️ **Placeholder only.** These are Naud's 2021 choices, not the 2018 values |
| **[S0]** Naud & Sprekeler 2018, PNAS main text (Materials and Methods) | Eqs. 5–6, burst definition, noise, connectivity, input statistics, decoding method, STP citations | ✅ Read from the PDF |

**Before Phase 2:** compare every row marked ⚠️ with the PNAS SI (see *Open items*).

---

## 1. Somatic compartment

$$
\frac{du_s}{dt} = -\frac{u_s - E_L}{\tau_s} + \frac{g_s\, f(u_d) + I_s + w_s}{C_s}
$$

$$
\frac{dw_s}{dt} = -\frac{w_s}{\tau_{w_s}}
$$

**Spike and reset:** when $u_s > \theta = -50$ mV, a spike is emitted, $u_s \leftarrow E_L$ and $w_s \leftarrow w_s + b_{w_s}$. Then an absolute refractory period of 3 ms follows, with $u_s$ clamped.

- The soma does **not** receive raw dendritic voltage. It receives the dendritic **nonlinearity** $g_s f(u_d)$, so a dendritic plateau drives the soma as a current.
- $b_{w_s} < 0$, so $w_s$ is a hyperpolarising current, added with a $+$ sign. This is spike-triggered adaptation.

## 2. Dendritic compartment

$$
\frac{du_d}{dt} = -\frac{u_d - E_L}{\tau_d} + \frac{g_d\, f(u_d) + K(t - \hat t_s) + I_d + w_d}{C_d}
$$

$$
\tau_{w_d}\frac{dw_d}{dt} = -w_d + a_{w_d}\,(u_d - E_L)
$$

**Dendritic nonlinearity** (the regenerative Ca²⁺-like current):

$$
f(u_d) = \frac{1}{1 + \exp\!\left(-\dfrac{u_d - E_d}{D_d}\right)}
$$

**Backpropagating action potential (bAP).** $\hat t_s$ is the time of the last somatic spike. The bAP is a rectangular current pulse:

$$
K(t - \hat t_s) = c_d \cdot \mathbb{1}\left[\,0.5\text{ ms} < t - \hat t_s < 2.5\text{ ms}\,\right]
$$

In words, the pulse has amplitude $c_d$ and lasts 2 ms, starting 0.5 ms after the somatic spike.

- $a_{w_d} < 0$, so $w_d$ is subthreshold adaptation that terminates the dendritic plateau. This sets the burst length.
- **Burst mechanism:** a somatic spike sends a bAP into the dendrite. If the dendrite is already depolarised by top-down input, the bAP pushes $u_d$ past $E_d$. The plateau $g_d f(u_d)$ then turns on and drives the soma through $g_s f(u_d)$, producing extra spikes, which is the burst.

## 3. Inputs and background noise

Total input current per compartment ($x \in \{s, d\}$):

$$
I_x = I_x^{\text{ext}} + I_x^{\text{bg}} + I_x^{\text{AMPA}} - I_x^{\text{GABA}}
$$

**Background noise.** This is an Ornstein–Uhlenbeck process, drawn independently for each neuron and each compartment:

$$
\frac{dI_x^{\text{bg}}}{dt} = \frac{\mu_x - I_x^{\text{bg}}}{\tau_{\text{OU}}} + \sigma_x\sqrt{\frac{2}{\tau_{\text{OU}}}}\;\xi_x(t)
$$

With this scaling, $\sigma_x$ is the stationary standard deviation of the current. In the paper, the noise amplitude is set so that the somatic membrane-potential fluctuations are **≈ 6 mV standard deviation** [S0].

**Synaptic currents.** Each is an instantaneous jump followed by exponential decay: $\tau_{\text{AMPA}} = 5$ ms and $\tau_{\text{GABA}} = 10$ ms [S1].

## 4. Parameters

### Soma [S1]

| Symbol | Code name | Value |
| --- | --- | --- |
| $\tau_s$ | `tau_s` | 16 ms |
| $C_s$ | `C_s` | 370 pF |
| $E_L$ | `EL` | −70 mV |
| $\theta$ (threshold) | `u_s > -0.05*volt` | −50 mV |
| reset | | $E_L$ (−70 mV) |
| refractory | | 3 ms |
| $g_s$ (dendrite → soma) | `g_s` | 1300 pA |
| $b_{w_s}$ (spike-triggered adaptation) | `b_w_s` | −200 pA |
| $\tau_{w_s}$ | `tau_w_s` | 100 ms |

### Dendrite [S1]

| Symbol | Code name | Value |
| --- | --- | --- |
| $\tau_d$ | `tau_d` | 7 ms |
| $C_d$ | `C_d` | 170 pF |
| $g_d$ (regenerative current) | `g_d` | 1200 pA |
| $c_d$ (bAP amplitude) | `c_d` | 2600 pA |
| bAP window | `K1`, `K2` | 0.5–2.5 ms after the somatic spike |
| $E_d$ (sigmoid midpoint) | `Ed` | −38 mV |
| $D_d$ (sigmoid slope) | `Dm` | 6 mV |
| $a_{w_d}$ (subthreshold adaptation) | `a_w_d` | −13 nS |
| $\tau_{w_d}$ | `tau_w_d` | 30 ms |

### Noise and simulation

| Quantity | Value | Source |
| --- | --- | --- |
| $\tau_{\text{OU}}$ (soma and dendrite) | 2 ms | S1 |
| $\mu_s, \mu_d$ | 0 pA (mean drive enters through $I^{\text{ext}}$) | S1 |
| $\sigma_s, \sigma_d$ | ~100–200 pA in S1 examples. Tune so that SD($u_s$) ≈ 6 mV | S0 / ⚠️ tune |
| Integration | Euler, $dt = 0.1$ ms | S1 |
| Initial $u_s$ | $E_L + U(0, 10)$ mV | S1 |

## 5. Events and bursts [S0]

- **Burst:** 2 or more spikes with consecutive inter-spike intervals **< 16 ms**, bounded by ISIs ≥ 16 ms on both sides.
- **Event:** either an isolated spike or the first spike of a burst. Every burst counts as exactly one event.
- **Population quantities** per time bin $\Delta t$ over $N$ neurons:

$$
E(t) = \frac{\#\text{events in bin}}{N\,\Delta t}, \qquad P(t) = \frac{\#\text{bursts in bin}}{\#\text{events in bin}}
$$

**Online detector** (optional, as used in S1). Two traces decay with $\tau_{\text{burst}} = -16/\ln(0.1) \approx 6.95$ ms, and each spike adds +1. A burst starts when the start trace exceeds 1.1, and ends when the stop trace falls below 0.1. For analysis, use the offline ISI rule above. It is easier to unit-test.

## 6. Readout synapses: extended Tsodyks–Markram [S2] ⚠️

The state per presynaptic neuron is resources $x$ and release probability $u$. Between spikes, $x \to 1$ with time constant $\tau_D$ and $u \to U$ with time constant $\tau_F$. At each presynaptic spike, the synapse transmits $w \cdot u\,x$ (using the pre-spike values) and then updates:

$$
x \leftarrow x - u\,x, \qquad u \leftarrow u + f\,(1 - u)
$$

| | $U$ (baseline release) | $f$ (facilitation increment) | $\tau_D$ | $\tau_F$ | What it reads out |
| --- | --- | --- | --- | --- | --- |
| **STD** (depressing) | 0.9 | 0.1 | 20 ms | 1 s | mostly the **event rate** $E(t)$ |
| **STF** (facilitating) | 0.02 | 0.1 | 100 ms | 100 ms | mostly **bursts**, i.e. $E \cdot P$ |

**What the 2018 paper itself says** [S0]: *"we used the extended Tsodyks–Markram model (63) with parameters constrained by the reported properties of neocortical connections (65) (SI Appendix, Computational Methods)."*

- Ref 63: Markram H, Wang Y, Tsodyks M (1998). *Differential signaling via the same axon of neocortical pyramidal neurons.* PNAS 95:5323–5328.
- Ref 65: Costa RP, Sjöström PJ, van Rossum MCW (2013). *Probabilistic inference of short-term synaptic plasticity in neocortical microcircuits.* Front Comput Neurosci 7:75.

The table values come from Payeur et al. (2021) code [S2], a later paper by Naud's group, and are used only as stand-ins. **Replace them** with the SI values, or with the Costa et al. (2013) fits for neocortical depressing and facilitating connections, before Phase 2's Figure 4.

In the 2018 network the STF and STD readouts target two separate inhibitory populations: **a** receives STF and **b** receives STD [S0].

## 7. Population setup for the multiplexing result [S0]

- **Main simulations:** 4,000 uncoupled neurons. **Information analysis:** 80,000 neurons.
- **Inputs:** two independent time-dependent signals. One is injected into the soma ($I_s^{\text{ext}}$, bottom-up), the other into the dendrites ($I_d^{\text{ext}}$, top-down). Both *"fluctuate with equal power in fast and slow frequencies over the 1- to 100-Hz range"*, i.e. a flat spectrum from 1 to 100 Hz. Exact amplitudes are in the SI.
- **Connectivity** (network figures only): connection probability 0.2 for excitatory and 1 for inhibitory connections. Synapses are exponentially decaying conductance changes.
- **Decoding:** estimate the dendritic input as $\log P(t)$ and the somatic input as $\log E(t)$. This works because the input-output curves are roughly exponential in the moderate-input regime.
- **Quality measure:** frequency-resolved **coherence** between each input and its estimate, then the information rate computed from it (SI Appendix, Theoretical Methods). Pulse responses use $\text{SNR}_I$ (SI Appendix, Data Analysis Methods).
- **Display:** time-dependent rates are smoothed with a 10 ms kernel.
- **Expected result:** $E(t)$ tracks the somatic signal up to about 100 Hz, while $P(t)$ tracks the dendritic signal well for slow fluctuations but poorly for fast ones.

## Open items: check against the PNAS SI

All of these need the **SI Appendix**. The main text has none of the values.

- [ ] **Neuron parameters:** compare §4 with SI Table S1. S1 says they are identical. Check $E_d$, $D_d$, $c_d$ and the bAP kernel $K$ in particular.
- [ ] **STD/STF:** get $U$, $f$, $\tau_D$, $\tau_F$ from SI Computational Methods. If the SI gives none, take them from Costa et al. 2013. The current values are 2021 placeholders (§6).
- [ ] **Input signals:** get the amplitudes of the 1–100 Hz signals and the mean currents $I_s^{\text{ext}}$, $I_d^{\text{ext}}$. *(The spectrum shape is now known.)*
- [ ] **Noise:** get the exact $\sigma_s$, $\sigma_d$. *(The target is known: somatic $V_m$ SD ≈ 6 mV.)*
- [ ] **Information rate:** get the coherence-to-information formula (SI Theoretical Methods), the bin size $\Delta t$ and the simulation length. *(The method is now known: coherence of $\log E$ and $\log P$ estimates.)*

## References

- Naud R, Sprekeler H (2018). Sparse bursts optimize information transmission in a multiplexed neural code. *PNAS* 115(27):E6329–E6338. doi:10.1073/pnas.1720995115
- Vercruysse F, Naud R, Sprekeler H (2021). Self-organization of a doubly asynchronous irregular network state for spikes and bursts. *PLOS Comput Biol* 17(11):e1009478.
- Payeur A, Guerguiev J, Zenke F, Richards BA, Naud R (2021). Burst-dependent synaptic plasticity can coordinate learning in hierarchical circuits. *Nat Neurosci* 24:1010–1019.
