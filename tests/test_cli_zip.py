import re
import sys
import zipfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from tuitorial.parse_yaml import cli


def test_cli_runs_from_zip(tmp_path, monkeypatch):
    yaml_content = "chapters:\n  - title: Deck\n    code: print('hi')\n"
    zip_path = tmp_path / "presentation.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("deck/tuitorial.yaml", yaml_content)
        archive.writestr("deck/images/logo.txt", "logo")

    captured: dict[str, object] = {}

    def fake_run(
        yaml_name: str,
        *,
        chapter_index: int | None,
        step_index: int,
        theme: str | None,
    ) -> None:
        captured["yaml_name"] = yaml_name
        captured["cwd"] = Path.cwd()
        captured["chapter"] = chapter_index
        captured["step"] = step_index
        captured["theme"] = theme
        assert Path(yaml_name).read_text() == yaml_content

    monkeypatch.setattr("tuitorial.parse_yaml.run_from_yaml", fake_run)
    original_cwd = Path.cwd()
    monkeypatch.setattr(sys, "argv", ["tuitorial", str(zip_path)])

    cli()

    assert captured["yaml_name"] == "tuitorial.yaml"
    assert captured["chapter"] is None
    assert captured["step"] == 0
    assert captured["theme"] is None
    assert captured["cwd"].name == "deck"
    assert Path.cwd() == original_cwd
    assert not captured["cwd"].exists()


@pytest.mark.parametrize(
    "members",
    [
        {"deck/readme.txt": "hello"},
        {
            "deck/a/tuitorial.yaml": "chapters: []\n",
            "deck/b/tuitorial.yaml": "chapters: []\n",
        },
    ],
)
def test_cli_zip_errors(monkeypatch, tmp_path, capsys, members):
    zip_path = tmp_path / "presentation.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for name, data in members.items():
            archive.writestr(name, data)

    run_mock = Mock()
    monkeypatch.setattr("tuitorial.parse_yaml.run_from_yaml", run_mock)
    original_cwd = Path.cwd()
    monkeypatch.setattr(sys, "argv", ["tuitorial", str(zip_path)])

    cli()

    output = capsys.readouterr().out
    plain_output = re.sub(r"\x1b\[[0-9;]*m", "", output)
    if len([name for name in members if name.endswith("tuitorial.yaml")]) == 0:
        assert "No 'tuitorial.yaml' found" in plain_output
    else:
        assert "Multiple 'tuitorial.yaml' files" in plain_output

    run_mock.assert_not_called()
    assert Path.cwd() == original_cwd


def test_cli_zip_watch_not_supported(monkeypatch, tmp_path, capsys):
    zip_path = tmp_path / "presentation.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("deck/tuitorial.yaml", "chapters: []\n")

    run_mock = Mock()
    monkeypatch.setattr("tuitorial.parse_yaml.run_from_yaml", run_mock)
    monkeypatch.setattr(sys, "argv", ["tuitorial", "--watch", str(zip_path)])

    cli()

    plain_output = re.sub(r"\x1b\[[0-9;]*m", "", capsys.readouterr().out)
    assert "`--watch` is not supported for ZIP archives" in plain_output
    run_mock.assert_not_called()


def test_cli_zip_missing_file(monkeypatch, tmp_path, capsys):
    zip_path = tmp_path / "missing.zip"

    run_mock = Mock()
    monkeypatch.setattr("tuitorial.parse_yaml.run_from_yaml", run_mock)
    monkeypatch.setattr(sys, "argv", ["tuitorial", str(zip_path)])

    cli()

    plain_output = re.sub(r"\x1b\[[0-9;]*m", "", capsys.readouterr().out)
    compact_output = " ".join(plain_output.split())
    assert "ZIP archive not found" in compact_output
    assert zip_path.stem in compact_output
    run_mock.assert_not_called()
