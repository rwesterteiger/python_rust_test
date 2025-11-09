# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the qt3d/simple-cpp example from Qt v5.x"""

import sys
from PySide6.QtCore import (Property, QObject, QPropertyAnimation, Signal)
from PySide6.QtGui import (QGuiApplication, QMatrix4x4, QQuaternion, QVector3D)
from PySide6.Qt3DCore import (Qt3DCore)
from PySide6.Qt3DExtras import (Qt3DExtras)
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QColor
from PySide6.Qt3DRender import Qt3DRender


class OrbitTransformController(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self._target = None
        self._matrix = QMatrix4x4()
        self._radius = 0
        self._angle = 0

    def setTarget(self, t):
        self._target = t

    def getTarget(self):
        return self._target

    def setRadius(self, radius):
        if self._radius != radius:
            self._radius = radius
            self.updateMatrix()
            self.radiusChanged.emit()

    def getRadius(self):
        return self._radius

    def setAngle(self, angle):
        if self._angle != angle:
            self._angle = angle
            self.updateMatrix()
            self.angleChanged.emit()

    def getAngle(self):
        return self._angle

    def updateMatrix(self):
        self._matrix.setToIdentity()
        self._matrix.rotate(self._angle, QVector3D(0, 1, 0))
        self._matrix.translate(self._radius, 0, 0)
        if self._target is not None:
            self._target.setMatrix(self._matrix)

    angleChanged = Signal()
    radiusChanged = Signal()
    angle = Property(float, getAngle, setAngle, notify=angleChanged)
    radius = Property(float, getRadius, setRadius, notify=radiusChanged)


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
        w.camera().lens().setPerspectiveProjection(45, 16 / 9, 0.1, 1000)
        w.camera().setPosition(QVector3D(0, 0, 40))
        w.camera().setViewCenter(QVector3D(0, 0, 0))

        # For camera controls
        self.createScene()
        self.camController = Qt3DExtras.QOrbitCameraController(self.rootEntity)
        self.camController.setLinearSpeed(50)
        self.camController.setLookSpeed(180)
        self.camController.setCamera(w.camera())

        w.setRootEntity(self.rootEntity)
        self.window = w

    def createScene(self):
        # Root entity
        self.rootEntity = Qt3DCore.QEntity()

        # Material
        self.material = Qt3DExtras.QPhongMaterial(self.rootEntity)
        self.material.setDiffuse(QColor(255,0,0))




        light = Qt3DRender.QPointLight(self.rootEntity)
        light.setColor("white")
        light.setIntensity(1.0)
       
        lt = Qt3DCore.QTransform()
        lt.setTranslation(QVector3D(1000.0, 10.0, 10.0))

        light_entity = Qt3DCore.QEntity(self.rootEntity)
        light_entity.addComponent(light)
        light_entity.addComponent(lt)

        # Torus
        self.torusEntity = Qt3DCore.QEntity(self.rootEntity)

        self.torusMesh = self._createMesh()

        self.torusTransform = Qt3DCore.QTransform()
        self.torusTransform.setScale3D(QVector3D(1.5, 1, 0.5))
        self.torusTransform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 45))

        self.torusEntity.addComponent(self.torusMesh)
        self.torusEntity.addComponent(self.torusTransform)
        self.torusEntity.addComponent(self.material)
        
        self.controller = self._makeController(self.torusTransform)

    def _createMesh(self):
        m = Qt3DExtras.QTorusMesh()
        m.setRadius(5)
        m.setMinorRadius(1)
        m.setRings(100)
        m.setSlices(20)

        return m
    
    def _makeController(self, xform):
        controller = OrbitTransformController(xform)
        controller.setTarget(xform)
        controller.setRadius(0)

        sphereRotateTransformAnimation = QPropertyAnimation(xform)
        sphereRotateTransformAnimation.setTargetObject(controller)
        sphereRotateTransformAnimation.setPropertyName(b"angle")
        sphereRotateTransformAnimation.setStartValue(0)
        sphereRotateTransformAnimation.setEndValue(360)
        sphereRotateTransformAnimation.setDuration(1000)
        sphereRotateTransformAnimation.setLoopCount(-1)
        sphereRotateTransformAnimation.start()

        return controller
