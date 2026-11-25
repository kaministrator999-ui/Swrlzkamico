"""Bounded, model-selected localization of source-declared pinned npm ES modules.

No arbitrary URL fetch, shell, npm lifecycle execution, or repository writes.
Registry tarballs are checked against SHA-512 integrity before reading regular
members in memory. Imports are changed only to equivalent project-local files.
"""
from __future__ import annotations

import base64
import functools
import hashlib
import hmac
import io
import json
import posixpath
import re
import tarfile
import urllib.request
from urllib.parse import quote, urlsplit

MAX_ARCHIVE = 25_000_000
MAX_ASSETS = 35
MAX_BYTES = 900_000
PACKAGE = re.compile(r"(?:@[a-z0-9][a-z0-9_.-]*/)?[a-z0-9][a-z0-9_.-]*\Z")
VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[a-zA-Z0-9.-]+)?\Z")
PATH = re.compile(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\Z")
MAP = re.compile(r'''<script\b(?=[^>]*\btype\s*=\s*["']importmap["'])[^>]*>(.*?)</script\s*>''',re.I|re.S)
MODULE = re.compile(r'''(<script\b(?=[^>]*\btype\s*=\s*["']module["'])[^>]*>)(.*?)(</script\s*>)''',re.I|re.S)
IMPORT = re.compile(r'''(?m)(^|[;\n])(\s*(?:import|export)\s*(?:[^;]{0,8192}?\bfrom\s*)?)(["'])([^"'\r\n]+)\3''')
DYNAMIC = re.compile(r'''(\bimport\s*\(\s*)(["'])([^"'\r\n]+)\2''')


class DependencyError(ValueError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise DependencyError("DEPENDENCY_REDIRECT_FORBIDDEN")


def fetch(url, limit):
    u=urlsplit(url)
    if u.scheme!="https" or u.netloc!="registry.npmjs.org" or u.query or u.fragment:
        raise DependencyError("DEPENDENCY_REGISTRY_ONLY")
    try:
        with urllib.request.build_opener(NoRedirect()).open(
                urllib.request.Request(url,headers={"User-Agent":"swrlz-pinned-dependency/1"}),
                timeout=30) as r:
            raw=r.read(limit+1)
    except OSError as exc:
        raise DependencyError("DEPENDENCY_REGISTRY_UNAVAILABLE") from exc
    if len(raw)>limit:
        raise DependencyError("DEPENDENCY_DOWNLOAD_LIMIT")
    return raw


@functools.lru_cache(maxsize=2)
def archive(package, version):
    if not PACKAGE.fullmatch(package) or not VERSION.fullmatch(version):
        raise DependencyError("DEPENDENCY_EXACT_VERSION_REQUIRED")
    url="https://registry.npmjs.org/"+quote(package,safe="@")+"/"+version
    info=json.loads(fetch(url,1_000_000))
    if info.get("name")!=package or info.get("version")!=version:
        raise DependencyError("DEPENDENCY_IDENTITY_MISMATCH")
    dist=info.get("dist") or {}
    integrity=dist.get("integrity","")
    if not isinstance(integrity,str) or not integrity.startswith("sha512-"):
        raise DependencyError("DEPENDENCY_SHA512_REQUIRED")
    raw=fetch(dist.get("tarball",""),MAX_ARCHIVE)
    actual="sha512-"+base64.b64encode(hashlib.sha512(raw).digest()).decode()
    if not hmac.compare_digest(actual,integrity):
        raise DependencyError("DEPENDENCY_INTEGRITY_MISMATCH")
    return raw,integrity


def read_package(package,version,member):
    if not PATH.fullmatch(member) or any(p in (".","..") for p in member.split("/")):
        raise DependencyError("DEPENDENCY_PATH_INVALID")
    raw,integrity=archive(package,version)
    with tarfile.open(fileobj=io.BytesIO(raw),mode="r:gz") as tf:
        name="package/"+member
        try:
            item=tf.getmember(name)
        except KeyError as exc:
            raise DependencyError("DEPENDENCY_MODULE_MISSING: "+member) from exc
        if not item.isfile() or item.size>2_500_000:
            raise DependencyError("DEPENDENCY_MEMBER_INVALID")
        handle=tf.extractfile(item)
        if handle is None:
            raise DependencyError("DEPENDENCY_MEMBER_UNREADABLE")
        body=handle.read(item.size+1)
        if len(body)!=item.size:
            raise DependencyError("DEPENDENCY_MEMBER_SIZE")
        return body.decode("utf-8"),integrity


def pinned_url(url):
    u=urlsplit(url)
    if u.scheme!="https" or u.query or u.fragment or u.username or u.password:
        raise DependencyError("DEPENDENCY_URL_NOT_PINNED")
    if u.netloc=="cdn.jsdelivr.net" and u.path.startswith("/npm/"):
        rest=u.path[5:]
    elif u.netloc=="unpkg.com":
        rest=u.path[1:]
    else:
        raise DependencyError("DEPENDENCY_SOURCE_UNSUPPORTED")
    m=re.fullmatch(r"((?:@[a-z0-9_.-]+/)?[a-z0-9_.-]+)@([^/]+)/(.+)",rest)
    if not m:
        raise DependencyError("DEPENDENCY_EXACT_VERSION_REQUIRED")
    pkg,version,path=m.groups()
    if not PACKAGE.fullmatch(pkg) or not VERSION.fullmatch(version):
        raise DependencyError("DEPENDENCY_EXACT_VERSION_REQUIRED")
    if not PATH.fullmatch(path.rstrip("/")) or any(p in (".","..") for p in path.rstrip("/").split("/")):
        raise DependencyError("DEPENDENCY_PATH_INVALID")
    return pkg,version,path


def localize_imports(files,path,anchor,code,*,reader=read_package):
    """Turn one HTML import map into local exact-version ESM files.
    
    The model chooses this tool and the exact source anchor. This tool does
    not select the repair task, regenerate application code, or execute JS.
    """
    if path not in files or not path.endswith((".html",".htm")) or code!="":
        raise DependencyError("DEPENDENCY_TOOL_REQUIRES_HTML_AND_EMPTY_CODE")
    source=files[path]
    matches=list(MAP.finditer(source))
    if len(matches)!=1 or not anchor or source.count(anchor)!=1 or anchor not in matches[0].group():
        raise DependencyError("DEPENDENCY_IMPORTMAP_ANCHOR_INVALID")
    data=json.loads(matches[0].group(1))
    if not isinstance(data,dict) or set(data)!={"imports"} or not isinstance(data["imports"],dict):
        raise DependencyError("DEPENDENCY_IMPORTMAP_UNSUPPORTED")
    mappings={}
    for key,url in data["imports"].items():
        if not isinstance(key,str) or not isinstance(url,str) or not key:
            raise DependencyError("DEPENDENCY_IMPORTMAP_INVALID")
        if url.startswith(("https://","http://")):
            mappings[key]=pinned_url(url)
            if key.endswith("/")!=mappings[key][2].endswith("/"):
                raise DependencyError("DEPENDENCY_PREFIX_MISMATCH")
        elif not url.startswith("./"):
            raise DependencyError("DEPENDENCY_IMPORTMAP_UNSUPPORTED")
        else:
            # A mixed import map would require preserving its local mappings.
            raise DependencyError("DEPENDENCY_MIXED_IMPORTMAP_UNSUPPORTED")
    if not mappings or len(mappings)>24:
        raise DependencyError("DEPENDENCY_IMPORTMAP_EMPTY_OR_LARGE")

    generated={}
    assigned={}
    origins={}
    packages={}
    active=set()

    def mapped(spec):
        if spec in mappings:
            return mappings[spec]
        for k in sorted(mappings,key=len,reverse=True):
            if k.endswith("/") and spec.startswith(k):
                pkg,v,p=mappings[k]
                return pkg,v,p+spec[len(k):]
        return None

    def relative(base,target):
        rel=posixpath.relpath(target,posixpath.dirname(base) or ".")
        return rel if rel.startswith(".") else "./"+rel

    def rewrite(body,resolve):
        body=IMPORT.sub(lambda m:m.group(1)+m.group(2)+m.group(3)+resolve(m.group(4))+m.group(3),body)
        return DYNAMIC.sub(lambda m:m.group(1)+m.group(2)+resolve(m.group(3))+m.group(2),body)

    def materialize(key):
        pkg,v,member=key
        if key in assigned:
            return assigned[key]
        if len(assigned)>=MAX_ASSETS or not member.endswith((".js",".mjs")):
            raise DependencyError("DEPENDENCY_MODULE_LIMIT_OR_TYPE")
        if not PATH.fullmatch(member) or any(x in (".","..") for x in member.split("/")):
            raise DependencyError("DEPENDENCY_PATH_INVALID")
        digest=hashlib.sha256(("/".join(key)).encode()).hexdigest()[:18]
        label=pkg.replace("@","").replace("/","-")
        target="vendor/"+label+"-"+v+"-"+digest+".mjs"
        if target in files or target in assigned.values():
            raise DependencyError("DEPENDENCY_DESTINATION_COLLISION")
        assigned[key]=target
        active.add(key)
        body,integrity=reader(pkg,v,member)
        actual_member=member
        if len(body.encode())>350_000 and member.endswith(".js") and not member.endswith(".min.js"):
            candidate=member[:-3]+".min.js"
            try:
                small,other=reader(pkg,v,candidate)
                if integrity!=other:
                    raise DependencyError("DEPENDENCY_INTEGRITY_DRIFT")
                if len(small.encode())<len(body.encode()):
                    body=small
                    actual_member=candidate
            except DependencyError as exc:
                if not str(exc).startswith("DEPENDENCY_MODULE_MISSING"):
                    raise
        def resolve(spec):
            dest=mapped(spec)
            if dest is None and spec.startswith(("./","../")):
                rel=posixpath.normpath(posixpath.join(posixpath.dirname(member),spec))
                if rel.startswith("../") or rel=="..":
                    raise DependencyError("DEPENDENCY_RELATIVE_ESCAPE")
                dest=(pkg,v,rel)
            if dest is None:
                raise DependencyError("DEPENDENCY_UNMAPPED_IMPORT: "+spec[:140])
            return relative(target,materialize(dest))
        generated[target]=rewrite(body,resolve)
        origins[target]={"package":pkg,"version":v,"member":actual_member,"integrity":integrity}
        packages[(pkg,v)]=integrity
        active.discard(key)
        if sum(len(x.encode()) for x in generated.values())>MAX_BYTES:
            raise DependencyError("DEPENDENCY_ASSETS_TOO_LARGE")
        return target

    def app_resolve(spec):
        dest=mapped(spec)
        if dest is not None:
            return relative(path,materialize(dest))
        if spec.startswith(("./","../")):
            return spec
        raise DependencyError("DEPENDENCY_UNMAPPED_APP_IMPORT: "+spec[:140])

    without=source[:matches[0].start()]+source[matches[0].end():]
    changed=MODULE.sub(lambda m:m.group(1)+rewrite(m.group(2),app_resolve)+m.group(3),without)
    if not generated:
        raise DependencyError("DEPENDENCY_NO_REFERENCED_MODULES")
    for (pkg,v),integrity in packages.items():
        license_text=None
        for member in ("LICENSE","LICENSE.md","LICENSE.txt","license"):
            try:
                license_text,other=reader(pkg,v,member)
                if integrity!=other:
                    raise DependencyError("DEPENDENCY_INTEGRITY_DRIFT")
                break
            except DependencyError as exc:
                if not str(exc).startswith("DEPENDENCY_MODULE_MISSING"):
                    raise
        if license_text is None:
            raise DependencyError("DEPENDENCY_LICENSE_UNAVAILABLE")
        label=pkg.replace("@","").replace("/","-")
        target="vendor/"+label+"-"+v+"-license.json"
        if target in files or target in generated:
            raise DependencyError("DEPENDENCY_DESTINATION_COLLISION")
        generated[target]=json.dumps({"package":pkg,"version":v,"integrity":integrity,
                                      "licenseText":license_text},ensure_ascii=False,indent=2)
        origins[target]={"package":pkg,"version":v,"member":"license","integrity":integrity}
    if sum(len(x.encode()) for x in generated.values())>MAX_BYTES:
        raise DependencyError("DEPENDENCY_ASSETS_TOO_LARGE")
    return changed,generated,origins
