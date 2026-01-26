/**
 * MacQ: Mac-Native Quantum Computing Software
 * C Core Engine - Main Header File
 *
 * Copyright (c) 2026 MacQ Development Team
 * Licensed under MIT License
 */

#ifndef MACQ_H
#define MACQ_H

#include <complex.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// Type Definitions
// ============================================================================

/** Complex number type (C99 standard) */
typedef double complex cplx;

/** Quantum state structure */
typedef struct {
  int num_qubits;        /**< Number of qubits */
  size_t vector_size;    /**< State vector length (2^num_qubits) */
  cplx *state_vector;    /**< State vector |ψ⟩ */
  bool use_accelerate;   /**< Enable Accelerate framework SIMD */
  void *_aligned_buffer; /**< 16-byte aligned memory buffer */
  double norm;           /**< Cached norm value */
} QuantumState;

/** Quantum gate type enumeration */
typedef enum {
  GATE_I,    /**< Identity gate */
  GATE_X,    /**< Pauli-X (NOT) */
  GATE_Y,    /**< Pauli-Y */
  GATE_Z,    /**< Pauli-Z */
  GATE_H,    /**< Hadamard */
  GATE_S,    /**< S gate (√Z) */
  GATE_T,    /**< T gate (π/8) */
  GATE_SDG,  /**< S† (inverse S) */
  GATE_TDG,  /**< T† (inverse T) */
  GATE_RX,   /**< Rotation around X-axis */
  GATE_RY,   /**< Rotation around Y-axis */
  GATE_RZ,   /**< Rotation around Z-axis */
  GATE_CX,   /**< CNOT (Controlled-NOT) */
  GATE_CY,   /**< Controlled-Y */
  GATE_CZ,   /**< Controlled-Z */
  GATE_SWAP, /**< SWAP */
  GATE_CCX,  /**< Toffoli (CCNOT) */
  GATE_CSWAP /**< Fredkin (Controlled-SWAP) */
} GateType;

/** Quantum gate structure */
typedef struct {
  GateType type; /**< Gate type */
  int target;    /**< Target qubit index */
  int control;   /**< Control qubit index (-1 if none) */
  int control2;  /**< Second control qubit for Toffoli (-1 if none) */
  double angle;  /**< Rotation angle (for Rx/Ry/Rz) */
  double phase;  /**< Phase parameter */
} QuantumGate;

/** Error codes */
typedef enum {
  MACQ_SUCCESS = 0,
  MACQ_ERROR_INVALID_QUBITS = -1,
  MACQ_ERROR_OUT_OF_MEMORY = -2,
  MACQ_ERROR_INVALID_GATE = -3,
  MACQ_ERROR_INVALID_INDEX = -4,
  MACQ_ERROR_NULL_POINTER = -5
} MacQError;

// ============================================================================
// Core Quantum State Functions
// ============================================================================

/**
 * Create a quantum state with specified number of qubits.
 * Initializes to |0...0⟩ state.
 *
 * @param num_qubits Number of qubits (1-30 recommended)
 * @return Pointer to QuantumState, or NULL on error
 */
QuantumState *qstate_create(int num_qubits);

/**
 * Free quantum state memory.
 *
 * @param qs Pointer to QuantumState
 */
void qstate_free(QuantumState *qs);

/**
 * Clone (deep copy) a quantum state.
 *
 * @param qs Source quantum state
 * @return Cloned quantum state, or NULL on error
 */
QuantumState *qstate_clone(const QuantumState *qs);

/**
 * Initialize quantum state to a computational basis state.
 *
 * @param qs Quantum state
 * @param bitstring String like "01101" (LSB first)
 * @return Error code
 */
MacQError qstate_init_basis(QuantumState *qs, const char *bitstring);

/**
 * Compute the norm of the quantum state.
 *
 * @param qs Quantum state
 * @return Norm value (should be ~1.0 for normalized states)
 */
double qstate_norm(const QuantumState *qs);

/**
 * Normalize the quantum state to unit norm.
 *
 * @param qs Quantum state
 * @return Error code
 */
MacQError qstate_normalize(QuantumState *qs);

// ============================================================================
// Single-Qubit Gate Operations
// ============================================================================

/**
 * Apply Pauli-X (NOT) gate to target qubit.
 * Matrix: [[0, 1], [1, 0]]
 *
 * @param qs Quantum state
 * @param target Target qubit index
 * @return Error code
 */
MacQError qstate_apply_x(QuantumState *qs, int target);

/**
 * Apply Pauli-Y gate to target qubit.
 * Matrix: [[0, -i], [i, 0]]
 *
 * @param qs Quantum state
 * @param target Target qubit index
 * @return Error code
 */
MacQError qstate_apply_y(QuantumState *qs, int target);

/**
 * Apply Pauli-Z gate to target qubit.
 * Matrix: [[1, 0], [0, -1]]
 *
 * @param qs Quantum state
 * @param target Target qubit index
 * @return Error code
 */
MacQError qstate_apply_z(QuantumState *qs, int target);

/**
 * Apply Hadamard gate to target qubit.
 * Matrix: 1/√2 * [[1, 1], [1, -1]]
 *
 * @param qs Quantum state
 * @param target Target qubit index
 * @return Error code
 */
MacQError qstate_apply_h(QuantumState *qs, int target);

/**
 * Apply S gate (phase gate, √Z) to target qubit.
 * Matrix: [[1, 0], [0, i]]
 *
 * @param qs Quantum state
 * @param target Target qubit index
 * @return Error code
 */
MacQError qstate_apply_s(QuantumState *qs, int target);

/**
 * Apply T gate (π/8 gate) to target qubit.
 * Matrix: [[1, 0], [0, e^(iπ/4)]]
 *
 * @param qs Quantum state
 * @param target Target qubit index
 * @return Error code
 */
MacQError qstate_apply_t(QuantumState *qs, int target);

// ============================================================================
// Rotation Gates
// ============================================================================

/**
 * Apply rotation around X-axis.
 * Matrix: [[cos(θ/2), -i*sin(θ/2)], [-i*sin(θ/2), cos(θ/2)]]
 *
 * @param qs Quantum state
 * @param target Target qubit index
 * @param theta Rotation angle in radians
 * @return Error code
 */
MacQError qstate_apply_rx(QuantumState *qs, int target, double theta);

/**
 * Apply rotation around Y-axis.
 * Matrix: [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]]
 *
 * @param qs Quantum state
 * @param target Target qubit index
 * @param theta Rotation angle in radians
 * @return Error code
 */
MacQError qstate_apply_ry(QuantumState *qs, int target, double theta);

/**
 * Apply rotation around Z-axis.
 * Matrix: [[e^(-iθ/2), 0], [0, e^(iθ/2)]]
 *
 * @param qs Quantum state
 * @param target Target qubit index
 * @param theta Rotation angle in radians
 * @return Error code
 */
MacQError qstate_apply_rz(QuantumState *qs, int target, double theta);

// ============================================================================
// Two-Qubit Gates
// ============================================================================

/**
 * Apply CNOT (Controlled-NOT) gate.
 *
 * @param qs Quantum state
 * @param control Control qubit index
 * @param target Target qubit index
 * @return Error code
 */
MacQError qstate_apply_cnot(QuantumState *qs, int control, int target);

/**
 * Apply Controlled-Z gate.
 *
 * @param qs Quantum state
 * @param control Control qubit index
 * @param target Target qubit index
 * @return Error code
 */
MacQError qstate_apply_cz(QuantumState *qs, int control, int target);

/**
 * Apply SWAP gate.
 *
 * @param qs Quantum state
 * @param qubit1 First qubit index
 * @param qubit2 Second qubit index
 * @return Error code
 */
MacQError qstate_apply_swap(QuantumState *qs, int qubit1, int qubit2);

// ============================================================================
// Three-Qubit Gates
// ============================================================================

/**
 * Apply Toffoli (CCNOT, Controlled-Controlled-NOT) gate.
 *
 * @param qs Quantum state
 * @param control1 First control qubit
 * @param control2 Second control qubit
 * @param target Target qubit
 * @return Error code
 */
MacQError qstate_apply_toffoli(QuantumState *qs, int control1, int control2,
                               int target);

/**
 * Apply Quantum Fourier Transform to a register of qubits.
 *
 * @param qs Quantum state
 * @param num_qubits Number of qubits in register
 * @param qubits Array of qubit indices
 * @param inverse True if inverse QFT should be applied
 * @return Error code
 */
MacQError qstate_apply_qft(QuantumState *qs, int num_qubits, const int *qubits,
                           bool inverse);

/**
 * Apply Modular Exponentiation: |x⟩|y⟩ → |x⟩|y · a^x mod N⟩
 *
 * @param qs Quantum state
 * @param a Base (e.g. 7)
 * @param N Modulus (e.g. 15)
 * @param num_controls Number of control qubits (representing x)
 * @param controls Array of control qubit indices
 * @param num_targets Number of target qubits (representing y)
 * @param targets Array of target qubit indices
 * @return Error code
 */
MacQError qstate_apply_mod_exp(QuantumState *qs, int a, int N, int num_controls,
                               const int *controls, int num_targets,
                               const int *targets);

/**
 * Apply Controlled-Phase gate.
 *
 * @param qs Quantum state
 * @param control Control qubit index
 * @param target Target qubit index
 * @param phi Phase angle in radians
 * @return Error code
 */
MacQError qstate_apply_cp(QuantumState *qs, int control, int target,
                          double phi);

// ============================================================================
// Measurement
// ============================================================================

/**
 * Measure a single qubit, collapsing the state.
 *
 * @param qs Quantum state (will be modified)
 * @param qubit Qubit index to measure
 * @return Measurement result (0 or 1), or -1 on error
 */
int qstate_measure(QuantumState *qs, int qubit);

/**
 * Get probability of measuring qubit in |1⟩ state (non-destructive).
 *
 * @param qs Quantum state
 * @param qubit Qubit index
 * @return Probability value [0, 1], or -1.0 on error
 */
double qstate_probability(const QuantumState *qs, int qubit);

/**
 * Get probability of specific basis state |i⟩.
 *
 * @param qs Quantum state
 * @param basis_index Basis state index (0 to 2^n - 1)
 * @return Probability value [0, 1], or -1.0 on error
 */
double qstate_basis_probability(const QuantumState *qs, size_t basis_index);

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Get the amplitude of a specific basis state.
 *
 * @param qs Quantum state
 * @param basis_index Basis state index
 * @return Complex amplitude
 */
cplx qstate_get_amplitude(const QuantumState *qs, size_t basis_index);

/**
 * Set the amplitude of a specific basis state (for testing).
 *
 * @param qs Quantum state
 * @param basis_index Basis state index
 * @param amplitude Complex amplitude to set
 * @return Error code
 */
MacQError qstate_set_amplitude(QuantumState *qs, size_t basis_index,
                               cplx amplitude);

/**
 * Print quantum state information (for debugging).
 *
 * @param qs Quantum state
 */
void qstate_print_info(const QuantumState *qs);

/**
 * Get library version string.
 *
 * @return Version string (e.g., "MacQ v1.0.0")
 */
const char *macq_version(void);

#ifdef __cplusplus
}
#endif

#endif // MACQ_H
