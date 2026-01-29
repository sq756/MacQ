#!/bin/bash
# MacQ Build Script - 创建macOS应用包

echo "🚀 开始构建MacQ应用..."

# 1. 清理旧的构建
echo "📦 清理旧构建..."
rm -rf build dist MacQ.app

# 2. 确保C库已编译
echo "🔧 编译C引擎..."
cd c_engine
make clean
make native
cd ..

# 3. 运行PyInstaller
echo "📦 打包应用..."
pyinstaller --clean --noconfirm MacQ.spec

# 4. 检查结果
if [ -d "dist/MacQ.app" ]; then
    echo "✅ 构建成功！"
    echo "📍 应用位置: dist/MacQ.app"
    echo ""
    echo "测试运行:"
    echo "  open dist/MacQ.app"
    echo ""
    echo "创建DMG:"
    echo "  hdiutil create -volname MacQ -srcfolder dist/MacQ.app -ov -format UDZO dist/MacQ-v1.0.0.dmg"
else
    echo "❌ 构建失败！"
    exit 1
fi
