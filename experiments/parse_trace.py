#!/usr/bin/env python3
"""Parse an nOBS/ns-2 old-format raw trace without scenario-specific constants.

The parser deliberately reports only facts observable in the trace.  In
particular, an OP_BURST line does not expose hdr_burst::burst_id/type/flow;
control/data pairing is reconstructed from the allocation order proved by
op-burst_agent.cc and validated against every pair's trace fields.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator, TextIO

EVENTS = {"+", "-", "r", "d"}


class TraceFormatError(ValueError):
    """A non-empty input line is not the expected 12-field trace format."""


@dataclass(frozen=True)
class Address:
    node: int
    port: int

    @classmethod
    def parse(cls, value: str, line_number: int) -> "Address":
        try:
            node, port = value.rsplit(".", 1)
            return cls(int(node), int(port))
        except (ValueError, AttributeError) as exc:
            raise TraceFormatError(
                f"line {line_number}: invalid address {value!r}"
            ) from exc


@dataclass(frozen=True)
class Event:
    kind: str
    time: float
    from_node: int
    to_node: int
    packet_type: str
    size_bytes: int
    flags: str
    flow_id: int
    source: Address
    destination: Address
    sequence_number: int
    packet_uid: int
    line_number: int

    @property
    def is_legal_transport_receive(self) -> bool:
        """True only at the transport packet's declared destination node."""
        return (
            self.kind == "r"
            and self.packet_type in {"tcp", "ack"}
            and self.to_node == self.destination.node
        )


def parse_line(line: str, line_number: int) -> Event | None:
    fields = line.split()
    if not fields:
        return None
    if len(fields) != 12:
        raise TraceFormatError(
            f"line {line_number}: expected 12 fields, found {len(fields)}"
        )
    kind = fields[0]
    if kind not in EVENTS:
        raise TraceFormatError(f"line {line_number}: unknown event {kind!r}")
    try:
        time = float(fields[1])
        if not math.isfinite(time) or time < 0:
            raise ValueError
        event = Event(
            kind=kind,
            time=time,
            from_node=int(fields[2]),
            to_node=int(fields[3]),
            packet_type=fields[4],
            size_bytes=int(fields[5]),
            flags=fields[6],
            flow_id=int(fields[7]),
            source=Address.parse(fields[8], line_number),
            destination=Address.parse(fields[9], line_number),
            sequence_number=int(fields[10]),
            packet_uid=int(fields[11]),
            line_number=line_number,
        )
    except ValueError as exc:
        if isinstance(exc, TraceFormatError):
            raise
        raise TraceFormatError(f"line {line_number}: invalid numeric field") from exc
    if event.size_bytes < 0 or event.packet_uid < 0:
        raise TraceFormatError(f"line {line_number}: negative size or packet UID")
    return event


def iter_events(stream: TextIO) -> Iterator[Event]:
    for line_number, line in enumerate(stream, 1):
        event = parse_line(line, line_number)
        if event is not None:
            yield event


def _address_text(address: Address) -> str:
    return f"{address.node}.{address.port}"


def _is_optical_event(event: Event) -> bool:
    """Recognize optical bursts across NS-2 packet-name table variants.

    Some native NS-2 trees print PT_OP_BURST as ``undefined`` because their
    packet-name table is not aligned with the overlay.  The trace-visible
    optical signature remains stable: sequence number -1 and an optical
    destination with port -1.  Keep OP_BURST as the primary form and accept
    only this narrow legacy fallback.
    """
    return event.packet_type == "OP_BURST" or (
        event.packet_type == "undefined"
        and event.sequence_number == -1
        and event.destination.port == -1
    )


def _same_burst_pair(control: Event, data: Event) -> bool:
    """Validate fields copied to both packets by BurstAgent::recv."""
    return (
        data.packet_uid + 1 == control.packet_uid
        and _is_optical_event(data)
        and _is_optical_event(control)
        and data.size_bytes > control.size_bytes
        and data.from_node == control.from_node
        and data.to_node == control.to_node
        and data.flow_id == control.flow_id
        and data.source == control.source
        and data.destination == control.destination
        and data.sequence_number == control.sequence_number == -1
        and control.time <= data.time
    )


def analyze(
    events: Iterable[Event], direct_control_uids: set[int] | None = None,
    delivered_direct_control_uids: set[int] | None = None,
    forbidden_direct_control_uids: set[int] | None = None,
) -> dict:
    direct_control_uids = set() if direct_control_uids is None else set(direct_control_uids)
    delivered_direct_control_uids = (
        set() if delivered_direct_control_uids is None
        else set(delivered_direct_control_uids)
    )
    forbidden_direct_control_uids = (
        set() if forbidden_direct_control_uids is None
        else set(forbidden_direct_control_uids)
    )
    if not delivered_direct_control_uids <= direct_control_uids:
        raise TraceFormatError("delivered direct-BHP UIDs are not a subset of traced UIDs")
    if direct_control_uids & forbidden_direct_control_uids:
        raise TraceFormatError("direct-BHP traced and forbidden UID sets overlap")
    event_counts: Counter[str] = Counter()
    packet_type_event_counts: dict[str, Counter[str]] = defaultdict(Counter)
    first_time: float | None = None
    last_time: float | None = None
    line_count = 0

    # UID is hdr_cmn::uid(), the only per-packet identity serialized by Trace.
    by_uid: dict[int, list[Event]] = defaultdict(list)
    legal_transport: dict[str, dict[int, Event]] = {
        "tcp": {},
        "ack": {},
    }
    drops_by_type: Counter[str] = Counter()

    for event in events:
        line_count += 1
        event_counts[event.kind] += 1
        packet_type_event_counts[event.packet_type][event.kind] += 1
        first_time = event.time if first_time is None else min(first_time, event.time)
        last_time = event.time if last_time is None else max(last_time, event.time)
        by_uid[event.packet_uid].append(event)
        if event.kind == "d":
            drops_by_type[event.packet_type] += 1
        if event.is_legal_transport_receive:
            prior = legal_transport[event.packet_type].get(event.packet_uid)
            if prior is not None:
                raise TraceFormatError(
                    f"lines {prior.line_number}/{event.line_number}: duplicate legal "
                    f"receive for UID {event.packet_uid}"
                )
            legal_transport[event.packet_type][event.packet_uid] = event

    first_optical: dict[int, Event] = {}
    for uid, history in by_uid.items():
        optical = [event for event in history if _is_optical_event(event)]
        if optical:
            first_optical[uid] = optical[0]

    # BurstAgent allocates data then control; data is UID n, control UID n+1.
    # Pair solely when all copied trace-visible fields and order agree.
    pairs: list[tuple[Event, Event]] = []
    paired_uids: set[int] = set()
    for data_uid in sorted(first_optical):
        data = first_optical[data_uid]
        control = first_optical.get(data_uid + 1)
        if control is not None and _same_burst_pair(control, data):
            if data_uid in paired_uids or data_uid + 1 in paired_uids:
                raise TraceFormatError(f"ambiguous optical pairing near UID {data_uid}")
            pairs.append((control, data))
            paired_uids.update((data_uid, data_uid + 1))

    forbidden_present = sorted(forbidden_direct_control_uids & set(first_optical))
    if forbidden_present:
        sample = ", ".join(map(str, forbidden_present[:8]))
        raise TraceFormatError(
            f"blocked direct-BHP controls present in optical trace: {len(forbidden_present)} "
            f"UIDs (sample: {sample})"
        )
    direct_not_delivered = sorted(
        uid for uid in delivered_direct_control_uids
        if not any(
            event.kind == "r" and event.to_node == event.destination.node
            for event in by_uid[uid]
            if _is_optical_event(event)
        )
    )
    if direct_not_delivered:
        sample = ", ".join(map(str, direct_not_delivered[:8]))
        raise TraceFormatError(
            f"direct-BHP controls not delivered to declared destination: "
            f"{len(direct_not_delivered)} UIDs (sample: {sample})"
        )
    unpaired = sorted(set(first_optical) - paired_uids - direct_control_uids)
    if unpaired:
        sample = ", ".join(map(str, unpaired[:8]))
        raise TraceFormatError(
            f"cannot prove control/data pairing for {len(unpaired)} optical UIDs "
            f"(sample: {sample})"
        )

    offered_bytes = sent_bytes = dropped_bytes = 0
    offered_packets = sent_packets = dropped_packets = 0
    burst_drop_uids: list[int] = []
    control_failed_uids: list[int] = []
    control_delivered = 0
    successful_link_reservations = 0
    flow_bursts: Counter[str] = Counter()
    flow_offered_bytes: Counter[str] = Counter()

    for control, data in pairs:
        data_history = by_uid[data.packet_uid]
        control_history = by_uid[control.packet_uid]
        offered_packets += 1
        offered_bytes += data.size_bytes
        flow_key = f"{_address_text(data.source)}->{_address_text(data.destination)}"
        flow_bursts[flow_key] += 1
        flow_offered_bytes[flow_key] += data.size_bytes

        data_drops = [event for event in data_history if event.kind == "d"]
        if data_drops:
            dropped_packets += 1
            dropped_bytes += data.size_bytes
            burst_drop_uids.append(data.packet_uid)
        elif any(
            event.kind == "r" and event.to_node == data.destination.node
            for event in data_history
        ):
            sent_packets += 1
            sent_bytes += data.size_bytes

        # A control '+' is emitted only after OpSRAgent has obtained a link
        # reservation and forwarded the control packet to that link.
        successful_link_reservations += sum(
            event.kind == "+" for event in control_history
        )
        reached_control_destination = any(
            event.kind == "r" and event.to_node == control.destination.node
            for event in control_history
        )
        if reached_control_destination:
            control_delivered += 1

        # Failed reservation can be explicit `d` on control, or (as in this
        # build's head-drop path) control stops at a transit node and its paired
        # data is explicitly dropped on that node's attempted outgoing link.
        explicit_control_drop = any(
            event.kind == "d" for event in control_history
        )
        last_control = control_history[-1]
        paired_data_drop_after_control = any(
            last_control.kind == "r"
            and last_control.to_node != control.destination.node
            and drop.from_node == last_control.to_node
            and drop.time >= last_control.time
            for drop in data_drops
        )
        if explicit_control_drop or paired_data_drop_after_control:
            control_failed_uids.append(control.packet_uid)

    transport = {}
    for packet_type in ("tcp", "ack"):
        receives = legal_transport[packet_type]
        flow_packets: Counter[int] = Counter()
        flow_bytes: Counter[int] = Counter()
        for event in receives.values():
            flow_packets[event.flow_id] += 1
            flow_bytes[event.flow_id] += event.size_bytes
        transport[packet_type] = {
            "legal_receive_packets": len(receives),
            "legal_receive_bytes": sum(event.size_bytes for event in receives.values()),
            "flow_ids": sorted(flow_packets),
            "per_flow": {
                str(flow_id): {
                    "legal_receive_packets": flow_packets[flow_id],
                    "legal_receive_bytes": flow_bytes[flow_id],
                }
                for flow_id in sorted(flow_packets)
            },
        }

    return {
        "schema": "ns2-old-12-field",
        "trace": {
            "lines": line_count,
            "first_time_s": first_time,
            "last_time_s": last_time,
            "event_counts": dict(sorted(event_counts.items())),
            "packet_type_event_counts": {
                name: dict(sorted(counts.items()))
                for name, counts in sorted(packet_type_event_counts.items())
            },
            "drop_lines_by_packet_type": dict(sorted(drops_by_type.items())),
        },
        "transport": transport,
        "optical": {
            "burst_pairs": len(pairs),
            "control_packets_offered": len(pairs),
            "data_bursts_offered": offered_packets,
            "data_bytes_offered": offered_bytes,
            "data_bursts_sent_end_to_end": sent_packets,
            "data_bytes_sent_end_to_end": sent_bytes,
            "data_bursts_explicitly_dropped": dropped_packets,
            "data_bytes_explicitly_dropped": dropped_bytes,
            "data_burst_drop_ratio": (
                dropped_packets / offered_packets if offered_packets else None
            ),
            "control_packets_delivered_end_to_end": control_delivered,
            "control_link_reservations_attempted": (
                successful_link_reservations + len(control_failed_uids)
            ),
            "control_link_reservations_succeeded": successful_link_reservations,
            "control_link_reservations_failed": len(control_failed_uids),
            "control_packets_unresolved_at_trace_end": (
                len(pairs) - control_delivered - len(control_failed_uids)
            ),
            "explicitly_dropped_data_uids": burst_drop_uids,
            "failed_control_uids": control_failed_uids,
            "endpoint_flow_bursts": dict(sorted(flow_bursts.items())),
            "endpoint_flow_offered_bytes": dict(sorted(flow_offered_bytes.items())),
            "trace_ip_flow_ids": sorted(
                {data.flow_id for _, data in pairs}
            ),
        },
        "identity_notes": {
            "packet_uid": "field 12; unique packet identity across link events",
            "tcp_flow_id": "field 8 (hdr_ip::flowid/fid)",
            "optical_trace_flow_id": (
                "field 8, but not hdr_burst::flow; use endpoint tuple for "
                "trace-visible optical flow grouping"
            ),
            "burst_pair": "data UID n plus validated control UID n+1",
        },
    }


def parse_path(
    path: str | Path, direct_control_uids: set[int] | None = None,
    delivered_direct_control_uids: set[int] | None = None,
    forbidden_direct_control_uids: set[int] | None = None,
) -> dict:
    with Path(path).open("r", encoding="utf-8") as stream:
        return analyze(
            iter_events(stream),
            direct_control_uids=direct_control_uids,
            delivered_direct_control_uids=delivered_direct_control_uids,
            forbidden_direct_control_uids=forbidden_direct_control_uids,
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path, help="raw ns-2 out.tr")
    parser.add_argument(
        "--compact", action="store_true", help="emit compact rather than indented JSON"
    )
    args = parser.parse_args(argv)
    try:
        metrics = parse_path(args.trace)
    except (OSError, TraceFormatError) as exc:
        print(f"parse_trace.py: {exc}", file=sys.stderr)
        return 2
    json.dump(metrics, sys.stdout, indent=None if args.compact else 2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
