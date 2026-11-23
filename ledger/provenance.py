"""Freeze raw source bytes with provenance, and read them back.

A snapshot is immutable once written. `verify` only ever reads it; `freeze` only
ever creates a new one. Nothing in this module rewrites an existing snapshot.
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

FETCHER = "climate-ledger/0.1.0"
USER_AGENT = FETCHER + " (+https://github.com/realtimshady16/climate-ledger)"


def sha256_bytes(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def _snapshot_id() -> str:
    # Timestamp for humans, short suffix so two freezes in the same second never
    # collide and never overwrite an existing snapshot.
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{uuid4().hex[:4]}"


def _stem(url: str) -> str:
    tail = url.split("?", 1)[0].rsplit("/", 1)[-1]
    return tail if "." in tail else "source.bin"


def freeze_claim(root: Path, claim: dict) -> Path:
    """Copy or fetch one source into a new immutable snapshot directory."""
    snapshot_id = _snapshot_id()
    snapshot = root / "data" / claim["id"] / snapshot_id
    raw = snapshot / "raw"
    raw.mkdir(parents=True, exist_ok=False)

    source = claim["source"]
    if "url" in source:
        request = urllib.request.Request(
            source["url"], headers={"User-Agent": USER_AGENT}
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read()
            status = response.status
        filename = source.get("filename") or _stem(source["url"])
        origin, kind = source["url"], "url"
    else:
        path = root / source["path"]
        body = path.read_bytes()
        status = None
        filename = source.get("filename") or path.name
        origin, kind = source["path"], "file"

    (raw / filename).write_bytes(body)
    (raw / "SHA256SUMS").write_text(f"{sha256_bytes(body)}  {filename}\n")

    provenance = {
        "claim_id": claim["id"],
        "snapshot_id": snapshot_id,
        "origin": origin,
        "kind": kind,
        "http_status": status,
        "bytes": len(body),
        "sha256": sha256_bytes(body),
        "filename": filename,
        "source_version": source.get("version"),
        "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fetched_by": FETCHER,
    }
    (snapshot / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n"
    )
    (root / "data" / claim["id"] / "LATEST").write_text(snapshot_id + "\n")
    return snapshot


def latest_snapshot(root: Path, claim_id: str) -> Path | None:
    pointer = root / "data" / claim_id / "LATEST"
    if not pointer.exists():
        return None
    snapshot = root / "data" / claim_id / pointer.read_text().strip()
    return snapshot if snapshot.is_dir() else None
