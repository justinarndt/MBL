# Sycamore Verification Protocol: Aubry-Andre MBL ("Stage II")

**Addressing the "Stage II" Gap in Quantum Applications**
*Reference: "The Grand Challenge of Quantum Applications" (arXiv:2511.09124v2)*

### The Problem
Google Quantum AI identified a critical bottleneck: the lack of "Stage II" problem instances—tasks that are **classically hard** to simulate but **quantumly easy to verify**. Random Circuit Sampling (RCS) is hard but difficult to verify due to chaotic thermalization.

### The Solution: Deterministic MBL
This project implements a 1D Spin Chain with Quasi-Periodic Z-Potentials (Aubry-Andre class). Unlike random circuits, this system is **deterministic** and scale-invariant.

* **Hamiltonian:** XX-Interaction + Quasi-Periodic Z-Field ($\Delta \cos(2\pi \beta i)$).
* **Parameters:** $\beta = 1.618$ (Golden Ratio), $\Delta = 6.0J$ (Deep Localization).
* **Scale:** Verified at $L=50$ (Sycamore Scale).

### Verification Results
Verified via Tensor Network simulations (TeNPy/TEBD) using `lazarus_v2.py`.

![Verification Plots](final_evidence.png)

1.  **Quantum Verifiability:** The system exhibits robust Many-Body Localization (MBL). The Imbalance parameter $\mathcal{I}(t)$ stabilizes at **~0.87**, providing a high-contrast "Heartbeat" signal for hardware fidelity.
2.  **Classical Hardness:** Entanglement entropy grows logarithmically ($S \propto \ln t$), forcing the Bond Dimension $\chi$ to scale from 8 to >300. This confirms the regime is non-trivial for classical simulation.

### Repository Contents
* `lazarus_v2.py`: The physics engine (using `physics-tenpy`) for generating the Hamiltonian and running TEBD diagnostics.

* `final_evidence.png`: Plot showing the Imbalance persistence (Heartbeat) and Entanglement growth (Cost).
