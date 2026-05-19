#!/usr/bin/env python3
import sys
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, Signal, Slot, QPoint, QRect, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QRadialGradient, QBrush, QFont, QLinearGradient

# Bento Design Tokens
BENTO_BG = QColor(18, 15, 23, 204) # rgba(18, 15, 23, 0.8)
BENTO_BORDER = QColor(47, 41, 58)    # #2F293A
PURPLE_GLOW = QColor(132, 0, 255)    # #8400ff
TEXT_WHITE = QColor(255, 255, 255)
TEXT_MUTED = QColor(255, 255, 255, 100)

TRUTH_GREEN = QColor(46, 204, 113)   # #2ECC71
UNCERTAIN_YELLOW = QColor(241, 196, 15) # #F1C40F
LIE_RED = QColor(231, 76, 60)       # #E74C3C

def interpret_confidence(conf):
    if conf >= 0.8:
        return "Truth", TRUTH_GREEN
    elif conf >= 0.4:
        return "Unsure", UNCERTAIN_YELLOW
    else:
        return "Lie", LIE_RED

class ConfidenceHTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            conf = data.get('confidence', 0.5)
            self.server.overlay.update_signal.emit(conf)
            self.send_response(200)
            self.end_headers()
        except Exception as e:
            print(f"Error handling POST: {e}")

    def log_message(self, format, *args):
        pass

class ConfidenceOverlay(QWidget):
    update_signal = Signal(float)

    def __init__(self):
        super().__init__()
        self.current_score = 1.0
        self.initUI()
        self.update_signal.connect(self.update_gauge)
        
        # Start HTTP server to receive confidence from proxy
        self.server = HTTPServer(('localhost', 9876), ConfidenceHTTPHandler)
        self.server.overlay = self
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def initUI(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Size for "typical widget" - compact and rectangular
        self.widget_w = 220
        self.widget_h = 110
        
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() - self.widget_w - 40, 40, self.widget_w, self.widget_h)
        
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. Draw Bento Card Background
        painter.setBrush(BENTO_BG)
        painter.setPen(QPen(BENTO_BORDER, 1.5))
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.drawRoundedRect(rect, 24, 24)

        # 2. Draw Dot Grid
        dot_spacing = 20
        dot_size = 2
        painter.setBrush(QColor(132, 0, 255, 40))
        painter.setPen(Qt.NoPen)
        for x in range(dot_spacing, self.width(), dot_spacing):
            for y in range(dot_spacing, self.height(), dot_spacing):
                painter.drawEllipse(x, y, dot_size, dot_size)

        # 3. Draw Header
        font = QFont("Inter", 8, QFont.Bold)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 2)
        painter.setFont(font)
        painter.setPen(TEXT_MUTED)
        painter.drawText(20, 30, "OPENOCCHIO PRO")

        # 4. Draw Score
        score = getattr(self, 'current_score', 1.0)
        label, color = interpret_confidence(score)
        
        font_score = QFont("Inter", 24, QFont.Black)
        painter.setFont(font_score)
        painter.setPen(TEXT_WHITE)
        painter.drawText(20, 70, f"{int(score*100)}%")

        # 5. Draw Truth Bar
        bar_x = 100
        bar_y = 58
        bar_h = 6
        bar_w = self.width() - bar_x - 20
        
        # Bg bar
        painter.setBrush(QColor(255, 255, 255, 20))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 3, 3)
        
        # Progress bar
        grad = QLinearGradient(bar_x, 0, bar_x + bar_w * score, 0)
        grad.setColorAt(0, PURPLE_GLOW)
        grad.setColorAt(1, color)
        painter.setBrush(grad)
        painter.drawRoundedRect(bar_x, bar_y, bar_w * score, bar_h, 3, 3)

        # 6. Draw Status Dot & Text
        painter.setBrush(color)
        painter.drawEllipse(20, 85, 8, 8)
        
        font_status = QFont("Inter", 9, QFont.Bold)
        painter.setFont(font_status)
        painter.setPen(color)
        painter.drawText(35, 93, label.upper())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()

    @Slot(float)
    def update_gauge(self, score):
        self.current_score = score
        self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = ConfidenceOverlay()
    sys.exit(app.exec())
