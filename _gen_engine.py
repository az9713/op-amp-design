#!/usr/bin/env python3
"""Complete schemdraw schematics for the one-box project.

Each function draws ONE connected circuit from symbols + nets.
No book crops, no hand SVG reuse, no placeholder boxes.
"""
from __future__ import annotations

from pathlib import Path

import schemdraw
import schemdraw.elements as elm

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figures" / "engine"
OUT.mkdir(parents=True, exist_ok=True)

INK = "#1F1E1D"
NEW = "#D97757"

elm.style(elm.STYLE_IEEE)


def save(name: str, d: schemdraw.Drawing) -> str:
    path = OUT / f"{name}.svg"
    d.save(str(path))
    print("ok", path.name)
    return path.name


# ─────────────────────────────────────────────────────────────
# Primitive complete circuits
# ─────────────────────────────────────────────────────────────

def circuit_inverter(color=INK, label="INV"):
    """Fig 1.2a — complete inverting amplifier."""
    with schemdraw.Drawing(show=False, fontsize=12) as d:
        d.config(unit=2.5)
        d += elm.Dot(open=True, color=color).label("Vi")
        d += elm.Resistor(color=color).right().label("Z1")
        d += elm.Dot(color=color)
        d.push()
        d += elm.Line(color=color).up()
        d += elm.Resistor(color=color).right().label("Z2")
        d += elm.Line(color=color).down()
        d += elm.Dot(color=color)
        d.pop()
        d += elm.Line(color=color).right().length(0.4)
        op = elm.Opamp(sign=True, leads=True, color=color).anchor("in1").label(label, loc="center", ofst=0)
        d += op
        d += elm.Line(color=color).left().at(op.in2).length(0.4)
        d += elm.Ground(color=color)
        d += elm.Line(color=color).at(op.out).right().label("Vo", loc="right")
        d += elm.Label().at((2.2, 2.6)).label("Fig 1.2a  ·  Vo/Vi = −Z2/Z1", color=color)
    return save("inv", d)


def circuit_summer(color=INK):
    """Fig 1.4 — complete two-input inverting summer."""
    with schemdraw.Drawing(show=False, fontsize=12) as d:
        d.config(unit=2.5)
        d += elm.Dot(open=True, color=color).label("Vi1")
        d += elm.Resistor(color=color).right().label("Zi1")
        d += elm.Dot(color=color)
        d.push()
        d += elm.Line(color=color).up()
        d += elm.Resistor(color=color).left().label("Zi2")
        d += elm.Dot(open=True, color=color).label("Vi2", loc="left")
        d.pop()
        d.push()
        d += elm.Line(color=color).up().length(2.4)
        d += elm.Resistor(color=color).right().label("Zf")
        fb = d.here
        d.pop()
        d += elm.Line(color=color).right().length(0.4)
        op = elm.Opamp(sign=True, leads=True, color=color).anchor("in1").label("SUM", loc="center")
        d += op
        d += elm.Line(color=color).left().at(op.in2).length(0.4)
        d += elm.Ground(color=color)
        d += elm.Line(color=color).at(op.out).right().length(0.5)
        d += elm.Dot(color=color)
        d += elm.Line(color=color).toy(fb)
        d += elm.Line(color=color).tox(fb)
        d += elm.Line(color=color).at(op.out).right().length(1.4).label("Vo", loc="right")
        d += elm.Label().at((2.4, 3.4)).label("Fig 1.4  ·  Vo = −(Zf/Zi1)Vi1 − (Zf/Zi2)Vi2", color=color)
    return save("sum", d)


def circuit_integrator(color=INK, name="INT1"):
    """§1.2.3 — complete inverting integrator."""
    with schemdraw.Drawing(show=False, fontsize=12) as d:
        d.config(unit=2.5)
        d += elm.Dot(open=True, color=color).label("Vi")
        d += elm.Resistor(color=color).right().label("R")
        d += elm.Dot(color=color)
        d.push()
        d += elm.Line(color=color).up()
        d += elm.Capacitor(color=color).right().label("C")
        d += elm.Line(color=color).down()
        d += elm.Dot(color=color)
        d.pop()
        d += elm.Line(color=color).right().length(0.4)
        op = elm.Opamp(sign=True, leads=True, color=color).anchor("in1").label(name, loc="center")
        d += op
        d += elm.Line(color=color).left().at(op.in2).length(0.4)
        d += elm.Ground(color=color)
        d += elm.Line(color=color).at(op.out).right().label("Vo", loc="right")
        d += elm.Label().at((2.2, 2.6)).label("§1.2.3  ·  Vo/Vi = −1/(RCs)", color=color)
    return save("int", d)


def circuit_loop_first_order(cc=False):
    """Week 2/3 — SUM and INT1 as ONE loop: ẋ = −x."""
    color = INK
    extra = NEW if cc else INK
    with schemdraw.Drawing(show=False, fontsize=12) as d:
        d.config(unit=2.4)
        # Integrator first, left to right
        d += elm.Dot(open=True, color=color).label("x")
        d += elm.Resistor(color=color).right().label("R")
        d += elm.Dot(color=color)
        n_int = d.here
        d.push()
        d += elm.Line(color=color).up()
        d += elm.Capacitor(color=color).right().label("C")
        d += elm.Line(color=color).down()
        d += elm.Dot(color=color)
        d.pop()
        d += elm.Line(color=color).right().length(0.35)
        opi = elm.Opamp(sign=True, leads=True, color=color).anchor("in1").label("INT1", loc="center")
        d += opi
        d += elm.Line(color=color).left().at(opi.in2).length(0.35)
        d += elm.Ground(color=color)
        if cc:
            d += elm.Capacitor(color=extra).at(opi.n1).down().label("Cc", color=extra)
            d += elm.Line(color=extra).tox(opi.n2)
        d += elm.Line(color=color).at(opi.out).right().length(0.7).label("ẋ", loc="top")
        d += elm.Resistor(color=NEW if not cc else color).right().label("Zi")
        d += elm.Dot(color=color)
        n_sum = d.here
        d.push()
        d += elm.Line(color=color).up()
        d += elm.Resistor(color=color).right().label("Zf")
        d += elm.Line(color=color).down()
        d += elm.Dot(color=color)
        d.pop()
        d += elm.Line(color=color).right().length(0.35)
        ops = elm.Opamp(sign=True, leads=True, color=color).anchor("in1").label("SUM", loc="center")
        d += ops
        d += elm.Line(color=color).left().at(ops.in2).length(0.35)
        d += elm.Ground(color=color)
        d += elm.Line(color=color).at(ops.out).right().length(0.8).label("x", loc="right")
        # close the loop along the top
        d += elm.Line(color=NEW).at(ops.out).up().length(2.3)
        d += elm.Line(color=NEW).left()
        d += elm.Line(color=NEW).tox(n_int)
        d += elm.Arrow(color=NEW).down().length(0.4)
        d += elm.Label().at((5, 3.4)).label(
            "ẋ = −x/RC  ·  patch SUM output back to INT1 input", color=NEW
        )
    return save("loop1" + ("-cc" if cc else ""), d)


def circuit_loop_second_order():
    """Week 4 — SUM → INT1 → INT2 → SUM. One circuit."""
    color = INK
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        d.config(unit=2.2)
        d += elm.Dot(open=True, color=color).label("x")
        d += elm.Resistor(color=color).right().label("Zi")
        d += elm.Dot(color=color)
        d.push()
        d += elm.Line(color=color).up()
        d += elm.Resistor(color=color).right().label("Zf")
        d += elm.Line(color=color).down()
        d += elm.Dot(color=color)
        d.pop()
        d += elm.Line(color=color).right().length(0.3)
        ops = elm.Opamp(sign=True, leads=True, color=color).anchor("in1").label("SUM", loc="center")
        d += ops
        d += elm.Ground(color=color).at(ops.in2)
        d += elm.Line(color=color).at(ops.out).right().length(0.5).label("ẍ", loc="top")
        d += elm.Resistor(color=NEW).right().label("R")
        d += elm.Dot(color=color)
        d.push()
        d += elm.Line(color=color).up()
        d += elm.Capacitor(color=color).right().label("C")
        d += elm.Line(color=color).down()
        d += elm.Dot(color=color)
        d.pop()
        d += elm.Line(color=color).right().length(0.3)
        op1 = elm.Opamp(sign=True, leads=True, color=NEW).anchor("in1").label("INT1", loc="center")
        d += op1
        d += elm.Ground(color=color).at(op1.in2)
        d += elm.Line(color=color).at(op1.out).right().length(0.5).label("ẋ", loc="top")
        d += elm.Resistor(color=NEW).right().label("R")
        d += elm.Dot(color=color)
        d.push()
        d += elm.Line(color=color).up()
        d += elm.Capacitor(color=color).right().label("C")
        d += elm.Line(color=color).down()
        d += elm.Dot(color=color)
        d.pop()
        d += elm.Line(color=color).right().length(0.3)
        op2 = elm.Opamp(sign=True, leads=True, color=NEW).anchor("in1").label("INT2", loc="center")
        d += op2
        d += elm.Ground(color=color).at(op2.in2)
        d += elm.Line(color=color).at(op2.out).right().length(0.7).label("x", loc="right")
        d += elm.Line(color=NEW).at(op2.out).up().length(2.2)
        d += elm.Line(color=NEW).left()
        d += elm.Line(color=NEW).left()
        d += elm.Line(color=NEW).tox((0.2, 0))
        d += elm.Arrow(color=NEW).down().length(0.35)
        d += elm.Label().at((6, 3.2)).label("second-order loop  ·  coral = INT2 and the new patch", color=NEW)
    return save("loop2", d)


def circuit_plant():
    """Fig 5.3a — complete series regulator."""
    color = INK
    with schemdraw.Drawing(show=False, fontsize=12) as d:
        d.config(unit=2.4)
        d += elm.Dot(open=True, color=color).label("VR")
        d += elm.Line(color=color).right()
        op = elm.Opamp(sign=True, leads=True, color=color).anchor("in2").label("ao", loc="center")
        d += op
        d += elm.Line(color=color).left().at(op.in1).length(1.0)
        d += elm.Dot(color=color)
        sense = d.here
        d += elm.Line(color=color).at(op.out).right().length(0.5)
        q = elm.BjtNpn(color=color).anchor("base").label("NPN")
        d += q
        d += elm.Resistor(color=color).up().at(q.collector).label("R")
        d += elm.Vdd(color=color).label("Vu")
        d += elm.Line(color=color).down().at(q.emitter).length(0.5)
        d += elm.Dot(color=color).label("Vl", loc="right")
        out = d.here
        d.push()
        d += elm.Resistor(color=color).down().label("RL")
        d += elm.Ground(color=color)
        d.pop()
        d.push()
        d += elm.Line(color=color).right().length(1.0)
        d += elm.Dot(color=color)
        d.push()
        d += elm.Capacitor(color=color).down().label("CL")
        d += elm.Ground(color=color)
        d.pop()
        d += elm.Line(color=color).right().length(0.8)
        d += elm.SourceI(color=color).down().label("Id")
        d += elm.Ground(color=color)
        d.pop()
        d += elm.Line(color=color).at(out).left().tox(sense)
        d += elm.Line(color=color).toy(sense)
        d += elm.Label().at((3.2, 4.2)).label("Fig 5.3a  ·  VR to +  ·  Vl sensed to −", color=INK)
    return save("plant", d)


def circuit_oscillator():
    """Fig 12.7 + integrator — complete function generator."""
    with schemdraw.Drawing(show=False, fontsize=12) as d:
        d.config(unit=2.4)
        d += elm.Dot(open=True, color=INK).label("vA")
        d += elm.Resistor(color=INK).right().label("R1")
        d += elm.Dot(color=INK)
        d.push()
        d += elm.Line(color=INK).up()
        d += elm.Resistor(color=INK).right().label("R2")
        d += elm.Line(color=INK).down()
        d += elm.Dot(color=INK)
        d.pop()
        d += elm.Line(color=INK).right().length(0.35)
        ops = elm.Opamp(sign=True, leads=True, color=INK).anchor("in2").label("SCHMITT", loc="center")
        d += ops
        d += elm.Ground(color=INK).at(ops.in1)
        d += elm.Line(color=INK).at(ops.out).right().length(0.7).label("vB", loc="top")
        d += elm.Resistor(color=NEW).right().label("R")
        d += elm.Dot(color=INK)
        d.push()
        d += elm.Line(color=INK).up()
        d += elm.Capacitor(color=INK).right().label("C")
        d += elm.Line(color=INK).down()
        d += elm.Dot(color=INK)
        d.pop()
        d += elm.Line(color=INK).right().length(0.35)
        opi = elm.Opamp(sign=True, leads=True, color=NEW).anchor("in1").label("INT3", loc="center")
        d += opi
        d += elm.Ground(color=INK).at(opi.in2)
        d += elm.Line(color=INK).at(opi.out).right().length(0.8).label("vA", loc="right")
        d += elm.Line(color=NEW).at(opi.out).up().length(2.2)
        d += elm.Line(color=NEW).left()
        d += elm.Line(color=NEW).tox((0.15, 0))
        d += elm.Arrow(color=NEW).down().length(0.35)
        d += elm.Label().at((5, 3.2)).label("Fig 12.7 + integrator  ·  period 4RC when VM = 10 V", color=NEW)
    return save("osc", d)


def circuit_diffpair():
    """Fig 7.4 — complete long-tailed pair."""
    with schemdraw.Drawing(show=False, fontsize=12) as d:
        d.config(unit=2.2)
        q1 = elm.BjtNpn(color=INK).reverse().label("Q1")
        d += q1
        d += elm.Line(color=INK).left().at(q1.base).length(0.8).label("vI1  −", loc="left")
        d += elm.Resistor(color=INK).up().at(q1.collector).label("RL")
        d += elm.Vdd(color=INK).label("+V")
        d += elm.Line(color=INK).down().at(q1.emitter).length(0.55)
        d += elm.Dot(color=INK)
        d += elm.Line(color=INK).right().length(2.6)
        d += elm.Dot(color=INK)
        d.push()
        d += elm.SourceI(color=INK).down().reverse().label("I")
        d += elm.Vss(color=INK).label("−V2")
        d.pop()
        q2 = elm.BjtNpn(color=INK).anchor("emitter").label("Q2")
        d += q2
        d += elm.Line(color=INK).right().at(q2.base).length(0.8).label("+  vI2", loc="right")
        d += elm.Resistor(color=INK).up().at(q2.collector).label("RL")
        d += elm.Vdd(color=INK)
        d += elm.Line(color=INK).at(q1.collector).right().length(0.7)
        d += elm.Gap().label("vo")
        d += elm.Line(color=INK).right().tox(q2.collector)
        d += elm.Label().at((1.6, 3.4)).label("Fig 7.4  ·  INT1 inverting ← Q1 base", color=INK)
    return save("diffpair", d)


def circuit_710():
    """Fig 7.10 — same pair, pot across collector loads."""
    with schemdraw.Drawing(show=False, fontsize=12) as d:
        d.config(unit=2.2)
        q1 = elm.BjtNpn(color=INK).reverse().label("Q1")
        d += q1
        d += elm.Resistor(color=INK).up().at(q1.collector).label("RL")
        left = d.here
        d += elm.Line(color=INK).down().at(q1.emitter).length(0.5)
        d += elm.Dot(color=INK)
        d += elm.Line(color=INK).right().length(2.8)
        d += elm.Dot(color=INK)
        d.push()
        d += elm.SourceI(color=INK).down().reverse().label("I")
        d += elm.Vss(color=INK)
        d.pop()
        q2 = elm.BjtNpn(color=INK).anchor("emitter").label("Q2")
        d += q2
        d += elm.Resistor(color=INK).up().at(q2.collector).label("RL")
        right = d.here
        pot = elm.Potentiometer(color=NEW).at(left).to(right).label("R", color=NEW)
        d += pot
        d += elm.Line(color=NEW).up().at(pot.tap).length(0.45).label("+Vc", loc="right", color=NEW)
        d += elm.Label().at((1.6, 3.8)).label("Fig 7.10  ·  pot in the collectors, not the emitters", color=NEW)
    return save("bal710", d)


def circuit_discrete(mode="int"):
    """
    Complete discrete channel.
    mode:
      int     — week 8: pair + CS + Q3 + complementary + C (integrator)
      cc      — week 9: plus Cc
      inv     — Fig 9.8: Z1/Z2, no C
      mirror  — week 10: PNP repeater replaces CS
    """
    with schemdraw.Drawing(show=False, fontsize=11) as d:
        d.config(unit=2.0)
        q1 = elm.BjtNpn(color=INK).reverse().label("Q1")
        d += q1
        d += elm.Line(color=INK).left().at(q1.base).length(0.7).label("− in", loc="left")
        d += elm.Line(color=INK).up().at(q1.collector).length(0.7)
        d += elm.Vdd(color=INK).label("+V1")
        d += elm.Line(color=INK).down().at(q1.emitter).length(0.45)
        d += elm.Dot(color=INK)
        d += elm.Line(color=INK).right().length(2.3)
        d += elm.Dot(color=INK)
        d.push()
        d += elm.SourceI(color=INK).down().reverse().label("I")
        d += elm.Vss(color=INK).label("−V2")
        d.pop()
        q2 = elm.BjtNpn(color=INK).anchor("emitter").label("Q2")
        d += q2
        d += elm.Line(color=INK).right().at(q2.base).length(0.55).label("+ in", loc="right")

        if mode == "mirror":
            qref = elm.BjtPnp(color=NEW).reverse().anchor("collector").at(q2.collector).label("Qref")
            d += qref
            d += elm.Line(color=NEW).at(qref.base).right().length(1.4)
            d += elm.Dot(color=NEW)
            d.push()
            d += elm.Line(color=NEW).up().length(0.15)
            d += elm.Line(color=NEW).at(qref.emitter).up().length(0.4)
            d += elm.Vdd(color=NEW)
            d.pop()
            qout = elm.BjtPnp(color=NEW).anchor("base").label("Qout")
            d += qout
            d += elm.Line(color=NEW).up().at(qout.emitter).length(0.4)
            d += elm.Vdd(color=NEW)
            d += elm.Line(color=NEW).at(qref.base).to(qref.collector)
            d += elm.Line(color=NEW).down().at(qout.collector).length(0.3)
            collect = d.here
        else:
            d += elm.SourceI(color=NEW).up().at(q2.collector).reverse().label("Ics")
            d += elm.Vdd(color=NEW)
            d += elm.Line(color=NEW).at(q2.collector).right().length(0.2)
            collect = d.here

        d += elm.Line(color=NEW).at(q2.collector).right().length(1.2)
        q3 = elm.BjtPnp(color=NEW).anchor("base").label("Q3")
        d += q3
        d += elm.Line(color=NEW).up().at(q3.emitter).length(0.35)
        d += elm.Vdd(color=NEW)
        d += elm.Resistor(color=NEW).down().at(q3.collector).label("R2")
        d += elm.Vss(color=NEW)
        if mode in ("cc", "mirror", "inv"):
            d += elm.Capacitor(color=NEW).at(q3.collector).left().label("Cc", color=NEW)
            d += elm.Line(color=NEW).tox(q3.base)

        d += elm.Line(color=NEW).at(q3.collector).right().length(0.9)
        qn = elm.BjtNpn(color=NEW).anchor("base").label("Qn")
        d += qn
        d += elm.Line(color=NEW).up().at(qn.collector).length(0.3)
        d += elm.Vdd(color=NEW)
        d += elm.Line(color=NEW).down().at(qn.emitter).length(0.4)
        d += elm.Dot(color=NEW).label("Vo", loc="right")
        vo = d.here
        qp = elm.BjtPnp(color=NEW).anchor("emitter").label("Qp")
        d += qp
        d += elm.Line(color=NEW).down().at(qp.collector).length(0.3)
        d += elm.Vss(color=NEW)
        d += elm.Diode(color=NEW).at(qn.base).down()
        d += elm.Diode(color=NEW).down()
        d += elm.Line(color=NEW).toy(qp.base)

        if mode == "inv":
            d += elm.Resistor(color=NEW).at(vo).up().label("Z2")
            d += elm.Line(color=NEW).left().tox(q1.base)
            d += elm.Dot(color=NEW)
            d += elm.Resistor(color=NEW).left().label("Z1")
            d += elm.Dot(open=True, color=NEW).label("Vi", loc="left")
            cap = "Fig 9.8 inverter  ·  C is off"
        else:
            d += elm.Capacitor(color=NEW if mode == "int" else INK).at(vo).down().length(1.5).label("C")
            d += elm.Line(color=INK).left().tox(q1.base)
            d += elm.Line(color=INK).up().toy(q1.base)
            d += elm.Dot(color=INK)
            cap = {
                "int": "Fig 8.8+8.13+8.27  ·  closed as integrator",
                "cc": "Fig 9.1  ·  week 8 + Cc",
                "mirror": "Fig 9.1 + Fig 10.9 repeater",
            }[mode]
        d += elm.Label().at((3.5, 4.6)).label(cap, color=NEW)
    return save({"int": "disc8", "cc": "disc9", "inv": "disc98", "mirror": "disc10"}[mode], d)


def circuit_threemode():
    """Fig 12.17 — complete three-mode integrator."""
    with schemdraw.Drawing(show=False, fontsize=12) as d:
        d.config(unit=2.3)
        d += elm.Dot(open=True, color=INK).label("vB")
        d += elm.Resistor(color=INK).right().label("R1")
        d += elm.Switch(action="close", color=NEW).right().label("① operate", color=NEW, loc="top")
        d += elm.Dot(color=INK)
        n = d.here
        d.push()
        d += elm.Line(color=INK).up()
        d += elm.Capacitor(color=INK).right().label("C")
        d += elm.Line(color=INK).down()
        d += elm.Dot(color=INK)
        d.pop()
        d += elm.Line(color=INK).right().length(0.35)
        op = elm.Opamp(sign=True, leads=True, color=INK).anchor("in1").label("INT", loc="center")
        d += op
        d += elm.Ground(color=INK).at(op.in2)
        d += elm.Line(color=INK).at(op.out).right().length(1.0).label("Vo", loc="right")
        # reset path
        d += elm.Dot(open=True, color=NEW).at((0, -2.8)).label("vA")
        d += elm.Resistor(color=NEW).right().label("R2")
        d += elm.Switch(color=NEW).right().label("② reset", color=NEW, loc="bottom")
        d += elm.Dot(color=NEW)
        d.push()
        d += elm.Line(color=NEW).up().toy(n)
        d.pop()
        d += elm.Resistor(color=NEW).right().label("R2")
        d += elm.Line(color=NEW).up().toy(op.out)
        d += elm.Line(color=NEW).tox(op.out)
        d += elm.Label().at((3.5, 3.0)).label(
            "Operate ①  ·  Reset ②  ·  Hold both open", color=NEW
        )
    return save("threemode", d)


def circuit_rectifier():
    """Fig 11.18 — complete precision rectifier."""
    with schemdraw.Drawing(show=False, fontsize=12) as d:
        d.config(unit=2.4)
        d += elm.Dot(open=True, color=INK).label("Vin")
        d += elm.Resistor(color=INK).right().label("R")
        d += elm.Dot(color=INK)
        d.push()
        d += elm.Line(color=INK).up()
        d += elm.Resistor(color=INK).right().label("R")
        d += elm.Line(color=INK).down()
        d += elm.Dot(color=INK)
        d.pop()
        d += elm.Line(color=INK).right().length(0.35)
        op = elm.Opamp(sign=True, leads=True, color=INK).anchor("in1")
        d += op
        d += elm.Ground(color=INK).at(op.in2)
        d += elm.Diode(color=INK).at(op.out).right().label("D")
        d += elm.Line(color=INK).right().label("Vo ≥ 0", loc="right")
        d += elm.Label().at((2.4, 2.6)).label("Fig 11.18 precision rectifier", color=INK)
    return save("rectifier", d)


def circuit_butterworth():
    """Fig 12.13 — five connected stages, one feedback."""
    with schemdraw.Drawing(show=False, fontsize=10) as d:
        d.config(unit=1.8)
        first_in = None
        last_out = None
        for i, name in enumerate(["SUM+INT", "INT", "INT", "INT", "INV"]):
            if i:
                d += elm.Line(color=INK).right().length(0.35)
            d += elm.Resistor(color=INK).right().label("R")
            d += elm.Dot(color=INK)
            if i == 0:
                first_in = d.here
            d.push()
            d += elm.Line(color=INK).up().length(0.9)
            if name == "INV":
                d += elm.Resistor(color=INK).right().label("R")
            else:
                d += elm.Capacitor(color=INK).right().label("C")
            d += elm.Line(color=INK).down().length(0.9)
            d += elm.Dot(color=INK)
            d.pop()
            d += elm.Line(color=INK).right().length(0.25)
            op = elm.Opamp(sign=True, leads=True, color=INK).anchor("in1").label(name, loc="center", fontsize=9)
            d += op
            d += elm.Ground(color=INK).at(op.in2)
            d += elm.Line(color=INK).at(op.out).right().length(0.35)
            last = d.here
        d += elm.Line(color=NEW).at(last).up().length(2.0)
        d += elm.Line(color=NEW).left().length(18)
        d += elm.Line(color=NEW).down().length(1.6)
        d += elm.Arrow(color=NEW).right().length(0.35)
        d += elm.Label().at((6, 2.8)).label("Fig 12.13  ·  coral = the closing patch", color=NEW)
    return save("butter", d)


def circuit_twin():
    """Analog model of Fig 5.3 — error amp, 1/R, load integrator."""
    with schemdraw.Drawing(show=False, fontsize=12) as d:
        d.config(unit=2.3)
        d += elm.Dot(open=True, color=INK).label("VR")
        d += elm.Resistor(color=INK).right().label("R")
        d += elm.Dot(color=INK)
        d.push()
        d += elm.Line(color=INK).up()
        d += elm.Resistor(color=INK).right().label("R")
        d += elm.Line(color=INK).down()
        d += elm.Dot(color=INK)
        d.pop()
        d += elm.Line(color=INK).right().length(0.3)
        op1 = elm.Opamp(sign=True, leads=True, color=INK).anchor("in1").label("error ao", loc="center")
        d += op1
        d += elm.Ground(color=INK).at(op1.in2)
        d += elm.Line(color=INK).at(op1.out).right().length(0.5)
        d += elm.Resistor(color=INK).right().label("R (1/R)")
        d += elm.Dot(color=INK)
        d.push()
        d += elm.Line(color=INK).up()
        d += elm.Capacitor(color=INK).right().label("CL")
        d += elm.Line(color=INK).down()
        d += elm.Dot(color=INK)
        d.pop()
        d += elm.Line(color=INK).right().length(0.3)
        op2 = elm.Opamp(sign=True, leads=True, color=NEW).anchor("in1").label("load INT", loc="center")
        d += op2
        d += elm.Ground(color=INK).at(op2.in2)
        d += elm.Line(color=INK).at(op2.out).right().label("Vl model", loc="right")
        d += elm.Label().at((5, 2.8)).label("analog twin of Fig 5.3  ·  overlay on the real Vl", color=NEW)
    return save("twin", d)


def circuit_lag():
    """Fig 13.1 — complete inverter with input lag."""
    with schemdraw.Drawing(show=False, fontsize=12) as d:
        d.config(unit=2.4)
        d += elm.Dot(open=True, color=INK).label("Vi")
        d += elm.Resistor(color=INK).right().label("Z1")
        d += elm.Dot(color=INK)
        d.push()
        d += elm.Resistor(color=NEW).down().label("Rlag")
        d += elm.Capacitor(color=NEW).down().label("Clag")
        d += elm.Ground(color=NEW)
        d.pop()
        d.push()
        d += elm.Line(color=INK).up()
        d += elm.Resistor(color=INK).right().label("Z2")
        d += elm.Line(color=INK).down()
        d += elm.Dot(color=INK)
        d.pop()
        d += elm.Line(color=INK).right().length(0.35)
        op = elm.Opamp(sign=True, leads=True, color=INK).anchor("in1").label("SUM/INV", loc="center")
        d += op
        d += elm.Ground(color=INK).at(op.in2)
        d += elm.Line(color=INK).at(op.out).right().label("Vo", loc="right")
        d += elm.Label().at((2.6, 2.6)).label("Fig 13.1  ·  lag does not change ideal Vo/Vi", color=NEW)
    return save("lag", d)


def circuit_twopole():
    """Fig 13.19 — two-pole compensation network (complete)."""
    with schemdraw.Drawing(show=False, fontsize=12) as d:
        d.config(unit=2.5)
        d += elm.Dot(open=True, color=INK).label("comp 1")
        d += elm.Capacitor(color=NEW).right().label("C")
        d += elm.Resistor(color=NEW).right().label("R")
        d += elm.Capacitor(color=NEW).right().label("C")
        d += elm.Dot(open=True, color=INK).label("comp 2", loc="right")
        d += elm.Label().at((3.5, 1.4)).label("Fig 13.19 two-pole  ·  on the regulator error amp", color=NEW)
    return save("twopole", d)


# ─────────────────────────────────────────────────────────────
# Page
# ─────────────────────────────────────────────────────────────

SECTIONS = [
    dict(
        id="w1",
        title="Week 1 — three complete ICs, not yet one loop",
        note="These are three separate circuits that live on one board.",
        figs=[
            ("sum", "Figure 1.4 weighted summer", "Socket SUM. Two inputs, Zf over the top, + grounded."),
            ("inv", "Figure 1.2a inverter", "Socket INV. Stays for the rest of the project."),
            ("int", "§1.2.3 integrator", "Socket INT1. This is the IC you pull in week 7."),
        ],
    ),
    dict(
        id="w2",
        title="Week 2 — first-order computer (one circuit)",
        note="INT1 and SUM are now one loop. Coral is the patch that closes ẋ = −x.",
        figs=[("loop1", "ẋ = −x", "INT1 output is ẋ. SUM returns x to the integrator input.")],
    ),
    dict(
        id="w3",
        title="Week 3 — same loop + Cc",
        note="The circuit is unchanged except the compensation capacitor on INT1.",
        figs=[("loop1-cc", "Week 2 loop + Figure 3.1 Cc", "Keep the better Cc until chapter 13.")],
    ),
    dict(
        id="w4",
        title="Week 4 — second-order computer (one circuit)",
        note="SUM, INT1, INT2 in one ring. Coral is INT2 and the new patch.",
        figs=[("loop2", "ẍ → ẋ → x → SUM", "Find the gain that sits on jω.")],
    ),
    dict(
        id="w5",
        title="Week 5 — the plant is its own complete circuit",
        note="Not patched to the computer yet.",
        figs=[("plant", "Figure 5.3a voltage regulator", "VR to +. Vl sensed to −. Series NPN, RL || CL, Id.")],
    ),
    dict(
        id="w6",
        title="Week 6 — Schmitt + integrator (one circuit)",
        note="Complete function generator. Coral closes vA back to the Schmitt.",
        figs=[("osc", "Figure 12.7 + integrator", "Square vB drives INT3. Triangle vA drives the Schmitt +.")],
    ),
    dict(
        id="w7",
        title="Week 7 — discrete front end (complete pair)",
        note="This is the whole circuit in the INT1 socket this week.",
        figs=[
            ("diffpair", "Figure 7.4 differential pair", "Q1 base is the inverting pin of the channel."),
            ("bal710", "Figure 7.10 collector pot", "Pot is in the collectors. Do not use the emitter pot."),
        ],
    ),
    dict(
        id="w8",
        title="Week 8 — complete discrete integrator",
        note="One circuit: pair + current-source load + Q3 + complementary output + C.",
        figs=[("disc8", "Figures 8.8, 8.13, 8.27 closed with C", "The socket is an integrator again.")],
    ),
    dict(
        id="w9",
        title="Week 9 — that circuit is Figure 9.1",
        note="Same transistors. Cc is the only new part. Then C goes back.",
        figs=[
            ("disc9", "Figure 9.1 as integrator", "Week 8 + Cc."),
            ("disc98", "Figure 9.8 measurement hookup", "C off, Z1/Z2 on. Restore C after the data."),
        ],
    ),
    dict(
        id="w10",
        title="Week 10 — same circuit, repeater load",
        note="Qref/Qout replace the single current source.",
        figs=[("disc10", "Figure 9.1 + Figure 10.9", "First-stage load is now a PNP repeater.")],
    ),
    dict(
        id="w11",
        title="Week 11 — three-mode integrator (one circuit)",
        note="The discrete amp does not change. The switches wrap C.",
        figs=[
            ("threemode", "Figure 12.17", "Operate ①. Reset ②. Hold both open."),
            ("rectifier", "Figure 11.18", "Keep on the chassis for later Wien control."),
        ],
    ),
    dict(
        id="w12",
        title="Week 12 — the two problems (two complete circuits)",
        note="Patches, not new amplifiers.",
        figs=[
            ("butter", "Figure 12.13 Butterworth", "Four integrators + inverter. Coral is the closing patch."),
            ("twin", "Analog twin of Figure 5.3", "Error amp, 1/R, load pole as an integrator."),
        ],
    ),
    dict(
        id="w13",
        title="Week 13 — two complete compensation circuits",
        note="Same computer, same plant. These networks go on them.",
        figs=[
            ("lag", "Figure 13.1 input lag", "Shunt on SUM / INV. Ideal gain unchanged."),
            ("twopole", "Figure 13.19 two-pole", "On the regulator error-amp compensation pins."),
        ],
    ),
]


def write_html() -> None:
    nav = "\n".join(f'      <a href="#{s["id"]}">{s["id"][1:]}</a>' for s in SECTIONS)
    body = []
    for s in SECTIONS:
        body.append(f'    <h2 id="{s["id"]}">{s["title"]}</h2>\n')
        body.append(f'    <p class="week-lead">{s["note"]}</p>\n')
        for slug, title, note in s["figs"]:
            body.append(
                f"""    <article class="card">
      <h3>{title}</h3>
      <p class="tag">{slug}.svg · schemdraw IEEE · one connected circuit</p>
      <img class="sch" src="figures/engine/{slug}.svg" alt="{title}">
      <p class="note">{note}</p>
    </article>
"""
            )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Roberge one-box — complete schemdraw circuits</title>
  <link rel="stylesheet" href="design-system/colors_and_type.css">
  <style>
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; }}
    body {{ background: var(--book); color: var(--slate); padding-bottom: 48px; }}
    .deck {{ max-width: 960px; margin: 0 auto; padding: 0 24px 48px; }}
    @media (min-width: 960px) {{ .deck {{ padding: 0 40px 64px; }} }}
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
    h2 {{ margin: 48px 0 6px; scroll-margin-top: 16px; }}
    .week-lead {{ margin: 0 0 14px; color: var(--fg-muted); max-width: 40rem; }}
    .card {{
      background: var(--bg-elev); border: 1px solid var(--hairline);
      border-radius: var(--r-md); padding: 16px; margin: 0 0 16px;
    }}
    .card h3 {{ font-family: var(--font-serif); font-weight: 400; font-size: 20px; margin: 0 0 4px; }}
    .tag {{ font-family: var(--font-mono); font-size: 11px; color: var(--crail-deep); margin: 0 0 12px; }}
    .note {{ font-size: 14px; color: var(--fg-muted); margin: 10px 0 0; }}
    img.sch {{
      width: 100%; height: auto; display: block; background: #fff;
      border: 1px solid var(--hairline); border-radius: var(--r-xs); padding: 16px;
    }}
    .back {{ font-size: 14px; }}
  </style>
</head>
<body>
  <div class="deck">
    <header>
      <div class="top">
        <img src="design-system/anthropic-mark.svg" alt="">
        <p class="eyebrow">Complete circuits · schemdraw only</p>
      </div>
      <h1 class="display">Each drawing is one circuit</h1>
      <p class="lede">Generated only from schemdraw. No book scans. No hand SVG. Coral is the net added that week.</p>
      <p class="back">
        <a href="schematics.html">Hand SVG</a> ·
        <a href="schematics-other.html">Book figures</a> ·
        <a href="capstone.html">Build log</a>
      </p>
    </header>
    <nav class="jump">
{nav}
    </nav>
{''.join(body)}
    <p class="back"><a href="capstone.html">Back to the build log</a></p>
  </div>
</body>
</html>
"""
    dest = ROOT / "schematics-engine.html"
    dest.write_text(html, encoding="utf-8")
    print("wrote", dest)


def main() -> None:
    jobs = [
        circuit_inverter,
        circuit_summer,
        circuit_integrator,
        circuit_loop_first_order,
        lambda: circuit_loop_first_order(cc=True),
        circuit_loop_second_order,
        circuit_plant,
        circuit_oscillator,
        circuit_diffpair,
        circuit_710,
        lambda: circuit_discrete("int"),
        lambda: circuit_discrete("cc"),
        lambda: circuit_discrete("inv"),
        lambda: circuit_discrete("mirror"),
        circuit_threemode,
        circuit_rectifier,
        circuit_butterworth,
        circuit_twin,
        circuit_lag,
        circuit_twopole,
    ]
    failed = []
    for fn in jobs:
        try:
            fn()
        except Exception as e:
            failed.append((getattr(fn, "__name__", str(fn)), repr(e)))
            print("FAIL", getattr(fn, "__name__", fn), e)
    write_html()
    if failed:
        raise SystemExit(f"{len(failed)} drawings failed")


if __name__ == "__main__":
    main()
