#![allow(non_camel_case_types)]

use std::io::Cursor;

use brotli::BrotliDecompress;
use pyo3::create_exception;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyModule};

create_exception!(_brotli_rs, error, PyException);

#[pyfunction]
fn _decompress<'py>(py: Python<'py>, data: &[u8]) -> PyResult<Bound<'py, PyBytes>> {
    let data = data.to_vec();
    let output = py
        .detach(|| {
            let mut input = Cursor::new(data);
            let mut output = Vec::new();
            BrotliDecompress(&mut input, &mut output).map_err(|exception| exception.to_string())?;
            Ok::<_, String>(output)
        })
        .map_err(error::new_err)?;
    Ok(PyBytes::new(py, &output))
}

#[pymodule]
fn _brotli_rs(py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add("error", py.get_type::<error>())?;
    module.add_function(wrap_pyfunction!(_decompress, module)?)?;
    Ok(())
}
