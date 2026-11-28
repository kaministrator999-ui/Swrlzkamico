#!/usr/bin/env python3
"""Publish trusted static applications into pre-authorized private OVH slots.
No root operations, firewall changes, arbitrary unit commands or chat/engine mutations.
"""
import hashlib
import io
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
import tempfile
import time
import urllib.request
import urllib.error

SOURCE=Path("/srv/swrlz/source")
HOME=Path.home()
ROOT=HOME/".local/share/swrlz-hosting"
UNITS=HOME/".config/systemd/user"
ENV=dict(os.environ,XDG_RUNTIME_DIR=f"/run/user/{os.getuid()}",
         DBUS_SESSION_BUS_ADDRESS=f"unix:path=/run/user/{os.getuid()}/bus")
def ctl(*args):
    return subprocess.run(["/usr/bin/systemctl","--user",*args],env=ENV,check=True,timeout=25)
def get(url):
    with urllib.request.urlopen(url,timeout=3) as r:
        return r.read()
def atomic_link(path,target):
    temp=path.with_name(".current-next")
    temp.unlink(missing_ok=True)
    temp.symlink_to(target)
    os.replace(temp,path)
def publish(port,rev):
    source=f"hosting/slot-{port}"
    if not (SOURCE/source/"index.html").is_file(): return
    upstream=8766+port-8443
    base=ROOT/str(port)
    release=base/"releases"/rev
    current=base/"current"
    unit=f"swrlz-hosting-{port}.service"
    unitpath=UNITS/unit
    base.mkdir(parents=True,exist_ok=True)
    release.parent.mkdir(parents=True,exist_ok=True)
    UNITS.mkdir(parents=True,exist_ok=True)
    if current.exists() and not current.is_symlink():
        raise RuntimeError("Current release is not a managed symlink")
    previous=os.readlink(current) if current.is_symlink() else None
    unit_text=("[Unit]\nDescription=SWRLZ trusted static slot "+str(port)+"\n"
               "[Service]\nType=simple\n"
               f"ExecStart=/usr/bin/python3 -m http.server {upstream} --bind 127.0.0.1 --directory {current}\n"
               "Restart=on-failure\nRestartSec=2\nNoNewPrivileges=yes\n"
               "[Install]\nWantedBy=default.target\n")
    had_unit=unitpath.exists()
    if had_unit and unitpath.read_text()!=unit_text:
        raise RuntimeError("Refusing to overwrite different service")
    if not had_unit:
        import socket
        with socket.socket() as sock:
            sock.settimeout(1)
            if sock.connect_ex(("127.0.0.1",upstream))==0:
                raise RuntimeError("Unmanaged upstream already listening")
    if not release.exists():
        raw=subprocess.check_output(["git","-C",str(SOURCE),"archive",rev,source],timeout=30)
        if len(raw)>64*1024*1024: raise RuntimeError("Static bundle exceeds 64 MiB")
        with tempfile.TemporaryDirectory(dir=release.parent) as tmp:
            stage=Path(tmp)
            with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
                total=0
                for m in tar:
                    p=PurePosixPath(m.name)
                    if p.is_absolute() or ".." in p.parts or not(m.isfile() or m.isdir()):
                        raise RuntimeError("Unsafe archive member")
                    total+=m.size
                    if total>64*1024*1024: raise RuntimeError("Static content exceeds limit")
                    tar.extract(m,stage)
            candidate=stage/source
            if not (candidate/"index.html").is_file(): raise RuntimeError("Missing entry page")
            candidate.rename(release)
    expected=hashlib.sha256((release/"index.html").read_bytes()).hexdigest()
    try:
        atomic_link(current,release)
        if not had_unit: unitpath.write_text(unit_text)
        ctl("daemon-reload")
        ctl("enable",unit)
        ctl("restart",unit)
        for _ in range(15):
            try:
                body=get(f"http://127.0.0.1:{upstream}/")
                if hashlib.sha256(body).hexdigest()==expected: break
            except (OSError,urllib.error.URLError): pass
            time.sleep(1)
        else: raise RuntimeError("Static HTTP verification failed")
        ctl("is-enabled",unit)
        ctl("is-active",unit)
    except Exception:
        if previous:
            atomic_link(current,previous)
            ctl("restart",unit)
        elif not had_unit:
            subprocess.run(["/usr/bin/systemctl","--user","disable","--now",unit],env=ENV,timeout=25)
            unitpath.unlink(missing_ok=True)
            current.unlink(missing_ok=True)
            ctl("daemon-reload")
        raise
    print(f"SWRLZ_HOSTING_SLOT_OK port={port} upstream={upstream} sha256={expected}",flush=True)
def main():
    if os.geteuid()==0: raise RuntimeError("Must run unprivileged")
    rev=subprocess.check_output(["git","-C",str(SOURCE),"rev-parse","HEAD"],text=True).strip()
    for port in range(8444,8451): publish(port,rev)
if __name__=="__main__": main()
