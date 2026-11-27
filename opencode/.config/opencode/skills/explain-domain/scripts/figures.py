#!/usr/bin/env python3
"""Build explain-domain figures and assemble the standalone page. Standard library only.

  figures.py flow  SPEC.json  > fragment.html   phase-lane dependency map (+ stepper when the spec has steps)
  figures.py chart SPEC.json  > fragment.html   time-series chart with crosshair readout (+ stepper, data table)
  figures.py inline SRC.html OUT.html [--font FILE.ttf --font-name NAME]
                                                 inline assets/kit.css and kit.js, optionally embed a font, refuse remote assets

Spec formats are documented in references/build.md. Warnings go to stderr; fix them before shipping.
"""
import base64
import html
import json
import math
import re
import sys
import textwrap
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
esc = html.escape


def warn(msg):
    print(f"warning: {msg}", file=sys.stderr)


def text_w(text, size, mono=False):
    """Rough rendered width; deliberately generous so boxes never clip."""
    if mono:
        return len(text) * size * 0.62
    wide = sum(1 for ch in text if ch.isupper() or ch.isdigit() or ch in "MW%")
    return (len(text) - wide) * size * 0.53 + wide * size * 0.64


def wrap(text, width_px, size=14, mono=True):
    if "\n" in text:
        return text.split("\n")
    per = max(8, int(width_px / (size * (0.62 if mono else 0.55))))
    return textwrap.wrap(text, per) or [""]


def unit(u):
    """Accept 'u3', 3 or '3'."""
    if u in (None, ""):
        return ""
    return u if str(u).startswith("u") else f"u{u}"


def label(cls, lines, x, y, step=None, up=False, dy=16):
    """Multi-line SVG text; with up=True the last line sits on y and earlier lines stack above it."""
    y0 = y - dy * (len(lines) - 1) if up else y
    spans = "".join(f'<tspan x="{x:.0f}" dy="{0 if i == 0 else dy}">{esc(t)}</tspan>' for i, t in enumerate(lines))
    w = f' data-w="{step}"' if step else ""
    return f'<text class="{cls}"{w} x="{x:.0f}" y="{y0:.0f}">{spans}</text>'


def walk(fid, inner, steps, key="", extra="", start=None):
    """Reader-driven stepper around a figure. steps: [{name, unit, value?, text}]. Captions double as the no-JS text."""
    rail = "".join(f'<li><button type="button" class="{unit(s.get("unit"))}" data-to="{i + 1}">{esc(s["name"])}</button></li>'
                   for i, s in enumerate(steps))
    caps = "".join(f'<li><b class="walk-t">{esc(s["name"])}</b>'
                   + (f'<span class="walk-v {unit(s.get("unit"))}">{esc(str(s["value"]))}</span>' if s.get("value") not in (None, "") else "")
                   + f'<span class="walk-d">{s["text"]}</span></li>' for s in steps)
    ident = f' id="{esc(fid)}"' if fid else ""
    if start == "last":
        start = len(steps)
    ident += f' data-start="{int(start)}"' if start else ""
    return (f'<figure class="walk" data-walk{ident}><div class="walk-bar"><ol class="walk-rail" aria-label="Steps">{rail}</ol>'
            f'<div class="walk-ctl"><button type="button" data-back>Back</button><button type="button" class="primary" data-step>Next</button></div></div>'
            f'<div class="frame">{inner}</div>{key}<p class="walk-cap" aria-live="polite"></p><ol class="walk-caps">{caps}</ol>{extra}</figure>')


def plain(fid, inner, caption="", key="", extra=""):
    ident = f' id="{esc(fid)}"' if fid else ""
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return f'<figure data-reveal{ident}><div class="frame">{inner}</div>{key}{cap}{extra}</figure>'


def html_key(items):
    if not items:
        return ""
    lis = "".join(f'<li class="{unit(i.get("unit"))}{" hollow" if i.get("hollow") else ""}">{esc(i["text"])}</li>' for i in items)
    return f'<ul class="key">{lis}</ul>'


# ---------------------------------------------------------------- flow

NH, PITCH, GUT, TOP = 96, 146, 150, 24


def flow(spec):
    fid = spec.get("id", "overview")
    gap = spec.get("gap", 130)
    lanes, nodes = spec["lanes"], {n["id"]: dict(n) for n in spec["nodes"]}
    steps = spec.get("steps") or []
    stepped = bool(steps)
    for n in nodes.values():
        need = max(text_w(n["label"], 14), text_w(str(n.get("value", "")), 30), text_w(n.get("sub", ""), 14)) + 26
        n["w"] = n.get("w") or max(spec.get("min_w", 170), math.ceil(need / 10) * 10)
        if stepped and "step" not in n:
            warn(f'node {n["id"]} has no step; it will show from step 1')
    cols = max(n["col"] for n in nodes.values()) + 1
    colw = [max([n["w"] for n in nodes.values() if n["col"] == c] or [0]) for c in range(cols)]
    colx = [GUT + sum(colw[:c]) + c * gap for c in range(cols)]
    for n in nodes.values():
        n["x"], n["y"] = colx[n["col"]] + (colw[n["col"]] - n["w"]) / 2 if spec.get("center") else colx[n["col"]], TOP + n["lane"] * PITCH
        n["r"], n["m"] = n["x"] + n["w"], n["y"] + NH / 2
    right = max(n["r"] for n in nodes.values())
    height = TOP + len(lanes) * PITCH - (PITCH - NH) + 16

    # Legend in the first free top-right corner; widen the drawing when nothing is free.
    legend, lx, ly, legend_html = spec.get("legend") or [], None, None, ""
    if legend:
        title = spec.get("legend_title", "Colour is the unit of measure")
        lw = max([text_w(i["text"], 14) + 34 for i in legend] + [text_w(title, 14)])
        lh = 26 + 28 * len(legend)
        lx = right - lw
        for top_lane in range(len(lanes)):
            y0 = TOP + top_lane * PITCH
            clash = [n for n in nodes.values() if n["r"] > lx - 24 and n["y"] < y0 + lh and n["y"] + NH > y0]
            if not clash:
                ly = y0
                break
        if ly is None:  # no free corner: show the legend as a key under the drawing rather than shrinking it
            legend_html = '<ul class="key"><li class="cap">' + esc(title) + ":</li>" + "".join(
                f'<li class="{unit(i.get("unit"))}">{esc(i["text"])}</li>' for i in legend) + "</ul>"
            legend = []
    width = right + 16

    def step_of(e):
        return e.get("step", nodes[e["to"]].get("step"))

    def w_attr(step):
        return f' data-w="{step}"' if stepped and step else ""

    out, marker = [], f"ah-{fid}"
    draw = "wdraw" if stepped else "draw"
    segs, pending, buses = [], [], {}  # every drawn segment, and (edge index, label, candidates) to place once all lines exist

    def path(pts, step, k, arrow=True, after=False):
        segs.extend((k, a, b) for a, b in zip(pts, pts[1:]))
        d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts)
        cls = f'e {draw}{" after" if after else ""}'
        m = f' marker-end="url(#{marker})"' if arrow else ""
        return f'<path class="{cls}"{w_attr(step)} pathLength="1"{m} d="{d}"/>'

    def along(a, b, y):
        """Label spots for a horizontal run from x=a to x=b at height y: above (wrapped to fit), then below."""
        mid, span = (a + b) / 2, abs(b - a) - 10
        return [("el", wrap(lab, span + room), mid, y - 9, True) for room in (0, 30, 60)] + [("el", wrap(lab, span + 40), mid, y + 19, False)]

    def beside(x, y1, y2, prefer="r"):
        """Label spots beside a vertical run: preferred side first, single line then wrapped, middle then ends."""
        out_ = []
        for width in (400, 150):
            lines = wrap(lab, width)
            for y in ((y1 + y2) / 2 + 4 - 8 * (len(lines) - 1), y1 + 16, y2 - 8 - 16 * (len(lines) - 1)):
                for side in (prefer, "l" if prefer == "r" else "r"):
                    out_.append((f"el {side}", lines, x + (8 if side == "r" else -8), y, False))
        return out_

    for k, e in enumerate(spec.get("edges", [])):
        step, lab = step_of(e), e.get("label", "")
        t = nodes[e["to"]]
        srcs = e["from"] if isinstance(e["from"], list) else [e["from"]]
        for s in srcs:
            if s not in nodes:
                sys.exit(f'edge from unknown node {s}')
        side = e.get("side", "r")
        ss = [nodes[s] for s in srcs]
        if len(srcs) > 1 and any(s["lane"] > t["lane"] for s in ss):
            sys.exit(f'merge into {t["id"]}: inputs must sit in the target lane or above it')
        if len(srcs) > 1 and not all(s["r"] < t["x"] for s in ss):
            # merge from above: inputs reach a bus over the target, then one shared line enters it from the top.
            # Inputs in the target's own lane step out sideways and up to the bus.
            buses[t["lane"]] = buses.get(t["lane"], -1) + 1
            jx, by = (t["x"] + t["r"]) / 2, t["y"] - 18 - 12 * buses[t["lane"]]
            for s in ss:
                sx = (s["x"] + s["r"]) / 2
                if s["lane"] < t["lane"]:
                    pts = [(sx, s["y"] + NH), (sx, by), (jx, by)] if abs(sx - jx) > 1 else [(sx, s["y"] + NH), (jx, by)]
                elif s["r"] < t["x"]:
                    pts = [(s["r"], s["m"]), (s["r"] + 16, s["m"]), (s["r"] + 16, by), (jx, by)]
                elif s["x"] > t["r"]:
                    pts = [(s["x"], s["m"]), (s["x"] - 16, s["m"]), (s["x"] - 16, by), (jx, by)]
                else:
                    sys.exit(f'merge into {t["id"]}: {s["id"]} overlaps the target')
                out.append(path(pts, step, k, arrow=False))
            out.append(f'<circle class="junc"{w_attr(step)} cx="{jx:.0f}" cy="{by:.0f}" r="3.5"/>')
            out.append(path([(jx, by), (jx, t["y"])], step, k, after=True))
            xs_ = [(s["x"] + s["r"]) / 2 for s in ss] + [jx]
            stops = sorted(set(round(x) for x in xs_))
            spans = sorted(zip(stops, stops[1:]), key=lambda ab: ab[0] - ab[1])  # widest gap between drops first
            cands = beside(jx, by + 4, by + 4, side) + [c for a_, b_ in spans for c in along(a_, b_, by)] + along(min(xs_), max(xs_), by) \
                + beside(jx, by + 4, by + 4, "l" if side == "r" else "r")
        elif len(srcs) > 1:  # merge from the left: inputs meet at a junction, then one shared line carries the label in
            jx, jy = max(s["r"] for s in ss) + 16, t["m"]
            if jx > t["x"] - 40:
                warn(f'merge into {t["id"]}: little room for the shared line; raise "gap"')
            for s in ss:
                pts = [(s["r"], s["m"]), (jx, jy)] if s["lane"] == t["lane"] else [(s["r"], s["m"]), (jx, s["m"]), (jx, jy)]
                out.append(path(pts, step, k, arrow=False))
            out.append(f'<circle class="junc"{w_attr(step)} cx="{jx:.0f}" cy="{jy:.0f}" r="3.5"/>')
            out.append(path([(jx, jy), (t["x"], jy)], step, k, after=True))
            cands = along(jx, t["x"], jy)
        else:
            s = nodes[srcs[0]]
            if t["lane"] == s["lane"]:
                if t["col"] <= s["col"]:
                    sys.exit(f'edge {s["id"]}->{t["id"]}: same-lane edges must point right')
                out.append(path([(s["r"], s["m"]), (t["x"], t["m"])], step, k))
                cands = along(s["r"], t["x"], s["m"])
            elif t["lane"] < s["lane"]:
                sys.exit(f'edge {s["id"]}->{t["id"]} points up a lane; reorder lanes so results sit below inputs')
            else:
                lo, hi = max(s["x"], t["x"]), min(s["r"], t["r"])
                if hi - lo >= 30:  # columns overlap: straight down, right of centre so a left-going sibling can leave from the left
                    x = e.get("x") or (lo + hi) / 2 + min(20, (hi - lo) / 4)
                    out.append(path([(x, s["y"] + NH), (x, t["y"])], step, k))
                    cands = beside(x, s["y"] + NH, t["y"], side)
                elif t["x"] > s["r"]:  # down and to the right: along the source lane, down a corridor, in from the left
                    cx = t["x"] - min(gap / 2, (t["x"] - s["r"]) / 2)
                    out.append(path([(s["r"], s["m"]), (cx, s["m"]), (cx, t["m"]), (t["x"], t["m"])], step, k))
                    cands = beside(cx, s["m"] + 10, t["m"] - 10, side) + along(cx, t["x"], t["m"]) + along(s["r"], cx, s["m"])
                else:  # down and to the left: leave from the left of the source, cross above the target, in from the top
                    sx, tx, yb = e.get("x") or s["x"] + min(40, s["w"] / 4), (t["x"] + t["r"]) / 2, t["y"] - 22
                    out.append(path([(sx, s["y"] + NH), (sx, yb), (tx, yb), (tx, t["y"])], step, k))
                    cands = along(tx, sx, yb) + beside(sx, s["y"] + NH, yb, "l")
        if lab:
            pending.append((k, step, cands))

    # Place each label at its first spot clear of nodes, the legend, other labels and other edges' lines.
    def box(c):
        cls, lines, x, y, up = c
        w = max(len(l) for l in lines) * 14 * 0.62 + 6
        y0 = y - 16 * (len(lines) - 1) if up else y
        x0 = x - w / 2 if cls == "el" else (x if cls.endswith(" r") else x - w)
        return (x0, y0 - 12, x0 + w, y0 + 16 * (len(lines) - 1) + 4)

    def overlap(a, b):
        return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))

    blocks = [(n["x"] - 3, n["y"] - 3, n["r"] + 3, n["y"] + NH + 3) for n in nodes.values()] + [(0, 0, GUT - 8, height)]
    if legend:
        blocks.append((lx - 8, ly - 4, width, ly + 26 + 28 * len(legend)))
    placed = []
    for k, step, cands in pending:
        lines_ = [(min(a[0], b[0]) - 3, min(a[1], b[1]) - 3, max(a[0], b[0]) + 3, max(a[1], b[1]) + 3) for j, a, b in segs]

        def cost(c):
            r = box(c)
            off = 0 if r[0] >= 0 and r[2] <= width and r[1] >= 0 and r[3] <= height else 1e6
            return off + sum(overlap(r, b) for b in blocks + placed) * 10 + sum(overlap(r, b) for b in lines_)
        best = min(cands, key=lambda c: (cost(c) > 0, cost(c), cands.index(c)))
        if cost(best) > 0:
            warn(f'edge label {" ".join(best[1])!r} could not be placed cleanly; shorten it, raise "gap", or set "side"')
        placed.append(box(best))
        cls, lines, x, y, up = best
        out.append(label(cls, lines, x, y, step if stepped else None, up=up))

    lanes_svg = []
    for i, ln in enumerate(lanes):
        y = TOP + i * PITCH
        if i:
            end = (lx - 20) if (legend and ly is not None and ly < y - 25 < ly + 26 + 28 * len(legend)) else width - 8
            lanes_svg.append(f'<line class="grid" x1="12" x2="{end:.0f}" y1="{y - 25}" y2="{y - 25}"/>')
        title = wrap(ln["title"], GUT - 16, 15, mono=False)
        lanes_svg.append(label("tb", title, 16, y + 26))
        if ln.get("note"):
            lanes_svg.append(f'<text class="td" x="16" y="{y + 30 + 20 * len(title)}">{esc(ln["note"])}</text>')

    nodes_svg = []
    for n in nodes.values():
        u = unit(n.get("unit"))
        cls = f'nd {u}{" out" if n.get("out") else ""}'
        nodes_svg.append(
            f'<g class="{cls}"{w_attr(n.get("step"))}><rect class="nd-box" x="{n["x"]:.0f}" y="{n["y"]}" width="{n["w"]}" height="{NH}" rx="6"/>'
            f'<text class="nd-k" x="{n["x"] + 12:.0f}" y="{n["y"] + 24}">{esc(n["label"])}</text>'
            f'<text class="nd-v" x="{n["x"] + 12:.0f}" y="{n["y"] + 60}">{esc(str(n.get("value", "")))}</text>'
            f'<text class="nd-s" x="{n["x"] + 12:.0f}" y="{n["y"] + 82}">{esc(n.get("sub", ""))}</text></g>')

    leg = []
    if legend:
        leg.append(f'<text class="td" x="{lx:.0f}" y="{ly + 14}">{esc(spec.get("legend_title", "Colour is the unit of measure"))}</text>')
        for i, item in enumerate(legend):
            y = ly + 26 + 28 * i
            leg.append(f'<g class="{unit(item.get("unit"))}"><rect class="sw" x="{lx:.0f}" y="{y}" width="18" height="18" rx="3"/>'
                       f'<text class="t" x="{lx + 30:.0f}" y="{y + 14}">{esc(item["text"])}</text></g>')

    if not spec.get("label"):
        warn("flow needs a 'label': one sentence naming the path from inputs to outputs")
    defs = (f'<defs><marker id="{marker}" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto">'
            f'<path d="M0 0L10 5L0 10z" fill="#4a5368"/></marker></defs>')
    svg = (f'<svg class="ve-svg wide" viewBox="0 0 {width:.0f} {height:.0f}" style="max-width:{width * 1.1:.0f}px" role="img" aria-label="{esc(spec.get("label", ""))}">'
           + defs + "".join(lanes_svg) + "".join(out) + "".join(nodes_svg) + "".join(leg) + "</svg>")
    if stepped:
        used = {n.get("step") for n in nodes.values()} | {step_of(e) for e in spec.get("edges", [])}
        if max(x for x in used if x) != len(steps):
            warn(f"flow has {len(steps)} step captions but parts use steps up to {max(x for x in used if x)}")
        return walk(fid, svg, steps, legend_html, start=spec.get("start"))
    return plain(fid, svg, spec.get("caption", ""), legend_html)


# ---------------------------------------------------------------- chart

def chart(spec):
    fid = spec.get("id", "")
    W, H = spec.get("width", 1000), spec.get("height", 330)
    L, R, T, B = 70, W - 20, 48, H - 52
    xs = spec["x"]
    n = len(xs["labels"])
    pos = xs.get("positions") or list(range(n))
    p0, p1 = xs.get("min", pos[0]), xs.get("max", pos[-1])
    # Bars need half a slot of room at each end so the first and last bars clear the axis labels.
    inset = (R - L) / (2 * n) if any(s.get("style") == "bars" for s in spec["series"]) else 0
    X = lambda i: L + inset + (pos[i] - p0) / ((p1 - p0) or 1) * (R - L - 2 * inset)
    ys = spec["y"]
    y0, y1 = ys["min"], ys["max"]
    Y = lambda v: B - (v - y0) / ((y1 - y0) or 1) * (B - T)
    steps = spec.get("steps") or []
    stepped = bool(steps)
    wa = lambda s: f' data-w="{s}"' if stepped and s else ""
    draw = "wdraw" if stepped else "draw"
    yfmt = ys.get("format", "{:g}")
    parts = []
    for v in ys.get("ticks", [y0, y1]):
        parts.append(f'<line class="grid" x1="{L}" x2="{R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/>'
                     f'<text class="td end num" x="{L - 10}" y="{Y(v) + 5:.1f}">{esc(yfmt.format(v))}</text>')
    ticks = xs.get("ticks", [0, n - 1])
    for i, text in zip(ticks, xs.get("tick_labels") or [xs["labels"][i] for i in ticks]):
        parts.append(f'<text class="td mid num" x="{X(i):.1f}" y="{B + 22}">{esc(text)}</text>')
    if xs.get("title"):
        parts.append(f'<text class="td mid" x="{(L + R) / 2:.0f}" y="{H - 8}">{esc(xs["title"])}</text>')
    if ys.get("title"):
        parts.append(f'<text class="td" x="{L}" y="{T - 30}">{esc(ys["title"])}</text>')
    for w in spec.get("windows", []):
        a, b = X(w["from"]), X(w["to"])
        pad = 9
        parts.append(f'<rect class="win {unit(w.get("unit"))}"{wa(w.get("step"))} x="{a - pad:.1f}" y="{T}" width="{b - a + 2 * pad:.1f}" height="{B - T}"/>')
        if w.get("label"):
            parts.append(f'<text class="td mid"{wa(w.get("step"))} x="{(a + b) / 2:.1f}" y="{B - 10}">{esc(w["label"])}</text>')
    series = spec["series"]
    for bt in spec.get("between", []):
        up, lo = series[bt["upper"]]["values"], series[bt["lower"]]["values"]
        bw = min(14, 0.6 * (R - L) / max(n - 1, 1))
        g = []
        for i in range(bt["from"], bt["to"] + 1):
            if up[i] is None or lo[i] is None or up[i] <= lo[i]:
                continue
            g.append(f'<rect class="bar tint" x="{X(i) - bw / 2:.1f}" y="{Y(up[i]):.1f}" width="{bw:.1f}" height="{Y(lo[i]) - Y(up[i]):.1f}"/>')
        parts.append(f'<g class="{unit(bt.get("unit", 3))}"{wa(bt.get("step"))}>{"".join(g)}</g>')
        if bt.get("label"):
            parts.append(f'<text class="t"{wa(bt.get("step"))} x="{X(bt["from"]) - 14:.1f}" y="{T + 18}" text-anchor="end">{esc(bt["label"])}</text>')

    def segments(vals):
        segs, cur = [], []
        for i, v in enumerate(vals):
            if v is None:
                if cur:
                    segs.append(cur)
                cur = []
            else:
                cur.append((X(i), Y(v)))
        if cur:
            segs.append(cur)
        return segs

    for s in series:
        u, style, st = unit(s.get("unit")), s.get("style", "line"), s.get("step")
        if style == "bars":
            bw = min(s.get("bar_width", 28), 0.7 * (R - L) / max(n - 1, 1))
            bars = "".join(f'<rect class="bar grow" style="--i:{i}" x="{X(i) - bw / 2:.1f}" y="{min(Y(v), Y(max(y0, 0))):.1f}" width="{bw:.1f}" height="{max(abs(Y(max(y0, 0)) - Y(v)), 1.5):.1f}"/>'
                           for i, v in enumerate(s["values"]) if v is not None)
            parts.append(f'<g class="{u}"{wa(st)}>{bars}</g>')
            continue
        for seg in segments(s["values"]):
            d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in seg)
            if style == "area":
                parts.append(f'<path class="area fade {u}"{wa(st)} d="{d} L{seg[-1][0]:.1f},{B} L{seg[0][0]:.1f},{B}Z"/>')
            cls = {"line": "", "area": "", "dash": " dash", "dot": " dot", "thin": " thin"}.get(style, "")
            if style in ("dash", "dot"):
                parts.append(f'<path class="ln{cls} fade {u}"{wa(st)} d="{d}"/>')
            else:
                parts.append(f'<path class="ln{cls} {draw} {u}"{wa(st)} pathLength="1" d="{d}"/>')
    for r in spec.get("refs", []):
        parts.append(f'<line class="ref"{wa(r.get("step"))} x1="{L}" x2="{R}" y1="{Y(r["y"]):.1f}" y2="{Y(r["y"]):.1f}"/>'
                     f'<text class="td end"{wa(r.get("step"))} x="{R}" y="{Y(r["y"]) - 6:.1f}">{esc(r.get("label", ""))}</text>')
    for m in spec.get("marks", []):
        x = X(m["at"])
        anchor = "end" if x > (L + R) / 2 else "start"
        dx = -8 if anchor == "end" else 8
        parts.append(f'<line class="mark"{wa(m.get("step"))} x1="{x:.1f}" x2="{x:.1f}" y1="{T - 8}" y2="{B}"/>'
                     f'<text class="tb" text-anchor="{anchor}"{wa(m.get("step"))} x="{x + dx:.1f}" y="{T - 12}">{esc(m["label"])}</text>')
    for note in spec.get("notes", []):
        x = X(note["at"])
        parts.append(label("t mid", wrap(note["text"], 200, 14, False), x, Y(note["y"]), note.get("step")))

    shown = [s for s in series if s.get("readout", True)]

    def fmt(s, i):
        v = s["values"][i]
        if s.get("text"):
            return s["text"][i]
        return "—" if v is None else s.get("format", "{:g}").format(v)

    rows = [[xs.get("readout_labels", xs["labels"])[i], round(X(i), 1),
             [[None if s["values"][i] is None else round(Y(s["values"][i]), 1), fmt(s, i)] for s in shown]] for i in range(n)]
    hov = {"names": [[s["name"], unit(s.get("unit")), "hollow" if s.get("style") in ("dash", "dot") else ""] for s in shown],
           "rows": rows, "at": spec.get("at", 0), "top": T, "bottom": B}
    lab = spec.get("label", "")
    if not lab:
        warn("chart needs a 'label': what the chart shows and the value at the point of interest")
    lab += " Use the left and right arrow keys to read each point."
    svg = (f'<svg class="ve-svg" viewBox="0 0 {W} {H}" role="img" tabindex="0" aria-label="{esc(lab)}" '
           f'data-hover="{esc(json.dumps(hov, separators=(",", ":")))}">' + "".join(parts) + "</svg>")
    key = html_key(spec.get("key") or [{"text": s["name"], "unit": s.get("unit"), "hollow": s.get("style") in ("dash", "dot")} for s in series])
    table = ""
    if spec.get("table", n <= 60):
        head = "".join(f"<th scope=\"col\">{esc(s['name'])}</th>" for s in series)
        body = "".join(f'<tr><th scope="row">{esc(xs.get("readout_labels", xs["labels"])[i])}</th>' + "".join(f"<td>{esc(fmt(s, i))}</td>" for s in series) + "</tr>" for i in range(n))
        table = (f'<details class="data"><summary>Data table</summary><div class="scroll"><table><thead><tr><th scope="col">{esc(xs.get("title", ""))}</th>{head}</tr></thead>'
                 f"<tbody>{body}</tbody></table></div></details>")
    if stepped:
        return walk(fid, svg, steps, key, table, start=spec.get("start"))
    return plain(fid, svg, spec.get("caption", ""), key, table)


# ---------------------------------------------------------------- inline

def inline(src, out, font=None, font_name="Brand"):
    doc = Path(src).read_text()
    css, js = (ASSETS / "kit.css").read_text(), (ASSETS / "kit.js").read_text()
    if font:
        data = base64.b64encode(Path(font).read_bytes()).decode()
        fmt = {"woff2": "woff2", "woff": "woff", "otf": "opentype"}.get(Path(font).suffix[1:], "truetype")
        css = (f"@font-face{{font-family:'{font_name}';font-weight:300 700;font-display:swap;src:url(data:font/{Path(font).suffix[1:]};base64,{data}) format('{fmt}')}}\n"
               + css + f"\n:root{{--font:'{font_name}',Arial,sans-serif}}\n")
    doc, a = re.subn(r'<link[^>]*href="kit\.css"[^>]*>', lambda _: f"<style>{css}</style>", doc)
    doc, b = re.subn(r'<script[^>]*src="kit\.js"[^>]*>\s*</script>', lambda _: f"<script>{js}</script>", doc)
    if (a, b) != (1, 1):
        sys.exit('expected exactly one <link rel="stylesheet" href="kit.css"> and one <script src="kit.js"></script>')
    remote = re.findall(r'<(?:link|script|img|iframe|source)\b[^>]*(?:src|href)="(?:https?:)?//[^"]+"', doc) + re.findall(r'url\((?:["\']?)(?:https?:)?//', doc)
    if remote:
        sys.exit("remote assets found; inline or remove them: " + "; ".join(remote[:3]))
    if re.search(r"\b(?:fetch|XMLHttpRequest|localStorage|sessionStorage)\b", doc.replace(js, "")):
        warn("page script uses network or storage APIs; a standalone walkthrough should not")
    Path(out).write_text(doc)
    print(f"wrote {out} ({len(doc.encode()) // 1024} KB)")


def main(argv):
    if len(argv) < 3 or argv[1] not in ("flow", "chart", "inline"):
        sys.exit(__doc__)
    if argv[1] == "inline":
        font = argv[argv.index("--font") + 1] if "--font" in argv else None
        name = argv[argv.index("--font-name") + 1] if "--font-name" in argv else "Brand"
        return inline(argv[2], argv[3], font, name)
    spec = json.loads(Path(argv[2]).read_text())
    print({"flow": flow, "chart": chart}[argv[1]](spec))


if __name__ == "__main__":
    main(sys.argv)
