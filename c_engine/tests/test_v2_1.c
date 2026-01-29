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

static int tests_total = 0;
static int tests_passed = 0;
static int tests_failed = 0;

static int is_close(double a, double b, double epsilon) {
  return fabs(a - b) < epsilon;
}

// 1. Test Density Matrix Creation
int test_dmatrix_creation() {
  DensityMatrix *dm = dmatrix_create(2);
  TEST_ASSERT(dm != NULL, "Failed to create density matrix");
  TEST_ASSERT(dm->num_qubits == 2, "Wrong qubit count");
  TEST_ASSERT(dm->dim == 4, "Wrong dimension");
  dmatrix_free(dm);
  return 1;
}

// 2. Test Density Matrix from State Vector (Bell state)
int test_dmatrix_from_qstate() {
  QuantumState *qs = qstate_create(2);
  qstate_apply_h(qs, 0);
  qstate_apply_cnot(qs, 0, 1);

  DensityMatrix *dm = dmatrix_from_qstate(qs);
  TEST_ASSERT(dm != NULL, "Failed to create DM from QS");

  // Bell state |00> + |11> -> rho has 0.5 at (0,0), (0,3), (3,0), (3,3)
  TEST_ASSERT(is_close(creal(dm->data[0 * 4 + 0]), 0.5, EPSILON),
              "rho[0,0] should be 0.5");
  TEST_ASSERT(is_close(creal(dm->data[3 * 4 + 3]), 0.5, EPSILON),
              "rho[3,3] should be 0.5");
  TEST_ASSERT(is_close(creal(dm->data[0 * 4 + 3]), 0.5, EPSILON),
              "rho[0,3] should be 0.5");

  dmatrix_free(dm);
  qstate_free(qs);
  return 1;
}

// 3. Test Partial Trace (Bell state -> I/2)
int test_partial_trace() {
  QuantumState *qs = qstate_create(2);
  qstate_apply_h(qs, 0);
  qstate_apply_cnot(qs, 0, 1);
  DensityMatrix *dm = dmatrix_from_qstate(qs);

  DensityMatrix *reduced = NULL;
  int qubits_to_trace[] = {1};
  MacQError err = dmatrix_partial_trace(dm, 1, qubits_to_trace, &reduced);

  TEST_ASSERT(err == MACQ_SUCCESS, "Partial trace failed");
  TEST_ASSERT(reduced->num_qubits == 1, "Reduced DM should have 1 qubit");
  TEST_ASSERT(is_close(creal(reduced->data[0 * 2 + 0]), 0.5, EPSILON),
              "Tr_1(Bell) should be 0.5|0><0|");
  TEST_ASSERT(is_close(creal(reduced->data[1 * 2 + 1]), 0.5, EPSILON),
              "Tr_1(Bell) should be 0.5|1><1|");

  dmatrix_free(dm);
  dmatrix_free(reduced);
  qstate_free(qs);
  return 1;
}

// 4. Test Noise Channel (Stochastic Damping)
int test_noise_stochastic() {
  srand(42);
  QuantumState *qs = qstate_create(1);
  qstate_apply_x(qs, 0); // Start in |1>

  // Apply heavy damping
  for (int i = 0; i < 100; i++) {
    qstate_apply_amplitude_damping(qs, 0, 0.1);
  }

  // After many applications, it should likely be |0>
  double prob1 = qstate_probability(qs, 0);
  TEST_ASSERT(prob1 < 0.1, "State should have decayed to |0>");

  qstate_free(qs);
  return 1;
}

// 5. Test Expectation Value (<Z>)
int test_expectation_value() {
  QuantumState *qs = qstate_create(1);
  // <0|Z|0> = 1
  QuantumGate z_gate = {GATE_Z, 0, -1, -1, 0, 0};
  double exp_z = qstate_expectation_value(qs, 1, &z_gate);
  TEST_ASSERT(is_close(exp_z, 1.0, EPSILON), "<0|Z|0> should be 1.0");

  // <1|Z|1> = -1
  qstate_apply_x(qs, 0);
  exp_z = qstate_expectation_value(qs, 1, &z_gate);
  TEST_ASSERT(is_close(exp_z, -1.0, EPSILON), "<1|Z|1> should be -1.0");

  // <+|X|+> = 1
  qstate_init_basis(qs, "0");
  qstate_apply_h(qs, 0);
  QuantumGate x_gate = {GATE_X, 0, -1, -1, 0, 0};
  double exp_x = qstate_expectation_value(qs, 1, &x_gate);
  TEST_ASSERT(is_close(exp_x, 1.0, EPSILON), "<+|X|+> should be 1.0");

  qstate_free(qs);
  return 1;
}

int main() {
  printf("========================================\n");
  printf("MacQ C Engine v2.1 Test Suite\n");
  printf("========================================\n\n");

  RUN_TEST(test_dmatrix_creation);
  RUN_TEST(test_dmatrix_from_qstate);
  RUN_TEST(test_partial_trace);
  RUN_TEST(test_noise_stochastic);
  RUN_TEST(test_expectation_value);

  printf("========================================\n");
  printf("Test Summary\n");
  printf("Passed: %d/%d\n", tests_passed, tests_total);
  return (tests_failed == 0) ? 0 : 1;
}
