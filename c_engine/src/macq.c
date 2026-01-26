/**
 * MacQ: Mac-Native Quantum Computing Software
 * C Core Engine - Core Implementation
 *
 * Copyright (c) 2026 MacQ Development Team
 * Licensed under MIT License
 */

#include "macq.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

#define MACQ_VERSION "1.0.0"
#define MAX_QUBITS 30 // Maximum recommended qubits for full state vector

// ============================================================================
// Helper Functions
// ============================================================================

static inline bool is_valid_qubit_index(const QuantumState *qs, int qubit) {
  return (qs != NULL && qubit >= 0 && qubit < qs->num_qubits);
}

static inline size_t get_index(int *qubits, int num_qubits) {
  size_t index = 0;
  for (int i = 0; i < num_qubits; i++) {
    if (qubits[i]) {
      index |= (1ULL << i);
    }
  }
  return index;
}

// ============================================================================
// Core Quantum State Functions
// ============================================================================

QuantumState *qstate_create(int num_qubits) {
  if (num_qubits < 1 || num_qubits > MAX_QUBITS) {
    fprintf(stderr, "Error: num_qubits must be between 1 and %d\n", MAX_QUBITS);
    return NULL;
  }

  QuantumState *qs = (QuantumState *)malloc(sizeof(QuantumState));
  if (!qs) {
    fprintf(stderr, "Error: Failed to allocate QuantumState\n");
    return NULL;
  }

  qs->num_qubits = num_qubits;
  qs->vector_size = 1ULL << num_qubits; // 2^num_qubits

// Allocate 16-byte aligned memory for SIMD optimization
#ifdef __APPLE__
  posix_memalign((void **)&qs->_aligned_buffer, 16,
                 qs->vector_size * sizeof(cplx));
#else
  qs->_aligned_buffer = aligned_alloc(16, qs->vector_size * sizeof(cplx));
#endif

  if (!qs->_aligned_buffer) {
    fprintf(stderr, "Error: Failed to allocate state vector\n");
    free(qs);
    return NULL;
  }

  qs->state_vector = (cplx *)qs->_aligned_buffer;

  // Initialize to |0...0⟩ state
  memset(qs->state_vector, 0, qs->vector_size * sizeof(cplx));
  qs->state_vector[0] = 1.0 + 0.0 * I;

  qs->use_accelerate = true;
  qs->norm = 1.0;

  return qs;
}

void qstate_free(QuantumState *qs) {
  if (qs) {
    if (qs->_aligned_buffer) {
      free(qs->_aligned_buffer);
    }
    free(qs);
  }
}

QuantumState *qstate_clone(const QuantumState *qs) {
  if (!qs)
    return NULL;

  QuantumState *new_qs = qstate_create(qs->num_qubits);
  if (new_qs) {
    memcpy(new_qs->state_vector, qs->state_vector,
           qs->vector_size * sizeof(cplx));
    new_qs->norm = qs->norm;
  }
  return new_qs;
}

MacQError qstate_init_basis(QuantumState *qs, const char *bitstring) {
  if (!qs || !bitstring)
    return MACQ_ERROR_NULL_POINTER;

  int len = (int)strlen(bitstring);
  if (len != qs->num_qubits) {
    fprintf(stderr, "Error: bitstring length (%d) != num_qubits (%d)\n", len,
            qs->num_qubits);
    return MACQ_ERROR_INVALID_INDEX;
  }

  // Clear state vector
  memset(qs->state_vector, 0, qs->vector_size * sizeof(cplx));

  // Calculate basis state index
  size_t index = 0;
  for (int i = 0; i < len; i++) {
    if (bitstring[i] == '1') {
      index |= (1ULL << i);
    } else if (bitstring[i] != '0') {
      fprintf(stderr, "Error: bitstring must contain only '0' or '1'\n");
      return MACQ_ERROR_INVALID_INDEX;
    }
  }

  // Set amplitude
  qs->state_vector[index] = 1.0 + 0.0 * I;
  qs->norm = 1.0;

  return MACQ_SUCCESS;
}

double qstate_norm(const QuantumState *qs) {
  if (!qs)
    return -1.0;

  double norm_squared = 0.0;
  for (size_t i = 0; i < qs->vector_size; i++) {
    cplx amp = qs->state_vector[i];
    norm_squared += creal(amp) * creal(amp) + cimag(amp) * cimag(amp);
  }

  return sqrt(norm_squared);
}

MacQError qstate_normalize(QuantumState *qs) {
  if (!qs)
    return MACQ_ERROR_NULL_POINTER;

  double norm = qstate_norm(qs);
  if (norm < 1e-10) {
    fprintf(stderr, "Error: Cannot normalize zero state\n");
    return MACQ_ERROR_INVALID_GATE;
  }

  for (size_t i = 0; i < qs->vector_size; i++) {
    qs->state_vector[i] /= norm;
  }

  qs->norm = 1.0;
  return MACQ_SUCCESS;
}

// ============================================================================
// Single-Qubit Gates
// ============================================================================

MacQError qstate_apply_x(QuantumState *qs, int target) {
  if (!is_valid_qubit_index(qs, target)) {
    return MACQ_ERROR_INVALID_INDEX;
  }

  size_t block_size = 1ULL << target;
  size_t num_blocks = qs->vector_size >> (target + 1);

  for (size_t block = 0; block < num_blocks; block++) {
    size_t base_idx = block * (block_size << 1);

    // Swap |0⟩ and |1⟩ components
    for (size_t i = 0; i < block_size; i++) {
      size_t idx0 = base_idx + i;
      size_t idx1 = idx0 + block_size;

      cplx temp = qs->state_vector[idx0];
      qs->state_vector[idx0] = qs->state_vector[idx1];
      qs->state_vector[idx1] = temp;
    }
  }

  return MACQ_SUCCESS;
}

MacQError qstate_apply_y(QuantumState *qs, int target) {
  if (!is_valid_qubit_index(qs, target)) {
    return MACQ_ERROR_INVALID_INDEX;
  }

  size_t block_size = 1ULL << target;
  size_t num_blocks = qs->vector_size >> (target + 1);

  for (size_t block = 0; block < num_blocks; block++) {
    size_t base_idx = block * (block_size << 1);

    // Y = [[0, -i], [i, 0]]
    for (size_t i = 0; i < block_size; i++) {
      size_t idx0 = base_idx + i;
      size_t idx1 = idx0 + block_size;

      cplx a0 = qs->state_vector[idx0];
      cplx a1 = qs->state_vector[idx1];

      qs->state_vector[idx0] = -I * a1;
      qs->state_vector[idx1] = I * a0;
    }
  }

  return MACQ_SUCCESS;
}

MacQError qstate_apply_z(QuantumState *qs, int target) {
  if (!is_valid_qubit_index(qs, target)) {
    return MACQ_ERROR_INVALID_INDEX;
  }

  size_t block_size = 1ULL << target;
  size_t num_blocks = qs->vector_size >> (target + 1);

  for (size_t block = 0; block < num_blocks; block++) {
    size_t base_idx = block * (block_size << 1);

    // Add -1 phase to |1⟩ component
    for (size_t i = 0; i < block_size; i++) {
      size_t idx1 = base_idx + i + block_size;
      qs->state_vector[idx1] = -qs->state_vector[idx1];
    }
  }

  return MACQ_SUCCESS;
}

MacQError qstate_apply_h(QuantumState *qs, int target) {
  if (!is_valid_qubit_index(qs, target)) {
    return MACQ_ERROR_INVALID_INDEX;
  }

  const double inv_sqrt2 = 1.0 / sqrt(2.0);
  size_t block_size = 1ULL << target;
  size_t num_blocks = qs->vector_size >> (target + 1);

  for (size_t block = 0; block < num_blocks; block++) {
    size_t base_idx = block * (block_size << 1);

    for (size_t i = 0; i < block_size; i++) {
      size_t idx0 = base_idx + i;
      size_t idx1 = idx0 + block_size;

      cplx a0 = qs->state_vector[idx0];
      cplx a1 = qs->state_vector[idx1];

      // H = 1/√2 * [[1, 1], [1, -1]]
      qs->state_vector[idx0] = inv_sqrt2 * (a0 + a1);
      qs->state_vector[idx1] = inv_sqrt2 * (a0 - a1);
    }
  }

  return MACQ_SUCCESS;
}

MacQError qstate_apply_s(QuantumState *qs, int target) {
  if (!is_valid_qubit_index(qs, target)) {
    return MACQ_ERROR_INVALID_INDEX;
  }

  size_t block_size = 1ULL << target;
  size_t num_blocks = qs->vector_size >> (target + 1);

  for (size_t block = 0; block < num_blocks; block++) {
    size_t base_idx = block * (block_size << 1);

    // Multiply |1⟩ component by i
    for (size_t i = 0; i < block_size; i++) {
      size_t idx1 = base_idx + i + block_size;
      qs->state_vector[idx1] *= I;
    }
  }

  return MACQ_SUCCESS;
}

MacQError qstate_apply_t(QuantumState *qs, int target) {
  if (!is_valid_qubit_index(qs, target)) {
    return MACQ_ERROR_INVALID_INDEX;
  }

  const cplx t_phase = cexp(I * M_PI / 4.0); // e^(iπ/4)
  size_t block_size = 1ULL << target;
  size_t num_blocks = qs->vector_size >> (target + 1);

  for (size_t block = 0; block < num_blocks; block++) {
    size_t base_idx = block * (block_size << 1);

    for (size_t i = 0; i < block_size; i++) {
      size_t idx1 = base_idx + i + block_size;
      qs->state_vector[idx1] *= t_phase;
    }
  }

  return MACQ_SUCCESS;
}

// ============================================================================
// Rotation Gates
// ============================================================================

MacQError qstate_apply_rx(QuantumState *qs, int target, double theta) {
  if (!is_valid_qubit_index(qs, target)) {
    return MACQ_ERROR_INVALID_INDEX;
  }

  double cos_half = cos(theta / 2.0);
  double sin_half = sin(theta / 2.0);
  cplx neg_i = -I;

  size_t block_size = 1ULL << target;
  size_t num_blocks = qs->vector_size >> (target + 1);

  for (size_t block = 0; block < num_blocks; block++) {
    size_t base_idx = block * (block_size << 1);

    for (size_t i = 0; i < block_size; i++) {
      size_t idx0 = base_idx + i;
      size_t idx1 = idx0 + block_size;

      cplx a0 = qs->state_vector[idx0];
      cplx a1 = qs->state_vector[idx1];

      // Rx = [[cos(θ/2), -i·sin(θ/2)], [-i·sin(θ/2), cos(θ/2)]]
      qs->state_vector[idx0] = cos_half * a0 + neg_i * sin_half * a1;
      qs->state_vector[idx1] = neg_i * sin_half * a0 + cos_half * a1;
    }
  }

  return MACQ_SUCCESS;
}

MacQError qstate_apply_ry(QuantumState *qs, int target, double theta) {
  if (!is_valid_qubit_index(qs, target)) {
    return MACQ_ERROR_INVALID_INDEX;
  }

  double cos_half = cos(theta / 2.0);
  double sin_half = sin(theta / 2.0);

  size_t block_size = 1ULL << target;
  size_t num_blocks = qs->vector_size >> (target + 1);

  for (size_t block = 0; block < num_blocks; block++) {
    size_t base_idx = block * (block_size << 1);

    for (size_t i = 0; i < block_size; i++) {
      size_t idx0 = base_idx + i;
      size_t idx1 = idx0 + block_size;

      cplx a0 = qs->state_vector[idx0];
      cplx a1 = qs->state_vector[idx1];

      // Ry = [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]]
      qs->state_vector[idx0] = cos_half * a0 - sin_half * a1;
      qs->state_vector[idx1] = sin_half * a0 + cos_half * a1;
    }
  }

  return MACQ_SUCCESS;
}

MacQError qstate_apply_rz(QuantumState *qs, int target, double theta) {
  if (!is_valid_qubit_index(qs, target)) {
    return MACQ_ERROR_INVALID_INDEX;
  }

  cplx phase_neg = cexp(-I * theta / 2.0);
  cplx phase_pos = cexp(I * theta / 2.0);

  size_t block_size = 1ULL << target;
  size_t num_blocks = qs->vector_size >> (target + 1);

  for (size_t block = 0; block < num_blocks; block++) {
    size_t base_idx = block * (block_size << 1);

    for (size_t i = 0; i < block_size; i++) {
      size_t idx0 = base_idx + i;
      size_t idx1 = idx0 + block_size;

      qs->state_vector[idx0] *= phase_neg;
      qs->state_vector[idx1] *= phase_pos;
    }
  }

  return MACQ_SUCCESS;
}

// ============================================================================
// Two-Qubit Gates
// ============================================================================

MacQError qstate_apply_cnot(QuantumState *qs, int control, int target) {
  if (!is_valid_qubit_index(qs, control) || !is_valid_qubit_index(qs, target)) {
    return MACQ_ERROR_INVALID_INDEX;
  }
  if (control == target) {
    return MACQ_ERROR_INVALID_GATE;
  }

  size_t mask_control = 1ULL << control;
  size_t mask_target = 1ULL << target;

  // Iterate through all states, flip target bit only when control is 1
  for (size_t i = 0; i < qs->vector_size; i++) {
    if (i & mask_control) {              // Control bit is 1
      size_t pair_idx = i ^ mask_target; // Flip target bit

      if (i < pair_idx) { // Avoid duplicate swaps
        cplx temp = qs->state_vector[i];
        qs->state_vector[i] = qs->state_vector[pair_idx];
        qs->state_vector[pair_idx] = temp;
      }
    }
  }

  return MACQ_SUCCESS;
}

MacQError qstate_apply_cz(QuantumState *qs, int control, int target) {
  if (!is_valid_qubit_index(qs, control) || !is_valid_qubit_index(qs, target)) {
    return MACQ_ERROR_INVALID_INDEX;
  }

  size_t mask_control = 1ULL << control;
  size_t mask_target = 1ULL << target;

  for (size_t i = 0; i < qs->vector_size; i++) {
    // Add -1 phase when both control and target bits are 1
    if ((i & mask_control) && (i & mask_target)) {
      qs->state_vector[i] = -qs->state_vector[i];
    }
  }

  return MACQ_SUCCESS;
}

MacQError qstate_apply_swap(QuantumState *qs, int qubit1, int qubit2) {
  if (!is_valid_qubit_index(qs, qubit1) || !is_valid_qubit_index(qs, qubit2)) {
    return MACQ_ERROR_INVALID_INDEX;
  }
  if (qubit1 == qubit2) {
    return MACQ_SUCCESS; // No-op
  }

  size_t mask1 = 1ULL << qubit1;
  size_t mask2 = 1ULL << qubit2;

  for (size_t i = 0; i < qs->vector_size; i++) {
    bool bit1 = (i & mask1) != 0;
    bool bit2 = (i & mask2) != 0;

    if (bit1 != bit2) { // Only swap when bits are different
      size_t pair_idx = i ^ mask1 ^ mask2;

      if (i < pair_idx) {
        cplx temp = qs->state_vector[i];
        qs->state_vector[i] = qs->state_vector[pair_idx];
        qs->state_vector[pair_idx] = temp;
      }
    }
  }

  return MACQ_SUCCESS;
}

// ============================================================================
// Three-Qubit Gates
// ============================================================================

MacQError qstate_apply_toffoli(QuantumState *qs, int control1, int control2,
                               int target) {
  if (!is_valid_qubit_index(qs, control1) ||
      !is_valid_qubit_index(qs, control2) ||
      !is_valid_qubit_index(qs, target)) {
    return MACQ_ERROR_INVALID_INDEX;
  }

  size_t mask_c1 = 1ULL << control1;
  size_t mask_c2 = 1ULL << control2;
  size_t mask_target = 1ULL << target;

  for (size_t i = 0; i < qs->vector_size; i++) {
    // Flip target bit only when both control bits are 1
    if ((i & mask_c1) && (i & mask_c2)) {
      size_t pair_idx = i ^ mask_target;

      if (i < pair_idx) {
        cplx temp = qs->state_vector[i];
        qs->state_vector[i] = qs->state_vector[pair_idx];
        qs->state_vector[pair_idx] = temp;
      }
    }
  }

  return MACQ_SUCCESS;
}

// ============================================================================
// Measurement
// ============================================================================

int qstate_measure(QuantumState *qs, int qubit) {
  if (!is_valid_qubit_index(qs, qubit)) {
    return -1;
  }

  // Calculate probability of measuring |1⟩
  double prob_0 = 0.0;
  double prob_1 = 0.0;

  size_t mask = 1ULL << qubit;
  for (size_t i = 0; i < qs->vector_size; i++) {
    double prob = creal(qs->state_vector[i]) * creal(qs->state_vector[i]) +
                  cimag(qs->state_vector[i]) * cimag(qs->state_vector[i]);

    if (i & mask) {
      prob_1 += prob;
    } else {
      prob_0 += prob;
    }
  }

  // Randomly choose outcome
  double rand_val = (double)rand() / RAND_MAX;
  int result = (rand_val < prob_0 / (prob_0 + prob_1)) ? 0 : 1;

  // Collapse state
  double norm_factor = (result == 0) ? sqrt(prob_0) : sqrt(prob_1);
  for (size_t i = 0; i < qs->vector_size; i++) {
    bool bit = (i & mask) != 0;
    if ((result == 1 && bit) || (result == 0 && !bit)) {
      qs->state_vector[i] /= norm_factor;
    } else {
      qs->state_vector[i] = 0.0;
    }
  }

  return result;
}

double qstate_probability(const QuantumState *qs, int qubit) {
  if (!is_valid_qubit_index(qs, qubit)) {
    return -1.0;
  }

  double prob_1 = 0.0;
  size_t mask = 1ULL << qubit;

  for (size_t i = 0; i < qs->vector_size; i++) {
    if (i & mask) {
      cplx amp = qs->state_vector[i];
      prob_1 += creal(amp) * creal(amp) + cimag(amp) * cimag(amp);
    }
  }

  return prob_1;
}

double qstate_basis_probability(const QuantumState *qs, size_t basis_index) {
  if (!qs || basis_index >= qs->vector_size) {
    return -1.0;
  }

  cplx amp = qs->state_vector[basis_index];
  return creal(amp) * creal(amp) + cimag(amp) * cimag(amp);
}

// ============================================================================
// Utility Functions
// ============================================================================

cplx qstate_get_amplitude(const QuantumState *qs, size_t basis_index) {
  if (!qs || basis_index >= qs->vector_size) {
    return 0.0;
  }
  return qs->state_vector[basis_index];
}

MacQError qstate_set_amplitude(QuantumState *qs, size_t basis_index,
                               cplx amplitude) {
  if (!qs || basis_index >= qs->vector_size) {
    return MACQ_ERROR_INVALID_INDEX;
  }
  qs->state_vector[basis_index] = amplitude;
  return MACQ_SUCCESS;
}

void qstate_print_info(const QuantumState *qs) {
  if (!qs) {
    printf("NULL quantum state\n");
    return;
  }

  printf("======================================\n");
  printf("Quantum State Information\n");
  printf("======================================\n");
  printf("Number of qubits: %d\n", qs->num_qubits);
  printf("Vector size: %zu (2^%d)\n", qs->vector_size, qs->num_qubits);
  printf("Norm: %.6f\n", qstate_norm(qs));
  printf("Memory: %.2f KB\n", qs->vector_size * sizeof(cplx) / 1024.0);
  printf("======================================\n");

  // Print non-zero amplitudes (limit to first 10)
  printf("Non-zero amplitudes (up to 10):\n");
  int count = 0;
  for (size_t i = 0; i < qs->vector_size && count < 10; i++) {
    cplx amp = qs->state_vector[i];
    double prob = creal(amp) * creal(amp) + cimag(amp) * cimag(amp);

    if (prob > 1e-10) {
      printf("|");
      for (int q = 0; q < qs->num_qubits; q++) {
        printf("%d", (int)((i >> q) & 1));
      }
      printf("⟩: %.6f%+.6fi (prob: %.4f%%)\n", creal(amp), cimag(amp),
             prob * 100.0);
      count++;
    }
  }
  printf("======================================\n");
}

const char *macq_version(void) { return "MacQ v" MACQ_VERSION; }
