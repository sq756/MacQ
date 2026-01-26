# MPS后端实现设计文档

## 概述

矩阵乘积态(Matrix Product State, MPS)是一种张量网络表示方法，可以高效模拟低纠缠量子态。这是MacQ扩展到100+量子比特的关键技术。

---

## 数学基础

### 态向量 vs MPS表示

**标准态向量**：
```
|ψ⟩ = Σ c_{i1,i2,...,in} |i1 i2 ... in⟩
```
需要存储 2^n 个系数 c。

**MPS分解**：
```
|ψ⟩ = Σ A[1]_{i1} A[2]_{i2} ... A[n]_{in} |i1 i2 ... in⟩
```

其中 A[k]_{i} 是一个 χ×χ 矩阵（对于边界，一端是1维）。

**关键参数**：
- **物理维度** d = 2（每个量子比特）
- **键维度** χ（bond dimension）：控制纠缠容量和精度

**存储需求**：
```
完整态向量: O(2^n)
MPS表示:    O(n * χ^2 * d)
```

当 χ << 2^(n/2) 时，MPS极大节省空间！

---

## C语言实现

### 数据结构定义

```c
// c_engine/include/mps.h

#ifndef MPS_H
#define MPS_H

#include <complex.h>
#include <stdbool.h>

typedef double complex cplx;

// MPS张量节点
typedef struct {
    int site;                    // 位点索引 (0 to n-1)
    int phys_dim;                // 物理维度 (通常为2)
    int bond_left;               // 左键维度
    int bond_right;              // 右键维度
    
    // 张量数据: 形状为 [bond_left, phys_dim, bond_right]
    // 存储为1D数组，按C序排列
    cplx* data;
    
    // 可选：预计算的规范化形式
    bool is_canonical;
    char canonical_center;       // 'L' 或 'R'
} MPSTensor;

// 完整MPS态
typedef struct {
    int num_sites;               // 量子比特数量
    int max_bond_dim;            // 最大允许的键维度
    
    MPSTensor* tensors;          // 张量链数组
    
    double truncation_error;     // 累积截断误差
    double norm;                 // 态的范数
    
    // 性能统计
    long long gate_count;
    long long svd_count;
} MPSState;

// 创建与销毁
MPSState* mps_create(int num_sites, int max_bond_dim);
void mps_free(MPSState* mps);

// 初始化到计算基态
void mps_init_basis_state(MPSState* mps, const char* bitstring);

// 单量子比特门
void mps_apply_single_gate(MPSState* mps, int site, const cplx gate[2][2]);

// 双量子比特门（核心挑战）
void mps_apply_two_gate(MPSState* mps, int site1, int site2, 
                        const cplx gate[4][4]);

// 规范化
void mps_canonicalize(MPSState* mps, int center);

// SVD截断
void mps_truncate_bond(MPSState* mps, int bond, double tolerance);

// 测量
int mps_measure(MPSState* mps, int site);
double mps_expectation_value(MPSState* mps, int site, 
                             const cplx obs[2][2]);

// 调试工具
void mps_print_info(const MPSState* mps);
double mps_compute_norm(const MPSState* mps);

#endif // MPS_H
```

---

## 关键算法实现

### 1. 单量子比特门（简单）

```c
// src/mps_gates.c

void mps_apply_single_gate(MPSState* mps, int site, const cplx gate[2][2]) {
    MPSTensor* A = &mps->tensors[site];
    
    int bond_left = A->bond_left;
    int bond_right = A->bond_right;
    
    // 创建临时张量存储结果
    cplx* new_data = malloc(bond_left * 2 * bond_right * sizeof(cplx));
    
    // 对物理索引应用门
    // new_A[α, i', β] = Σ_i gate[i', i] * A[α, i, β]
    for (int alpha = 0; alpha < bond_left; alpha++) {
        for (int beta = 0; beta < bond_right; beta++) {
            for (int i_new = 0; i_new < 2; i_new++) {
                cplx sum = 0.0;
                for (int i_old = 0; i_old < 2; i_old++) {
                    int idx_old = alpha * (2 * bond_right) + 
                                 i_old * bond_right + beta;
                    sum += gate[i_new][i_old] * A->data[idx_old];
                }
                int idx_new = alpha * (2 * bond_right) + 
                             i_new * bond_right + beta;
                new_data[idx_new] = sum;
            }
        }
    }
    
    // 替换旧数据
    free(A->data);
    A->data = new_data;
}
```

### 2. 双量子比特门（复杂）

**策略**：使用奇异值分解(SVD)控制纠缠增长。

```c
// src/mps_two_gate.c

#include <Accelerate/Accelerate.h>  // 使用Apple的LAPACK

void mps_apply_two_gate(MPSState* mps, int site1, int site2, 
                        const cplx gate[4][4]) {
    // 假设相邻位点 (site2 = site1 + 1)
    if (site2 != site1 + 1) {
        // 对于非相邻，需要SWAP门移动（TODO）
        fprintf(stderr, "Non-adjacent gates not yet implemented\n");
        return;
    }
    
    MPSTensor* A = &mps->tensors[site1];
    MPSTensor* B = &mps->tensors[site2];
    
    int chi_left = A->bond_left;
    int chi_mid = A->bond_right;  // = B->bond_left
    int chi_right = B->bond_right;
    
    // Step 1: 合并两个张量为一个4阶张量
    // Theta[α, i, j, β] = Σ_γ A[α, i, γ] * B[γ, j, β]
    cplx* theta = malloc(chi_left * 2 * 2 * chi_right * sizeof(cplx));
    
    for (int alpha = 0; alpha < chi_left; alpha++) {
        for (int i = 0; i < 2; i++) {
            for (int j = 0; j < 2; j++) {
                for (int beta = 0; beta < chi_right; beta++) {
                    cplx sum = 0.0;
                    for (int gamma = 0; gamma < chi_mid; gamma++) {
                        int idx_A = alpha * (2 * chi_mid) + i * chi_mid + gamma;
                        int idx_B = gamma * (2 * chi_right) + j * chi_right + beta;
                        sum += A->data[idx_A] * B->data[idx_B];
                    }
                    int idx = alpha * (2 * 2 * chi_right) + 
                             i * (2 * chi_right) + 
                             j * chi_right + beta;
                    theta[idx] = sum;
                }
            }
        }
    }
    
    // Step 2: 应用双量子比特门
    // Theta'[α, i', j', β] = Σ_{i,j} gate[i'j', ij] * Theta[α, i, j, β]
    cplx* theta_new = malloc(chi_left * 2 * 2 * chi_right * sizeof(cplx));
    
    for (int alpha = 0; alpha < chi_left; alpha++) {
        for (int beta = 0; beta < chi_right; beta++) {
            for (int ij_new = 0; ij_new < 4; ij_new++) {
                int i_new = ij_new / 2;
                int j_new = ij_new % 2;
                
                cplx sum = 0.0;
                for (int ij_old = 0; ij_old < 4; ij_old++) {
                    int i_old = ij_old / 2;
                    int j_old = ij_old % 2;
                    
                    int idx_old = alpha * (2 * 2 * chi_right) + 
                                 i_old * (2 * chi_right) + 
                                 j_old * chi_right + beta;
                    sum += gate[ij_new][ij_old] * theta[idx_old];
                }
                
                int idx_new = alpha * (2 * 2 * chi_right) + 
                             i_new * (2 * chi_right) + 
                             j_new * chi_right + beta;
                theta_new[idx_new] = sum;
            }
        }
    }
    
    free(theta);
    
    // Step 3: SVD分解 Theta' → A' * S * B'
    // 重塑 theta_new 为矩阵 [chi_left * 2, 2 * chi_right]
    int m = chi_left * 2;
    int n = 2 * chi_right;
    int min_dim = (m < n) ? m : n;
    
    // 使用vDSP的SVD（需要转换为实数格式或使用zgesvd）
    // 这里简化：假设使用LAPACK的zgesvd
    
    double* S = malloc(min_dim * sizeof(double));
    cplx* U = malloc(m * min_dim * sizeof(cplx));
    cplx* VT = malloc(min_dim * n * sizeof(cplx));
    
    // 调用LAPACK的zgesvd
    // ... (详细实现省略，需要正确调用Accelerate的LAPACK)
    
    // Step 4: 截断小奇异值
    int new_bond_dim = min_dim;
    if (new_bond_dim > mps->max_bond_dim) {
        new_bond_dim = mps->max_bond_dim;
        
        // 计算截断误差
        double error_sq = 0.0;
        for (int k = new_bond_dim; k < min_dim; k++) {
            error_sq += S[k] * S[k];
        }
        mps->truncation_error += sqrt(error_sq);
    }
    
    // Step 5: 重构新的A和B张量
    // A'[α, i, γ'] = U[α*2 + i, γ'] * sqrt(S[γ'])
    free(A->data);
    A->data = malloc(chi_left * 2 * new_bond_dim * sizeof(cplx));
    A->bond_right = new_bond_dim;
    
    for (int alpha = 0; alpha < chi_left; alpha++) {
        for (int i = 0; i < 2; i++) {
            for (int gamma = 0; gamma < new_bond_dim; gamma++) {
                int idx_U = (alpha * 2 + i) * min_dim + gamma;
                int idx_A = alpha * (2 * new_bond_dim) + i * new_bond_dim + gamma;
                A->data[idx_A] = U[idx_U] * sqrt(S[gamma]);
            }
        }
    }
    
    // B'[γ', j, β] = sqrt(S[γ']) * VT[γ', j*chi_right + β]
    free(B->data);
    B->data = malloc(new_bond_dim * 2 * chi_right * sizeof(cplx));
    B->bond_left = new_bond_dim;
    
    for (int gamma = 0; gamma < new_bond_dim; gamma++) {
        for (int j = 0; j < 2; j++) {
            for (int beta = 0; beta < chi_right; beta++) {
                int idx_VT = gamma * n + j * chi_right + beta;
                int idx_B = gamma * (2 * chi_right) + j * chi_right + beta;
                B->data[idx_B] = sqrt(S[gamma]) * VT[idx_VT];
            }
        }
    }
    
    // 清理
    free(theta_new);
    free(S);
    free(U);
    free(VT);
    
    mps->svd_count++;
}
```

### 3. 测量实现

```c
// src/mps_measure.c

int mps_measure(MPSState* mps, int site) {
    // 计算测量到|0⟩和|1⟩的概率
    double prob_0 = 0.0;
    double prob_1 = 0.0;
    
    // 需要收缩整个MPS网络（计算密集）
    // 简化实现：假设已规范化到测量位点
    
    MPSTensor* A = &mps->tensors[site];
    
    // 对于规范形式，局部概率为：
    // p(i) = Σ_{α,β} |A[α, i, β]|^2
    
    for (int alpha = 0; alpha < A->bond_left; alpha++) {
        for (int beta = 0; beta < A->bond_right; beta++) {
            int idx_0 = alpha * (2 * A->bond_right) + 0 * A->bond_right + beta;
            int idx_1 = alpha * (2 * A->bond_right) + 1 * A->bond_right + beta;
            
            prob_0 += cabs(A->data[idx_0]) * cabs(A->data[idx_0]);
            prob_1 += cabs(A->data[idx_1]) * cabs(A->data[idx_1]);
        }
    }
    
    // 归一化
    double total = prob_0 + prob_1;
    prob_0 /= total;
    prob_1 /= total;
    
    // 随机采样
    double rand_val = (double)rand() / RAND_MAX;
    int result = (rand_val < prob_0) ? 0 : 1;
    
    // 坍缩态（投影）
    // ... (实现态投影)
    
    return result;
}
```

---

## Python接口

```python
# macq/mps_backend.py

import ctypes
import numpy as np
from .c_bridge import lib

class MPSBackend:
    """MPS后端for MacQ"""
    
    def __init__(self, num_qubits, max_bond_dim=100):
        self.num_qubits = num_qubits
        self.max_bond_dim = max_bond_dim
        
        # 调用C函数创建MPS
        self._mps_ptr = lib.mps_create(num_qubits, max_bond_dim)
        
        # 初始化为|0...0⟩
        bitstring = '0' * num_qubits
        lib.mps_init_basis_state(self._mps_ptr, bitstring.encode())
    
    def apply_gate(self, gate_name, qubits, **params):
        """应用量子门"""
        if len(qubits) == 1:
            # 单量子比特门
            gate_matrix = self._get_gate_matrix(gate_name, **params)
            lib.mps_apply_single_gate(
                self._mps_ptr, 
                qubits[0],
                gate_matrix.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
            )
        elif len(qubits) == 2:
            # 双量子比特门
            gate_matrix = self._get_two_qubit_gate(gate_name)
            lib.mps_apply_two_gate(
                self._mps_ptr,
                qubits[0],
                qubits[1],
                gate_matrix.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
            )
        else:
            raise ValueError("MPS backend only supports 1 or 2 qubit gates")
    
    def measure(self, qubit):
        """测量单个量子比特"""
        return lib.mps_measure(self._mps_ptr, qubit)
    
    def get_truncation_error(self):
        """获取累积截断误差"""
        return lib.mps_get_truncation_error(self._mps_ptr)
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, '_mps_ptr'):
            lib.mps_free(self._mps_ptr)
```

---

## 性能优化技巧

### 1. 使用Accelerate框架

```c
// 矩阵乘法优化
#include <Accelerate/Accelerate.h>

void optimized_matrix_multiply(const cplx* A, const cplx* B, cplx* C,
                               int m, int n, int k) {
    // 使用vDSP的复数矩阵乘法
    // cblas_zgemm(...);
}
```

### 2. 智能规范化策略

```c
// 只在必要时规范化
void smart_canonicalize(MPSState* mps, int gate_site) {
    // 检查当前规范中心与操作位点的距离
    if (abs(mps->canonical_center - gate_site) > 5) {
        mps_canonicalize(mps, gate_site);
    }
}
```

### 3. 自适应bond dimension

```c
// 根据截断误差动态调整
void adaptive_truncate(MPSState* mps, int bond, double target_error) {
    // 从大到小尝试bond dimension
    for (int chi = mps->max_bond_dim; chi >= 10; chi -= 10) {
        double error = estimate_truncation_error(mps, bond, chi);
        if (error < target_error) {
            actual_truncate(mps, bond, chi);
            return;
        }
    }
}
```

---

## 测试用例

```c
// tests/test_mps.c

#include "mps.h"
#include <assert.h>
#include <math.h>

void test_bell_state() {
    // 创建2量子比特MPS
    MPSState* mps = mps_create(2, 10);
    mps_init_basis_state(mps, "00");
    
    // 应用 H ⊗ I
    cplx H[2][2] = {
        {1.0/sqrt(2), 1.0/sqrt(2)},
        {1.0/sqrt(2), -1.0/sqrt(2)}
    };
    mps_apply_single_gate(mps, 0, H);
    
    // 应用 CNOT
    cplx CNOT[4][4] = {
        {1, 0, 0, 0},
        {0, 1, 0, 0},
        {0, 0, 0, 1},
        {0, 0, 1, 0}
    };
    mps_apply_two_gate(mps, 0, 1, CNOT);
    
    // 测量应该得到50%的00和50%的11
    int counts[4] = {0};
    for (int shot = 0; shot < 1000; shot++) {
        MPSState* test_mps = mps_clone(mps);
        int bit0 = mps_measure(test_mps, 0);
        int bit1 = mps_measure(test_mps, 1);
        counts[bit0 * 2 + bit1]++;
        mps_free(test_mps);
    }
    
    printf("Bell state measurement results:\n");
    printf("|00⟩: %d/1000 (expected ~500)\n", counts[0]);
    printf("|11⟩: %d/1000 (expected ~500)\n", counts[3]);
    
    assert(counts[0] > 400 && counts[0] < 600);
    assert(counts[3] > 400 && counts[3] < 600);
    
    mps_free(mps);
}
```

---

## 集成到MacQ主线

### Makefile更新

```makefile
# c_engine/Makefile

MPS_SOURCES = src/mps.c src/mps_gates.c src/mps_two_gate.c src/mps_measure.c
MPS_OBJECTS = $(MPS_SOURCES:.c=.o)

libmacq_mps.dylib: $(MPS_OBJECTS)
	$(CC) -shared -framework Accelerate -o $@ $^

# Python可动态选择加载libmacq.dylib或libmacq_mps.dylib
```

---

## 总结

**实现MPS后端后，MacQ将能够**：
- ✅ 模拟100量子比特的低纠缠电路
- ✅ 内存需求仅数百KB到数MB
- ✅ 完全兼容现有API
- ✅ 用户可透明切换后端

**开发时间估计**：
- MPS核心实现: 2-3周
- SVD优化与调试: 1周
- Python集成: 3天
- 测试与文档: 1周

**总计**: 约1个月全职开发

这将是MacQ区别于其他量子模拟器的杀手级功能！
