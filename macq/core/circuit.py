"""
MacQ Core - Circuit Representation and Execution
Standalone circuit object that handles gates, metadata, and execution via C bridge.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from ..c_bridge import QuantumState, DensityMatrix

class Circuit:
    """Standalone Quantum Circuit object for headless/scripted usage."""
    
    def __init__(self, num_qubits: int = 3):
        self.num_qubits = num_qubits
        self.gates: List[Dict[str, Any]] = []
        self._metadata: Dict[str, Any] = {}

    def add_gate(self, gate_type: str, qubit: int, time_step: int = None, 
                 control: int = None, control2: int = None, params: dict = None):
        """Add a gate to the circuit."""
        if time_step is None:
            time_step = self._next_available_time_step(qubit)
            
        gate = {
            'type': gate_type,
            'qubit': qubit,
            'time_step': time_step,
            'control': control,
            'control2': control2,
            'params': params or {}
        }
        self.gates.append(gate)
        # Keep gates sorted by time_step
        self.gates.sort(key=lambda g: g['time_step'])
        return self

    def _next_available_time_step(self, qubit: int) -> int:
        occupied = [g['time_step'] for g in self.gates if g['qubit'] == qubit]
        if not occupied:
            return 0
        return max(occupied) + 1

    def execute(self, initial_state: QuantumState = None, noise_level: float = 0.0) -> QuantumState:
        """Execute the circuit and return the final QuantumState."""
        if not self.gates:
            return initial_state if initial_state else QuantumState(self.num_qubits)
            
        qs = initial_state if initial_state else QuantumState(self.num_qubits)
        
        for gate in self.gates:
            gate_type = gate['type']
            qubit = gate['qubit']
            control = gate.get('control')
            control2 = gate.get('control2')
            params = gate.get('params', {})
            
            applied = False
            try:
                # 1. Single Qubit Gates
                if gate_type == 'H':
                    qs.h(qubit)
                    applied = True
                elif gate_type == 'X':
                    qs.x(qubit)
                    applied = True
                elif gate_type == 'Y':
                    qs.y(qubit)
                    applied = True
                elif gate_type == 'Z':
                    qs.z(qubit)
                    applied = True
                elif gate_type == 'S':
                    qs.s(qubit)
                    applied = True
                elif gate_type == 'T':
                    qs.t(qubit)
                    applied = True
                
                # 2. Rotation Gates
                elif gate_type in ['Rx', 'Ry', 'Rz']:
                    angle = params.get('angle', 0.0)
                    if isinstance(angle, str):
                        import math
                        angle = angle.replace('π', 'math.pi').replace('pi', 'math.pi')
                        try:
                            # Use a safe eval or a parser if possible, but for now:
                            angle = eval(angle, {"math": math, "np": np})
                        except:
                            angle = 0.0
                    
                    if gate_type == 'Rx': qs.rx(qubit, angle)
                    elif gate_type == 'Ry': qs.ry(qubit, angle)
                    elif gate_type == 'Rz': qs.rz(qubit, angle)
                    applied = True
                
                # 3. Two-Qubit Gates
                elif gate_type == 'CNOT' and control is not None:
                    qs.cnot(control, qubit)
                    applied = True
                elif gate_type == 'CZ' and control is not None:
                    qs.cz(control, qubit)
                    applied = True
                elif gate_type == 'SWAP' and control is not None:
                    qs.swap(control, qubit)
                    applied = True
                
                # 4. Three-Qubit Gates
                elif gate_type in ['Toffoli', 'CCX']:
                    c1 = control
                    c2 = control2
                    if c1 is not None and c2 is not None:
                        qs.toffoli(c1, c2, qubit)
                        applied = True
                
                # 5. Advanced Gates
                elif gate_type == 'MEASURE':
                    qs.measure(qubit)
                    applied = True
                elif gate_type in ['QFT', 'QFT_INV']:
                    q_list = params.get('qubits', [qubit])
                    qs.qft(q_list, inverse=(gate_type == 'QFT_INV'))
                    applied = True
                elif gate_type == 'MOD_EXP':
                    a = params.get('a', 2)
                    N = params.get('N', 15)
                    ctrls = params.get('controls', [])
                    tgts = params.get('targets', [])
                    if ctrls and tgts:
                        qs.mod_exp(a, N, ctrls, tgts)
                        applied = True

                # Noise Injection
                if applied and noise_level > 0:
                    qs.apply_depolarizing(qubit, noise_level * 0.5)
                    qs.apply_amplitude_damping(qubit, noise_level * 0.5)
                    if control is not None:
                        qs.apply_depolarizing(control, noise_level * 0.5)
                    if control2 is not None:
                        qs.apply_depolarizing(control2, noise_level * 0.5)

            except Exception as e:
                # In CLI/Notebook, we want to know about errors
                raise RuntimeError(f"Error applying gate {gate_type} on q{qubit}: {e}")
        
        return qs

    def to_qlang(self) -> str:
        """Convert circuit back to Q-Lang source code."""
        from ..qlang.compiler import QLangDecompiler
        decompiler = QLangDecompiler()
        return decompiler.decompile(self.gates, self.num_qubits)

    @classmethod
    def from_qlang(cls, code: str):
        """Build a circuit from Q-Lang source code."""
        from ..qlang.parser import QLangParser
        from ..qlang.compiler import QLangCompiler
        from ..qlang.validator import QLangValidator
        
        parser = QLangParser()
        ast = parser.parse(code)
        
        # Determine qubit count from AST if possible
        num_qubits = 3 # Default
        for ts in ast.time_steps:
            for op in ts.operations:
                from ..qlang.parser import QubitsNode
                if isinstance(op, QubitsNode):
                    num_qubits = op.count
                    break
        
        validator = QLangValidator(num_qubits=num_qubits)
        validator.validate(ast)
        
        compiler = QLangCompiler()
        gates = compiler.compile(ast)
        
        circuit = cls(num_qubits=num_qubits)
        circuit.gates = gates
        return circuit

    def clear(self):
        """Clear all gates."""
        self.gates = []
