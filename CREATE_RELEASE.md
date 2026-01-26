# 创建GitHub Release - MacQ v1.0.0

## 方法1: 使用GitHub网页界面（推荐）

### 步骤：
1. 访问: https://github.com/sq756/MacQ/releases/new

2. **填写信息**:
   - Tag version: `v1.0.0`
   - Target: `main`
   - Release title: `MacQ v1.0.0 - 量子电路模拟器`
   
3. **描述**（复制下面内容）:

```markdown
## 🎉 MacQ v1.0.0 首次发布

MacQ是一个专业的量子电路模拟器，具有现代化的macOS原生界面。

### ✨ 核心特性
- **完整量子门集**: H, X, Y, Z, CNOT, CZ, SWAP, Toffoli等
- **高性能C引擎**: 比纯Python快10-20倍
- **Premium界面**: 深色主题、渐变效果、拖拽操作
- **智能可视化**: 自动过滤、突出显示主要量子态

### 📦 下载
- **MacQ-v1.0.0.dmg** - macOS安装器（推荐）

### 系统要求
- macOS 10.13 (High Sierra) 或更高
- 约200MB磁盘空间
- 无需Python环境

### 🚀 快速开始
1. 下载并打开DMG文件
2. 拖拽MacQ.app到Applications
3. 双击启动，开始创建量子电路！

### 📚 示例：创建Bell态
1. 右键q0 → 选择H门
2. 右键q1 → 选择CNOT门
3. 点击"▶ Run Circuit"
4. 观察|00⟩和|11⟩各50%的纠缠态！

欢迎提Issue和PR！🚀⚛️
```

4. **上传文件**:
   - 点击"Attach binaries by dropping them here"
   - 拖入文件: `dist/MacQ-v1.0.0.dmg` (86MB)

5. **发布**:
   - 勾选 "Set as the latest release"
   - 点击 "Publish release"

---

## 方法2: 使用GitHub CLI（命令行）

```bash
# 安装GitHub CLI（如果未安装）
brew install gh

# 登录
gh auth login

# 创建Release并上传DMG
gh release create v1.0.0 \
  dist/MacQ-v1.0.0.dmg \
  --title "MacQ v1.0.0 - 量子电路模拟器" \
  --notes-file RELEASE.md

# 查看Release
gh release view v1.0.0
```

---

## 文件位置
- DMG文件: `dist/MacQ-v1.0.0.dmg` (86 MB)
- Release notes: `RELEASE.md`
- 应用包: `dist/MacQ.app` (334 MB) - 仅上传DMG即可

---

## 注意事项
⚠️ DMG文件已添加到`.gitignore`，不会提交到Git仓库
✅ Release通过GitHub网页上传，不占用仓库空间
📦 用户下载后可直接安装使用
