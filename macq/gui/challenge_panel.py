from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton,
    QGroupBox, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from ..core.challenge import ChallengeJudge

class ChallengePanel(QWidget):
    # Signal when a challenge is selected, carrying the challenge_id
    challenge_selected = Signal(str)
    # Signal to request verification of the current circuit
    verify_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.judge = ChallengeJudge()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title = QLabel("🧩 MacQ Challenges")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Challenge List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: #1E2237;
                border: 1px solid #3E445B;
                border-radius: 8px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #2E344B; }
            QListWidget::item:selected { background: #4A90E2; color: white; border-radius: 4px; }
        """)
        for c in self.judge.challenges:
            item = QListWidgetItem(c.title)
            item.setData(Qt.UserRole, c.id)
            self.list_widget.addItem(item)
        
        layout.addWidget(self.list_widget)
        
        # Details Area
        self.details_group = QGroupBox("📋 Level Details")
        self.details_group.setStyleSheet("QGroupBox { color: #A0A0A0; font-weight: bold; }")
        details_layout = QVBoxLayout(self.details_group)
        
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setStyleSheet("background: transparent; border: none; color: #D0D0D0;")
        details_layout.addWidget(self.description_text)
        
        layout.addWidget(self.details_group)
        
        # Verify Button
        self.verify_btn = QPushButton("🚀 Verify Submission")
        self.verify_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #42E695, stop:1 #3BB2B8);
                color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { opacity: 0.9; }
            QPushButton:pressed { background: #2E8B57; }
        """)
        self.verify_btn.clicked.connect(self._on_verify_clicked)
        layout.addWidget(self.verify_btn)
        
        self.list_widget.currentItemChanged.connect(self._on_item_changed)
        
        # Initial state
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _on_item_changed(self, current, previous):
        if not current: return
        challenge_id = current.data(Qt.UserRole)
        challenge = self.judge.get_challenge(challenge_id)
        if challenge:
            self.description_text.setText(challenge.description)
            self.challenge_selected.emit(challenge_id)

    def _on_verify_clicked(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            challenge_id = current_item.data(Qt.UserRole)
            self.verify_requested.emit(challenge_id)

    def show_result(self, result: dict):
        if result['status'] == 'success':
            QMessageBox.information(self, "Success!", f"✨ {result['message']}")
        else:
            QMessageBox.warning(self, "Keep Trying!", f"❌ {result['message']}")
