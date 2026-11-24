#!/usr/bin/env python3
"""Produce small browser-renderable §E static files from sealed v11.552 HTML.

The exact SHA-sealed 526-patch source is unchanged. A delivery-only transform
moves its 10.7 MB synchronous-order-preserving ES module into one external file,
keeping *each* served file under 10,000,000 bytes (also under 10 MiB). This
avoids large-file/LFS download handling on static hosting.
"""
import argparse
import hashlib
import json
import subprocess
import tempfile
import shutil
from pathlib import Path

SOURCE_START = b'<script type="module">\n(async()=>{\nconst app=document.getElementById'
SOURCE_CLOSE = b'\n</script>\n</body>\n</html>'
MODULE = "swrlz-engine-v11.552.js"
TAG = ('<script type="module" src="./'+MODULE+'"></script>').encode("ascii")
MAX_FILE = 10_000_000


def digest(data):
    return hashlib.sha256(data).hexdigest()


def split_html(original):
    if original.count(SOURCE_START) != 1:
        raise ValueError("Cannot locate the one root §E module entry")
    start = original.index(SOURCE_START)
    end = original.rfind(SOURCE_CLOSE)
    if end <= start:
        raise ValueError("Root module closing tag is missing")
    prefix = b'<script type="module">'
    assert original[start:start+len(prefix)] == prefix
    module = original[start+len(prefix):end]
    if not module.startswith(b"\n(async()=>{") or not module.rstrip().endswith(b"})();"):
        raise ValueError("Module does not match the sealed engine entry")
    if b'import.meta' in module:
        raise ValueError("Refuse to relocate module with import.meta-relative paths")
    served = original[:start] + TAG + original[end+len(b'\n</script>'):]
    restored = served.replace(TAG, prefix+module+b'\n</script>', 1)
    if restored != original:
        raise ValueError("Static delivery fails lossless round-trip")
    if '<title>§wyrl§ Engine · Maker v11.546</title>'.encode('utf8') not in served:
        raise ValueError("Static document lost its verified version")
    if len(served) >= MAX_FILE:
        raise ValueError(f"HTML remains over 10MB: {len(served)} bytes")
    return served, module

def compact_module(source):
    """Delivery-only whitespace compaction; original sealed HTML is unchanged.

    Pin esbuild for JS-aware whitespace/comment handling (including templates,
    regexes and quoted strings). Disable semantic minification and mangling.
    """
    with tempfile.TemporaryDirectory(prefix="se546-module-") as temp:
        folder=Path(temp)
        original=folder/"source.js"
        output=folder/"compact.js"
        original.write_bytes(source)
        subprocess.run(["npx","--yes","esbuild@0.25.12",str(original),
                        "--minify-whitespace","--legal-comments=none",
                        "--charset=utf8","--target=es2022",
                        "--outfile="+str(output)],check=True,timeout=180)
        compact=output.read_bytes()
    if not compact or len(compact)>=MAX_FILE:
        raise ValueError(f"Compacted JavaScript still over 10MB: {len(compact)} bytes")
    print("SE552_DELIVERY_MODULE_COMPACTED",len(source),len(compact),flush=True)
    return compact


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.output).resolve()
    receipt_path = root/"SOURCE.json"
    receipt = json.loads(receipt_path.read_text("utf8"))
    page = (root/"index.html").read_bytes()
    other = (root/"modeler.html").read_bytes()
    if page != other:
        raise ValueError("Index/modeler must share the same sealed source")
    if len(page) != receipt["finalBytes"] or digest(page) != receipt["finalSha256"]:
        raise ValueError("Do not transform a source whose original SHA receipt fails")
    served, source_module = split_html(page)
    # Only the public JS delivery changes; the 526-patch source SHA above is
    # still validated before any transformation. Keep the account-repair
    # receipt separately inspectable in SOURCE.json.
    from delivery_account_startup_repair_v11_553 import apply as account_repair
    repaired_module, account_receipt = account_repair(source_module)
    from delivery_uv_first_starter_v11_554 import apply as uv_first_starter
    starter_module, starter_receipt = uv_first_starter(repaired_module)
    module = compact_module(starter_module)
    (root/"index.html").write_bytes(served)
    (root/"modeler.html").write_bytes(served)
    (root/MODULE).write_bytes(module)
    # Ship locally hosted, version-pinned open-source xatlas WASM. Never
    # depend on a CDN or silently fake the UV tool if the binary is absent.
    with tempfile.TemporaryDirectory(prefix="se555-xatlas-deps-") as depdir:
        subprocess.run(["npm","install","--prefix",depdir,"--no-save",
                        "--ignore-scripts","--no-audit","--no-fund",
                        "xatlas-wasm@0.1.3"],check=True,timeout=180)
        dist=Path(depdir)/"node_modules/xatlas-wasm/dist"
        dest=root/"assets/uv-unwrapper"
        dest.mkdir(parents=True,exist_ok=True)
        for name in ("index.mjs","xatlas.wasm"):
            src=dist/name
            if not src.is_file() or not src.stat().st_size:
                raise ValueError("xatlas package missing required runtime "+name)
            if src.stat().st_size>=MAX_FILE:
                raise ValueError("xatlas "+name+" exceeds static host file limit")
            shutil.copy2(src,dest/name)
        shared_root=Path(__file__).resolve().parents[1]/"runtime"
        shared_files=("uv_atlas_core_v11_555.mjs","uv_lscm_core_v11_555.mjs")
        for name in shared_files:
            shutil.copy2(shared_root/name,dest/name)
        # Preserve the vendor's MIT attribution with the shipped WASM.
        for name in ("LICENSE","NOTICE"):
            license_file=dist.parent/name
            if license_file.is_file():
                shutil.copy2(license_file,dest/("xatlas-"+name))
        print("SE555_LOCAL_XATLAS_WASM_BUNDLED",
              {name:(dest/name).stat().st_size for name in
               ("index.mjs","xatlas.wasm",*shared_files)},flush=True)

    receipt["accountStartupDeliveryRepair"] = account_receipt
    receipt["uvFirstHumanoidDelivery"] = starter_receipt
    receipt["xatlasWasmDelivery"] = {
      "version":"xatlas-wasm@0.1.3",
      "files":{p.name:{"bytes":p.stat().st_size,
                        "sha256":digest(p.read_bytes())}
               for p in (root/"assets/uv-unwrapper").iterdir()}
    }
    receipt["staticDelivery"] = {
        "mode": "external-es-module",
        "verifiedSourceSha256": receipt["finalSha256"],
        "module": MODULE,
        "sourceModuleBytes": len(source_module),
        "sourceModuleSha256": digest(source_module),
        "repairedModuleBytes": len(repaired_module),
        "repairedModuleSha256": digest(repaired_module),
        "deliveryTransform": "esbuild-0.25.12-whitespace-only",
        "moduleBytes": len(module),
        "moduleSha256": digest(module),
        "indexBytes": len(served),
        "indexSha256": digest(served),
        "modelerBytes": len(served),
        "modelerSha256": digest(served),
        "fileLimitBytes": MAX_FILE,
    }
    receipt_path.write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf8")
    assert (root/"index.html").read_bytes() == (root/"modeler.html").read_bytes()
    assert len((root/MODULE).read_bytes()) < MAX_FILE
    print("SE552_STATIC_DELIVERY_PASS", json.dumps(receipt["staticDelivery"], sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
