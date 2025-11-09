use glam::{Vec3, vec3};
use ndarray::Array2;
use numpy::{Ix2, PyArray, ToPyArray};
use pyo3::{Bound, IntoPyObject, PyResult, Python, types::PyTuple};


fn to_pyarray3<'py>(py: Python<'py>, v : Vec<Vec3>) -> Bound<'py, PyArray<f32, Ix2>> {
  let mut a = Array2::<f32>::zeros((v.len(), 3));

  for (idx, p) in v.into_iter().enumerate() {
    a[[idx, 0]] = p.x;
    a[[idx, 1]] = p.y;
    a[[idx, 2]] = p.z;
  }

  return a.to_pyarray(py);
}


pub struct Mesh {
  vtx_pos  : Vec<Vec3>,
  vtx_norm : Vec<Vec3>,
  vtx_idxs : Vec<u32>,  
}

impl Mesh {
  pub fn to_numpy<'py>(self, py: Python<'py>) -> PyResult<Bound<'py, PyTuple>> {
    let pos  = to_pyarray3(py, self.vtx_pos);
    let norm = to_pyarray3(py, self.vtx_norm);
    let idxs = self.vtx_idxs.to_pyarray(py);

    (pos, norm, idxs).into_pyobject(py)
  }
}

/// Returns (positions, normals, indices)
pub fn cube_mesh(half_extents: Vec3) -> Mesh {
    let hx = half_extents.x;
    let hy = half_extents.y;
    let hz = half_extents.z;

    // 6 faces * 4 verts each (CCW when viewed from outside)
    let vtx_pos = vec![
        // +Z (front)
        vec3(-hx, -hy,  hz), vec3( hx, -hy,  hz), vec3( hx,  hy,  hz), vec3(-hx,  hy,  hz),
        // -Z (back)
        vec3( hx, -hy, -hz), vec3(-hx, -hy, -hz), vec3(-hx,  hy, -hz), vec3( hx,  hy, -hz),
        // +X (right)
        vec3( hx, -hy,  hz), vec3( hx, -hy, -hz), vec3( hx,  hy, -hz), vec3( hx,  hy,  hz),
        // -X (left)
        vec3(-hx, -hy, -hz), vec3(-hx, -hy,  hz), vec3(-hx,  hy,  hz), vec3(-hx,  hy, -hz),
        // +Y (top)
        vec3(-hx,  hy,  hz), vec3( hx,  hy,  hz), vec3( hx,  hy, -hz), vec3(-hx,  hy, -hz),
        // -Y (bottom)
        vec3(-hx, -hy, -hz), vec3( hx, -hy, -hz), vec3( hx, -hy,  hz), vec3(-hx, -hy,  hz),
    ];

    let vtx_norm = vec![
        // +Z
        vec3(0.0, 0.0,  1.0),
        vec3(0.0, 0.0,  1.0),
        vec3(0.0, 0.0,  1.0),
        vec3(0.0, 0.0,  1.0),
        // -Z
        vec3(0.0, 0.0, -1.0),
        vec3(0.0, 0.0, -1.0),
        vec3(0.0, 0.0, -1.0),
        vec3(0.0, 0.0, -1.0),
        // +X
        vec3(1.0, 0.0,  0.0),
        vec3(1.0, 0.0,  0.0),
        vec3(1.0, 0.0,  0.0),
        vec3(1.0, 0.0,  0.0),
        // -X
        vec3(-1.0, 0.0, 0.0),
        vec3(-1.0, 0.0, 0.0),
        vec3(-1.0, 0.0, 0.0),
        vec3(-1.0, 0.0, 0.0),
        // +Y
        vec3(0.0, 1.0,  0.0),
        vec3(0.0, 1.0,  0.0),
        vec3(0.0, 1.0,  0.0),
        vec3(0.0, 1.0,  0.0),
        // -Y
        vec3(0.0, -1.0, 0.0),
        vec3(0.0, -1.0, 0.0),
        vec3(0.0, -1.0, 0.0),
        vec3(0.0, -1.0, 0.0),
    ];

    // Two triangles per face: (0,1,2) and (0,2,3) with an offset per face
    let mut vtx_idxs = Vec::with_capacity(6 * 6);

    for face in 0..6u32 {
        let o = face * 4;
        vtx_idxs.extend_from_slice(&[o + 0, o + 1, o + 2, o + 0, o + 2, o + 3]);
    }

    Mesh {
        vtx_pos,
        vtx_norm,
        vtx_idxs
    }
}