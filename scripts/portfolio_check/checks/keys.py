from __future__ import annotations

import base64
import re
import struct
from pathlib import Path

from .. import config
from ..model import FAIL, PASS, Result

PRIVATE_MARKERS = ("-----BEGIN", "PuTTY-User-Key-File")
UNUMBER = re.compile(r"^u\d{6,8}$", re.I)


def parse_public_key(text: str) -> tuple:
    stripped = text.strip()
    if not stripped:
        return False, "file is empty"
    for marker in PRIVATE_MARKERS:
        if marker in stripped:
            if marker == "-----BEGIN":
                return False, ("this is a PRIVATE key — never share it. "
                               "Delete it from the repo, rotate the key, and "
                               "commit the .pub file instead")
            return False, ("this is a PuTTY .ppk file. Export it as OpenSSH "
                           "format ('Conversions -> Export OpenSSH key') and "
                           "commit the public half")
    if len(stripped.splitlines()) > 1:
        return False, "a public key is a single line"

    parts = stripped.split()
    if len(parts) < 2:
        return False, "expected '<type> <base64> [comment]'"
    key_type, blob = parts[0], parts[1]
    if key_type not in config.ALLOWED_KEY_TYPES:
        return False, f"unknown key type {key_type!r}"
    try:
        raw = base64.b64decode(blob, validate=True)
    except Exception:
        return False, "the base64 body is not decodable"

    fields = _unpack(raw)
    if not fields:
        return False, "the key body is malformed"
    if fields[0].decode("ascii", "replace") != key_type:
        return False, "the key type does not match its body (truncated or edited?)"

    if key_type == "ssh-rsa" and len(fields) >= 3:
        bits = (len(fields[2].lstrip(b"\x00"))) * 8
        if bits < config.MIN_RSA_BITS:
            return False, (f"RSA key is only ~{bits} bits; use at least "
                           f"{config.MIN_RSA_BITS}, or better, ed25519")
        return True, f"{key_type}, ~{bits} bits"
    return True, key_type


def _unpack(raw: bytes) -> list:
    out, offset = [], 0
    while offset + 4 <= len(raw):
        (length,) = struct.unpack(">I", raw[offset:offset + 4])
        offset += 4
        if length > len(raw) - offset:
            return []
        out.append(raw[offset:offset + length])
        offset += length
    return out


def check_key(repo: Path, week: int) -> Result:
    keys_dir = repo / config.KEYS_DIR
    found = sorted(keys_dir.glob("*.pub")) if keys_dir.is_dir() else []

    stray = [p.name for p in keys_dir.iterdir()
             if p.is_file() and p.suffix != ".pub"] if keys_dir.is_dir() else []

    if not found:
        detail = "no keys/*.pub found"
        if stray:
            detail += f" (but {keys_dir.name}/ contains {', '.join(stray)})"
        return Result(
            id="ssh_key", title="SSH public key submitted", status=FAIL,
            detail=detail,
            fix="Commit your PUBLIC key as keys/<your-u-number>.pub. That is "
                "the file ending in .pub, never the one without it. Follow "
                "the provided instructions on how to generate.",
        )
    if len(found) > 1:
        return Result(
            id="ssh_key", title="SSH public key submitted", status=FAIL,
            detail=f"{len(found)} key files", evidence=[p.name for p in found],
            fix="Keep exactly one key file, named after your u-number.",
        )

    key_file = found[0]
    stem = key_file.stem
    text = key_file.read_text(encoding="utf-8", errors="replace")
    ok, message = parse_public_key(text)
    if not ok:
        return Result(
            id="ssh_key", title="SSH public key submitted", status=FAIL,
            detail=f"{key_file.name}: {message}",
            fix="Fix the key file and commit again. Your key is submitted to the "
                "GPU servers from this file, so it must be valid before week 2.",
        )
    if not UNUMBER.match(stem):
        return Result(
            id="ssh_key", title="SSH public key submitted", status=FAIL,
            detail=f"{key_file.name} is a valid {message} key, but the filename "
                   "is not a u-number",
            fix="Rename it to keys/<your-u-number>.pub, e.g. keys/u123456.pub, as "
                "we match keys to accounts by filename.",
        )
    return Result(id="ssh_key", title="SSH public key submitted", status=PASS,
                  detail=f"{key_file.name}: {message}")
