"""
MacQ: Mac-Native Quantum Computing Software
Python Bridge to C Engine

Copyright (c) 2026 MacQ Development Team
Licensed under MIT License
"""

import ctypes
import os
import numpy as np
from typing import Optional, List, Tuple
from enum import IntEnum

# ============================================================================
# C Types and Structures
# ============================================================================

class GateType(IntEnum):
    """Quantum gate type enumeration (matching C enum)"""
    GATE_I = 0
    GATE_X = 1
    GATE_Y = 2
    GATE_Z = 3
    GATE_H = 4
    GATE_S = 5
    GATE_T = 6
    GATE_SDG = 7
    GATE_TDG = 8
    GATE_RX = 9
    GATE_RY = 10
    GATE_RZ = 11
    GATE_CX = 12
    GATE_CY = 13
    GATE_CZ = 14
    GATE_SWAP = 15
    GATE_CCX = 16
    GATE_CSWAP = 17

class MacQError(IntEnum):
    """Error codes (matching C enum)"""
    SUCCESS = 0
    ERROR_INVALID_QUBITS = -1
    ERROR_OUT_OF_MEMORY = -2
    ERROR_INVALID_GATE = -3
    ERROR_INVALID_INDEX = -4
    ERROR_NULL_POINTER = -5
    ERROR_DIMENSION_MISMATCH = -6

# ============================================================================
# Load C Library
# ============================================================================

def _find_library():
    """Find the compiled core library in the package or local directories"""
    module_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Extension names to look for
    lib_names = [
        'libmacq_core.dylib', # macOS
        'macq_core.dll',      # Windows
        'libmacq_core.so',    # Linux
        'libmacq.dylib',      # Legacy/Local
    ]
    
    # Directories to search
    search_dirs = [
        os.path.join(module_dir, 'core'),           # Package location (installed)
        os.path.join(module_dir, '..', 'c_engine'), # Development location
        module_dir,                                 # Current dir
    ]
    
    for d in search_dirs:
        for name in lib_names:
            path = os.path.join(d, name)
            if os.path.exists(path):
                return path
    
    raise FileNotFoundError(
        "Could not find MacQ core library. "
        "Please install the package with 'pip install .' or build the C engine manually."
    )

# Load the library
_lib_path = _find_library()
_lib = ctypes.CDLL(_lib_path)

# ============================================================================
# C Function Declarations
# ============================================================================

# Version
_lib.macq_version.restype = ctypes.c_char_p
_lib.macq_version.argtypes = []

# Core state functions
_lib.qstate_create.restype = ctypes.c_void_p
_lib.qstate_create.argtypes = [ctypes.c_int]

_lib.qstate_free.restype = None
_lib.qstate_free.argtypes = [ctypes.c_void_p]

_lib.qstate_clone.restype = ctypes.c_void_p
_lib.qstate_clone.argtypes = [ctypes.c_void_p]

_lib.qstate_init_basis.restype = ctypes.c_int
_lib.qstate_init_basis.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

_lib.qstate_norm.restype = ctypes.c_double
_lib.qstate_norm.argtypes = [ctypes.c_void_p]

_lib.qstate_normalize.restype = ctypes.c_int
_lib.qstate_normalize.argtypes = [ctypes.c_void_p]

# Single-qubit gates
_lib.qstate_apply_x.restype = ctypes.c_int
_lib.qstate_apply_x.argtypes = [ctypes.c_void_p, ctypes.c_int]

_lib.qstate_apply_y.restype = ctypes.c_int
_lib.qstate_apply_y.argtypes = [ctypes.c_void_p, ctypes.c_int]

_lib.qstate_apply_z.restype = ctypes.c_int
_lib.qstate_apply_z.argtypes = [ctypes.c_void_p, ctypes.c_int]

_lib.qstate_apply_h.restype = ctypes.c_int
_lib.qstate_apply_h.argtypes = [ctypes.c_void_p, ctypes.c_int]

_lib.qstate_apply_s.restype = ctypes.c_int
_lib.qstate_apply_s.argtypes = [ctypes.c_void_p, ctypes.c_int]

_lib.qstate_apply_t.restype = ctypes.c_int
_lib.qstate_apply_t.argtypes = [ctypes.c_void_p, ctypes.c_int]

# Rotation gates
_lib.qstate_apply_rx.restype = ctypes.c_int
_lib.qstate_apply_rx.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double]

_lib.qstate_apply_ry.restype = ctypes.c_int
_lib.qstate_apply_ry.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double]

_lib.qstate_apply_rz.restype = ctypes.c_int
_lib.qstate_apply_rz.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double]

# Two-qubit gates
_lib.qstate_apply_cnot.restype = ctypes.c_int
_lib.qstate_apply_cnot.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]

_lib.qstate_apply_cz.restype = ctypes.c_int
_lib.qstate_apply_cz.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]

_lib.qstate_apply_swap.restype = ctypes.c_int
_lib.qstate_apply_swap.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]

# Three-qubit gates
_lib.qstate_apply_toffoli.restype = ctypes.c_int
_lib.qstate_apply_toffoli.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]

# New v2.0 gates
_lib.qstate_apply_cp.restype = ctypes.c_int
_lib.qstate_apply_cp.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_double]

_lib.qstate_apply_qft.restype = ctypes.c_int
_lib.qstate_apply_qft.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_bool]

_lib.qstate_apply_mod_exp.restype = ctypes.c_int
_lib.qstate_apply_mod_exp.argtypes = [
    ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.POINTER(ctypes.c_int),
    ctypes.c_int, ctypes.POINTER(ctypes.c_int)
]

# Noise Channels
_lib.qstate_apply_amplitude_damping.restype = ctypes.c_int
_lib.qstate_apply_amplitude_damping.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double]

_lib.qstate_apply_phase_damping.restype = ctypes.c_int
_lib.qstate_apply_phase_damping.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double]

_lib.qstate_apply_depolarizing.restype = ctypes.c_int
_lib.qstate_apply_depolarizing.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double]

# Expectations
_lib.qstate_expectation_value.restype = ctypes.c_double
# Note: Simplified version, gates passed as array of QuantumGate objects
# We need to define QuantumGate structure first

# Measurement
_lib.qstate_measure.restype = ctypes.c_int
_lib.qstate_measure.argtypes = [ctypes.c_void_p, ctypes.c_int]

_lib.qstate_probability.restype = ctypes.c_double
_lib.qstate_probability.argtypes = [ctypes.c_void_p, ctypes.c_int]

_lib.qstate_basis_probability.restype = ctypes.c_double
_lib.qstate_basis_probability.argtypes = [ctypes.c_void_p, ctypes.c_size_t]

# Complex number structure for ctypes
class CComplex(ctypes.Structure):
    """C complex number compatible with C99 'double complex'"""
    _fields_ = [("real", ctypes.c_double), ("imag", ctypes.c_double)]
    
    def to_python(self):
        """Convert to Python complex"""
        return complex(self.real, self.imag)

class QuantumGateC(ctypes.Structure):
    """C quantum gate structure"""
    _fields_ = [
        ("type", ctypes.c_int),
        ("target", ctypes.c_int),
        ("control", ctypes.c_int),
        ("control2", ctypes.c_int),
        ("angle", ctypes.c_double),
        ("phase", ctypes.c_double)
    ]

_lib.qstate_expectation_value.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(QuantumGateC)]

# Density Matrix
class CDensityMatrix(ctypes.Structure):
    _fields_ = [
        ("num_qubits", ctypes.c_int),
        ("dim", ctypes.c_size_t),
        ("data", ctypes.POINTER(CComplex)),
        ("use_accelerate", ctypes.c_bool), # Wait, updated struct in macq.h didn't have this?
        ("_aligned_buffer", ctypes.c_void_p)
    ]

_lib.dmatrix_create.restype = ctypes.c_void_p
_lib.dmatrix_create.argtypes = [ctypes.c_int]

_lib.dmatrix_free.restype = None
_lib.dmatrix_free.argtypes = [ctypes.c_void_p]

_lib.dmatrix_from_qstate.restype = ctypes.c_void_p
_lib.dmatrix_from_qstate.argtypes = [ctypes.c_void_p]

_lib.dmatrix_partial_trace.restype = ctypes.c_int
_lib.dmatrix_partial_trace.argtypes = [
    ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_void_p)
]

_lib.dmatrix_export_data.restype = ctypes.c_int
_lib.dmatrix_export_data.argtypes = [
    ctypes.c_void_p, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)
]

# Utility
_lib.qstate_get_amplitude.restype = CComplex
_lib.qstate_get_amplitude.argtypes = [ctypes.c_void_p, ctypes.c_size_t]

_lib.qstate_set_amplitude.restype = ctypes.c_int
_lib.qstate_set_amplitude.argtypes = [ctypes.c_void_p, ctypes.c_size_t, CComplex]

# ============================================================================
# Python Wrapper Classes
# ============================================================================

class QuantumState:
    """
    Python wrapper for C QuantumState.
    
    Manages quantum state vector and provides high-level interface
    to C quantum operations.
    """
    
    def __init__(self, num_qubits: int):
        """
        Create a quantum state with specified number of qubits.
        
        Args:
            num_qubits: Number of qubits (1-30 recommended)
        
        Raises:
            ValueError: If num_qubits is invalid
            MemoryError: If unable to allocate state
        """
        if num_qubits < 1 or num_qubits > 30:
            raise ValueError(f"num_qubits must be between 1 and 30, got {num_qubits}")
        
        self._ptr = _lib.qstate_create(num_qubits)
        if not self._ptr:
            raise MemoryError(f"Failed to create quantum state with {num_qubits} qubits")
        
        self.num_qubits = num_qubits
        self.vector_size = 2 ** num_qubits
    
    def __del__(self):
        """Free C memory when Python object is destroyed"""
        if hasattr(self, '_ptr') and self._ptr:
            _lib.qstate_free(self._ptr)
            self._ptr = None
    
    def clone(self) -> 'QuantumState':
        """Create a deep copy of this quantum state"""
        new_state = QuantumState.__new__(QuantumState)
        new_state._ptr = _lib.qstate_clone(self._ptr)
        new_state.num_qubits = self.num_qubits
        new_state.vector_size = self.vector_size
        return new_state
    
    def init_basis(self, bitstring: str) -> None:
        """
        Initialize to a computational basis state.
        
        Args:
            bitstring: String of '0' and '1' (e.g., "0101")
                      Little-endian: bitstring[i] is qubit i
        """
        if len(bitstring) != self.num_qubits:
            raise ValueError(f"bitstring length must match num_qubits ({self.num_qubits})")
        
        err = _lib.qstate_init_basis(self._ptr, bitstring.encode())
        if err != MacQError.SUCCESS:
            raise RuntimeError(f"Failed to initialize basis state: error {err}")
    
    def norm(self) -> float:
        """Calculate the norm of the quantum state"""
        return _lib.qstate_norm(self._ptr)
    
    def normalize(self) -> None:
        """Normalize the quantum state to unit norm"""
        err = _lib.qstate_normalize(self._ptr)
        if err != MacQError.SUCCESS:
            raise RuntimeError(f"Failed to normalize state: error {err}")
    
    # Single-qubit gates
    def x(self, target: int) -> 'QuantumState':
        """Apply Pauli-X gate"""
        _lib.qstate_apply_x(self._ptr, target)
        return self
    
    def y(self, target: int) -> 'QuantumState':
        """Apply Pauli-Y gate"""
        _lib.qstate_apply_y(self._ptr, target)
        return self
    
    def z(self, target: int) -> 'QuantumState':
        """Apply Pauli-Z gate"""
        _lib.qstate_apply_z(self._ptr, target)
        return self
    
    def h(self, target: int) -> 'QuantumState':
        """Apply Hadamard gate"""
        _lib.qstate_apply_h(self._ptr, target)
        return self
    
    def s(self, target: int) -> 'QuantumState':
        """Apply S gate (phase gate)"""
        _lib.qstate_apply_s(self._ptr, target)
        return self
    
    def t(self, target: int) -> 'QuantumState':
        """Apply T gate (π/8 gate)"""
        _lib.qstate_apply_t(self._ptr, target)
        return self
    
    # Rotation gates
    def rx(self, target: int, theta: float) -> 'QuantumState':
        """Apply Rx(θ) rotation gate"""
        _lib.qstate_apply_rx(self._ptr, target, theta)
        return self
    
    def ry(self, target: int, theta: float) -> 'QuantumState':
        """Apply Ry(θ) rotation gate"""
        _lib.qstate_apply_ry(self._ptr, target, theta)
        return self
    
    def rz(self, target: int, theta: float) -> 'QuantumState':
        """Apply Rz(θ) rotation gate"""
        _lib.qstate_apply_rz(self._ptr, target, theta)
        return self
    
    # Two-qubit gates
    def cnot(self, control: int, target: int) -> 'QuantumState':
        """Apply CNOT (Controlled-NOT) gate"""
        _lib.qstate_apply_cnot(self._ptr, control, target)
        return self
    
    def cx(self, control: int, target: int) -> 'QuantumState':
        """Alias for cnot()"""
        return self.cnot(control, target)
    
    def cz(self, control: int, target: int) -> 'QuantumState':
        """Apply Controlled-Z gate"""
        _lib.qstate_apply_cz(self._ptr, control, target)
        return self
    
    def swap(self, qubit1: int, qubit2: int) -> 'QuantumState':
        """Apply SWAP gate"""
        _lib.qstate_apply_swap(self._ptr, qubit1, qubit2)
        return self
    
    # Three-qubit gates
    def toffoli(self, control1: int, control2: int, target: int) -> 'QuantumState':
        """Apply Toffoli (CCNOT) gate"""
        _lib.qstate_apply_toffoli(self._ptr, control1, control2, target)
        return self
    
    def ccx(self, control1: int, control2: int, target: int) -> 'QuantumState':
        """Alias for toffoli()"""
        return self.toffoli(control1, control2, target)
    
    # New v2.0 methods
    def cp(self, control: int, target: int, phi: float) -> 'QuantumState':
        """Apply Controlled-Phase gate"""
        _lib.qstate_apply_cp(self._ptr, control, target, phi)
        return self
        
    def qft(self, qubits: List[int], inverse: bool = False) -> 'QuantumState':
        """Apply Quantum Fourier Transform to a register of qubits"""
        num_qubits = len(qubits)
        q_array = (ctypes.c_int * num_qubits)(*qubits)
        _lib.qstate_apply_qft(self._ptr, num_qubits, q_array, inverse)
        return self
        
    def mod_exp(self, a: int, N: int, controls: List[int], targets: List[int]) -> 'QuantumState':
        """Apply Modular Exponentiation: |x⟩|y⟩ → |x⟩|y · a^x mod N⟩"""
        num_c = len(controls)
        num_t = len(targets)
        c_array = (ctypes.c_int * num_c)(*controls)
        t_array = (ctypes.c_int * num_t)(*targets)
        _lib.qstate_apply_mod_exp(self._ptr, a, N, num_c, c_array, num_t, t_array)
        return self
    
    # Measurement
    def measure(self, qubit: int) -> int:
        """
        Measure a qubit, collapsing the state.
        
        Args:
            qubit: Qubit index to measure
        
        Returns:
            Measurement result (0 or 1)
        """
        result = _lib.qstate_measure(self._ptr, qubit)
        if result < 0:
            raise ValueError(f"Invalid qubit index: {qubit}")
        return result
    
    def probability(self, qubit: int) -> float:
        """Get probability of measuring qubit in |1⟩ state"""
        return _lib.qstate_probability(self._ptr, qubit)
    
    def basis_probability(self, basis_index: int) -> float:
        """Get probability of specific basis state |i⟩"""
        return _lib.qstate_basis_probability(self._ptr, basis_index)
    
    def get_amplitude(self, basis_index: int) -> complex:
        """Get the complex amplitude of a basis state"""
        c_amp = _lib.qstate_get_amplitude(self._ptr, basis_index)
        return c_amp.to_python()
    
    def get_statevector(self) -> np.ndarray:
        """
        Get the full state vector as a NumPy array.
        
        Returns:
            Complex numpy array of shape (2^n,)
        """
        vec = np.zeros(self.vector_size, dtype=np.complex128)
        for i in range(self.vector_size):
            vec[i] = self.get_amplitude(i)
        return vec
    
    def probabilities(self) -> np.ndarray:
        """
        Get probabilities of all basis states.
        
        Returns:
            Real numpy array of shape (2^n,) with probabilities
        """
        vec = self.get_statevector()
        return np.abs(vec) ** 2

    def sample_counts(self, shots: int) -> dict:
        """
        Perform weighted random sampling based on current state probabilities.
        
        Args:
            shots: Number of measurement repetitions
            
        Returns:
            Dictionary mapping basis states (binary strings) to counts
        """
        if shots <= 0:
            return {}
            
        probs = self.probabilities()
        # Ensure probabilities sum to 1 (handling tiny precision errors)
        probs /= np.sum(probs)
        
        indices = np.arange(self.vector_size)
        samples = np.random.choice(indices, size=shots, p=probs)
        
        counts = {}
        for s in samples:
            bin_str = f"{s:0{self.num_qubits}b}"
            counts[bin_str] = counts.get(bin_str, 0) + 1
            
        return counts

    def __repr__(self) -> str:
        return f"QuantumState(num_qubits={self.num_qubits}, norm={self.norm():.6f})"
        
    # Noise methods
    def apply_amplitude_damping(self, target: int, rate: float) -> 'QuantumState':
        """Apply amplitude damping noise stochastic model"""
        _lib.qstate_apply_amplitude_damping(self._ptr, target, rate)
        return self
        
    def apply_phase_damping(self, target: int, rate: float) -> 'QuantumState':
        """Apply phase damping noise stochastic model"""
        _lib.qstate_apply_phase_damping(self._ptr, target, rate)
        return self
        
    def apply_depolarizing(self, target: int, rate: float) -> 'QuantumState':
        """Apply depolarizing noise stochastic model"""
        _lib.qstate_apply_depolarizing(self._ptr, target, rate)
        return self

    def expectation_value(self, gates: List[Tuple]) -> float:
        """Compute expectation value for a sequence of gates treated as an operator"""
        num_gates = len(gates)
        gates_array = (QuantumGateC * num_gates)()
        for i, g in enumerate(gates):
            # Tuples like (type, target, control, control2, angle, phase)
            gates_array[i].type = g[0]
            gates_array[i].target = g[1]
            gates_array[i].control = g[2] if len(g) > 2 else -1
            gates_array[i].control2 = g[3] if len(g) > 3 else -1
            gates_array[i].angle = g[4] if len(g) > 4 else 0.0
            gates_array[i].phase = g[5] if len(g) > 5 else 0.0
        return _lib.qstate_expectation_value(self._ptr, num_gates, gates_array)

class DensityMatrix:
    """Python wrapper for C DensityMatrix"""
    
    def __init__(self, num_qubits: int):
        self._ptr = _lib.dmatrix_create(num_qubits)
        if not self._ptr:
            raise MemoryError("Failed to create density matrix")
        self.num_qubits = num_qubits
        self.dim = 2 ** num_qubits
        
    def __del__(self):
        if hasattr(self, '_ptr') and self._ptr:
            _lib.dmatrix_free(self._ptr)
            
    @classmethod
    def from_statevector(cls, qs: QuantumState) -> 'DensityMatrix':
        dm = cls.__new__(cls)
        dm._ptr = _lib.dmatrix_from_qstate(qs._ptr)
        dm.num_qubits = qs.num_qubits
        dm.dim = qs.vector_size
        return dm
        
    def partial_trace(self, qubits_to_trace: List[int]) -> 'DensityMatrix':
        num_trace = len(qubits_to_trace)
        q_array = (ctypes.c_int * num_trace)(*qubits_to_trace)
        dst_ptr = ctypes.c_void_p()
        err = _lib.dmatrix_partial_trace(self._ptr, num_trace, q_array, ctypes.byref(dst_ptr))
        if err != MacQError.SUCCESS:
            raise RuntimeError(f"Partial trace failed with error {err}")
            
        new_dm = DensityMatrix.__new__(DensityMatrix)
        new_dm._ptr = dst_ptr
        new_dm.num_qubits = self.num_qubits - num_trace
        new_dm.dim = 2 ** new_dm.num_qubits
        return new_dm
        
    def to_numpy(self) -> np.ndarray:
        """Export to 2D numpy array"""
        real = np.zeros(self.dim * self.dim, dtype=np.float64)
        imag = np.zeros(self.dim * self.dim, dtype=np.float64)
        _lib.dmatrix_export_data(self._ptr, 
                                 real.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                 imag.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
        return (real + 1j * imag).reshape((self.dim, self.dim))


def version() -> str:
    """Get MacQ library version"""
    return _lib.macq_version().decode('utf-8')
