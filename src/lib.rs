#![allow(non_camel_case_types)]

use std::io::Write;

use brotli::enc::backward_references::{BrotliEncoderMode, BrotliEncoderParams};
use brotli::enc::writer::StandardAlloc;
use brotli::{BrotliDecompressStream, BrotliResult, BrotliState, CompressorWriter};
use brotli_decompressor::BrotliDecoderHasMoreOutput;
use pyo3::create_exception;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyModule};

create_exception!(_brotli_rs, error, PyException);

type DecoderState = BrotliState<StandardAlloc, StandardAlloc, StandardAlloc>;

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

#[pyclass(name = "_Compressor")]
struct PythonCompressor {
    writer: Option<CompressorWriter<Vec<u8>>>,
}

#[pymethods]
impl PythonCompressor {
    #[new]
    fn new(mode: i32, quality: i32, lgwin: i32, lgblock: i32) -> PyResult<Self> {
        let params = validate_parameters(mode, quality, lgwin, lgblock)?;
        Ok(Self {
            writer: Some(CompressorWriter::with_params(Vec::new(), 4096, &params)),
        })
    }

    fn process<'py>(&mut self, py: Python<'py>, data: &[u8]) -> PyResult<Bound<'py, PyBytes>> {
        let data = data.to_vec();
        let output = py
            .detach(|| {
                let writer = self
                    .writer
                    .as_mut()
                    .ok_or_else(|| "Compressor has already been finished".to_owned())?;
                writer
                    .write_all(&data)
                    .map_err(|err| format!("Brotli compression failed: {err}"))?;
                Ok::<_, String>(std::mem::take(writer.get_mut()))
            })
            .map_err(codec_error)?;
        Ok(PyBytes::new(py, &output))
    }

    fn flush<'py>(&mut self, py: Python<'py>) -> PyResult<Bound<'py, PyBytes>> {
        let output = py
            .detach(|| {
                let writer = self
                    .writer
                    .as_mut()
                    .ok_or_else(|| "Compressor has already been finished".to_owned())?;
                writer
                    .flush()
                    .map_err(|err| format!("Brotli compression failed: {err}"))?;
                Ok::<_, String>(std::mem::take(writer.get_mut()))
            })
            .map_err(codec_error)?;
        Ok(PyBytes::new(py, &output))
    }

    fn finish<'py>(&mut self, py: Python<'py>) -> PyResult<Bound<'py, PyBytes>> {
        let output = py
            .detach(|| {
                self.writer
                    .take()
                    .map(CompressorWriter::into_inner)
                    .ok_or_else(|| "Compressor has already been finished".to_owned())
            })
            .map_err(codec_error)?;
        Ok(PyBytes::new(py, &output))
    }
}

#[pyclass(name = "_Decompressor")]
struct PythonDecompressor {
    state: DecoderState,
    pending: Vec<u8>,
    total_out: usize,
    max_output: Option<usize>,
    needs_output: bool,
    finished: bool,
    failed: bool,
}

#[pymethods]
impl PythonDecompressor {
    #[new]
    fn new(max_output: Option<usize>) -> Self {
        Self {
            state: BrotliState::new_strict(
                StandardAlloc::default(),
                StandardAlloc::default(),
                StandardAlloc::default(),
            ),
            pending: Vec::new(),
            total_out: 0,
            max_output,
            needs_output: false,
            finished: false,
            failed: false,
        }
    }

    fn process<'py>(
        &mut self,
        py: Python<'py>,
        data: &[u8],
        output_buffer_limit: Option<usize>,
    ) -> PyResult<Bound<'py, PyBytes>> {
        let data = data.to_vec();
        let output = py
            .detach(|| self.process_inner(&data, output_buffer_limit))
            .map_err(codec_error)?;
        Ok(PyBytes::new(py, &output))
    }

    fn can_accept_more_data(&self) -> bool {
        !self.failed && self.pending.is_empty() && !self.needs_output
    }

    fn is_finished(&self) -> bool {
        self.finished
    }
}

impl PythonDecompressor {
    fn process_inner(
        &mut self,
        data: &[u8],
        output_buffer_limit: Option<usize>,
    ) -> Result<Vec<u8>, String> {
        if self.failed {
            return Err("Brotli decoder is in a failed state".to_owned());
        }
        if self.finished {
            if data.is_empty() {
                return Ok(Vec::new());
            }
            self.failed = true;
            return Err("Brotli stream has trailing data".to_owned());
        }
        if (!self.pending.is_empty() || self.needs_output) && !data.is_empty() {
            return Err(
                "Decoder cannot accept more data until pending output is drained".to_owned(),
            );
        }
        if !data.is_empty() {
            self.pending.extend_from_slice(data);
        }
        if output_buffer_limit == Some(0) {
            self.needs_output = !self.pending.is_empty() || self.needs_output;
            return Ok(Vec::new());
        }

        let mut output = Vec::new();
        loop {
            let call_remaining = output_buffer_limit
                .map(|limit| (limit - output.len()).min(64 * 1024))
                .unwrap_or(64 * 1024);
            if call_remaining == 0 {
                self.needs_output = true;
                break;
            }

            let max_remaining = self
                .max_output
                .map(|maximum| maximum.saturating_sub(self.total_out));
            let probe_limit = match max_remaining {
                Some(0) => 1,
                Some(remaining) => call_remaining.min(remaining),
                None => call_remaining,
            };
            let mut chunk = vec![0_u8; probe_limit.max(1)];
            let mut available_in = self.pending.len();
            let mut input_offset = 0;
            let mut available_out = chunk.len();
            let mut output_offset = 0;
            let result = BrotliDecompressStream(
                &mut available_in,
                &mut input_offset,
                &self.pending,
                &mut available_out,
                &mut output_offset,
                &mut chunk,
                &mut self.total_out,
                &mut self.state,
            );

            if max_remaining == Some(0) && output_offset != 0 {
                self.failed = true;
                return Err("Decompressed data exceeds max_output".to_owned());
            }
            self.pending.drain(..input_offset);
            output.extend_from_slice(&chunk[..output_offset]);

            match result {
                BrotliResult::ResultSuccess => {
                    if !self.pending.is_empty() {
                        self.failed = true;
                        return Err("Brotli stream has trailing data".to_owned());
                    }
                    self.finished = true;
                    self.needs_output = false;
                    break;
                }
                BrotliResult::NeedsMoreInput => {
                    self.needs_output = false;
                    break;
                }
                BrotliResult::NeedsMoreOutput => {
                    self.needs_output = BrotliDecoderHasMoreOutput(&self.state);
                    if output_buffer_limit.is_some_and(|limit| output.len() >= limit) {
                        break;
                    }
                }
                BrotliResult::ResultFailure => {
                    self.failed = true;
                    return Err("Brotli decompression failed".to_owned());
                }
            }
        }

        Ok(output)
    }
}

#[pymodule]
fn _brotli_rs(py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add("error", py.get_type::<error>())?;
    module.add_class::<PythonCompressor>()?;
    module.add_class::<PythonDecompressor>()?;
    Ok(())
}
