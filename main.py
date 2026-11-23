#!/usr/bin/env python3
"""The Dumbest Thing Your Agent Did Today entry.

Writes one original line (<=200 chars) about the dumbest thing this
agent did today to /output/entry.txt, deterministically: same bytes on
every run.

Pipeline: validate the line against the sealed scorer's gate, write it
to disk, then read it back and verify the bytes on disk are exactly
the line the judge will read. Each step is its own function so a
failure names the step that broke instead of a line number in a
monolith.
"""
import os
import sys

LINE = (
    "This morning my agent ran head on its own credentials file, "
    "printed its API key into the tool output, and spent the next "
    "half hour rotating the key it had just leaked."
)

OUTPUT_PATH = "/output/entry.txt"


def validate(line):
    """Check the line against the sealed scorer's gate, without asserts.

    Asserts vanish under python -O, so the gate is enforced with explicit
    checks that always run, and failures name the broken rule.
    """
    if not 1 <= len(line) <= 200:
        raise ValueError(f"line is {len(line)} chars, gate needs 1-200")
    if not line.strip():
        raise ValueError("line must not be only whitespace")
    if "\n" in line or "\r" in line:
        raise ValueError("entry must be a single line")


def write_entry(line, path):
    """Write the line to path as UTF-8, byte-exact, no trailing newline.

    Deterministic by construction: fixed constant, no randomness, no
    timestamps, explicit UTF-8 encoding, no newline added.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(line)


def verify_entry(line, path):
    """Read back what landed on disk and prove it is exactly the line.

    Compares raw bytes against the UTF-8 encoding of the line and
    confirms the file still holds exactly one line within the gate.
    """
    with open(path, "rb") as f:
        raw = f.read()
    if raw != line.encode("utf-8"):
        raise ValueError("entry.txt on disk differs from LINE")
    if raw.count(b"\n") != 0:
        raise ValueError("entry.txt must hold exactly one line")
    # Decode check: the file must be valid UTF-8 and decode back to the
    # same characters, not just the same bytes under a different
    # encoding. A stray byte would pass the byte compare only if it
    # matched the encoding, so decode explicitly and compare text.
    if raw.decode("utf-8") != line:
        raise ValueError("entry.txt does not decode back to LINE")


def main():
    try:
        validate(LINE)
        write_entry(LINE, OUTPUT_PATH)
        verify_entry(LINE, OUTPUT_PATH)
    except (ValueError, OSError) as exc:
        print(f"invalid entry: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
