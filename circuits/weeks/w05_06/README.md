# Weeks 5–6 cumulative circuit package

`graph.json` extends the approved Weeks 0–4 graph. It adds the physical REG1 plant in Week 5 and the persistent OSC1/INT3 source in Week 6. The two review configurations contain only the active weekly experiment at full visual weight; inherited hardware remains present and inactive.

`case-manifest.json` gives the nine Week 5 RL/CL combinations and the external plant-input safety boundary. Symbolic `RL_CASE` and `CL_CASE` labels in the structural schematic/netlist refer to this manifest.

Generated SVG, structural SPICE, and connectivity receipts are under `generated/weeks05_06/`. Performance simulation uses separately recorded topology-tier model cards and never presents generic device behavior as historical LM301A/BD139/1N47xx performance.

The standalone review surface is `week05-06-review.html`. `generated/weeks05_06/proof/summary.json` records checked numerical outcomes. The Week 6 topology proof uses an explicit 10 mV capacitor initial condition with transient `UIC` solely to break the ideal oscillator's exact zero-state symmetry; it adds no hidden electrical component.
