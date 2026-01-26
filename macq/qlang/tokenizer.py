"""
Q-Lang Tokenizer
Lexical analysis for quantum circuit description language
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """Token types for Q-Lang"""
    # Literals
    GATE_NAME = auto()      # H, X, CNOT, etc.
    IDENTIFIER = auto()     # c0, c1, etc. (lowercase identifiers)
    NUMBER = auto()         # 0, 1, 2, etc.
    PARAMETER = auto()      # (π/4), (0.5), etc.
    
    # Operators
    SEMICOLON = auto()      # ;
    COMMA = auto()          # ,
    DASH = auto()           # -
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    ARROW = auto()          # ->
    
    # Keywords
    MEASURE = auto()        # measure
    IF = auto()             # if
    THEN = auto()           # then
    AND = auto()            # and
    OR = auto()             # or
    NOT = auto()            # not
    EQUALS = auto()         # ==
    
    # Special
    COMMENT = auto()        # # ...
    NEWLINE = auto()        # \n
    EOF = auto()            # End of file
    
    # Errors
    INVALID = auto()


@dataclass
class Token:
    """Represents a single token"""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', L{self.line}:C{self.column})"


class QLangTokenizer:
    """Tokenizer for Q-Lang"""
    
    # Token patterns (order matters for matching)
    TOKEN_PATTERNS = [
        (TokenType.COMMENT, r'#[^\n]*'),
        # Keywords - must be before identifiers
        (TokenType.MEASURE, r'\bmeasure\b'),
        (TokenType.IF, r'\bif\b'),
        (TokenType.THEN, r'\bthen\b'),
        (TokenType.AND, r'\band\b'),
        (TokenType.OR, r'\bor\b'),
        (TokenType.NOT, r'\bnot\b'),
        (TokenType.GATE_NAME, r'[A-Z][A-Za-z0-9_†]*'),  # Allow underscores for MOD_EXP
        (TokenType.IDENTIFIER, r'[a-z][a-z0-9_]*'),  # Lowercase identifiers for classical bits
        (TokenType.NUMBER, r'\d+'),
        (TokenType.PARAMETER, r'\([^)]+\)'),
        (TokenType.EQUALS, r'=='),  # Must be before other operators
        (TokenType.ARROW, r'->'),  # Must be before DASH
        (TokenType.SEMICOLON, r';'),
        (TokenType.COMMA, r','),
        (TokenType.DASH, r'-'),
        (TokenType.LPAREN, r'\('),
        (TokenType.RPAREN, r'\)'),
        (TokenType.NEWLINE, r'\n'),
    ]
    
    # Valid gate names
    ALLOWED_GATES = {
        'H', 'X', 'Y', 'Z', 'S', 'T', 'S†', 'T†',  # Single qubit
        'Rx', 'Ry', 'Rz',  # Parametric
        'CNOT', 'CX', 'CZ', 'SWAP',  # Two qubit
        'Toffoli', 'CCNOT', 'CCZ',  # Three qubit
        'MOD_EXP', 'MOD_ADD', 'MOD_MUL',  # Modular arithmetic (v2.0)
    }
    
    def __init__(self):
        # Compile regex patterns
        self.pattern = '|'.join(f'(?P<{t.name}>{p})' for t, p in self.TOKEN_PATTERNS)
        self.regex = re.compile(self.pattern)
    
    def tokenize(self, code: str) -> List[Token]:
        """
        Tokenize Q-Lang source code
        
        Args:
            code: Q-Lang source code string
            
        Returns:
            List of tokens
            
        Raises:
            SyntaxError: If invalid token encountered
        """
        tokens = []
        line = 1
        line_start = 0
        
        for match in self.regex.finditer(code):
            token_type = TokenType[match.lastgroup]
            value = match.group()
            column = match.start() - line_start + 1
            
            # Skip whitespace (spaces, tabs)
            if value.isspace() and token_type != TokenType.NEWLINE:
                continue
            
            # Validate gate names
            if token_type == TokenType.GATE_NAME:
                if value not in self.ALLOWED_GATES:
                    raise SyntaxError(
                        f"Line {line}:{column}: Unknown gate '{value}'"
                    )
            
            # Create token
            token = Token(token_type, value, line, column)
            tokens.append(token)
            
            # Track line numbers
            if token_type == TokenType.NEWLINE:
                line += 1
                line_start = match.end()
        
        # Check for unmatched characters
        total_matched = sum(len(t.value) for t in tokens if t.type != TokenType.NEWLINE)
        code_no_whitespace = re.sub(r'[ \t]+', '', code)
        code_no_newlines = code_no_whitespace.replace('\n', '')
        
        if total_matched < len(code_no_newlines):
            # Find first unmatched character
            pos = 0
            for token in tokens:
                pos += len(token.value)
            
            if pos < len(code):
                line_num = code[:pos].count('\n') + 1
                raise SyntaxError(
                    f"Line {line_num}: Invalid character '{code[pos]}'"
                )
        
        # Add EOF token
        tokens.append(Token(TokenType.EOF, '', line, 0))
        
        return tokens
    
    def filter_comments(self, tokens: List[Token]) -> List[Token]:
        """Remove comment tokens"""
        return [t for t in tokens if t.type != TokenType.COMMENT]
    
    def filter_newlines(self, tokens: List[Token]) -> List[Token]:
        """Remove unnecessary newlines (keep only significant ones)"""
        result = []
        prev_was_newline = False
        
        for token in tokens:
            if token.type == TokenType.NEWLINE:
                # Only keep if not preceded by another newline
                if not prev_was_newline and result:
                    result.append(token)
                prev_was_newline = True
            else:
                result.append(token)
                prev_was_newline = False
        
        return result


# Example usage
if __name__ == '__main__':
    tokenizer = QLangTokenizer()
    
    # Test case 1: Simple Bell state
    code1 = """
    # Bell state preparation
    H 0
    CNOT 0-1
    """
    
    print("Test 1: Bell state")
    print("=" * 50)
    tokens = tokenizer.tokenize(code1)
    tokens = tokenizer.filter_comments(tokens)
    tokens = tokenizer.filter_newlines(tokens)
    
    for token in tokens:
        print(token)
    print()
    
    # Test case 2: Parallel operations
    code2 = "H 0, 2; X 1; CNOT 0-1"
    
    print("Test 2: Parallel operations")
    print("=" * 50)
    tokens = tokenizer.tokenize(code2)
    for token in tokens:
        print(token)
    print()
    
    # Test case 3: Error - invalid gate
    try:
        code3 = "INVALID 0"
        tokenizer.tokenize(code3)
    except SyntaxError as e:
        print("Test 3: Error handling")
        print("=" * 50)
        print(f"Caught expected error: {e}")
