import numpy as np
import matplotlib.pyplot as plt
from physics import SpinChain  # Assumes physics.py is in the same folder

# --- 1. The Discovered "Lazarus Sequence" (L=10) ---
# Parameters from your run:
genome_L10 = np.array([
    0.94791692, 0.53241117, 0.61798154, 0.58561579, 1.15209473, 
    1.27981671, 0.61539413, 1.02252724, 1.24199189, # J terms (9)
    1.0666585,  1.44220798, 0.83773367, 1.15752662, 1.06443279, 
    0.77917893, 1.46338286, 1.36173537, 0.85364171, 1.1402877  # h terms (10)
])

def extend_genome(genome, current_L, target_L):
    """
    Extends a genome from current_L to target_L using Cyclic Repetition.
    This treats the L=10 sequence as a 'unit cell' of a larger crystal.
    """
    if target_L == current_L:
        return genome
        
    # Split into J and h components
    num_J = current_L - 1
    J_part = genome[:num_J]
    h_part = genome[num_J:]
    
    # Calculate new lengths
    target_num_J = target_L - 1
    target_num_h = target_L
    
    # Extend J (Cyclic)
    J_extended = []
    for i in range(target_num_J):
        J_extended.append(J_part[i % num_J])
        
    # Extend h (Cyclic)
    h_extended = []
    for i in range(target_num_h):
        h_extended.append(h_part[i % len(h_part)])
        
    return np.concatenate((J_extended, h_extended))

def run_scaling_analysis():
    print("==================================================")
    print("   PROJECT LAZARUS: STAGE II SCALING VERIFICATION")
    print("==================================================")
    print("Objective: Test if 'Lazarus Sequence' holds <r> ~ 0.39 at larger L.")
    
    sizes = [10, 12, 14]
    results = []
    
    for L in sizes:
        print(f"\n--- Testing System Size L={L} ---")
        
        # 1. Extend Genome
        genome_extended = extend_genome(genome_L10, 10, L)
        
        # 2. Build Hamiltonian
        sim = SpinChain(L)
        sim.build_hamiltonian(genome_extended)
        
        # 3. Calculate Statistics
        # Note: L=14 might take 1-2 minutes on a laptop
        print(f"Diagonalizing Hamiltonian (Dim: {2**L}x{2**L})...")
        r = sim.get_level_statistics()
        results.append(r)
        
        print(f"Result <r> = {r:.4f}")
        
        # Interpretation
        dist_poisson = abs(r - 0.386)
        dist_wd = abs(r - 0.530)
        
        if dist_poisson < dist_wd:
            status = "SCARRED (Non-Ergodic)"
        else:
            status = "THERMAL (Ergodic)"
        print(f"Status: {status}")

    # --- Plotting ---
    plt.figure(figsize=(8, 5))
    plt.plot(sizes, results, marker='o', linewidth=2, label='Lazarus Sequence')
    plt.axhline(0.386, color='g', linestyle='--', label='Poisson (Integrable)')
    plt.axhline(0.530, color='r', linestyle='--', label='Wigner-Dyson (Chaos)')
    
    plt.xlabel('System Size (L)')
    plt.ylabel('Level Spacing Ratio <r>')
    plt.title('Finite-Size Scaling of Spectral Statistics')
    plt.xticks(sizes)
    plt.legend()
    plt.grid(True)
    plt.savefig('scaling_verification_plot.png')
    print("\n[DONE] Plot saved to 'scaling_verification_plot.png'")

if __name__ == "__main__":
    run_scaling_analysis()