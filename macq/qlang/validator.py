"""
Q-Lang Validator
Semantic analysis and conflict detection for quantum circuits
"""

from typing import List, Set, Optional
from .parser import (
    Program, TimeStep, GateOperation,
    SingleQubitGate, TwoQubitGate, ThreeQubitGate,
    MeasurementNode, ConditionalNode, ModularGate
)


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


class QLangValidator:
    """Validator for Q-Lang programs"""
    
    def __init__(self, num_qubits: int):
        """
        Initialize validator
        
        Args:
            num_qubits: Total number of available qubits
        """
        self.num_qubits = num_qubits
        self.errors = []
    
    def validate(self, program: Program) -> bool:
        """
        Validate entire program
        
        Args:
            program: Parsed Q-Lang program
            
        Returns:
            True if valid, raises ValidationError if invalid
        """
        self.errors = []
        
        try:
            self._validate_program(program)
        except ValidationError as e:
            raise
        
        return len(self.errors) == 0
    
    def _validate_program(self, program: Program):
        """Validate entire program"""
        for time_step in program.time_steps:
            self._validate_time_step(time_step)
    
    def _validate_time_step(self, time_step: TimeStep):
        """
        Validate a single time step
        
        Checks:
        1. Each operation is valid
        2. No qubit is used twice in same time step
        """
        used_qubits: Set[int] = set()
        
        for operation in time_step.operations:
            # Validate individual operation
            self._validate_operation(operation)
            
            # Get all qubits involved in this operation
            involved_qubits = self._get_involved_qubits(operation)
            
            # Check for conflicts
            conflicts = used_qubits & involved_qubits
            if conflicts:
                raise ValidationError(
                    f"Line {operation.line}: Qubit(s) {conflicts} used multiple times "
                    f"in same time step"
                )
            
            used_qubits.update(involved_qubits)
    
    def _validate_operation(self, operation: GateOperation):
        """Validate a single gate operation"""
        
        if isinstance(operation, SingleQubitGate):
            self._validate_single_qubit_gate(operation)
        elif isinstance(operation, TwoQubitGate):
            self._validate_two_qubit_gate(operation)
        elif isinstance(operation, ThreeQubitGate):
            self._validate_three_qubit_gate(operation)
        elif isinstance(operation, ModularGate):
            self._validate_modular_gate(operation)
        elif isinstance(operation, MeasurementNode):
            self._validate_measurement(operation)
        elif isinstance(operation, ConditionalNode):
            self._validate_conditional(operation)
    
    def _validate_single_qubit_gate(self, gate: SingleQubitGate):
        """Validate single-qubit gate"""
        # Check qubit indices
        for qubit in gate.qubits:
            if qubit < 0 or qubit >= self.num_qubits:
                raise ValidationError(
                    f"Line {gate.line}: Qubit {qubit} out of range [0, {self.num_qubits-1}]"
                )
        
        # Check for duplicate qubits in list
        if len(gate.qubits) != len(set(gate.qubits)):
            duplicates = [q for q in gate.qubits if gate.qubits.count(q) > 1]
            raise ValidationError(
                f"Line {gate.line}: Duplicate qubit(s) {set(duplicates)} in gate operation"
            )
        
        # Check parameter requirements
        parametric_gates = {'Rx', 'Ry', 'Rz'}
        if gate.gate_name in parametric_gates:
            if gate.parameter is None:
                raise ValidationError(
                    f"Line {gate.line}: Gate '{gate.gate_name}' requires a parameter"
                )
            # Validate parameter can be evaluated
            try:
                gate.parameter.evaluate()
            except ValueError as e:
                raise ValidationError(
                    f"Line {gate.line}: {str(e)}"
                )
        else:
            if gate.parameter is not None:
                raise ValidationError(
                    f"Line {gate.line}: Gate '{gate.gate_name}' does not accept parameters"
                )
    
    def _validate_two_qubit_gate(self, gate: TwoQubitGate):
        """Validate two-qubit gate"""
        # Check qubit indices
        for qubit in [gate.control, gate.target]:
            if qubit < 0 or qubit >= self.num_qubits:
                raise ValidationError(
                    f"Line {gate.line}: Qubit {qubit} out of range [0, {self.num_qubits-1}]"
                )
        
        # Check control != target
        if gate.control == gate.target:
            raise ValidationError(
                f"Line {gate.line}: Control and target qubits cannot be the same ({gate.control})"
            )
    
    def _validate_three_qubit_gate(self, gate: ThreeQubitGate):
        """Validate three-qubit gate"""
        # Check qubit indices
        for qubit in [gate.control1, gate.control2, gate.target]:
            if qubit < 0 or qubit >= self.num_qubits:
                raise ValidationError(
                    f"Line {gate.line}: Qubit {qubit} out of range [0, {self.num_qubits-1}]"
                )
        
        # Check all three are different
        qubits = {gate.control1, gate.control2, gate.target}
        if len(qubits) != 3:
            raise ValidationError(
                f"Line {gate.line}: Control and target qubits must be distinct "
                f"(got {gate.control1}, {gate.control2}, {gate.target})"
            )
    
    def _validate_modular_gate(self, gate: ModularGate):
        """Validate modular arithmetic gate"""
        # Check all control qubits
        for qubit in gate.control_qubits:
            if qubit < 0 or qubit >= self.num_qubits:
                raise ValidationError(
                    f"Line {gate.line}: Control qubit {qubit} out of range [0, {self.num_qubits-1}]"
                )
        
        # Check all target qubits
        for qubit in gate.target_qubits:
            if qubit < 0 or qubit >= self.num_qubits:
                raise ValidationError(
                    f"Line {gate.line}: Target qubit {qubit} out of range [0, {self.num_qubits-1}]"
                )
        
        # Check no overlap between control and target
        control_set = set(gate.control_qubits)
        target_set = set(gate.target_qubits)
        overlap = control_set & target_set
        if overlap:
            raise ValidationError(
                f"Line {gate.line}: Qubit(s) {overlap} appear in both control and target registers"
            )
    
    def _validate_measurement(self, node: MeasurementNode):
        """Validate measurement operation"""
        if node.qubit < 0 or node.qubit >= self.num_qubits:
            raise ValidationError(
                f"Line {node.line}: Qubit {node.qubit} out of range [0, {self.num_qubits-1}]"
            )
    
    def _validate_conditional(self, node: ConditionalNode):
        """Validate conditional operation"""
        # Recursively validate the inner operation
        self._validate_operation(node.operation)
    
    def _get_involved_qubits(self, operation: GateOperation) -> Set[int]:
        """Get all qubits involved in an operation"""
        if isinstance(operation, SingleQubitGate):
            return set(operation.qubits)
        elif isinstance(operation, TwoQubitGate):
            return {operation.control, operation.target}
        elif isinstance(operation, ThreeQubitGate):
            return {operation.control1, operation.control2, operation.target}
        elif isinstance(operation, ModularGate):
            return set(operation.control_qubits) | set(operation.target_qubits)
        elif isinstance(operation, MeasurementNode):
            return {operation.qubit}
        elif isinstance(operation, ConditionalNode):
            return self._get_involved_qubits(operation.operation)
        return set()


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == '__main__':
    from .parser import QLangParser
    
    parser = QLangParser()
    
    # Test 1: Valid Bell state
    print("Test 1: Valid Bell state")
    print("=" * 60)
    code1 ="""
H 0
CNOT 0-1
    """
    ast1 = parser.parse(code1)
    validator1 = QLangValidator(num_qubits=2)
    try:
        validator1.validate(ast1)
        print("✅ Validation passed!")
    except ValidationError as e:
        print(f"❌ Validation failed: {e}")
    print()
    
    # Test 2: Error - Qubit out of range
    print("Test 2: Error - Qubit out of range")
    print("=" * 60)
    code2 = "H 5"
    ast2 = parser.parse(code2)
    validator2 = QLangValidator(num_qubits=3)
    try:
        validator2.validate(ast2)
        print("✅ Validation passed!")
    except ValidationError as e:
        print(f"❌ Validation failed: {e}")
    print()
    
    # Test 3: Error - Same qubit used twice in time step
    print("Test 3: Error - Same qubit used twice")
    print("=" * 60)
    code3 = "H 0; X 0"
    ast3 = parser.parse(code3)
    validator3 = QLangValidator(num_qubits=3)
    try:
        validator3.validate(ast3)
        print("✅ Validation passed!")
    except ValidationError as e:
        print(f"❌ Validation failed: {e}")
    print()
    
    # Test 4: Error - Control = Target
    print("Test 4: Error - Control = Target")
    print("=" * 60)
    code4 = "CNOT 0-0"
    ast4 = parser.parse(code4)
    validator4 = QLangValidator(num_qubits=3)
    try:
        validator4.validate(ast4)
        print("✅ Validation passed!")
    except ValidationError as e:
        print(f"❌ Validation failed: {e}")
    print()
    
    # Test 5: Valid parallel operations
    print("Test 5: Valid parallel operations")
    print("=" * 60)
    code5 = "H 0, 2; X 1; CNOT 3-4"
    ast5 = parser.parse(code5)
    validator5 = QLangValidator(num_qubits=5)
    try:
        validator5.validate(ast5)
        print("✅ Validation passed!")
    except ValidationError as e:
        print(f"❌ Validation failed: {e}")
    print()
    
    # Test 6: Error - Missing parameter
    print("Test 6: Error - Missing parameter for Rx")
    print("=" * 60)
    try:
        code6 = "Rx 0"  # Should fail parsing already
        ast6 = parser.parse(code6)
    except Exception as e:
        print(f"❌ Parse error (expected): {e}")
    print()
    
    # Test 7: Complex valid circuit
    print("Test 7: Complex valid circuit")
    print("=" * 60)
    code7 = """
H 0, 2, 4; X 1, 3
CNOT 0-1; CNOT 2-3
Toffoli 0-1-2
    """
    ast7 = parser.parse(code7)
    validator7 = QLangValidator(num_qubits=5)
    try:
        validator7.validate(ast7)
        print("✅ Validation passed!")
    except ValidationError as e:
        print(f"❌ Validation failed: {e}")
    
    print("\n✅ All validator tests completed!")
