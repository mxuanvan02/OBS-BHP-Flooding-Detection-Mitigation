from __future__ import annotations
import math
from dataclasses import dataclass
import numpy as np

@dataclass
class RunResult:
    scenario: str
    seed: int
    attack_rate_mbps: float
    legal_packets: int
    legal_bytes: int
    bursts_sent: int
    bursts_lost: int
    burst_loss_rate: float
    windows: list[dict]


def _window_stats(events, start, end, duration, attack_active):
    xs = [e for e in events if start <= e["t"] < end]
    legal = sum(e["legal_bytes"] for e in xs)
    attacker = sum(e["attack_bytes"] for e in xs)
    bursts = sum(e["bursts"] for e in xs)
    lost = sum(e["lost"] for e in xs)
    total = legal + attacker
    mean_rate = total * 8 / (end-start) / 1e6
    rates = np.array([e["attack_bytes"] * 8 / 1e6 / (end-start) for e in xs])
    variability = float(np.std(rates) / (np.mean(rates)+1e-12)) if len(rates) else 0.0
    return {"window_start": start, "window_end": end, "attack_label": int(attack_active),
            "legal_mbps": legal * 8 / 1e6 / (end-start), "aggregate_mbps": mean_rate,
            "attacker_mbps": attacker * 8 / 1e6 / (end-start), "burst_rate": bursts/(end-start),
            "burst_loss_rate": lost/max(bursts,1), "rate_cv": variability,
            "active_sources": int(any(e["attack_bytes"] > 0 for e in xs))}


def simulate(cfg: dict, scenario: str, seed: int, attack_rate_mbps: float | None = None) -> RunResult:
    sim = cfg["simulation"]; defense = cfg["defense"]; ass = cfg["assumptions"]
    rng = np.random.default_rng(seed)
    duration, dt = sim["duration_s"], sim["dt_s"]
    n = int(round(duration/dt)); attack_rate = attack_rate_mbps or sim["attacker_rate_mbps"]
    jitter = 1 + rng.uniform(-sim["rate_jitter"], sim["rate_jitter"])
    attack_rate *= jitter
    capacity = ass["background_capacity_mbps"]
    legal_rate = sim["legal_rate_mbps"]
    attacker = attack_rate * sim["attacker_count"] if scenario != "S0" else 0.0
    events=[]; total_legal_bytes=0; bursts=0; lost=0
    for i in range(n):
        t=i*dt; active=sim["attack_start_s"] <= t < sim["attack_stop_s"]
        offered_attack = attacker if active else 0.0
        allowed_attack = offered_attack
        if scenario == "S2_rate_limit" and t >= sim["attack_start_s"] + defense["detect_delay_s"]:
            allowed_attack = min(offered_attack, defense["cir_mbps"])
        elif scenario == "S2_isolation" and t >= sim["attack_start_s"] + defense["detect_delay_s"]:
            allowed_attack = defense["isolation_rate_mbps"]
        offered = legal_rate + allowed_attack
        contention = max(0.0, offered-capacity)/max(offered,1e-9)
        # Reservation starvation: legal traffic loses reservation before physical burst loss rises.
        legal_eff = legal_rate * max(0.0, 1.0 - 0.82*contention)
        if scenario == "S0": legal_eff = legal_rate * (0.985 + 0.01*rng.random())
        legal_eff *= 0.985 + 0.03*rng.random()
        lb = int(legal_eff*1e6/8*dt); ab = int(allowed_attack*1e6/8*dt)
        total = lb+ab
        b = int(total/max(ass["burst_bytes"],1))
        # Keep loss approximately low and independent of starvation.
        l = int(rng.binomial(max(b,0), 0.002))
        total_legal_bytes += lb; bursts += b; lost += l
        events.append({"t":t,"legal_bytes":lb,"attack_bytes":ab,"bursts":b,"lost":l})
    windows=[]; w=sim["window_s"]; start=0.0
    while start < duration-1e-12:
        end=min(duration,start+w)
        windows.append(_window_stats(events,start,end,duration, sim["attack_start_s"] <= start < sim["attack_stop_s"] and scenario != "S0"))
        start=end
    return RunResult(scenario, seed, attack_rate, int(total_legal_bytes/ass["legal_packet_bytes"]), total_legal_bytes, bursts, lost, lost/max(bursts,1), windows)
