mod mesh;
mod spherical_harmonics;

use pyo3::pymodule;

#[pymodule]
mod pytest_lib { 
use glam::vec3;
use pyo3::{prelude::*, types::PyTuple};

use crate::{mesh::{self, Mesh}, spherical_harmonics};


  #[pyfunction]
  fn create_mesh(py: Python<'_>) -> PyResult<Mesh>  {
    let mesh = spherical_harmonics::sphere_mesh(4);

    return Ok(mesh);

    // Ok(mesh.to_numpy(py)?.unbind())
  }
}

