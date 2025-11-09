import sys
from PySide6.QtCore import Qt, QThread, Signal, QLineF, QPointF
from PySide6.QtWidgets import QApplication,QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QSlider, QMessageBox, QFrame, QGridLayout
import time
import mesh_viewer
import canvas

# from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QTransform
# from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QLabel

class Worker(QThread):
  def __init__(self, f):
    super().__init__()
    self._f = f

  def run(self):
    self._result = self._f()

  def get_result(self):
    return self._result
  
class MyWindow(QMainWindow):
  def __init__(self):
    super().__init__()

    self._worker = None
    self._create_gui()
    
  def _create_gui(self):
    # Build layout on a central widget
    central = QWidget(self)

    self.setCentralWidget(central)
    self.setWindowTitle("PySide6 Example")

    g = QGridLayout(central)

    # Create UI elements
    self.label = QLabel("Press the button")
    self.button = QPushButton("Click me")
    self.button.clicked.connect(self.on_button_clicked)

    g.addWidget(self.label, 0,0)

    self.radius_label = QLabel("")
    g.addWidget(self.radius_label, 1, 0)

    self.slider = QSlider(Qt.Horizontal)
    self.slider.setRange(0, 1000)

    self.slider.valueChanged.connect(self.update_radius_label)
    self.slider.valueChanged.connect(self.start_worker)

    g.addWidget(self.slider, 2, 0)

    g.addWidget(self.button, 3, 0)

    # self.canvas = canvas.Canvas()
    #g.addWidget(self.canvas, 0, 1, 100, 1)


    self.mesh_viewer = mesh_viewer.MeshViewer()

    g.addWidget(self.mesh_viewer, 0, 2, 100, 1)

    g.setRowStretch(100, 1.0)
    self.update_radius_label()
  
  def get_radius(self):
    return self.slider.value() / 1000.0
  
  def update_radius_label(self):
    radius = self.get_radius()
    self.radius_label.setText(f"Radius: {radius:.2f}")

  def on_button_clicked(self):
    if self._worker is not None:
      QMessageBox.information(self, "Error", "Worker already running!")
      return
    
    self.start_worker()
  
  def start_worker(self):
    if self._worker is not None:
      return
    
    radius = self.get_radius()

    self._worker = Worker(lambda: pytest_lib.get_points(radius))
    self._worker.finished.connect(self.worker_done)
    self._worker.start()

  def worker_done(self):
    self._worker.wait()
    pts = self._worker.get_result()
    self.canvas.set_points(pts)
    self._worker = None

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
        QApplication.quit()

  def closeEvent(self, event):
    if self._worker:
      self._worker.wait()
      self._worker = None

def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()

    return app.exec()

sys.exit(main())