import os
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


def test_utf8_decoding(tmp_path: Path) -> None:
    p = tmp_path / "u.txt"
    p.write_text("café naïve", encoding="utf-8")
    env = {**os.environ, "LC_ALL": "C", "PYTHONUTF8": "0", "PYTHONCOERCECLOCALE": "0"}
    env.pop("PYTHONIOENCODING", None)
    r = subprocess.run(
        [sys.executable, "-m", "textstats", str(p)],
        capture_output=True, env=env, check=False,
    )
    assert r.returncode == 0, r.stderr
    assert r.stdout.decode("utf-8") == format_report("café naïve") + "\n"


def test_subprocess(path: Path) -> None:
    r = subprocess.run(
        [sys.executable, "-m", "textstats", str(path)],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    assert r.returncode == 0
    assert r.stdout == format_report(TEXT) + "\n"


def _assert_clean_error(rc: int, cap: pytest.CaptureFixture[str]) -> None:
    out = cap.readouterr()
    assert rc == 1
    assert out.out == ""
    assert out.err.startswith("textstats: error:")
    assert "Traceback" not in out.err


def test_missing_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _assert_clean_error(main([str(tmp_path / "nope.txt")]), capsys)


def test_directory(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _assert_clean_error(main([str(tmp_path)]), capsys)


def test_invalid_utf8(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    p = tmp_path / "bad.txt"
    p.write_bytes(b"\xff\xfe\xfa")
    _assert_clean_error(main([str(p)]), capsys)


def test_negative_top(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(*a: object, **k: object) -> str:
        raise AssertionError("file was read")

    monkeypatch.setattr(Path, "read_text", boom)
    with pytest.raises(SystemExit) as e:
        main([str(tmp_path / "x.txt"), "--top", "-1"])
    assert e.value.code == 2
    assert "usage" in capsys.readouterr().err.lower()


def test_non_integer_top(path: Path) -> None:
    with pytest.raises(SystemExit) as e:
        main([str(path), "--top", "abc"])
    assert e.value.code == 2
