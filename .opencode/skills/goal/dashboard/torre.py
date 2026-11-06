#!/usr/bin/env python3
"""Torre de Control de Goal — tablero vivo (stdlib, solo lectura).

Diseño original (Goal Observability) + pestaña Auto-research.
Objetivos: `.opencode/goals/`. Investigaciones: `research/` y mirrors por goal.

Uso:
  python torre.py --serve --port 3010 --project <raiz>
  python torre.py --render --project <raiz>
"""
import argparse
import csv
import html
import io
import json
import os
import re
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
HEAD_RE = re.compile(r"^##\s+(.+)$", re.M)
MONTHS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def read(path, limit=400_000):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read(limit)
    except OSError:
        return ""


def frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    out = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip().lower()] = v.strip().strip('"').strip("'")
    return out, text[end + 4:]


def table_rows(text):
    rows, header = [], None
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(c and set(c) <= set("-: ") for c in cells):
            continue
        if header is None:
            header = [c.lower() for c in cells]
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def sections(body):
    parts = HEAD_RE.split(body)
    return [(parts[i].strip(), parts[i + 1].strip()) for i in range(1, len(parts), 2)]


def block_after(text, title):
    m = re.search(r"^##\s+" + re.escape(title) + r"\s*$", text, re.M | re.I)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = HEAD_RE.search(rest)
    return (rest[:nxt.start()] if nxt else rest).strip()


def num(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def mdate(name, path):
    m = DATE_RE.match(name)
    if m:
        return m.group(1)
    try:
        return datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d")
    except OSError:
        return ""


def nice_date(iso):
    try:
        d = datetime.strptime(iso[:10], "%Y-%m-%d")
        return f"{d.day} {MONTHS[d.month - 1]}"
    except (ValueError, IndexError):
        return iso[:10]


def nice_stamp(ts):
    try:
        d = datetime.fromtimestamp(ts)
        return f"{d.day} {MONTHS[d.month - 1]} {d.strftime('%H:%M')}"
    except (OSError, ValueError):
        return "—"


def short(n):
    n = float(n or 0)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1000:
        return f"{n / 1000:.1f}K".replace(".0K", "K")
    return f"{int(n)}"


def money(v):
    v = float(v or 0)
    if v == 0:
        return "$0.00"
    return "$" + (f"{v:.3f}" if v < 1 else f"{v:.2f}")


# ---------- investigación ----------
def scan_experiment(path, name):
    note_path = ""
    for cand in ("NOTE.md", "NOTEBOOK.md", "README.md"):
        p = os.path.join(path, cand)
        if os.path.exists(p):
            note_path = p
            break
    note = read(note_path) if note_path else ""
    fm, body = frontmatter(note)
    metric = {}
    mp = os.path.join(path, "metric.json")
    if os.path.exists(mp):
        try:
            metric = json.loads(read(mp) or "{}")
        except json.JSONDecodeError:
            metric = {}
    traces = os.path.join(path, "traces")
    proofs = len([f for f in os.listdir(traces) if f.endswith(".proof")]) if os.path.isdir(traces) else 0
    return {
        "id": name, "name": name, "date": mdate(name, path),
        "verdict": (fm.get("verdict") or metric.get("verdict") or "").lower(),
        "delta": num(metric.get("delta", fm.get("delta"))),
        "value": num(metric.get("result", fm.get("metric_value"))),
        "baseline": num(metric.get("baseline")),
        "hallazgo": block_after(body, "Hallazgo"),
        "sections": sections(body), "body": body,
        "proofs": proofs, "has_note": bool(note_path), "kind": "",
    }


def scan_versions(path):
    base = os.path.join(path, "versions")
    out = []
    if not os.path.isdir(base):
        return out
    for name in sorted(os.listdir(base)):
        d = os.path.join(base, name)
        if not os.path.isdir(d):
            continue
        meta = {}
        mp = os.path.join(d, "meta.json")
        if os.path.exists(mp):
            try:
                meta = json.loads(read(mp) or "{}")
            except json.JSONDecodeError:
                meta = {}
        files = [f for f in os.listdir(d) if f != "meta.json" and not f.startswith(".")]
        out.append({
            "id": name, "dir": d, "files": files,
            "delta": num(meta.get("delta")), "value": num(meta.get("metric_value", meta.get("result"))),
            "date": str(meta.get("fecha") or meta.get("date") or mdate(name, d)),
            "exp": str(meta.get("experimento") or meta.get("exp") or ""),
        })
    out.sort(key=lambda v: v["id"], reverse=True)
    return out


def scan_campaign(path, cid, label):
    exps, index_rows = [], {}
    idx = os.path.join(path, "_index.md")
    if not os.path.exists(idx):
        idx = os.path.join(path, "INDEX.md")
    for row in table_rows(read(idx)):
        slug = (row.get("slug") or "").strip()
        if slug:
            index_rows[slug] = row
    if os.path.isdir(path):
        for name in os.listdir(path):
            d = os.path.join(path, name)
            if not os.path.isdir(d) or name.startswith("_") or name in ("archive", "versions", "probes", "template"):
                continue
            e = scan_experiment(d, name)
            key = next((k for k in index_rows if name.endswith(k)), None)
            if key:
                r = index_rows[key]
                e["verdict"] = e["verdict"] or (r.get("verdict") or "").lower()
                e["hallazgo"] = e["hallazgo"] or (r.get("hallazgo") or "")
                e["kind"] = r.get("type") or ""
            exps.append(e)
    exps.sort(key=lambda x: (x["date"], x["name"]))
    best = None
    for e in exps:
        if e["delta"] is not None and (best is None or e["delta"] < best):
            best = e["delta"]
    return {
        "id": cid, "label": label, "path": path, "experiments": exps,
        "learnings": read(os.path.join(path, "LEARNINGS.md")),
        "best": read(os.path.join(path, "BEST.md")),
        "versions": scan_versions(path),
        "wins": sum(1 for e in exps if e["verdict"] in ("success", "ok", "win", "mejora")),
        "fails": sum(1 for e in exps if e["verdict"] in ("fail", "lose")),
        "best_delta": best,
        "updated": max([e["date"] for e in exps], default=""),
    }


def scan_goals(root, obs):
    base = os.path.join(root, ".opencode", "goals")
    legacy = {g.get("slug"): g for g in (obs.get("goals") or [])}
    out = []
    if not os.path.isdir(base):
        return out
    for slug in sorted(os.listdir(base)):
        d = os.path.join(base, slug)
        if not os.path.isdir(d) or slug in ("archive", "dashboard") or slug.startswith("test-"):
            continue
        st = {}
        sp = os.path.join(d, "STATE.json")
        if os.path.exists(sp):
            try:
                st = json.loads(read(sp) or "{}")
            except json.JSONDecodeError:
                st = {}
        plan = read(os.path.join(d, "PLAN.md"))
        log = read(os.path.join(d, "LOG.md"))
        obj = block_after(plan, "Objetivo").splitlines()
        last = ""
        for line in reversed(log.splitlines()):
            if line.strip().startswith("## "):
                last = line.strip()[3:]
                break
        old = legacy.get(slug, {})
        comites = st.get("comites_consecutivos", st.get("comites_totales"))
        out.append({
            "slug": slug,
            "objetivo": (obj[0].strip() if obj and obj[0].strip() else old.get("obj", ""))[:180],
            "status": st.get("status", old.get("state", "—")),
            "level": old.get("level", "—"),
            "iter": st.get("iter", "—"),
            "comites": comites if comites is not None else "—",
            "tokens": num(old.get("tokens"), 0) or 0,
            "basal": num(old.get("basal"), 0) or 0,
            "progress": num(old.get("progress"), 0) or 0,
            "fase": old.get("fase", ""),
            "last": last[:150],
            "mtime": os.path.getmtime(d),
            "research": os.path.isdir(os.path.join(d, "research")),
        })
    out.sort(key=lambda g: g["mtime"], reverse=True)
    return out


def collect(root):
    obs = {}
    op = os.path.join(root, ".opencode", "goals", "observability.json")
    if os.path.exists(op):
        try:
            obs = json.loads(read(op) or "{}")
        except json.JSONDecodeError:
            obs = {}
    goals = scan_goals(root, obs)
    camps = []
    pr = os.path.join(root, "research")
    if os.path.isdir(pr) and any(not n.startswith("_") and os.path.isdir(os.path.join(pr, n)) for n in os.listdir(pr)):
        camps.append(scan_campaign(pr, "proyecto", "Proyecto · " + (os.path.basename(root.rstrip("\\/")) or root)))
    base = os.path.join(root, ".opencode", "goals")
    if os.path.isdir(base):
        for slug in sorted(os.listdir(base)):
            rp = os.path.join(base, slug, "research")
            if os.path.isdir(rp) and os.listdir(rp):
                c = scan_campaign(rp, slug, slug)
                if c["experiments"]:
                    camps.append(c)
    camps.sort(key=lambda c: c["updated"], reverse=True)
    return {"root": root, "project": os.path.basename(root.rstrip("\\/")) or root,
            "goals": goals, "campaigns": camps, "obs": obs}


# ---------- markdown ----------
def inline(s):
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)


def md(text):
    out, buf, in_code = [], [], False
    rows = []

    def flush_rows():
        if not rows:
            return
        head = rows[0]
        body = [r for r in rows[1:] if r != ["-"]]
        th = "".join(f"<th>{inline(c)}</th>" for c in head)
        tr = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
        out.append(f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>")
        rows.clear()

    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(c and set(c) <= set("-: ") for c in cells):
                rows.append(["-"])
            else:
                rows.append(cells)
            continue
        flush_rows()
        if s.startswith("```"):
            if in_code:
                out.append("<pre>" + html.escape("\n".join(buf)) + "</pre>")
                buf, in_code = [], False
            else:
                in_code = True
            continue
        if in_code:
            buf.append(line)
            continue
        s = line.rstrip()
        if not s.strip():
            if buf:
                out.append("<ul>" + "".join(buf) + "</ul>" if buf[0].startswith("<li>") else "<p>" + "<br>".join(buf) + "</p>")
                buf = []
            continue
        if s.lstrip().startswith(("- ", "* ")):
            if buf and not buf[0].startswith("<li>"):
                out.append("<p>" + "<br>".join(buf) + "</p>")
                buf = []
            buf.append("<li>" + inline(s.lstrip()[2:]) + "</li>")
            continue
        buf.append(inline(s))
    flush_rows()
    if in_code and buf:
        out.append("<pre>" + html.escape("\n".join(buf)) + "</pre>")
        buf = []
    if buf:
        out.append("<ul>" + "".join(buf) + "</ul>" if buf[0].startswith("<li>") else "<p>" + "<br>".join(buf) + "</p>")
    return "\n".join(out)


# ---------- diseño ----------
CSS = """
:root{--bg:#09090b;--card:#101012;--soft:#0f0f11;--line:#202024;--line2:#2a2a2f;
--text:#fafafa;--muted:#a1a1aa;--dim:#6f6f7a;--lime:#80DB97;--lime-soft:rgba(128,219,151,.12);--bad:#f87171}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif;letter-spacing:-.011em;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}a:hover{color:var(--lime)}
code{background:#1c1c20;padding:1px 5px;border-radius:5px;font-size:.88em;font-family:"JetBrains Mono",ui-monospace,monospace}
.topbar{position:sticky;top:0;z-index:30;background:rgba(9,9,11,.94);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
.bar{display:flex;align-items:center;gap:12px;height:58px;flex-wrap:nowrap;overflow:hidden}
.logo{width:30px;height:30px;border-radius:9px;background:var(--lime);display:grid;place-items:center;color:#0a0f0b;flex:none}
.brand{font-size:13px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;white-space:nowrap}
.tag{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--lime);border:1px solid var(--line2);padding:4px 9px;border-radius:999px;background:var(--lime-soft);white-space:nowrap}
.live{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--muted)}
.dot{width:7px;height:7px;border-radius:50%;background:var(--lime);box-shadow:0 0 8px rgba(128,219,151,.8)}
.spacer{flex:1}
.seg{display:flex;background:var(--card);border:1px solid var(--line);border-radius:999px;padding:3px;gap:2px}
.seg a,.seg span{font-size:11px;padding:4px 10px;border-radius:999px;color:var(--muted)}
.seg .on{background:var(--lime);color:#0a0f0b;font-weight:600}
.tabs{display:flex;gap:6px;padding:0 0 10px;margin-top:-2px}
.tab{font-size:12px;padding:6px 13px;border-radius:8px;color:var(--muted);border:1px solid transparent}
.tab.on{background:var(--card);border-color:var(--line2);color:var(--text)}
main{max-width:1120px;margin:0 auto;padding:26px 20px 80px}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:15px 16px}
.kpi .lbl{font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--dim)}
.kpi .val{font-size:24px;font-weight:600;margin:6px 0 3px;letter-spacing:-.02em}
.kpi .sub{font-size:11px;color:var(--muted)}
.minis{display:grid;grid-template-columns:repeat(8,1fr);gap:10px;margin-top:14px}
.mini{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:11px 12px}
.mini .lbl{font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mini .val{font-size:19px;font-weight:600;margin-top:4px}
.mini .sub{font-size:10px;color:var(--dim)}
.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;margin-top:14px}
.phead{display:flex;align-items:flex-start;gap:12px;padding:15px 16px 10px;flex-wrap:wrap}
.ptitle{font-size:11px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;margin:0}
.psub{font-size:11px;color:var(--dim);margin-top:4px}
.pbody{padding:0 16px 16px}
.tools{display:flex;gap:8px;align-items:center;margin-left:auto}
.input,.select{background:#0b0b0d;border:1px solid var(--line2);border-radius:8px;color:var(--text);font:12px Inter,sans-serif;padding:7px 10px}
.input{min-width:190px}
.btn{background:#141416;border:1px solid var(--line2);border-radius:8px;color:var(--text);font:12px Inter,sans-serif;padding:7px 12px;cursor:pointer}
.btn:hover{border-color:var(--lime);color:var(--lime)}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;padding:9px 10px;font-size:10px;font-weight:500;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);border-bottom:1px solid var(--line)}
td{padding:12px 10px;border-bottom:1px solid #17171a;vertical-align:middle}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover td{background:#0d0d0f}
.goal{display:flex;gap:11px;align-items:center}
.ico{width:26px;height:26px;border-radius:8px;background:#1a1a1d;display:grid;place-items:center;flex:none;color:var(--lime)}
.gname{font-weight:600;font-size:13px}
.gobj{font-size:11.5px;color:var(--dim);margin-top:2px}
.pill{font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;padding:3px 7px;border-radius:5px;border:1px solid var(--line2);color:var(--muted);white-space:nowrap}
.pill.large{color:var(--lime);border-color:rgba(128,219,151,.3)}
.cost{text-align:right;white-space:nowrap}
.cost b{font-size:12.5px;font-weight:600}
.cost .tk{font-size:10.5px;color:var(--dim);margin-left:4px}
.bar2{height:3px;background:#26262b;border-radius:2px;margin-top:7px;overflow:hidden}
.bar2 i{display:block;height:100%;background:var(--lime)}
.ok{color:var(--lime)}.bad{color:var(--bad)}
.sub{color:var(--muted);font-size:12px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;display:block}
.card:hover{border-color:rgba(128,219,151,.45)}
.card b{font-size:14px;font-weight:600}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:9px}
.chip{font-size:11px;color:var(--muted);border:1px solid var(--line2);padding:3px 9px;border-radius:999px}
.note h3{font-size:10.5px;letter-spacing:.11em;text-transform:uppercase;color:var(--dim);margin:20px 0 6px}
.note p,.note li{color:#d4d4d8;line-height:1.65;margin:6px 0;font-size:13.5px}
.note ul{padding-left:18px}
.note pre{background:#0b0b0d;border:1px solid var(--line);border-radius:9px;padding:12px;overflow:auto;font-size:12.5px}
.empty{color:var(--dim);font-size:13px;padding:16px 2px}
svg text{fill:#6f6f7a;font-size:10px;font-family:Inter,sans-serif}
@media(max-width:980px){.minis{grid-template-columns:repeat(4,1fr)}.kpis{grid-template-columns:1fr}}
"""


def logo_svg():
    return ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M12 19V5"/><path d="M5 12l7-7 7 7"/></svg>')


def shell(title, body, active):
    now = datetime.now().strftime("%H:%M")
    tabs = [("Objetivos", "/", "g"), ("Auto-research", "/research", "r")]
    nav = "".join(f'<a class="tab{" on" if k == active else ""}" href="{h}">{l}</a>' for l, h, k in tabs)
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>
<style>{CSS}</style></head><body>
<div class="topbar"><div class="wrap">
<div class="bar">
  <span class="logo">{logo_svg()}</span>
  <span class="brand">Goal Observability</span>
  <span class="tag">Torre de Control</span>
  <span class="live"><i class="dot"></i>LIVE {now}</span>
  <span class="spacer"></span>
  <span class="seg"><span class="on">Todo</span><a href="/">24h</a><a href="/">7d</a><a href="/">30d</a></span>
</div>
<nav class="tabs">{nav}</nav>
</div></div>
<main>{body}</main></body></html>"""


def status_cls(v):
    return "ok" if v in ("success", "ok", "win", "mejora") else ("bad" if v in ("fail", "lose") else "")


def fmt_delta(d):
    return "—" if d is None else f"{d:+.3f}".replace(".", ",", 1)


# ---------- gráfica ----------
def area_chart(points, W=1060, H=250, unit="$"):
    if len(points) < 2:
        return '<div class="empty">Aún no hay dos mediciones para dibujar la evolución.</div>'
    pad_l, pad_r, pad_t, pad_b = 42, 12, 16, 26
    ys = [p[1] for p in points]
    lo, hi = min(ys), max(ys)
    span = (hi - lo) or (abs(hi) or 1)
    lo, hi = lo - span * .18, hi + span * .12
    xs = [pad_l + i * (W - pad_l - pad_r) / (len(points) - 1) for i in range(len(points))]
    pt = [(x, H - pad_b - (v - lo) / (hi - lo) * (H - pad_t - pad_b)) for x, (_, v) in zip(xs, points)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pt)
    area = f"{pad_l},{H - pad_b} " + line + f" {pt[-1][0]:.1f},{H - pad_b}"
    grid = ""
    for k in range(4):
        gy = pad_t + k * (H - pad_t - pad_b) / 3
        val = hi - k * (hi - lo) / 3
        grid += (f'<line x1="{pad_l}" y1="{gy:.1f}" x2="{W - pad_r}" y2="{gy:.1f}" stroke="#1b1b1f"/>'
                 f'<text x="{pad_l - 8}" y="{gy + 3:.1f}" text-anchor="end">{unit}{val:.2g}</text>')
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#80DB97"/>' for x, y in pt)
    labels, seen = "", set()
    for i in range(len(points)):
        label = points[i][0]
        if label in seen:
            continue
        seen.add(label)
        labels += f'<text x="{xs[i]:.1f}" y="{H - 8}" text-anchor="middle">{html.escape(label)}</text>'
    return (f'<svg viewBox="0 0 {W} {H}" width="100%" height="{H}" preserveAspectRatio="none">'
            f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="#80DB97" stop-opacity=".28"/>'
            f'<stop offset="100%" stop-color="#80DB97" stop-opacity="0"/></linearGradient></defs>'
            f'{grid}<polygon points="{area}" fill="url(#g)"/>'
            f'<polyline points="{line}" fill="none" stroke="#80DB97" stroke-width="1.8"/>'
            f'{dots}{labels}</svg>')


# ---------- vistas ----------
def view_home(data):
    g, obs = data["goals"], data["obs"]
    rc = obs.get("real_counts") or {}
    tokens = sum(x["tokens"] for x in g)
    daily = obs.get("daily") or []
    cost_total = sum(float(d.get("cost") or 0) for d in daily)
    ratio = (cost_total / tokens * 1000) if tokens else 0
    if ratio < 0.0005:
        ratio = 0.023  # precio de referencia OpenCode ($0.000023/tok)
    last24 = float(daily[-1].get("cost") or 0) if daily else 0
    last_tok = float(daily[-1].get("tokens") or 0) if daily else 0

    kpis = f"""
<div class="kpis">
  <div class="kpi"><div class="lbl">Consumo total tokens</div><div class="val">{short(tokens)}</div>
    <div class="sub">Real OpenCode · {len(g)} goals · {short(sum(x['basal'] for x in g))} basal</div></div>
  <div class="kpi"><div class="lbl">Ratio $/1K tokens</div><div class="val">{money(ratio)}</div>
    <div class="sub">Basado en {money(cost_total)} de gasto registrado</div></div>
  <div class="kpi"><div class="lbl">Gasto últimas 24h</div><div class="val">{short(last_tok)} tok</div>
    <div class="sub">total {money(last24)}</div></div>
</div>"""

    def mini(label, value, sub):
        return f'<div class="mini"><div class="lbl">{label}</div><div class="val">{value}</div><div class="sub">{sub}</div></div>'

    minis = "<div class='minis'>" + "".join([
        mini("Auto-Goal", rc.get("AUTO-GOAL", 0), "autónomos"),
        mini("Comités", rc.get("COMITES", 0), "usos en rango"),
        mini("Comités PRO", rc.get("COMITES PRO", 0), "usos en rango"),
        mini("Mini-skills", rc.get("MINI-SKILLS", 0), "promovidas"),
        mini("Planes", rc.get("PLANES", len(g)), "PLAN.md generados"),
        mini("Research", rc.get("RESEARCH", sum(len(c["experiments"]) for c in data["campaigns"])), "pruebas"),
        mini("Find-skills", rc.get("FIND-SKILLS", 0), "búsquedas"),
        mini("Auto-compact", rc.get("AUTO-COMPACT", 0), "compactados"),
    ]) + "</div>"

    pts = [(nice_date(d.get("date", "")), float(d.get("tokens") or 0)) for d in daily]
    if len(pts) < 2:
        acc, pts = 0, []
        for x in sorted(g, key=lambda y: y["mtime"]):
            acc += x["tokens"]
            pts.append((nice_date(datetime.fromtimestamp(x["mtime"]).strftime("%Y-%m-%d")), acc))
    chart = area_chart(pts, unit="")

    rows = ""
    for x in g:
        pct = int(max(0, min(100, x["progress"] or 0)))
        saved = 0
        if x["basal"]:
            saved = int(round((x["tokens"] - x["basal"]) / x["basal"] * 100))
        level = (x["level"] or "—").upper()
        cls = " large" if level == "LARGE" else ""
        rows += f"""<tr data-q="{html.escape((x['slug'] + ' ' + x['objetivo']).lower())}">
<td style="color:var(--muted);font-size:12px">{nice_stamp(x['mtime'])}</td>
<td><div class="goal"><span class="ico">{logo_svg()}</span><div>
  <div class="gname">{html.escape(x['slug'])}</div>
  <div class="gobj">{html.escape(x['objetivo']) or '—'}</div></div></div></td>
<td>{('<span class="pill' + cls + '">' + html.escape(level) + '</span>') if level != '—' else '<span style="color:var(--dim)">—</span>'}</td>
<td class="cost"><b>{money(0)}</b><span class="tk">{short(x['tokens'])} tok</span>
  <div class="bar2"><i style="width:{pct}%"></i></div>
  <div class="tk">{pct}% · {saved:+d}%</div></td></tr>"""
    if not rows:
        rows = '<tr><td colspan="4" class="empty">Sin objetivos en este proyecto.</td></tr>'

    body = f"""{kpis}{minis}
<div class="panel"><div class="phead"><div>
  <h2 class="ptitle">Evolución eficiencia · tokens (menor es mejor)</h2>
  <div class="psub">Acumulado por objetivo. Se actualiza al abrir.</div></div>
  <div class="tools"><span class="chip">— goal</span></div></div>
  <div class="pbody">{chart}</div></div>
<div class="panel"><div class="phead"><div>
  <h2 class="ptitle">Goals — semáforo</h2>
  <div class="psub">Nivel 1 · {len(g)} objetivos</div></div>
  <div class="tools">
    <input class="input" id="q" placeholder="Buscar slug u objetivo…" oninput="filt()">
    <select class="select" id="lv" onchange="filt()"><option>Todos</option><option>SMALL</option><option>LARGE</option></select>
    <button class="btn" onclick="exp()">Export CSV</button>
  </div></div>
  <div class="pbody" style="padding-top:0">
  <table id="tb"><thead><tr><th>Fecha</th><th>Slug / Objetivo</th><th>Nivel</th><th style="text-align:right">Coste</th></tr></thead>
  <tbody>{rows}</tbody></table></div></div>
<script>
function filt(){{
  var q=document.getElementById('q').value.toLowerCase(), lv=document.getElementById('lv').value;
  document.querySelectorAll('#tb tbody tr').forEach(function(tr){{
    var okq=!q||(tr.dataset.q||'').includes(q);
    var okl=lv==='Todos'||(tr.querySelector('.pill')||{{textContent:''}}).textContent.trim()===lv;
    tr.style.display=(okq&&okl)?'':'none';
  }});
}}
function exp(){{
  var rows=[['fecha','slug','objetivo','nivel','tokens']];
  document.querySelectorAll('#tb tbody tr').forEach(function(tr){{
    if(tr.style.display==='none')return;
    var c=tr.querySelectorAll('td');
    rows.push([c[0].innerText,c[1].querySelector('.gname').innerText,c[1].querySelector('.gobj').innerText,
               c[2].innerText,c[3].querySelector('.tk').innerText]);
  }});
  var csv=rows.map(function(r){{return r.map(function(v){{return '"'+v.replace(/"/g,'""')+'"';}}).join(',');}}).join('\\n');
  var a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([csv],{{type:'text/csv'}}));a.download='goals.csv';a.click();
}}
</script>"""
    return shell("Objetivos · " + data["project"], body, "g")


def view_research(data):
    if not data["campaigns"]:
        return shell("Auto-research · " + data["project"],
                     '<div class="panel"><div class="phead"><h2 class="ptitle">Auto-research</h2></div>'
                     '<div class="pbody"><div class="empty">Todavía no hay investigaciones en este proyecto.</div></div></div>', "r")
    cards = ""
    for c in data["campaigns"]:
        cards += f"""<a class="card" href="/run/{c['id']}">
<div style="display:flex;justify-content:space-between;align-items:center;gap:8px">
  <b>{html.escape(c['label'])}</b><span class="pill large">research</span></div>
<div class="sub" style="margin-top:6px">{len(c['experiments'])} pruebas · {c['wins']} con mejora</div>
<div class="chips"><span class="chip">mejor {fmt_delta(c['best_delta'])}</span>
<span class="chip">última {html.escape(c['updated'] or '—')}</span></div></a>"""
    body = (f'<div class="panel"><div class="phead"><div><h2 class="ptitle">Investigaciones</h2>'
            f'<div class="psub">Cada prueba guarda su cuaderno completo</div></div></div>'
            f'<div class="pbody"><div class="cards">{cards}</div></div></div>')
    return shell("Auto-research · " + data["project"], body, "r")


def view_run(data, cid):
    c = next((x for x in data["campaigns"] if x["id"] == cid), None)
    if not c:
        return None
    pts = [(nice_date(e["date"]), e["value"]) for e in c["experiments"] if e["value"] is not None]
    if len(pts) < 2:
        pts = [(nice_date(e["date"]), e["delta"]) for e in c["experiments"] if e["delta"] is not None]
    rows = "".join(
        f'<tr><td><a href="/exp/{c["id"]}/{e["id"]}"><b>{html.escape(e["name"])}</b></a></td>'
        f'<td class="{status_cls(e["verdict"])}">{html.escape(e["verdict"] or "—")}</td>'
        f'<td>{fmt_delta(e["delta"])}</td>'
        f'<td style="color:var(--dim)">{html.escape(re.sub(r"<[^>]+>", "", e["hallazgo"])[:80]) or "—"}</td></tr>'
        for e in reversed(c["experiments"])) or '<tr><td colspan="4" class="empty">Sin pruebas.</td></tr>'
    learn = md(c["learnings"]) if c["learnings"].strip() else '<div class="empty">Sin aprendizaje acumulado.</div>'
    best = (f'<div class="panel"><div class="phead"><div><h2 class="ptitle">Mejor versión guardada</h2>'
            f'<div class="psub">Apuntador a la mejor versión conocida</div></div></div>'
            f'<div class="pbody note">{md(c["best"])}</div></div>') if c["best"].strip() else ""
    vers = ""
    if c["versions"]:
        vrows = "".join(
            f'<tr><td><a href="/ver/{c["id"]}/{v["id"]}"><b>{html.escape(v["id"])}</b></a></td>'
            f'<td style="color:var(--muted)">{html.escape(v["date"])}</td>'
            f'<td>{html.escape(v["exp"]) or "—"}</td><td>{fmt_delta(v["delta"])}</td>'
            f'<td style="color:var(--dim)">{html.escape(", ".join(v["files"]))[:70]}</td></tr>'
            for v in c["versions"])
        vers = ('<div class="panel"><div class="phead"><div><h2 class="ptitle">Versiones del sujeto</h2>'
                '<div class="psub">Cada mejora deja copia exacta del archivo</div></div></div>'
                '<div class="pbody" style="padding-top:0"><table><thead><tr><th>Versión</th><th>Fecha</th>'
                f'<th>Experimento</th><th>Cambio</th><th>Archivos</th></tr></thead><tbody>{vrows}</tbody></table></div></div>')

    body = f"""
<p class="sub" style="margin:0 0 12px"><a href="/research">← investigaciones</a></p>
<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
  <h1 style="font-size:19px;margin:0">{html.escape(c['label'])}</h1>
  <span class="chip">{len(c['experiments'])} pruebas</span><span class="chip ok">{c['wins']} con mejora</span>
  <span class="chip bad">{c['fails']} sin mejora</span><span class="chip">mejor {fmt_delta(c['best_delta'])}</span></div>
<div class="panel"><div class="phead"><div><h2 class="ptitle">Progreso</h2>
  <div class="psub">Métrica por prueba, en orden</div></div></div><div class="pbody">{area_chart(pts, unit="")}</div></div>
{vers}
{best}
<div class="panel"><div class="phead"><div><h2 class="ptitle">Pruebas</h2>
  <div class="psub">Pincha para abrir el cuaderno</div></div></div>
  <div class="pbody" style="padding-top:0"><table><thead><tr><th>Fecha · prueba</th><th>Veredicto</th><th>Cambio</th><th>Hallazgo</th></tr></thead>
  <tbody>{rows}</tbody></table></div></div>
<div class="panel"><div class="phead"><h2 class="ptitle">Lo aprendido</h2></div>
  <div class="pbody note">{learn}</div></div>"""
    return shell(c["label"] + " · auto-research", body, "r")


def view_exp(data, cid, eid):
    c = next((x for x in data["campaigns"] if x["id"] == cid), None)
    e = next((x for x in c["experiments"] if x["id"] == eid), None) if c else None
    if not e:
        return None
    secs = "".join(f"<h3>{html.escape(t)}</h3>{md(b)}" for t, b in e["sections"])
    if not secs:
        secs = md(e["body"]) if e["body"].strip() else '<div class="empty">Este experimento no tiene cuaderno todavía.</div>'
    chips = [f'<span class="chip">{html.escape(e["date"])}</span>']
    if e["value"] is not None:
        chips.append(f'<span class="chip">métrica {e["value"]:.3g}</span>')
    if e["baseline"] is not None:
        chips.append(f'<span class="chip">base {e["baseline"]:.3g}</span>')
    chips.append(f'<span class="chip {status_cls(e["verdict"])}">{html.escape(e["verdict"] or "sin veredicto")}</span>')
    chips.append(f'<span class="chip">{e["proofs"]} pruebas de ejecución</span>')
    body = f"""
<p class="sub" style="margin:0 0 12px"><a href="/run/{c['id']}">← {html.escape(c['label'])}</a></p>
<h1 style="font-size:19px;margin:0">{html.escape(e['name'])}</h1>
<div class="chips">{''.join(chips)}</div>
<div class="panel note" style="margin-top:16px"><div class="pbody">{secs}</div></div>"""
    return shell(e["name"] + " · cuaderno", body, "r")


def view_ver(data, cid, vid):
    c = next((x for x in data["campaigns"] if x["id"] == cid), None)
    v = next((x for x in c["versions"] if x["id"] == vid), None) if c else None
    if not v:
        return None
    blocks = ""
    for f in v["files"]:
        body = read(os.path.join(v["dir"], f))
        blocks += f"<h3>{html.escape(f)}</h3><pre>{html.escape(body)}</pre>"
    chips = [f'<span class="chip">{html.escape(v["date"])}</span>']
    if v["value"] is not None:
        chips.append(f'<span class="chip">métrica {v["value"]:.3g}</span>')
    if v["delta"] is not None:
        chips.append(f'<span class="chip">cambio {fmt_delta(v["delta"])}</span>')
    if v["exp"]:
        chips.append(f'<span class="chip">{html.escape(v["exp"])}</span>')
    body = f"""
<p class="sub" style="margin:0 0 12px"><a href="/run/{c['id']}">← {html.escape(c['label'])}</a></p>
<h1 style="font-size:19px;margin:0">{html.escape(v['id'])}</h1>
<div class="chips">{''.join(chips)}</div>
<div class="panel note" style="margin-top:16px"><div class="pbody">{blocks or '<div class="empty">Sin archivos.</div>'}</div></div>"""
    return shell(v["id"] + " · versión", body, "r")


# ---------- servidor ----------
class Handler(BaseHTTPRequestHandler):
    root = "."

    def log_message(self, *a):
        pass

    def send(self, body, code=200, ctype="text/html; charset=utf-8"):
        raw = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = unquote(self.path.split("?")[0]).strip("/")
        data = collect(self.root)
        parts = path.split("/")
        page = None
        if path == "":
            page = view_home(data)
        elif path == "research":
            page = view_research(data)
        elif parts[0] == "run" and len(parts) == 2:
            page = view_run(data, parts[1])
        elif parts[0] == "exp" and len(parts) == 3:
            page = view_exp(data, parts[1], parts[2])
        elif parts[0] == "ver" and len(parts) == 3:
            page = view_ver(data, parts[1], parts[2])
        if page is None:
            return self.send("no encontrado", 404, "text/plain; charset=utf-8")
        if not (path.startswith("exp/") or path.startswith("ver/")):
            page = page.replace("<head>", '<head><meta http-equiv="refresh" content="15">', 1)
        self.send(page)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=os.getcwd())
    ap.add_argument("--port", type=int, default=3010)
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--render", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.project)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if a.render or not a.serve:
        out = os.path.join(root, ".opencode", "goals", "dashboard.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(view_home(collect(root)))
        print("escrito:", out)
        if not a.serve:
            return
    Handler.root = root
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print(f"torre lista en http://127.0.0.1:{a.port}  (proyecto: {root})")
    srv.serve_forever()


if __name__ == "__main__":
    main()
