# Weeks 0–4 production decisions

Status: first review batch; not yet approved for insertion into `capstone.html`.

## Binding choices

- W00 uses an external isolated, regulated, current-limited ±15 V bench supply. No mains wiring is placed on the chassis sheet.
- PGND and SGND have exactly one declared tie. The two 3.3 kΩ dummy loads are temporary commissioning fixtures.
- W01 installs three LM301A computing channels: a unity inverter, an equal-weight summer, and a 10 ms inverting integrator. Each has 0.1 µF local rail bypassing and explicit compensation terminals on its detail sheet.
- W02 uses the approved three-block sign-correct loop `SUM1 → INV1 → INT1`, giving `dx/dt = −x/τ`, with `τ = 10 ms`. The source figures are conceptual authorities; this wiring is the approved engineering synthesis.
- W03 first reproduces the Figure 3.1 unity-inverter compensation comparison with 12 pF and 220 pF cases. It then restores the cumulative W02 loop and compares the same two compensation choices on INT1. The review end-state retains 220 pF on INT1 conservatively; this remains subject to measurement.
- W04 adds INT2 and implements `x'' + (0.2/τ)x' + x/τ² = 0`, with `τ = 10 ms`. A separate measurement configuration removes damping and inserts a declared 0 V DC / AC 1 series loop source.
- A 30 pF C0G capacitor is the normal LM301A single-pole compensation value unless a W03 comparison variant explicitly replaces it.
- 100 Ω output-jack isolation resistors are proposed build values, not claims copied from Roberge.

## Presentation split

The functional sheet collapses each LM301A core but shows the complete passive computing network and all inter-module experiment connections. Companion core-detail sheets expose the LM301A power, bypass, and compensation wiring. Both views are projections of the same graph; neither is a second electrical authority.

## Deliberately deferred

- physical patch-cord drawings and jack-panel routing;
- a low-voltage modern redesign (preserved as a distinct second project, not a modification of the ±15 V historical build);
- exact LM301A package/socket pin mapping until a sourced package selection is locked;
- realistic LM301A macromodel validation and tolerance/temperature simulation;
- internal mains supply, PCB layout, enclosure layout, and full protection sizing;
- final compensation selection until the specified transient tests are performed.

## Review boundary

`capstone.html` is intentionally unchanged. Approval of this batch authorizes later insertion; it does not happen automatically.
