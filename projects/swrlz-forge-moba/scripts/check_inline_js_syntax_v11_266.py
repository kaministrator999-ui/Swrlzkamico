#!/usr/bin/env python3
"""Validate actual assembled §E inline JavaScript with Node's parser.

v11.264 shipped syntactically invalid shader array string elements because
source-text assertions and SHA checks alone don't parse script bodies.
Fail closed on missing target script and on any JS parse error. No browser
automation or GPU context is created.
"""
import re
import subprocess
import sys
from pathlib import Path

html_path=Path(sys.argv[1])
html=html_path.read_text(encoding="utf-8")
scripts=re.findall(r"<script\\b[^>]*>(.*?)</script\\s*>",html,flags=re.I|re.S)
targets=[part for part in scripts if "const mistV=[" in part and "vMistAngle" in part]
if len(targets)!=1:
    raise SystemExit(f"Expected one live nebula JS script, found {len(targets)}; inline scripts={len(scripts)}")
body=targets[0]
correct="'varying float vMistAngle;',\\n 'varying vec3 vMistTint;',"
# The two script arrays, mistV and mistF, must be valid JavaScript.
if body.count(correct)!=2:
    raise SystemExit(f"Expected 2 shader array separators, got {body.count(correct)}")
bad="'varying float vMistAngle;'\\n 'varying vec3 vMistTint;',"
if bad in body:
    raise SystemExit("Malformed adjacent shader strings survived the boot fix")
result=subprocess.run(["node","--check","-"],input=body,text=True,capture_output=True)
if result.returncode:
    print(result.stdout)
    print(result.stderr,file=sys.stderr)
    raise SystemExit("§E initialization blocked: assembled inline JS failed Node syntax check")
print(f"INLINE_JS_PARSE_OK | scripts={len(scripts)} | shaderScriptChars={len(body)}")
