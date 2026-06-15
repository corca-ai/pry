"""test_bgate.py — unit tests for the cleaned (b)-gate lens classifier (S5).

Pins the post-fix behavior: module-direct boundary -> welded; boundary-verb on an
injected receiver (param / self-attr-from-__init__) -> seamed; boundary-verb on a
local var -> undecided; and the noise that caused the first artifactual mute
(dict.get / list.append / signal.connect) is NOT a candidate at all.

Run: python3 -m pytest harness/test_bgate.py -q
"""

from __future__ import annotations

import bgate_lens


def _classify(src):
    return bgate_lens.classify_file(src)


def test_module_direct_is_welded():
    out = _classify("import requests\ndef f():\n    return requests.get(url)\n")
    assert any(f["class"] == "welded" and f["kind"] == "network" for f in out)


def test_clock_module_direct_is_welded():
    out = _classify("from datetime import datetime\ndef f():\n    return datetime.now()\n")
    assert any(f["class"] == "welded" and f["kind"] == "clock" for f in out)


def test_param_injected_boundary_verb_is_seamed():
    src = ("def handler(self, client):\n"
           "    return client.request('GET', url)\n")
    out = _classify(src)
    assert any(f["class"] == "seamed" for f in out)


def test_self_injected_boundary_verb_is_seamed():
    src = ("class S:\n"
           "    def __init__(self, conn):\n"
           "        self.conn = conn\n"
           "    def run(self):\n"
           "        return self.conn.execute('SELECT 1')\n")
    out = _classify(src)
    assert any(f["class"] == "seamed" for f in out)


def test_local_var_boundary_verb_is_undecided():
    src = ("def f():\n"
           "    cur = make_cursor()\n"
           "    return cur.execute('SELECT 1')\n")
    out = _classify(src)
    assert any(f["class"] == "undecided" for f in out)


def test_dict_get_and_list_append_are_not_candidates():
    # the noise that caused the first artifactual mute must NOT be picked up
    src = ("def f(d, xs):\n"
           "    xs.append(1)\n"
           "    return d.get('k')\n")
    out = _classify(src)
    assert out == []


def test_signal_connect_is_not_a_candidate():
    # Django/blinker signal.connect is not a demand-subset boundary
    src = ("def wire():\n    post_save.connect(handler)\n")
    out = _classify(src)
    assert all(f["class"] != "seamed" for f in out)
    assert not any(f["expr"].endswith("connect") for f in out)
