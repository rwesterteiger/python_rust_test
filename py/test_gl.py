# run_me_first_gl_smoke.py
import os, sys
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtOpenGL import QOpenGLWindow
from PySide6.QtWidgets import QApplication
from PySide6 import QtCore

# Helpful logs from Qt's GL stack (optional)
os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.gl=true;qt.opengl=true")

class Win(QOpenGLWindow):
    def initializeGL(self):
        ctx = self.context()
        fmt = ctx.format()
        print("Qt:", QtCore.qVersion())
        print("GL version:", fmt.majorVersion(), fmt.minorVersion(), "profile:", fmt.profile())
        f = ctx.functions()
        # constants (QOpenGLFunctions on macOS doesn't expose enums)
        GL_COLOR_BUFFER_BIT = 0x00004000
        f.glClearColor(0.2, 0.1, 0.3, 1.0)
        f.glClear(GL_COLOR_BUFFER_BIT)

    def resizeGL(self, w, h):
        self.context().functions().glViewport(0, 0, w, h)

    def paintGL(self):
        f = self.context().functions()
        GL_COLOR_BUFFER_BIT = 0x00004000
        f.glClear(GL_COLOR_BUFFER_BIT)

if __name__ == "__main__":
    setup_format()
    app = QApplication(sys.argv)
    w = Win()
    w.resize(640, 480)
    w.show()
    sys.exit(app.exec())
