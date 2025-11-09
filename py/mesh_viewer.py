# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the qt3d/simple-cpp example from Qt v5.x"""

import pytest_lib

import sys
import numpy as np

from PySide6.QtCore import (Property, QObject, QPropertyAnimation, Signal)
from PySide6.QtGui import (QGuiApplication, QMatrix4x4, QQuaternion, QVector3D)
from PySide6.Qt3DCore import (Qt3DCore)
from PySide6.Qt3DExtras import (Qt3DExtras)
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QColor
from PySide6.Qt3DRender import Qt3DRender

import orbit_controller
import make_mesh

class MeshViewer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        w = Qt3DExtras.Qt3DWindow()
        w.defaultFrameGraph().setClearColor(QColor("#101218"))

        container = QtWidgets.QWidget.createWindowContainer(w, self)
        container.setFixedSize(1024, 1024)
        container.setFocusPolicy(QtCore.Qt.StrongFocus)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container)

        # Camera
        w.camera().lens().setPerspectiveProjection(60, 1.0, 0.1, 100)
        w.camera().setPosition(QVector3D(0, 2, 5))
        w.camera().setViewCenter(QVector3D(0, 0, 0))

        # For camera controls
        self.createScene()
        self.camController = Qt3DExtras.QOrbitCameraController(self.rootEntity)
        self.camController.setLinearSpeed(50)
        self.camController.setLookSpeed(180)
        self.camController.setCamera(w.camera())

        w.setRootEntity(self.rootEntity)
        self.window = w

    def createLight(self):
        light = Qt3DRender.QPointLight(self.rootEntity)
        light.setColor("white")
        light.setIntensity(1.0)

        lt = Qt3DCore.QTransform(self.rootEntity)
        lt.setTranslation(QVector3D(10.0, 10.0, 10.0))

        light_entity = Qt3DCore.QEntity(self.rootEntity)
        light_entity.addComponent(light)
        light_entity.addComponent(lt)

        light_vis = Qt3DCore.QEntity(self.rootEntity)
        mesh = Qt3DExtras.QSphereMesh(self.rootEntity)
        mesh.setRadius(0.2)
        mat = Qt3DExtras.QPhongMaterial(self.rootEntity)
        mat.setDiffuse(QColor(255,255,255))
        #mat.setAmbient(QColor(255,255,255))

        lt2 = Qt3DCore.QTransform(self.rootEntity)
        lt2.setTranslation(QVector3D(10.0, 10.0, 10.0))

        light_vis.addComponent(mesh)
        # reuse lt so the sphere follows the light:
        light_vis.addComponent(lt2)
        light_vis.addComponent(mat)

    def createTorus(self):
      # Material


      self.material = Qt3DExtras.QPhongMaterial(self.rootEntity)
      self.material.setDiffuse(QColor(255,0,0))

      # Torus
      self.torusEntity = Qt3DCore.QEntity(self.rootEntity)

      self.mesh = self._createMesh()
      self.torusTransform = Qt3DCore.QTransform()
      self.torusTransform.setScale3D(QVector3D(2, 1, 2))
      self.torusTransform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 45))

      self.torusEntity.addComponent(self.mesh)
      self.torusEntity.addComponent(self.torusTransform)
      self.torusEntity.addComponent(self.material)
      
    def createScene(self):
        # Root entity
        self.rootEntity = Qt3DCore.QEntity()

        self.createLight()
        self.createTorus()
        
        self.controller = self._makeController(self.torusTransform)



    def cube_arrays(self, size: float = 1.0):
      """
      Returns (positions, normals, uvs, indices) for a cube of edge length `size`,
      centered at the origin. Dtypes match Qt expectations.
        positions: (24,3) float32
        normals:   (24,3) float32
        uvs:       (24,2) float32
        indices:   (36,)  uint32  (12 triangles)
      """
      s = size * 0.5

      # Face definitions: (normal, four corners CCW, uv for each corner)
      # Order: +X, -X, +Y, -Y, +Z, -Z
      faces = [
          #  +X
          (np.array([1, 0, 0],  dtype=np.float32),
          [ [ s, -s, -s], [ s, -s,  s], [ s,  s,  s], [ s,  s, -s] ]),
          #  -X
          (np.array([-1, 0, 0], dtype=np.float32),
          [ [-s, -s,  s], [-s, -s, -s], [-s,  s, -s], [-s,  s,  s] ]),
          #  +Y
          (np.array([0, 1, 0],  dtype=np.float32),
          [ [-s,  s, -s], [ s,  s, -s], [ s,  s,  s], [-s,  s,  s] ]),
          #  -Y
          (np.array([0, -1, 0], dtype=np.float32),
          [ [-s, -s,  s], [ s, -s,  s], [ s, -s, -s], [-s, -s, -s] ]),
          #  +Z
          (np.array([0, 0, 1],  dtype=np.float32),
          [ [ s, -s,  s], [-s, -s,  s], [-s,  s,  s], [ s,  s,  s] ]),
          #  -Z
          (np.array([0, 0, -1], dtype=np.float32),
          [ [-s, -s, -s], [ s, -s, -s], [ s,  s, -s], [-s,  s, -s] ]),
      ]

      # Same UVs for each face (quad)
      face_uv = np.array([
          [0.0, 0.0],  # bottom-left
          [1.0, 0.0],  # bottom-right
          [1.0, 1.0],  # top-right
          [0.0, 1.0],  # top-left
      ], dtype=np.float32)

      positions = []
      normals   = []
      uvs       = []
      indices   = []

      for fi, (nrm, corners) in enumerate(faces):
          base = fi * 4
          # append 4 verts
          for v in corners:
              positions.append(v)
              normals.append(nrm)
          uvs.extend(face_uv)

          # two triangles per face: (0,1,2) (0,2,3) relative to this face
          indices.extend([base + 0, base + 1, base + 2,
                          base + 0, base + 2, base + 3])

      positions = np.asarray(positions, dtype=np.float32)
      normals   = np.asarray(normals,   dtype=np.float32)
      uvs       = np.asarray(uvs,       dtype=np.float32)
      indices   = np.asarray(indices,   dtype=np.uint32)
      return positions, normals, uvs, indices


    def _createMesh(self):
        mesh = pytest_lib.create_mesh()
        pos, norm, idxs = mesh.to_numpy()

        return make_mesh.make_mesh_renderer(self.rootEntity, pos, norm, idxs)
        m = Qt3DExtras.QTorusMesh()
        m.setRadius(5)
        m.setMinorRadius(1)
        m.setRings(100)
        m.setSlices(20)

        return m
    
    def _makeController(self, xform):
        controller = orbit_controller.OrbitTransformController(xform)
        controller.setTarget(xform)
        controller.setRadius(0)

        sphereRotateTransformAnimation = QPropertyAnimation(xform)
        sphereRotateTransformAnimation.setTargetObject(controller)
        sphereRotateTransformAnimation.setPropertyName(b"angle")
        sphereRotateTransformAnimation.setStartValue(0)
        sphereRotateTransformAnimation.setEndValue(360)
        sphereRotateTransformAnimation.setDuration(4000)
        sphereRotateTransformAnimation.setLoopCount(-1)
        sphereRotateTransformAnimation.start()

        return controller
