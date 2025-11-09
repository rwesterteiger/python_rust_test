from array import array
import sys, os
from math import sin, cos, pi
os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.gl=true;qt.opengl=true")

import ctypes

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QMatrix4x4, QVector3D, QSurfaceFormat 
from PySide6.QtOpenGL import (
    QOpenGLDebugLogger, QOpenGLDebugMessage,
    QOpenGLShaderProgram, QOpenGLShader,
    QOpenGLBuffer, QOpenGLVertexArrayObject,
)

import sys, os, traceback
import functools


def fatal_on_exception():
    def _decorate(func):
      @functools.wraps(func)
      def _w(*args, **kwargs):
          try:
              return func(*args, **kwargs)
          except BaseException as e:
              tb = traceback.TracebackException.from_exception(
                  e, capture_locals=True
              )
              print("".join(tb.format()), file=sys.stderr, flush=True)
              os._exit(1  )
      return _w
    return _decorate

# Numeric GL enums (don’t mix PyOpenGL here)
GL_COLOR_BUFFER_BIT = 0x00004000
GL_DEPTH_BUFFER_BIT = 0x00000100
GL_DEPTH_TEST       = 0x0B71
GL_CULL_FACE        = 0x0B44
GL_BACK             = 0x0405
GL_FLOAT            = 0x1406
GL_TRIANGLES        = 0x0004
GL_UNSIGNED_INT     = 0x1405
GL_UNSIGNED_SHORT = 0x1403

class SphereWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.program = None
        self.vbo = None
        self.ibo = None
        self.vao = None
        self.index_count = 0
        self.proj = QMatrix4x4(); self.view = QMatrix4x4(); self.model = QMatrix4x4()
    
    def handle_log_message(self, msg: QOpenGLDebugMessage):
      print(f"[OpenGL] {msg.severity()} {msg.source()} {msg.type()}:\n  {msg.message()}")

    def build_sphere(self, stacks=24, slices=48, radius=1.0):
        verts, indices = [], []
        for i in range(stacks + 1):
            v = i / stacks; phi = (v - 0.5) * pi
            y = sin(phi); r = cos(phi)
            for j in range(slices + 1):
                u = j / slices; theta = u * 2.0 * pi
                x = r * cos(theta); z = r * sin(theta)
                verts.extend((radius*x, radius*y, radius*z, x, y, z))
        for i in range(stacks):
            for j in range(slices):
                i0 = i*(slices+1)+j; i1=i0+1; i2=i0+(slices+1); i3=i2+1
                indices.extend((i0, i2, i1, i1, i2, i3))
       # print(verts)
        return array('f', verts).tobytes(), array('H', indices).tobytes(), len(indices)

    @fatal_on_exception()
    def initializeGL(self):
      ctx = self.context()
      f = ctx.functions()


      # State
      f.glEnable(GL_DEPTH_TEST)
      f.glEnable(GL_CULL_FACE)
      f.glCullFace(GL_BACK)


      # Shaders
      self.program = QOpenGLShaderProgram(self)
      if not self.program.addShaderFromSourceCode(QOpenGLShader.Vertex, """
          #version 330 core
          layout(location=0) in vec3 in_pos;
          layout(location=1) in vec3 in_normal;
          uniform mat4 u_model,u_view,u_proj;
          uniform mat3 u_normalMatrix;
          out vec3 v_normal_vs;
          void main(){
              vec4 pos_vs = u_view * u_model * vec4(in_pos,1.0);
              v_normal_vs = normalize(u_normalMatrix * in_normal);
              gl_Position = u_proj * pos_vs;
          }"""):
          raise RuntimeError(self.program.log())
      if not self.program.addShaderFromSourceCode(QOpenGLShader.Fragment, """
          #version 330 core
          in vec3 v_normal_vs;
          uniform vec3 u_lightDir_vs, u_color;
          out vec4 fragColor;
          void main(){
              float ambient = 0.6;
              float ndotl = max(dot(normalize(v_normal_vs), normalize(-u_lightDir_vs)), 0.0);
              fragColor = vec4((ambient + ndotl) * u_color, 1.0);
          }"""):
          raise RuntimeError(self.program.log())
      if not self.program.link():
          raise RuntimeError(self.program.log())
      
      vbo_data, ibo_data, self.index_count = self.build_sphere(8, 8, 1.0)
      self.vao = QOpenGLVertexArrayObject(self)
      self.vao.create()
      self.vao.bind()          # VAO is now active

      self.program.bind()      # ensure attribute bindings work properly

      self.vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
      self.vbo.create()
      self.vbo.bind()
      self.vbo.allocate(vbo_data, len(vbo_data))

      stride = 6 * 4
      self.program.enableAttributeArray(0)
      self.program.setAttributeBuffer(0, GL_FLOAT, 0, 3, stride)
      self.program.enableAttributeArray(1)
      self.program.setAttributeBuffer(1, GL_FLOAT, 12, 3, stride)

      self.ibo = QOpenGLBuffer(QOpenGLBuffer.IndexBuffer)
      self.ibo.create()
      self.ibo.bind()
      print(len(ibo_data))
      self.ibo.allocate(ibo_data, len(ibo_data))

      # ✅ Correct order:
      self.program.release()
      self.vao.release()
      # ✅ Now VAO holds VBO+IBO reliably.

      # ✅ At this point VAO now retains VBO + IBO state properly on macOS.

      # (Now you may release VBO/IBO if desired, but to be extra safe leave them alive.)

      # Camera
      self.view.setToIdentity()
      self.view.lookAt(QVector3D(0,0,10), QVector3D(0,0,0), QVector3D(0,1,0))
      self.model.setToIdentity()

    @fatal_on_exception()
    def resizeGL(self, w, h):
      self.proj.setToIdentity()
      self.proj.perspective(45.0, (w/h) if h else 1.0, 0.1, 100.0)

    @fatal_on_exception()
    def paintGL(self):
        f = self.context().functions()

        f.glViewport(0, 0, self.width(), self.height())
        f.glClearColor(0.1, 0.1, 0.3, 1.0)
        f.glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.program.bind()
        self.vao.bind()

        self.program.setUniformValue("u_model", self.model)
        self.program.setUniformValue("u_view", self.view)
        self.program.setUniformValue("u_proj", self.proj)
        self.program.setUniformValue("u_normalMatrix", (self.view*self.model).normalMatrix())
        self.program.setUniformValue("u_lightDir_vs", QVector3D(0.5, 1.0, 0.3))
        self.program.setUniformValue("u_color", QVector3D(0.85, 0.85, 0.9))

        f.glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_SHORT, ctypes.c_void_p(0))
        print(f.glGetError())
        # f.glDrawArrays(GL_TRIANGLES, 0, self.index_count)

        self.vao.release()
        self.program.release()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Sphere — QOpenGLWidget (macOS Core)")
        self.setMinimumSize(640, 480)
        self.setCentralWidget(SphereWidget(self))

def set_surface_format():
    fmt = QSurfaceFormat()
    fmt.setRenderableType(QSurfaceFormat.OpenGL)
    fmt.setProfile(QSurfaceFormat.CoreProfile)
    fmt.setVersion(4, 1)   # drop to (3,3) if needed
    #fmt.setDepthBufferSize(24)
    #fmt.setStencilBufferSize(8)
    #fmt.setSwapInterval(1)

    # fmt.setOption(QSurfaceFormat.DebugContext)

    QSurfaceFormat.setDefaultFormat(fmt)

if __name__ == "__main__":
    set_surface_format()
    
    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())
