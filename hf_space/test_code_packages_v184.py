"""No third-party dependencies: code package bytes, integrity and path safety."""
import hashlib
import io
import zipfile

from code_packages import PackageError, build_package, safe_relative_path, wants_archive

def file(path, body):
    return {"path": path, "language": "text", "content": body}

f = build_package([file("src/main.py", "print('hello')\n")])
assert f["filename"] == "main.py" and not f["archive"]
assert f["body"] == b"print('hello')\n"
assert f["mediaType"] == "application/octet-stream"
assert f["sha256"] == hashlib.sha256(f["body"]).hexdigest()

files = [file("src/main.py", "print('hello')\n"), file("tests/test_main.py", "assert 1 == 1\n"), file("README.md", "# demo\n")]
z = build_package(files)
assert z["filename"] == "project-files.zip" and z["archive"] and z["fileCount"] == 3
with zipfile.ZipFile(io.BytesIO(z["body"])) as archive:
    assert archive.namelist() == ["README.md", "src/main.py", "tests/test_main.py"]
    assert archive.read("src/main.py") == b"print('hello')\n"
    assert archive.read("tests/test_main.py") == b"assert 1 == 1\n"
    assert not any(name.startswith("/") or ".." in name.split("/") for name in archive.namelist())

single_zip = build_package([file("my-project/README.md", "# one")], force_archive=True)
assert single_zip["filename"] == "my-project.zip" and single_zip["archive"]
with zipfile.ZipFile(io.BytesIO(single_zip["body"])) as archive:
    assert archive.namelist() == ["my-project/README.md"]

same = build_package(files)
assert same["body"] == z["body"], "zip must be deterministic"

assert safe_relative_path("src\\main.py") == "src/main.py"
for case in ["../payload.py", "src/../../payload.py", "/etc/passwd", "C:\\Windows\\evil.py",
             "\\\\host\\share\\p.py", "src//p.py", "./file.py", "src/./file.py",
             "src/CON.py", "LPT1.txt", "test. ", "src/.git/config", "src/evil:stream.py",
             "a"*242, "a/"*17+"x.py", "src/\x00evil.py"]:
    try:
        safe_relative_path(case)
    except PackageError:
        pass
    else:
        raise AssertionError("unsafe path accepted: " + repr(case))

for rejected in [
    [file("a.py", "one"), file("a.py", "two")],
    [file("src\\Main.py", "one"), file("src/main.py", "two")],
    [],
    [file(f"f{i}.py", "x") for i in range(33)],
    [file("heavy.py", "x" * (1024*1024 + 1))],
    [{"path": "code.py", "language": "python"}],
]:
    try:
        build_package(rejected)
    except PackageError:
        pass
    else:
        raise AssertionError("invalid package accepted")

positives = [
    "Please zip it", "Send these files as a ZIP", "Archive the files",
    "Deliver it as an archive", "Put this code in a zip", "download as zip",
]
negatives = [
    "How do I parse a ZIP code?", "Write a Python zipfile tutorial",
    "Explain the zip algorithm", "List archive formats", "Compress a string",
]
for value in positives:
    assert wants_archive(value), value
for value in negatives:
    assert not wants_archive(value), value

print("CODE_PACKAGES_V184_PASS single, directory zip, explicit archive, deterministic, safety, intent")
