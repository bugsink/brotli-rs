// Copyright (c) 2026 Patrik Wenger. MIT license; see LICENSE.
// Adapted from tests/roundtrip.rs, tests/fixtures/mod.rs and tests/api.rs.
// To regenerate: copy to examples/brotli_rs_vectors.rs in the pinned Burli
// checkout, then cargo run --release --example brotli_rs_vectors -- OUTPUT_DIR.
use burli::Options;
use std::{fs, io::Write, path::PathBuf};

use burli_core::bits::BitWriter;

/// A final compressed block producing 'A', with optional unused final trees.
pub fn literal_with_unused_trees(unused_literal: bool, unused_distance: bool) -> Vec<u8> {
    let mut writer = BitWriter::new();
    // Window 16, final compressed block, decoded length one.
    for (width, value) in [(1, 0), (1, 1), (1, 0), (2, 0), (16, 0)] {
        writer.write_bits(width, value).unwrap();
    }
    // One block type per category, no postfix/direct distances, LSB6 contexts.
    writer.write_bits(3, 0).unwrap();
    writer.write_bits(6, 0).unwrap();
    writer.write_bits(2, 0).unwrap();
    write_context_map(&mut writer, unused_literal);
    write_context_map(&mut writer, unused_distance);
    write_single_symbol(&mut writer, 8, u64::from(b'A'));
    if unused_literal {
        write_single_symbol(&mut writer, 8, u64::from(b'B'));
    }
    write_single_symbol(&mut writer, 10, 8); // Insert one byte; no copy needed.
    write_single_symbol(&mut writer, 6, 0);
    if unused_distance {
        write_single_symbol(&mut writer, 6, 1);
    }
    writer.into_bytes()
}

fn write_single_symbol(writer: &mut BitWriter, width: u8, symbol: u64) {
    writer.write_bits(2, 1).unwrap();
    writer.write_bits(2, 0).unwrap();
    writer.write_bits(width, symbol).unwrap();
}

fn write_context_map(writer: &mut BitWriter, unused_tree: bool) {
    writer.write_bits(1, u64::from(unused_tree)).unwrap();
    if unused_tree {
        writer.write_bits(3, 0).unwrap(); // Declare two trees.
        writer.write_bits(1, 0).unwrap(); // No RLE.
        write_single_symbol(writer, 1, 0); // Every context selects tree zero.
        writer.write_bits(1, 0).unwrap(); // No MTF.
    }
}

fn mixed_collector_input() -> Vec<u8> {
    const BLOCK: usize = 1 << 16;
    let mut state = 0x9e37_79b9_7f4a_7c15_u64;
    let mut next = move || {
        state ^= state << 13;
        state ^= state >> 7;
        state ^= state << 17;
        state
    };
    let pattern: Vec<u8> = (0..100).map(|_| b'a' + (next() % 26) as u8).collect();
    let mut input: Vec<u8> = pattern.iter().copied().cycle().take(BLOCK).collect();
    let binary_start = input.len();
    input.extend((0..BLOCK).map(|_| next() as u8));
    for copy in 0..2 {
        let dst = binary_start + 4096 + copy * 7919;
        input.copy_within(dst - 3072..dst - 3072 + 1024, dst);
    }
    input.extend(pattern.iter().copied().cycle().take(BLOCK));
    // A short final block takes the q0 direct path. Its first copy has the
    // initial last distance, which the ring no longer holds.
    input.extend_from_slice(b"wxyzwxyzwxyz");
    input.extend((0..288).map(|_| next() as u8));
    input
}

fn text(len: usize) -> Vec<u8> {
    let words = [
        "brotli ",
        "window ",
        "meta-block ",
        "literal ",
        "context ",
        "copy ",
        "the ",
        "of ",
        "distance\n",
        "decoder, ",
        "Huffman ",
        "code ",
    ];
    let mut state = 0x9e37_79b9_u32;
    let mut text = Vec::with_capacity(len + 16);
    while text.len() < len {
        state = state.wrapping_mul(1_664_525).wrapping_add(1_013_904_223);
        text.extend_from_slice(words[(state >> 28) as usize % words.len()].as_bytes());
    }
    text.truncate(len);
    text
}

fn rust_brotli(input: &[u8], quality: i32, lgwin: i32, lgblock: i32) -> Vec<u8> {
    let params = rust_brotli::enc::BrotliEncoderParams {
        quality,
        lgwin,
        lgblock,
        ..Default::default()
    };
    let mut encoded = Vec::new();
    {
        let mut writer = rust_brotli::CompressorWriter::with_params(&mut encoded, 4096, &params);
        writer.write_all(input).unwrap();
    }
    encoded
}

fn main() {
    let dest = PathBuf::from(std::env::args().nth(1).expect("output directory"));
    fs::create_dir_all(&dest).unwrap();
    let save = |name: &str, payload: &[u8], encoded: &[u8]| {
        fs::write(dest.join(format!("{name}.raw")), payload).unwrap();
        fs::write(dest.join(format!("{name}.br")), encoded).unwrap();
    };
    for (literal, distance) in [(false, false), (true, false), (false, true), (true, true)] {
        save(
            &format!("unused_{literal}_{distance}"),
            b"A",
            &literal_with_unused_trees(literal, distance),
        );
    }
    let payload = text(300_000);
    save(
        "within_meta_block",
        &payload,
        &rust_brotli(&payload, 5, 22, 24),
    );
    let input = mixed_collector_input();
    fs::write(dest.join("collectors.raw"), &input).unwrap();
    for quality in 0..=5 {
        let options = Options::default()
            .with_quality(quality)
            .unwrap()
            .with_block_bits(Some(16))
            .unwrap();
        fs::write(
            dest.join(format!("collectors_q{quality}.br")),
            burli::compress_with_options(&input, &options).unwrap(),
        )
        .unwrap();
        let mut encoder = burli::StreamEncoder::new(Vec::new(), quality).unwrap();
        encoder.write_all(&input).unwrap();
        fs::write(
            dest.join(format!("collectors_stream_q{quality}.br")),
            encoder.finish().unwrap(),
        )
        .unwrap();
    }
    let mut input = vec![b'x'; 1 << 16];
    input.extend_from_slice(b"time_");
    for index in 0..4096 {
        input.push((index * 37 + 11) as u8);
    }
    let options = Options::default()
        .with_quality(2)
        .unwrap()
        .with_window_bits(10)
        .unwrap()
        .with_block_bits(Some(16))
        .unwrap();
    save(
        "dictionary_q2",
        &input,
        &burli::compress_with_options(&input, &options).unwrap(),
    );
    let mut encoder = burli::StreamEncoder::with_options(Vec::new(), options).unwrap();
    encoder.write_all(&input).unwrap();
    fs::write(
        dest.join("dictionary_stream_q2.br"),
        encoder.finish().unwrap(),
    )
    .unwrap();
    let mut input = vec![b'x'; 2048];
    input.extend_from_slice(b"time time time after a split meta-block");
    for quality in 4..=5 {
        let options = Options::default()
            .with_quality(quality)
            .unwrap()
            .with_window_bits(10)
            .unwrap();
        save(
            &format!("dictionary_q{quality}"),
            &input,
            &burli::compress_with_options(&input, &options).unwrap(),
        );
    }
}
