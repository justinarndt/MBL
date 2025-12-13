# src/mapping.py
import networkx as nx
import cirq
import numpy as np

def get_sycamore_graph(device_name='sycamore'):
    """
    Generates the connectivity graph for the Sycamore processor.
    Mimics the 'rotated lattice' topology.
    """
    # Create a 10x10 grid to represent the raw qubit layout
    # In a real deployment, this pulls from cirq_google.Sycamore
    qubits = [cirq.GridQubit(r, c) for r in range(10) for c in range(10)]
    
    # Sycamore has a specific coupling map (checkerboard-like)
    # We build a graph where edges represent valid couplers
    G = nx.Graph()
    G.add_nodes_from(qubits)
    
    for q in qubits:
        # Add edges for nearest neighbors (simplified Sycamore topology)
        neighbors = [
            cirq.GridQubit(q.row + 1, q.col),
            cirq.GridQubit(q.row, q.col + 1)
        ]
        for n in neighbors:
            if n in qubits:
                G.add_edge(q, n)
    
    # HARDCODED DEFECT MAP (Simulating 'Weber' chip calibration data)
    # This signals insider awareness of yield issues [cite: 119]
    dead_qubits = [
        cirq.GridQubit(0, 5), cirq.GridQubit(2, 4), cirq.GridQubit(6, 2),
        cirq.GridQubit(7, 8), cirq.GridQubit(9, 1)
    ]
    for dq in dead_qubits:
        if dq in G:
            G.remove_node(dq)
            
    return G

def find_snake_path(G, start_node=None, length=50):
    """
    Finds a simple path (Snake) avoiding defects using Warnsdorff's heuristic.
    """
    nodes = list(G.nodes())
    
    # Prioritize corners/edges to maximize space usage
    if start_node is None:
        start_candidates = sorted(nodes, key=lambda n: G.degree(n))
    else:
        start_candidates = [start_node]

    best_path = []

    for start in start_candidates[:5]: # Try best 5 start points
        stack = [(start, [start])]
        
        while stack:
            current, path = stack.pop()
            
            if len(path) >= length:
                return path # Found valid path
            
            if len(path) > len(best_path):
                best_path = path

            # Get neighbors not in path
            neighbors = [n for n in G.neighbors(current) if n not in path]
            
            # Warnsdorff's Heuristic: Sort by degree (low to high)
            # Hug boundaries to avoid fragmenting the grid [cite: 104]
            neighbors.sort(key=lambda n: G.degree(n), reverse=True)
            
            for n in neighbors:
                stack.append((n, path + [n]))
                
    return best_path

def visualize_mapping(path):
    print(f"Mapped Chain Length: {len(path)}")
    print("Start:", path[0])
    print("End:  ", path[-1])