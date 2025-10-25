use pyo3::pymodule;
use pyo3::pyclass;
use std::fmt::Formatter;

#[pymodule]
mod pytest_lib { 
  use pyo3::{prelude::*, IntoPyObjectExt};
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
}

