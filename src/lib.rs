#![allow(non_camel_case_types)]

use std::io::Cursor;

use brotli::enc::backward_references::{BrotliEncoderMode, BrotliEncoderParams};
use brotli::{BrotliCompress, BrotliDecompress};
use pyo3::create_exception;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyModule};

create_exception!(_brotli_rs, error, PyException);

fn codec_error(message: impl Into<String>) -> PyErr {
    error::new_err(message.into())
}

fn validate_parameters(
    mode: i32,
    quality: i32,
    lgwin: i32,
    lgblock: i32,
) -> PyResult<BrotliEncoderParams> {
    let mode = match mode {
        0 => BrotliEncoderMode::BROTLI_MODE_GENERIC,
        1 => BrotliEncoderMode::BROTLI_MODE_TEXT,
        2 => BrotliEncoderMode::BROTLI_MODE_FONT,
        _ => return Err(codec_error("Invalid mode")),
    };
    if !(0..=11).contains(&quality) {
        return Err(codec_error("Invalid quality"));
    }
    if !(10..=24).contains(&lgwin) {
        return Err(codec_error("Invalid lgwin"));
    }
    if lgblock != 0 && !(16..=24).contains(&lgblock) {
        return Err(codec_error("Invalid lgblock"));
    }

    Ok(BrotliEncoderParams {
        mode,
        quality,
        lgwin,
        lgblock,
        ..BrotliEncoderParams::default()
    })
}

#[pyfunction]
fn _compress<'py>(
    py: Python<'py>,
    data: &[u8],
    mode: i32,
    quality: i32,
    lgwin: i32,
    lgblock: i32,
) -> PyResult<Bound<'py, PyBytes>> {
    let params = validate_parameters(mode, quality, lgwin, lgblock)?;
    let data = data.to_vec();
    let output = py
        .detach(|| {
            let mut input = Cursor::new(data);
            let mut output = Vec::new();
            BrotliCompress(&mut input, &mut output, &params)
                .map_err(|exception| format!("Brotli compression failed: {exception}"))?;
            Ok::<_, String>(output)
        })
        .map_err(codec_error)?;
    Ok(PyBytes::new(py, &output))
}

#[pyfunction]
fn _decompress<'py>(py: Python<'py>, data: &[u8]) -> PyResult<Bound<'py, PyBytes>> {
    let data = data.to_vec();
    let output = py
        .detach(|| {
            let mut input = Cursor::new(data);
            let mut output = Vec::new();
            BrotliDecompress(&mut input, &mut output)
                .map_err(|exception| format!("Brotli decompression failed: {exception}"))?;
            Ok::<_, String>(output)
        })
        .map_err(codec_error)?;
    Ok(PyBytes::new(py, &output))
}

#[pymodule]
fn _brotli_rs(py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add("error", py.get_type::<error>())?;
    module.add_function(wrap_pyfunction!(_compress, module)?)?;
    module.add_function(wrap_pyfunction!(_decompress, module)?)?;
    Ok(())
}
