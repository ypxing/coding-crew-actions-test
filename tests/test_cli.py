import subprocess
import sys
from pathlib import Path

import pytest

from textstats import format_report
from textstats.__main__ import main

TEXT = "the cat the a cat the dog\n"


@pytest.fixture
def path(tmp_path: Path) -> Path:
    p = tmp_path / "in.txt"
    p.write_text(TEXT, encoding="utf-8")
    return p


def test_prints_report(path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(path)]) == 0
    assert capsys.readouterr().out == format_report(TEXT) + "\n"


def test_top_option(path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(path), "--top", "2"]) == 0
    assert capsys.readouterr().out == format_report(TEXT, n=2) + "\n"


def test_default_top_is_three(path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    main([str(path)])
    out = capsys.readouterr().out.split("top words:\n")[1].strip().split("\n")
    assert len(out) == 3


def test_utf8_decoding(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    import locale

    monkeypatch.setattr(locale, "getpreferredencoding", lambda *a, **k: "ascii")
    p = tmp_path / "u.txt"
    p.write_text("café naïve", encoding="utf-8")
    assert main([str(p)]) == 0
    assert capsys.readouterr().out == format_report("café naïve") + "\n"


def test_subprocess(path: Path) -> None:
    r = subprocess.run(
        [sys.executable, "-m", "textstats", str(path)],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    assert r.returncode == 0
    assert r.stdout == format_report(TEXT) + "\n"
