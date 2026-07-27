# Reconstructed NS-2.35+nOBS scenarios

> **Practical-use gate:** the current pilot is an integration experiment, not
> yet a deployable BHP-flooding defense. UDP/CBR payload traffic causes nOBS to
> generate legitimate burst-control packets; it does not forge BHPs directly.
> Likewise, Tcl-scheduled source stopping is an oracle action rather than an
> online detector-actuator loop, and the stock per-source TBF is not yet proven
> to police the actual optical control path. Therefore pilot results must not be
> used to claim practical attack detection or mitigation. Expansion to the
> inferential matrix is blocked until the threat model, observation interface,
> control-path actuator, false-positive impact, latency, and overhead gates pass.

This directory is a source-only reconstructed experiment based on upstream
`sim20_7bmulti-cont.tcl`. It runs the already-built **real NS-2.35+nOBS v2.1
binary**, routes TCP and UDP packets into the nOBS source-routing agent and
burstifier, and writes the native text trace with `Simulator trace-all`.
It does not import or call the repository's Python simulator, and it does not
modify the nOBS binary.

## Scenarios and CLI

```text
ns scenario.tcl <scenario> <seed> <attack_rate_mbps> <sim_time_s> <mitigation> [trace_path]
```

Valid combinations:

- `S0 ... none`: two legal persistent TCP Reno/FTP flows, no attack.
- `S1 ... none`: legal flows plus eight UDP CBR attackers.
- `S2 ... rate_limit`: S1 plus a stock NS-2 TBF on each attacker, CIR 4 Mb/s.
- `S2 ... isolation`: attackers stop 0.25 s after their 0.10 s start.

`attack_rate_mbps` is the offered rate **per attacker**. The script validates
scenario/mitigation combinations and optional output trace path.

Example from this directory:

```bash
../build/ns-allinone-2.35/ns-2.35/ns scenario.tcl S1 1 12 0.6 none out.tr
```

## Topology and traffic

The optical core retains the seven-node T topology and optical facilities of
the nOBS example:

```text
0--1
   |
   2--3--4
   |
   6--5
```

Legal senders attach to optical ingress 0, legal receivers to egress 4, and
attackers to ingress 5. Explicit source routes cross the real nOBS core. A
received native trace must therefore contain both electronic `udp` records and
optical `OP_BURST` records for S1/S2.

## Pilot

Run one short seed for each concrete scenario:

```bash
./run_pilots.sh
```

Raw logs and traces are retained under `pilots/raw/{S0,S1,S2_rate_limit,S2_isolation}`.
The runner saves the exact shell command, stdout, stderr, exit code, trace size,
trace SHA-256, input SHA-256, and common pilot configuration. These pilots only
verify that the reconstructed Tcl scenario executes through nOBS; they are not
used to force or claim agreement with the thesis tables.

## Reconstructed assumptions and limits

The thesis and recovered source do not specify enough parameters to recreate
the original experiment. Every missing choice is labeled `reconstructed-assumption`
in `manifest.json`. Important assumptions are: two legal flows, 3 Mb/s legal
access links, 12 Mb/s per attacker for the pilot, 1000-byte packets, attack
start 0.10 s, one wavelength, nOBS example burst settings, and one per-attacker
TBF with a 32,000-bit bucket and 50-packet queue.

Only CIR=4 Mb/s is documented for mitigation. Missing PIR/CBS/PBS and color
policy mean the rate-limit scenario uses stock NS-2 single-rate TBF rather than
pretending to reproduce a complete RFC 2698 marker. Isolation is modeled by
stopping attack applications exactly 0.25 s after attack start. No parameter
is fitted to the thesis's reported numeric outcomes.

## Tests

```bash
python3 -m unittest tests.test_scenario -v
```

The six scenario tests inspect CLI/config invariants and perform a very short
real-binary smoke run. They do not parse or modify another agent's trace parser.
