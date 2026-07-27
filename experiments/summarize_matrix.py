import csv
import json
import pathlib
import sys


root = pathlib.Path(sys.argv[1])
rows = []
for path in sorted(root.glob("seed_*/*/metrics.json")):
    metrics = json.loads(path.read_text())
    name = path.parent.name
    if name.startswith("S2_rate_limit"):
        scenario, mitigation = "S2", "rate_limit"
    elif name.startswith("S2_isolation"):
        scenario, mitigation = "S2", "isolation"
    elif name.startswith("S1_"):
        scenario, mitigation = "S1", "none"
    else:
        scenario, mitigation = "S0", "none"

    transport = metrics["transport"]["tcp"]
    optical = metrics["optical"]
    rows.append(
        {
            "seed": path.parts[-3].split("_")[-1],
            "scenario": scenario,
            "mitigation": mitigation,
            "legal_packets": transport["legal_receive_packets"],
            "legal_bytes": transport["legal_receive_bytes"],
            "burst_offered": optical["data_bursts_offered"],
            "burst_sent": optical["data_bursts_sent_end_to_end"],
            "explicit_drop": optical["data_bursts_explicitly_dropped"],
        }
    )

if not rows:
    raise SystemExit("no metrics found")

with (root / "summary.csv").open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"rows={len(rows)}")
