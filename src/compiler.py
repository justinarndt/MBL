# src/compiler.py
import cirq
import numpy as np

def compile_aubry_andre_trotter_step(qubits, J, Delta, V, dt):
    """
    Compiles a single Trotter step of the Aubry-Andre Hamiltonian
    into native Sycamore FSIM gates.
    
    Args:
        qubits: Ordered list of cirq.GridQubit (from mapping.py)
        J: Hopping strength
        Delta: Interaction strength
        V: List of on-site potentials
        dt: Time step size
    """
    circuit = cirq.Circuit()
    
    # FSIM Parameters [cite: 134, 135]
    # theta maps to the hopping term (XY)
    # phi maps to the interaction term (ZZ)
    theta = -2.0 * J * dt
    phi = -2.0 * Delta * dt
    
    fsim_gate = cirq.FSimGate(theta=theta, phi=phi)
    
    # Parity-based layering (Checkerboard decomposition)
    # Layer 1: Even bonds
    even_moments = []
    for i in range(0, len(qubits)-1, 2):
        q1, q2 = qubits[i], qubits[i+1]
        even_moments.append(fsim_gate.on(q1, q2))
    circuit.append(cirq.Moment(even_moments))
    
    # Layer 2: Odd bonds
    odd_moments = []
    for i in range(1, len(qubits)-1, 2):
        q1, q2 = qubits[i], qubits[i+1]
        odd_moments.append(fsim_gate.on(q1, q2))
    circuit.append(cirq.Moment(odd_moments))
    
    # Layer 3: On-site potentials (Virtual Z rotations)
    # Propagator is exp(-i * dt * V_i * Z_i)
    z_moments = []
    for i, q in enumerate(qubits):
        # rads = 2 * V * dt [cite: 146]
        rads = 2.0 * V[i] * dt
        z_moments.append(cirq.rz(rads).on(q))
    circuit.append(cirq.Moment(z_moments))
    
    return circuit