import numpy as np
from PySide6.QtGui import QColor
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender
from PySide6.Qt3DExtras import Qt3DExtras

def make_mesh_renderer(parent_entity: Qt3DCore.QEntity,
                       positions: np.ndarray,
                       normals: np.ndarray,
                       indices: np.ndarray) -> Qt3DCore.QEntity:
    """
    positions: (N,3) float32
    normals:   (N,3) float32 (optional; pass zeros if not used by your material)
    indices:   (M,)  uint32  (triangles)
    """
    assert positions.dtype == np.float32 and positions.ndim == 2 and positions.shape[1] == 3
    assert normals.dtype   == np.float32 and normals.shape == positions.shape
    assert indices.dtype   == np.uint32   and indices.ndim == 1

    # --- Geometry & raw buffers ---
    geom = Qt3DCore.QGeometry(parent_entity)
    pos_buf = Qt3DCore.QBuffer(geom)
    pos_buf.setUsage(Qt3DCore.QBuffer.StaticDraw)
    pos_buf.setData(positions.tobytes())

    nrm_buf = Qt3DCore.QBuffer(geom)
    nrm_buf.setUsage(Qt3DCore.QBuffer.StaticDraw)
    nrm_buf.setData(normals.tobytes())

    idx_buf = Qt3DCore.QBuffer(geom)
    idx_buf.setUsage(Qt3DCore.QBuffer.StaticDraw)
    idx_buf.setData(indices.tobytes())

    # --- Attributes ---
    # Positions
    pos_attr = Qt3DCore.QAttribute(geom)
    pos_attr.setName(Qt3DCore.QAttribute.defaultPositionAttributeName())
    pos_attr.setBuffer(pos_buf)
    pos_attr.setVertexBaseType(Qt3DCore.QAttribute.Float)
    pos_attr.setVertexSize(3)
    pos_attr.setAttributeType(Qt3DCore.QAttribute.VertexAttribute)
    pos_attr.setByteStride(0)   # tightly packed (equiv. 12 bytes for 3*float32)
    pos_attr.setByteOffset(0)
    pos_attr.setCount(positions.shape[0])

    # Normals
    nrm_attr = Qt3DCore.QAttribute(geom)
    nrm_attr.setName(Qt3DCore.QAttribute.defaultNormalAttributeName())
    nrm_attr.setBuffer(nrm_buf)
    nrm_attr.setVertexBaseType(Qt3DCore.QAttribute.Float)
    nrm_attr.setVertexSize(3)
    nrm_attr.setAttributeType(Qt3DCore.QAttribute.VertexAttribute)
    nrm_attr.setByteStride(0)
    nrm_attr.setByteOffset(0)
    nrm_attr.setCount(normals.shape[0])

    # Indices
    idx_attr = Qt3DCore.QAttribute(geom)
    idx_attr.setAttributeType(Qt3DCore.QAttribute.IndexAttribute)
    idx_attr.setBuffer(idx_buf)
    idx_attr.setVertexBaseType(Qt3DCore.QAttribute.UnsignedInt)
    idx_attr.setVertexSize(1)
    idx_attr.setByteStride(0)
    idx_attr.setByteOffset(0)
    idx_attr.setCount(indices.shape[0])

    geom.addAttribute(pos_attr)
    geom.addAttribute(nrm_attr)
    geom.addAttribute(idx_attr)

    # --- Renderer ---
    geom_renderer = Qt3DRender.QGeometryRenderer(parent_entity)
    geom_renderer.setGeometry(geom)
    geom_renderer.setPrimitiveType(Qt3DRender.QGeometryRenderer.Triangles)

    return geom_renderer
