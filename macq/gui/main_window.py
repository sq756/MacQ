"""
MacQ GUI - Main Window
Mac-Native Quantum Computing Software

Copyright (c) 2026 MacQ Development Team
Licensed under MIT License
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QMenuBar, QMenu, QToolBar,
    QLabel, QPushButton, QMessageBox, QGraphicsDropShadowEffect, QSpinBox, 
    QScrollArea
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QAction, QKeySequence, QColor, QIcon

from ..c_bridge import version
from ..qlang.compiler import QLangDecompiler
from .styles import (
    MAIN_WINDOW_STYLE, RUN_BUTTON_STYLE, CLEAR_BUTTON_STYLE
)
from .gate_palette import GatePaletteWidget
from .circuit_editor import CircuitEditorWidget
from .visualizer import VisualizationWidget
from .qlang_editor import QLangEditorWidget


class MainWindow(QMainWindow):
    """MacQ主窗口 - 现代高级设计"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MacQ - Quantum Circuit Simulator")
        self.setGeometry(100, 100, 1400, 850)
        
        # 应用主样式
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        # 初始化组件
        self._init_ui()
        self._create_menus()
        self._create_toolbar()
        self._create_statusbar()
        
        # 连接信号
        self._connect_signals()
        
    def _init_ui(self):
        """初始化UI布局"""
        # 中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Initialize components
        self.gate_palette = GatePaletteWidget()
        self.circuit_editor = CircuitEditorWidget()
        self.visualizer = VisualizationWidget()
        self.qlang_editor = QLangEditorWidget()
        self.decompiler = QLangDecompiler()

        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left: Gate palette
        main_splitter.addWidget(self.gate_palette)
        
        # Center: Vertical splitter for circuit editor and Q-Lang editor
        center_splitter = QSplitter(Qt.Vertical)
        
        # Wrap circuit editor in a scroll area
        self.circuit_scroll = QScrollArea()
        self.circuit_scroll.setWidget(self.circuit_editor)
        self.circuit_scroll.setWidgetResizable(True)
        self.circuit_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #0F111A;
            }
            QScrollBar:horizontal, QScrollBar:vertical {
                border: none;
                background: #1E2237;
                width: 10px;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal, QScrollBar::handle:vertical {
                background: #4A90E2;
                min-width: 20px;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                border: none;
                background: none;
            }
        """)
        
        center_splitter.addWidget(self.circuit_scroll)
        center_splitter.addWidget(self.qlang_editor)
        center_splitter.setSizes([400, 300])  # Initial sizes
        main_splitter.addWidget(center_splitter)
        
        # Right: Visualizer
        main_splitter.addWidget(self.visualizer)
        
        # Set initial sizes for the main splitter (e.g., 1:2:1)
        main_splitter.setSizes([200, 800, 400])
        
        main_layout.addWidget(main_splitter)
        
    def _create_menus(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        new_action = QAction("新建电路(&N)", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self._new_circuit)
        file_menu.addAction(new_action)
        
        open_action = QAction("打开...(&O)", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._open_circuit)
        file_menu.addAction(open_action)
        
        save_action = QAction("保存(&S)", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._save_circuit)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("导出图片...(&E)", self)
        export_action.triggered.connect(self._export_image)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("退出(&Q)", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        
        undo_action = QAction("撤销(&U)", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.setEnabled(False)  # TODO: 实现撤销功能
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("重做(&R)", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.setEnabled(False)  # TODO: 实现重做功能
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        clear_action = QAction("清空电路(&C)", self)
        clear_action.triggered.connect(self._clear_circuit)
        edit_menu.addAction(clear_action)
        
        # 电路菜单
        circuit_menu = menubar.addMenu("电路(&C)")
        
        add_qubit_action = QAction("添加量子比特(&A)", self)
        add_qubit_action.triggered.connect(self._add_qubit)
        circuit_menu.addAction(add_qubit_action)
        
        remove_qubit_action = QAction("删除量子比特(&R)", self)
        remove_qubit_action.triggered.connect(self._remove_qubit)
        circuit_menu.addAction(remove_qubit_action)
        
        circuit_menu.addSeparator()
        
        run_action = QAction("运行电路(&R)", self)
        run_action.setShortcut(Qt.Key_F5)
        run_action.triggered.connect(self._run_circuit)
        circuit_menu.addAction(run_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于MacQ(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # 运行按钮 - 渐变样式
        self.run_btn = QPushButton("▶ Run Circuit")
        self.run_btn.setStyleSheet(RUN_BUTTON_STYLE)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(91, 134, 229, 100))
        shadow.setOffset(0, 4)
        self.run_btn.setGraphicsEffect(shadow)
        
        toolbar.addWidget(self.run_btn)
        toolbar.addSeparator()
        
        # 量子比特控制
        qubit_label = QLabel("  Qubits: ")
        qubit_label.setStyleSheet("color: #B0B0B0; font-weight: 600;")
        toolbar.addWidget(qubit_label)
        
        self.qubit_spinner = QSpinBox()
        self.qubit_spinner.setMinimum(1)
        self.qubit_spinner.setMaximum(25)  # Increased from 10 to 25 for Shor's algorithm
        self.qubit_spinner.setValue(3)
        toolbar.addWidget(self.qubit_spinner)
        
        toolbar.addSeparator()
        
        # 清空按钮 - 红色渐变
        self.clear_btn = QPushButton("🗑 Clear")
        self.clear_btn.setStyleSheet(CLEAR_BUTTON_STYLE)
        self.clear_btn.clicked.connect(self._clear_circuit)
        
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(12)
        shadow2.setColor(QColor(226, 74, 74, 80))
        shadow2.setOffset(0, 3)
        self.clear_btn.setGraphicsEffect(shadow2)
        
        toolbar.addWidget(self.clear_btn)
        
    def _create_statusbar(self):
        """创建状态栏"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # 左侧状态信息
        self.status_label = QLabel("就绪")
        self.statusbar.addWidget(self.status_label)
        
        # 右侧信息
        self.info_label = QLabel("")
        self.statusbar.addPermanentWidget(self.info_label)
        
        self._update_statusbar()
        
    def _sync_circuit_to_code(self):
        """Sync visual circuit to Q-Lang code"""
        # Get gates from circuit editor
        gates = self.circuit_editor.gates
        
        if not gates:
            self.qlang_editor.set_code("# Empty circuit\n")
            return
        
        # Decompile to Q-Lang
        code = self.decompiler.decompile(gates, self.qubit_spinner.value())
        
        # Update editor (without triggering recompile)
        self.qlang_editor.set_code(code)
    
    def _sync_code_to_circuit(self, gates):
        """Sync Q-Lang code to visual circuit"""
        # Clear current circuit
        self.circuit_editor.clear_circuit()
        
        # Add compiled gates
        for gate in gates:
            self.circuit_editor.gates.append(gate)
        
        # Update display
        self.circuit_editor.update()
        self.statusBar().showMessage(f'Compiled {len(gates)} gates from Q-Lang', 2000)
        
    def _connect_signals(self):
        """连接信号槽"""
        # 电路改变时更新可视化和代码
        self.circuit_editor.circuit_changed.connect(
            self._on_circuit_changed
        )
        self.circuit_editor.circuit_changed.connect(self._sync_circuit_to_code)
        
        # 门被添加时的反馈
        self.circuit_editor.gate_added.connect(
            self._on_gate_added
        )
        
        # Q-Lang editor signals
        self.qlang_editor.code_compiled.connect(self._sync_code_to_circuit)
        
        # Toolbar buttons
        self.run_btn.clicked.connect(self._run_circuit)
        self.qubit_spinner.valueChanged.connect(self._on_qubit_count_changed)
        
        # Set initial qubit count for Q-Lang editor
        self.qlang_editor.set_qubit_count(self.qubit_spinner.value())
        
    def _on_circuit_changed(self):
        """电路改变时的处理"""
        self._update_statusbar()
        
    def _on_gate_added(self, gate_type, qubit):
        """门被添加时的反馈"""
        self.status_label.setText(f"已添加 {gate_type} 门到 q[{qubit}]")
        
    def _on_qubit_count_changed(self, count):
        """量子比特数改变"""
        self.circuit_editor.set_qubit_count(count)
        self.qlang_editor.set_qubit_count(count)  # Update Q-Lang validator
        self._update_statusbar()
        
    def _update_statusbar(self):
        """更新状态栏信息"""
        num_qubits = self.circuit_editor.get_qubit_count()
        num_gates = self.circuit_editor.get_gate_count()
        
        self.info_label.setText(
            f"{num_qubits} 量子比特 | {num_gates} 个门 | {version()}"
        )
        
    def _new_circuit(self):
        """新建电路"""
        reply = QMessageBox.question(
            self, '新建电路',
            '确定要新建电路吗？当前电路将被清空。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._clear_circuit()
            
    def _open_circuit(self):
        """打开电路文件"""
        # TODO: 实现电路加载
        QMessageBox.information(
            self, "打开电路",
            "电路加载功能即将推出！"
        )
        
    def _save_circuit(self):
        """保存电路"""
        # TODO: 实现电路保存
        QMessageBox.information(
            self, "保存电路",
            "电路保存功能即将推出！"
        )
        
    def _export_image(self):
        """导出电路图片"""
        # TODO: 实现图片导出
        QMessageBox.information(
            self, "导出图片",
            "图片导出功能即将推出！"
        )
        
    def _clear_circuit(self):
        """清空电路"""
        self.circuit_editor.clear_circuit()
        self.visualizer.clear()
        self.status_label.setText("电路已清空")
        
    def _add_qubit(self):
        """添加量子比特"""
        current = self.qubit_spinbox.value()
        self.qubit_spinbox.setValue(current + 1)
        
    def _remove_qubit(self):
        """删除量子比特"""
        current = self.qubit_spinbox.value()
        if current > 1:
            self.qubit_spinbox.setValue(current - 1)
            
    def _run_circuit(self):
        """运行电路"""
        try:
            self.status_label.setText("正在执行电路...")
            
            # 执行电路
            result_state = self.circuit_editor.execute_circuit()
            
            if result_state:
                # 更新可视化
                self.visualizer.update_state(result_state)
                self.status_label.setText("电路执行完成")
            else:
                self.status_label.setText("电路为空")
                
        except Exception as e:
            QMessageBox.critical(
                self, "执行错误",
                f"电路执行时发生错误:\n{str(e)}"
            )
            self.status_label.setText("执行失败")
            
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于MacQ",
            f"""<h2>MacQ - Mac原生量子计算仿真软件</h2>
            <p><b>版本:</b> {version()}</p>
            <p><b>描述:</b> 高性能量子计算仿真桌面应用</p>
            <p><b>特性:</b></p>
            <ul>
                <li>C语言核心引擎</li>
                <li>Apple Silicon优化</li>
                <li>可视化量子电路编辑器</li>
                <li>实时概率分布图表</li>
            </ul>
            <p><b>许可证:</b> MIT License</p>
            <p><b>©</b> 2026 MacQ Development Team</p>
            """
        )
