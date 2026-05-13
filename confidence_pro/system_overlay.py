#!/usr/bin/env python3
import sys
import threading
import time
import pyperclip
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from wrapper import compute_confidence, interpret_confidence

class ConfidenceOverlay(QWidget):
    update_signal = Signal(float)

    def __init__(self):
        super().__init__()
        self.initUI()
        
        self.last_clipboard = ""
        self.is_processing = False
        self.update_signal.connect(self.update_gauge)
        
        # Start Clipboard Watcher
        self.watcher_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        self.watcher_thread.start()

    def initUI(self):
        # Always on top and frameless
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Position in bottom right
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() - 250, screen.height() - 150, 220, 100)
        
        layout = QVBoxLayout()
        self.container = QWidget()
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            #container {
                background-color: white;
                border: 2px solid #eee;
                border-radius: 15px;
            }
            QLabel { color: #2c3e50; font-family: 'Arial'; }
            QProgressBar {
                border: 2px solid #eee;
                border-radius: 5px;
                text-align: center;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 3px;
            }
        """)
        
        inner_layout = QVBoxLayout(self.container)
        
        self.header = QLabel("OpenOcchio Gauge")
        self.header.setStyleSheet("font-weight: bold; font-size: 12px; color: #7f8c8d;")
        inner_layout.addWidget(self.header)
        
        self.progress = QProgressBar()
        self.progress.setValue(0)
        inner_layout.addWidget(self.progress)
        
        label_layout = QHBoxLayout()
        self.score_label = QLabel("0.00")
        self.score_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        label_layout.addWidget(self.score_label)
        
        self.status_label = QLabel("READY")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 10px;")
        label_layout.addWidget(self.status_label)
        
        inner_layout.addLayout(label_layout)
        layout.addWidget(self.container)
        self.setLayout(layout)
        
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()

    @Slot(float)
    def update_gauge(self, score):
        label, color_code, score_text = interpret_confidence(score)
        
        hex_color = "#2ecc71" # Green
        if score < 0.8: hex_color = "#f1c40f" # Yellow
        if score < 0.6: hex_color = "#e67e22" # Orange
        if score < 0.4: hex_color = "#e74c3c" # Red
        
        self.progress.setStyleSheet(f"QProgressBar::chunk {{ background-color: {hex_color}; }}")
        self.progress.setValue(int(score * 100))
        self.score_label.setText(f"{score:.2f}")
        self.score_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {hex_color};")
        self.status_label.setText(score_text.upper())
        self.status_label.setStyleSheet(f"font-weight: bold; font-size: 10px; color: {hex_color};")

    def monitor_clipboard(self):
        while True:
            try:
                current_clip = pyperclip.paste()
                if current_clip != self.last_clipboard and len(current_clip) > 10 and not self.is_processing:
                    self.last_clipboard = current_clip
                    self.is_processing = True
                    # We can't update GUI directly from thread, but we can emit a placeholder if needed
                    # For simplicity, we just run the blocking logic
                    conf = compute_confidence(current_clip)
                    self.update_signal.emit(conf)
                    self.is_processing = False
                time.sleep(1)
            except Exception:
                time.sleep(5)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = ConfidenceOverlay()
    sys.exit(app.exec())
