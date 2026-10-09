// EDUCATIONAL FIXTURE ONLY — NOT a repository native module.
// When Rust tools are available: rustc --edition=2021 --test frame_reconciler.rs -o frame_tests && ./frame_tests
use std::collections::BTreeMap;

#[derive(Debug, PartialEq, Eq)]
struct Frame {
    request_id: String,
    sequence: u64,
    text: String,
}

// Borrow rather than move or mutate caller-owned event frames.
// Returned borrowed strings cannot outlive the input slice.
fn ordered_frames<'a>(frames: &'a [Frame], request_id: &str) -> Vec<&'a str> {
    let mut first_by_sequence: BTreeMap<u64, &'a str> = BTreeMap::new();
    for frame in frames {
        if frame.request_id == request_id && frame.sequence > 0 {
            first_by_sequence
                .entry(frame.sequence)
                .or_insert(frame.text.as_str());
        }
    }
    first_by_sequence.into_values().collect()
}

fn parse_sequence(value: &str) -> Result<u64, std::num::ParseIntError> {
    value.parse::<u64>()
}

#[test]
fn isolates_orders_and_preserves_input() {
    let frames = vec![
        Frame { request_id: "thread-A".into(), sequence: 3, text: "!".into() },
        Frame { request_id: "thread-B".into(), sequence: 1, text: "leak".into() },
        Frame { request_id: "thread-A".into(), sequence: 1, text: "Hi".into() },
        Frame { request_id: "thread-A".into(), sequence: 2, text: " there".into() },
        Frame { request_id: "thread-A".into(), sequence: 2, text: "WRONG".into() },
    ];
    let prior: Vec<(&str, u64, &str)> = frames
        .iter()
        .map(|f| (f.request_id.as_str(), f.sequence, f.text.as_str()))
        .collect();

    assert_eq!(ordered_frames(&frames, "thread-A"), vec!["Hi", " there", "!"]);
    assert!(ordered_frames(&frames, "missing").is_empty());
    assert_eq!(
        frames.iter()
            .map(|f| (f.request_id.as_str(), f.sequence, f.text.as_str()))
            .collect::<Vec<_>>(),
        prior
    );
    assert_eq!(parse_sequence("2").unwrap(), 2);
    assert!(parse_sequence("two").is_err());
}
