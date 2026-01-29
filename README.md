# MacQ: Mac-Native Quantum Computing Software

<div align="center">

![MacQ Logo](assets/logo.png)

**高性能量子计算仿真软件 | High-Performance Quantum Computing Simulation**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)
[![Language](https://img.shields.io/badge/Language-C-blue.svg)](https://en.wikipedia.org/wiki/C_(programming_language))
[![GUI](https://img.shields.io/badge/GUI-Qt%2FPySide6-green.svg)](https://www.qt.io/)

[English](#english) | [中文](#中文)

</div>

---

## 中文

### 项目简介

**MacQ** 是一款专为 macOS 平台设计的高性能量子计算仿真桌面软件。它采用 **C语言编写的核心计算引擎**，配合直观的可视化"块状"编程界面，让用户能够轻松构建和运行量子电路。

### 核心特性

- 🚀 **C语言原生引擎**: 100% 纯 C 编写的量子态计算核心，零 Python 开销
- 🍎 **Apple Silicon 优化**: 深度集成 Accelerate 框架，支持 **GCD 多线程**与 **ARM NEON SIMD** 加速
- 🧪 **物理仿真增强**: 支持**密度矩阵**、**偏迹 (Partial Trace)** 与随机**噪声模型**
- 🖥️ **macOS 原生应用**: 真正的桌面软件，非 web 应用或 Python 脚本
- 🎨 **可视化编辑器**: 拖拽式量子门块设计，支持 Q-Lang 智能编译器 (v2.0)
- ⚡ **极致性能**: 跨平台多线程架构，专为 M-系列芯片极致优化

### 架构设计

```
┌─────────────────────────────────────────┐
│  GUI Layer (PySide6/Qt)                 │  60fps 界面响应
│  - 可视化量子块编辑器                      │
│  - 实时概率分布图表                        │
└─────────────────┬───────────────────────┘
                  │ Python ctypes
┌─────────────────▼───────────────────────┐
│  Bridge Layer (Python)                  │  <1ms 调用延迟
│  - C/Python 类型转换                     │
│  - 内存共享管理                          │
└─────────────────┬───────────────────────┘
                  │ libmacq.dylib
┌─────────────────▼───────────────────────┐
│  C Engine (C + GCD + SIMD)              │  高性能计算
│  - 量子态向量操作 & 多线程并行             │
│  - NEON/SSE SIMD 加速实现                │
│  - 密度矩阵与噪声模拟模块                 │
└─────────────────────────────────────────┘
```

### 快速开始

#### 系统要求

- macOS 12.0+ (Intel 或 Apple Silicon)
- Xcode Command Line Tools
- Python 3.9+

#### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/sq756/MacQ.git
cd MacQ

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 编译 C 核心引擎
cd c_engine
make libmacq.dylib

# 4. 运行应用
cd ..
python main_app.py
```

#### 创建第一个量子电路：贝尔态

```python
from macq import QuantumCircuit

# 创建 2 量子比特电路
qc = QuantumCircuit(2)

# 添加门
qc.h(0)        # Hadamard 门
qc.cx(0, 1)    # CNOT 门

# 执行
result = qc.execute()

# 查看结果
print(f"|00⟩: {result.probability(0):.2%}")  # 50%
print(f"|11⟩: {result.probability(3):.2%}")  # 50%
```

### 文档

- 📖 [完整开发文档（中文）](MacQ_开发文档_中文版.md)
- 📖 [Developer Guide (English)](MacQ_Developer_Guide_EN.md)
- 📚 [API 参考](docs/api_reference.md)
- 🎓 [使用教程](docs/tutorials/)

### 项目结构

```
MacQ/
├── c_engine/              # C 语言核心引擎
│   ├── include/          # 头文件
│   ├── src/              # C 源代码
│   ├── tests/            # C 单元测试
│   └── Makefile          # 构建系统
├── macq/                  # Python 包
│   ├── c_bridge.py       # C/Python 桥接
│   ├── circuit.py        # 量子电路高层 API
│   └── gui/              # GUI 组件
├── examples/              # 示例电路
├── tests/                 # Python 测试
├── docs/                  # 文档
├── main_app.py            # 应用入口
└── README.md              # 本文件
```

### 性能基准

*基于 Apple M1 Max 芯片测试*

| 操作 | 10 量子比特 | 20 量子比特 | 30 量子比特 |
|------|------------|------------|------------|
| 单门操作 | <1μs | ~10μs | ~1ms |
| CNOT 门 | <5μs | ~50μs | ~5ms |
| QFT 电路 | <100μs | ~10ms | ~1s |

### 路线图

- [x] **2026 Q1**: 完整单量子比特门集、Q-Lang 编译器 v2.0
- [x] **2026 Q2**: **C-Engine v2.1**: 多线程加速、SIMD 优化、噪声模型
- [ ] **2026 Q3**: Bloch 球面 3D 可视化、自定义门矩阵
- [ ] **2026 Q4**: 硬件后端集成、分布式仿真

### 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 许可证

本项目采用 [MIT License](LICENSE)。

### 联系方式

- **GitHub Issues**: [https://github.com/sq756/MacQ/issues](https://github.com/sq756/MacQ/issues)
- **Email**: sq2000@stu.pku.edu.cn

---

## English

### Introduction

**MacQ** is a high-performance quantum computing simulation desktop software specifically designed for the macOS platform. It features a **C language-powered core computational engine** combined with an intuitive visual "block-based" programming interface, enabling users to easily build and execute quantum circuits.

### Key Features

- 🚀 **C Native Engine**: 100% pure C-written quantum state computation core, zero Python overhead
- 🍎 **Apple Silicon Optimized**: Deep integration with Accelerate framework, **GCD multi-threading**, and **ARM NEON SIMD**
- 🧪 **Physical Simulation**: Advanced support for **Density Matrices**, **Partial Trace**, and stochastic **Noise Models**
- 🖥️ **macOS Native App**: True desktop software, not a web app or Python script
- 🎨 **Visual Editor**: Drag-and-drop quantum gate blocks with Q-Lang smart compiler (v2.0)
- ⚡ **Ultimate Performance**: Highly-optimized multi-threaded architecture for M-series chips

### Architecture

```
┌─────────────────────────────────────────┐
│  GUI Layer (PySide6/Qt)                 │  60fps UI Response
│  - Visual Quantum Block Editor          │
│  - Real-time Probability Charts         │
└─────────────────┬───────────────────────┘
                  │ Python ctypes
┌─────────────────▼───────────────────────┐
│  Bridge Layer (Python)                  │  <1ms Call Latency
│  - C/Python Type Conversion             │
│  - Memory Sharing Management            │
└─────────────────┬───────────────────────┘
                  │ libmacq.dylib
┌─────────────────▼───────────────────────┐
│  C Engine (C + GCD + SIMD)              │  Advanced HPC
│  - Quantum State Vector & Multi-threading│
│  - NEON/SSE SIMD Implementation         │
│  - Density Matrix & Noise Modules       │
└─────────────────────────────────────────┘
```

### Quick Start

#### System Requirements

- macOS 12.0+ (Intel or Apple Silicon)
- Xcode Command Line Tools
- Python 3.9+

#### Installation

```bash
# 1. Clone the repository
git clone https://github.com/sq756/MacQ.git
cd MacQ

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Build C core engine
cd c_engine
make libmacq.dylib

# 4. Run the application
cd ..
python main_app.py
```

#### Create Your First Quantum Circuit: Bell State

```python
from macq import QuantumCircuit

# Create 2-qubit circuit
qc = QuantumCircuit(2)

# Add gates
qc.h(0)        # Hadamard gate
qc.cx(0, 1)    # CNOT gate

# Execute
result = qc.execute()

# View results
print(f"|00⟩: {result.probability(0):.2%}")  # 50%
print(f"|11⟩: {result.probability(3):.2%}")  # 50%
```

### Documentation

- 📖 [Complete Development Documentation (Chinese)](MacQ_开发文档_中文版.md)
- 📖 [Developer Guide (English)](MacQ_Developer_Guide_EN.md)
- 📚 [API Reference](docs/api_reference.md)
- 🎓 [Tutorials](docs/tutorials/)

### Project Structure

```
MacQ/
├── c_engine/              # C Language Core Engine
│   ├── include/          # Header Files
│   ├── src/              # C Source Code
│   ├── tests/            # C Unit Tests
│   └── Makefile          # Build System
├── macq/                  # Python Package
│   ├── c_bridge.py       # C/Python Bridge
│   ├── circuit.py        # High-level Circuit API
│   └── gui/              # GUI Components
├── examples/              # Example Circuits
├── tests/                 # Python Tests
├── docs/                  # Documentation
├── main_app.py            # Application Entry Point
└── README.md              # This File
```

### Performance Benchmarks

*Tested on Apple M1 Max*

| Operation | 10 Qubits | 20 Qubits | 30 Qubits |
|-----------|-----------|-----------|-----------|
| Single Gate | <1μs | ~10μs | ~1ms |
| CNOT Gate | <5μs | ~50μs | ~5ms |
| QFT Circuit | <100μs | ~10ms | ~1s |

### Roadmap

- [x] **2026 Q1**: Complete single-qubit gate set, Q-Lang v2.0
- [x] **2026 Q2**: **C-Engine v2.1**: Multi-threaded, SIMD, Noise models
- [ ] **2026 Q3**: Bloch sphere 3D visualization, Custom gate matrix
- [ ] **2026 Q4**: Hardware backend integration, Distributed simulation

### Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### License

This project is licensed under the [MIT License](LICENSE).

### Contact

- **GitHub Issues**: [https://github.com/sq756/MacQ/issues](https://github.com/sq756/MacQ/issues)
- **Email**:sq2000@stu.pku.edu.cn

---

<div align="center">

**Made with ❤️ for the quantum computing community**

</div>
