import pytest

import converter


def fake_build(options):
    def convert(source, target):
        target.write_text("resultado", encoding="utf-8")
        return None

    return convert


@pytest.fixture
def source(tmp_path, monkeypatch):
    monkeypatch.setattr(converter, "build_converter", fake_build)
    path = tmp_path / "a.pdf"
    path.write_text("x", encoding="utf-8")
    return path


def test_default_output_is_next_to_input(source):
    assert converter.main([str(source)]) == 0
    assert source.with_suffix(".md").read_text(encoding="utf-8") == "resultado"


def test_stdout_prints_only_content(source, capsys):
    assert converter.main([str(source), "--stdout"]) == 0
    assert capsys.readouterr().out.strip() == "resultado"
    assert not source.with_suffix(".md").exists()


def test_stdout_rejects_multiple_inputs(source):
    with pytest.raises(SystemExit) as error:
        converter.main([str(source), str(source), "--stdout"])
    assert error.value.code == 2


def test_stdout_rejects_output(source, tmp_path):
    with pytest.raises(SystemExit) as error:
        converter.main([str(source), "--stdout", "-o", str(tmp_path / "x.md")])
    assert error.value.code == 2


def test_missing_input_returns_one(tmp_path, source):
    assert converter.main([str(tmp_path / "none.pdf")]) == 1


def test_empty_directory_returns_one(tmp_path, source):
    empty = tmp_path / "empty"
    empty.mkdir()
    assert converter.main([str(empty)]) == 1


def test_failure_returns_one_and_lists_file(source, monkeypatch, capsys):
    def failing(options):
        def convert(input_path, output_path):
            raise ValueError("quebrado")

        return convert

    monkeypatch.setattr(converter, "build_converter", failing)
    assert converter.main([str(source)]) == 1
    assert "a.pdf" in capsys.readouterr().err


def test_summary_goes_to_stderr(source, capsys):
    assert converter.main([str(source)]) == 0
    captured = capsys.readouterr()
    assert "Convertidos: 1" in captured.err
    assert captured.out == ""


def test_format_changes_default_suffix(source):
    assert converter.main([str(source), "--format", "html"]) == 0
    assert source.with_suffix(".html").exists()


def test_stdout_uses_format_suffix(tmp_path, monkeypatch, capsys):
    seen = []

    def recording_build(options):
        def convert(source, target):
            seen.append(target.suffix)
            target.write_text("<p>ok</p>", encoding="utf-8")
            return None

        return convert

    monkeypatch.setattr(converter, "build_converter", recording_build)
    path = tmp_path / "a.pdf"
    path.write_text("x", encoding="utf-8")
    assert converter.main([str(path), "--format", "html", "--stdout"]) == 0
    assert seen == [".html"]
    assert "<p>ok</p>" in capsys.readouterr().out
