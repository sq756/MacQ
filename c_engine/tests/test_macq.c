/**
 * MacQ C Engine Test Suite
 * Copyright (c) 2026 MacQ Development Team
 */

#include "../include/macq.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define EPSILON 1e-6
#define TEST_ASSERT(condition, message)                                        \
  do {                                                                         \
    if (!(condition)) {                                                        \
      fprintf(stderr, "✗ FAIL: %s\n   at %s:%d\n", message, __FILE__,          \
              __LINE__);                                                       \
      return 0;                                                                \
    }                                                                          \
  } while (0)

#define RUN_TEST(test_func)                                                    \
  do {                                                                         \
    printf("Running %s...\n", #test_func);                                     \
    if (test_func()) {                                                         \
      printf("✓ PASS: %s\n\n", #test_func);                                    \
      tests_passed++;                                                          \
    } else {                                                                   \
      printf("✗ FAIL: %s\n\n", #test_func);                                    \
      tests_failed++;                                                          \
    }                                                                          \
    tests_total++;                                                             \
  } while (0)

// Test statistics
static int tests_total = 0;
static int tests_passed = 0;
static int tests_failed = 0;

// ============================================================================
// Helper Functions
// ============================================================================

static int is_close(double a, double b, double epsilon) {
  return fabs(a - b) < epsilon;
}

static int is_cplx_close(cplx a, cplx b, double epsilon) {
  return is_close(creal(a), creal(b), epsilon) &&
         is_close(cimag(a), cimag(b), epsilon);
}

// ============================================================================
// Test Cases
// ============================================================================

int test_version() {
  const char *version = macq_version();
  TEST_ASSERT(version != NULL, "Version string should not be NULL");
  printf("  MacQ version: %s\n", version);
  return 1;
}

int test_create_and_free() {
  QuantumState *qs = qstate_create(3);
  TEST_ASSERT(qs != NULL, "Failed to create quantum state");
  TEST_ASSERT(qs->num_qubits == 3, "Wrong number of qubits");
  TEST_ASSERT(qs->vector_size == 8, "Wrong vector size");

  // Should be initialized to |000⟩
  cplx amp0 = qstate_get_amplitude(qs, 0);
  TEST_ASSERT(is_cplx_close(amp0, 1.0 + 0.0 * I, EPSILON),
              "|000⟩ amplitude should be 1");

  cplx amp1 = qstate_get_amplitude(qs, 1);
  TEST_ASSERT(is_cplx_close(amp1, 0.0 + 0.0 * I, EPSILON),
              "|001⟩ amplitude should be 0");

  qstate_free(qs);
  return 1;
}

int test_basis_initialization() {
  QuantumState *qs = qstate_create(4);
  TEST_ASSERT(qs != NULL, "Failed to create quantum state");

  // Initialize to |1010⟩ (bitstring "0101" means q0=0, q1=1, q2=0, q3=1)
  // This gives index = 0 + 2 + 0 + 8 = 10
  MacQError err = qstate_init_basis(qs, "0101");
  TEST_ASSERT(err == MACQ_SUCCESS, "Failed to initialize basis state");

  cplx amp = qstate_get_amplitude(qs, 10);
  TEST_ASSERT(is_cplx_close(amp, 1.0 + 0.0 * I, EPSILON),
              "|0101⟩ amplitude should be 1");

  qstate_free(qs);
  return 1;
}

int test_pauli_x_gate() {
  QuantumState *qs = qstate_create(1);

  // Apply X gate: |0⟩ → |1⟩
  qstate_apply_x(qs, 0);

  cplx amp0 = qstate_get_amplitude(qs, 0);
  cplx amp1 = qstate_get_amplitude(qs, 1);

  TEST_ASSERT(is_cplx_close(amp0, 0.0, EPSILON), "|0⟩ amplitude should be 0");
  TEST_ASSERT(is_cplx_close(amp1, 1.0, EPSILON), "|1⟩ amplitude should be 1");

  // Apply X again: |1⟩ → |0⟩
  qstate_apply_x(qs, 0);

  amp0 = qstate_get_amplitude(qs, 0);
  amp1 = qstate_get_amplitude(qs, 1);

  TEST_ASSERT(is_cplx_close(amp0, 1.0, EPSILON), "|0⟩ amplitude should be 1");
  TEST_ASSERT(is_cplx_close(amp1, 0.0, EPSILON), "|1⟩ amplitude should be 0");

  qstate_free(qs);
  return 1;
}

int test_hadamard_gate() {
  QuantumState *qs = qstate_create(1);

  // Apply H gate: |0⟩ → (|0⟩ + |1⟩)/√2
  qstate_apply_h(qs, 0);

  double expected = 1.0 / sqrt(2.0);
  cplx amp0 = qstate_get_amplitude(qs, 0);
  cplx amp1 = qstate_get_amplitude(qs, 1);

  TEST_ASSERT(is_close(creal(amp0), expected, EPSILON),
              "|0⟩ amplitude real part should be 1/√2");
  TEST_ASSERT(is_close(creal(amp1), expected, EPSILON),
              "|1⟩ amplitude real part should be 1/√2");

  // Probabilities should be 50-50
  double prob0 = qstate_basis_probability(qs, 0);
  double prob1 = qstate_basis_probability(qs, 1);

  TEST_ASSERT(is_close(prob0, 0.5, EPSILON), "|0⟩ probability should be 0.5");
  TEST_ASSERT(is_close(prob1, 0.5, EPSILON), "|1⟩ probability should be 0.5");

  qstate_free(qs);
  return 1;
}

int test_cnot_gate() {
  QuantumState *qs = qstate_create(2);

  // Test 1: |00⟩ + CNOT → |00⟩
  qstate_apply_cnot(qs, 0, 1);
  cplx amp = qstate_get_amplitude(qs, 0); // |00⟩
  TEST_ASSERT(is_cplx_close(amp, 1.0, EPSILON), "|00⟩ should remain |00⟩");

  // Test 2: |10⟩ + CNOT(0,1) → |11⟩
  // "01" means q0=0, q1=1, so this is |01⟩ = index 2, not |10⟩
  // After CNOT with control=0 (which is 0), target unchanged → still |01⟩
  // Let's test |10⟩ correctly: "10" → q0=1, q1=0, index=1
  qstate_init_basis(qs, "10"); // q0=1, q1=0 → |10⟩ = index 1
  qstate_apply_cnot(qs, 0, 1); // control q0=1, flip q1 → |11⟩ = index 3
  amp = qstate_get_amplitude(qs, 3); // |11⟩
  TEST_ASSERT(is_cplx_close(amp, 1.0, EPSILON), "|10⟩ should become |11⟩");

  qstate_free(qs);
  return 1;
}

int test_bell_state() {
  QuantumState *qs = qstate_create(2);

  // Create Bell state: H⊗I then CNOT
  qstate_apply_h(qs, 0);
  qstate_apply_cnot(qs, 0, 1);

  // Should be (|00⟩ + |11⟩)/√2
  double expected = 1.0 / sqrt(2.0);

  cplx amp00 = qstate_get_amplitude(qs, 0); // |00⟩
  cplx amp11 = qstate_get_amplitude(qs, 3); // |11⟩

  TEST_ASSERT(is_close(creal(amp00), expected, EPSILON),
              "|00⟩ amplitude should be 1/√2");
  TEST_ASSERT(is_close(creal(amp11), expected, EPSILON),
              "|11⟩ amplitude should be 1/√2");

  // |01⟩ and |10⟩ should be zero
  cplx amp01 = qstate_get_amplitude(qs, 1);
  cplx amp10 = qstate_get_amplitude(qs, 2);

  TEST_ASSERT(is_cplx_close(amp01, 0.0, EPSILON), "|01⟩ amplitude should be 0");
  TEST_ASSERT(is_cplx_close(amp10, 0.0, EPSILON), "|10⟩ amplitude should be 0");

  qstate_free(qs);
  return 1;
}

int test_rotation_gates() {
  QuantumState *qs = qstate_create(1);

  // Rx(π): should flip |0⟩ to |1⟩ (with phase)
  qstate_apply_rx(qs, 0, M_PI);
  cplx amp1 = qstate_get_amplitude(qs, 1);
  TEST_ASSERT(is_close(cabs(amp1), 1.0, EPSILON), "Rx(π) should rotate to |1⟩");

  // Ry(π/2): creates equal superposition
  qstate_init_basis(qs, "0");
  qstate_apply_ry(qs, 0, M_PI / 2.0);
  double prob0 = qstate_basis_probability(qs, 0);
  double prob1 = qstate_basis_probability(qs, 1);
  TEST_ASSERT(is_close(prob0, 0.5, EPSILON),
              "Ry(π/2) should create 50-50 superposition");
  TEST_ASSERT(is_close(prob1, 0.5, EPSILON),
              "Ry(π/2) should create 50-50 superposition");

  qstate_free(qs);
  return 1;
}

int test_toffoli_gate() {
  QuantumState *qs = qstate_create(3);

  // |110⟩ + Toffoli → |111⟩
  // "110" means q0=1, q1=1, q2=0 → index = 1 + 2 + 0 = 3
  qstate_init_basis(qs, "110"); // q0=1, q1=1, q2=0 → |110⟩ = index 3
  qstate_apply_toffoli(qs, 0, 1,
                       2); // both controls (q0,q1) are 1, flip q2 → |111⟩

  cplx amp = qstate_get_amplitude(qs, 7); // |111⟩ = index 7
  TEST_ASSERT(is_cplx_close(amp, 1.0, EPSILON),
              "Toffoli should flip target when both controls are 1");

  // |010⟩ + Toffoli → |010⟩ (no change)
  qstate_init_basis(qs, "010");
  qstate_apply_toffoli(qs, 0, 1, 2);
  amp = qstate_get_amplitude(qs, 2); // |010⟩
  TEST_ASSERT(is_cplx_close(amp, 1.0, EPSILON),
              "Toffoli should not change when control bits are not both 1");

  qstate_free(qs);
  return 1;
}

int test_normalization() {
  QuantumState *qs = qstate_create(2);

  // Manually set unnormalized state
  qstate_set_amplitude(qs, 0, 2.0);
  qstate_set_amplitude(qs, 1, 2.0);

  double norm_before = qstate_norm(qs);
  TEST_ASSERT(is_close(norm_before, sqrt(8.0), EPSILON),
              "Norm should be sqrt(8) before normalization");

  qstate_normalize(qs);
  double norm_after = qstate_norm(qs);
  TEST_ASSERT(is_close(norm_after, 1.0, EPSILON),
              "Norm should be 1.0 after normalization");

  qstate_free(qs);
  return 1;
}

int test_measurement() {
  srand(time(NULL));

  QuantumState *qs = qstate_create(1);
  qstate_apply_h(qs, 0); // Create equal superposition

  // Measure many times, should get roughly 50-50
  int counts[2] = {0, 0};
  const int num_shots = 1000;

  for (int i = 0; i < num_shots; i++) {
    QuantumState *test_qs = qstate_clone(qs);
    int result = qstate_measure(test_qs, 0);
    TEST_ASSERT(result == 0 || result == 1, "Measurement should return 0 or 1");
    counts[result]++;
    qstate_free(test_qs);
  }

  double ratio = (double)counts[0] / num_shots;
  TEST_ASSERT(ratio > 0.4 && ratio < 0.6,
              "Equal superposition should give ~50% each outcome");

  printf("  Measurement statistics: |0⟩: %d (%.1f%%), |1⟩: %d (%.1f%%)\n",
         counts[0], counts[0] * 100.0 / num_shots, counts[1],
         counts[1] * 100.0 / num_shots);

  qstate_free(qs);
  return 1;
}

int test_large_state() {
  // Test with larger state (10 qubits = 1024 amplitudes)
  QuantumState *qs = qstate_create(10);
  TEST_ASSERT(qs != NULL, "Should be able to create 10-qubit state");
  TEST_ASSERT(qs->vector_size == 1024, "10 qubits should have 1024 amplitudes");

  // Apply some gates
  qstate_apply_h(qs, 0);
  qstate_apply_h(qs, 1);
  qstate_apply_cnot(qs, 0, 1);

  double norm = qstate_norm(qs);
  TEST_ASSERT(is_close(norm, 1.0, EPSILON),
              "Large state should maintain normalization");

  qstate_free(qs);
  return 1;
}

// ============================================================================
// Main Test Runner
// ============================================================================

int main() {
  printf("========================================\n");
  printf("MacQ C Engine Test Suite\n");
  printf("========================================\n\n");

  RUN_TEST(test_version);
  RUN_TEST(test_create_and_free);
  RUN_TEST(test_basis_initialization);
  RUN_TEST(test_pauli_x_gate);
  RUN_TEST(test_hadamard_gate);
  RUN_TEST(test_cnot_gate);
  RUN_TEST(test_bell_state);
  RUN_TEST(test_rotation_gates);
  RUN_TEST(test_toffoli_gate);
  RUN_TEST(test_normalization);
  RUN_TEST(test_measurement);
  RUN_TEST(test_large_state);

  printf("========================================\n");
  printf("Test Summary\n");
  printf("========================================\n");
  printf("Total tests: %d\n", tests_total);
  printf("Passed: %d (✓)\n", tests_passed);
  printf("Failed: %d (✗)\n", tests_failed);
  printf("Success rate: %.1f%%\n", tests_passed * 100.0 / tests_total);
  printf("========================================\n");

  return (tests_failed == 0) ? 0 : 1;
}
