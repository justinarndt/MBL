# src/noise_models.py
import cirq
import numpy as np

class SycamoreNoiseModel(cirq.NoiseModel):
    """
    High-fidelity noise model mimicking Google Sycamore (2025).
    Includes T1 relaxation, Tphi dephasing, and residual ZZ crosstalk.
    """
    def __init__(self, t1_micros=20.0, tphi_micros=30.0, gate_time_ns=25.0):
        self.t1 = t1_micros * 1000.0   # convert to ns
        self.tphi = tphi_micros * 1000.0
        self.gate_duration = gate_time_ns

    def noisy_moments(self, circuit, moments):
        # Calculate damping parameters [cite: 158, 164]
        gamma = 1.0 - np.exp(-self.gate_duration / self.t1)
        lam = 1.0 - np.exp(-self.gate_duration / self.tphi)
        
        for moment in moments:
            # 1. Yield the original operations
            yield moment
            
            # 2. Apply decoherence to all qubits involved
            noise_ops = []
            for qubit in moment.qubits:
                noise_ops.append(cirq.amplitude_damp(gamma).on(qubit))
                noise_ops.append(cirq.phase_damp(lam).on(qubit))
            
            # 3. Apply residual ZZ crosstalk (simplified for demonstration)
            # This models the "always-on" coupling error [cite: 167]
            for i in range(len(moment.qubits) - 1):
                q1, q2 = list(moment.qubits)[i], list(moment.qubits)[i+1]
                # Small coherent error
                noise_ops.append(cirq.ZZPowGate(exponent=0.01).on(q1, q2))

            yield cirq.Moment(noise_ops)

def add_readout_error(result_dict, error_prob=0.03):
    """Simulates readout bit-flips."""
    # Placeholder for post-processing logic
    return result_dict