# Q-Lang: Quantum Circuit Description Language

**Multi-Language Specification Document**

---

## Table of Contents / 目录 / 目次

- [English Version](#english)
- [中文版本](#中文)
- [日本語版](#日本語)

---

<a name="english"></a>
# 🌐 English Version

## Q-Lang: Quantum Circuit Description Language Specification

### 📖 Overview

Q-Lang is a text-based quantum circuit description language designed for precise definition of quantum gate timing and placement, avoiding conflicts inherent in graphical drag-and-drop interfaces.

**Version**: 1.0.0  
**Date**: 2026-01-26  
**Author**: MacQ Team

### 🎯 Design Principles

1. **Sequential Lines = Time Steps**: Top-to-bottom lines represent temporal progression
2. **Semicolons for Parallelism**: Operations in the same time step are separated by `;`
3. **Concise Clarity**: Gate name + qubit(s), control qubits connected with `-`
4. **Conflict Detection**: Pre-compilation syntax and physical constraint validation

### 📝 Syntax Rules

#### Basic Format
```
line_number | statement1; statement2; statement3
```

#### Single-Qubit Gates

**Syntax**: `GateName qubit_list`

**Examples**:
```q
H 0, 2, 5          # Apply H to q0, q2, q5
X 1, 3             # Apply X to q1, q3
Rz(π/4) 2          # Parametric rotation gate
```

**Supported Gates**: `H`, `X`, `Y`, `Z`, `I`, `S`, `T`, `S†`, `T†`, `Rx(θ)`, `Ry(θ)`, `Rz(θ)`

#### Two-Qubit Gates

**Syntax**: `GateName control-target`

**Examples**:
```q
CNOT 0-1           # q0 control, q1 target
CZ 2-3             # q2 control, q3 target
SWAP 1-4           # Swap q1 and q4
```

**Supported Gates**: `CNOT`, `CZ`, `SWAP`

#### Three-Qubit Gates

**Syntax**: `GateName control1-control2-target`

**Example**:
```q
Toffoli 0-1-2      # q0, q1 control, q2 target
```

#### Parallel Operations

**Syntax**: Separate with `;` on same line

**Example**:
```q
H 0; X 1; Z 2      # Simultaneous operations
CNOT 0-1; H 3      # Parallel CNOT and H
```

#### Comments
```q
# Single-line comment
H 0  # End-of-line comment
```

### 📋 Complete Examples

#### Example 1: Bell State Preparation
```q
# Bell state: (|00⟩ + |11⟩)/√2
H 0
CNOT 0-1
```

#### Example 2: GHZ State (3 qubits)
```q
# GHZ state: (|000⟩ + |111⟩)/√2
H 0
CNOT 0-1
CNOT 0-2
```

#### Example 3: Complex Circuit with Parallelism
```q
# Step 1: Initialization
H 0, 2, 4; X 1, 3

# Step 2: Entanglement
CNOT 0-1; CNOT 2-3

# Step 3: Measurement basis transformation
H 1; S 3; T 4

# Step 4: Toffoli gate
Toffoli 0-1-2
```

### ⚠️ Conflict Detection Rules

#### 1. Syntax Errors

| Error Type | Example | Message |
|-----------|---------|---------|
| Unknown gate | `ABC 0` | `Error: Unknown gate 'ABC'` |
| Qubit out of range | `H 10` (only 3 qubits) | `Error: Qubit 10 out of range [0,2]` |
| Invalid parameter | `Rx(abc) 0` | `Error: Invalid parameter 'abc'` |
| Missing control | `CNOT 0` | `Error: CNOT requires control-target` |

#### 2. Physical Conflicts

| Conflict Type | Example | Message |
|--------------|---------|---------|
| Qubit used twice | `H 0; X 0` | `Error: Qubit 0 used twice in same step` |
| Control = Target | `CNOT 1-1` | `Error: Control and target cannot be same` |
| Parameter mismatch | `Rx() 0` | `Error: Rx requires 1 parameter` |

### 📊 BNF Grammar

```bnf
<program>     ::= <line>*
<line>        ::= <time_step> | <comment> | <empty>
<time_step>   ::= <operation> (";" <operation>)*
<operation>   ::= <single_gate> | <two_gate> | <three_gate>
<single_gate> ::= <gate_name> <params>? <qubit_list>
<two_gate>    ::= <gate_name> <qubit> "-" <qubit>
<three_gate>  ::= <gate_name> <qubit> "-" <qubit> "-" <qubit>
<qubit_list>  ::= <qubit> ("," <qubit>)*
<qubit>       ::= [0-9]+
<gate_name>   ::= "H" | "X" | "Y" | "Z" | "CNOT" | ...
<params>      ::= "(" <expression> ")"
<comment>     ::= "#" [^\n]*
```

### 💡 Future Extensions

- Variable support: `angle = π/4; Rx(angle) 0`
- Macro definitions: `macro Bell(a,b) { H a; CNOT a-b }`
- Conditional gates: `if measure(0) then X 1`
- Loop structures: `repeat 5 { H 0; X 0 }`

---

<a name="中文"></a>
# 🇨🇳 中文版本

## Q-Lang: 量子电路描述语言规范

### 📖 概述

Q-Lang是一种文本化量子电路描述语言，用于精确定义量子门的时序和位置，避免图形拖拽的冲突问题。

**版本**: 1.0.0  
**日期**: 2026-01-26  
**作者**: MacQ团队

### 🎯 设计原则

1. **时序即行序**: 从上到下的行代表时间步
2. **并行用分号**: 同一时间步的操作用`;`分隔
3. **简洁明确**: 门名+量子比特，控制位用`-`连接
4. **冲突检测**: 编译前检查语法和物理约束

### 📝 语法规则

#### 基本格式
```
行号 | 语句1; 语句2; 语句3
```

#### 单量子比特门

**语法**: `门名 量子比特列表`

**示例**:
```q
H 0, 2, 5          # 对q0, q2, q5应用H门
X 1, 3             # 对q1, q3应用X门
Rz(π/4) 2          # 带参数的旋转门
```

**支持的门**: `H`, `X`, `Y`, `Z`, `I`, `S`, `T`, `S†`, `T†`, `Rx(θ)`, `Ry(θ)`, `Rz(θ)`

#### 双量子比特门

**语法**: `门名 控制位-目标位`

**示例**:
```q
CNOT 0-1           # q0控制，q1目标
CZ 2-3             # q2控制，q3目标
SWAP 1-4           # 交换q1和q4
```

**支持的门**: `CNOT`, `CZ`, `SWAP`

#### 三量子比特门

**语法**: `门名 控制位1-控制位2-目标位`

**示例**:
```q
Toffoli 0-1-2      # q0,q1控制，q2目标
```

#### 并行操作

**语法**: 同行用`;`分隔

**示例**:
```q
H 0; X 1; Z 2      # 同时对q0,q1,q2应用不同门
CNOT 0-1; H 3      # 同时执行CNOT和H
```

#### 注释
```q
# 这是单行注释
H 0  # 行尾注释
```

### 📋 完整示例

#### 示例1: Bell态制备
```q
# Bell态: (|00⟩ + |11⟩)/√2
H 0
CNOT 0-1
```

#### 示例2: GHZ态（3量子比特）
```q
# GHZ态: (|000⟩ + |111⟩)/√2
H 0
CNOT 0-1
CNOT 0-2
```

#### 示例3: 复杂电路（并行操作）
```q
# 第1步: 初始化
H 0, 2, 4; X 1, 3

# 第2步: 纠缠
CNOT 0-1; CNOT 2-3

# 第3步: 测量基变换
H 1; S 3; T 4

# 第4步: Toffoli门
Toffoli 0-1-2
```

### ⚠️ 冲突检测规则

#### 1. 语法错误检测

| 错误类型 | 示例 | 提示 |
|---------|------|------|
| 门名不存在 | `ABC 0` | `Error: Unknown gate 'ABC'` |
| 量子比特越界 | `H 10` (仅3比特) | `Error: Qubit 10 out of range [0,2]` |
| 参数格式错误 | `Rx(abc) 0` | `Error: Invalid parameter 'abc'` |
| 缺少控制位 | `CNOT 0` | `Error: CNOT requires control-target` |

#### 2. 物理冲突检测

| 冲突类型 | 示例 | 提示 |
|---------|------|------|
| 同时操作同一量子比特 | `H 0; X 0` | `Error: Qubit 0 used twice in same step` |
| 控制位=目标位 | `CNOT 1-1` | `Error: Control and target cannot be same` |
| 参数数量不匹配 | `Rx() 0` | `Error: Rx requires 1 parameter` |

### 📊 BNF语法定义

```bnf
<程序>     ::= <行>*
<行>       ::= <时间步> | <注释> | <空行>
<时间步>   ::= <操作> (";" <操作>)*
<操作>     ::= <单门> | <双门> | <三门>
<单门>     ::= <门名> <参数>? <比特列表>
<双门>     ::= <门名> <比特> "-" <比特>
<三门>     ::= <门名> <比特> "-" <比特> "-" <比特>
<比特列表> ::= <比特> ("," <比特>)*
<比特>     ::= [0-9]+
<门名>     ::= "H" | "X" | "Y" | "Z" | "CNOT" | ...
<参数>     ::= "(" <表达式> ")"
<注释>     ::= "#" [^\n]*
```

### 💡 未来扩展

- 变量支持: `angle = π/4; Rx(angle) 0`
- 宏定义: `macro Bell(a,b) { H a; CNOT a-b }`
- 条件门: `if measure(0) then X 1`
- 循环结构: `repeat 5 { H 0; X 0 }`

---

<a name="日本語"></a>
# 🇯🇵 日本語版

## Q-Lang: 量子回路記述言語仕様

### 📖 概要

Q-Langは、量子ゲートのタイミングと配置を正確に定義するためのテキストベースの量子回路記述言語であり、グラフィカルなドラッグアンドドロップに固有の競合を回避します。

**バージョン**: 1.0.0  
**日付**: 2026-01-26  
**著者**: MacQチーム

### 🎯 設計原則

1. **行順序=時間順序**: 上から下への行が時間の進行を表す
2. **並列処理にセミコロン**: 同一時間ステップの操作は`;`で区切る
3. **簡潔明瞭**: ゲート名+量子ビット、制御ビットは`-`で接続
4. **競合検出**: コンパイル前に構文と物理制約を検証

### 📝 構文規則

#### 基本形式
```
行番号 | ステートメント1; ステートメント2; ステートメント3
```

#### 単一量子ビットゲート

**構文**: `ゲート名 量子ビットリスト`

**例**:
```q
H 0, 2, 5          # q0, q2, q5にHゲートを適用
X 1, 3             # q1, q3にXゲートを適用
Rz(π/4) 2          # パラメータ付き回転ゲート
```

**サポートされるゲート**: `H`, `X`, `Y`, `Z`, `I`, `S`, `T`, `S†`, `T†`, `Rx(θ)`, `Ry(θ)`, `Rz(θ)`

#### 2量子ビットゲート

**構文**: `ゲート名 制御ビット-ターゲットビット`

**例**:
```q
CNOT 0-1           # q0制御、q1ターゲット
CZ 2-3             # q2制御、q3ターゲット
SWAP 1-4           # q1とq4を交換
```

**サポートされるゲート**: `CNOT`, `CZ`, `SWAP`

#### 3量子ビットゲート

**構文**: `ゲート名 制御ビット1-制御ビット2-ターゲットビット`

**例**:
```q
Toffoli 0-1-2      # q0、q1制御、q2ターゲット
```

#### 並列操作

**構文**: 同じ行で`;`で区切る

**例**:
```q
H 0; X 1; Z 2      # 同時操作
CNOT 0-1; H 3      # 並列CNOTとH
```

#### コメント
```q
# 単一行コメント
H 0  # 行末コメント
```

### 📋 完全な例

#### 例1: Bell状態の準備
```q
# Bell状態: (|00⟩ + |11⟩)/√2
H 0
CNOT 0-1
```

#### 例2: GHZ状態（3量子ビット）
```q
# GHZ状態: (|000⟩ + |111⟩)/√2
H 0
CNOT 0-1
CNOT 0-2
```

#### 例3: 並列処理を含む複雑な回路
```q
# ステップ1: 初期化
H 0, 2, 4; X 1, 3

# ステップ2: エンタングルメント
CNOT 0-1; CNOT 2-3

# ステップ3: 測定基底変換
H 1; S 3; T 4

# ステップ4: Toffoliゲート
Toffoli 0-1-2
```

### ⚠️ 競合検出規則

#### 1. 構文エラー

| エラータイプ | 例 | メッセージ |
|------------|---|----------|
| 未知のゲート | `ABC 0` | `Error: Unknown gate 'ABC'` |
| 範囲外の量子ビット | `H 10` (3ビットのみ) | `Error: Qubit 10 out of range [0,2]` |
| 無効なパラメータ | `Rx(abc) 0` | `Error: Invalid parameter 'abc'` |
| 制御ビット欠落 | `CNOT 0` | `Error: CNOT requires control-target` |

#### 2. 物理的競合

| 競合タイプ | 例 | メッセージ |
|----------|---|----------|
| 同じビットを2回使用 | `H 0; X 0` | `Error: Qubit 0 used twice in same step` |
| 制御=ターゲット | `CNOT 1-1` | `Error: Control and target cannot be same` |
| パラメータ不一致 | `Rx() 0` | `Error: Rx requires 1 parameter` |

### 💡 将来の拡張

- 変数サポート: `angle = π/4; Rx(angle) 0`
- マクロ定義: `macro Bell(a,b) { H a; CNOT a-b }`
- 条件ゲート: `if measure(0) then X 1`  
- ループ構造: `repeat 5 { H 0; X 0 }`

---

## 📚 Additional Resources

### Implementation Reference
- [Python Parser Example](https://github.com/sq756/MacQ/examples/qlang_parser.py)
- [GUI Integration Guide](https://github.com/sq756/MacQ/docs/gui_qlang.md)
- [Conflict Validator](https://github.com/sq756/MacQ/macq/qlang/validator.py)

### Community
- GitHub Issues: https://github.com/sq756/MacQ/issues
- Discussions: https://github.com/sq756/MacQ/discussions

---

**Q-Lang: Making Quantum Programming Simple! / 让量子编程更简单！/ 量子プログラミングを簡単に！** ⚛️

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-26  
**License**: MIT  
**Copyright**: MacQ Team © 2026
