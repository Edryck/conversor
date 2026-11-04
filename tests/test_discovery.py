import os
from pathlib import Path
import pytest
from document_conversion.discovery import (
    InputNotFoundError, collect_inputs, is_batch_request, is_up_to_date, resolve_output,
)


def touch(path):
    path.write_text("x", encoding="utf-8")
    return path


def test_directory_is_filtered_sorted_and_not_recursive(tmp_path):
    touch(tmp_path / "b.pdf")
    touch(tmp_path / "a.docx")
    touch(tmp_path / "a.md")
    (tmp_path / "sub").mkdir()
    touch(tmp_path / "sub" / "c.pdf")
    names = [p.name for p in collect_inputs([str(tmp_path)])]
    assert names == ["a.docx", "b.pdf"]


def test_explicit_file_keeps_unlisted_extension(tmp_path):
    source = touch(tmp_path / "notes.txt")
    assert collect_inputs([str(source)]) == [source]


def test_quoted_glob_and_duplicates(tmp_path):
    source = touch(tmp_path / "a.pdf")
    assert collect_inputs([str(tmp_path / "*.pdf"), str(source)]) == [source]


def test_missing_input_raises(tmp_path):
    with pytest.raises(InputNotFoundError):
        collect_inputs([str(tmp_path / "none.pdf")])


def test_batch_detection(tmp_path):
    source = touch(tmp_path / "a.pdf")
    assert is_batch_request([str(source)]) is False
    assert is_batch_request([str(tmp_path)]) is True
    assert is_batch_request([str(tmp_path / "*.pdf")]) is True
    assert is_batch_request([str(source), str(source)]) is True


def test_resolve_output_cases():
    source = Path("in/a.pdf")
    assert resolve_output(source, None, False, "markdown") == Path("in/a.md")
    assert resolve_output(source, Path("x.md"), False, "markdown") == Path("x.md")
    assert resolve_output(source, Path("out"), True, "html") == Path("out/a.html")


def test_up_to_date_uses_mtime(tmp_path):
    source = touch(tmp_path / "a.pdf")
    target = tmp_path / "a.md"
    assert is_up_to_date(source, target) is False
    touch(target)
    os.utime(source, (100, 100))
    os.utime(target, (100, 100))
    assert is_up_to_date(source, target) is True
    os.utime(source, (200, 200))
    assert is_up_to_date(source, target) is False
