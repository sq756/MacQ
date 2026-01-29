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
    DensityMatrix,
    version
)
from .core.circuit import Circuit

__all__ = [
    'QuantumState',
    'GateType',
    'MacQError',
    'DensityMatrix',
    'Circuit',
    'version'
]

__version__ = '1.2.0'
