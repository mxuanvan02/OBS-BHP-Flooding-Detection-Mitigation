#!/usr/bin/env python3
"""Run a fail-closed S1 attack-rate sweep on retained NS-2.35+nOBS traces."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOBS_ROOT = HERE.parent
NS = NOBS_ROOT / "build/ns-allinone-2.35/ns-2.35/ns"
TCL = HERE / "scenario.tcl"
PARSER = HERE / "parse_trace.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    rates = tuple(float(x) for x in args.rates.split(","))
    if not rates or any(rate <= 0 for rate in rates):
        raise SystemExit("--rates must contain positive values")
    if args.seeds <= 0:
        raise SystemExit("--seeds must be positive")
    for required in (NS, TCL, PARSER):
        if not required.is_file():
            raise SystemExit(f"missing input: {required}")

    out = Path(args.out).resolve()
    if out.exists() and any(out.iterdir()) and not args.resume:
        raise SystemExit(f"refusing to overwrite non-empty output: {out}")
    out.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "nobs-s1-rate-sweep-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scenario": "S1",
        "rates_mbps_per_source": list(rates),
        "seeds": list(range(1, args.seeds + 1)),
        "expected_cells": len(rates) * args.seeds,
        "sim_time_s": args.sim_time,
        "environment": {
            "NOBS_LEGAL_FLOWS": args.legal_flows,
            "NOBS_LEGAL_ACCESS_MBPS": args.legal_access_mbps,
            "NOBS_ATTACKER_ACCESS_MBPS": args.attacker_access_mbps,
            "NOBS_OPTICAL_RATE_MBPS": args.optical_rate_mbps,
        },
        "input_sha256": {"scenario.tcl": sha256(TCL), "parse_trace.py": sha256(PARSER), "ns": sha256(NS)},
    }
    write_json(out / "sweep_manifest.json", manifest)
    env = os.environ.copy()
    env.update({
        "NOBS_LEGAL_FLOWS": str(args.legal_flows),
        "NOBS_LEGAL_ACCESS_MBPS": str(args.legal_access_mbps),
        "NOBS_ATTACKER_ACCESS_MBPS": str(args.attacker_access_mbps),
        "NOBS_OPTICAL_RATE_MBPS": str(args.optical_rate_mbps),
    })

    failures: list[str] = []
    attempted = 0
    successful = 0
    for rate in rates:
        rate_name = f"rate_{rate:g}"
        for seed in range(1, args.seeds + 1):
            attempted += 1
            cell = out / rate_name / f"seed_{seed}"
            cell.mkdir(parents=True, exist_ok=True)
            run_path = cell / "run.json"
            if args.resume and run_path.is_file():
                prior = json.loads(run_path.read_text(encoding="utf-8"))
                if prior.get("exit_code") == 0 and (cell / "metrics.json").is_file():
                    successful += 1
                    print(f"SKIP rate={rate:g} seed={seed}", flush=True)
                    continue
            command = [str(NS), str(TCL), "S1", str(seed), str(rate), str(args.sim_time), "none", "out.tr"]
            (cell / "command.txt").write_text(" ".join(command) + "\n", encoding="utf-8")
            print(f"RUN rate={rate:g} seed={seed}", flush=True)
            try:
                with (cell / "stdout.log").open("w", encoding="utf-8") as stdout, (cell / "stderr.log").open("w", encoding="utf-8") as stderr:
                    result = subprocess.run(command, cwd=cell, env=env, stdout=stdout, stderr=stderr, timeout=args.timeout, check=False)
                rc = result.returncode
            except subprocess.TimeoutExpired:
                rc = 124
            record = {"rate_mbps_per_source": rate, "seed": seed, "exit_code": rc, "sim_time_s": args.sim_time}
            trace = cell / "out.tr"
            if rc == 0 and trace.is_file():
                parsed = subprocess.run([sys.executable, str(PARSER), str(trace)], text=True, capture_output=True, check=False)
                if parsed.returncode == 0:
                    (cell / "metrics.json").write_text(parsed.stdout, encoding="utf-8")
                    record.update({"trace_bytes": trace.stat().st_size, "trace_sha256": sha256(trace), "metrics_sha256": sha256(cell / "metrics.json")})
                    successful += 1
                else:
                    rc = record["exit_code"] = 2
                    (cell / "parser.stderr.log").write_text(parsed.stderr, encoding="utf-8")
            if rc != 0:
                failures.append(f"rate={rate:g}/seed={seed}:rc={rc}")
            write_json(run_path, record)

    write_json(out / "completion.json", {
        "complete": not failures and attempted == len(rates) * args.seeds,
        "attempted_cells": attempted,
        "successful_cells": successful,
        "failed_cells": len(failures),
        "failures": failures,
    })
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--rates", default="5,10,15,20,25,30,35,40,45,50")
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--sim-time", type=float, default=5.0)
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--legal-flows", type=int, default=2)
    ap.add_argument("--legal-access-mbps", type=float, default=155.0)
    ap.add_argument("--attacker-access-mbps", type=float, default=155.0)
    ap.add_argument("--optical-rate-mbps", type=float, default=400.0)
    ap.add_argument("--resume", action="store_true")
    return run(ap.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
