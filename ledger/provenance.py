"""Freeze raw source bytes with provenance, and read them back.

A snapshot is immutable once written. `verify` only ever reads it; `freeze` only
ever creates a new one. Nothing in this module rewrites an existing snapshot.

Datasets, not claims, are frozen: two claims that read the same source must never
end up on two different vintages of it.
"""

from __future__ import annotations

import hashlib
import http.cookiejar
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

FETCHER = "climate-ledger/0.3.0"
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


def _download(url: str, licence_url: str | None) -> tuple[bytes, int]:
    """Fetch a URL, optionally accepting a portal licence first.

    Some data portals (ICOS among them) answer a bare GET with an HTML licence
    page; the licence_accept link sets a cookie that unlocks the object URL.
    """
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    headers = {"User-Agent": USER_AGENT}
    if licence_url:
        opener.open(urllib.request.Request(licence_url, headers=headers), timeout=60).read()
    with opener.open(urllib.request.Request(url, headers=headers), timeout=120) as response:
        return response.read(), response.status


def freeze_dataset(root: Path, dataset: dict) -> Path:
    """Copy or fetch one source into a new immutable snapshot directory."""
    snapshot_id = _snapshot_id()
    snapshot = root / "data" / dataset["id"] / snapshot_id
    raw = snapshot / "raw"
    raw.mkdir(parents=True, exist_ok=False)

    source = dataset["source"]
    if "url" in source:
        body, status = _download(source["url"], source.get("licence_url"))
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
        "dataset_id": dataset["id"],
        "snapshot_id": snapshot_id,
        "origin": origin,
        "kind": kind,
        "http_status": status,
        "bytes": len(body),
        "sha256": sha256_bytes(body),
        "filename": filename,
        "source_version": dataset.get("version"),
        "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fetched_by": FETCHER,
    }

    if dataset.get("extract") == "xlsx":
        from . import extract

        derived = extract.xlsx_to_csv(raw / filename, snapshot / "derived", dataset["sheets"])
        provenance["derived"] = [path.name for path in derived]

    (snapshot / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n"
    )
    (root / "data" / dataset["id"] / "LATEST").write_text(snapshot_id + "\n")
    return snapshot


def latest_snapshot(root: Path, dataset_id: str) -> Path | None:
    pointer = root / "data" / dataset_id / "LATEST"
    if not pointer.exists():
        return None
    snapshot = root / "data" / dataset_id / pointer.read_text().strip()
    return snapshot if snapshot.is_dir() else None
