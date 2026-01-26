"""
Q-Lang Compiler
Converts Q-Lang AST to visual circuit representation
"""

from typing import List, Dict, Any
from .parser import (
    Program, TimeStep, GateOperation,
    SingleQubitGate, TwoQubitGate, ThreeQubitGate
)


class QLangCompiler:
    """Compiler: Q-Lang AST → Circuit gates"""
    
    def compile(self, program: Program) -> List[Dict[str, Any]]:
        """
        Compile Q-Lang program to circuit gate list
        
        Args:
            program: Parsed and validated Q-Lang program
            
        Returns:
            List of gate dictionaries compatible with CircuitEditorWidget
            Format: {'type': str, 'qubit': int, 'time_step': int, 
                     'control': int, 'params': dict}
        """
        gates = []
        
        for time_step_idx, time_step in enumerate(program.time_steps):
            for operation in time_step.operations:
                compiled_gates = self._compile_operation(operation, time_step_idx)
                gates.extend(compiled_gates)
        
        return gates
    
    def _compile_operation(self, operation: GateOperation, 
                          time_step: int) -> List[Dict[str, Any]]:
        """Compile a single operation to gate dict(s)"""
        
        if isinstance(operation, SingleQubitGate):
            return self._compile_single_qubit_gate(operation, time_step)
        elif isinstance(operation, TwoQubitGate):
            return [self._compile_two_qubit_gate(operation, time_step)]
        elif isinstance(operation, ThreeQubitGate):
            return [self._compile_three_qubit_gate(operation, time_step)]
        
        return []
    
    def _compile_single_qubit_gate(self, gate: SingleQubitGate, 
                                   time_step: int) -> List[Dict[str, Any]]:
        """Compile single-qubit gate (may apply to multiple qubits)"""
        gates = []
        
        for qubit in gate.qubits:
            gate_dict = {
                'type': gate.gate_name,
                'qubit': qubit,
                'time_step': time_step,
                'control': None,
                'params': {}
            }
            
            # Add parameter if present
            if gate.parameter:
                try:
                    param_value = gate.parameter.evaluate()
                    gate_dict['params']['angle'] = param_value
                except ValueError:
                    # Keep original expression if evaluation fails
                    gate_dict['params']['angle'] = gate.parameter.expression
            
            gates.append(gate_dict)
        
        return gates
    
    def _compile_two_qubit_gate(self, gate: TwoQubitGate, 
                               time_step: int) -> Dict[str, Any]:
        """Compile two-qubit gate"""
        return {
            'type': gate.gate_name,
            'qubit': gate.target,
            'time_step': time_step,
            'control': gate.control,
            'params': {}
        }
    
    def _compile_three_qubit_gate(self, gate: ThreeQubitGate, 
                                  time_step: int) -> Dict[str, Any]:
        """Compile three-qubit gate (Toffoli, CCZ)"""
        return {
            'type': gate.gate_name,
            'qubit': gate.target,
            'time_step': time_step,
            'control': gate.control1,  # Store first control
            'control2': gate.control2,  # Store second control
            'params': {}
        }


class QLangDecompiler:
    """Decompiler: Circuit gates → Q-Lang code"""
    
    def decompile(self, gates: List[Dict[str, Any]], 
                  num_qubits: int = None) -> str:
        """
        Decompile circuit gates to Q-Lang code
        
        Args:
            gates: List of gate dictionaries from CircuitEditorWidget
            num_qubits: Optional number of qubits (for validation)
            
        Returns:
            Q-Lang source code string
        """
        if not gates:
            return "# Empty circuit\n"
        
        # Group gates by time step
        time_steps: Dict[int, List[Dict[str, Any]]] = {}
        for gate in gates:
            ts = gate['time_step']
            if ts not in time_steps:
                time_steps[ts] = []
            time_steps[ts].append(gate)
        
        # Generate code
        lines = []
        lines.append("# Generated Q-Lang code")
        lines.append("")
        
        # Sort by time step
        for ts in sorted(time_steps.keys()):
            gates_in_step = time_steps[ts]
            
            # Group by gate type and qubits for compact representation
            statements = []
            
            for gate in gates_in_step:
                statement = self._decompile_gate(gate)
                statements.append(statement)
            
            # Join statements with semicolons
            line = "; ".join(statements)
            lines.append(line)
        
        return "\n".join(lines)
    
    def _decompile_gate(self, gate: Dict[str, Any]) -> str:
        """Decompile a single gate to Q-Lang syntax"""
        gate_type = gate['type']
        qubit = gate['qubit']
        control = gate.get('control')
        params = gate.get('params', {})
        
        # Two-qubit gates
        if control is not None and gate_type in ['CNOT', 'CZ', 'SWAP', 'CX']:
            return f"{gate_type} {control}-{qubit}"
        
        # Three-qubit gates
        if 'control2' in gate:
            control2 = gate['control2']
            return f"{gate_type} {control}-{control2}-{qubit}"
        
        # Parametric single-qubit gates
        if gate_type in ['Rx', 'Ry', 'Rz'] and 'angle' in params:
            angle = params['angle']
            # Format angle nicely
            if isinstance(angle, float):
                # Check for common fractions of π
                import math
                if abs(angle - math.pi/2) < 0.001:
                    angle_str = "π/2"
                elif abs(angle - math.pi/4) < 0.001:
                    angle_str = "π/4"
                elif abs(angle - math.pi) < 0.001:
                    angle_str = "π"
                else:
                    angle_str = f"{angle:.6f}".rstrip('0').rstrip('.')
            else:
                angle_str = str(angle)
            
            return f"{gate_type}({angle_str}) {qubit}"
        
        # Regular single-qubit gates
        return f"{gate_type} {qubit}"


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == '__main__':
    from .parser import QLangParser
    from .validator import QLangValidator
    
    parser = QLangParser()
    compiler = QLangCompiler()
    decompiler = QLangDecompiler()
    
    # Test 1: Bell state
    print("Test 1: Bell state compilation")
    print("=" * 60)
    code1 = """
H 0
CNOT 0-1
    """
    ast1 = parser.parse(code1)
    validator1 = QLangValidator(num_qubits=2)
    validator1.validate(ast1)
    
    gates1 = compiler.compile(ast1)
    print("Compiled gates:")
    for gate in gates1:
        print(f"  {gate}")
    
    print("\nDecompiled code:")
    decompiled1 = decompiler.decompile(gates1)
    print(decompiled1)
    print()
    
    # Test 2: Complex circuit
    print("Test 2: Complex circuit with parallel operations")
    print("=" * 60)
    code2 = """
H 0, 2, 4; X 1, 3
CNOT 0-1; CNOT 2-3
Toffoli 0-1-2
    """
    ast2 = parser.parse(code2)
    validator2 = QLangValidator(num_qubits=5)
    validator2.validate(ast2)
    
    gates2 = compiler.compile(ast2)
    print("Compiled gates:")
    for gate in gates2:
        print(f"  {gate}")
    
    print("\nDecompiled code:")
    decompiled2 = decompiler.decompile(gates2)
    print(decompiled2)
    print()
    
    # Test 3: Parametric gates
    print("Test 3: Parametric rotation gates")
    print("=" * 60)
    code3 = """
Rx(π/2) 0
Ry(π/4) 1
Rz(1.5708) 2
    """
    ast3 = parser.parse(code3)
    validator3 = QLangValidator(num_qubits=3)
    validator3.validate(ast3)
    
    gates3 = compiler.compile(ast3)
    print("Compiled gates:")
    for gate in gates3:
        print(f"  {gate}")
    
    print("\nDecompiled code:")
    decompiled3 = decompiler.decompile(gates3)
    print(decompiled3)
    
    print("\n✅ All compiler tests completed!")
