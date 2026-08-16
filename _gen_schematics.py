#!/usr/bin/env python3
"""Generate schematics.html — one chassis that grows each week."""

from pathlib import Path

INK = "#1F1E1D"
NEW = "#D97757"
EMPTY = "#B4B3AC"
FONT = "DM Sans, sans-serif"

def G(color, body):
    return (
        f'<g color="{color}" fill="none" stroke="currentColor" '
        f'stroke-width="1.8" stroke-linejoin="miter" stroke-linecap="butt">'
        f"{body}</g>"
    )

def T(x, y, text, size=12, fill=None, anchor=None):
    f = fill or INK
    a = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{f}"{a}>{text}</text>'

def pm(x, y):
    return T(x + 12, y - 8, "−", 15) + T(x + 12, y + 24, "+", 15)

# ─── compact Arrow modules (origin = op-amp left-face center) ───

def inverter(x, y, label="INV", z1="Z1", z2="Z2", vin="Vi", vout="Vo"):
    return f"""
      <use href="#oa" x="{x}" y="{y}"/>
      <line x1="{x-110}" y1="{y-16}" x2="{x-78}" y2="{y-16}"/>
      <use href="#res" x="{x-58}" y="{y-16}"/>
      <line x1="{x-38}" y1="{y-16}" x2="{x}" y2="{y-16}"/>
      <use href="#dot" x="{x-28}" y="{y-16}"/>
      <line x1="{x-28}" y1="{y-16}" x2="{x-28}" y2="{y-62}"/>
      <line x1="{x-28}" y1="{y-62}" x2="{x-8}" y2="{y-62}"/>
      <use href="#res" x="{x+12}" y="{y-62}"/>
      <line x1="{x+32}" y1="{y-62}" x2="{x+100}" y2="{y-62}"/>
      <line x1="{x+100}" y1="{y-62}" x2="{x+100}" y2="{y}"/>
      <use href="#dot" x="{x+100}" y="{y}"/>
      <line x1="{x+74}" y1="{y}" x2="{x+130}" y2="{y}"/>
      <line x1="{x-16}" y1="{y+16}" x2="{x}" y2="{y+16}"/>
      <use href="#gnd" x="{x-16}" y="{y+16}"/>
      {pm(x, y)}
      {T(x-58, y-28, z1, 11)}
      {T(x+2, y-74, z2, 11)}
      {T(x-110, y-24, vin, 11)}
      {T(x+108, y-8, vout, 11)}
      {T(x+8, y-48, label, 11, NEW)}
    """

def integrator(x, y, label="INT", r="R", c="C", vin="Vi", vout="Vo"):
    return f"""
      <use href="#oa" x="{x}" y="{y}"/>
      <line x1="{x-110}" y1="{y-16}" x2="{x-78}" y2="{y-16}"/>
      <use href="#res" x="{x-58}" y="{y-16}"/>
      <line x1="{x-38}" y1="{y-16}" x2="{x}" y2="{y-16}"/>
      <use href="#dot" x="{x-28}" y="{y-16}"/>
      <line x1="{x-28}" y1="{y-16}" x2="{x-28}" y2="{y-62}"/>
      <line x1="{x-28}" y1="{y-62}" x2="{x+18}" y2="{y-62}"/>
      <use href="#cap" x="{x+30}" y="{y-62}"/>
      <line x1="{x+40}" y1="{y-62}" x2="{x+100}" y2="{y-62}"/>
      <line x1="{x+100}" y1="{y-62}" x2="{x+100}" y2="{y}"/>
      <use href="#dot" x="{x+100}" y="{y}"/>
      <line x1="{x+74}" y1="{y}" x2="{x+130}" y2="{y}"/>
      <line x1="{x-16}" y1="{y+16}" x2="{x}" y2="{y+16}"/>
      <use href="#gnd" x="{x-16}" y="{y+16}"/>
      {pm(x, y)}
      {T(x-62, y-28, r, 11)}
      {T(x+24, y-74, c, 11)}
      {T(x-110, y-24, vin, 11)}
      {T(x+108, y-8, vout, 11)}
      {T(x+8, y-48, label, 11, NEW)}
    """

def summer(x, y, label="SUM", n=2):
    """Two-input inverting summer. Inputs at y-16 and y-50."""
    y1, y2 = y - 16, y - 50
    return f"""
      <use href="#oa" x="{x}" y="{y}"/>
      <line x1="{x-120}" y1="{y2}" x2="{x-88}" y2="{y2}"/>
      <use href="#res" x="{x-68}" y="{y2}"/>
      <line x1="{x-48}" y1="{y2}" x2="{x-20}" y2="{y2}"/>
      <line x1="{x-120}" y1="{y1}" x2="{x-88}" y2="{y1}"/>
      <use href="#res" x="{x-68}" y="{y1}"/>
      <line x1="{x-48}" y1="{y1}" x2="{x-20}" y2="{y1}"/>
      <line x1="{x-20}" y1="{y2}" x2="{x-20}" y2="{y1}"/>
      <use href="#dot" x="{x-20}" y="{y2}"/>
      <use href="#dot" x="{x-20}" y="{y1}"/>
      <line x1="{x-20}" y1="{y1}" x2="{x}" y2="{y1}"/>
      <line x1="{x-20}" y1="{y2}" x2="{x-20}" y2="{y-72}"/>
      <line x1="{x-20}" y1="{y-72}" x2="{x+8}" y2="{y-72}"/>
      <use href="#res" x="{x+28}" y="{y-72}"/>
      <line x1="{x+48}" y1="{y-72}" x2="{x+100}" y2="{y-72}"/>
      <line x1="{x+100}" y1="{y-72}" x2="{x+100}" y2="{y}"/>
      <use href="#dot" x="{x+100}" y="{y}"/>
      <line x1="{x+74}" y1="{y}" x2="{x+130}" y2="{y}"/>
      <line x1="{x-16}" y1="{y+16}" x2="{x}" y2="{y+16}"/>
      <use href="#gnd" x="{x-16}" y="{y+16}"/>
      {pm(x, y)}
      {T(x-78, y2-12, "Zi2", 11)}
      {T(x-78, y1-12, "Zi1", 11)}
      {T(x+18, y-84, "Zf", 11)}
      {T(x-120, y2-12, "Vi2", 11)}
      {T(x-120, y1-12, "Vi1", 11)}
      {T(x+108, y-8, "Vo", 11)}
      {T(x+8, y-48, label, 11, NEW)}
    """

def schmitt(x, y, label="SCHMITT"):
    """Fig 12.7a noninverting Schmitt. Input on +."""
    return f"""
      <use href="#oa" x="{x}" y="{y}"/>
      <line x1="{x-110}" y1="{y+16}" x2="{x-78}" y2="{y+16}"/>
      <use href="#res" x="{x-58}" y="{y+16}"/>
      <line x1="{x-38}" y1="{y+16}" x2="{x}" y2="{y+16}"/>
      <use href="#dot" x="{x-28}" y="{y+16}"/>
      <line x1="{x-28}" y1="{y+16}" x2="{x-28}" y2="{y-62}"/>
      <line x1="{x-28}" y1="{y-62}" x2="{x-8}" y2="{y-62}"/>
      <use href="#res" x="{x+12}" y="{y-62}"/>
      <line x1="{x+32}" y1="{y-62}" x2="{x+100}" y2="{y-62}"/>
      <line x1="{x+100}" y1="{y-62}" x2="{x+100}" y2="{y}"/>
      <use href="#dot" x="{x+100}" y="{y}"/>
      <line x1="{x+74}" y1="{y}" x2="{x+130}" y2="{y}"/>
      <line x1="{x-16}" y1="{y-16}" x2="{x}" y2="{y-16}"/>
      <use href="#gnd" x="{x-16}" y="{y-16}"/>
      {pm(x, y)}
      {T(x-62, y+4, "R1", 11)}
      {T(x+2, y-74, "R2", 11)}
      {T(x-110, y+8, "vI", 11)}
      {T(x+108, y-8, "vB", 11)}
      {T(x+4, y-48, label, 11, NEW)}
    """

def mini_stage(x, y, kind="int", label=""):
    """Arrow-correct compact integrator/inverter for chain drawings."""
    fb = "cap" if kind == "int" else "res"
    return f"""
      <use href="#oa" x="{x}" y="{y}"/>
      <line x1="{x-44}" y1="{y-16}" x2="{x-24}" y2="{y-16}"/>
      <use href="#res" x="{x-24}" y="{y-16}"/>
      <line x1="{x-4}" y1="{y-16}" x2="{x}" y2="{y-16}"/>
      <use href="#dot" x="{x-14}" y="{y-16}"/>
      <line x1="{x-14}" y1="{y-16}" x2="{x-14}" y2="{y-48}"/>
      <line x1="{x-14}" y1="{y-48}" x2="{x+18}" y2="{y-48}"/>
      <use href="#{fb}" x="{x+30}" y="{y-48}"/>
      <line x1="{x+40}" y1="{y-48}" x2="{x+90}" y2="{y-48}"/>
      <line x1="{x+90}" y1="{y-48}" x2="{x+90}" y2="{y}"/>
      <use href="#dot" x="{x+90}" y="{y}"/>
      <line x1="{x+74}" y1="{y}" x2="{x+90}" y2="{y}"/>
      <line x1="{x-16}" y1="{y+16}" x2="{x}" y2="{y+16}"/>
      <use href="#gnd" x="{x-16}" y="{y+16}"/>
      {pm(x, y)}
      {T(x + 8, y - 36, label, 10, NEW)}
    """


def empty_socket(x, y, name):
    return G(EMPTY, f"""
      <rect x="{x-50}" y="{y-50}" width="140" height="100" rx="4" fill="none" stroke-dasharray="5 4"/>
      {T(x+20, y-8, name, 12, EMPTY, "middle")}
      {T(x+20, y+10, "empty", 11, EMPTY, "middle")}
    """)

def plant(x, y, label="PLANT"):
    """Fig 5.3a compact."""
    return f"""
      <use href="#oa" x="{x}" y="{y}"/>
      <line x1="{x-70}" y1="{y+16}" x2="{x}" y2="{y+16}"/>
      <line x1="{x-50}" y1="{y-16}" x2="{x}" y2="{y-16}"/>
      <use href="#dot" x="{x-50}" y="{y-16}"/>
      <line x1="{x+74}" y1="{y}" x2="{x+110}" y2="{y}"/>
      <use href="#npn" x="{x+110}" y="{y}"/>
      <line x1="{x+126}" y1="{y-36}" x2="{x+126}" y2="{y-70}"/>
      <line x1="{x+126}" y1="{y-70}" x2="{x+200}" y2="{y-70}"/>
      <line x1="{x+126}" y1="{y+36}" x2="{x+126}" y2="{y+60}"/>
      <use href="#resv" x="{x+126}" y="{y+80}"/>
      <line x1="{x+126}" y1="{y+100}" x2="{x+126}" y2="{y+120}"/>
      <use href="#dot" x="{x+126}" y="{y+120}"/>
      <line x1="{x+126}" y1="{y+120}" x2="{x+200}" y2="{y+120}"/>
      <line x1="{x+160}" y1="{y+120}" x2="{x+160}" y2="{y+136}"/>
      <use href="#dot" x="{x+160}" y="{y+120}"/>
      <use href="#resv" x="{x+160}" y="{y+156}"/>
      <use href="#gnd" x="{x+160}" y="{y+176}"/>
      <line x1="{x+190}" y1="{y+120}" x2="{x+190}" y2="{y+136}"/>
      <use href="#dot" x="{x+190}" y="{y+120}"/>
      <use href="#capv" x="{x+190}" y="{y+146}"/>
      <line x1="{x+190}" y1="{y+156}" x2="{x+190}" y2="{y+176}"/>
      <use href="#gnd" x="{x+190}" y="{y+176}"/>
      <line x1="{x-50}" y1="{y-16}" x2="{x-50}" y2="{y+120}"/>
      <line x1="{x-50}" y1="{y+120}" x2="{x+126}" y2="{y+120}"/>
      <use href="#dot" x="{x-50}" y="{y+120}"/>
      {pm(x, y)}
      {T(x-70, y+8, "VR", 11)}
      {T(x+204, y-66, "Vu", 11)}
      {T(x+138, y+124, "Vl", 11)}
      {T(x+148, y+160, "RL", 10)}
      {T(x+198, y+150, "CL", 10)}
      {T(x+20, y-48, label, 11, NEW)}
    """

def patch(x1, y1, x2, y2, via_y=None):
    if via_y is None:
        return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x1}" y2="{via_y}"/>'
        f'<line x1="{x1}" y1="{via_y}" x2="{x2}" y2="{via_y}"/>'
        f'<line x1="{x2}" y1="{via_y}" x2="{x2}" y2="{y2}"/>'
        f'<use href="#dot" x="{x1}" y="{y1}"/>'
        f'<use href="#dot" x="{x2}" y="{y2}"/>'
    )

def bay(x, y, w, h, title):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" '
        f'fill="#FAF9F5" stroke="#E4E1D6" stroke-width="1"/>'
        + T(x + 10, y + 16, title, 11, "#6F6E69")
    )

# Fixed positions on the chassis
# Computer row
SUM = (170, 160)
INT1 = (430, 160)
INT2 = (690, 160)
INT3 = (430, 400)
INV = (170, 400)
SCH = (690, 400)
PLT = (980, 200)

def svg(vbox, body, aria):
    return f'''<svg class="sch" viewBox="{vbox}" xmlns="http://www.w3.org/2000/svg" aria-label="{aria}">
        {body}
      </svg>'''

# ─── INT1 socket interiors (growing discrete amp) ───

def pair_only(color=INK):
    """Fig 7.4 pair. Output is differential collectors. C still on the socket."""
    return G(color, f"""
      <line x1="40" y1="28" x2="420" y2="28"/>
      <use href="#dot" x="120" y="28"/>
      <use href="#dot" x="300" y="28"/>
      <line x1="40" y1="250" x2="420" y2="250"/>
      <use href="#dot" x="210" y="250"/>
      <line x1="120" y1="28" x2="120" y2="48"/>
      <use href="#resv" x="120" y="68"/>
      <line x1="120" y1="88" x2="120" y2="104"/>
      <line x1="300" y1="28" x2="300" y2="48"/>
      <use href="#resv" x="300" y="68"/>
      <line x1="300" y1="88" x2="300" y2="104"/>
      <use href="#npn" x="104" y="140"/>
      <use href="#npnr" x="316" y="140"/>
      <line x1="40" y1="140" x2="104" y2="140"/>
      <line x1="380" y1="140" x2="316" y2="140"/>
      <line x1="120" y1="176" x2="120" y2="210"/>
      <line x1="300" y1="176" x2="300" y2="210"/>
      <line x1="120" y1="210" x2="300" y2="210"/>
      <use href="#dot" x="210" y="210"/>
      <line x1="210" y1="210" x2="210" y2="226"/>
      <circle cx="210" cy="238" r="11"/>
      <circle cx="210" cy="238" r="6.5"/>
      <line x1="210" y1="231" x2="210" y2="246"/>
      <polygon points="207,242 213,242 210,248" fill="currentColor" stroke="none"/>
      <line x1="210" y1="249" x2="210" y2="250"/>
      <line x1="120" y1="104" x2="200" y2="104"/>
      <line x1="300" y1="104" x2="220" y2="104"/>
      {T(428, 32, "+V", 12)}
      {T(428, 254, "−V2", 12)}
      {T(132, 72, "RL", 11)}
      {T(312, 72, "RL", 11)}
      {T(80, 132, "Q1", 11)}
      {T(324, 132, "Q2", 11)}
      {T(16, 136, "− in", 11, NEW)}
      {T(384, 136, "+ in", 11, NEW)}
      {T(222, 240, "I", 11)}
      {T(200, 94, "vo", 11)}
    """)

def _pair():
    return f"""
      <line x1="30" y1="24" x2="700" y2="24"/>
      <use href="#dot" x="86" y="24"/>
      <use href="#dot" x="214" y="24"/>
      <use href="#dot" x="356" y="24"/>
      <use href="#dot" x="436" y="24"/>
      <line x1="30" y1="300" x2="700" y2="300"/>
      <use href="#dot" x="150" y="300"/>
      <use href="#dot" x="356" y="300"/>
      <use href="#dot" x="436" y="300"/>
      <use href="#npn" x="70" y="130"/>
      <use href="#npnr" x="230" y="130"/>
      <line x1="30" y1="130" x2="70" y2="130"/>
      <line x1="270" y1="130" x2="230" y2="130"/>
      <line x1="86" y1="94" x2="86" y2="24"/>
      <line x1="214" y1="94" x2="214" y2="70"/>
      <line x1="86" y1="166" x2="86" y2="220"/>
      <line x1="214" y1="166" x2="214" y2="220"/>
      <line x1="86" y1="220" x2="214" y2="220"/>
      <use href="#dot" x="150" y="220"/>
      <line x1="150" y1="220" x2="150" y2="236"/>
      <circle cx="150" cy="250" r="11"/>
      <circle cx="150" cy="250" r="6.5"/>
      <line x1="150" y1="243" x2="150" y2="258"/>
      <polygon points="147,254 153,254 150,260" fill="currentColor" stroke="none"/>
      <line x1="150" y1="261" x2="150" y2="300"/>
      {T(708, 28, "+V1", 12)}
      {T(708, 304, "−V2", 12)}
      {T(48, 122, "Q1", 11)}
      {T(238, 122, "Q2", 11)}
      {T(162, 252, "I", 11)}
      {T(12, 126, "− in", 11, NEW)}
      {T(274, 126, "+ in", 11, NEW)}
    """

def _stages():
    return f"""
      <use href="#pnp" x="340" y="80"/>
      <line x1="356" y1="44" x2="356" y2="24"/>
      <line x1="214" y1="70" x2="230" y2="70"/>
      <line x1="230" y1="70" x2="230" y2="80"/>
      <line x1="230" y1="80" x2="340" y2="80"/>
      <line x1="356" y1="116" x2="356" y2="160"/>
      <use href="#resv" x="356" y="180"/>
      <line x1="356" y1="200" x2="356" y2="300"/>
      <use href="#dot" x="356" y="160"/>
      <line x1="356" y1="160" x2="400" y2="160"/>
      <use href="#npn" x="420" y="90"/>
      <use href="#pnp" x="420" y="230"/>
      <line x1="436" y1="54" x2="436" y2="24"/>
      <line x1="436" y1="266" x2="436" y2="300"/>
      <line x1="436" y1="126" x2="436" y2="160"/>
      <line x1="436" y1="194" x2="436" y2="160"/>
      <use href="#dot" x="436" y="160"/>
      <line x1="436" y1="160" x2="560" y2="160"/>
      <line x1="400" y1="90" x2="420" y2="90"/>
      <line x1="400" y1="230" x2="420" y2="230"/>
      <use href="#dot" x="400" y="90"/>
      <use href="#dot" x="400" y="160"/>
      <use href="#dot" x="400" y="230"/>
      <line x1="400" y1="90" x2="400" y2="118"/>
      <g transform="translate(400,118) rotate(90)"><use href="#diode"/></g>
      <line x1="400" y1="132" x2="400" y2="160"/>
      <line x1="400" y1="160" x2="400" y2="188"/>
      <g transform="translate(400,188) rotate(90)"><use href="#diode"/></g>
      <line x1="400" y1="202" x2="400" y2="230"/>
      {T(368, 76, "Q3", 11)}
      {T(368, 184, "R2", 11)}
      {T(448, 84, "NPN", 11)}
      {T(448, 236, "PNP", 11)}
      {T(568, 156, "Vo", 12)}
    """

def _cs_load():
    return f"""
      <use href="#pnp" x="198" y="56"/>
      <line x1="214" y1="20" x2="214" y2="24"/>
      <line x1="214" y1="92" x2="214" y2="94"/>
      <line x1="198" y1="56" x2="170" y2="56"/>
      <line x1="170" y1="56" x2="170" y2="40"/>
      <line x1="170" y1="40" x2="214" y2="40"/>
      <use href="#dot" x="214" y="40"/>
      {T(224, 54, "CS load", 11)}
    """

def _cc():
    return f"""
      <line x1="356" y1="160" x2="300" y2="160"/>
      <line x1="300" y1="160" x2="300" y2="80"/>
      <use href="#cap" x="300" y="80"/>
      <line x1="300" y1="80" x2="340" y2="80"/>
      <use href="#dot" x="300" y="80"/>
      {T(272, 70, "Cc", 12, NEW)}
    """

def _mirror():
    return f"""
      <use href="#pnp" x="138" y="56"/>
      <use href="#pnp" x="198" y="56"/>
      <line x1="154" y1="20" x2="154" y2="24"/>
      <line x1="214" y1="20" x2="214" y2="24"/>
      <line x1="138" y1="56" x2="198" y2="56"/>
      <line x1="154" y1="92" x2="154" y2="40"/>
      <line x1="138" y1="40" x2="154" y2="40"/>
      <line x1="138" y1="40" x2="138" y2="56"/>
      <use href="#dot" x="138" y="56"/>
      <use href="#dot" x="154" y="92"/>
      <line x1="214" y1="92" x2="214" y2="94"/>
      {T(224, 54, "Fig 10.9 repeater", 11, NEW)}
    """

def pair_plus_stages(highlight="stages"):
    """highlight = stages | cc | mirror. Pair always black. Highlighted parts coral."""
    out = G(INK, _pair())
    if highlight == "stages":
        out += G(NEW, _stages() + _cs_load())
    elif highlight == "cc":
        out += G(INK, _stages() + _cs_load())
        out += G(NEW, _cc())
    elif highlight == "mirror":
        out += G(INK, _stages() + _cc())
        out += G(NEW, _mirror())
    return out


def c_feedback(color=INK):
    """Integrating C from Vo back to − in, drawn under the discrete amp."""
    return G(color, f"""
      <use href="#dot" x="560" y="160"/>
      <line x1="560" y1="160" x2="560" y2="330"/>
      <line x1="560" y1="330" x2="16" y2="330"/>
      <use href="#cap" x="200" y="330"/>
      <line x1="16" y1="330" x2="16" y2="130"/>
      <line x1="16" y1="130" x2="30" y2="130"/>
      <use href="#dot" x="30" y="130"/>
      {T(188, 318, "C", 12)}
    """)

def r_feedback_inverter(color=NEW):
    """Fig 9.8: replace C with Z1/Z2 inverter around the discrete amp."""
    return G(color, f"""
      <line x1="30" y1="130" x2="-10" y2="130"/>
      <use href="#res" x="-30" y="130"/>
      <line x1="-50" y1="130" x2="-80" y2="130"/>
      <use href="#dot" x="40" y="130"/>
      <line x1="40" y1="130" x2="40" y2="50"/>
      <line x1="40" y1="50" x2="200" y2="50"/>
      <use href="#res" x="220" y="50"/>
      <line x1="240" y1="50" x2="560" y2="50"/>
      <line x1="560" y1="50" x2="560" y2="160"/>
      <use href="#dot" x="560" y="160"/>
      {T(-38, 116, "Z1", 11, NEW)}
      {T(210, 38, "Z2", 11, NEW)}
      {T(-90, 126, "Vi", 11, NEW)}
    """)

# ─── week cards ───

def card(title, tag, svgs, note):
    parts = "\n".join(svgs)
    return f'''    <article class="card">
      <h3>{title}</h3>
      <p class="tag">{tag}</p>
      {parts}
      <p class="note">{note}</p>
    </article>
'''

def added(items):
    lis = "".join(f"<li>{i}</li>" for i in items)
    return f'<ul class="added">{lis}</ul>'

# Chassis compositions

def chassis_w1():
    body = (
        bay(20, 40, 820, 460, "computer")
        + G(NEW, summer(*SUM) + integrator(*INT1, label="INT1") + inverter(*INV))
        + empty_socket(*INT2, "INT2")
        + empty_socket(690, 400, "INT3")
        + T(20, 28, "Week 1 · three ICs land. Two sockets stay empty.", 13, NEW)
    )
    return svg("0 0 860 480", body, "Week 1 chassis")

def chassis_w2():
    body = (
        bay(20, 40, 820, 460, "computer")
        + G(INK, summer(*SUM) + integrator(*INT1, label="INT1") + inverter(*INV))
        + empty_socket(*INT2, "INT2")
        + empty_socket(690, 400, "INT3")
        + G(NEW, patch(SUM[0] + 130, SUM[1], INT1[0] - 110, INT1[1] - 16)
            + patch(INT1[0] + 130, INT1[1], 36, SUM[1] - 16, via_y=48)
            + f'<line x1="36" y1="{SUM[1]-16}" x2="{SUM[0]-120}" y2="{SUM[1]-16}"/>'
            + f'<use href="#dot" x="{SUM[0]-120}" y="{SUM[1]-16}"/>'
            + T(360, 44, "patch  ẋ = −x   ·   do not solder", 12, NEW))
        + T(20, 28, "Week 2 = week 1 + one patch cord.", 13, NEW)
    )
    return svg("0 0 860 480", body, "Week 2 chassis")

def chassis_w3():
    body = (
        bay(20, 40, 820, 460, "computer")
        + G(INK, summer(*SUM) + integrator(*INT1, label="INT1") + inverter(*INV)
            + patch(SUM[0] + 130, SUM[1], INT1[0] - 110, INT1[1] - 16)
            + patch(INT1[0] + 130, INT1[1], 36, SUM[1] - 16, via_y=48)
            + f'<line x1="36" y1="{SUM[1]-16}" x2="{SUM[0]-120}" y2="{SUM[1]-16}"/>'
            + f'<use href="#dot" x="{SUM[0]-120}" y="{SUM[1]-16}"/>')
        + empty_socket(*INT2, "INT2")
        + empty_socket(690, 400, "INT3")
        + G(NEW, f'''
          <line x1="{INT1[0]+8}" y1="{INT1[1]+56}" x2="{INT1[0]+40}" y2="{INT1[1]+56}"/>
          <use href="#cap" x="{INT1[0]+52}" y="{INT1[1]+56}"/>
          <line x1="{INT1[0]+62}" y1="{INT1[1]+56}" x2="{INT1[0]+90}" y2="{INT1[1]+56}"/>
          {T(INT1[0]+50, INT1[1]+74, "Cc  Fig 3.1", 11, NEW)}
        ''')
        + T(20, 28, "Week 3 = week 2 + default Cc on INT1. Patch unchanged.", 13, NEW)
    )
    return svg("0 0 860 500", body, "Week 3 chassis")

def chassis_w4():
    body = (
        bay(20, 40, 900, 460, "computer")
        + G(INK, summer(*SUM) + integrator(*INT1, label="INT1") + inverter(*INV) + f'''
          <line x1="{INT1[0]+8}" y1="{INT1[1]+56}" x2="{INT1[0]+40}" y2="{INT1[1]+56}"/>
          <use href="#cap" x="{INT1[0]+52}" y="{INT1[1]+56}"/>
          <line x1="{INT1[0]+62}" y1="{INT1[1]+56}" x2="{INT1[0]+90}" y2="{INT1[1]+56}"/>
        ''')
        + G(NEW, integrator(*INT2, label="INT2", vout="x")
            + patch(SUM[0] + 130, SUM[1], INT1[0] - 110, INT1[1] - 16)
            + patch(INT1[0] + 130, INT1[1], INT2[0] - 110, INT2[1] - 16)
            + patch(INT2[0] + 130, INT2[1], SUM[0] - 120, SUM[1] - 50, via_y=48)
            + T(480, 44, "SUM → INT1 → INT2 → SUM    ẍ , ẋ , x", 12, NEW))
        + empty_socket(690, 400, "INT3")
        + T(20, 28, "Week 4 = week 3 + INT2 in the reserved socket + a second-order patch.", 13, NEW)
    )
    return svg("0 0 940 500", body, "Week 4 chassis")

def chassis_w5():
    body = (
        bay(20, 40, 900, 460, "computer")
        + bay(930, 40, 330, 300, "plant · not patched to the computer")
        + G(INK, summer(*SUM) + integrator(*INT1, label="INT1") + integrator(*INT2, label="INT2")
            + inverter(*INV)
            + patch(SUM[0] + 130, SUM[1], INT1[0] - 110, INT1[1] - 16)
            + patch(INT1[0] + 130, INT1[1], INT2[0] - 110, INT2[1] - 16)
            + patch(INT2[0] + 130, INT2[1], SUM[0] - 120, SUM[1] - 50, via_y=48))
        + empty_socket(690, 400, "INT3")
        + G(NEW, plant(*PLT, label="Fig 5.3"))
        + T(20, 28, "Week 5 = week 4 + the regulator on the unused end. Two systems, one board.", 13, NEW)
    )
    return svg("0 0 1280 520", body, "Week 5 chassis")

def chassis_w6():
    body = (
        bay(20, 40, 900, 260, "computer")
        + bay(930, 40, 330, 300, "plant")
        + bay(500, 300, 410, 230, "oscillator")
        + G(INK, summer(*SUM) + integrator(*INT1, label="INT1") + integrator(*INT2, label="INT2")
            + inverter(*INV) + plant(*PLT, label="Fig 5.3")
            + patch(SUM[0] + 130, SUM[1], INT1[0] - 110, INT1[1] - 16)
            + patch(INT1[0] + 130, INT1[1], INT2[0] - 110, INT2[1] - 16)
            + patch(INT2[0] + 130, INT2[1], SUM[0] - 120, SUM[1] - 50, via_y=48))
        + G(NEW, schmitt(*SCH) + integrator(*INT3, label="INT3", vin="vB", vout="vA")
            + patch(SCH[0] + 130, SCH[1], INT3[0] - 110, INT3[1] - 16, via_y=470)
            + patch(INT3[0] + 130, INT3[1], SCH[0] - 110, SCH[1] + 16, via_y=318)
            + T(560, 314, "vA ↻ Schmitt   vB → INT3", 12, NEW))
        + T(20, 28, "Week 6 = week 5 + Schmitt and INT3 as the function generator.", 13, NEW)
    )
    return svg("0 0 1280 560", body, "Week 6 chassis")

def int1_socket_box(label, fill_note="", color=None):
    x, y = INT1
    c = color or NEW
    return (
        f'<rect x="{x-130}" y="{y-90}" width="280" height="180" rx="6" '
        f'fill="#fff" stroke="{c}" stroke-width="1.8"/>'
        + T(x + 10, y - 74, label, 12, c, "middle")
        + T(x + 10, y + 4, fill_note, 11, INK, "middle")
    )

def chassis_w7():
    body = (
        bay(20, 40, 900, 260, "computer")
        + bay(930, 40, 330, 300, "plant")
        + bay(500, 300, 410, 230, "oscillator")
        + G(INK, summer(*SUM) + integrator(*INT2, label="INT2") + inverter(*INV)
            + plant(*PLT, label="Fig 5.3") + schmitt(*SCH)
            + integrator(*INT3, label="INT3", vin="vB", vout="vA")
            + patch(SUM[0] + 130, SUM[1], INT1[0] - 110, INT1[1] - 16)
            + patch(INT1[0] + 130, INT1[1], INT2[0] - 110, INT2[1] - 16)
            + patch(INT2[0] + 130, INT2[1], SUM[0] - 120, SUM[1] - 50, via_y=48)
            + patch(SCH[0] + 130, SCH[1], INT3[0] - 110, INT3[1] - 16, via_y=470)
            + patch(INT3[0] + 130, INT3[1], SCH[0] - 110, SCH[1] + 16, via_y=318))
        + G(NEW, int1_socket_box("INT1 socket · IC pulled", "Fig 7.4 pair only  ·  C stays")
            + f'''
          <use href="#npn" x="{INT1[0]-40}" y="{INT1[1]+10}"/>
          <use href="#npnr" x="{INT1[0]+50}" y="{INT1[1]+10}"/>
          <line x1="{INT1[0]-70}" y1="{INT1[1]+10}" x2="{INT1[0]-40}" y2="{INT1[1]+10}"/>
          <line x1="{INT1[0]+80}" y1="{INT1[1]+10}" x2="{INT1[0]+50}" y2="{INT1[1]+10}"/>
        ''')
        + T(20, 28, "Week 7 = week 6, but INT1’s IC is gone. Only the input pair lives in that socket.", 13, NEW)
    )
    return svg("0 0 1280 560", body, "Week 7 chassis")

def chassis_w8():
    body = (
        bay(20, 40, 900, 260, "computer")
        + bay(930, 40, 330, 300, "plant")
        + bay(500, 300, 410, 230, "oscillator")
        + G(INK, summer(*SUM) + integrator(*INT2, label="INT2") + inverter(*INV)
            + plant(*PLT, label="Fig 5.3") + schmitt(*SCH)
            + integrator(*INT3, label="INT3", vin="vB", vout="vA")
            + patch(SUM[0] + 130, SUM[1], INT1[0] - 110, INT1[1] - 16)
            + patch(INT1[0] + 130, INT1[1], INT2[0] - 110, INT2[1] - 16)
            + patch(INT2[0] + 130, INT2[1], SUM[0] - 120, SUM[1] - 50, via_y=48)
            + patch(SCH[0] + 130, SCH[1], INT3[0] - 110, INT3[1] - 16, via_y=470)
            + patch(INT3[0] + 130, INT3[1], SCH[0] - 110, SCH[1] + 16, via_y=318)
            + int1_socket_box("INT1 socket", "")
            + f'''
          <use href="#npn" x="{INT1[0]-50}" y="{INT1[1]-10}"/>
          <use href="#npnr" x="{INT1[0]+10}" y="{INT1[1]-10}"/>
        ''')
        + G(NEW, f'''
          <use href="#pnp" x="{INT1[0]+40}" y="{INT1[1]-20}"/>
          <use href="#npn" x="{INT1[0]+70}" y="{INT1[1]+20}"/>
          <use href="#pnp" x="{INT1[0]+70}" y="{INT1[1]+55}"/>
          {T(INT1[0]+10, INT1[1]+80, "+ Q3 + complementary out", 11, NEW, "middle")}
        ''')
        + T(20, 28, "Week 8 = week 7 pair + second stage + complementary output. Socket is an op-amp again.", 13, NEW)
    )
    return svg("0 0 1280 560", body, "Week 8 chassis")

def chassis_w9():
    body = (
        bay(20, 40, 900, 260, "computer")
        + bay(930, 40, 330, 300, "plant")
        + bay(500, 300, 410, 230, "oscillator")
        + G(INK, summer(*SUM) + integrator(*INT2, label="INT2") + inverter(*INV)
            + plant(*PLT, label="Fig 5.3") + schmitt(*SCH)
            + integrator(*INT3, label="INT3", vin="vB", vout="vA")
            + patch(SUM[0] + 130, SUM[1], INT1[0] - 110, INT1[1] - 16)
            + patch(INT1[0] + 130, INT1[1], INT2[0] - 110, INT2[1] - 16)
            + patch(INT2[0] + 130, INT2[1], SUM[0] - 120, SUM[1] - 50, via_y=48)
            + patch(SCH[0] + 130, SCH[1], INT3[0] - 110, INT3[1] - 16, via_y=470)
            + patch(INT3[0] + 130, INT3[1], SCH[0] - 110, SCH[1] + 16, via_y=318)
            + int1_socket_box("INT1 = Fig 9.1", "")
            + f'''
          <use href="#npn" x="{INT1[0]-50}" y="{INT1[1]-10}"/>
          <use href="#npnr" x="{INT1[0]+10}" y="{INT1[1]-10}"/>
          <use href="#pnp" x="{INT1[0]+40}" y="{INT1[1]-20}"/>
          <use href="#npn" x="{INT1[0]+70}" y="{INT1[1]+20}"/>
          <use href="#pnp" x="{INT1[0]+70}" y="{INT1[1]+55}"/>
        ''')
        + G(NEW, f'''
          <use href="#cap" x="{INT1[0]+20}" y="{INT1[1]+70}"/>
          {T(INT1[0]+20, INT1[1]+88, "Cc", 11, NEW, "middle")}
        ''')
        + T(20, 28, "Week 9 = week 8 amplifier + Cc. That assembly is Figure 9.1.", 13, NEW)
    )
    return svg("0 0 1280 560", body, "Week 9 chassis")

def chassis_w10():
    body = (
        bay(20, 40, 900, 260, "computer")
        + bay(930, 40, 330, 300, "plant")
        + bay(500, 300, 410, 230, "oscillator")
        + G(INK, summer(*SUM) + integrator(*INT2, label="INT2") + inverter(*INV)
            + plant(*PLT, label="Fig 5.3") + schmitt(*SCH)
            + integrator(*INT3, label="INT3", vin="vB", vout="vA")
            + patch(SUM[0] + 130, SUM[1], INT1[0] - 110, INT1[1] - 16)
            + patch(INT1[0] + 130, INT1[1], INT2[0] - 110, INT2[1] - 16)
            + patch(INT2[0] + 130, INT2[1], SUM[0] - 120, SUM[1] - 50, via_y=48)
            + patch(SCH[0] + 130, SCH[1], INT3[0] - 110, INT3[1] - 16, via_y=470)
            + patch(INT3[0] + 130, INT3[1], SCH[0] - 110, SCH[1] + 16, via_y=318)
            + int1_socket_box("INT1 = Fig 9.1 + 10.9", "")
            + f'''
          <use href="#npn" x="{INT1[0]-50}" y="{INT1[1]-10}"/>
          <use href="#npnr" x="{INT1[0]+10}" y="{INT1[1]-10}"/>
          <use href="#pnp" x="{INT1[0]+40}" y="{INT1[1]-20}"/>
          <use href="#npn" x="{INT1[0]+70}" y="{INT1[1]+20}"/>
          <use href="#pnp" x="{INT1[0]+70}" y="{INT1[1]+55}"/>
          <use href="#cap" x="{INT1[0]+20}" y="{INT1[1]+70}"/>
        ''')
        + G(NEW, f'''
          <use href="#pnp" x="{INT1[0]-20}" y="{INT1[1]-40}"/>
          <use href="#pnp" x="{INT1[0]+10}" y="{INT1[1]-40}"/>
          {T(INT1[0]+10, INT1[1]-52, "repeater", 10, NEW, "middle")}
        ''')
        + T(20, 28, "Week 10 = week 9 amp + Figure 10.9 current repeater as the first-stage load.", 13, NEW)
    )
    return svg("0 0 1280 560", body, "Week 10 chassis")

def chassis_w11():
    body = (
        bay(20, 40, 900, 240, "computer · three-mode")
        + bay(930, 40, 330, 300, "plant")
        + bay(500, 300, 410, 230, "oscillator")
        + G(INK, summer(*SUM) + integrator(*INT2, label="INT2") + inverter(*INV)
            + plant(*PLT, label="Fig 5.3") + schmitt(*SCH)
            + integrator(*INT3, label="INT3", vin="vB", vout="vA")
            + patch(SUM[0] + 130, SUM[1], INT1[0] - 110, INT1[1] - 16)
            + patch(INT1[0] + 130, INT1[1], INT2[0] - 110, INT2[1] - 16)
            + patch(INT2[0] + 130, INT2[1], SUM[0] - 120, SUM[1] - 50, via_y=48)
            + patch(SCH[0] + 130, SCH[1], INT3[0] - 110, INT3[1] - 16, via_y=470)
            + patch(INT3[0] + 130, INT3[1], SCH[0] - 110, SCH[1] + 16, via_y=318)
            + int1_socket_box("INT1 Fig 9.1", "discrete + repeater", INK))
        + G(NEW, f'''
          <use href="#sw" x="{INT1[0]-90}" y="{INT1[1]-16}"/>
          <use href="#sw" x="{INT2[0]-90}" y="{INT2[1]-16}"/>
          {T(INT1[0]-90, INT1[1]-28, "①②", 11, NEW)}
          {T(INT2[0]-90, INT2[1]-28, "①②", 11, NEW)}
        ''')
        + T(20, 28, "Week 11 = week 10 + reset/operate/hold switches on both integrators.", 13, NEW)
    )
    return svg("0 0 1280 560", body, "Week 11 chassis")

def chassis_w12():
    body = (
        bay(20, 40, 900, 240, "computer · patched for an ODE")
        + bay(930, 40, 330, 300, "plant + analog twin")
        + bay(500, 300, 410, 230, "oscillator = test input")
        + G(INK, summer(*SUM) + inverter(*INV) + plant(*PLT, label="Fig 5.3")
            + schmitt(*SCH) + int1_socket_box("INT1 Fig 9.1", "your amp", INK)
            + integrator(*INT2, label="INT2")
            + integrator(*INT3, label="INT3", vin="vB", vout="vA")
            + patch(SUM[0] + 130, SUM[1], INT1[0] - 110, INT1[1] - 16)
            + patch(INT1[0] + 130, INT1[1], INT2[0] - 110, INT2[1] - 16)
            + patch(INT2[0] + 130, INT2[1], SUM[0] - 120, SUM[1] - 50, via_y=48)
            + patch(SCH[0] + 130, SCH[1], INT3[0] - 110, INT3[1] - 16, via_y=470)
            + patch(INT3[0] + 130, INT3[1], SCH[0] - 110, SCH[1] + 16, via_y=318))
        + G(NEW, f'''
          <rect x="930" y="310" width="330" height="200" rx="4" fill="#fff"/>
          {mini_stage(1040, 400, "int", "twin")}
          {T(948, 330, "analog twin of Vl", 11, NEW)}
          {T(948, 500, "same ODE as Fig 5.3b · overlay on the scope", 11, NEW)}
        ''')
        + T(20, 28, "Week 12 = week 11, patched to run the ODE. Twin of the regulator sits beside the hardware.", 13, NEW)
    )
    return svg("0 0 1280 560", body, "Week 12 chassis")

def chassis_w13():
    body = (
        bay(20, 40, 900, 260, "computer")
        + bay(930, 40, 330, 300, "plant")
        + bay(500, 300, 410, 230, "oscillator")
        + G(INK, summer(*SUM) + int1_socket_box("INT1 Fig 9.1", "your amp", INK)
            + integrator(*INT2, label="INT2")
            + inverter(*INV) + plant(*PLT, label="Fig 5.3") + schmitt(*SCH)
            + integrator(*INT3, label="INT3", vin="vB", vout="vA")
            + patch(SUM[0] + 130, SUM[1], INT1[0] - 110, INT1[1] - 16)
            + patch(INT1[0] + 130, INT1[1], INT2[0] - 110, INT2[1] - 16)
            + patch(INT2[0] + 130, INT2[1], SUM[0] - 120, SUM[1] - 50, via_y=48)
            + patch(SCH[0] + 130, SCH[1], INT3[0] - 110, INT3[1] - 16, via_y=470)
            + patch(INT3[0] + 130, INT3[1], SCH[0] - 110, SCH[1] + 16, via_y=318))
        + G(NEW, f'''
          <line x1="{SUM[0]-20}" y1="{SUM[1]-16}" x2="{SUM[0]-20}" y2="{SUM[1]+50}"/>
          <use href="#resv" x="{SUM[0]-20}" y="{SUM[1]+70}"/>
          <line x1="{SUM[0]-20}" y1="{SUM[1]+90}" x2="{SUM[0]-20}" y2="{SUM[1]+100}"/>
          <use href="#capv" x="{SUM[0]-20}" y="{SUM[1]+110}"/>
          <use href="#gnd" x="{SUM[0]-20}" y="{SUM[1]+120}"/>
          {T(SUM[0]-8, SUM[1]+74, "lag 13.1", 10, NEW)}
          <use href="#cap" x="{INT1[0]+40}" y="{INT1[1]+40}"/>
          {T(INT1[0]+40, INT1[1]+56, "Cc", 11, NEW, "middle")}
          <line x1="{PLT[0]+40}" y1="{PLT[1]+50}" x2="{PLT[0]+90}" y2="{PLT[1]+50}"/>
          <use href="#cap" x="{PLT[0]+102}" y="{PLT[1]+50}"/>
          <use href="#res" x="{PLT[0]+140}" y="{PLT[1]+50}"/>
          <use href="#cap" x="{PLT[0]+178}" y="{PLT[1]+50}"/>
          {T(PLT[0]+100, PLT[1]+70, "Fig 13.19", 10, NEW)}
        ''')
        + T(20, 28, "Week 13 = week 12 + two compensation recipes on the same hardware.", 13, NEW)
    )
    return svg("0 0 1280 560", body, "Week 13 chassis")


WEEKS = [
    dict(
        id="w1", title="Week 1 — computing core lands",
        lineage="Start. Three ICs. Two empty sockets.",
        added=["Figure 1.2a inverter (INV)", "Figure 1.4 summer (SUM)", "§1.2.3 integrator (INT1)", "Empty reserved sockets INT2, INT3"],
        cards=[
            ("The box so far", "everything this week is new", [chassis_w1()],
             "Build all three. Measure each Vo/Vi. Do not patch an ODE yet."),
        ],
    ),
    dict(
        id="w2", title="Week 2 — close ẋ = −x",
        lineage="Week 1 + one patch.",
        added=["Patch cord: INT1 output → SUM Vi1 → INT1 input", "No new amplifiers"],
        cards=[
            ("The box so far", "coral = the patch", [chassis_w2()],
             "Same three ICs. Time constant must be RC once |L| is large."),
        ],
    ),
    dict(
        id="w3", title="Week 3 — characterize the machine you already have",
        lineage="Week 2 + default Cc. Patch unchanged.",
        added=["Cc on INT1’s LM301A (Figure 3.1, two values — keep the better one)", "No new sockets"],
        cards=[
            ("The box so far", "coral = Cc", [chassis_w3()],
             "Step and ramp the same ẋ = −x patch. The computer’s error is this transient."),
        ],
    ),
    dict(
        id="w4", title="Week 4 — second integrator, second-order loop",
        lineage="Week 3 + INT2 in the reserved socket + a new patch.",
        added=["INT2 (identical to INT1) in the empty socket", "Patch SUM → INT1 → INT2 → SUM"],
        cards=[
            ("The box so far", "coral = INT2 and the new loop", [chassis_w4()],
             "The computer can ring. Measure L of the patched loop, not of a textbook plant."),
        ],
    ),
    dict(
        id="w5", title="Week 5 — plant on the unused end",
        lineage="Week 4 + Figure 5.3. Not connected to the computer.",
        added=["Error amp ao", "Series NPN, emitter R, RL || CL, Id test sink", "Optional lead/lag on the computer only if week 4 still rings"],
        cards=[
            ("The box so far", "coral = the regulator", [chassis_w5()],
             "Two systems, one chassis. Jacks sit next to each other. Do not patch them together yet."),
            ("New module · Figure 5.3a", "§5.2.2", [
                svg("0 0 720 320", G(NEW, plant(200, 130, "Fig 5.3")), "Figure 5.3 close-up")
            ], "VR to +. Vl sensed to −. Series pass, load RL || CL. Id is a load-step sink."),
        ],
    ),
    dict(
        id="w6", title="Week 6 — test oscillator on the patchbay",
        lineage="Week 5 + Schmitt + INT3.",
        added=["Figure 12.7 Schmitt", "INT3 becomes the triangle generator", "Loop: vA → Schmitt → vB → INT3"],
        cards=[
            ("The box so far", "coral = oscillator", [chassis_w6()],
             "Computer and plant stay as they were. The oscillator is the machine’s signal source, not a throwaway."),
            ("New module · Figure 12.7a", "positive feedback to +", [
                svg("0 0 640 220", G(NEW, schmitt(300, 120)), "Schmitt close-up")
            ], "Thresholds ±(R1/R2)VM. − is grounded."),
        ],
    ),
    dict(
        id="w7", title="Week 7 — pull INT1’s IC, start the discrete pair",
        lineage="Week 6, except INT1’s IC is gone. Pair + C only.",
        added=["Pull the INT1 IC", "Figure 7.4 long-tailed pair + current-source tail in that socket", "Balance with Figure 7.10 (collector pot, not the emitter pot)"],
        cards=[
            ("The box so far", "coral = INT1 socket after the IC comes out", [chassis_w7()],
             "SUM, INT2, INV, plant, oscillator still run on ICs. Hold time of C is now this pair’s IB."),
            ("Inside the INT1 socket this week", "Figure 7.4 · this is all that is in there", [
                svg("0 0 500 280", pair_only(NEW) + G(NEW, f'''
                  <line x1="40" y1="140" x2="20" y2="140"/>
                  <line x1="20" y1="140" x2="20" y2="270"/>
                  <line x1="20" y1="270" x2="400" y2="270"/>
                  <use href="#cap" x="220" y="270"/>
                  <line x1="400" y1="270" x2="400" y2="104"/>
                  {T(208, 258, "C still on the socket", 11, NEW)}
                '''), "Week 7 INT1 interior")
            ], "No second stage yet. C stays. Watch it wander in hold — that is this week’s computer error."),
            ("Balance · Figure 7.10", "add this pot across the two collector loads", [
                svg("0 0 520 280", G(INK, """
                  <line x1="80" y1="40" x2="80" y2="70"/>
                  <use href="#resv" x="80" y="90"/>
                  <line x1="80" y1="110" x2="80" y2="140"/>
                  <line x1="320" y1="40" x2="320" y2="70"/>
                  <use href="#resv" x="320" y="90"/>
                  <line x1="320" y1="110" x2="320" y2="140"/>
                  <use href="#npn" x="64" y="176"/>
                  <use href="#npnr" x="336" y="176"/>
                  <line x1="80" y1="212" x2="80" y2="240"/>
                  <line x1="320" y1="212" x2="320" y2="240"/>
                  <line x1="80" y1="240" x2="320" y2="240"/>
                """) + G(NEW, f"""
                  <line x1="80" y1="40" x2="320" y2="40"/>
                  <use href="#res" x="200" y="40"/>
                  <line x1="200" y1="16" x2="200" y2="40"/>
                  <use href="#dot" x="200" y="40"/>
                  {T(210, 20, "+Vc  pot wiper", 12, NEW)}
                  {T(188, 28, "R", 11, NEW)}
                """), "Figure 7.10")
            ], "Coral is the only new part on last week’s pair. Short the bases, null vo, remove the short."),
        ],
    ),
    dict(
        id="w8", title="Week 8 — finish that same channel",
        lineage="Week 7 pair + Figure 8.8 + 8.13 + 8.27.",
        added=["PNP CE second stage (Q3) on Q2’s collector", "Current-source load in place of R1 (Figure 8.13)", "Complementary output (Figure 8.27) so the socket can drive C again"],
        cards=[
            ("The box so far", "coral = stages added behind last week’s pair", [chassis_w8()],
             "INT1 is a complete discrete op-amp again. Close C and it is an integrator."),
            ("Inside the INT1 socket this week", "week 7 pair in black · new stages in coral", [
                svg("0 0 760 380", pair_plus_stages("stages") + c_feedback(NEW)
                    + G(NEW, T(20, 18, "black = week 7 pair and rails   ·   coral = C closed around a finished amp", 12, NEW)),
                    "Week 8 INT1 interior")
            ], "Same Q1/Q2 you built last week. Q3, the current-source load, the complementary pair, and C are new. The socket must accept C and look like an op-amp."),
        ],
    ),
    dict(
        id="w9", title="Week 9 — that channel is now Figure 9.1",
        lineage="Week 8 amplifier + Cc. Then C goes back.",
        added=["Cc (Figure 9.10 / 9.12 data)", "Temporary Figure 9.8 inverter close for the Ch 9 measurements", "Then put C back — INT1 is your amp for the rest of the project"],
        cards=[
            ("The box so far", "coral = Cc on last week’s amp", [chassis_w9()],
             "Nothing else on the chassis moves. Repeat the week-2 ẋ = −x step through this amp. Compare hold time to the IC you pulled."),
            ("INT1 socket = week 8 + Cc", "Figure 9.1", [
                svg("0 0 760 380", pair_plus_stages("cc") + c_feedback(INK)
                    + G(NEW, T(20, 18, "black = week 8   ·   coral = Cc", 12, NEW)),
                    "Week 9 INT1 as integrator")
            ], "This is last week’s circuit. The only new component is Cc."),
            ("Measurement hookup · Figure 9.8", "same amp, C lifted, resistive feedback for the Ch 9 data", [
                svg("0 0 760 360", pair_plus_stages("cc") + r_feedback_inverter(NEW)
                    + G(NEW, T(20, 18, "C is off. Z1/Z2 are on. Take Fig 9.10 steps vs Cc and Fig 9.12 slew. Then restore C.", 12, NEW)),
                    "Figure 9.8 inverter test")
            ], "Do not leave it as an inverter. The computer needs the capacitor back."),
        ],
    ),
    dict(
        id="w10", title="Week 10 — current repeater on the same amp",
        lineage="Week 9 Figure 9.1 + Figure 10.9 in place of the simple CS load.",
        added=["Figure 10.9 current repeater as first-stage load", "Optional Figure 10.25 FET followers on INT2 only"],
        cards=[
            ("The box so far", "coral = repeater on INT1", [chassis_w10()],
             "INT2 is still an IC (maybe FET-fronted). Hold-time ratio is IB."),
            ("INT1 socket = week 9 + repeater", "Figure 10.9 replaces the single PNP load", [
                svg("0 0 760 380", pair_plus_stages("mirror") + c_feedback(INK)
                    + G(NEW, T(20, 18, "black = week 9 amp   ·   coral = Qref / Qout repeater", 12, NEW)),
                    "Week 10 INT1 interior")
            ], "Same Q1–Q3 and complementary pair. The first-stage load is now a pair of PNPs with the reference diode-connected."),
        ],
    ),
    dict(
        id="w11", title="Week 11 — reset / operate / hold",
        lineage="Week 10 + Figure 12.17 switches on both integrators.",
        added=["Operate switch ① and reset switch ② on INT1 and INT2", "Figure 11.18 precision rectifier stays on the chassis"],
        cards=[
            ("The box so far", "coral = mode switches", [chassis_w11()],
             "The discrete amp does not move. You wrap FET switches around C."),
            ("New around each integrator · Figure 12.17", "week 10 integrator in black · switches in coral", [
                svg("0 0 720 300", G(INK, integrator(360, 130, label="INT", vin="vB", vout="Vo")) + G(NEW, f"""
                  <line x1="40" y1="230" x2="80" y2="230"/>
                  <use href="#res" x="100" y="230"/>
                  <line x1="120" y1="230" x2="150" y2="230"/>
                  <use href="#sw" x="168" y="230"/>
                  <line x1="182" y1="230" x2="250" y2="230"/>
                  <use href="#dot" x="250" y="230"/>
                  <line x1="250" y1="230" x2="250" y2="114"/>
                  <line x1="250" y1="230" x2="300" y2="230"/>
                  <use href="#res" x="320" y="230"/>
                  <line x1="340" y1="230" x2="460" y2="230"/>
                  <line x1="460" y1="230" x2="460" y2="130"/>
                  <use href="#sw" x="168" y="114"/>
                  {T(8, 226, "vA", 12, NEW)}
                  {T(150, 216, "② reset", 11, NEW)}
                  {T(150, 100, "① operate", 11, NEW)}
                  {T(308, 216, "R2", 11, NEW)}
                """), "Figure 12.17 on an existing integrator")
            ], "Operate: ① closed, ② open. Reset: ① open, ② closed → Vo = −vA. Hold: both open."),
            ("Also keep · Figure 11.18", "precision rectifier", [
                svg("0 0 640 220", G(NEW, """
                  <use href="#oa" x="260" y="120"/>
                  <line x1="40" y1="104" x2="80" y2="104"/>
                  <use href="#res" x="100" y="104"/>
                  <line x1="120" y1="104" x2="260" y2="104"/>
                  <use href="#dot" x="180" y="104"/>
                  <line x1="334" y1="120" x2="380" y2="120"/>
                  <use href="#diode" x="380" y="120"/>
                  <line x1="394" y1="120" x2="500" y2="120"/>
                  <use href="#dot" x="450" y="120"/>
                  <line x1="450" y1="120" x2="450" y2="48"/>
                  <line x1="450" y1="48" x2="200" y2="48"/>
                  <use href="#res" x="180" y="48"/>
                  <line x1="160" y1="48" x2="180" y2="48"/>
                  <line x1="180" y1="48" x2="180" y2="104"/>
                  <line x1="244" y1="136" x2="260" y2="136"/>
                  <use href="#gnd" x="244" y="136"/>
                """) + T(272, 112, "−", 16) + T(272, 144, "+", 16) + T(528, 124, "Vo ≥ 0", 13),
                    "Precision rectifier")
            ], "Needed later if you add Wien amplitude control."),
        ],
    ),
    dict(
        id="w12", title="Week 12 — run the two problems",
        lineage="Week 11 hardware, new patches. No new amplifiers required.",
        added=["Patch Figure 12.13 (or 12.14) on the existing blocks", "Analog twin of Figure 5.3 beside the real plant", "Oscillator from week 6 is the test input"],
        cards=[
            ("The box so far", "coral = analog twin of the regulator", [chassis_w12()],
             "This is the finished function. Week 13 only makes it faster and quieter."),
            ("Problem 1a patch · Figure 12.13", "same five blocks, one feedback", [
                svg("0 0 820 220",
                    G(INK,
                      mini_stage(80, 130, "int", "SUM+INT")
                      + mini_stage(230, 130, "int", "INT")
                      + mini_stage(380, 130, "int", "INT")
                      + mini_stage(530, 130, "int", "INT")
                      + mini_stage(680, 130, "inv", "INV")
                      + f'''
                  <line x1="170" y1="130" x2="186" y2="130"/>
                  <line x1="186" y1="130" x2="186" y2="114"/>
                  <use href="#dot" x="186" y="114"/>
                  <line x1="320" y1="130" x2="336" y2="130"/>
                  <line x1="336" y1="130" x2="336" y2="114"/>
                  <use href="#dot" x="336" y="114"/>
                  <line x1="470" y1="130" x2="486" y2="130"/>
                  <line x1="486" y1="130" x2="486" y2="114"/>
                  <use href="#dot" x="486" y="114"/>
                  <line x1="620" y1="130" x2="636" y2="130"/>
                  <line x1="636" y1="130" x2="636" y2="114"/>
                  <use href="#dot" x="636" y="114"/>
                ''')
                    + G(NEW, f'''
                  <line x1="770" y1="130" x2="800" y2="130"/>
                  <line x1="800" y1="130" x2="800" y2="24"/>
                  <line x1="800" y1="24" x2="36" y2="24"/>
                  <line x1="36" y1="24" x2="36" y2="114"/>
                  <use href="#dot" x="36" y="114"/>
                '''),
                    "Butterworth patch")
            ], "Coral is only the closing patch. The five triangles are sockets you already have."),
        ],
    ),
    dict(
        id="w13", title="Week 13 — compensate the assembled box",
        lineage="Week 12 + two recipes. Same computer, same plant, same discrete amp.",
        added=["Figure 13.1 input lag on SUM / INV ICs", "Cc on the Figure 9.1 channel (§13.3.2)", "Figure 13.19 two-pole on the regulator error amp after you have measured L"],
        cards=[
            ("The box so far", "coral = compensation parts", [chassis_w13()],
             "Raise time-scale α until it breaks. Fix L. Raise it again."),
        ],
    ),
]


HEAD = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Roberge one-box — schematics</title>
  <link rel="stylesheet" href="design-system/colors_and_type.css">
  <style>
    * { box-sizing: border-box; }
    html, body { margin: 0; }
    body { background: var(--book); color: var(--slate); padding-bottom: 48px; }
    .deck { max-width: 1100px; margin: 0 auto; padding: 0 24px 48px; }
    @media (min-width: 1100px) { .deck { padding: 0 40px 64px; } }
    .top { display: flex; align-items: center; gap: 10px; padding: 20px 0 8px; }
    .top img { width: 22px; height: 22px; }
    .top .eyebrow { margin: 0; }
    h1.display { margin: 8px 0 12px; font-size: clamp(32px, 6vw, 48px); }
    .lede { margin: 0 0 16px; max-width: 44rem; }
    .legend {
      display: flex; flex-wrap: wrap; gap: 16px; margin: 0 0 20px;
      font-size: 13px; color: var(--fg-muted);
    }
    .legend span { display: inline-flex; align-items: center; gap: 8px; }
    .swatch { width: 22px; height: 3px; display: inline-block; }
    .swatch.old { background: #1F1E1D; }
    .swatch.new { background: #D97757; }
    .swatch.empty { background: repeating-linear-gradient(90deg, #B4B3AC 0 4px, transparent 4px 8px); height: 2px; }
    nav.jump { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 32px; }
    nav.jump a {
      font-family: var(--font-sans); font-size: 13px; padding: 6px 10px;
      border: 1px solid var(--hairline); border-radius: var(--r-sm);
      background: var(--bg-elev); text-decoration: none; color: var(--fg);
    }
    nav.jump a:hover { color: var(--accent-hover); }
    h2 { margin: 56px 0 6px; scroll-margin-top: 16px; }
    .lineage { margin: 0 0 10px; color: var(--crail-deep); font-size: 15px; }
    .added { margin: 0 0 16px; padding-left: 1.2rem; max-width: 44rem; }
    .added li { margin: 0 0 4px; }
    .card {
      background: var(--bg-elev); border: 1px solid var(--hairline);
      border-radius: var(--r-md); padding: 16px 16px 12px; margin: 0 0 16px;
    }
    .card h3 { font-family: var(--font-serif); font-weight: 400; font-size: 20px; margin: 0 0 4px; }
    .tag { font-family: var(--font-mono); font-size: 11px; color: var(--crail-deep); margin: 0 0 12px; }
    .note { font-size: 14px; color: var(--fg-muted); margin: 10px 0 0; }
    svg.sch {
      width: 100%; height: auto; display: block; background: #fff;
      border-radius: var(--r-xs); border: 1px solid var(--hairline);
    }
    .back { font-family: var(--font-sans); font-size: 14px; }
  </style>
</head>
<body>
  <svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
    <defs>
      <g id="oa" fill="#fff" stroke="currentColor" stroke-width="1.8" stroke-linejoin="miter">
        <polygon points="0,-40 0,40 74,0"/>
      </g>
      <g id="res" fill="#fff" stroke="currentColor" stroke-width="1.8">
        <rect x="-20" y="-8" width="40" height="16" rx="1.2"/>
      </g>
      <g id="resv" fill="#fff" stroke="currentColor" stroke-width="1.8">
        <rect x="-8" y="-20" width="16" height="40" rx="1.2"/>
      </g>
      <g id="cap" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="butt">
        <line x1="-5" y1="-12" x2="-5" y2="12"/>
        <line x1="5" y1="-12" x2="5" y2="12"/>
      </g>
      <g id="capv" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="butt">
        <line x1="-12" y1="-5" x2="12" y2="-5"/>
        <line x1="-12" y1="5" x2="12" y2="5"/>
      </g>
      <g id="gnd" fill="currentColor" stroke="currentColor" stroke-width="1.8" stroke-linejoin="miter">
        <line x1="0" y1="0" x2="0" y2="14"/>
        <polygon points="-6.5,14 6.5,14 0,26"/>
      </g>
      <g id="dot" fill="currentColor" stroke="none">
        <circle cx="0" cy="0" r="2.8"/>
      </g>
      <g id="varr" fill="currentColor" stroke="currentColor" stroke-width="1.5" stroke-linejoin="miter">
        <line x1="0" y1="10" x2="0" y2="-16"/>
        <polygon points="-4,-10 4,-10 0,-18"/>
      </g>
      <g id="diode" fill="#fff" stroke="currentColor" stroke-width="1.8" stroke-linejoin="miter">
        <polygon points="0,-8 0,8 14,0"/>
        <line x1="14" y1="-8" x2="14" y2="8"/>
      </g>
      <g id="npn" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="miter">
        <line x1="0" y1="0" x2="16" y2="0"/>
        <line x1="16" y1="-13" x2="16" y2="13" stroke-width="2.6"/>
        <line x1="16" y1="-10" x2="16" y2="-36"/>
        <line x1="16" y1="10" x2="16" y2="36"/>
        <polygon points="12,22 20,22 16,31" fill="currentColor" stroke="none"/>
      </g>
      <g id="pnp" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="miter">
        <line x1="0" y1="0" x2="16" y2="0"/>
        <line x1="16" y1="-13" x2="16" y2="13" stroke-width="2.6"/>
        <line x1="16" y1="-36" x2="16" y2="-10"/>
        <line x1="16" y1="10" x2="16" y2="36"/>
        <polygon points="12,-22 20,-22 16,-13" fill="currentColor" stroke="none"/>
      </g>
      <g id="npnr" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="miter">
        <line x1="0" y1="0" x2="-16" y2="0"/>
        <line x1="-16" y1="-13" x2="-16" y2="13" stroke-width="2.6"/>
        <line x1="-16" y1="-10" x2="-16" y2="-36"/>
        <line x1="-16" y1="10" x2="-16" y2="36"/>
        <polygon points="-20,22 -12,22 -16,31" fill="currentColor" stroke="none"/>
      </g>
      <g id="sw" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
        <line x1="-14" y1="0" x2="-2" y2="0"/>
        <circle cx="-2" cy="0" r="2.2" fill="#fff"/>
        <line x1="-2" y1="0" x2="10" y2="-10"/>
        <circle cx="14" cy="0" r="2.2" fill="#fff"/>
        <line x1="16" y1="0" x2="14" y2="0"/>
      </g>
    </defs>
  </svg>

  <div class="deck">
    <header>
      <div class="top">
        <img src="design-system/anthropic-mark.svg" alt="">
        <p class="eyebrow">Visual guide · one chassis</p>
      </div>
      <h1 class="display">The box, week by week</h1>
      <p class="lede">One board. Each week is last week plus the coral parts. Flip week 8 → 9 → 10 and watch INT1 grow.</p>
      <div class="legend">
        <span><i class="swatch old"></i> already on the box</span>
        <span><i class="swatch new"></i> added this week</span>
        <span><i class="swatch empty"></i> reserved empty socket</span>
      </div>
      <p class="back"><a href="capstone.html">Back to the build log</a></p>
    </header>
'''


def main():
    nav = '    <nav class="jump">\n' + "\n".join(
        f'      <a href="#{w["id"]}">{w["id"][1:]}</a>' for w in WEEKS
    ) + "\n    </nav>\n"

    body = [HEAD, nav]
    for w in WEEKS:
        body.append(f'    <h2 id="{w["id"]}">{w["title"]}</h2>\n')
        body.append(f'    <p class="lineage">{w["lineage"]}</p>\n')
        body.append(added(w["added"]))
        for title, tag, svgs, note in w["cards"]:
            body.append(card(title, tag, svgs, note))

    body.append('    <p class="back"><a href="capstone.html">Back to the build log</a></p>\n')
    body.append("  </div>\n</body>\n</html>\n")
    out = Path("/mnt/c/users/simon/Downloads/op_amps_roberge/schematics.html")
    out.write_text("".join(body), encoding="utf-8")
    print("wrote", out, "bytes", out.stat().st_size)


if __name__ == "__main__":
    main()
