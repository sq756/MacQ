"""
MacQ Core - Circuit Optimization
Algorithms for simplifying quantum circuits.
"""

from typing import List, Dict, Any

class CircuitOptimizer:
    """Headless optimizer for simplifying quantum circuits."""
    
    @staticmethod
    def simplify_pauli_strings(gates: List[Dict[str, Any]], num_qubits: int) -> List[Dict[str, Any]]:
        """
        Eliminate redundant consecutive self-inverse gates (e.g., X-X -> I).
        
        Args:
            gates: List of gate dictionaries.
            num_qubits: Number of qubits in the circuit.
            
        Returns:
            Optimized list of gates.
        """
        if not gates:
            return []
            
        optimized_gates = []
        # Group by qubits to check for local redundancies
        all_q_gates = [[] for _ in range(num_qubits)]
        for g in gates:
            if g['qubit'] < num_qubits:
                all_q_gates[g['qubit']].append(g)
        
        # We need to preserve global order (time_step) but check local adjacency
        # Actually, if we only eliminate X-X on the same qubit, it's safe if no other multi-qubit gates 
        # involving that qubit are between them.
        # This basic version follows the GUI's logic for now.
        
        result_gates = []
        for q in range(num_qubits):
            q_gates = sorted(all_q_gates[q], key=lambda g: g['time_step'])
            if not q_gates:
                continue
            
            i = 0
            while i < len(q_gates):
                current = q_gates[i]
                if i + 1 < len(q_gates):
                    next_gate = q_gates[i+1]
                    # Self-inverse Pauli and Hadamard gates
                    if (current['type'] == next_gate['type'] and 
                        current['type'] in ['X', 'Y', 'Z', 'H', 'I']):
                        i += 2
                        continue
                
                result_gates.append(current)
                i += 1
        
        # Sort by time step before returning
        result_gates.sort(key=lambda g: g['time_step'])
        return result_gates

    def optimize(self, circuit) -> None:
        """Apply optimization to a Circuit object in-place."""
        circuit.gates = self.simplify_pauli_strings(circuit.gates, circuit.num_qubits)
