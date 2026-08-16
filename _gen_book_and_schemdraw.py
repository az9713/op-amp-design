#!/usr/bin/env python3
"""Option 2: crop Roberge PDF figures. Option 3: schemdraw IEEE SVGs."""
from __future__ import annotations

from pathlib import Path

import pymupdf
import schemdraw
import schemdraw.elements as elm

ROOT = Path(__file__).resolve().parent
PDF = ROOT / "op_amps_roberge.pdf"
BOOK = ROOT / "figures" / "book"
ENG = ROOT / "figures" / "schemdraw"
BOOK.mkdir(parents=True, exist_ok=True)
ENG.mkdir(parents=True, exist_ok=True)

# First page that actually shows each figure (1-based PDF page)
FIGURES = [
    ("fig-1.2", "Figure 1.2a/b — inverter / noninverter", 9),
    ("fig-1.4", "Figure 1.4 — weighted summer", 13),
    ("fig-5.3", "Figure 5.3 — voltage regulator plant", 119),
    ("fig-7.4", "Figure 7.4 — differential pair", 180),
    ("fig-7.10", "Figure 7.10 — equal-VBE collector pot", 186),
    ("fig-8.8", "Figure 8.8 — two-stage core", 215),
    ("fig-8.13", "Figure 8.13 — current-source load", 220),
    ("fig-8.27", "Figure 8.27 — complementary output", 231),
    ("fig-10.9", "Figure 10.9 — current repeater", 269),
    ("fig-11.18", "Figure 11.18 — precision rectifier", 313),
    ("fig-12.1", "Figure 12.1 — Wien bridge", 330),
    ("fig-12.7", "Figure 12.7 — Schmitt trigger", 337),
    ("fig-12.8", "Figure 12.8 — function-generator waveforms", 338),
    ("fig-12.13", "Figure 12.13 — Butterworth analog computer", 343),
    ("fig-12.17", "Figure 12.17 — three-mode integrator", 348),
    ("fig-13.1", "Figure 13.1 — input lag", 372),
    ("fig-13.19", "Figure 13.19 — two-pole compensation", 390),
]


def extract_book_pages() -> list[tuple[str, str, str]]:
    doc = pymupdf.open(PDF)
    out = []
    mat = pymupdf.Matrix(1.8, 1.8)
    for slug, title, page_no in FIGURES:
        page = doc[page_no - 1]
        pix = page.get_pixmap(matrix=mat, alpha=False)
        dest = BOOK / f"{slug}.png"
        pix.save(dest)
        out.append((slug, title, f"figures/book/{slug}.png"))
        print("book", dest.name, pix.width, "x", pix.height)
    return out


def _save(d: schemdraw.Drawing, name: str) -> str:
    path = ENG / f"{name}.svg"
    d.save(str(path))
    print("schemdraw", path.name)
    return f"figures/schemdraw/{name}.svg"


def draw_inverter() -> str:
    with schemdraw.Drawing(show=False, file=str(ENG / "inv.svg")) as d:
        d.config(fontsize=11)
        d += elm.Dot(open=True).label("Vi")
        d += elm.Resistor().right().label("Z1")
        d += elm.Dot().label("∑", loc="bottom")
        d.push()
        d += elm.Line().up().length(1.2)
        d += elm.Resistor().right().label("Z2")
        d += elm.Line().down().length(1.2)
        d += elm.Dot()
        d.pop()
        d += elm.Line().right().length(0.4)
        op = elm.Opamp(sign=True).anchor("in1")
        d += op
        d += elm.Ground().at(op.in2)
        d += elm.Line().at(op.out).right().length(0.8).label("Vo  jack INV", loc="right")
    return "figures/schemdraw/inv.svg"


def draw_noninv() -> str:
    with schemdraw.Drawing(show=False, file=str(ENG / "noninv.svg")) as d:
        d.config(fontsize=11)
        d += elm.Dot(open=True).label("Vi")
        d += elm.Line().right()
        op = elm.Opamp(sign=True).anchor("in2")
        d += op
        d += elm.Line().left().at(op.in1).length(0.5)
        d += elm.Dot()
        d.push()
        d += elm.Resistor().down().label("Z1")
        d += elm.Ground()
        d.pop()
        d += elm.Resistor().right().label("Z2")
        d += elm.Line().toy(op.out)
        d += elm.Dot()
        d += elm.Line().right().at(op.out).length(0.6).label("Vo", loc="right")
    return "figures/schemdraw/noninv.svg"


def draw_summer() -> str:
    with schemdraw.Drawing(show=False, file=str(ENG / "sum.svg")) as d:
        d.config(fontsize=11)
        d += elm.Dot(open=True).label("Vi1")
        d += elm.Resistor().right().label("Zi1")
        d += elm.Dot().label("∑", loc="bottom")
        n = d.here
        d.push()
        d += elm.Line().up().length(1.4)
        d += elm.Resistor().left().label("Zi2")
        d += elm.Dot(open=True).label("Vi2", loc="left")
        d.pop()
        d.push()
        d += elm.Line().up().length(2.4)
        d += elm.Resistor().right().label("Zf")
        fb = d.here
        d.pop()
        d += elm.Line().right().length(0.4)
        op = elm.Opamp(sign=True).anchor("in1")
        d += op
        d += elm.Ground().at(op.in2)
        d += elm.Line().at(op.out).right().length(0.5)
        d += elm.Dot()
        d += elm.Line().toy(fb)
        d += elm.Line().tox(fb)
        d += elm.Line().at(op.out).right().length(1.4).label("Vo  jack SUM", loc="right")
    return "figures/schemdraw/sum.svg"


def draw_integrator() -> str:
    with schemdraw.Drawing(show=False, file=str(ENG / "int.svg")) as d:
        d.config(fontsize=11)
        d += elm.Dot(open=True).label("Vi")
        d += elm.Resistor().right().label("R")
        d += elm.Dot()
        d.push()
        d += elm.Line().up().length(1.2)
        d += elm.Capacitor().right().label("C")
        d += elm.Line().down().length(1.2)
        d += elm.Dot()
        d.pop()
        d += elm.Line().right().length(0.4)
        op = elm.Opamp(sign=True).anchor("in1")
        d += op
        d += elm.Ground().at(op.in2)
        d += elm.Line().at(op.out).right().length(0.8).label("Vo  jack INT", loc="right")
    return "figures/schemdraw/int.svg"


def draw_schmitt() -> str:
    with schemdraw.Drawing(show=False, file=str(ENG / "schmitt.svg")) as d:
        d.config(fontsize=11)
        d += elm.Dot(open=True).label("vI")
        d += elm.Resistor().right().label("R1")
        d += elm.Dot()
        d.push()
        d += elm.Line().up().length(1.2)
        d += elm.Resistor().right().label("R2")
        d += elm.Line().down().length(1.2)
        d += elm.Dot()
        d.pop()
        d += elm.Line().right().length(0.4)
        op = elm.Opamp(sign=True).anchor("in2")  # + input
        d += op
        d += elm.Ground().at(op.in1)
        d += elm.Line().at(op.out).right().length(0.8).label("vo  ±VM", loc="right")
    return "figures/schemdraw/schmitt.svg"


def draw_diffpair() -> str:
    with schemdraw.Drawing(show=False, file=str(ENG / "diffpair.svg")) as d:
        d.config(fontsize=11)
        # Q1
        q1 = elm.BjtNpn().reverse().label("Q1")
        d += q1
        d += elm.Line().left().at(q1.base).length(0.6).label("vI1 −", loc="left")
        d += elm.Resistor().up().at(q1.collector).label("RL")
        d += elm.Line().right().length(2.4).label("+V", loc="right")
        top = d.here
        d += elm.Line().down().at(q1.emitter).length(0.6)
        d += elm.Dot()
        emit = d.here
        d += elm.Line().right().length(2.4)
        d += elm.Dot()
        d.push()
        d += elm.Resistor().down().label("RE")
        d += elm.Line().down().length(0.2).label("−V2", loc="bottom")
        d.pop()
        q2 = elm.BjtNpn().anchor("emitter").label("Q2")
        d += q2
        d += elm.Line().right().at(q2.base).length(0.6).label("+ vI2", loc="right")
        d += elm.Resistor().up().at(q2.collector).label("RL")
        d += elm.Line().up().toy(top)
    return "figures/schemdraw/diffpair.svg"


def draw_plant() -> str:
    with schemdraw.Drawing(show=False, file=str(ENG / "plant.svg")) as d:
        d.config(fontsize=11)
        d += elm.Dot(open=True).label("VR")
        d += elm.Line().right()
        op = elm.Opamp(sign=True).anchor("in2")
        d += op
        d += elm.Line().left().at(op.in1).length(0.8)
        d += elm.Dot()
        sense = d.here
        d += elm.Line().at(op.out).right().length(0.4)
        q = elm.BjtNpn().anchor("base").label("NPN")
        d += q
        d += elm.Line().up().at(q.collector).length(0.8).label("Vu", loc="right")
        d += elm.Line().down().at(q.emitter).length(0.4)
        d += elm.Resistor().down().label("R")
        d += elm.Dot().label("Vl", loc="right")
        out = d.here
        d.push()
        d += elm.Resistor().down().label("RL")
        d += elm.Ground()
        d.pop()
        d.push()
        d += elm.Line().right().length(0.8)
        d += elm.Capacitor().down().label("CL")
        d += elm.Ground()
        d.pop()
        d += elm.Line().at(out).left().tox(sense)
        d += elm.Line().toy(sense)
    return "figures/schemdraw/plant.svg"


def draw_threemode() -> str:
    with schemdraw.Drawing(show=False, file=str(ENG / "threemode.svg")) as d:
        d.config(fontsize=11)
        d += elm.Dot(open=True).label("vB")
        d += elm.Resistor().right().label("R1")
        d += elm.Switch().right().label("①", loc="top")
        d += elm.Dot()
        d.push()
        d += elm.Line().up().length(1.2)
        d += elm.Capacitor().right().label("C")
        d += elm.Line().down().length(1.2)
        d += elm.Dot()
        d.pop()
        d += elm.Line().right().length(0.4)
        op = elm.Opamp(sign=True).anchor("in1")
        d += op
        d += elm.Ground().at(op.in2)
        d += elm.Line().at(op.out).right().length(0.8).label("Vo", loc="right")
    return "figures/schemdraw/threemode.svg"


def draw_lag() -> str:
    with schemdraw.Drawing(show=False, file=str(ENG / "lag.svg")) as d:
        d.config(fontsize=11)
        d += elm.Dot(open=True).label("Vi")
        d += elm.Resistor().right().label("Z1")
        d += elm.Dot()
        d.push()
        d += elm.Resistor().down().label("Rlag")
        d += elm.Capacitor().down().label("Clag")
        d += elm.Ground()
        d.pop()
        d.push()
        d += elm.Line().up().length(1.2)
        d += elm.Resistor().right().label("Z2")
        d += elm.Line().down().length(1.2)
        d += elm.Dot()
        d.pop()
        d += elm.Line().right().length(0.4)
        op = elm.Opamp(sign=True).anchor("in1")
        d += op
        d += elm.Ground().at(op.in2)
        d += elm.Line().at(op.out).right().length(0.8).label("Vo", loc="right")
    return "figures/schemdraw/lag.svg"


ENGINE = [
    ("Inverting amplifier — socket INV", "Figure 1.2a · §1.2.1", draw_inverter),
    ("Noninverting amplifier", "Figure 1.2b · §1.2.2", draw_noninv),
    ("Weighted summer — socket SUM", "Figure 1.4 · §1.2.3", draw_summer),
    ("Inverting integrator — socket INT", "§1.2.3 · Z2 = C", draw_integrator),
    ("Schmitt trigger", "Figure 12.7a · §12.2.1", draw_schmitt),
    ("Differential pair", "Figure 7.4 · §7.3.1", draw_diffpair),
    ("Voltage regulator plant", "Figure 5.3a · §5.2.2", draw_plant),
    ("Three-mode integrator (operate path)", "Figure 12.17 · §12.3.3", draw_threemode),
    ("Input lag on a stock inverter", "Figure 13.1 · §13.2.1", draw_lag),
]


def write_html(book, engine_rows: list[tuple[str, str, str]]) -> None:
    cards_book = []
    for slug, title, src in book:
        cards_book.append(
            f"""    <article class="card">
      <h3>{title}</h3>
      <p class="tag">from op_amps_roberge.pdf · CC BY-NC-SA 4.0</p>
      <img class="fig" src="{src}" alt="{title}">
    </article>"""
        )
    cards_eng = []
    for title, tag, src in engine_rows:
        cards_eng.append(
            f"""    <article class="card">
      <h3>{title}</h3>
      <p class="tag">{tag} · schemdraw IEEE</p>
      <img class="fig svg" src="{src}" alt="{title}">
    </article>"""
        )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Roberge one-box — book figures and schemdraw</title>
  <link rel="stylesheet" href="design-system/colors_and_type.css">
  <style>
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; }}
    body {{ background: var(--book); color: var(--slate); padding-bottom: 48px; }}
    .deck {{ max-width: 880px; margin: 0 auto; padding: 0 24px 48px; }}
    @media (min-width: 900px) {{ .deck {{ padding: 0 48px 64px; }} }}
    .top {{ display: flex; align-items: center; gap: 10px; padding: 20px 0 8px; }}
    .top img {{ width: 22px; height: 22px; }}
    h1.display {{ margin: 8px 0 12px; font-size: clamp(32px, 6vw, 48px); }}
    .lede {{ margin: 0 0 16px; max-width: 42rem; }}
    nav.jump {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 28px; }}
    nav.jump a {{
      font-family: var(--font-sans); font-size: 13px; padding: 6px 10px;
      border: 1px solid var(--hairline); border-radius: var(--r-sm);
      background: var(--bg-elev); text-decoration: none; color: var(--fg);
    }}
    h2 {{ margin: 40px 0 8px; }}
    .card {{
      background: var(--bg-elev); border: 1px solid var(--hairline);
      border-radius: var(--r-md); padding: 16px; margin: 0 0 16px;
    }}
    .card h3 {{ font-family: var(--font-serif); font-weight: 400; font-size: 20px; margin: 0 0 4px; }}
    .tag {{ font-family: var(--font-mono); font-size: 11px; color: var(--crail-deep); margin: 0 0 12px; }}
    img.fig {{ width: 100%; height: auto; display: block; background: #fff; border: 1px solid var(--hairline); border-radius: var(--r-xs); }}
    img.svg {{ padding: 12px; }}
    .back {{ font-size: 14px; }}
  </style>
</head>
<body>
  <div class="deck">
    <header>
      <div class="top">
        <img src="design-system/anthropic-mark.svg" alt="">
        <p class="eyebrow">Visual guide · two other methods</p>
      </div>
      <h1 class="display">Book pages, then a real engine</h1>
      <p class="lede">Method 1 (hand SVG) is still in <a href="schematics.html">schematics.html</a>. This page is method 2 (the Roberge pages) and method 3 (schemdraw, IEEE symbols, auto-routed wires).</p>
      <nav class="jump">
        <a href="#book">2 · book figures</a>
        <a href="#engine">3 · schemdraw</a>
        <a href="schematics.html">1 · hand SVG</a>
        <a href="capstone.html">Build log</a>
      </nav>
    </header>

    <h2 id="book">Method 2 — the textbook pages</h2>
    <p class="lede">These are the LibreTexts pages that contain the cited figures. Use them as the electrical source of truth.</p>
{chr(10).join(cards_book)}

    <h2 id="engine">Method 3 — schemdraw IEEE</h2>
    <p class="lede">Same topologies, drawn by a schematic library. Wires attach to pins because the library owns the symbols.</p>
{chr(10).join(cards_eng)}

    <p class="back"><a href="capstone.html">Back to the build log</a></p>
  </div>
</body>
</html>
"""
    dest = ROOT / "schematics-other.html"
    dest.write_text(html, encoding="utf-8")
    print("wrote", dest)


def main() -> None:
    book = extract_book_pages()
    rows = []
    for title, tag, fn in ENGINE:
        src = fn()
        rows.append((title, tag, src))
    write_html(book, rows)


if __name__ == "__main__":
    main()
