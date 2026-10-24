import pytest

import textstats
from textstats import format_report


def test_exported() -> None:
    assert "format_report" in textstats.__all__


def test_full_report() -> None:
    assert format_report("the cat the a cat the") == (
        "words: 6\ncharacters: 21\ncharacters (no spaces): 16\n"
        "top words:\n  the: 3\n  cat: 2\n  a: 1"
    )


def test_n_limits_and_orders() -> None:
    lines = format_report("b a b a c", n=2).split("\n")
    assert lines[3:] == ["top words:", "  a: 2", "  b: 2"]


def test_empty() -> None:
    assert format_report("") == (
        "words: 0\ncharacters: 0\ncharacters (no spaces): 0\ntop words:\n  (none)"
    )


def test_n_zero() -> None:
    assert format_report("a b", n=0).endswith("top words:\n  (none)")


def test_negative_n() -> None:
    with pytest.raises(ValueError):
        format_report("a", n=-1)
