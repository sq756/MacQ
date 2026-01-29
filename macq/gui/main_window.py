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
    QScrollArea, QGroupBox, QRadioButton, QSlider, QDoubleSpinBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QAction, QKeySequence, QColor, QIcon

from ..c_bridge import version
from ..qlang.compiler import QLangDecompiler
from .styles import (
    MAIN_WINDOW_STYLE, RUN_BUTTON_STYLE, CLEAR_BUTTON_STYLE
)
from .qlang_editor import QLangEditorWidget
from .challenge_panel import ChallengePanel
from .oracle_dialog import OracleDialog


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
        from PySide6.QtWidgets import QTabWidget
        self.left_tabs = QTabWidget()
        self.left_tabs.setTabPosition(QTabWidget.West) # Modern vertical tabs
        self.left_tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: #0F111A; }
            QTabBar::tab { 
                background: #1E2237; color: #A0A0A0; padding: 15px; 
                margin-bottom: 2px; border-top-right-radius: 4px; border-bottom-right-radius: 4px;
            }
            QTabBar::tab:selected { background: #4A90E2; color: white; }
        """)
        
        self.gate_palette = GatePaletteWidget()
        self.challenge_panel = ChallengePanel()
        
        self.left_tabs.addTab(self.gate_palette, "⚛️ Gates")
        self.left_tabs.addTab(self.challenge_panel, "🧩 Challenges")
        
        main_splitter.addWidget(self.left_tabs)
        
        # Center: Vertical splitter for circuit editor and Q-Lang editor
        center_splitter = QSplitter(Qt.Vertical)
        
        # Wrap circuit editor in a scroll area
        self.circuit_scroll = QScrollArea()
        self.circuit_scroll.setWidget(self.circuit_editor)
        self.circuit_scroll.setWidgetResizable(False) # Honor fixed size exactly
        self.circuit_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.circuit_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.circuit_scroll.viewport().setStyleSheet("background-color: #0F111A;")
        self.circuit_scroll.setStyleSheet("QScrollArea { border: none; background: #0F111A; }")
        
        center_splitter.addWidget(self.circuit_scroll)
        center_splitter.addWidget(self.qlang_editor)
        center_splitter.setSizes([500, 300]) # 5:3 ratio
        main_splitter.addWidget(center_splitter)
        
        # Right: Visualizer & Settings
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Simulation Settings Group
        self.settings_group = QGroupBox("🧪 实验配置 (Simulation Settings)")
        self.settings_group.setStyleSheet("""
            QGroupBox {
                background: rgba(40, 44, 65, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding-top: 25px;
                margin-top: 10px;
                font-weight: bold;
                color: #A0A0A0;
            }
        """)
        settings_layout = QVBoxLayout(self.settings_group)
        
        # Mode Toggle
        mode_layout = QHBoxLayout()
        self.ideal_radio = QRadioButton("Ideal (理论)")
        self.noisy_radio = QRadioButton("Noisy (实验)")
        self.ideal_radio.setChecked(True)
        mode_layout.addWidget(self.ideal_radio)
        mode_layout.addWidget(self.noisy_radio)
        settings_layout.addLayout(mode_layout)
        
        # Shots Control
        shots_layout = QHBoxLayout()
        shots_layout.addWidget(QLabel("Shots (采样):"))
        self.shots_spin = QSpinBox()
        self.shots_spin.setRange(1, 100000)
        self.shots_spin.setValue(1024)
        shots_layout.addWidget(self.shots_spin)
        settings_layout.addLayout(shots_layout)
        
        # Noise Level
        noise_layout = QHBoxLayout()
        noise_layout.addWidget(QLabel("Noise Level (噪声):"))
        self.noise_spin = QDoubleSpinBox()
        self.noise_spin.setRange(0.0, 1.0)
        self.noise_spin.setSingleStep(0.01)
        self.noise_spin.setValue(0.01)
        noise_layout.addWidget(self.noise_spin)
        settings_layout.addLayout(noise_layout)
        
        right_layout.addWidget(self.settings_group)
        right_layout.addWidget(self.visualizer)
        
        main_splitter.addWidget(right_panel)
        
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
        
        optimize_action = QAction("优化电路(&O)", self)
        optimize_action.triggered.connect(self.circuit_editor.optimize_circuit)
        circuit_menu.addAction(optimize_action)
        
        circuit_menu.addSeparator()
        
        hamiltonian_action = QAction("查看哈密顿量矩阵(&H)", self)
        hamiltonian_action.triggered.connect(self._show_hamiltonian)
        circuit_menu.addAction(hamiltonian_action)
        
        # 视图菜单 (Theme)
        view_menu = menubar.addMenu("视图(&V)")
        theme_menu = view_menu.addMenu("颜色主题")
        
        from .styles import THEMES
        for theme_name in THEMES:
            theme_action = QAction(theme_name, self)
            theme_action.triggered.connect(lambda checked, name=theme_name: self._apply_theme(name))
            theme_menu.addAction(theme_action)
        
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
        
        # Update geometry and display
        self.circuit_editor._update_size()
        self.circuit_editor.update()
        self._update_statusbar()
        self.statusBar().showMessage(f'Compiled {len(gates)} gates from Q-Lang', 2000)
        
    def _connect_signals(self):
        """连接信号槽"""
        # 电路改变时更新可视化、代码和状态栏
        self.circuit_editor.circuit_changed.connect(self._on_circuit_changed)
        self.circuit_editor.circuit_changed.connect(self._sync_circuit_to_code)
        
        # 门被添加时的反馈
        self.circuit_editor.gate_added.connect(self._on_gate_added)
        
        # Palette Signals
        self.gate_palette.gate_selected.connect(self._on_gate_palette_selected)
        
        # Q-Lang editor signals
        self.qlang_editor.code_compiled.connect(self._sync_code_to_circuit)
        self.qlang_editor.qubit_count_detected.connect(self.qubit_spinner.setValue)
        
        # Challenge Signals
        self.challenge_panel.verify_requested.connect(self._verify_challenge)
        
        # Toolbar buttons
        self.run_btn.clicked.connect(self._run_circuit)
        self.qubit_spinner.valueChanged.connect(self._on_qubit_count_changed)
        
        # Set initial qubit count for Q-Lang editor
        self.qlang_editor.set_qubit_count(self.qubit_spinner.value())
        
    def _on_gate_palette_selected(self, gate_name):
        """Handle gate selection from palette, including special Oracle/Algorithms"""
        if gate_name == "Oracle":
            dialog = OracleDialog(self.qubit_spinner.value(), self)
            dialog.gates_generated.connect(self._add_multiple_gates)
            dialog.exec()
        elif gate_name == "QFT":
            # Add a 3-qubit QFT as a template if enough qubits
            self._add_qft_template()
        elif gate_name == "Grover":
            self._add_grover_template()
        # Non-special gates are handled by drag-and-drop usually, 
        # but we could also allow click-to-add for convenience
        
    def _add_multiple_gates(self, gate_list):
        """Add a list of gates (from Oracle or Macro) to the circuit"""
        for g in gate_list:
            # We add them consecutively
            self.circuit_editor.add_gate(g['type'], g['qubit'] if 'qubit' in g else g['qubits'][0], 
                                          control=g['qubits'][:-1] if 'qubits' in g and len(g['qubits']) > 1 else None)
        self._sync_circuit_to_code()
        self.circuit_editor.update()

    def _add_qft_template(self):
        """Add a standard QFT template for first 3 qubits"""
        if self.qubit_spinner.value() < 3: return
        qft_gates = [
            {'type': 'H', 'qubit': 0},
            {'type': 'CZ', 'qubits': [1, 0]}, # Simplified CP gate
            {'type': 'CZ', 'qubits': [2, 0]},
            {'type': 'H', 'qubit': 1},
            {'type': 'CZ', 'qubits': [2, 1]},
            {'type': 'H', 'qubit': 2},
            {'type': 'SWAP', 'qubits': [0, 2]}
        ]
        self._add_multiple_gates(qft_gates)

    def _add_grover_template(self):
        """Add a Grover Diffusion operator for 2 qubits"""
        if self.qubit_spinner.value() < 2: return
        grover_gates = [
            {'type': 'H', 'qubit': 0}, {'type': 'H', 'qubit': 1},
            {'type': 'X', 'qubit': 0}, {'type': 'X', 'qubit': 1},
            {'type': 'H', 'qubit': 1},
            {'type': 'CNOT', 'qubits': [0, 1]},
            {'type': 'H', 'qubit': 1},
            {'type': 'X', 'qubit': 0}, {'type': 'X', 'qubit': 1},
            {'type': 'H', 'qubit': 0}, {'type': 'H', 'qubit': 1}
        ]
        self._add_multiple_gates(grover_gates)

    def _on_circuit_changed(self):
        """电路改变时的处理"""
        self._update_statusbar()
        self.visualizer.clear()
        
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
        """打开 .qlang 电路文件"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开 Q-Lang 文件", "", "Q-Lang Files (*.qlang *.ql);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                self.qlang_editor.set_code(code)
                self.qlang_editor.compile_code()
                self.statusBar().showMessage(f"已加载: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "读取错误", f"无法打开文件:\n{str(e)}")
        
    def _save_circuit(self):
        """保存为 .qlang 电路文件"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存 Q-Lang 文件", "", "Q-Lang Files (*.qlang);;All Files (*)"
        )
        
        if file_path:
            if not file_path.endswith('.qlang'):
                file_path += '.qlang'
            try:
                code = self.qlang_editor.get_code()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                self.statusBar().showMessage(f"已保存: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "保存错误", f"无法保存文件:\n{str(e)}")
        
    def _verify_challenge(self, challenge_id: str):
        """Run the circuit and verify against the challenge target"""
        from ..c_bridge import QuantumState
        
        # Get current circuit data
        gates = self.circuit_editor.gates
        qubits = self.circuit_editor.get_qubit_count()
        
        try:
            state = QuantumState(qubits)
            for gate in gates:
                state.apply_gate(gate)
            
            vec = state.get_statevector()
            
            # Judge result
            result = self.challenge_panel.judge.verify(challenge_id, vec)
            
            # Show feedback
            self.challenge_panel.show_result(result)
            
        except Exception as e:
            QMessageBox.critical(self, "Execution Error", f"Could not simulate circuit: {e}")

    def _export_image(self):
        """导出电路图片 (PNG/JPG)"""
        from PySide6.QtWidgets import QFileDialog
        from PySide6.QtGui import QPixmap
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出电路图片", "", "Images (*.png *.jpg);;All Files (*)"
        )
        
        if file_path:
            try:
                # Grab the circuit editor content
                pixmap = self.circuit_editor.grab()
                pixmap.save(file_path)
                self.statusBar().showMessage(f"已导出图片: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "导出错误", f"无法导出图片:\n{str(e)}")
        
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
        """运行电路，支持 Ideal vs Experimental 模式"""
        try:
            self.status_label.setText("正在执行电路...")
            
            # 读取模拟配置
            is_noisy = self.noisy_radio.isChecked()
            shots = self.shots_spin.value()
            noise_level = self.noise_spin.value() if is_noisy else 0.0
            
            # 1. 执行电路 (获取理论态)
            result_state = self.circuit_editor.execute_circuit(noise_level=noise_level)
            
            if result_state:
                # 2. 如果是实验模式，进行采样
                counts = None
                if is_noisy:
                    self.status_label.setText(f"正在进行实验采样 (Shots: {shots})...")
                    counts = result_state.sample_counts(shots)
                
                # 3. 更新可视化
                # 注意：如果是 Noisy 模式，result_state 是带噪态，theo_probs 将反映噪声后的分布
                self.visualizer.update_state(result_state, counts=counts, shots=shots if is_noisy else None)
                
                self.status_label.setText("电路运行完成" + (" (Noisy/Experimental)" if is_noisy else " (Ideal)"))
            else:
                self.status_label.setText("电路为空")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, "执行错误",
                f"电路执行时发生错误:\n{str(e)}"
            )
            self.status_label.setText("执行失败")
            
    def _show_hamiltonian(self):
        """计算并显示电路的哈密顿量/幺正矩阵"""
        from .hamiltonian_dialog import HamiltonianDialog
        
        try:
            # Sync qubit count before calculation
            self.circuit_editor.num_qubits = self.qubit_spinner.value()
            self.status_label.setText("正在计算矩阵...")
            
            # 计算矩阵
            matrix = self.circuit_editor.get_circuit_unitary()
            
            # 显示对话框
            dialog = HamiltonianDialog(matrix, self)
            dialog.exec()
            
            self.status_label.setText("矩阵计算完成")
            
        except Exception as e:
            QMessageBox.critical(
                self, "计算错误",
                f"计算哈密顿量矩阵时发生错误:\n{str(e)}"
            )
            self.status_label.setText("计算失败")
            
    def _apply_theme(self, theme_name):
        """切换应用主题"""
        from .styles import THEMES
        theme = THEMES.get(theme_name)
        if not theme: return
        
        self.setStyleSheet(theme.main_window)
        self.gate_palette.setStyleSheet(theme.palette)
        self.circuit_editor.setStyleSheet(theme.circuit)
        self.visualizer.setStyleSheet(theme.visualizer)
        self.run_btn.setStyleSheet(theme.run_btn)
        self.clear_btn.setStyleSheet(theme.clear_btn)
        
        self.status_label.setText(f"已切换主题: {theme_name}")
        
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
