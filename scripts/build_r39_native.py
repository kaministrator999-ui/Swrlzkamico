"""Build R39 CPython extensions for the current Space interpreter, not a GitHub runner ABI."""
from __future__ import annotations
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import sysconfig

def build(root: Path | None = None) -> dict:
    root = (root or Path(__file__).resolve().parents[1]).resolve()
    import numpy
    source_dir = root / "native"
    target_dir = root / "swyrlz"
    suffix = sysconfig.get_config_var("EXT_SUFFIX")
    if not suffix:
        raise RuntimeError("CPython extension suffix unavailable")
    cc = shlex.split(os.environ.get("CC") or sysconfig.get_config_var("CC") or "cc")
    includes = [sysconfig.get_path("include"), numpy.get_include()]
    result = {"python": sys.version.split()[0], "numpy": numpy.__version__, "extensions": {}}
    for name, source in (("_r39_native", "r39_native.c"), ("_r39_batch", "r39_batch.c")):
        src = source_dir / source
        output = target_dir / (name + suffix)
        if not src.is_file():
            raise FileNotFoundError(src)
        command = cc + ["-O3", "-fPIC", "-shared", "-std=c11", "-pthread",
                        "-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION"]
        command += ["-I" + inc for inc in includes]
        command += [str(src), "-o", str(output), "-lm"]
        subprocess.run(command, check=True, capture_output=True, text=True, timeout=180)
        result["extensions"][name] = str(output)
    # Verify both binaries in a fresh process so the import cache cannot mask failure.
    probe = subprocess.run([sys.executable, "-c",
        "from swyrlz import r39_native; assert r39_native.available(), r39_native.diagnostics(); "
        "assert r39_native.matmat_available(), r39_native.diagnostics(); print(r39_native.diagnostics())"],
        cwd=str(root), env={**os.environ, "PYTHONPATH": str(root) + os.pathsep + os.environ.get("PYTHONPATH", "")},
        capture_output=True, text=True, timeout=30)
    if probe.returncode:
        raise RuntimeError("Native import probe failed: " + probe.stderr[-1000:] + probe.stdout[-1000:])
    result["verified"] = True
    return result

if __name__ == "__main__":
    print(json.dumps(build()), flush=True)
