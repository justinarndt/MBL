import numpy as np
import scipy.sparse as sparse
import scipy.sparse.linalg as linalg
import matplotlib.pyplot as plt
import time

try:
    from tenpy.models.spins import SpinChain
    from tenpy.networks.mps import MPS
    from tenpy.algorithms import tebd
    TENPY_AVAILABLE = True
except ImportError:
    TENPY_AVAILABLE = False
    print("WARNING: 'physics-tenpy' not found.")

# --- PART 1: THE GENERATOR (Z-Basis Traps) ---
class GeneratorGenome:
    def __init__(self, J0=1.0, Delta=3.0, Beta=1.618, Phi=0.0, h_avg=0.0):
        self.J0 = J0          # Interaction Strength (in X)
        self.Delta = Delta    # Trap Strength (in Z)
        self.Beta = Beta      # Frequency
        self.Phi = Phi        # Phase
        self.h_avg = h_avg    # Bias

    def generate_couplings(self, L):
        indices = np.arange(L)
        # Constant Interaction in X-basis to drive dynamics
        J = np.ones(L-1) * self.J0
        
        # Quasi-Periodic Potential in Z-basis to TRAP the state
        # h_z = Delta * cos(2*pi*beta*i + phi)
        h = self.h_avg + self.Delta * np.cos(2 * np.pi * self.Beta * indices + self.Phi)
        return J, h

# --- PART 2: DYNAMIC SCANNER (Rotated for New Hamiltonian) ---
class DynamicScanner:
    def __init__(self, L=12):
        self.L = L
        self.dim = 2**L
        self.sz = np.array([[1., 0.], [0., -1.]])
        self.sx = np.array([[0., 1.], [1., 0.]])

    def get_imbalance_score(self, genome):
        J, h = genome.generate_couplings(self.L)
        H = sparse.csr_matrix((self.dim, self.dim), dtype=float)
        
        # Interaction J is now SxSx (Flip-Flop term)
        for i in range(self.L - 1):
            term = sparse.csr_matrix([1.])
            for site in range(self.L):
                op = self.sx if (site==i or site==i+1) else sparse.eye(2)
                term = sparse.kron(term, op, format='csr')
            H += J[i] * term
            
        # Field h is now Sz (The Trap)
        for i in range(self.L):
            term = sparse.csr_matrix([1.])
            for site in range(self.L):
                op = self.sz if site==i else sparse.eye(2)
                term = sparse.kron(term, op, format='csr')
            H += h[i] * term
            
        # Initial State: Néel |0101...> (Z-basis)
        neel_int = 0
        for i in range(1, self.L, 2):
            neel_int += 2**i
            
        psi = np.zeros(self.dim)
        psi[neel_int] = 1.0
        
        # Evolve
        dt = 0.5
        current_psi = psi
        avg_imbalance = 0.0
        
        # Precompute I operator (Z-basis)
        I_op = sparse.csr_matrix((self.dim, self.dim), dtype=float)
        for i in range(self.L):
            term = sparse.csr_matrix([1.])
            for site in range(self.L):
                op = self.sz if site==i else sparse.eye(2)
                term = sparse.kron(term, op, format='csr')
            I_op += ((-1)**i) * term

        for t in np.arange(0, 10.0, dt):
            imb = np.vdot(current_psi, I_op.dot(current_psi)).real / self.L
            avg_imbalance += abs(imb)
            current_psi = linalg.expm_multiply(-1j * H * dt, current_psi)
            
        return avg_imbalance / len(np.arange(0, 10.0, dt))

# --- PART 3: DEEP VERIFIER (Corrected Physics) ---
class DeepVerifier:
    def __init__(self, L=50):
        self.L = L

    def run_imbalance_dynamics(self, genome, t_max=20, dt=0.1):
        if not TENPY_AVAILABLE: return [], [], []
        
        print(f"--- STARTING L={self.L} Z-BASIS MBL SIMULATION ---")
        J, h = genome.generate_couplings(self.L)
        
        # PHYSICS CORRECTION:
        # J goes to 'Jx' (Interaction)
        # h goes to 'hz' (Trap)
        model_params = {
            'L': self.L, 'S': 0.5, 
            'Jx': J, 'hz': h,      
            'bc_MPS': 'finite', 'conserve': None
        }
        
        model = SpinChain(model_params)
        init_state = ["up", "down"] * (self.L // 2)
        psi = MPS.from_product_state(model.lat.mps_sites(), init_state)
        
        # We increase chi_max to 800 to allow logarithmic growth
        tebd_engine = tebd.TEBDEngine(psi, model, {'dt': dt, 'order': 2, 'trunc_params': {'chi_max': 800}})
        
        times = []
        imbalances = []
        bond_dims = []
        
        steps = int(t_max / dt)
        
        for i in range(steps):
            tebd_engine.run()
            mags = 2 * psi.expectation_value("Sz") 
            imbalance = np.mean([mags[j] * ((-1)**(j % 2)) for j in range(self.L)])
            
            times.append((i+1)*dt)
            imbalances.append(imbalance)
            bond_dims.append(max(psi.chi))
            
            if i % 10 == 0:
                print(f"t={times[-1]:.1f} | I={imbalance:.3f} | MaxChi={max(psi.chi)}")
                
        return times, imbalances, bond_dims

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    print("Initializing Project Lazarus Phase 3 (Physics Correction)...")
    
    # 1. THE SEARCH (Scanning Delta for Z-Localization)
    print("\n[STEP 1] TUNING TRAP STRENGTH (Delta)")
    # We scan Delta from 2.0 to 6.0. 
    # MBL transition is typically Delta > 2J.
    scan_range = np.linspace(2.0, 6.0, 15)
    scanner = DynamicScanner(L=12)
    
    best_score = 0.0
    best_delta = 0.0
    
    for delta in scan_range:
        # Beta=1.618 (Golden Ratio)
        genome = GeneratorGenome(J0=1.0, Delta=delta, Beta=1.618, Phi=0.0)
        score = scanner.get_imbalance_score(genome)
        print(f"Delta: {delta:.2f} | Avg Imbalance: {score:.4f}")
        
        if score > best_score:
            best_score = score
            best_delta = delta
            
    print(f"\n>> BEST TRAP: Delta={best_delta:.2f} (Avg I={best_score:.4f})")
    
    # 2. THE VERIFICATION
    print("\n[STEP 2] DEEP VERIFICATION (L=50)")
    if TENPY_AVAILABLE:
        verifier = DeepVerifier(L=50)
        candidate = GeneratorGenome(J0=1.0, Delta=best_delta, Beta=1.618, Phi=0.0)
        
        # Long run
        ts, imbs, chis = verifier.run_imbalance_dynamics(candidate, t_max=40.0)
        
        # Plot
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        plt.plot(ts, imbs, label="Imbalance", color='blue')
        plt.axhline(0, color='black', linestyle='--', alpha=0.3)
        plt.xlabel("Time")
        plt.ylabel("Imbalance I(t)")
        plt.title(f"Z-MBL Verification (Delta={best_delta:.2f})")
        plt.ylim(0.0, 1.0) # Should stay positive now!
        plt.grid(True)
        
        plt.subplot(1, 2, 2)
        plt.plot(ts, chis, color='orange', label="Bond Dim")
        plt.xlabel("Time")
        plt.ylabel("Bond Dimension (Chi)")
        plt.title("Entanglement Growth")
        plt.grid(True)
        
        plt.savefig("lazarus_v2_results_corrected.png")
        print("Results saved to 'lazarus_v2_results_corrected.png'")