from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_enabled = True
        self.grid_size = 10
        self.alignment_guides = []  # List of (x1, y1, x2, y2) for alignment lines
        self.setStyleSheet("background-color: #f0f0f0;")
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setClipRegion(event.region())  # Optimize repaints
        
        # Draw grid
        if self.grid_enabled:
            pen = QPen(QColor(200, 200, 200), 1, Qt.PenStyle.DotLine)
            painter.setPen(pen)
            for x in range(0, self.width(), self.grid_size):
                painter.drawLine(x, 0, x, self.height())
            for y in range(0, self.height(), self.grid_size):
                painter.drawLine(0, y, self.width(), y)

        # Draw alignment guides
        pen = QPen(QColor(255, 0, 0), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        for guide in self.alignment_guides:
            x1, y1, x2, y2 = map(int, guide)
            painter.drawLine(x1, y1, x2, y2)
            
            # --- THIS IS THE FIX ---
            # The text now shows the correct X or Y coordinate of the line
            if x1 == x2:  # Vertical guide
                painter.drawText(x1 + 5, 20, f"x: {x1}")
            else:  # Horizontal guide
                painter.drawText(20, y1 - 5, f"y: {y1}")

        painter.end()

    def update_grid(self, grid_enabled, grid_size):
        self.grid_enabled = grid_enabled
        self.grid_size = grid_size
        self.update()

    def update_alignment_guides(self, guides):
        self.alignment_guides = guides
        self.update()