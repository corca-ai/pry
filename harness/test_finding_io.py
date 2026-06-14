"""Executable proof for finding_io.py (docs/spec-eval-harness.md Slice 1 step 2).

Drives the built CLI end-to-end on a synthetic `pry map` + tiny repo, the way
tests/exclude_smoke.rs drives the binary. Stdlib only (no pytest):

    python3 harness/test_finding_io.py        # or: python3 -m unittest -v ...

Pins:
  * emit blinds the verdict bit + applies PQ3 selection (census/sample/control);
  * the full panel -> reconcile -> freeze happy path, with group/precision
    recovered from the map (SC1/SC2);
  * AC1: reconcile AND freeze REFUSE (exit != 0) on an incomplete vote/label set;
  * the 1-1-1 -> tie-break escalation loop;
  * emit is byte-deterministic (Constraints / SC3-analog).
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "finding_io.py"

# Findings keyed so the test knows each id's true class (the worklist blinds it).
# 3 demand-welds (network, subprocess, + 4 clock that PQ3 samples down to 1),
# 3 demand-seamed (the control pool), 1 NON-demand weld (must be excluded).
MAP_FINDINGS = [
    {"file": "a.ts", "line": 5, "col": 2, "kind": "network",
     "class": "welded", "demand": True},
    {"file": "a.ts", "line": 10, "col": 2, "kind": "subprocess",
     "class": "welded", "demand": True},
    {"file": "a.ts", "line": 15, "col": 2, "kind": "clock",
     "class": "welded", "demand": True},
    {"file": "a.ts", "line": 16, "col": 2, "kind": "clock",
     "class": "welded", "demand": True},
    {"file": "a.ts", "line": 17, "col": 2, "kind": "clock",
     "class": "welded", "demand": True},
    {"file": "a.ts", "line": 18, "col": 2, "kind": "clock",
     "class": "welded", "demand": True},
    {"file": "a.ts", "line": 20, "col": 4, "kind": "network",
     "class": "seamed", "demand": True},
    {"file": "a.ts", "line": 21, "col": 4, "kind": "db",
     "class": "seamed", "demand": True},
    {"file": "a.ts", "line": 22, "col": 4, "kind": "fileio",
     "class": "seamed", "demand": True},
    {"file": "a.ts", "line": 25, "col": 2, "kind": "network",
     "class": "welded", "demand": False},  # non-demand: excluded
]


def _fid(r: dict) -> str:
    return f"{r['file']}:{r['line']}:{r['col']}:{r['kind']}"


class FindingIOTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pry-finding-io-"))
        # a source file long enough that every finding line has context
        (self.tmp / "a.ts").write_text(
            "".join(f"const line{n} = {n};\n" for n in range(1, 41))
        )
        self.map = self.tmp / "map.json"
        self.map.write_text(json.dumps(
            {"tool": "pry", "corpus": str(self.tmp), "findings": MAP_FINDINGS}))
        self.worklist = self.tmp / "worklist.json"
        self.reconciled = self.tmp / "reconciled.json"
        self.labels = self.tmp / "labels.json"
        self.by_id = {_fid(r): r for r in MAP_FINDINGS}

    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPT), *args],
                              capture_output=True, text=True)

    def emit(self) -> dict:
        cp = self.run_cli("emit", "--map", str(self.map), "--repo",
                          str(self.tmp), "--out", str(self.worklist))
        self.assertEqual(cp.returncode, 0, cp.stderr)
        return json.loads(self.worklist.read_text())

    def write_votes(self, persona: str, labels: dict[str, str]) -> None:
        (self.tmp / f"finding_verdicts.{persona}.json").write_text(json.dumps(
            {fid: {"label": lbl, "confidence": "high", "reason": "test"}
             for fid, lbl in labels.items()}))

    def reconcile(self) -> subprocess.CompletedProcess:
        return self.run_cli("reconcile", "--worklist", str(self.worklist),
                            "--eval-dir", str(self.tmp), "--out",
                            str(self.reconciled))

    def freeze(self) -> subprocess.CompletedProcess:
        return self.run_cli("freeze", "--model-id", "test-model", "--map",
                            str(self.map), "--worklist", str(self.worklist),
                            "--reconciled", str(self.reconciled), "--out",
                            str(self.labels))

    # --- the labels every persona assigns for the happy path ----------------
    def consensus_labels(self, worklist: dict) -> dict[str, str]:
        labels = {}
        for f in worklist["findings"]:
            cls = self.by_id[f["id"]]["class"]
            # welds -> GENUINE; one seamed-control flagged GENUINE (a false-seam)
            if cls == "welded":
                labels[f["id"]] = "GENUINE"
            elif f["id"].endswith("20:4:network"):
                labels[f["id"]] = "GENUINE"      # pry false-seamed this one
            else:
                labels[f["id"]] = "FALSE-WELD"
        return labels

    def test_emit_blinds_and_applies_pq3_selection(self) -> None:
        wl = self.emit()
        ids = {f["id"] for f in wl["findings"]}
        # blinding: no verdict bit leaks
        for f in wl["findings"]:
            self.assertNotIn("class", f)
            self.assertNotIn("demand", f)
            self.assertNotIn("input_sim", f)
            self.assertIn(">>", f["source_context"])  # location marker only
        # non-demand weld excluded
        self.assertNotIn("a.ts:25:2:network", ids)
        # non-clock demand-welds: full census
        self.assertIn("a.ts:5:2:network", ids)
        self.assertIn("a.ts:10:2:subprocess", ids)
        # clock demand-welds: sampled down (4 -> ~1 at 25%)
        clock = [i for i in ids if i.endswith(":clock")]
        self.assertEqual(len(clock), 1, f"PQ3 clock sample should be 1, got {clock}")
        # seamed control present (false-seam probe)
        self.assertIn("a.ts:20:4:network", ids)
        self.assertEqual(len([i for i in ids if i.startswith("a.ts:2")]), 3)

    def test_emit_is_deterministic(self) -> None:
        a = self.emit()
        first = self.worklist.read_text()
        self.worklist.unlink()
        b = self.emit()
        self.assertEqual(first, self.worklist.read_text())
        self.assertEqual(a, b)

    def test_full_panel_reconcile_freeze(self) -> None:
        wl = self.emit()
        labels = self.consensus_labels(wl)
        for p in ("pragmatic", "skeptic", "neutral"):
            self.write_votes(p, labels)
        rc = self.reconcile()
        self.assertEqual(rc.returncode, 0, rc.stderr)
        rec = json.loads(self.reconciled.read_text())["reconciled"]
        self.assertTrue(all(v["decision"] == "unanimous" for v in rec.values()))

        fz = self.freeze()
        self.assertEqual(fz.returncode, 0, fz.stderr)
        out = json.loads(self.labels.read_text())
        # group recovered from the map (was blinded in the worklist)
        groups = {v["group"] for v in out["labels"].values()}
        self.assertEqual(groups, {"demand_weld", "seamed_control"})
        # precision is over demand-welds only: all 3 GENUINE -> 100%
        self.assertIn("100.00%", fz.stdout)
        # the one control flagged GENUINE is reported as a false-seam
        self.assertIn("1/3 flagged GENUINE", fz.stdout)
        # provenance stamped
        self.assertEqual(out["labeler_model"], "test-model")
        self.assertEqual(out["personas"], ["pragmatic", "skeptic", "neutral"])

    def test_reconcile_refuses_incomplete_votes(self) -> None:
        wl = self.emit()
        labels = self.consensus_labels(wl)
        self.write_votes("pragmatic", labels)
        self.write_votes("skeptic", labels)
        # neutral drops one finding -> incomplete
        partial = dict(labels)
        partial.pop(next(iter(partial)))
        self.write_votes("neutral", partial)
        rc = self.reconcile()
        self.assertNotEqual(rc.returncode, 0)
        self.assertIn("RECONCILE REFUSED", rc.stderr)

    def test_freeze_refuses_incomplete_reconciled(self) -> None:
        # AC1: a reconciled set missing an id must be rejected, not silently frozen.
        wl = self.emit()
        labels = self.consensus_labels(wl)
        for p in ("pragmatic", "skeptic", "neutral"):
            self.write_votes(p, labels)
        self.assertEqual(self.reconcile().returncode, 0)
        rec = json.loads(self.reconciled.read_text())
        dropped = next(iter(rec["reconciled"]))
        del rec["reconciled"][dropped]
        self.reconciled.write_text(json.dumps(rec))
        fz = self.freeze()
        self.assertNotEqual(fz.returncode, 0)
        self.assertIn("FREEZE REFUSED", fz.stderr)
        self.assertIn(dropped, fz.stderr)

    def test_tiebreak_escalation_loop(self) -> None:
        wl = self.emit()
        labels = self.consensus_labels(wl)
        # force a 1-1-1 split on the network weld
        split_id = "a.ts:5:2:network"
        self.write_votes("pragmatic", {**labels, split_id: "GENUINE"})
        self.write_votes("skeptic", {**labels, split_id: "FALSE-WELD"})
        self.write_votes("neutral", {**labels, split_id: "COSMETIC"})
        rc = self.reconcile()
        self.assertEqual(rc.returncode, 3, rc.stderr)  # EXIT_NEEDS_TIEBREAK
        tb_wl = self.tmp / "finding_tiebreak_worklist.json"
        self.assertTrue(tb_wl.exists())
        tb = json.loads(tb_wl.read_text())
        self.assertEqual([f["id"] for f in tb["findings"]], [split_id])
        self.assertIn("GENUINE", tb["findings"][0]["candidate_labels"])

        # tie-break judge picks one of the candidate labels -> resolves
        (self.tmp / "finding_tiebreak_verdicts.json").write_text(json.dumps(
            {split_id: {"label": "GENUINE", "confidence": "medium",
                        "reason": "judge"}}))
        rc2 = self.reconcile()
        self.assertEqual(rc2.returncode, 0, rc2.stderr)
        rec = json.loads(self.reconciled.read_text())["reconciled"]
        self.assertEqual(rec[split_id]["decision"], "tiebreak")
        self.assertEqual(rec[split_id]["label"], "GENUINE")

    def test_arbiter_escalation_loop(self) -> None:
        # 1-1-1 panel, tie-break picks a 4th distinct label -> still tied ->
        # arbiter round resolves it. (Hardens the ground-truth-deciding path.)
        wl = self.emit()
        labels = self.consensus_labels(wl)
        split_id = "a.ts:5:2:network"
        self.write_votes("pragmatic", {**labels, split_id: "GENUINE"})
        self.write_votes("skeptic", {**labels, split_id: "FALSE-WELD"})
        self.write_votes("neutral", {**labels, split_id: "COSMETIC"})
        self.assertEqual(self.reconcile().returncode, 3)
        # tie-break introduces a 4th label -> [G,F,C,A] all distinct -> arbiter
        (self.tmp / "finding_tiebreak_verdicts.json").write_text(json.dumps(
            {split_id: {"label": "AMBIGUOUS", "confidence": "low",
                        "reason": "judge unsure"}}))
        rc = self.reconcile()
        self.assertEqual(rc.returncode, 4, rc.stderr)  # EXIT_NEEDS_ARBITER
        self.assertTrue((self.tmp / "finding_arbiter_worklist.json").exists())
        (self.tmp / "finding_arbiter_verdicts.json").write_text(json.dumps(
            {split_id: {"label": "GENUINE", "confidence": "high",
                        "reason": "arbiter"}}))
        rc2 = self.reconcile()
        self.assertEqual(rc2.returncode, 0, rc2.stderr)
        rec = json.loads(self.reconciled.read_text())["reconciled"]
        self.assertEqual(rec[split_id]["decision"], "arbiter")
        self.assertEqual(rec[split_id]["label"], "GENUINE")

    def test_reconcile_refuses_malformed_tiebreak(self) -> None:
        # A present-but-malformed escalation vote must REFUSE (not KeyError, not
        # silently freeze an incomplete audit trail) — escalation gets the same
        # schema guard as the panel.
        wl = self.emit()
        labels = self.consensus_labels(wl)
        split_id = "a.ts:5:2:network"
        self.write_votes("pragmatic", {**labels, split_id: "GENUINE"})
        self.write_votes("skeptic", {**labels, split_id: "FALSE-WELD"})
        self.write_votes("neutral", {**labels, split_id: "COSMETIC"})
        self.assertEqual(self.reconcile().returncode, 3)
        for bad in ({"confidence": "high", "reason": "no label"},   # missing label
                    {"label": "GENUINE"}):                          # missing conf/reason
            (self.tmp / "finding_tiebreak_verdicts.json").write_text(
                json.dumps({split_id: bad}))
            rc = self.reconcile()
            self.assertEqual(rc.returncode, 1, f"{bad} -> {rc.stdout}{rc.stderr}")
            self.assertIn("RECONCILE REFUSED", rc.stderr)

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
