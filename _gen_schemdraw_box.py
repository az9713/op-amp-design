#!/usr/bin/env python3
"""Redraw every schematics.html diagram with schemdraw. Writes a NEW html only."""
from __future__ import annotations

from pathlib import Path

import schemdraw
import schemdraw.elements as elm

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figures" / "schemdraw-box"
OUT.mkdir(parents=True, exist_ok=True)

INK = "#1F1E1D"
NEW = "#D97757"
EMPTY = "#B4B3AC"

elm.style(elm.STYLE_IEEE)


def save(name: str, d: schemdraw.Drawing) -> str:
    path = OUT / f"{name}.svg"
    d.save(str(path))
    print("wrote", path.name)
    return f"figures/schemdraw-box/{name}.svg"


# ── building blocks ──────────────────────────────────────────

def inverter(d, *, label="INV", z1="Z1", z2="Z2", vin="Vi", vout="Vo", color=INK):
    d += elm.Dot(open=True, color=color).label(vin)
    d += elm.Resistor(color=color).right().label(z1)
    d += elm.Dot(color=color)
    d.push()
    d += elm.Line(color=color).up().length(1.15)
    d += elm.Resistor(color=color).right().label(z2)
    d += elm.Line(color=color).down().length(1.15)
    d += elm.Dot(color=color)
    d.pop()
    d += elm.Line(color=color).right().length(0.35)
    op = elm.Opamp(sign=True, color=color).anchor("in1").label(label, loc="top")
    d += op
    d += elm.Line(color=color).left().at(op.in2).length(0.35)
    d += elm.Ground(color=color)
    d += elm.Line(color=color).at(op.out).right().length(0.8).label(vout, loc="right")
    return op


def integrator(d, *, label="INT", vin="Vi", vout="Vo", color=INK):
    d += elm.Dot(open=True, color=color).label(vin)
    d += elm.Resistor(color=color).right().label("R")
    d += elm.Dot(color=color)
    d.push()
    d += elm.Line(color=color).up().length(1.15)
    d += elm.Capacitor(color=color).right().label("C")
    d += elm.Line(color=color).down().length(1.15)
    d += elm.Dot(color=color)
    d.pop()
    d += elm.Line(color=color).right().length(0.35)
    op = elm.Opamp(sign=True, color=color).anchor("in1").label(label, loc="top")
    d += op
    d += elm.Line(color=color).left().at(op.in2).length(0.35)
    d += elm.Ground(color=color)
    d += elm.Line(color=color).at(op.out).right().length(0.8).label(vout, loc="right")
    return op


def summer(d, *, label="SUM", color=INK):
    d += elm.Dot(open=True, color=color).label("Vi1")
    d += elm.Resistor(color=color).right().label("Zi1")
    d += elm.Dot(color=color)
    n = d.here
    d.push()
    d += elm.Line(color=color).up().length(1.35)
    d += elm.Resistor(color=color).left().label("Zi2")
    d += elm.Dot(open=True, color=color).label("Vi2", loc="left")
    d.pop()
    d.push()
    d += elm.Line(color=color).up().length(2.4)
    d += elm.Resistor(color=color).right().label("Zf")
    fb = d.here
    d.pop()
    d += elm.Line(color=color).right().length(0.35)
    op = elm.Opamp(sign=True, color=color).anchor("in1").label(label, loc="top")
    d += op
    d += elm.Line(color=color).left().at(op.in2).length(0.35)
    d += elm.Ground(color=color)
    d += elm.Line(color=color).at(op.out).right().length(0.4)
    d += elm.Dot(color=color)
    d += elm.Line(color=color).toy(fb)
    d += elm.Line(color=color).tox(fb)
    d += elm.Line(color=color).at(op.out).right().length(1.2).label("Vo", loc="right")
    return op


def schmitt(d, *, label="SCHMITT", color=INK):
    d += elm.Dot(open=True, color=color).label("vI")
    d += elm.Resistor(color=color).right().label("R1")
    d += elm.Dot(color=color)
    d.push()
    d += elm.Line(color=color).up().length(1.15)
    d += elm.Resistor(color=color).right().label("R2")
    d += elm.Line(color=color).down().length(1.15)
    d += elm.Dot(color=color)
    d.pop()
    d += elm.Line(color=color).right().length(0.35)
    op = elm.Opamp(sign=True, color=color).anchor("in2").label(label, loc="top")
    d += op
    d += elm.Line(color=color).left().at(op.in1).length(0.35)
    d += elm.Ground(color=color)
    d += elm.Line(color=color).at(op.out).right().length(0.8).label("vB ±VM", loc="right")
    return op


def plant(d, *, label="PLANT", color=INK):
    d += elm.Dot(open=True, color=color).label("VR")
    d += elm.Line(color=color).right()
    op = elm.Opamp(sign=True, color=color).anchor("in2").label(label, loc="top")
    d += op
    d += elm.Line(color=color).left().at(op.in1).length(0.9)
    d += elm.Dot(color=color)
    sense = d.here
    d += elm.Line(color=color).at(op.out).right().length(0.45)
    q = elm.BjtNpn(color=color).anchor("base").label("NPN")
    d += q
    d += elm.Line(color=color).up().at(q.collector).length(0.7).label("Vu", loc="right")
    d += elm.Line(color=color).down().at(q.emitter).length(0.35)
    d += elm.Resistor(color=color).down().label("R")
    d += elm.Dot(color=color).label("Vl", loc="right")
    out = d.here
    d.push()
    d += elm.Resistor(color=color).down().label("RL")
    d += elm.Ground(color=color)
    d.pop()
    d.push()
    d += elm.Line(color=color).right().length(0.9)
    d += elm.Capacitor(color=color).down().label("CL")
    d += elm.Ground(color=color)
    d.pop()
    d += elm.Line(color=color).at(out).left().tox(sense)
    d += elm.Line(color=color).toy(sense)
    return op


def empty(d, label):
    d += elm.Rect(w=2.6, h=1.8, lw=1.1, ls="--", color=EMPTY, fill="none").label(
        label + "\nempty", color=EMPTY
    )


# ── week / module drawings ───────────────────────────────────

def w1():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        summer(d, color=NEW)
        d.move(3.2, 0)
        integrator(d, label="INT1", color=NEW)
        d.move(3.2, 0)
        empty(d, "INT2")
        d.move(-10.5, -4.6)
        inverter(d, color=NEW)
        d.move(6.5, 0)
        empty(d, "INT3")
        d += elm.Label().at((0, 3.2)).label("Week 1 · three ICs land", color=NEW)
    return save("w1-chassis", d)


def w2():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        op_s = summer(d, color=INK)
        d.move(3.2, 0)
        op_i = integrator(d, label="INT1", color=INK)
        d.move(3.2, 0)
        empty(d, "INT2")
        # coral patch: INT1 out back toward SUM (shown as a labeled loop)
        d += elm.Line(color=NEW).at(op_i.out).up().length(1.6)
        d += elm.Line(color=NEW).left().length(8.2)
        d += elm.Arrow(color=NEW).down().length(0.5).label("patch  ẋ = −x", loc="top", color=NEW)
        d.move(-3.5, -6.2)
        inverter(d, color=INK)
        d.move(6.5, 0)
        empty(d, "INT3")
        d += elm.Label().at((0, 4.4)).label("Week 2 = week 1 + one patch", color=NEW)
    return save("w2-chassis", d)


def w3():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        summer(d, color=INK)
        d.move(3.2, 0)
        op = integrator(d, label="INT1", color=INK)
        d += elm.Capacitor(color=NEW).at(op.n1).down().label("Cc", color=NEW)
        d += elm.Line(color=NEW).tox(op.n2)
        d.move(3.2, 0)
        empty(d, "INT2")
        d.move(-10.5, -5.0)
        inverter(d, color=INK)
        d.move(6.5, 0)
        empty(d, "INT3")
        d += elm.Label().at((0, 3.4)).label("Week 3 = week 2 + default Cc", color=NEW)
    return save("w3-chassis", d)


def w4():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        summer(d, color=INK)
        d.move(3.0, 0)
        integrator(d, label="INT1", vout="ẋ", color=INK)
        d.move(3.0, 0)
        op2 = integrator(d, label="INT2", vin="ẋ", vout="x", color=NEW)
        d += elm.Line(color=NEW).at(op2.out).up().length(1.5)
        d += elm.Line(color=NEW).left().length(11.5)
        d += elm.Arrow(color=NEW).down().length(0.45).label("SUM → INT1 → INT2 → SUM", color=NEW, loc="top")
        d.move(-8.0, -5.2)
        inverter(d, color=INK)
        d.move(6.5, 0)
        empty(d, "INT3")
        d += elm.Label().at((0, 4.2)).label("Week 4 = week 3 + INT2", color=NEW)
    return save("w4-chassis", d)


def w5():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        summer(d, color=INK)
        d.move(3.0, 0)
        integrator(d, label="INT1", color=INK)
        d.move(3.0, 0)
        integrator(d, label="INT2", color=INK)
        d.move(-8.0, -5.0)
        inverter(d, color=INK)
        d.move(6.5, 0)
        empty(d, "INT3")
        d.move(5.5, 4.5)
        plant(d, color=NEW)
        d += elm.Label().at((0, 8.5)).label("Week 5 = week 4 + Fig 5.3  ·  not patched together", color=NEW)
    return save("w5-chassis", d)


def w5_plant():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        plant(d, label="Fig 5.3", color=NEW)
    return save("w5-plant", d)


def w6():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        summer(d, color=INK)
        d.move(3.0, 0)
        integrator(d, label="INT1", color=INK)
        d.move(3.0, 0)
        integrator(d, label="INT2", color=INK)
        d.move(-8.0, -5.0)
        inverter(d, color=INK)
        d.move(5.5, 0)
        schmitt(d, color=NEW)
        d.move(3.2, 0)
        integrator(d, label="INT3", vin="vB", vout="vA", color=NEW)
        d += elm.Label().at((0, 8.6)).label("Week 6 = week 5 + Schmitt + INT3", color=NEW)
    return save("w6-chassis", d)


def w6_schmitt():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        schmitt(d, color=NEW)
    return save("w6-schmitt", d)


def w7():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        summer(d, color=INK)
        d.move(3.0, 0)
        d += elm.Rect(w=3.4, h=2.4, color=NEW, lw=1.4, fill="none").label(
            "INT1 socket\nFig 7.4 pair only\nC stays", color=NEW
        )
        d.move(4.2, 0)
        integrator(d, label="INT2", color=INK)
        d.move(-9.2, -5.0)
        inverter(d, color=INK)
        d.move(5.5, 0)
        schmitt(d, color=INK)
        d.move(3.2, 0)
        integrator(d, label="INT3", vin="vB", vout="vA", color=INK)
        d += elm.Label().at((0, 3.6)).label("Week 7 = week 6, INT1 IC pulled", color=NEW)
    return save("w7-chassis", d)


def w7_pair():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        q1 = elm.BjtNpn(color=NEW).reverse().label("Q1")
        d += q1
        d += elm.Line(color=NEW).left().at(q1.base).length(0.7).label("− in", loc="left")
        d += elm.Resistor(color=NEW).up().at(q1.collector).label("RL")
        d += elm.Vdd(color=NEW).label("+V")
        d += elm.Line(color=NEW).down().at(q1.emitter).length(0.55)
        d += elm.Dot(color=NEW)
        d += elm.Line(color=NEW).right().length(2.6)
        d += elm.Dot(color=NEW)
        d.push()
        d += elm.SourceI(color=NEW).down().reverse().label("I")
        d += elm.Vss(color=NEW).label("−V2")
        d.pop()
        q2 = elm.BjtNpn(color=NEW).anchor("emitter").label("Q2")
        d += q2
        d += elm.Line(color=NEW).right().at(q2.base).length(0.7).label("+ in", loc="right")
        d += elm.Resistor(color=NEW).up().at(q2.collector).label("RL")
        d += elm.Vdd(color=NEW)
        d += elm.Line(color=NEW).at(q1.collector).right().tox(q2.collector)
        d += elm.Gap().label("vo")
        d += elm.Capacitor(color=NEW).at(q1.base).down().length(2.2).label("C still on socket")
        d += elm.Line(color=NEW).right().tox(q2.collector)
        d += elm.Line(color=NEW).up().toy(q2.collector)
    return save("w7-int1", d)


def w7_710():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        d += elm.BjtNpn(color=INK).reverse().label("Q1")
        q1 = d.here
        d += elm.Resistor(color=INK).up().label("RL")
        d += elm.Line(color=NEW).right().length(2.8)
        pot_end = d.here
        d += elm.Resistor(color=INK).down().label("RL")
        d += elm.BjtNpn(color=INK).anchor("collector").label("Q2")
        d += elm.Potentiometer(color=NEW).at(pot_end).left().label("R  +Vc wiper", color=NEW)
        d += elm.Label().at((1.4, 3.2)).label("Fig 7.10 · pot in the collectors", color=NEW)
    return save("w7-710", d)


def w8():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        summer(d, color=INK)
        d.move(3.0, 0)
        d += elm.Rect(w=3.6, h=2.6, color=NEW, lw=1.4, fill="none").label(
            "INT1 socket\nweek-7 pair\n+ Q3 + output", color=NEW
        )
        d.move(4.4, 0)
        integrator(d, label="INT2", color=INK)
        d.move(-9.4, -5.0)
        inverter(d, color=INK)
        d.move(5.5, 0)
        schmitt(d, color=INK)
        d.move(3.2, 0)
        integrator(d, label="INT3", vin="vB", vout="vA", color=INK)
        d += elm.Label().at((0, 3.6)).label("Week 8 = week 7 pair + second stage + complementary out", color=NEW)
    return save("w8-chassis", d)


def _two_stage(d, *, cc=False, mirror=False, close="C"):
    """Discrete Fig 8.8 + 8.13 + 8.27. Optional Cc / repeater / C vs Z2."""
    col_pair = INK
    col_new = NEW if (cc or mirror) else NEW
    q1 = elm.BjtNpn(color=col_pair).reverse().label("Q1")
    d += q1
    d += elm.Line(color=col_pair).left().at(q1.base).length(0.6).label("− in", loc="left")
    d += elm.Line(color=col_pair).up().at(q1.collector).length(0.8)
    d += elm.Vdd(color=col_pair).label("+V1")
    d += elm.Line(color=col_pair).down().at(q1.emitter).length(0.5)
    d += elm.Dot(color=col_pair)
    d += elm.Line(color=col_pair).right().length(2.4)
    d += elm.Dot(color=col_pair)
    d.push()
    d += elm.SourceI(color=col_pair).down().reverse().label("I")
    d += elm.Vss(color=col_pair).label("−V2")
    d.pop()
    q2 = elm.BjtNpn(color=col_pair).anchor("emitter").label("Q2")
    d += q2
    d += elm.Line(color=col_pair).right().at(q2.base).length(0.55).label("+ in", loc="right")
    if mirror:
        d += elm.CurrentMirror(color=NEW).at(q2.collector).up().label("Fig 10.9", color=NEW)
        d += elm.Vdd(color=NEW)
    else:
        d += elm.SourceI(color=col_new).up().at(q2.collector).reverse().label("CS")
        d += elm.Vdd(color=col_new)
    d += elm.Line(color=col_new).at(q2.collector).right().length(1.1)
    q3 = elm.BjtPnp(color=col_new).anchor("base").label("Q3")
    d += q3
    d += elm.Line(color=col_new).up().at(q3.emitter).length(0.4)
    d += elm.Vdd(color=col_new)
    d += elm.Resistor(color=col_new).down().at(q3.collector).label("R2")
    d += elm.Vss(color=col_new)
    d += elm.Line(color=col_new).at(q3.collector).right().length(0.8)
    qn = elm.BjtNpn(color=col_new).anchor("base").label("NPN")
    d += qn
    d += elm.Line(color=col_new).up().at(qn.collector).length(0.35)
    d += elm.Vdd(color=col_new)
    d += elm.Line(color=col_new).down().at(qn.emitter).length(0.45)
    d += elm.Dot(color=col_new).label("Vo", loc="right")
    vo = d.here
    qp = elm.BjtPnp(color=col_new).anchor("emitter").label("PNP")
    d += qp
    d += elm.Line(color=col_new).down().at(qp.collector).length(0.35)
    d += elm.Vss(color=col_new)
    d += elm.Diode(color=col_new).at(qn.base).down().label("D")
    d += elm.Diode(color=col_new).down().label("D")
    d += elm.Line(color=col_new).toy(qp.base)
    if cc:
        d += elm.Capacitor(color=NEW).at(q3.collector).left().label("Cc", color=NEW)
        d += elm.Line(color=NEW).tox(q3.base)
    if close == "C":
        d += elm.Capacitor(color=NEW if not cc and not mirror else INK).at(vo).down().length(1.6).label("C")
        d += elm.Line().left().tox(q1.base)
        d += elm.Line().up().toy(q1.base)
        d += elm.Dot()
    else:
        d += elm.Resistor(color=NEW).at(vo).up().length(1.2).label("Z2")
        d += elm.Line(color=NEW).left().tox(q1.base)
        d += elm.Resistor(color=NEW).down().label("Z1")
        d += elm.Dot(open=True, color=NEW).label("Vi", loc="left")


def w8_int1():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        _two_stage(d, close="C")
        d += elm.Label().at((0, 4.4)).label("black pair · coral = Q3 + CS + complementary + C", color=NEW)
    return save("w8-int1", d)


def w9():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        summer(d, color=INK)
        d.move(3.0, 0)
        d += elm.Rect(w=3.6, h=2.6, color=NEW, lw=1.4, fill="none").label(
            "INT1 = Fig 9.1\nweek 8 + Cc", color=NEW
        )
        d.move(4.4, 0)
        integrator(d, label="INT2", color=INK)
        d.move(-9.4, -5.0)
        inverter(d, color=INK)
        d.move(5.5, 0)
        schmitt(d, color=INK)
        d.move(3.2, 0)
        integrator(d, label="INT3", vin="vB", vout="vA", color=INK)
        d += elm.Label().at((0, 3.6)).label("Week 9 = week 8 amp + Cc", color=NEW)
    return save("w9-chassis", d)


def w9_int1():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        _two_stage(d, cc=True, close="C")
        d += elm.Label().at((0, 4.4)).label("week 8 in black · coral = Cc", color=NEW)
    return save("w9-int1", d)


def w9_98():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        _two_stage(d, cc=True, close="R")
        d += elm.Label().at((0, 4.6)).label("Fig 9.8 · C lifted, Z1/Z2 on · then restore C", color=NEW)
    return save("w9-98", d)


def w10():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        summer(d, color=INK)
        d.move(3.0, 0)
        d += elm.Rect(w=3.8, h=2.6, color=NEW, lw=1.4, fill="none").label(
            "INT1 = Fig 9.1\n+ Fig 10.9 repeater", color=NEW
        )
        d.move(4.6, 0)
        integrator(d, label="INT2", color=INK)
        d.move(-9.6, -5.0)
        inverter(d, color=INK)
        d.move(5.5, 0)
        schmitt(d, color=INK)
        d.move(3.2, 0)
        integrator(d, label="INT3", vin="vB", vout="vA", color=INK)
        d += elm.Label().at((0, 3.6)).label("Week 10 = week 9 + current repeater", color=NEW)
    return save("w10-chassis", d)


def w10_int1():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        _two_stage(d, cc=True, mirror=True, close="C")
        d += elm.Label().at((0, 4.4)).label("week 9 amp · coral = Qref/Qout repeater", color=NEW)
    return save("w10-int1", d)


def w11():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        summer(d, color=INK)
        d.move(3.0, 0)
        d += elm.Rect(w=3.4, h=2.4, color=INK, lw=1.2, fill="none").label("INT1 Fig 9.1")
        d.move(4.2, 0)
        integrator(d, label="INT2", color=INK)
        d += elm.Switch(color=NEW).at((3.2, 2.6)).right().label("①②", color=NEW)
        d.move(-9.2, -5.0)
        inverter(d, color=INK)
        d.move(5.5, 0)
        schmitt(d, color=INK)
        d.move(3.2, 0)
        integrator(d, label="INT3", vin="vB", vout="vA", color=INK)
        d += elm.Label().at((0, 3.8)).label("Week 11 = week 10 + reset/operate/hold switches", color=NEW)
    return save("w11-chassis", d)


def w11_1217():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        d += elm.Dot(open=True, color=INK).label("vB")
        d += elm.Resistor(color=INK).right().label("R1")
        d += elm.Switch(action="close", color=NEW).right().label("① operate", color=NEW)
        d += elm.Dot(color=INK)
        d.push()
        d += elm.Line(color=INK).up().length(1.2)
        d += elm.Capacitor(color=INK).right().label("C")
        d += elm.Line(color=INK).down().length(1.2)
        d += elm.Dot(color=INK)
        d.pop()
        d += elm.Line(color=INK).right().length(0.35)
        op = elm.Opamp(sign=True, color=INK).anchor("in1").label("INT", loc="top")
        d += op
        d += elm.Ground(color=INK).at(op.in2)
        d += elm.Line(color=INK).at(op.out).right().length(0.8).label("Vo", loc="right")
        d += elm.Dot(open=True, color=NEW).at((0, -2.6)).label("vA")
        d += elm.Resistor(color=NEW).right().label("R2")
        d += elm.Switch(color=NEW).right().label("② reset", color=NEW)
        d += elm.Dot(color=NEW)
        d += elm.Resistor(color=NEW).right().label("R2")
        d += elm.Line(color=NEW).up().toy(op.out)
        d += elm.Line(color=NEW).tox(op.out)
    return save("w11-1217", d)


def w11_rect():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        d += elm.Dot(open=True, color=NEW).label("Vin")
        d += elm.Resistor(color=NEW).right().label("R")
        d += elm.Dot(color=NEW)
        n = d.here
        d.push()
        d += elm.Line(color=NEW).up().length(1.15)
        d += elm.Resistor(color=NEW).right().label("R")
        d += elm.Line(color=NEW).down().length(1.15)
        d += elm.Dot(color=NEW)
        d.pop()
        d += elm.Line(color=NEW).right().length(0.35)
        op = elm.Opamp(sign=True, color=NEW).anchor("in1")
        d += op
        d += elm.Ground(color=NEW).at(op.in2)
        d += elm.Diode(color=NEW).at(op.out).right().label("D")
        d += elm.Line(color=NEW).right().length(0.5).label("Vo ≥ 0", loc="right")
    return save("w11-rectifier", d)


def w12():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        summer(d, color=INK)
        d.move(3.0, 0)
        d += elm.Rect(w=3.2, h=2.2, color=INK, lw=1.2, fill="none").label("INT1 Fig 9.1")
        d.move(4.0, 0)
        integrator(d, label="INT2", color=INK)
        d.move(-9.0, -5.0)
        inverter(d, color=INK)
        d.move(5.5, 0)
        schmitt(d, color=INK)
        d.move(3.2, 0)
        integrator(d, label="INT3", vin="vB", vout="vA", color=INK)
        d.move(4.0, 4.6)
        integrator(d, label="twin of Vl", vin="error", vout="Vl model", color=NEW)
        d += elm.Label().at((0, 8.8)).label("Week 12 = week 11 patched + analog twin of Fig 5.3", color=NEW)
    return save("w12-chassis", d)


def w12_butter():
    with schemdraw.Drawing(show=False, fontsize=10) as d:
        for i, lab in enumerate(["SUM+INT", "INT", "INT", "INT", "INV"]):
            if i:
                d += elm.Line(color=INK).right().length(0.45)
            if lab == "INV":
                inverter(d, label=lab, z1="R", z2="R", vin="", vout="", color=INK)
            else:
                integrator(d, label=lab, vin="", vout="", color=INK)
        d += elm.Line(color=NEW).right().length(0.4)
        d += elm.Line(color=NEW).up().length(2.2)
        d += elm.Line(color=NEW).left().length(16.5)
        d += elm.Arrow(color=NEW).down().length(0.4).label("closing patch · Fig 12.13", color=NEW)
    return save("w12-butter", d)


def w13():
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        d += elm.Dot(open=True, color=INK).label("Vi1")
        d += elm.Resistor(color=INK).right().label("Zi1")
        d += elm.Dot(color=INK)
        d.push()
        d += elm.Resistor(color=NEW).down().label("Rlag")
        d += elm.Capacitor(color=NEW).down().label("Clag")
        d += elm.Ground(color=NEW)
        d.pop()
        d.push()
        d += elm.Line(color=INK).up().length(1.2)
        d += elm.Resistor(color=INK).right().label("Zf")
        d += elm.Line(color=INK).down().length(1.2)
        d += elm.Dot(color=INK)
        d.pop()
        d += elm.Line(color=INK).right().length(0.35)
        op = elm.Opamp(sign=True, color=INK).anchor("in1").label("SUM", loc="top")
        d += op
        d += elm.Ground(color=INK).at(op.in2)
        d += elm.Line(color=INK).at(op.out).right().length(0.7)
        d.move(2.4, 0)
        d += elm.Rect(w=3.2, h=2.2, color=INK, lw=1.2, fill="none").label("INT1 + Cc")
        d += elm.Capacitor(color=NEW).at((8.2, 1.4)).right().label("Cc", color=NEW)
        d.move(4.6, -0.2)
        integrator(d, label="INT2", color=INK)
        d.move(4.0, 0)
        d += elm.Capacitor(color=NEW).label("C")
        d += elm.Resistor(color=NEW).label("R")
        d += elm.Capacitor(color=NEW).label("C").label("Fig 13.19", loc="bottom", color=NEW)
        d += elm.Label().at((0, 4.0)).label("Week 13 = week 12 + two compensation recipes", color=NEW)
    return save("w13-chassis", d)


WEEKS = [
    dict(
        id="w1",
        title="Week 1 — computing core lands",
        lineage="Start. Three ICs. Two empty sockets.",
        added=["Figure 1.2a inverter (INV)", "Figure 1.4 summer (SUM)", "§1.2.3 integrator (INT1)", "Empty reserved sockets INT2, INT3"],
        cards=[
            ("The box so far", "everything this week is new", "w1-chassis",
             "Build all three. Measure each Vo/Vi. Do not patch an ODE yet."),
        ],
    ),
    dict(
        id="w2",
        title="Week 2 — close ẋ = −x",
        lineage="Week 1 + one patch.",
        added=["Patch cord: INT1 output → SUM Vi1 → INT1 input", "No new amplifiers"],
        cards=[
            ("The box so far", "coral = the patch", "w2-chassis",
             "Same three ICs. Time constant must be RC once |L| is large."),
        ],
    ),
    dict(
        id="w3",
        title="Week 3 — characterize the machine you already have",
        lineage="Week 2 + default Cc. Patch unchanged.",
        added=["Cc on INT1’s LM301A (Figure 3.1)", "No new sockets"],
        cards=[
            ("The box so far", "coral = Cc", "w3-chassis",
             "Step and ramp the same ẋ = −x patch."),
        ],
    ),
    dict(
        id="w4",
        title="Week 4 — second integrator, second-order loop",
        lineage="Week 3 + INT2 in the reserved socket + a new patch.",
        added=["INT2 (identical to INT1)", "Patch SUM → INT1 → INT2 → SUM"],
        cards=[
            ("The box so far", "coral = INT2 and the new loop", "w4-chassis",
             "The computer can ring. Measure L of the patched loop."),
        ],
    ),
    dict(
        id="w5",
        title="Week 5 — plant on the unused end",
        lineage="Week 4 + Figure 5.3. Not connected to the computer.",
        added=["Error amp ao", "Series NPN, emitter R, RL || CL"],
        cards=[
            ("The box so far", "coral = the regulator", "w5-chassis",
             "Two systems, one chassis. Do not patch them together yet."),
            ("New module · Figure 5.3a", "§5.2.2", "w5-plant",
             "VR to +. Vl sensed to −. Series pass, load RL || CL."),
        ],
    ),
    dict(
        id="w6",
        title="Week 6 — test oscillator on the patchbay",
        lineage="Week 5 + Schmitt + INT3.",
        added=["Figure 12.7 Schmitt", "INT3 becomes the triangle generator"],
        cards=[
            ("The box so far", "coral = oscillator", "w6-chassis",
             "Computer and plant stay. The oscillator is the signal source."),
            ("New module · Figure 12.7a", "positive feedback to +", "w6-schmitt",
             "Thresholds ±(R1/R2)VM. − is grounded."),
        ],
    ),
    dict(
        id="w7",
        title="Week 7 — pull INT1’s IC, start the discrete pair",
        lineage="Week 6, except INT1’s IC is gone. Pair + C only.",
        added=["Pull the INT1 IC", "Figure 7.4 pair + tail current", "Balance with Figure 7.10"],
        cards=[
            ("The box so far", "coral = INT1 socket after the IC comes out", "w7-chassis",
             "SUM, INT2, INV, plant, oscillator still run on ICs."),
            ("Inside the INT1 socket this week", "Figure 7.4", "w7-int1",
             "No second stage yet. C stays."),
            ("Balance · Figure 7.10", "pot across the collector loads", "w7-710",
             "Short the bases, null vo, remove the short."),
        ],
    ),
    dict(
        id="w8",
        title="Week 8 — finish that same channel",
        lineage="Week 7 pair + Figure 8.8 + 8.13 + 8.27.",
        added=["PNP CE second stage (Q3)", "Current-source load (Figure 8.13)", "Complementary output (Figure 8.27)"],
        cards=[
            ("The box so far", "coral = stages added behind last week’s pair", "w8-chassis",
             "INT1 is a complete discrete op-amp again."),
            ("Inside the INT1 socket this week", "week 7 pair + new stages", "w8-int1",
             "Same Q1/Q2. Q3, CS load, complementary pair, and C are new."),
        ],
    ),
    dict(
        id="w9",
        title="Week 9 — that channel is now Figure 9.1",
        lineage="Week 8 amplifier + Cc. Then C goes back.",
        added=["Cc", "Temporary Figure 9.8 inverter for Ch 9 data", "Then put C back"],
        cards=[
            ("The box so far", "coral = Cc on last week’s amp", "w9-chassis",
             "Repeat the week-2 ẋ = −x step through this amp."),
            ("INT1 socket = week 8 + Cc", "Figure 9.1", "w9-int1",
             "This is last week’s circuit. The only new component is Cc."),
            ("Measurement hookup · Figure 9.8", "C lifted, resistive feedback", "w9-98",
             "Do not leave it as an inverter. The computer needs C back."),
        ],
    ),
    dict(
        id="w10",
        title="Week 10 — current repeater on the same amp",
        lineage="Week 9 Figure 9.1 + Figure 10.9.",
        added=["Figure 10.9 current repeater as first-stage load"],
        cards=[
            ("The box so far", "coral = repeater on INT1", "w10-chassis",
             "INT2 is still an IC. Hold-time ratio is IB."),
            ("INT1 socket = week 9 + repeater", "Figure 10.9", "w10-int1",
             "Same Q1–Q3. The first-stage load is now a current repeater."),
        ],
    ),
    dict(
        id="w11",
        title="Week 11 — reset / operate / hold",
        lineage="Week 10 + Figure 12.17 switches.",
        added=["Operate ① and reset ② on both integrators", "Figure 11.18 precision rectifier"],
        cards=[
            ("The box so far", "coral = mode switches", "w11-chassis",
             "The discrete amp does not move. You wrap switches around C."),
            ("New around each integrator · Figure 12.17", "switches in coral", "w11-1217",
             "Operate: ① closed, ② open. Reset: ① open, ② closed. Hold: both open."),
            ("Also keep · Figure 11.18", "precision rectifier", "w11-rectifier",
             "Needed later if you add Wien amplitude control."),
        ],
    ),
    dict(
        id="w12",
        title="Week 12 — run the two problems",
        lineage="Week 11 hardware, new patches.",
        added=["Patch Figure 12.13", "Analog twin of Figure 5.3"],
        cards=[
            ("The box so far", "coral = analog twin of the regulator", "w12-chassis",
             "This is the finished function. Week 13 only makes it faster and quieter."),
            ("Problem 1a patch · Figure 12.13", "same five blocks, one feedback", "w12-butter",
             "Coral is only the closing patch."),
        ],
    ),
    dict(
        id="w13",
        title="Week 13 — compensate the assembled box",
        lineage="Week 12 + two recipes.",
        added=["Figure 13.1 input lag on SUM", "Cc on Figure 9.1", "Figure 13.19 two-pole on the plant"],
        cards=[
            ("The box so far", "coral = compensation parts", "w13-chassis",
             "Raise time-scale α until it breaks. Fix L. Raise it again."),
        ],
    ),
]


def write_html() -> None:
    parts = [
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Roberge one-box — schemdraw</title>
  <link rel="stylesheet" href="design-system/colors_and_type.css">
  <style>
    * { box-sizing: border-box; }
    html, body { margin: 0; }
    body { background: var(--book); color: var(--slate); padding-bottom: 48px; }
    .deck { max-width: 1100px; margin: 0 auto; padding: 0 24px 48px; }
    @media (min-width: 1100px) { .deck { padding: 0 40px 64px; } }
    .top { display: flex; align-items: center; gap: 10px; padding: 20px 0 8px; }
    .top img { width: 22px; height: 22px; }
    h1.display { margin: 8px 0 12px; font-size: clamp(32px, 6vw, 48px); }
    .lede { margin: 0 0 16px; max-width: 44rem; }
    .legend { display: flex; flex-wrap: wrap; gap: 16px; margin: 0 0 20px; font-size: 13px; color: var(--fg-muted); }
    .legend span { display: inline-flex; align-items: center; gap: 8px; }
    .swatch { width: 22px; height: 3px; display: inline-block; }
    .swatch.old { background: #1F1E1D; }
    .swatch.new { background: #D97757; }
    nav.jump { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 32px; }
    nav.jump a {
      font-family: var(--font-sans); font-size: 13px; padding: 6px 10px;
      border: 1px solid var(--hairline); border-radius: var(--r-sm);
      background: var(--bg-elev); text-decoration: none; color: var(--fg);
    }
    h2 { margin: 56px 0 6px; scroll-margin-top: 16px; }
    .lineage { margin: 0 0 10px; color: var(--crail-deep); font-size: 15px; }
    .added { margin: 0 0 16px; padding-left: 1.2rem; max-width: 44rem; }
    .card {
      background: var(--bg-elev); border: 1px solid var(--hairline);
      border-radius: var(--r-md); padding: 16px; margin: 0 0 16px;
    }
    .card h3 { font-family: var(--font-serif); font-weight: 400; font-size: 20px; margin: 0 0 4px; }
    .tag { font-family: var(--font-mono); font-size: 11px; color: var(--crail-deep); margin: 0 0 12px; }
    .note { font-size: 14px; color: var(--fg-muted); margin: 10px 0 0; }
    img.sch {
      width: 100%; height: auto; display: block; background: #fff;
      border-radius: var(--r-xs); border: 1px solid var(--hairline); padding: 12px;
    }
    .back { font-size: 14px; }
  </style>
</head>
<body>
  <div class="deck">
    <header>
      <div class="top">
        <img src="design-system/anthropic-mark.svg" alt="">
        <p class="eyebrow">Visual guide · schemdraw IEEE</p>
      </div>
      <h1 class="display">The box, drawn by a schematic engine</h1>
      <p class="lede">Same week-by-week machine as the hand SVG page. Symbols and pin attachments come from schemdraw. Existing pages were not overwritten.</p>
      <div class="legend">
        <span><i class="swatch old"></i> already on the box</span>
        <span><i class="swatch new"></i> added this week</span>
      </div>
      <p class="back">
        <a href="schematics.html">Hand SVG</a> ·
        <a href="schematics-other.html">Book + first schemdraw set</a> ·
        <a href="capstone.html">Build log</a>
      </p>
    </header>
"""
    ]
    parts.append('    <nav class="jump">\n')
    for w in WEEKS:
        parts.append(f'      <a href="#{w["id"]}">{w["id"][1:]}</a>\n')
    parts.append("    </nav>\n")
    for w in WEEKS:
        parts.append(f'    <h2 id="{w["id"]}">{w["title"]}</h2>\n')
        parts.append(f'    <p class="lineage">{w["lineage"]}</p>\n')
        parts.append("    <ul class=\"added\">")
        parts.append("".join(f"<li>{i}</li>" for i in w["added"]))
        parts.append("</ul>\n")
        for title, tag, slug, note in w["cards"]:
            parts.append(
                f"""    <article class="card">
      <h3>{title}</h3>
      <p class="tag">{tag} · schemdraw IEEE</p>
      <img class="sch" src="figures/schemdraw-box/{slug}.svg" alt="{title}">
      <p class="note">{note}</p>
    </article>
"""
            )
    parts.append('    <p class="back"><a href="capstone.html">Back to the build log</a></p>\n')
    parts.append("  </div>\n</body>\n</html>\n")
    dest = ROOT / "schematics-schemdraw.html"
    dest.write_text("".join(parts), encoding="utf-8")
    print("wrote", dest)


def main() -> None:
    gens = [
        w1, w2, w3, w4, w5, w5_plant, w6, w6_schmitt, w7, w7_pair, w7_710,
        w8, w8_int1, w9, w9_int1, w9_98, w10, w10_int1, w11, w11_1217,
        w11_rect, w12, w12_butter, w13,
    ]
    failed = []
    for fn in gens:
        try:
            fn()
        except Exception as e:
            failed.append((fn.__name__, repr(e)))
            print("FAIL", fn.__name__, e)
    write_html()
    if failed:
        print("FAILED", len(failed))
        for n, e in failed:
            print(" ", n, e)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
