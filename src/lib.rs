use pyo3::pymodule;
use pyo3::pyclass;
use std::fmt::Formatter;
use numpy::convert::IntoPyArray;

#[pymodule]
mod pytest_lib { 
  use glam::{Vec3, vec3};
use ndarray::{Array2, Ix2};
use numpy::{IntoPyArray, PyArray, ToPyArray};
use pyo3::{IntoPyObjectExt, prelude::*, types::PyTuple};
  use std::{fmt::{Display, Formatter}, time::Duration};


  #[pyclass(str)]
  #[derive(Clone,Copy,Debug)]
  pub struct Point {
    #[pyo3(get, set)]
    pub x : f32,
    #[pyo3(get, set)]
    pub y : f32,
  }

  impl From<(f32,f32)> for Point {
    fn from(xy : (f32, f32)) -> Self {
      Point {
        x : xy.0,
        y : xy.1,
      }
    }
  }

  impl Display for Point {
    fn fmt(&self, f: &mut Formatter<'_>) -> Result<(), std::fmt::Error> {
      std::fmt::Debug::fmt(self, f)
    }
  }
  
  fn get_circle_points(radius : f32) -> Vec<Point> {
    const N : usize = 16;

    const STEP : f32 = (360.0 / N as f32).to_radians();

    (0..N).map(move |i| {
      let a = STEP * i as f32;
      let y = radius * a.cos();
      let x = radius * a.sin();
      (x,y).into()
    }).collect()
  }

  #[pyfunction]
  fn get_points(py: Python<'_>, radius : f32) -> PyResult<Py<PyAny>> {
    let pts = py.detach(|| {
      // std::thread::sleep(Duration::from_secs(1));
      get_circle_points(radius)
    });

    Ok(pts.into_py_any(py)?)
  }

  /// Formats the sum of two numbers as string.
  #[pyfunction]
  fn sum_as_string(py: Python<'_>, a: usize, b: usize) -> PyResult<String> {
    py.detach(|| {
      std::thread::sleep(Duration::from_secs(5));
      Ok((a + b).to_string())
    })
  }

  /// Returns (positions, normals, indices)
  pub fn cube_mesh(half_extents: Vec3) -> (Vec<Vec3>, Vec<Vec3>, Vec<u32>) {
      let hx = half_extents.x;
      let hy = half_extents.y;
      let hz = half_extents.z;

      // 6 faces * 4 verts each (CCW when viewed from outside)
      let positions = vec![
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

      let normals = vec![
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
      let mut indices = Vec::with_capacity(6 * 6);

      for face in 0..6u32 {
          let o = face * 4;
          indices.extend_from_slice(&[o + 0, o + 1, o + 2, o + 0, o + 2, o + 3]);
      }

      (positions, normals, indices)
  }

  fn to_pyarray3<'py>(py: Python<'py>, v : Vec<Vec3>) -> Bound<'py, PyArray<f32, Ix2>> {
    let mut a = Array2::<f32>::zeros((v.len(), 3));

    for (idx, p) in v.into_iter().enumerate() {
      a[[idx, 0]] = p.x;
      a[[idx, 1]] = p.y;
      a[[idx, 2]] = p.z;
    }

    return a.into_pyarray(py);
  }

  #[pyfunction]
  fn create_mesh(py: Python<'_>) -> PyResult<Py<PyTuple>>  {
    let (pos, norm, idxs) = cube_mesh(vec3(1.0, 1.0, 1.0));

    let pos  = to_pyarray3(py, pos);
    let norm = to_pyarray3(py, norm);
    let idxs = idxs.to_pyarray(py);

   // let v : Vec3 = (1.0,2.0,3.0).into();

/*
    let vertices = 

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
 */

    let r = (pos, norm, idxs).into_pyobject(py)?;

    Ok(r.unbind())
  }
}

