# MacQ量子比特扩展方案：突破内存限制

## 问题分析

### 100量子比特的内存需求

**直接态向量模拟的限制**：

```python
# 内存需求计算
n_qubits = 100
vector_size = 2**n_qubits  # 2^100 ≈ 1.27 × 10^30
bytes_per_complex = 16      # sizeof(complex double)

total_memory = vector_size * bytes_per_complex
# ≈ 2.0 × 10^31 字节 
# ≈ 20,000,000,000,000 TB (两千万亿TB!)
```

**现实限制**：
- 您的Mac mini (16GB RAM): 最多约 **30-32 量子比特**
- 世界上最大的超级计算机 (数PB内存): 最多约 **45-50 量子比特**

### 为什么"以空间换时间"在量子模拟中很难？

传统计算中，我们可以：
```c
// 传统：空间换时间
// 预计算所有结果存在表中，O(1)查询但O(n)空间
int lookup_table[N];

// 或：时间换空间
// 每次计算，O(n)时间但O(1)空间
int compute_on_demand(int x);
```

但量子态不同：
- **量子态本身就是指数级信息**：100量子比特的完整态包含 2^100 个复数振幅
- **不能"只存储需要的部分"**：叠加态意味着所有可能都存在
- **测量会坍缩态**：无法通过分批计算+合并来绕过

---

## 解决方案：多种模拟方法

### 方案1: 矩阵乘积态 (MPS) 表示

**核心思想**：利用量子纠缠的局域性，将态分解为张量链。

#### 理论基础

对于纠缠度有限的态，可以表示为：
```
|ψ⟩ ≈ Σ A[1]^{i1} · A[2]^{i2} · ... · A[n]^{in} |i1 i2 ... in⟩
```

其中每个 `A[k]` 是一个小矩阵（秩为χ，称为"bond dimension"）。

**内存需求**：
```python
# 完整态向量
full_memory = 2^n * 16 字节

# MPS表示（bond dimension χ）
mps_memory = n * χ^2 * 4 * 16 字节  # 4个索引方向
```

**示例**：100量子比特，χ=100
```
MPS内存 = 100 * 100^2 * 4 * 16 字节 
        = 6.4 GB （完全可行！）
```

#### C语言实现框架

```c
// c_engine/include/mps.h

typedef struct {
    int site;                    // 当前位点
    int physical_dim;            // 物理维度（量子比特为2）
    int bond_dim_left;           // 左键维度 χ_left
    int bond_dim_right;          // 右键维度 χ_right
    complex double* tensor;      // 张量数据
} MPSTensor;

typedef struct {
    int num_qubits;
    int max_bond_dim;            // 最大键维度（控制精度）
    MPSTensor* tensors;          // 张量链
    double truncation_error;     // 截断误差
} MPSState;

// 创建MPS态
MPSState* mps_create(int num_qubits, int max_bond_dim);

// 应用单量子比特门（精确）
void mps_apply_single_gate(MPSState* mps, int site, GateType gate);

// 应用双量子比特门（近似，会增加纠缠）
void mps_apply_two_gate(MPSState* mps, int site1, int site2, 
                        GateType gate);

// SVD截断以控制键维度
void mps_truncate(MPSState* mps, double tolerance);
```

**适用场景**：
- ✅ 量子电路深度较浅
- ✅ 纠缠主要在相邻量子比特之间（1D拓扑）
- ✅ 量子傅里叶变换、某些VQE算法
- ❌ 高度纠缠的态（如100量子比特的随机电路）

---

### 方案2: 稀疏态模拟

**核心思想**：只存储非零（或显著）的振幅。

```c
// c_engine/include/sparse_state.h

typedef struct {
    size_t basis_state;      // 基态索引（如 |01101⟩ → 13）
    complex double amplitude; // 振幅
} StateAmplitude;

typedef struct {
    int num_qubits;
    size_t num_nonzero;      // 非零项数量
    size_t capacity;
    StateAmplitude* amplitudes;
} SparseState;

// 稀疏态操作
void sparse_apply_gate(SparseState* ss, QuantumGate gate);
```

**内存需求**：
```python
# 如果只有k个非零项
sparse_memory = k * (8 + 16) 字节  # 索引+振幅

# 例如：100量子比特但只有1000个非零项
memory = 1000 * 24 字节 = 24 KB！
```

**适用场景**：
- ✅ 计算基态（如 |0...0⟩）开始的浅电路
- ✅ Grover搜索算法（稀疏oracle）
- ✅ 特定对称性的问题
- ❌ Hadamard密集的电路（会迅速填满）

---

### 方案3: 混合磁盘映射（Time-Space Trade-off）

**核心思想**：将部分态向量存在磁盘，按需加载。

```c
// c_engine/include/disk_state.h

typedef struct {
    int num_qubits;
    size_t chunk_size;          // 内存块大小
    int num_chunks_in_memory;   // 内存中缓存的块数
    char* disk_file;            // 磁盘映射文件
    int fd;                     // 文件描述符
    complex double* mmap_ptr;   // mmap指针
} DiskMappedState;

// 使用macOS的mmap
DiskMappedState* disk_state_create(int num_qubits, 
                                   const char* tmpdir);

// 页面错误自动加载
void disk_apply_gate(DiskMappedState* dms, QuantumGate gate);
```

**性能估算**：
```
40量子比特（直接态向量需要17.6TB）：
- 使用外置SSD（1TB）可以存储部分
- 门操作速度：约0.1-1秒/门（vs 内存的1μs/门）
- 速度降低10^5-10^6倍，但可以运行！
```

**适用场景**：
- ✅ 离线模拟（不需要实时）
- ✅ 有大容量存储设备
- ❌ 需要快速迭代

---

### 方案4: 蒙特卡洛采样模拟

**核心思想**：不存储完整态，而是采样测量结果。

```c
// c_engine/include/sampling_sim.h

typedef struct {
    int num_qubits;
    QuantumGate* circuit;       // 电路定义
    int circuit_depth;
    int num_samples;            // 采样次数
} SamplingSimulator;

// 执行一次采样（运行整个电路）
uint64_t sampling_run_once(SamplingSimulator* sim);

// 估计期望值
double estimate_expectation(SamplingSimulator* sim, 
                           Observable obs,
                           int num_shots);
```

**内存需求**：
```python
# 只需要存储电路和临时变量
memory = circuit_depth * sizeof(gate) + O(1)
       ≈ 几KB（与量子比特数无关！）
```

**适用场景**：
- ✅ 只关心测量结果统计（不需要完整态）
- ✅ 变分量子算法（VQE, QAOA）
- ✅ 真实量子硬件的仿真预演
- ❌ 需要态向量的完整信息

---

## MacQ实现策略

### 推荐的多后端架构

```c
// c_engine/include/backend.h

typedef enum {
    BACKEND_STATEVECTOR,    // 完整态向量（<30 qubits）
    BACKEND_MPS,            // MPS（30-100 qubits，低纠缠）
    BACKEND_SPARSE,         // 稀疏态（任意qubits，低Hamming weight）
    BACKEND_DISK,           // 磁盘映射（35-45 qubits，慢但可行）
    BACKEND_SAMPLING        // 蒙特卡洛（任意qubits，统计结果）
} BackendType;

typedef struct {
    BackendType type;
    union {
        QuantumState* statevector;
        MPSState* mps;
        SparseState* sparse;
        DiskMappedState* disk;
        SamplingSimulator* sampling;
    } impl;
} UniversalBackend;

// 自动选择最佳后端
UniversalBackend* backend_auto_select(int num_qubits, 
                                     QuantumCircuit* circuit);
```

### Python用户接口

```python
from macq import QuantumCircuit

# 自动选择后端
qc = QuantumCircuit(100, backend='auto')  
# 内部选择: 检测到100 qubits → 尝试MPS

# 手动指定
qc = QuantumCircuit(100, backend='mps', max_bond_dim=200)
qc = QuantumCircuit(100, backend='sampling', shots=10000)

# 电路构建
for i in range(100):
    qc.h(i)
# 警告: "High entanglement detected, MPS may be slow. 
#        Consider switching to 'sampling' backend."

# 执行
result = qc.execute()
```

---

## 性能对比表

| 量子比特数 | 完整态向量 | MPS (χ=100) | 稀疏态 | 磁盘映射 | 采样模拟 |
|-----------|-----------|------------|--------|---------|---------|
| **10** | ✅ 16KB | ✅ 64KB | ✅ 可变 | ⚠️ 过度 | ✅ 1KB |
| **20** | ✅ 16MB | ✅ 128KB | ✅ 可变 | ⚠️ 过度 | ✅ 1KB |
| **30** | ✅ 16GB | ✅ 192KB | ✅ 可变 | ✅ 17.6TB | ✅ 1KB |
| **40** | ❌ 16TB | ✅ 256KB | ⚠️ 指数增长 | ⚠️ 17.6PB | ✅ 1KB |
| **50** | ❌ 16PB | ✅ 320KB | ❌ 太大 | ❌ 不可行 | ✅ 1KB |
| **100** | ❌ 2×10^31B | ✅ 640KB | ❌ 不可行 | ❌ 不可行 | ✅ 1KB |

**速度对比**（单门操作）：
- 完整态向量: **1μs**
- MPS: **10μs - 1ms**（取决于纠缠）
- 稀疏态: **1μs - 1ms**（取决于稀疏度）
- 磁盘映射: **0.1s - 10s**
- 采样模拟: **每次采样需完整电路，总时间=采样数×电路时间**

---

## 实现建议

### Phase 1: 基础态向量（已计划）
```c
// 支持到30量子比特
QuantumState* qstate_create(int num_qubits);  // 限制 <= 30
```

### Phase 2: MPS后端（推荐优先实现）
```c
// 允许100量子比特的低纠缠模拟
MPSState* mps_create(int num_qubits, int max_bond_dim);
```

**所需库**：
- LAPACK（SVD分解）- macOS Accelerate自带！
- BLAS（矩阵乘法）- 同样自带

### Phase 3: 采样模拟器
```python
# 简单但功能强大
class SamplingBackend:
    def run(self, circuit, shots=1024):
        results = []
        for _ in range(shots):
            state = [0] * n_qubits  # 从|0...0⟩开始
            for gate in circuit:
                state = apply_stochastic(gate, state)
            results.append(measure_all(state))
        return histogram(results)
```

---

## 结论

**您的问题答案**：

1. **能否模拟100个量子比特纠缠？**
   - 完整态向量：❌ 物理不可能
   - MPS方法：✅ **可以**，如果纠缠度有限（bond dimension χ < 500）
   - 采样模拟：✅ **可以**，但只能获得统计结果，不是完整态

2. **能否以空间换时间？**
   - 传统意义上：❌ 量子态本身就是指数空间
   - 近似方法：✅ 可以用MPS/稀疏态牺牲一些精度
   - 磁盘映射：✅ 可以用极慢速度换取大规模（40量子比特左右）

**最实用的方案**：
- **30量子比特以下**：使用完整态向量（您当前的设计）
- **30-100量子比特**：使用MPS（需要额外实现）
- **任意规模但只要统计**：使用采样模拟器

建议先完成基础态向量引擎，然后在Phase 2实现MPS后端作为扩展！
