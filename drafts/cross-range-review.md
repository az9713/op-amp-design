# Cross-range cumulative-project review

**Reviewed:** `spec-weeks-00-04.md`, `spec-weeks-05-09.md`, and `spec-weeks-10-13.md`  
**Scope:** physical inheritance, stable identities, configuration boundaries, hardware counts, infrastructure, and later-week consequences  
**Verdict:** **REQUEST CHANGES BEFORE GATE 0.** The drafts are strong as range-local research notes, but they do not yet describe one mechanically mergeable project state.

## Summary

| Severity | Count | Meaning here |
|---|---:|---|
| BLOCKER | 8 | A canonical cumulative graph cannot be authored honestly until resolved. |
| MAJOR | 7 | A later state, configuration, or verification result would otherwise be ambiguous. |
| MINOR | 3 | Consistency work that should be completed with the merge. |

The most important positive result is that the drafts consistently preserve the user's central rule: physical hardware accumulates, inactive hardware remains visible, mutually exclusive experiments receive separate configurations, and the schematic/netlist pair must project from the same graph. Week 7's nonfunctional state is especially honest and should be preserved.

## BLOCKER findings

### B-01 — The three ranges use three incompatible identity systems

**Evidence:** Weeks 0–4 reserve `AC.*`, `INF.*`, `N_*`, `P15_*`, `N15_*`, `SGND`, and `PGND`. Weeks 5–9 rename inherited objects to `CORE.*` and infrastructure to `INFRA.VP15/VN15/AGND`. Weeks 10–13 rename them again to `CMP-*`, `PLANT-*`, `SRC-*`, `VCC_15/VEE_15/AGND`, and underscore-style ports. Component identity drifts too: `AC.INT1.U3` becomes `CORE.INT1.U_OP`, while its capacitor is variously `CFB3`, `CORE.INT1.C_INT`, and `C_INT1`.

**Risk:** an equivalence checker would see different components and nets rather than inherited hardware. `PGND` also disappears, risking accidental use of signal ground for the regulator/load return.

**Smallest honest resolution:** freeze one global identity dictionary before graph authoring. Prefer the earliest stable physical identities and map later prose to them; do not implement aliases as extra electrical nets. At minimum the dictionary must distinguish:

| Physical identity | Range-local names that must collapse to it |
|---|---|
| inverter module | `AC.INV1` / `CORE.INV1` / `CMP-INV1` |
| summer module | `AC.SUM1` / `CORE.SUM1` / `CMP-SUM1` |
| INT1 passive/socket channel | `AC.INT1` / `CORE.INT1` / `CMP-INT1` |
| INT2 passive/socket channel | `AC.INT2` / `CORE.INT2` / `CMP-INT2` |
| regulator | `REG1` / `PLANT-REG1` |
| oscillator | `OSC1` / `SRC-OSC1` |
| positive/negative signal rails | one canonical pair; all other spellings are presentation labels only |
| grounds | preserve separate `SGND` and `PGND` plus the single Week 0 net tie |

INT1 additionally needs separate stable identities for its socket/interface, stock LM301A, passive integrator network, and later `AMP1`; treating all four as one `CMP-INT1` object cannot express Week 7's removal correctly.

### B-02 — Week 2 has no approved circuit, and its sign choice propagates through Weeks 3 and 9

**Evidence:** the capstone asks for `xdot = -x` using the existing summer and integrator. The Week 2 draft correctly finds that an inverting summer followed by an inverting integrator gives the wrong sign, and provisionally inserts `INV1`. Week 3 inherits the unchanged Week 2 loop. Week 9-C says to repeat the Week 2 response without restating the complete loop graph.

**Risk:** approving the wrong two-block sign produces exponential growth, while silently adding `INV1` contradicts the current curriculum wording. Every inherited loop net from W2 through W3 and the W9-C regression depends on this choice.

**Smallest honest resolution:** approve one of the two already identified electrically correct choices: direct INT1 self-feedback, or the three-block `SUM1 -> INV1 -> INT1` chain. Then assign one persistent configuration ID and exact endpoint list, and have W3 and W9-C explicitly inherit that same configuration graph. Do not retain the unsupported two-block SUM+INT claim.

### B-03 — Week 12 assumes the fixed Week 1 blocks are freely reconfigurable, but their hardware does not support that yet

**Evidence:** Week 1 defines a fixed resistor-feedback `AC.SUM1` and a fixed unity inverter `AC.INV1`. W12-BW turns `CMP-SUM1` into an integrating summer and uses the inverter as `BW_COMB`, which must sum `x` and `d2x/dt2` with coefficients. No Week 12 delta adds or selects the required feedback capacitor and coefficient networks, and calling this only "configuration wiring" is not sufficient for the fixed passive networks defined in Week 1.

**Risk:** the Butterworth hardware count looks sufficient only by silently changing two installed modules' internal electrical graphs.

**Smallest honest resolution:** keep the existing op amps and all prior passives physically installed, but add explicit W12 selectable/patchable passive networks: an integrating-feedback capacitor and coefficient inputs for the first integrating summer, and the required multi-input coefficient network for `BW_COMB`. Each unused earlier resistor path must be explicitly open in `W12-BW`. Alternatively, redefine the Week 1 blocks now as patchable op-amp cells with externally selectable impedances; that is a larger project-wide decision and must still preserve each component ID.

### B-04 — The Week 5 regulator is still symbolic, but Weeks 12 and 13 depend on its exact graph

**Evidence:** W5 leaves regulator voltage/current, pass-device polarity, current source/load injector, protection, thermal limits, and loop-injection topology TBD. W12-REG-TWIN must derive its equation and signs from that plant. W13-FIXED-CLOAD and W13-TWOPOLE-REG1 require its output impedance, load pole, error-amplifier compensation ports, and measured loop.

**Risk:** three later configurations could be internally coherent yet model or compensate a different regulator than the one physically built.

**Smallest honest resolution:** resolve the W5 plant graph and its operating envelope before accepting the W12 twin or either regulator compensation configuration. Values may remain symbolic where justified, but pass-device polarity, reference/output relationship, load/disturbance path, protection boundary, `SGND`/`PGND` returns, error-amplifier pins, and loop-break endpoints cannot remain symbolic connections.

### B-05 — The dedicated Week 6 oscillator integrator must be made a global decision

**Evidence:** W6 proposes `OSC1.U_INT` because INT1 is dismantled in W7 and INT2 must remain the stock comparison channel. This becomes even more necessary in W12-REG-TWIN, where the persistent oscillator must drive a load step while the computing blocks implement the twin.

**Risk:** "reuse an integrator" is not compatible with simultaneous later use unless the oscillator has its own retained integrator. Deferring the choice corrupts hardware counts, rail loading, bypass allocation, and W7/W12 active-state descriptions.

**Smallest honest resolution:** approve the draft's dedicated `OSC1.U_INT` interpretation. Record it as a new persistent op-amp channel first installed in W6, with its own bypass/compensation identities. Note explicitly that this is the minimal implementation addition needed to satisfy persistence and simultaneous Week 12 operation.

### B-06 — W7 -> W8 -> W9 -> W10 lacks one exact replacement map

**Evidence:** W7 removes the stock INT1 op amp and adds Q1/Q2/Q3 plus temporary collector loads. W8 admits that Figures 8.8, 8.13, and 8.27 do not define one coherent circuit. W9 removes temporary parts and converts the assembly to Figure 9.1. W10 then describes a current repeater "adaptation" at the first-stage load but does not identify which Figure 9.1 device(s) or connection it replaces.

**Risk:** the sequence can only be drawn by inventing connections. W10 in particular is not necessarily a pure addition; adding a current repeater in parallel with the Figure 9.1 load could be electrically wrong.

**Smallest honest resolution:** require a single component/pin/net transition table with four columns (W7, W8, W9, W10) before any of these graphs is implemented. Every row must be `retained`, `added`, `removed-off-circuit`, `temporary-removed`, or `reconnected`. Preserve Q1/Q2/Q3 only where their pin mapping is exact. W10 must explicitly identify the replaced Figure 9.1 load element/path; call it a replacement if that is what the accepted topology requires.

### B-07 — The Week 12 regulator twin has no physical ownership or count

**Evidence:** the cumulative delta says to add `TWIN-REG1`, while its proposed submodules are `TWIN-SUM1` and `TWIN-INT1`. It does not say whether these are new physical amplifiers or configuration roles played by the retained computer modules. Yet the same configuration must run beside `REG1` and be driven by persistent `OSC1`.

**Risk:** the chassis manifest and Week 0 load budget differ materially between a dedicated twin and a re-patched computing core. A block-only `TWIN-REG1` would also violate the build-ready requirement.

**Smallest honest resolution:** because W12 configurations are already separate, define `TWIN-REG1` as a configuration namespace over named retained computing modules and newly installed coefficient passives, unless the curriculum explicitly requires dedicated twin amplifiers. If dedicated hardware is required, inventory every amplifier/passive and add it to the W12 physical delta. Do not leave `TWIN-SUM1`/`TWIN-INT1` as unowned abstract blocks.

### B-08 — Week 0 protection and supply distribution cannot close without a total hardware manifest

**Evidence:** W0 correctly defers fuse/current-limit selection until Weeks 5–13 loads are inventoried. The later drafts add one W5 error amplifier, two W6 oscillator amplifiers, W11 reset followers and a rectifier amplifier, W12 INT3, two unspecified physical multipliers, and possibly dedicated twin amplifiers. The discrete amplifier, pass transistor, gate drivers, rectifier load, and multiplier implementation add further rail current.

**Risk:** Gate 0 cannot honestly approve branch protection, connector rating, decoupling zones, optional 22-ohm rail isolation, or dummy-load acceptance without this inventory.

**Smallest honest resolution:** add a week-by-week physical hardware manifest and symbolic worst-case rail-load expression. Do not select unsupported currents yet; identify every load and source its maximum later. W0 fuse/protection values remain a downstream freeze item, but the topology and allocation of local bypass positions must cover every accepted persistent channel.

## MAJOR findings

### M-01 — The Week 3 compensation selector disappears during the INT1 replacement

`AC.INT1.CCSEL3` is installed and retained from W3, but W7 removes the LM301A and W9 introduces new `AMP1.COMP_A/B` and `AMP1.CC`. Specify whether the W3 selector remains physically installed but electrically open, is removed, or is deliberately repurposed after pin/interface verification. Never connect a selector wired for LM301A compensation pins to `AMP1` merely because both are called compensation terminals.

### M-02 — W5's conditional lead/lag state is unresolved and can collide with W13

W6 inherits "any explicitly retained" W5 computer compensation, but W5 never decides retained, switchable, or removed. W13 later installs input lag on a summer as a new campaign. Freeze the W5 outcome as one of: not installed; installed removable and open in baseline; or installed selector with named states. W13 must reuse that physical network if electrically identical, or add a separately identified network; it must not silently duplicate or erase it.

### M-03 — W11's phrase "both installed integrators" is false after the recommended W6 decision

The chassis then contains at least the two computing integrators plus `OSC1.U_INT`. Rewrite W11 as "both computing-core integrators (`INT1` and `INT2`)". The oscillator integrator remains retained and inactive, not converted to reset/operate/hold.

### M-04 — Socket and off-circuit artifact identities are not stable

W1 installs INT2/INT3 sockets, W4 appears to replace `AC.INT2.SOCKET` with `AC.INT2`, W7 introduces an INT1 socket identity not reserved in W1, and W12 replaces the INT3 socket name with `CMP-INT3`. Define sockets as permanent mechanical/electrical objects from their installation week; insertion/removal changes the occupant state, not the socket ID. The removed LM301A should remain in the physical inventory as an off-circuit artifact but must not appear as an electrical instance.

### M-05 — W9-C does not explicitly restore the complete approved W2 loop

It restores the INT1 resistor/capacitor but only refers narratively to repeating `xdot=-x`. Once B-02 is resolved, W9-C must list every intermodule endpoint inherited from W2 and the status of W9-A/B resistors. This prevents the inverter test resistor and integration capacitor from appearing simultaneously.

### M-06 — Week 12 hardware counts omit the implementation cost of functional blocks

The "one new integrator, not two" conclusion is sound for the Butterworth op-amp count, but the physical delta must also count: the new INT3 socket occupant and any mode hardware; Butterworth selectable passives; two multiplier implementations and their support amplifiers/carrier/filter circuitry; test points; and any dedicated twin circuitry. Keep functional configuration counts separate from total physical rail-load counts.

### M-07 — Week 13 campaigns are separate but not yet complete active circuits

`W13-FIXED-LAG` names a "selected" summer/inverter, `W13-ONEPOLE-LM301A` names a "selected" LM301A channel, and the capacitive-load case is conditional. Before graph authoring, name the exact retained DUT and complete feedback loop for each configuration. If Figure 13.7/13.8 is inapplicable to the accepted regulator, mark that configuration not installed rather than including its parts in the Week 13 cumulative end state. The two campaign families must also declare all one-pole capacitors open whenever the regulator two-pole network owns the same compensation terminals.

## MINOR findings

### m-01 — Naming syntax itself is inconsistent

Dots, hyphens, and underscores are all used as hierarchy delimiters. After B-01, adopt one machine-readable syntax and reserve display labels for typography. This will simplify delta and equivalence reports.

### m-02 — Temporary fixtures need one state class

Loop injectors, W7 collector-load diagnostics, W8 servos, W9 inverter resistors, and Figure 11.2 measurement networks are variously called temporary, configuration-specific, or removable. Give all of them a uniform `fixture/configuration-only` state so they are present in the matched schematic/netlist for that configuration but excluded from the persistent hardware delta unless physically retained.

### m-03 — Active/grey presentation must not suppress powered inactive hardware from the graph

The drafts generally state this correctly. Make it an explicit merge invariant: grey is a rendering attribute only. Installed inactive modules retain rails, bypassing, and safe input/output terminations in the cumulative physical graph; an experiment projection may omit their internal detail but not their physical existence.

## Required merge artifacts before Gate 0

1. **Global identity registry:** stable module, component, socket, pin, and net names, including `SGND`/`PGND` and the Week 0 net tie.
2. **Week-by-week physical manifest:** installed, populated, removed-off-circuit, and configuration-only objects, with an unresolved symbolic rail-load budget.
3. **Configuration registry:** exact active configurations and mutually exclusive states for W1–W13, including separate W12 and W13 configurations already approved by the user.
4. **Transition tables:** at minimum W1 socket population, W3 compensation, W7–W10 `AMP1`, W11 mode hardware, W12 core-block reconfiguration, and W13 compensation selection.
5. **Dependency order:** resolve W2 sign; approve dedicated W6 oscillator integrator; bind the W5 regulator graph; bind W7–W10 transitions; then freeze W12 twin/multiplier ownership and W13 DUTs. Protection values and realistic models follow the accepted physical manifest.

No unsupported resistor, capacitor, transistor, protection, or compensation value needs to be invented to resolve these structural findings.

