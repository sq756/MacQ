"""
MacQ: Mac-Native Quantum Computing Software
Python Package Initialization

Copyright (c) 2026 MacQ Development Team
Licensed under MIT License
"""

from .c_bridge import (
    QuantumState,
    GateType,
    MacQError,
    version
)

__all__ = [
    'QuantumState',
    'GateType',
    'MacQError',
    'version'
]

__version__ = '1.0.0'
