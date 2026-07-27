import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPERIMENTS))

from parse_trace import TraceFormatError, analyze, iter_events, parse_line  # noqa: E402


SUCCESS_TRACE = """\
+ 0.0 7 0 tcp 1040 ------- 47 7.1 47.1 0 10
- 0.0 7 0 tcp 1040 ------- 47 7.1 47.1 0 10
r 0.001 7 0 tcp 1040 ------- 47 7.1 47.1 0 10
+ 0.008000 0 1 OP_BURST 40 ------- 0 0.1 4.-1 -1 12
- 0.008000 0 1 OP_BURST 40 ------- 0 0.1 4.-1 -1 12
+ 0.008045 0 1 OP_BURST 1080 ------- 0 0.1 4.-1 -1 11
- 0.008045 0 1 OP_BURST 1080 ------- 0 0.1 4.-1 -1 11
r 0.018000 3 4 OP_BURST 40 ------- 0 0.1 4.-1 -1 12
r 0.018045 3 4 OP_BURST 1080 ------- 0 0.1 4.-1 -1 11
+ 0.020 4 47 tcp 1040 ------- 47 7.1 47.1 0 10
- 0.020 4 47 tcp 1040 ------- 47 7.1 47.1 0 10
r 0.021 4 47 tcp 1040 ------- 47 7.1 47.1 0 10
"""

DROP_TRACE = """\
+ 1.000000 5 6 OP_BURST 40 ------- 0 5.1 4.-1 -1 22
- 1.000000 5 6 OP_BURST 40 ------- 0 5.1 4.-1 -1 22
+ 1.000045 5 6 OP_BURST 20840 ------- 0 5.1 4.-1 -1 21
- 1.000045 5 6 OP_BURST 20840 ------- 0 5.1 4.-1 -1 21
r 1.010000 5 6 OP_BURST 40 ------- 0 5.1 4.-1 -1 22
d 1.010045 6 2 OP_BURST 20840 ------- 0 5.1 4.-1 -1 21
"""


class ParseLineTests(unittest.TestCase):
    def test_old_trace_fields(self):
        event = parse_line(
            "r 0.04905 4 47 tcp 40 ------- 47 7.1 47.1 0 1218", 3
        )
        self.assertEqual(event.kind, "r")
        self.assertEqual(event.flow_id, 47)
        self.assertEqual(event.source.node, 7)
        self.assertEqual(event.destination.node, 47)
        self.assertEqual(event.packet_uid, 1218)
        self.assertTrue(event.is_legal_transport_receive)

    def test_transit_receive_is_not_legal_transport_receive(self):
        event = parse_line(
            "r 0.001002 7 0 tcp 40 ------- 47 7.1 47.1 0 1218", 1
        )
        self.assertFalse(event.is_legal_transport_receive)

    def test_rejects_bad_field_count_and_event(self):
        with self.assertRaises(TraceFormatError):
            parse_line("r 0.0 1", 1)
        with self.assertRaises(TraceFormatError):
            parse_line("x 0 1 2 tcp 40 ------- 1 1.1 2.1 0 3", 2)


class AnalysisTests(unittest.TestCase):
    def test_success_metrics_and_no_double_counting(self):
        result = analyze(iter_events(io.StringIO(SUCCESS_TRACE)))
        tcp = result["transport"]["tcp"]
        optical = result["optical"]
        self.assertEqual(tcp["legal_receive_packets"], 1)
        self.assertEqual(tcp["legal_receive_bytes"], 1040)
        self.assertEqual(tcp["flow_ids"], [47])
        self.assertEqual(optical["burst_pairs"], 1)
        self.assertEqual(optical["data_bursts_offered"], 1)
        self.assertEqual(optical["data_bytes_offered"], 1080)
        self.assertEqual(optical["data_bursts_sent_end_to_end"], 1)
        self.assertEqual(optical["data_bursts_explicitly_dropped"], 0)

    def test_explicit_burst_drop_and_failed_control_reservation(self):
        result = analyze(iter_events(io.StringIO(DROP_TRACE)))
        optical = result["optical"]
        self.assertEqual(optical["data_bursts_offered"], 1)
        self.assertEqual(optical["data_bursts_explicitly_dropped"], 1)
        self.assertEqual(optical["data_bytes_explicitly_dropped"], 20840)
        self.assertEqual(optical["control_link_reservations_failed"], 1)
        self.assertEqual(optical["explicitly_dropped_data_uids"], [21])

    def test_explicit_control_drop_is_failed_reservation(self):
        trace = DROP_TRACE.replace(
            "r 1.010000 5 6 OP_BURST 40 ------- 0 5.1 4.-1 -1 22",
            "d 1.010000 6 2 OP_BURST 40 ------- 0 5.1 4.-1 -1 22",
        )
        result = analyze(iter_events(io.StringIO(trace)))
        self.assertEqual(result["optical"]["control_link_reservations_failed"], 1)
        self.assertEqual(result["optical"]["failed_control_uids"], [22])

    def test_rejects_unprovable_optical_pair(self):
        bad = SUCCESS_TRACE.replace("0.1 4.-1 -1 12", "9.1 4.-1 -1 12")
        with self.assertRaisesRegex(TraceFormatError, "cannot prove"):
            analyze(iter_events(io.StringIO(bad)))

    def test_cli_json(self):
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "out.tr"
            path.write_text(SUCCESS_TRACE, encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(EXPERIMENTS / "parse_trace.py"), str(path)],
                check=True,
                text=True,
                capture_output=True,
            )
            result = json.loads(completed.stdout)
            self.assertEqual(result["schema"], "ns2-old-12-field")


if __name__ == "__main__":
    unittest.main()
