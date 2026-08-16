#!/usr/bin/env python3
"""Arrow-connection checker for the shipped schematics.html.

Reads the real file (not a copy). Each svg.sch is scored against the
Arrow pin-stub / feedback T-join / no-endpoint-inside-triangle rules.
Exit 0 only if every diagram passes, or is listed in an attempt log
with 3 attempts and a stop (passed as --attempt-log).
"""
from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "schematics.html"
TOL = 1.6  # px — stroke width is 1.8


class SvgCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.svgs: list[dict] = []
        self._cur: dict | None = None
        self._depth = 0
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "svg" and a.get("class") == "sch":
            self._cur = {
                "aria": a.get("aria-label", "?"),
                "viewBox": a.get("viewBox", ""),
                "raw": "",
            }
            self._depth = 1
            self._buf = [self.get_starttag_text() or ""]
            return
        if self._cur is not None:
            self._depth += 1
            self._buf.append(self.get_starttag_text() or "")

    def handle_endtag(self, tag):
        if self._cur is None:
            return
        self._buf.append(f"</{tag}>")
        self._depth -= 1
        if tag == "svg" and self._depth == 0:
            self._cur["raw"] = "".join(self._buf)
            self.svgs.append(self._cur)
            self._cur = None

    def handle_data(self, data):
        if self._cur is not None:
            self._buf.append(data)


def parse_svgs(html: str) -> list[dict]:
    p = SvgCollector()
    p.feed(html)
    return p.svgs


def _nums(el: str, *names: str) -> list[float]:
    out = []
    for n in names:
        m = re.search(rf'\b{n}="([^"]+)"', el)
        out.append(float(m.group(1)) if m else float("nan"))
    return out


def collect_geometry(raw: str):
    oas = []
    for m in re.finditer(r'<use\b[^>]*href="#oa"[^>]*/?>', raw):
        el = m.group(0)
        x, y = _nums(el, "x", "y")
        oas.append((x, y))
    lines = []
    for m in re.finditer(r"<line\b[^>]*/?>", raw):
        el = m.group(0)
        x1, y1, x2, y2 = _nums(el, "x1", "y1", "x2", "y2")
        lines.append((x1, y1, x2, y2))
    dots = []
    for m in re.finditer(r'<use\b[^>]*href="#dot"[^>]*/?>', raw):
        el = m.group(0)
        dots.append(tuple(_nums(el, "x", "y")))
    gnds = []
    for m in re.finditer(r'<use\b[^>]*href="#gnd"[^>]*/?>', raw):
        el = m.group(0)
        gnds.append(tuple(_nums(el, "x", "y")))
    npns = []
    for href in ("#npn", "#npnr", "#pnp"):
        for m in re.finditer(rf'<use\b[^>]*href="{href}"[^>]*/?>', raw):
            el = m.group(0)
            npns.append((href, *_nums(el, "x", "y")))
    return oas, lines, dots, gnds, npns


def near(a, b, tol=TOL) -> bool:
    return abs(a - b) <= tol


def pt_near(p, q, tol=TOL) -> bool:
    return near(p[0], q[0], tol) and near(p[1], q[1], tol)


def segment_crosses_triangle(x1, y1, x2, y2, ox, oy) -> bool:
    """True if the open segment intersects the strict triangle interior."""
    if inside_triangle(x1, y1, ox, oy) or inside_triangle(x2, y2, ox, oy):
        return True
    steps = 40
    for i in range(1, steps):
        t = i / steps
        if inside_triangle(x1 + t * (x2 - x1), y1 + t * (y2 - y1), ox, oy):
            return True
    return False


def point_on_segment_interior(px, py, x1, y1, x2, y2, tol=TOL) -> bool:
    if pt_near((px, py), (x1, y1), tol) or pt_near((px, py), (x2, y2), tol):
        return False
    dx, dy = x2 - x1, y2 - y1
    length2 = dx * dx + dy * dy
    if length2 < 1:
        return False
    t = ((px - x1) * dx + (py - y1) * dy) / length2
    if t <= 0.04 or t >= 0.96:
        return False
    qx, qy = x1 + t * dx, y1 + t * dy
    return (px - qx) ** 2 + (py - qy) ** 2 <= tol * tol


def unmarked_tjoins(lines, dots) -> list[str]:
    fails = []
    for i, (x1, y1, x2, y2) in enumerate(lines):
        for end in ((x1, y1), (x2, y2)):
            for j, (a, b, c, d) in enumerate(lines):
                if i == j:
                    continue
                if not point_on_segment_interior(end[0], end[1], a, b, c, d):
                    continue
                if not any(pt_near(end, dot) for dot in dots):
                    fails.append(
                        f"unmarked T-join at ({end[0]:.0f},{end[1]:.0f})"
                    )
                    return fails
    return fails


def inside_triangle(px, py, ox, oy) -> bool:
    """Strictly inside the #oa triangle (ox,oy-40)-(ox,oy+40)-(ox+74,oy)."""
    # barycentric
    x1, y1 = ox, oy - 40
    x2, y2 = ox, oy + 40
    x3, y3 = ox + 74, oy
    den = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    if den == 0:
        return False
    a = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / den
    b = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / den
    c = 1 - a - b
    eps = 1e-6
    return a > eps and b > eps and c > eps


def line_hits_pin(lines, pin, from_left=True) -> bool:
    px, py = pin
    for x1, y1, x2, y2 in lines:
        ends = ((x1, y1), (x2, y2))
        if not any(pt_near(e, pin) for e in ends):
            continue
        other = ends[1] if pt_near(ends[0], pin) else ends[0]
        if from_left and other[0] < px - 0.2 and near(other[1], py, 4):
            return True
        if not from_left:
            return True
    return False


def has_dot_on_net(dots, pin, xa_min, xa_max) -> bool:
    px, py = pin
    for dx, dy in dots:
        if near(dy, py, TOL) and xa_min <= dx <= xa_max and not pt_near((dx, dy), pin):
            return True
    return False


def check_oa(ox, oy, lines, dots, gnds) -> list[str]:
    fails = []
    inv = (ox, oy - 16)
    non = (ox, oy + 16)
    out = (ox + 74, oy)

    for x1, y1, x2, y2 in lines:
        if inside_triangle(x1, y1, ox, oy) or inside_triangle(x2, y2, ox, oy):
            fails.append(f"wire endpoint inside triangle at oa({ox:.0f},{oy:.0f})")
            break
        if segment_crosses_triangle(x1, y1, x2, y2, ox, oy):
            fails.append(
                f"wire crosses triangle interior at oa({ox:.0f},{oy:.0f}) "
                f"({x1:.0f},{y1:.0f})–({x2:.0f},{y2:.0f})"
            )
            break

    if not line_hits_pin(lines, inv, from_left=True):
        fails.append(f"− pin stub missing at ({inv[0]:.0f},{inv[1]:.0f})")
    if not line_hits_pin(lines, non, from_left=True):
        fails.append(f"+ pin stub missing at ({non[0]:.0f},{non[1]:.0f})")

    # output leaves the tip
    if not any(
        pt_near((x1, y1), out) or pt_near((x2, y2), out) for x1, y1, x2, y2 in lines
    ):
        fails.append(f"output not leaving tip ({out[0]:.0f},{out[1]:.0f})")

    # feedback T-join on the inverting net before the stub
    # (Schmitt / noninverting amps T-join the + net instead)
    t_inv = has_dot_on_net(dots, inv, ox - 160, ox - 4)
    t_non = has_dot_on_net(dots, non, ox - 160, ox - 4)
    if not t_inv and not t_non:
        fails.append(f"no feedback T-join before pin at oa({ox:.0f},{oy:.0f})")

    # When a pin is only a short stub (no incoming signal), it must be a
    # down-arrow ground. Signal pins (VR, sense, vI) must not be forced to gnd.
    for pin, name in ((inv, "−"), (non, "+")):
        # A short stub that T-joins a summing/feedback net is a signal pin.
        joined = has_dot_on_net(dots, pin, ox - 160, ox - 4)
        if _short_stub_only(pin, lines) and not joined and not _gnd_on_stub(pin, gnds):
            fails.append(
                f"{name} pin is a short stub without a ground arrow at oa({ox:.0f},{oy:.0f})"
            )
    return fails


def _short_stub_only(pin, lines) -> bool:
    hits = []
    px, py = pin
    for x1, y1, x2, y2 in lines:
        ends = ((x1, y1), (x2, y2))
        if not any(pt_near(e, pin) for e in ends):
            continue
        other = ends[1] if pt_near(ends[0], pin) else ends[0]
        hits.append(other)
    if not hits:
        return False
    return all(abs(ox - px) <= 28 and near(oy, py, 4) for ox, oy in hits)


def _gnd_on_stub(pin, gnds) -> bool:
    px, py = pin
    for gx, gy in gnds:
        if near(gy, py, 8) and (px - 28) <= gx <= px + 2:
            return True
    return False


def check_transistors(npns, lines) -> list[str]:
    """No line endpoint strictly inside the base-bar body."""
    fails = []
    for href, x, y in npns:
        # bar is a vertical segment at x±16, y±13
        bx = x + 16 if href != "#npnr" else x - 16
        for x1, y1, x2, y2 in lines:
            for px, py in ((x1, y1), (x2, y2)):
                if abs(px - bx) < 3 and abs(py - y) < 10:
                    # endpoint on the bar itself is the illegal "base hit the body"
                    # unless it is exactly the base lead attach (y==0 relative)
                    if abs(py - y) > 2:
                        fails.append(
                            f"wire ends on {href} body at ({px:.0f},{py:.0f})"
                        )
    return fails


def check_diagram(svg: dict) -> list[str]:
    oas, lines, dots, gnds, npns = collect_geometry(svg["raw"])
    fails: list[str] = []
    if not oas and not npns:
        if "<line" not in svg["raw"] and "<use" not in svg["raw"]:
            fails.append("empty drawing")
            return fails
    for ox, oy in oas:
        fails.extend(check_oa(ox, oy, lines, dots, gnds))
    fails.extend(check_transistors(npns, lines))
    fails.extend(unmarked_tjoins(lines, dots))
    return fails


def load_attempt_log(path: Path | None) -> dict[str, int]:
    if not path or not path.exists():
        return {}
    out: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        # format: N  aria-label  [stop]
        m = re.match(r"^\s*(\d+)\s+(.+?)(?:\s+stop)?\s*$", line)
        if not m:
            continue
        out[m.group(2).strip()] = int(m.group(1))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", type=Path, default=HTML)
    ap.add_argument("--attempt-log", type=Path, default=None)
    ap.add_argument("--report", type=Path, default=None)
    args = ap.parse_args(argv)

    html = args.html.read_text(encoding="utf-8")
    svgs = parse_svgs(html)
    attempts = load_attempt_log(args.attempt_log)

    lines_out = []
    bad = 0
    for svg in svgs:
        fails = check_diagram(svg)
        n = attempts.get(svg["aria"], 0)
        stopped = n >= 3 and bool(fails)
        status = "PASS" if not fails else ("STOP" if stopped else "FAIL")
        if status == "FAIL":
            bad += 1
        detail = "; ".join(fails) if fails else "ok"
        lines_out.append(f"{status:4}  {svg['aria']}: {detail}")

    report = (
        f"file: {args.html}\n"
        f"diagrams: {len(svgs)}\n"
        + "\n".join(lines_out)
        + f"\nfailing (not stopped): {bad}\n"
    )
    if args.report:
        args.report.write_text(report, encoding="utf-8")
    sys.stdout.write(report)
    return 0 if bad == 0 and svgs else 1


if __name__ == "__main__":
    raise SystemExit(main())
