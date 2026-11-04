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


def test_glob_ignores_unsupported_extensions(tmp_path):
    touch(tmp_path / "a.pdf")
    touch(tmp_path / "a.md")
    names = [p.name for p in collect_inputs([str(tmp_path / "*")])]
    assert names == ["a.pdf"]


def test_literal_name_with_brackets_is_not_a_glob(tmp_path):
    source = touch(tmp_path / "r [final].pdf")
    touch(tmp_path / "r f.pdf")
    assert collect_inputs([str(source)]) == [source]
    assert is_batch_request([str(source)]) is False


def test_literal_folder_with_brackets_is_listed(tmp_path):
    folder = tmp_path / "p [x]"
    folder.mkdir()
    source = touch(folder / "a.pdf")
    assert collect_inputs([str(folder)]) == [source]
    assert is_batch_request([str(folder)]) is True


def test_uppercase_extension_is_listed(tmp_path):
    source = touch(tmp_path / "A.PDF")
    assert collect_inputs([str(tmp_path)]) == [source]


def test_glob_without_match_returns_empty(tmp_path):
    assert collect_inputs([str(tmp_path / "*.pdf")]) == []


@pytest.mark.parametrize("page", ["a.html", "a.htm", "a.HTML"])
def test_directory_drops_html_with_pdf_sibling(tmp_path, page):
    source = touch(tmp_path / "a.pdf")
    touch(tmp_path / page)
    assert collect_inputs([str(tmp_path)]) == [source]


def test_directory_keeps_html_without_pdf_sibling(tmp_path):
    touch(tmp_path / "a.pdf")
    page = touch(tmp_path / "b.html")
    assert page in collect_inputs([str(tmp_path)])


def test_glob_drops_html_with_pdf_sibling(tmp_path):
    touch(tmp_path / "a.PDF")
    touch(tmp_path / "a.html")
    assert collect_inputs([str(tmp_path / "*.html")]) == []


def test_explicit_html_with_pdf_sibling_is_kept(tmp_path):
    touch(tmp_path / "a.pdf")
    page = touch(tmp_path / "a.html")
    assert collect_inputs([str(page)]) == [page]
