"""
MacQ Oracle Builder
Compiles high-level boolean expressions into quantum circuits.
"""

import ast
from typing import List, Dict, Any

class ExpressionToGates:
    """
    Translates a boolean expression into a sequence of X and MCX gates.
    Uses a truth-table expansion (Sum of Products style).
    """
    def __init__(self, expression: str, inputs: List[str], target: str):
        self.expression = expression
        self.inputs = inputs
        self.target = target
        self.gates = []

    def compile(self):
        """
        Evaluate the expression for all 2^n inputs and generate MCX gates for minterms.
        """
        n = len(self.inputs)
        for i in range(2**n):
            # Map inputs to bits
            bits = [(i >> (n - 1 - j)) & 1 for j in range(n)]
            scope = {name: bit for name, bit in zip(self.inputs, bits)}
            
            # Evaluate expression safely
            try:
                # Replace logical operators with bitwise ones if not already
                expr = self.expression.replace(' and ', ' & ').replace(' or ', ' | ').replace(' not ', ' ~ ')
                result = eval(expr, {"__builtins__": None}, scope)
                
                if result & 1:
                    # Found a minterm!
                    # Add X gates for '0' controls
                    controls = []
                    for name, bit in scope.items():
                        if bit == 0:
                            self.gates.append({"type": "X", "qubits": [name]})
                        controls.append(name)
                    
                    # Add Multi-Controlled X (MCX)
                    self.gates.append({"type": "MCX", "controls": controls, "target": self.target})
                    
                    # Clean up: Add X gates back for '0' controls
                    for name, bit in scope.items():
                        if bit == 0:
                            self.gates.append({"type": "X", "qubits": [name]})
                            
            except Exception as e:
                print(f"Error evaluating expression: {e}")
                continue
        
        return self.gates

class OracleBuilder:
    @staticmethod
    def build_from_expression(expression: str, inputs: List[str], target: str) -> List[Dict[str, Any]]:
        compiler = ExpressionToGates(expression, inputs, target)
        return compiler.compile()
