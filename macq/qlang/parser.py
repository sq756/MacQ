"""
Q-Lang Parser
Syntax analysis and AST construction for quantum circuit description language
"""

from dataclasses import dataclass
from typing import List, Optional, Union
from .tokenizer import Token, TokenType, QLangTokenizer


# ============================================================================
# AST Node Definitions
# ============================================================================

@dataclass
class ASTNode:
    """Base class for all AST nodes"""
    line: int
    column: int


@dataclass
class Parameter(ASTNode):
    """Parameter for parametric gates (e.g., π/4, 0.5)"""
    expression: str
    
    def __init__(self, expression: str, line: int = 0, column: int = 0):
        self.expression = expression
        self.line = line
        self.column = column
    
    def evaluate(self) -> float:
        """Evaluate parameter expression"""
        import math
        # Replace π with pi
        expr = self.expression.replace('π', str(math.pi))
        expr = expr.replace('pi', str(math.pi))
        try:
            return eval(expr)
        except Exception as e:
            raise ValueError(f"Invalid parameter expression '{self.expression}': {e}")


@dataclass
class MeasurementNode(ASTNode):
    """Measurement operation: measure qubit -> classical_bit"""
    qubit: int
    classical_bit: str  # Name of classical bit (e.g., "c0", "c1")
    
    def __init__(self, qubit: int, classical_bit: str, line: int = 0, column: int = 0):
        self.qubit = qubit
        self.classical_bit = classical_bit
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"measure {self.qubit} -> {self.classical_bit}"


@dataclass
class Condition(ASTNode):
    """Condition expression for classical control"""
    pass


@dataclass
class BitCondition(Condition):
    """Simple bit condition: c0 or c0 == 1 or c0 == 0"""
    bit_name: str
    expected_value: Optional[int] = None  # None means "if c0" (equivalent to c0 == 1)
    
    def __init__(self, bit_name: str, expected_value: Optional[int] = None, 
                 line: int = 0, column: int = 0):
        self.bit_name = bit_name
        self.expected_value = expected_value
        self.line = line
        self.column = column
    
    def __repr__(self):
        if self.expected_value is None:
            return f"{self.bit_name}"
        return f"{self.bit_name} == {self.expected_value}"


@dataclass
class AndCondition(Condition):
    """Logical AND of conditions"""
    left: Condition
    right: Condition
    
    def __init__(self, left: Condition, right: Condition, line: int = 0, column: int = 0):
        self.left = left
        self.right = right
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"({self.left} and {self.right})"


@dataclass
class OrCondition(Condition):
    """Logical OR of conditions"""
    left: Condition
    right: Condition
    
    def __init__(self, left: Condition, right: Condition, line: int = 0, column: int = 0):
        self.left = left
        self.right = right
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"({self.left} or {self.right})"


@dataclass
class ConditionalNode(ASTNode):
    """Conditional gate operation: if condition then operation"""
    condition: Condition
    operation: 'GateOperation'  # Forward reference
    
    def __init__(self, condition: Condition, operation: 'GateOperation', 
                 line: int = 0, column: int = 0):
        self.condition = condition
        self.operation = operation
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"if {self.condition} then {self.operation}"


@dataclass
class SingleQubitGate(ASTNode):
    """Single-qubit gate operation"""
    gate_name: str
    qubits: List[int]
    parameter: Optional[Parameter] = None
    
    def __init__(self, gate_name: str, qubits: List[int], parameter: Optional[Parameter] = None, 
                 line: int = 0, column: int = 0):
        self.gate_name = gate_name
        self.qubits = qubits
        self.parameter = parameter
        self.line = line
        self.column = column
    
    def __repr__(self):
        param_str = f"({self.parameter.expression})" if self.parameter else ""
        qubits_str = ", ".join(map(str, self.qubits))
        return f"{self.gate_name}{param_str} {qubits_str}"


@dataclass
class TwoQubitGate(ASTNode):
    """Two-qubit gate operation (CNOT, CZ, SWAP)"""
    gate_name: str
    control: int
    target: int
    
    def __init__(self, gate_name: str, control: int, target: int, line: int = 0, column: int = 0):
        self.gate_name = gate_name
        self.control = control
        self.target = target
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"{self.gate_name} {self.control}-{self.target}"


@dataclass
class ThreeQubitGate(ASTNode):
    """Three-qubit gate operation (Toffoli, CCZ)"""
    gate_name: str
    control1: int
    control2: int
    target: int
    
    def __init__(self, gate_name: str, control1: int, control2: int, target: int,
                 line: int = 0, column: int = 0):
        self.gate_name = gate_name
        self.control1 = control1
        self.control2 = control2
        self.target = target
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"{self.gate_name} {self.control1}-{self.control2}-{self.target}"


# Type alias for gate operations (including measurements and conditionals)
GateOperation = Union[SingleQubitGate, TwoQubitGate, ThreeQubitGate, MeasurementNode, ConditionalNode]


@dataclass
class TimeStep(ASTNode):
    """Represents a single time step with parallel operations"""
    operations: List[GateOperation]
    
    def __init__(self, operations: List[GateOperation], line: int = 0, column: int = 0):
        self.operations = operations
        self.line = line
        self.column = column
    
    def __repr__(self):
        ops_str = "; ".join(str(op) for op in self.operations)
        return f"TimeStep({ops_str})"


@dataclass
class Program(ASTNode):
    """Root node representing entire Q-Lang program"""
    time_steps: List[TimeStep]
    
    def __init__(self, time_steps: List[TimeStep], line: int = 0, column: int = 0):
        self.time_steps = time_steps
        self.line = line
        self.column = column
    
    def __repr__(self):
        steps_str = "\n".join(f"  {i}: {ts}" for i, ts in enumerate(self.time_steps))
        return f"Program(\n{steps_str}\n)"


# ============================================================================
# Parser Implementation
# ============================================================================

class QLangParser:
    """Parser for Q-Lang"""
    
    # Gates that require parameters
    PARAMETRIC_GATES = {'Rx', 'Ry', 'Rz'}
    
    # Multi-qubit gates
    TWO_QUBIT_GATES = {'CNOT', 'CZ', 'SWAP', 'CX'}
    THREE_QUBIT_GATES = {'Toffoli', 'CCZ', 'CCNOT'}
    
    def __init__(self):
        self.tokenizer = QLangTokenizer()
        self.tokens = []
        self.pos = 0
    
    def parse(self, code: str) -> Program:
        """
        Parse Q-Lang source code into AST
        
        Args:
            code: Q-Lang source code
            
        Returns:
            Program AST node
        """
        # Tokenize
        self.tokens = self.tokenizer.tokenize(code)
        self.tokens = self.tokenizer.filter_comments(self.tokens)
        self.pos = 0
        
        # Parse program
        time_steps = []
        
        while not self._is_eof():
            # Skip empty lines
            if self._current_token().type == TokenType.NEWLINE:
                self._advance()
                continue
            
            # Parse time step
            time_step = self._parse_time_step()
            if time_step.operations:  # Only add non-empty steps
                time_steps.append(time_step)
            
            # Expect newline or EOF
            if not self._is_eof():
                self._expect(TokenType.NEWLINE)
        
        return Program(time_steps, 0, 0)
    
    def _parse_time_step(self) -> TimeStep:
        """Parse a single time step (one line)"""
        operations = []
        line = self._current_token().line
        col = self._current_token().column
        
        while True:
            # Parse single operation
            op = self._parse_operation()
            operations.append(op)
            
            # Check for semicolon (parallel operation)
            if self._current_token().type == TokenType.SEMICOLON:
                self._advance()
                continue
            
            # End of time step
            break
        
        return TimeStep(operations, line, col)
    
    def _parse_operation(self) -> GateOperation:
        """Parse a single gate operation, measurement, or conditional"""
        current = self._current_token()
        
        # Check for conditional (if-then)
        if current.type == TokenType.IF:
            return self._parse_conditional()
        
        # Check for measurement
        if current.type == TokenType.MEASURE:
            return self._parse_measurement()
        
        # Otherwise parse gate
        gate_token = self._expect(TokenType.GATE_NAME)
        gate_name = gate_token.value
        line, col = gate_token.line, gate_token.column
        
        # Check for parameter (for Rx, Ry, Rz)
        parameter = None
        if gate_name in self.PARAMETRIC_GATES:
            param_token = self._expect(TokenType.PARAMETER)
            # Remove parentheses
            param_expr = param_token.value[1:-1]
            parameter = Parameter(param_expr, line, col)
        
        # Determine gate type
        if gate_name in self.THREE_QUBIT_GATES:
            return self._parse_three_qubit_gate(gate_name, line, col)
        elif gate_name in self.TWO_QUBIT_GATES:
            return self._parse_two_qubit_gate(gate_name, line, col)
        else:
            return self._parse_single_qubit_gate(gate_name, parameter, line, col)
    
    def _parse_measurement(self) -> MeasurementNode:
        """Parse measurement: measure qubit -> classical_bit"""
        measure_token = self._advance()  # consume 'measure'
        line, col = measure_token.line, measure_token.column
        
        # Parse qubit number
        qubit_token = self._expect(TokenType.NUMBER)
        qubit = int(qubit_token.value)
        
        # Expect arrow
        self._expect(TokenType.ARROW)
        
        # Parse classical bit name (lowercase identifier like "c0", "c1")
        cbit_token = self._current_token()
        if cbit_token.type == TokenType.IDENTIFIER:
            cbit_name = cbit_token.value
            self._advance()
        elif cbit_token.type == TokenType.GATE_NAME:
            # Accept uppercase too (like C0)
            cbit_name = cbit_token.value
            self._advance()
        else:
            raise SyntaxError(
                f"Line {cbit_token.line}:{cbit_token.column}: "
                f"Expected classical bit name after '->', got {cbit_token.type.name}"
            )
        
        return MeasurementNode(qubit, cbit_name, line, col)
    
    def _parse_conditional(self) -> ConditionalNode:
        """Parse conditional: if condition then operation"""
        if_token = self._advance()  # consume 'if'
        line, col = if_token.line, if_token.column
        
        # Parse condition
        condition = self._parse_condition()
        
        # Expect 'then'
        self._expect(TokenType.THEN)
        
        # Parse operation (recursively - can be any operation except another conditional)
        # Save current position to check if operation is another if
        saved_pos = self.pos
        current = self._current_token()
        
        if current.type == TokenType.IF:
            raise SyntaxError(
                f"Line {current.line}:{current.column}: "
                "Nested if-statements are not supported"
            )
        
        # Parse the operation
        operation = self._parse_operation()
        
        return ConditionalNode(condition, operation, line, col)
    
    def _parse_condition(self) -> Condition:
        """Parse condition expression"""
        # Parse primary condition
        left = self._parse_primary_condition()
        
        # Check for logical operators
        while True:
            current = self._current_token()
            
            if current.type == TokenType.AND:
                self._advance()
                right = self._parse_primary_condition()
                left = AndCondition(left, right, current.line, current.column)
            elif current.type == TokenType.OR:
                self._advance()
                right = self._parse_primary_condition()
                left = OrCondition(left, right, current.line, current.column)
            else:
                break
        
        return left
    
    def _parse_primary_condition(self) -> Condition:
        """Parse a primary condition (bit check)"""
        # Expect identifier (classical bit name)
        bit_token = self._current_token()
        
        if bit_token.type != TokenType.IDENTIFIER and bit_token.type != TokenType.GATE_NAME:
            raise SyntaxError(
                f"Line {bit_token.line}:{bit_token.column}: "
                f"Expected classical bit name, got {bit_token.type.name}"
            )
        
        bit_name = bit_token.value
        self._advance()
        
        # Check for '==' comparison
        if self._current_token().type == TokenType.EQUALS:
            self._advance()
            
            # Expect 0 or 1
            value_token = self._expect(TokenType.NUMBER)
            value = int(value_token.value)
            
            if value not in [0, 1]:
                raise ValueError(
                    f"Line {value_token.line}:{value_token.column}: "
                    f"Classical bit value must be 0 or 1, got {value}"
                )
            
            return BitCondition(bit_name, value, bit_token.line, bit_token.column)
        else:
            # Simple condition: "if c0" means "if c0 == 1"
            return BitCondition(bit_name, None, bit_token.line, bit_token.column)
    
    def _parse_single_qubit_gate(self, gate_name: str, parameter: Optional[Parameter],
                                   line: int, col: int) -> SingleQubitGate:
        """Parse single-qubit gate with qubit list"""
        qubits = []
        
        # Parse first qubit
        qubit_token = self._expect(TokenType.NUMBER)
        qubits.append(int(qubit_token.value))
        
        # Parse additional qubits (comma-separated)
        while self._current_token().type == TokenType.COMMA:
            self._advance()
            qubit_token = self._expect(TokenType.NUMBER)
            qubits.append(int(qubit_token.value))
        
        return SingleQubitGate(gate_name, qubits, parameter, line, col)
    
    def _parse_two_qubit_gate(self, gate_name: str, line: int, col: int) -> TwoQubitGate:
        """Parse two-qubit gate (control-target)"""
        control_token = self._expect(TokenType.NUMBER)
        control = int(control_token.value)
        
        self._expect(TokenType.DASH)
        
        target_token = self._expect(TokenType.NUMBER)
        target = int(target_token.value)
        
        return TwoQubitGate(gate_name, control, target, line, col)
    
    def _parse_three_qubit_gate(self, gate_name: str, line: int, col: int) -> ThreeQubitGate:
        """Parse three-qubit gate (control1-control2-target)"""
        control1_token = self._expect(TokenType.NUMBER)
        control1 = int(control1_token.value)
        
        self._expect(TokenType.DASH)
        
        control2_token = self._expect(TokenType.NUMBER)
        control2 = int(control2_token.value)
        
        self._expect(TokenType.DASH)
        
        target_token = self._expect(TokenType.NUMBER)
        target = int(target_token.value)
        
        return ThreeQubitGate(gate_name, control1, control2, target, line, col)
    
    # Helper methods
    def _current_token(self) -> Token:
        """Get current token"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF
    
    def _advance(self) -> Token:
        """Move to next token"""
        token = self._current_token()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token
    
    def _expect(self, token_type: TokenType) -> Token:
        """Expect specific token type"""
        token = self._current_token()
        if token.type != token_type:
            raise SyntaxError(
                f"Line {token.line}:{token.column}: "
                f"Expected {token_type.name}, got {token.type.name} ('{token.value}')"
            )
        return self._advance()
    
    def _is_eof(self) -> bool:
        """Check if at end of file"""
        return self._current_token().type == TokenType.EOF


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == '__main__':
    parser = QLangParser()
    
    # Test 1: Bell state
    print("Test 1: Bell state")
    print("=" * 60)
    code1 = """
    H 0
    CNOT 0-1
    """
    ast1 = parser.parse(code1)
    print(ast1)
    print()
    
    # Test 2: Parallel operations
    print("Test 2: Parallel operations")
    print("=" * 60)
    code2 = "H 0, 2; X 1; CNOT 0-1"
    ast2 = parser.parse(code2)
    print(ast2)
    print()
    
    # Test 3: GHZ state
    print("Test 3: GHZ state")
    print("=" * 60)
    code3 = """
    H 0
    CNOT 0-1
    CNOT 0-2
    """
    ast3 = parser.parse(code3)
    print(ast3)
    print()
    
    # Test 4: Parametric gates
    print("Test 4: Parametric rotation gates")
    print("=" * 60)
    code4 = """
    Rx(3.14159/2) 0
    Ry(π/4) 1
    Rz(0.785) 2
    """
    ast4 = parser.parse(code4)
    print(ast4)
    print()
    
    # Test 5: Complex circuit
    print("Test 5: Complex circuit")
    print("=" * 60)
    code5 = """
    # Initialize
    H 0, 2, 4; X 1, 3
    
    # Entangle
    CNOT 0-1; CNOT 2-3
    
    # Toffoli
    Toffoli 0-1-2
    """
    ast5 = parser.parse(code5)
    print(ast5)
