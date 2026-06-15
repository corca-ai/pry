"""test_sweep.py — unit tests for the S2 sweep join pure logic (no git/pry).

enclosing_block_size (the site-size proxy) and arm_of (the pinned arm assignment).

Run: python3 -m pytest harness/test_sweep.py -q
"""

from __future__ import annotations

import sweep


# --- arm_of: the pinned pre-registration arms --------------------------------

def test_welded_at_demand_is_wd():
    assert sweep.arm_of({"class": "welded", "demand": True}) == ("wd", None)


def test_seamed_is_rest_seamed():
    assert sweep.arm_of({"class": "seamed", "demand": True}) == ("rest", "seamed")
    assert sweep.arm_of({"class": "seamed", "demand": False}) == ("rest", "seamed")


def test_welded_not_demand_is_rest_wnd():
    assert sweep.arm_of({"class": "welded", "demand": False}) == ("rest", "wnd")


def test_ambiguous_is_neither():
    assert sweep.arm_of({"class": "ambiguous", "demand": False}) == (None, None)
    assert sweep.arm_of({"class": None, "demand": None}) == (None, None)


# --- enclosing_block_size: the site-size proxy -------------------------------

def test_block_size_innermost():
    text = "function f() {\n  if (x) {\n    boom();\n  }\n}\n"
    # line 3 (boom) is in the inner if-block: lines 2..4 -> span 3
    assert sweep.enclosing_block_size(text, 3) == 3


def test_block_size_outer_when_not_in_inner():
    text = "function f() {\n  a();\n  if (x) {\n    b();\n  }\n}\n"
    # line 2 (a) is only in the function block: lines 1..6 -> span 6
    assert sweep.enclosing_block_size(text, 2) == 6


def test_block_size_top_level_is_one():
    text = "const x = 1;\nconst y = 2;\n"
    assert sweep.enclosing_block_size(text, 1) == 1


def test_block_size_deterministic():
    text = "function f() {\n  g(() => {\n    h();\n  });\n}\n"
    a = sweep.enclosing_block_size(text, 3)
    b = sweep.enclosing_block_size(text, 3)
    assert a == b == 3
