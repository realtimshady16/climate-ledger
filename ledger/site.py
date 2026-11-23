"""One static page, generated from the ledger. No framework, no build step.

The page is deliberately plain: system fonts, no fixed background, no viewport
units, so it renders both as a standalone site and inside a host that supplies
its own chrome.
"""

from __future__ import annotations

import html

REPO = "https://github.com/realtimshady16/climate-ledger"

VERDICT_LABEL = {
    "confirmed": "confirmed",
    "transcribed": "transcribed",
    "drifted": "drifted",
    "error": "error",
    "missing-snapshot": "no snapshot",
}


def _fmt(value: object, unit: str | None) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, float):
        text = f"{value:,.3f}".rstrip("0").rstrip(".")
    else:
        text = str(value)
    return f"{text} {unit}" if unit else text


def render(payload: dict, repo: str = REPO) -> str:
    summary = payload["summary"]
    rows = []
    for claim in payload["claims"]:
        cid = html.escape(claim["id"])
        verdict = claim["verdict"]
        label = VERDICT_LABEL.get(verdict, verdict)
        rows.append(
            f"""      <tr class="v-{html.escape(verdict)}">
        <td><a href="{repo}/blob/main/claims/{cid}/README.md"><code>{cid}</code></a>
          <div class="q">{html.escape(claim["question"])}</div></td>
        <td class="num">{claim["tier"]}</td>
        <td class="num">{_fmt(claim.get("published"), claim.get("unit"))}</td>
        <td class="num">{_fmt(claim.get("value"), claim.get("unit"))}</td>
        <td class="num">{_fmt(claim.get("delta"), None)}</td>
        <td><span class="badge">{html.escape(label)}</span></td>
        <td class="num">{claim["checked_at"][:10]}</td>
      </tr>"""
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Climate ledger — {summary["confirmed"]} confirmed of {summary["total"]}</title>
<style>
  :root {{
    color-scheme: light dark;
    --fg: #16181d; --muted: #5c6270; --line: #d8dbe2;
    --ok: #1a7f4b; --warn: #8a5a00; --bad: #a4272d; --chip: #eef0f4;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --fg: #e8eaee; --muted: #9aa2b1; --line: #333844;
             --ok: #4ec98a; --warn: #e0b154; --bad: #ff8a8a; --chip: #1e222b; }}
  }}
  body {{ margin: 0; padding: 24px 16px 48px; color: var(--fg);
          font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }}
  main {{ max-width: 900px; margin: 0 auto; }}
  h1 {{ font-size: 1.7rem; margin: 0 0 4px; letter-spacing: -0.01em; }}
  p.sub {{ margin: 0 0 18px; color: var(--muted); }}
  .tally {{ display: flex; gap: 18px; flex-wrap: wrap; margin: 0 0 22px;
            font-variant-numeric: tabular-nums; }}
  .tally b {{ font-size: 1.35rem; display: block; }}
  table {{ width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }}
  th, td {{ text-align: left; padding: 9px 8px; border-bottom: 1px solid var(--line);
            vertical-align: top; }}
  th {{ font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em;
        color: var(--muted); font-weight: 600; }}
  td.num, th.num {{ text-align: right; white-space: nowrap; }}
  .q {{ color: var(--muted); font-size: 0.85rem; margin-top: 2px; }}
  .badge {{ display: inline-block; padding: 1px 8px; border-radius: 999px;
            background: var(--chip); font-size: 0.8rem; white-space: nowrap; }}
  .v-confirmed .badge {{ color: var(--ok); }}
  .v-drifted .badge, .v-error .badge, .v-missing-snapshot .badge {{ color: var(--bad); }}
  .v-transcribed .badge {{ color: var(--warn); }}
  footer {{ margin-top: 26px; color: var(--muted); font-size: 0.85rem; }}
  code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.9em; }}
  a {{ color: inherit; }}
</style>
</head>
<body>
<main>
  <h1>Climate ledger</h1>
  <p class="sub">The climate numbers the news quotes, recomputed from pinned source
  bytes. Generated {html.escape(payload["generated_at"])}.</p>

  <div class="tally">
    <div><b>{summary["confirmed"]}</b>confirmed</div>
    <div><b>{summary["transcribed"]}</b>transcribed</div>
    <div><b>{summary["drifted"]}</b>drifted</div>
    <div><b>{summary["failed"]}</b>failed</div>
    <div><b>{summary["total"]}</b>claims</div>
  </div>

  <table>
    <thead>
      <tr><th>Claim</th><th class="num">Tier</th><th class="num">Published</th>
      <th class="num">Recomputed</th><th class="num">Δ</th><th>Verdict</th>
      <th class="num">Checked</th></tr>
    </thead>
    <tbody>
{chr(10).join(rows)}
    </tbody>
  </table>

  <footer>
    <p><b>Method.</b> <code>make freeze</code> fetched each source once and pinned the
    bytes with a SHA-256; <code>make verify</code> recomputed every value offline from
    those bytes and exits non-zero if one moves outside its stated tolerance.
    Tier A is computed; Tier B is transcribed from a document with a page reference.
    The difference is shown, not hidden.</p>
    <p>Code MIT, prose and derived data CC BY 4.0. Upstream sources keep their own
    terms — see <a href="{repo}/blob/main/NOTICE.md">NOTICE.md</a>.
    Source and method for each entry: <a href="{repo}">{repo.replace("https://", "")}</a>.</p>
  </footer>
</main>
</body>
</html>
"""
