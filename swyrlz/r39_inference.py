from __future__ import annotations

import codecs
import json
import mmap
import re
import struct
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator

import numpy as np

from swyrlz.backend import RAW, ensure_r39

ENGINE_ID = "swrlz_r39_python_reference_v1"
MODEL_SHA256 = "65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee"
HEADER_BYTES = 128
TOC_ENTRY_BYTES = 128
MAGIC = b"SWRLZX\r\n"
ENDIAN_MARKER = 0x01020304
SEC_MANIFEST = 1
SEC_ARCH = 2
SEC_TOKENIZER = 3
SEC_TENSOR_DIR = 4
SEC_TENSOR_DATA = 5
SEC_GENERATION = 7
LAYER_KV = [0, 0, 8, 0, 0, 8, 0, 0, 8, 0, 8, 0, 8, 0, 8, 0]
PRE = re.compile(r"'s|'t|'re|'ve|'m|'ll|'d| ?[^\W\d_]+| ?\d+| ?[^\s\w]+|\s+(?!\S)|\s+", re.UNICODE)


class R39InferenceError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class TocEntry:
    section_id: int
    section_type: int
    flags: int
    alignment: int
    offset: int
    stored_length: int
    logical_length: int
    codec: int
    schema_version: int
    sha256: str


def _json_section(mm: mmap.mmap, entry: TocEntry) -> dict[str, Any]:
    try:
        value = json.loads(mm[entry.offset:entry.offset + entry.stored_length])
    except Exception as exc:
        raise R39InferenceError("R39_METADATA_JSON_INVALID", f"Section {entry.section_id} JSON failed: {type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise R39InferenceError("R39_METADATA_JSON_NOT_OBJECT", f"Section {entry.section_id} must be a JSON object.")
    return value


def _bytes_to_unicode() -> tuple[dict[int, str], dict[str, int]]:
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(0xA1, 0xAC + 1)) + list(range(0xAE, 0xFF + 1))
    cs = bs.copy()
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    forward = {b: chr(c) for b, c in zip(bs, cs)}
    return forward, {v: k for k, v in forward.items()}


class BpeTokenizer:
    def __init__(self, spec: dict[str, Any]) -> None:
        self.spec = spec
        self.tokens = [str(x) for x in spec.get("tokens", [])]
        if not self.tokens:
            raise R39InferenceError("R39_TOKENIZER_EMPTY", "Tokenizer has no tokens.")
        self.token_to_id = {t: i for i, t in enumerate(self.tokens)}
        self.ranks = {tuple(m.split(" ", 1)): i for i, m in enumerate(spec.get("merges", [])) if isinstance(m, str) and " " in m}
        self.specials = sorted(((t, i) for i, t in enumerate(self.tokens) if t.startswith("<|") and t.endswith("|>")), key=lambda x: -len(x[0]))
        self.b2u, self.u2b = _bytes_to_unicode()
        self.bos = spec.get("bosTokenId")
        self.eos = spec.get("eosTokenId")
        self.add_bos = bool(spec.get("addBos", False))
        self.add_eos = bool(spec.get("addEos", False))
        kind = str(spec.get("kind", "")).upper()
        if kind not in {"GGML_BPE", "SWYRLZX_BPE"}:
            raise R39InferenceError("R39_TOKENIZER_KIND_UNSUPPORTED", f"Tokenizer kind {kind or '<missing>'} is not supported by the Python reference engine.")

    def encode(self, text: str) -> list[int]:
        out: list[int] = []
        cursor = 0
        while cursor < len(text):
            hit = next(((s, i) for s, i in self.specials if text.startswith(s, cursor)), None)
            if hit:
                out.append(hit[1])
                cursor += len(hit[0])
                continue
            positions = [text.find(s, cursor) for s, _ in self.specials]
            positions = [p for p in positions if p >= 0]
            end = min(positions) if positions else len(text)
            segment = text[cursor:end]
            for match in PRE.finditer(segment):
                symbols = list("".join(self.b2u[b] for b in match.group(0).encode("utf-8")))
                while len(symbols) > 1:
                    best_i = -1
                    best_rank = 1 << 60
                    for i in range(len(symbols) - 1):
                        rank = self.ranks.get((symbols[i], symbols[i + 1]))
                        if rank is not None and rank < best_rank:
                            best_i, best_rank = i, rank
                    if best_i < 0:
                        break
                    symbols[best_i] += symbols[best_i + 1]
                    del symbols[best_i + 1]
                for symbol in symbols:
                    token_id = self.token_to_id.get(symbol)
                    if token_id is None:
                        raise R39InferenceError("R39_BPE_TOKEN_MISSING", f"BPE symbol is absent from vocabulary: {symbol!r}")
                    out.append(token_id)
            cursor = end
        if self.add_bos and self.bos is not None and (not out or out[0] != int(self.bos)):
            out.insert(0, int(self.bos))
        if self.add_eos and self.eos is not None and (not out or out[-1] != int(self.eos)):
            out.append(int(self.eos))
        return out

    def token_bytes(self, token_id: int) -> bytes | None:
        if not 0 <= token_id < len(self.tokens):
            raise R39InferenceError("R39_TOKEN_ID_OUT_OF_RANGE", f"Token {token_id} is outside vocabulary.")
        token = self.tokens[token_id]
        if token.startswith("<|") and token.endswith("|>"):
            return None
        try:
            return bytes(self.u2b[ch] for ch in token)
        except KeyError as exc:
            raise R39InferenceError("R39_BPE_DECODE_SYMBOL_INVALID", f"Token {token_id} contains a non-byte-codec symbol.") from exc


class IncrementalDecoder:
    def __init__(self, tokenizer: BpeTokenizer) -> None:
        self.tokenizer = tokenizer
        self.decoder = codecs.getincrementaldecoder("utf-8")("strict")

    def push(self, token_id: int) -> str:
        raw = self.tokenizer.token_bytes(token_id)
        if raw is None:
            return ""
        try:
            return self.decoder.decode(raw, final=False)
        except UnicodeDecodeError as exc:
            raise R39InferenceError("R39_STREAM_UTF8_INVALID", f"Generated token {token_id} produced invalid UTF-8.") from exc

    def finish(self) -> str:
        try:
            return self.decoder.decode(b"", final=True)
        except UnicodeDecodeError as exc:
            raise R39InferenceError("R39_STREAM_UTF8_TRUNCATED", "Generated token stream ended inside a UTF-8 sequence.") from exc


def _q4_scale_min(sc: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    nb = sc.shape[0]
    scale = np.empty((nb, 8), np.int16)
    minimum = np.empty((nb, 8), np.int16)
    scale[:, :4] = sc[:, :4] & 63
    minimum[:, :4] = sc[:, 4:8] & 63
    for j in range(4, 8):
        scale[:, j] = (sc[:, j + 4] & 15) | ((sc[:, j - 4] >> 6) << 4)
        minimum[:, j] = (sc[:, j + 4] >> 4) | ((sc[:, j] >> 6) << 4)
    return scale, minimum


def _deq_q4k(raw: np.ndarray, cols: int, rows: int) -> np.ndarray:
    blocks = raw.reshape(rows * (cols // 256), 144)
    d = blocks[:, 0:2].copy().view("<f2").reshape(-1).astype(np.float32)
    dm = blocks[:, 2:4].copy().view("<f2").reshape(-1).astype(np.float32)
    sc = blocks[:, 4:16]
    qs = blocks[:, 16:]
    scale, minimum = _q4_scale_min(sc)
    out = np.empty((blocks.shape[0], 256), np.float32)
    for g in range(4):
        q = qs[:, g * 32:(g + 1) * 32]
        out[:, g * 64:g * 64 + 32] = (d * scale[:, 2 * g])[:, None] * (q & 15) - (dm * minimum[:, 2 * g])[:, None]
        out[:, g * 64 + 32:g * 64 + 64] = (d * scale[:, 2 * g + 1])[:, None] * (q >> 4) - (dm * minimum[:, 2 * g + 1])[:, None]
    return out.reshape(rows, cols)


def _deq_q6k(raw: np.ndarray, cols: int, rows: int) -> np.ndarray:
    blocks = raw.reshape(rows * (cols // 256), 210)
    ql = blocks[:, :128]
    qh = blocks[:, 128:192]
    sc = blocks[:, 192:208].view(np.int8).astype(np.int16)
    d = blocks[:, 208:210].copy().view("<f2").reshape(-1).astype(np.float32)
    out = np.empty((blocks.shape[0], 256), np.float32)
    ix = np.arange(32) // 16
    for half in range(2):
        lo0 = ql[:, half * 64:half * 64 + 32]
        lo1 = ql[:, half * 64 + 32:half * 64 + 64]
        hi = qh[:, half * 32:(half + 1) * 32]
        s = half * 8
        o = half * 128
        q1 = ((lo0 & 15) | (((hi >> 0) & 3) << 4)).astype(np.int16) - 32
        q2 = ((lo1 & 15) | (((hi >> 2) & 3) << 4)).astype(np.int16) - 32
        q3 = (((lo0 >> 4) & 15) | (((hi >> 4) & 3) << 4)).astype(np.int16) - 32
        q4 = (((lo1 >> 4) & 15) | (((hi >> 6) & 3) << 4)).astype(np.int16) - 32
        out[:, o:o + 32] = d[:, None] * sc[:, s + ix] * q1
        out[:, o + 32:o + 64] = d[:, None] * sc[:, s + 2 + ix] * q2
        out[:, o + 64:o + 96] = d[:, None] * sc[:, s + 4 + ix] * q3
        out[:, o + 96:o + 128] = d[:, None] * sc[:, s + 6 + ix] * q4
    return out.reshape(rows, cols)


def _deq_q40(raw: np.ndarray, cols: int, rows: int) -> np.ndarray:
    blocks = raw.reshape(rows * (cols // 32), 18)
    d = blocks[:, :2].copy().view("<f2").reshape(-1).astype(np.float32)
    q = blocks[:, 2:18]
    out = np.empty((blocks.shape[0], 32), np.float32)
    out[:, :16] = d[:, None] * ((q & 15).astype(np.int16) - 8)
    out[:, 16:] = d[:, None] * ((q >> 4).astype(np.int16) - 8)
    return out.reshape(rows, cols)


def _deq_q80(raw: np.ndarray, cols: int, rows: int) -> np.ndarray:
    blocks = raw.reshape(rows * (cols // 32), 34)
    d = blocks[:, :2].copy().view("<f2").reshape(-1).astype(np.float32)
    q = blocks[:, 2:34].view(np.int8).astype(np.float32)
    return (d[:, None] * q).reshape(rows, cols)


def _deq(kind: str, raw: np.ndarray, shape: tuple[int, ...]) -> np.ndarray:
    cols = int(shape[0])
    rows = int(shape[1]) if len(shape) > 1 else 1
    if kind == "f32":
        return raw.copy().view("<f4").reshape(rows, cols)
    if kind == "f16":
        return raw.copy().view("<f2").astype(np.float32).reshape(rows, cols)
    if kind == "bf16":
        u = raw.copy().view("<u2").astype(np.uint32) << 16
        return u.view(np.float32).reshape(rows, cols)
    if kind == "q4_0":
        return _deq_q40(raw, cols, rows)
    if kind == "q8_0":
        return _deq_q80(raw, cols, rows)
    if kind == "q4_k":
        return _deq_q4k(raw, cols, rows)
    if kind == "q6_k":
        return _deq_q6k(raw, cols, rows)
    raise R39InferenceError("R39_QUANTIZER_UNSUPPORTED", f"Tensor quantizer {kind} is unsupported.")


class R39Model:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.file = path.open("rb")
        self.mm = mmap.mmap(self.file.fileno(), 0, access=mmap.ACCESS_READ)
        self.header, self.toc = self._read_header_toc()
        by_type: dict[int, list[TocEntry]] = {}
        for entry in self.toc:
            by_type.setdefault(entry.section_type, []).append(entry)
        try:
            manifest_entry = self._one(by_type, SEC_MANIFEST)
            arch_entry = self._one(by_type, SEC_ARCH)
            tokenizer_entry = self._one(by_type, SEC_TOKENIZER)
            tensor_dir_entry = self._one(by_type, SEC_TENSOR_DIR)
        except Exception:
            self.close()
            raise
        self.manifest = _json_section(self.mm, manifest_entry)
        self.graph = _json_section(self.mm, arch_entry)
        self.tokenizer_spec = _json_section(self.mm, tokenizer_entry)
        self.tensor_directory = _json_section(self.mm, tensor_dir_entry)
        self.generation = _json_section(self.mm, self._one(by_type, SEC_GENERATION)) if SEC_GENERATION in by_type else {}
        self.data_sections = {e.section_id: e for e in self.toc if e.section_type == SEC_TENSOR_DATA}
        self.desc: dict[str, dict[str, Any]] = {}
        self.desc_by_id: dict[str, dict[str, Any]] = {}
        for raw in self.tensor_directory.get("tensors", []):
            if not isinstance(raw, dict):
                continue
            name = str(raw.get("name", ""))
            tensor_id = str(raw.get("tensorId", ""))
            sid = int(raw.get("dataSectionId", 5))
            off = int(raw.get("dataOffsetBytes", -1))
            length = int(raw.get("storedLengthBytes", 0))
            section = self.data_sections.get(sid)
            if not name or not tensor_id or section is None or off < 0 or length <= 0 or off + length > section.stored_length:
                raise R39InferenceError("R39_TENSOR_DESCRIPTOR_INVALID", f"Tensor descriptor cannot be mapped safely: {name or tensor_id or '<unnamed>'}")
            d = {**raw, "shape": tuple(int(x) for x in raw.get("shape", [])), "kind": str(raw.get("quantization") or raw.get("dataType") or "").lower(), "section": section}
            self.desc[name] = d
            self.desc_by_id[tensor_id] = d
        self.tokenizer = BpeTokenizer(self.tokenizer_spec)
        self._validate_reference_profile()

    @staticmethod
    def _one(by_type: dict[int, list[TocEntry]], section_type: int) -> TocEntry:
        entries = by_type.get(section_type, [])
        if len(entries) != 1:
            raise R39InferenceError("R39_ACTIVE_SECTION_AMBIGUOUS", f"Expected one active TOC section of type {section_type}; found {len(entries)}.")
        return entries[0]

    def _read_header_toc(self) -> tuple[dict[str, Any], list[TocEntry]]:
        head = self.mm[:HEADER_BYTES]
        if len(head) != HEADER_BYTES or head[:8] != MAGIC:
            raise R39InferenceError("R39_HEADER_INVALID", "Canonical SWRLZX header is absent.")
        major, minor, hbytes, flags, endian, file_bytes, toc_offset, toc_count, toc_entry_bytes, manifest_id, tensor_dir_id, lineage_id, integrity_id = struct.unpack_from("<HHIIIQQIIIIII", head, 8)
        if major != 1 or hbytes != HEADER_BYTES or endian != ENDIAN_MARKER or toc_entry_bytes != TOC_ENTRY_BYTES or file_bytes != len(self.mm):
            raise R39InferenceError("R39_HEADER_CONTRACT_INVALID", "SWRLZX header fields fail v1 contract.")
        if toc_offset != HEADER_BYTES or toc_count <= 0 or toc_count > 4096:
            raise R39InferenceError("R39_TOC_RANGE_INVALID", "SWRLZX TOC location/count is invalid.")
        entries: list[TocEntry] = []
        for i in range(toc_count):
            pos = toc_offset + i * TOC_ENTRY_BYTES
            b = self.mm[pos:pos + TOC_ENTRY_BYTES]
            if len(b) != TOC_ENTRY_BYTES:
                raise R39InferenceError("R39_TOC_EOF", "SWRLZX TOC is truncated.")
            sid, stype, sflags, align, off, stored, logical, codec, schema = struct.unpack_from("<IIIIQQQII", b, 0)
            if align < 64 or align & (align - 1) or off % align or off < HEADER_BYTES + toc_count * TOC_ENTRY_BYTES or off + stored > len(self.mm):
                raise R39InferenceError("R39_SECTION_RANGE_INVALID", f"SWRLZX section {sid} has invalid physical bounds/alignment.")
            entries.append(TocEntry(sid, stype, sflags, align, off, stored, logical, codec, schema, b[48:80].hex()))
        return ({"major": major, "minor": minor, "flags": flags, "fileBytes": file_bytes, "tocCount": toc_count, "manifestSectionId": manifest_id, "tensorDirectorySectionId": tensor_dir_id, "lineageSectionId": lineage_id, "integritySectionId": integrity_id, "rootDigestSha256": head[64:96].hex()}, entries)

    def _validate_reference_profile(self) -> None:
        required = {"token_embd.weight", "token_embd_norm.weight"}
        for i, kv in enumerate(LAYER_KV):
            required.update({f"blk.{i}.attn_norm.weight", f"blk.{i}.ffn_norm.weight", f"blk.{i}.ffn_gate.weight", f"blk.{i}.ffn_up.weight", f"blk.{i}.ffn_down.weight"})
            if kv == 0:
                required.update({f"blk.{i}.shortconv.in_proj.weight", f"blk.{i}.shortconv.conv.weight", f"blk.{i}.shortconv.out_proj.weight"})
            else:
                required.update({f"blk.{i}.attn_q.weight", f"blk.{i}.attn_k.weight", f"blk.{i}.attn_v.weight", f"blk.{i}.attn_output.weight", f"blk.{i}.attn_q_norm.weight", f"blk.{i}.attn_k_norm.weight"})
        missing = sorted(required - self.desc.keys())
        if missing:
            raise R39InferenceError("R39_REFERENCE_TENSORS_MISSING", "Reference LFM2 tensor set is incomplete: " + ", ".join(missing[:8]))
        emb = self.desc["token_embd.weight"]["shape"]
        if len(emb) != 2 or emb[0] != 1024 or emb[1] != len(self.tokenizer.tokens):
            raise R39InferenceError("R39_REFERENCE_PROFILE_MISMATCH", f"Expected token_embd shape [1024,{len(self.tokenizer.tokens)}], got {emb}.")
        nodes = self.graph.get("nodes", [])
        if not isinstance(nodes, list) or len(nodes) < 99:
            raise R39InferenceError("R39_GRAPH_PROFILE_UNSUPPORTED", f"Architecture graph has {len(nodes) if isinstance(nodes, list) else 'invalid'} nodes; canonical LFM2 graph is not present.")

    def _raw(self, name: str) -> np.ndarray:
        d = self.desc[name]
        sec: TocEntry = d["section"]
        off = sec.offset + int(d["dataOffsetBytes"])
        length = int(d["storedLengthBytes"])
        return np.frombuffer(self.mm, dtype=np.uint8, count=length, offset=off)

    @staticmethod
    def _row_bytes(kind: str, cols: int) -> int:
        if kind == "f32": return cols * 4
        if kind in {"f16", "bf16"}: return cols * 2
        if kind == "q4_0":
            if cols % 32: raise R39InferenceError("R39_Q4_0_BLOCK_MISMATCH", str(cols))
            return (cols // 32) * 18
        if kind == "q8_0":
            if cols % 32: raise R39InferenceError("R39_Q8_0_BLOCK_MISMATCH", str(cols))
            return (cols // 32) * 34
        if kind == "q4_k":
            if cols % 256: raise R39InferenceError("R39_Q4K_BLOCK_MISMATCH", str(cols))
            return (cols // 256) * 144
        if kind == "q6_k":
            if cols % 256: raise R39InferenceError("R39_Q6K_BLOCK_MISMATCH", str(cols))
            return (cols // 256) * 210
        raise R39InferenceError("R39_QUANTIZER_UNSUPPORTED", kind)

    def matrix(self, name: str) -> np.ndarray:
        d = self.desc[name]
        return _deq(d["kind"], self._raw(name), d["shape"])

    def row(self, name: str, row: int) -> np.ndarray:
        d = self.desc[name]
        cols = int(d["shape"][0])
        rows = int(d["shape"][1]) if len(d["shape"]) > 1 else 1
        if not 0 <= row < rows:
            raise R39InferenceError("R39_TENSOR_ROW_OUT_OF_RANGE", f"{name}:{row}/{rows}")
        rb = self._row_bytes(d["kind"], cols)
        raw = self._raw(name)[row * rb:(row + 1) * rb]
        return _deq(d["kind"], raw, (cols, 1)).reshape(-1)

    def vector(self, name: str) -> np.ndarray:
        return self.matrix(name).reshape(-1)

    def matvec(self, name: str, x: np.ndarray) -> np.ndarray:
        d = self.desc[name]
        shape = d["shape"]
        cols = int(shape[0])
        rows = int(shape[1]) if len(shape) > 1 else 1
        if x.size != cols:
            raise R39InferenceError("R39_MATVEC_SHAPE_MISMATCH", f"{name}: expected {cols}, got {x.size}")
        rb = self._row_bytes(d["kind"], cols)
        raw = self._raw(name)
        batch_rows = max(1, min(rows, max(64, (4 * 1024 * 1024) // max(4 * cols, 1))))
        out = np.empty(rows, dtype=np.float32)
        for start in range(0, rows, batch_rows):
            count = min(batch_rows, rows - start)
            block = raw[start * rb:(start + count) * rb]
            matrix = _deq(d["kind"], block, (cols, count))
            out[start:start + count] = matrix @ x
        return out

    def close(self) -> None:
        try: self.mm.close()
        except Exception: pass
        try: self.file.close()
        except Exception: pass


class RecurrentState:
    def __init__(self) -> None:
        self.conv = {i: np.zeros((2, 1024), np.float32) for i, kv in enumerate(LAYER_KV) if kv == 0}
        self.kv: dict[int, list[tuple[np.ndarray, np.ndarray]]] = {i: [] for i, kv in enumerate(LAYER_KV) if kv}
        self.pos = 0


def _rms(x: np.ndarray, w: np.ndarray, eps: float = 1e-5) -> np.ndarray:
    return (x / np.sqrt(np.mean(x * x, dtype=np.float32) + np.float32(eps), dtype=np.float32) * w).astype(np.float32)


def _silu(x: np.ndarray) -> np.ndarray:
    return (x / (1 + np.exp(-x, dtype=np.float32))).astype(np.float32)


def _rope(x: np.ndarray, heads: int, hd: int, pos: int, theta: float = 1_000_000.0) -> np.ndarray:
    y = x.reshape(heads, hd).copy()
    half = hd // 2
    inv = 1.0 / (theta ** (np.arange(half, dtype=np.float64) * 2.0 / hd))
    angle = pos * inv
    c = np.cos(angle).astype(np.float32)
    s = np.sin(angle).astype(np.float32)
    a = y[:, :half].copy()
    b = y[:, half:].copy()
    y[:, :half] = a * c - b * s
    y[:, half:] = b * c + a * s
    return y.reshape(-1)


def _forward(model: R39Model, token: int, state: RecurrentState) -> np.ndarray:
    x = model.row("token_embd.weight", token).astype(np.float32)
    for i, kvh in enumerate(LAYER_KV):
        n = _rms(x, model.vector(f"blk.{i}.attn_norm.weight"))
        if kvh == 0:
            projected = model.matvec(f"blk.{i}.shortconv.in_proj.weight", n)
            b, c, z = np.split(projected, 3)
            bx = (b * z).astype(np.float32)
            cw = model.matrix(f"blk.{i}.shortconv.conv.weight")
            hist = state.conv[i]
            cv = (hist[0] * cw[:, 0] + hist[1] * cw[:, 1] + bx * cw[:, 2]).astype(np.float32)
            state.conv[i][0] = hist[1].copy()
            state.conv[i][1] = bx
            op = model.matvec(f"blk.{i}.shortconv.out_proj.weight", (c * cv).astype(np.float32))
        else:
            q = model.matvec(f"blk.{i}.attn_q.weight", n)
            k = model.matvec(f"blk.{i}.attn_k.weight", n)
            v = model.matvec(f"blk.{i}.attn_v.weight", n)
            qn = model.vector(f"blk.{i}.attn_q_norm.weight")
            kn = model.vector(f"blk.{i}.attn_k_norm.weight")
            q = np.concatenate([_rms(q.reshape(16, 64)[h], qn) for h in range(16)]).astype(np.float32)
            k = np.concatenate([_rms(k.reshape(8, 64)[h], kn) for h in range(8)]).astype(np.float32)
            q = _rope(q, 16, 64, state.pos)
            k = _rope(k, 8, 64, state.pos)
            state.kv[i].append((k.copy(), v.copy()))
            att = np.zeros((16, 64), np.float32)
            for h in range(16):
                kh = h // 2
                qh = q.reshape(16, 64)[h]
                scores = np.array([np.dot(qh, kk.reshape(8, 64)[kh]) / 8.0 for kk, _ in state.kv[i]], np.float32)
                weights = np.exp(scores - scores.max(), dtype=np.float32)
                weights /= weights.sum(dtype=np.float32)
                for weight, (_, vv) in zip(weights, state.kv[i]):
                    att[h] += weight * vv.reshape(8, 64)[kh]
            op = model.matvec(f"blk.{i}.attn_output.weight", att.reshape(-1))
        residual = (x + op).astype(np.float32)
        fn = _rms(residual, model.vector(f"blk.{i}.ffn_norm.weight"))
        gate = model.matvec(f"blk.{i}.ffn_gate.weight", fn)
        up = model.matvec(f"blk.{i}.ffn_up.weight", fn)
        ff = model.matvec(f"blk.{i}.ffn_down.weight", (_silu(gate) * up).astype(np.float32))
        x = (residual + ff).astype(np.float32)
    x = _rms(x, model.vector("token_embd_norm.weight"))
    logits = model.matvec("token_embd.weight", x)
    state.pos += 1
    return logits


def _sample(logits: np.ndarray, history: list[int], temperature: float, top_p: float, top_k: int, repetition_penalty: float, seed: int) -> int:
    adjusted = logits.copy()
    for token in set(history):
        if 0 <= token < adjusted.size:
            adjusted[token] = adjusted[token] * repetition_penalty if adjusted[token] < 0 else adjusted[token] / repetition_penalty
    k = min(max(1, top_k), adjusted.size)
    candidate_idx = np.argpartition(adjusted, -k)[-k:]
    candidate_idx = candidate_idx[np.argsort(adjusted[candidate_idx])[::-1]]
    if temperature <= 0 or len(candidate_idx) == 1:
        return int(candidate_idx[0])
    values = adjusted[candidate_idx]
    weights = np.exp((values - values[0]) / np.float32(temperature), dtype=np.float64)
    probs = weights / max(weights.sum(), 1e-300)
    cumulative = np.cumsum(probs)
    nucleus = max(1, int(np.searchsorted(cumulative, top_p, side="left")) + 1)
    rng = np.random.default_rng(seed & 0xFFFFFFFF)
    pick = rng.random() * weights[:nucleus].sum()
    running = 0.0
    for i in range(nucleus):
        running += float(weights[i])
        if pick <= running:
            return int(candidate_idx[i])
    return int(candidate_idx[nucleus - 1])


def render_chat_prompt(payload: dict[str, Any]) -> str:
    parts = ["<|startoftext|>"]
    directive = str(payload.get("responseDirective") or "You are §wyrlz. Answer directly and truthfully.").strip()
    parts.append(f"<|im_start|>system\n{directive}<|im_end|>\n")
    for turn in payload.get("history", []):
        if not isinstance(turn, dict):
            continue
        role = str(turn.get("role", "USER")).upper()
        mapped = "assistant" if role in {"ASSISTANT", "AI", "SWRLZ", "SELF"} else "system" if role == "SYSTEM" else "user"
        text = str(turn.get("text", "")).strip()
        if text:
            parts.append(f"<|im_start|>{mapped}\n{text}<|im_end|>\n")
    parts.append(f"<|im_start|>user\n{str(payload.get('prompt', '')).strip()}<|im_end|>\n<|im_start|>assistant\n")
    return "".join(parts)


def inspect_engine(path: Path = RAW) -> dict[str, Any]:
    ensure = ensure_r39()
    if not ensure.get("modelReady") or not path.is_file():
        return {"ok": False, "oneTokenReady": False, "interactiveReady": False, "code": ensure.get("code", "R39_NOT_READY"), "detail": ensure.get("detail", "R39 is not ready.")}
    model: R39Model | None = None
    try:
        model = R39Model(path)
        return {"ok": True, "oneTokenReady": True, "interactiveReady": True, "engineId": ENGINE_ID, "modelId": model.manifest.get("modelId", "R39"), "modelSha256": MODEL_SHA256, "tocCount": model.header["tocCount"], "tensorCount": len(model.desc), "tokenCount": len(model.tokenizer.tokens), "graphNodeCount": len(model.graph.get("nodes", [])), "sectionPayloadLocationsReconstructed": True, "note": "Readiness means the exact reference LFM2 tensor/tokenizer execution path is structurally available; live latency is measured only during generation."}
    except R39InferenceError as exc:
        return {"ok": False, "oneTokenReady": False, "interactiveReady": False, "code": exc.code, "detail": exc.detail}
    finally:
        if model is not None:
            model.close()


def generate_events(payload: dict[str, Any], is_cancelled: Callable[[], bool] | None = None) -> Iterator[dict[str, Any]]:
    request_id = str(payload["requestId"])
    started = time.monotonic()
    model: R39Model | None = None
    yield {"type": "STATUS", "phase": "MODEL_LOADING", "reason": "Reconstructing/verifying R39 and opening the canonical SWRLZX tensor view."}
    try:
        load = ensure_r39()
        if not load.get("modelReady"):
            raise R39InferenceError(str(load.get("code", "R39_LOAD_FAILED")), str(load.get("detail", "R39 reconstruction failed.")))
        model = R39Model(RAW)
        yield {"type": "ROUTE", "phase": "ROUTE_RESOLVED", "reason": "Using local R39 Python reference inference.", "identity": {"route": "LOCAL_R39", "engineId": ENGINE_ID, "modelId": str(model.manifest.get("modelId") or "R39"), "modelSha256": MODEL_SHA256}}
        prompt = render_chat_prompt(payload)
        tokens = model.tokenizer.encode(prompt)
        if len(tokens) > 32768:
            tokens = tokens[-32768:]
        if not tokens:
            raise R39InferenceError("R39_PROMPT_TOKENIZATION_EMPTY", "Prompt produced no model tokens.")
        generation = payload.get("generation") if isinstance(payload.get("generation"), dict) else {}
        max_tokens = min(512, max(1, int(generation.get("maxTokens", 128))))
        temperature = min(2.0, max(0.0, float(generation.get("temperature", 0.1))))
        top_p = min(1.0, max(0.01, float(generation.get("topP", 0.9))))
        state = RecurrentState()
        yield {"type": "STATUS", "phase": "PREFILL", "reason": f"Prefilling {len(tokens)} token(s) into local R39 recurrent state."}
        logits: np.ndarray | None = None
        for ordinal, token in enumerate(tokens):
            if is_cancelled and is_cancelled():
                raise R39InferenceError("REQUEST_CANCELLED", "Generation was cancelled.")
            logits = _forward(model, token, state)
            if ordinal and ordinal % 16 == 0:
                yield {"type": "STATUS", "phase": "PREFILL", "reason": f"Prefill {ordinal}/{len(tokens)}."}
        assert logits is not None
        decoder = IncrementalDecoder(model.tokenizer)
        recent: list[int] = []
        first_ms: int | None = None
        yield {"type": "STATUS", "phase": "GENERATING", "reason": "R39 prefill complete; decoding locally."}
        for _ in range(max_tokens):
            if is_cancelled and is_cancelled():
                raise R39InferenceError("REQUEST_CANCELLED", "Generation was cancelled.")
            next_token = _sample(logits, recent[-64:], temperature, top_p, 50, 1.05, hash(request_id) ^ (state.pos * 0x9E3779B9))
            if model.tokenizer.eos is not None and next_token == int(model.tokenizer.eos):
                break
            text = decoder.push(next_token)
            if first_ms is None:
                first_ms = int((time.monotonic() - started) * 1000)
            if text:
                yield {"type": "DELTA", "phase": "GENERATING", "text": text, "firstDeltaLatencyMs": first_ms}
            recent.append(next_token)
            logits = _forward(model, next_token, state)
        tail = decoder.finish()
        if tail:
            yield {"type": "DELTA", "phase": "GENERATING", "text": tail, "firstDeltaLatencyMs": first_ms}
        yield {"type": "COMPLETED", "phase": "COMPLETE", "reason": "Local R39 generation completed.", "totalLatencyMs": int((time.monotonic() - started) * 1000)}
    except R39InferenceError as exc:
        if exc.code == "REQUEST_CANCELLED":
            yield {"type": "CANCELLED", "phase": "CANCELLED", "reason": exc.detail, "categories": [exc.code], "totalLatencyMs": int((time.monotonic() - started) * 1000)}
        else:
            yield {"type": "FAILED", "phase": "ERROR", "reason": exc.detail, "categories": [exc.code], "totalLatencyMs": int((time.monotonic() - started) * 1000)}
    except Exception as exc:
        yield {"type": "FAILED", "phase": "ERROR", "reason": f"Local R39 inference failed ({type(exc).__name__}).", "categories": ["R39_INFERENCE_RUNTIME_FAILED"], "totalLatencyMs": int((time.monotonic() - started) * 1000)}
    finally:
        if model is not None:
            model.close()
