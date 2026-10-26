#!/usr/bin/env python3
"""Run a CI command and expose its bounded failure tail through check annotations.

GitHub's checks API can read annotations even when downloading full Actions logs
is unavailable. Arguments are executed directly, never through a shell. No
process environment is printed; values of credential-like environment variables
are redacted from streamed output and the annotation.
"""
from __future__ import annotations

import argparse
from collections import deque
import os
import re
import subprocess
import sys


def annotation_text(value: str, limit: int = 7600) -> str:
    """Escape workflow-command data without splitting an encoded character."""
    parts = []
    size = 0
    for char in reversed(value):
        escaped = {'%': '%25', '\r': '%0D', '\n': '%0A'}.get(char, char)
        cost = len(escaped.encode('utf-8', errors='replace'))
        if size + cost > limit:
            break
        parts.append(escaped)
        size += cost
    return ''.join(reversed(parts))


def credential_values(environment: dict[str, str]) -> list[str]:
    values = set()
    for name, value in environment.items():
        if re.search(r'(?:TOKEN|SECRET|PASSWORD|CREDENTIAL|PRIVATE_KEY|API_KEY)', name, re.I):
            values.update(part for part in [value, *value.splitlines()] if len(part) >= 8)
    return sorted(values, key=len, reverse=True)


def redact(value: str, credentials: list[str]) -> str:
    for credential in credentials:
        value = value.replace(credential, '[REDACTED]')
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label', required=True)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('a command is required after --')
    credentials = credential_values(dict(os.environ))
    tail: deque[str] = deque(maxlen=200)
    print('CI check: ' + redact(args.label, credentials), flush=True)
    try:
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, encoding='utf-8', errors='replace', bufsize=1) as process:
            assert process.stdout is not None
            for line in process.stdout:
                safe = redact(line, credentials)
                sys.stdout.write(safe)
                sys.stdout.flush()
                tail.append(safe[-16000:])
            code = process.wait()
    except OSError as error:
        code = 127
        tail.append(redact(str(error), credentials))
    if code:
        heading = annotation_text(redact(f'{args.label} failed with exit {code}.', credentials), 800)
        body = annotation_text(''.join(tail), 7600 - len(heading.encode('utf-8')) - 3)
        print('\n::error::' + heading + '%0A' + body, flush=True)
    return code if code >= 0 else 128 - code


if __name__ == '__main__':
    raise SystemExit(main())
