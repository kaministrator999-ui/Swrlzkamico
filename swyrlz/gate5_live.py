from __future__ import annotations

import hashlib
import json
import os
import struct
import time
from pathlib import Path

RAW = Path(os.environ.get("SWRLZ_R39_PATH", "/tmp/swrlz-admin/live/SWYRLZ_LALM_R39_PHYSICAL_BASE_REPAIRED.§wyrlzx"))
EXPECTED_RAW_SIZE = 233_637_480
EXPECTED_RAW_SHA256 = "65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee"
SWRLZX_MAGIC = b"SWRLZX\r\n"
INTEGRITY_MAGIC = b"SXI1"
HEADER_BYTES = 128
TOC_ENTRY_BYTES = 128
ENDIAN_MARKER = 0x01020304
SECTION_NAMES = {1:"MANIFEST",2:"ARCHITECTURE_GRAPH",3:"TOKENIZER",4:"TENSOR_DIRECTORY",5:"TENSOR_DATA",6:"QUANTIZATION_PROFILE",7:"GENERATION_PROFILE",8:"STREAM_CONTRACT",9:"MODULE_INTERFACES",10:"LINEAGE",11:"INTEGRITY",12:"SIGNATURE",0x7FFFFFFF:"VENDOR_PRIVATE"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _read_json(handle, entry: dict) -> dict:
    if entry["storedLength"] > 64 * 1024 * 1024:
        raise ValueError(f"SECTION_JSON_TOO_LARGE:{entry['sectionId']}")
    handle.seek(entry["offset"]); raw = handle.read(entry["storedLength"])
    value = json.loads(raw)
    if not isinstance(value, dict): raise ValueError(f"SECTION_JSON_NOT_OBJECT:{entry['sectionId']}")
    return value


def _parse_header_toc(handle, size: int) -> tuple[dict, list[dict]]:
    head = handle.read(HEADER_BYTES)
    if len(head) != HEADER_BYTES or head[:8] != SWRLZX_MAGIC: raise ValueError("CANONICAL_SWRLZX_HEADER_NOT_PRESENT_AT_OFFSET_0")
    major, minor, hbytes, flags, endian, file_bytes, toc_offset, toc_count, toc_entry_bytes, manifest_id, tensor_dir_id, lineage_id, integrity_id = struct.unpack_from("<HHIIIQQIIIIII", head, 8)
    if major != 1 or hbytes != HEADER_BYTES or endian != ENDIAN_MARKER or toc_entry_bytes != TOC_ENTRY_BYTES: raise ValueError("SWRLZX_HEADER_CONTRACT_INVALID")
    if file_bytes != size or toc_offset != HEADER_BYTES or toc_count <= 0 or toc_count > 4096: raise ValueError("SWRLZX_HEADER_RANGE_INVALID")
    toc=[]; handle.seek(toc_offset)
    for _ in range(toc_count):
        b=handle.read(TOC_ENTRY_BYTES)
        if len(b)!=TOC_ENTRY_BYTES: raise ValueError("SWRLZX_TOC_EOF")
        sid, stype, sflags, align, off, stored, logical, codec, schema=struct.unpack_from("<IIIIQQQII",b,0)
        if align < 64 or align & (align-1) or off % align or off < HEADER_BYTES+toc_count*TOC_ENTRY_BYTES or off+stored > size: raise ValueError(f"SWRLZX_SECTION_RANGE_INVALID:{sid}")
        toc.append({"sectionId":sid,"sectionType":stype,"sectionTypeName":SECTION_NAMES.get(stype,f"TYPE_{stype}"),"offset":off,"storedLength":stored,"logicalLength":logical,"codec":codec,"schemaVersion":schema,"sha256":b[48:80].hex()})
    return {"major":major,"minor":minor,"flags":flags,"fileBytes":file_bytes,"tocOffset":toc_offset,"tocCount":toc_count,"manifestSectionId":manifest_id,"tensorDirectorySectionId":tensor_dir_id,"lineageSectionId":lineage_id,"integritySectionId":integrity_id,"rootDigestSha256":head[64:96].hex()},toc


def inspect_r39() -> dict:
    started=time.monotonic()
    if not RAW.is_file(): raise FileNotFoundError(f"R39_NOT_PRESENT: {RAW}")
    size=RAW.stat().st_size; digest=sha256_file(RAW)
    if size!=EXPECTED_RAW_SIZE or digest!=EXPECTED_RAW_SHA256: raise ValueError(f"R39_INTEGRITY_FAILED size={size} sha256={digest}")
    with RAW.open("rb") as handle:
        header,toc=_parse_header_toc(handle,size)
        by_type: dict[int,list[dict]]={}
        for entry in toc: by_type.setdefault(entry["sectionType"],[]).append(entry)
        tokenizer_entry=(by_type.get(3) or [None])[0]; tensor_dir_entry=(by_type.get(4) or [None])[0]; data_entries=by_type.get(5,[])
        tokenizer=_read_json(handle,tokenizer_entry) if tokenizer_entry else {}
        tensor_dir=_read_json(handle,tensor_dir_entry) if tensor_dir_entry else {}
        tensor_count=len(tensor_dir.get("tensors",[])) if isinstance(tensor_dir.get("tensors",[]),list) else 0
        mapped=0; bad=[]; data_by_id={e["sectionId"]:e for e in data_entries}
        for d in tensor_dir.get("tensors",[]) if isinstance(tensor_dir.get("tensors",[]),list) else []:
            try:
                sid=int(d.get("dataSectionId",5)); off=int(d["dataOffsetBytes"]); length=int(d["storedLengthBytes"]); section=data_by_id[sid]
                if off<0 or length<=0 or off+length>section["storedLength"]: raise ValueError()
                mapped+=1
            except Exception: bad.append(str(d.get("name") or d.get("tensorId") or "<unknown>"))
        integrity=(by_type.get(11) or [None])[0]
        integrity_summary=None
        if integrity:
            handle.seek(integrity["offset"]); raw=handle.read(min(integrity["storedLength"],64*1024))
            if raw[:4]==INTEGRITY_MAGIC and len(raw)>=40:
                integrity_summary={"offset":integrity["offset"],"rootDigestSha256":raw[4:36].hex(),"declaredRecordCount":struct.unpack_from("<I",raw,36)[0]}
    required={str(sid):bool(by_type.get(sid)) for sid in (3,4,5)}; blockers=[]
    for sid,present in required.items():
        if not present: blockers.append(f"SECTION_{sid}_NOT_PRESENT_IN_ACTIVE_TOC")
    if not tokenizer.get("tokens"): blockers.append("TOKENIZER_VOCAB_NOT_AVAILABLE")
    if tensor_count<=0: blockers.append("TENSOR_DIRECTORY_EMPTY")
    if bad: blockers.append("TENSOR_DATA_RANGES_INVALID")
    engine={"oneTokenReady":False,"interactiveReady":False}
    if not blockers:
        try:
            from swyrlz.r39_inference import inspect_engine
            engine=inspect_engine(RAW)
            if not engine.get("oneTokenReady"): blockers.append(str(engine.get("code") or "R39_ENGINE_NOT_READY"))
        except Exception as exc:
            blockers.append(f"R39_ENGINE_PROBE_FAILED:{type(exc).__name__}")
    return {"ok":True,"stage":"gate5-r39-local-inference-readiness","modelPath":str(RAW),"rawSize":size,"rawSha256":digest,"containerVerified":True,"canonicalHeaderPresent":True,"header":header,"integrity":integrity_summary,"requiredSectionsRegistered":required,"sectionPayloadLocationsReconstructed":bool(tokenizer_entry and tensor_dir_entry and data_entries),"tokenizer":{"kind":tokenizer.get("kind"),"tokenCount":len(tokenizer.get("tokens",[])),"mergeCount":len(tokenizer.get("merges",[]))},"tensorDirectory":{"tensorCount":tensor_count,"mappedTensorCount":mapped,"invalidTensors":bad[:12],"tensorDataSectionCount":len(data_entries)},"engine":engine,"oneTokenReady":bool(engine.get("oneTokenReady")) and not blockers,"interactiveReady":bool(engine.get("interactiveReady")) and not blockers,"blockers":blockers,"bytesInspectedAfterHash":HEADER_BYTES+header["tocCount"]*TOC_ENTRY_BYTES+(tokenizer_entry["storedLength"] if tokenizer_entry else 0)+(tensor_dir_entry["storedLength"] if tensor_dir_entry else 0)+(min(integrity["storedLength"],64*1024) if integrity else 0),"inspectionMs":int((time.monotonic()-started)*1000)}


if __name__=="__main__":
    try: print(json.dumps(inspect_r39(),ensure_ascii=False,indent=2))
    except Exception as exc:
        print(json.dumps({"ok":False,"error":f"{type(exc).__name__}: {exc}"},ensure_ascii=False,indent=2)); raise
