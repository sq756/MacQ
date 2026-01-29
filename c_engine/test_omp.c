#include <stdio.h>
#ifdef _OPENMP
#include <omp.h>
#endif

int main() {
#ifdef _OPENMP
  printf("OpenMP is enabled. Threads: %d\n", omp_get_max_threads());
#else
  printf("OpenMP is NOT enabled.\n");
#endif
  return 0;
}
