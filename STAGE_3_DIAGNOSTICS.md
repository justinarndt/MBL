# Stage III: Closed-Loop Hamiltonian Learning (Digital Twin)

> "The ultimate test of a quantum simulation is not just predicting the future state, but diagnosing the present errors."

### The Objective
Standard MBL benchmarks (Stage II) assume a perfect unitary evolution. Real hardware (Sycamore) suffers from calibration drift and crosstalk. **Stage III transforms the MBL protocol from a benchmark into a diagnostic tool.**

### The Method: Differentiable Physics
This module (`lazarus_v3_twin.py`) treats the laws of physics as a differentiable layer.
1.  **Ingest:** Takes a noisy experimental trace (Imbalance vs Time).
2.  **Invert:** Uses a gradient-based optimizer (L-BFGS-B) to minimize the error between the theoretical `DigitalTwin` and the experimental data.
3.  **Diagnose:** Outputs the *exact* Hamiltonian parameters of the physical chip, revealing broken couplers or crosstalk without manual calibration.

### Results
The system successfully recovered hidden hardware defects (e.g., a broken coupler at $J_{3,4}$) purely from the output signal.

![Calibration Heatmap](stage3_calibration_heatmap.png)

*Upper: The Digital Twin (Green) accurately reconstructing the drifting hardware parameters (Red).*
*Lower: Error heatmap showing near-zero residuals (< 1e-4) after optimization.*