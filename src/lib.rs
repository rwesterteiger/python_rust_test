mod mesh;

use pyo3::pymodule;

#[pymodule]
mod pytest_lib { 
use glam::vec3;
use pyo3::{prelude::*, types::PyTuple};

use crate::mesh;


  #[pyfunction]
  fn create_mesh(py: Python<'_>) -> PyResult<Py<PyTuple>>  {
    let mesh = mesh::cube_mesh(vec3(1.0, 1.0, 1.0));

    Ok(mesh.to_numpy(py)?.unbind())
  }
}

