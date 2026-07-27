# Direct BHP control-path experiment

This harness drives the patched native NS-2.35+nOBS BHP admission path directly. The versioned `config.json` is the sole source of experiment topology, traffic, seed, and guard-profile parameters; `runner.py` serializes those values into the Tcl process environment.

## Files

- `config.json` — schema `nobs-direct-bhp-experiment-v1`, eight seeds and four scenario labels.
- `scenario.tcl` — native NS workload; it fails closed when a required value is absent or malformed.
- `runner.py` — cell selection, config snapshotting, native execution, artifact hashing, and post-run validation.
- `validator.py` — config, detector-boundary, audit-chain, artifact-hash, selected-cell, and full-matrix validation.

Run commands from `experiments/direct_bhp/`.

## Validate configuration and detector boundary

```bash
python3 validator.py --config config.json
```

The boundary check proves that `BhpObservation` has only the expected contemporaneous fields, that `bhp_guard_.observe(observation)` and the admission decision precede the reservation call, and that no explicit future/oracle field is wired into detector configuration.

## Single-cell native smoke

```bash
python3 runner.py \
  --config config.json \
  --out /tmp/direct-bhp-smoke \
  --seed 101 \
  --label S2_rate_limit
```

The output directory must not already contain files. Repeat `--seed` and `--label` to select more than one configured cell.

## Full 32-cell matrix

```bash
python3 runner.py \
  --config config.json \
  --out /path/to/direct-bhp-matrix
```

With no selectors, the runner requests all 8 × 4 configured cells. A successful run records `full_matrix_complete: true` only after every expected cell is present, successful, and validated.

## Validate retained results

Use the retained snapshot as the authoritative config:

```bash
python3 validator.py \
  --config /path/to/results/experiment_config.snapshot.json \
  --results /path/to/results \
  --output /path/to/results/revalidation.json
```

Validation fails closed on missing/extra selected cells, malformed native rows, unrecognized record widths, nonempty native suffix fields, broken `BHP_CREATE→OBSERVE→DECIDE→ACT` ordering, detector-boundary drift, metadata inconsistencies, and input or artifact hash mismatches.

## Retained artifacts

The result root retains:

- `experiment_config.snapshot.json`
- `matrix_manifest.json`
- `completion.json`
- `validation.json`

Each cell under `seed_<seed>/<label>/` retains:

- `out.tr`
- `stat.txt`
- `bhp_audit.log`
- `bhp_source.log`
- `stdout.log`
- `stderr.log`
- `command.txt`
- `run.json`, including input and artifact SHA-256 values

## Execution status for this implementation session

Only a limited native smoke was run during this implementation session. The complete 32-cell matrix was **not** run, and no full-matrix completion claim is made here.
