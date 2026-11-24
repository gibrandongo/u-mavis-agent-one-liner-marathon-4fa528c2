#!/usr/bin/env python3
"""One-Liner Marathon entry.

Writes a single one-line comedy joke to $MAKEFUN_OUTPUT_DIR/entry.txt.

Python 3.13, standard library only. No network, no clock, no randomness.
"""

import os
import sys

JOKE = (
    "I told my therapist my phone listens to me. She said, "
    "'Of course it does \u2014 it's the only thing in your life "
    "that pays attention.'"
)

MAX_CHARS = 280


def validate(line):
    """Check the joke line against the competition's guards."""
    if not line or not line.strip():
        raise ValueError("joke line is empty or whitespace only")
    if "\n" in line or "\r" in line:
        raise ValueError("joke line must be exactly one line")
    if len(line) > MAX_CHARS:
        raise ValueError("joke line exceeds 280 characters")
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in line):
        raise ValueError("joke line contains control characters")
    return line


def main():
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not output_dir:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 1

    try:
        line = validate(JOKE)
    except ValueError as exc:
        print("invalid joke line: %s" % exc, file=sys.stderr)
        return 1
    payload = (line + "\n").encode("utf-8")

    os.makedirs(output_dir, exist_ok=True)
    target = os.path.join(output_dir, "entry.txt")
    tmp = os.path.join(output_dir, "entry.txt.tmp")

    try:
        with open(tmp, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, target)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise

    # Byte-level re-read verify: what is on disk must be exactly the payload.
    with open(target, "rb") as handle:
        on_disk = handle.read()
    if on_disk != payload:
        raise SystemExit("verification failed: entry.txt does not match payload")

    return 0


if __name__ == "__main__":
    sys.exit(main())
