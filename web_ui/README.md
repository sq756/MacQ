# MacQ Web UI - 3D量子可视化

## 启动方式

### 1. 启动后端服务器
```bash
cd web_ui
python server.py
```

### 2. 打开浏览器
访问: http://localhost:5000

## 功能特性

### 🌐 3D可视化
- **Bloch球面**: 实时3D量子态表示
- **粒子场**: WebGL粒子效果背景
- **流畅动画**: 60fps渲染

### ⚛️ 量子门操作
- 拖拽门到电路区域
- 实时电路显示
- 支持所有基础量子门

### 📊 实时图表
- Chart.js概率分布图
- 动态更新
- 美观的渐变配色

### 🎨 现代设计
- Glassmorphism毛玻璃效果
- 深色渐变主题
- 响应式布局

## 技术栈
- **Frontend**: HTML5 + Three.js + Chart.js
- **Backend**: Flask + Python
- **Quantum Engine**: MacQ C核心

## 浏览器要求
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- 需要WebGL 2.0支持
