# Direct-BHP matrix analysis

- Validated cells: 32/32
- Seeds: 101, 202, 303, 404, 505, 606, 707, 808
- S0 legal TCP bytes (mean): 50,623,120
- S1 legal TCP bytes (mean): 15,633,620 (69.12% below S0)
- S2 rate-limit legal TCP bytes: 50,623,120 (100.00% of S0)
- S2 isolation legal TCP bytes: 50,623,120 (100.00% of S0)
- Exact sign test: all 8 seeds show S1<S0 and both S2>S1; two-sided p=0.0078125 for each directional comparison.

## Claim boundary
- Intervals describe only the eight fixed seeds.
- The workload emits native direct control-only BHPs with absent data payload.
- The guard is a deterministic contemporaneous token-budget state machine, not a reconstructed ML detector.
- Legitimate nOBS controls do not enter the explicit direct-BHP guard path; zero collateral here is architectural scope, not an estimated false-positive rate.
- Claims are limited to the declared seven-node topology, traffic profile, and five-second runs.
