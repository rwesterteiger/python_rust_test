from PySide6.QtWidgets import QApplication,QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QSlider, QMessageBox, QFrame, QGridLayout
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QTransform
from PySide6.QtCore import Qt, QThread, Signal, QLineF, QPointF


class Canvas(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Fixed size as requested
        self.setFixedSize(1024, 1024)

        # Frame look
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)
        self.setMidLineWidth(0)

        # State
        self._bg = self.palette().base().color()
        self._points = []  # stored in LOGICAL space (-1..1, -1..1)
        self.setMouseTracking(True)

    def set_points(self, pts):
      self._points = pts
      self.update()

    # setup coord system from (-1,-1) to (1,1)
    def _logical_transform(self, rect):
        """
        Map logical coords [-1,1]x[-1,1] to the widget's content rect.
        Logical origin at center; y grows UPWARDS (so we flip Y).
        """
        t = QTransform()
        # move origin to content center (device coords)
        t.translate(rect.center().x(), rect.center().y())
        # scale logical units to half-width/half-height, flip Y
        t.scale(rect.width() / 2.0, -rect.height() / 2.0)
        return t

    def device_to_logical(self, pos):
        """Convert a device QPointF to logical coords."""
        rect = self.contentsRect()
        T = self._logical_transform(rect)
        inv, ok = T.inverted()
        if ok:
            return inv.map(pos)
        return QPointF(0.0, 0.0)

    # --- Interaction ---------------------------------------------------------
    def mouseMoveEvent(self, e):
        pass
        # Convert to logical coords and store if inside the [-1,1] square
        #lp = self.device_to_logical(e.position())
        #if -1.0 <= lp.x() <= 1.0 and -1.0 <= lp.y() <= 1.0:
        #    self._points.append(lp)
        #    self.update()

    def clear(self):
        self._points.clear()
        self.update()

    # --- Painting ------------------------------------------------------------
    def paintEvent(self, event):
        # 1) Let QFrame paint its border
        super().paintEvent(event)

        rect = self.contentsRect()
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)

        # Fill content background (device coords)
        p.fillRect(rect, self._bg)

        # Clip to content area
        p.setClipRect(rect)

        # 2) Switch to logical coords (-1..1, -1..1), y up
        p.setTransform(self._logical_transform(rect))

        PEN_WIDTH = 0.004
        # Cosmetic pens keep constant pixel width despite transforms
        axis_pen = QPen(QColor(50, 50, 50, 255), PEN_WIDTH)       # 0 => cosmetic
        grid_pen = QPen(QColor(64, 64, 64, 64), PEN_WIDTH)

        # Grid (logical coords)
        p.setPen(grid_pen)

        GRID_N = 5

        for i in range(1, GRID_N):
          k = i / GRID_N
          p.drawLine(QLineF( k, -1.0,  k, 1.0))
          p.drawLine(QLineF(-k, -1.0, -k, 1.0))

          p.drawLine(QLineF(-1.0,  k, 1.0,  k))
          p.drawLine(QLineF(-1.0, -k, 1.0, -k))
        # Axes
        p.setPen(axis_pen)
        p.drawLine(-1.0, 0.0, 1.0, 0.0)  # x-axis
        p.drawLine(0.0, -1.0, 0.0, 1.0)  # y-axis

        # Points drawn in logical space
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(30, 144, 255, 220)))
        r = 0.02  # logical radius (~2% of height/width)
        for pt in self._points:
          print(pt)
          pt = QPointF(pt.x, pt.y)
          p.drawEllipse(pt, r, r)

        # 3) If you need device-space text/UI overlays, reset transform:
        p.resetTransform()
        p.setPen(QColor(60, 60, 60))
        p.drawText(rect.adjusted(8, 6, -8, -6), Qt.AlignTop | Qt.AlignLeft, "Logical coords: (-1,-1) bottom-left to (1,1) top-right")

