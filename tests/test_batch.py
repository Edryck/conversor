import os

from document_conversion import batch
from document_conversion.batch import run_batch


def write_ok(source, target):
    target.write_text("ok", encoding="utf-8")


def run(inputs, convert=write_ok, force=False):
    return run_batch(inputs, convert, None, True, "markdown", force)


def make(tmp_path, name):
    path = tmp_path / name
    path.write_text("x", encoding="utf-8")
    return path


def test_failure_does_not_stop_batch(tmp_path):
    bad, good = make(tmp_path, "bad.pdf"), make(tmp_path, "good.pdf")

    def convert(source, target):
        if source == bad:
            raise ValueError("quebrado")
        write_ok(source, target)

    results = run([bad, good], convert)
    assert [r.status for r in results] == ["failed", "converted"]
    assert "quebrado" in results[0].message


def test_failed_conversion_leaves_no_partial_output(tmp_path):
    source = make(tmp_path, "a.pdf")

    def convert(source, target):
        target.write_text("parcial", encoding="utf-8")
        raise ValueError("quebrado")

    run([source], convert)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a.pdf"]


def test_skip_and_force(tmp_path):
    source = make(tmp_path, "a.pdf")
    target = make(tmp_path, "a.md")
    os.utime(source, (100, 100))
    os.utime(target, (200, 200))
    assert run([source])[0].status == "skipped"
    assert run([source], force=True)[0].status == "converted"


def test_output_collision_fails_second_file(tmp_path):
    first, second = make(tmp_path, "a.docx"), make(tmp_path, "a.pdf")
    results = run([first, second], force=True)
    assert [r.status for r in results] == ["converted", "failed"]


def test_input_equal_to_output_is_not_overwritten(tmp_path):
    source = make(tmp_path, "a.md")
    results = run([source], force=True)
    assert results[0].status == "failed"
    assert source.read_text(encoding="utf-8") == "x"


def test_warning_is_kept_in_message(tmp_path):
    source = make(tmp_path, "a.pdf")

    def convert(source, target):
        write_ok(source, target)
        return "aviso"

    assert run([source], convert)[0].message == "aviso"


def test_output_matching_other_input_keeps_original(tmp_path):
    page = tmp_path / "a.html"
    page.write_text("original", encoding="utf-8")
    source = make(tmp_path, "a.pdf")
    results = run_batch([source, page], write_ok, None, True, "html", True)
    assert [r.status for r in results] == ["failed", "failed"]
    assert page.read_text(encoding="utf-8") == "original"


def test_output_matching_later_input_fails_whichever_owns_it(tmp_path):
    page = tmp_path / "a.html"
    page.write_text("original", encoding="utf-8")
    source = make(tmp_path, "a.pdf")
    results = run_batch([page, source], write_ok, None, True, "html", True)
    assert [r.status for r in results] == ["failed", "failed"]
    assert page.read_text(encoding="utf-8") == "original"


def test_up_to_date_error_fails_only_that_file(tmp_path, monkeypatch):
    bad, good = make(tmp_path, "bad.pdf"), make(tmp_path, "good.pdf")
    original = batch.is_up_to_date
    converted = []

    def flaky(input_path, output_path):
        if input_path == bad:
            raise OSError("sem acesso")
        return original(input_path, output_path)

    def convert(source, target):
        converted.append(source)
        write_ok(source, target)

    monkeypatch.setattr(batch, "is_up_to_date", flaky)
    results = run([bad, good], convert)
    assert [r.status for r in results] == ["failed", "converted"]
    assert "sem acesso" in results[0].message
    assert converted == [good]


def test_resolve_output_error_fails_only_that_file(tmp_path, monkeypatch):
    bad, good = make(tmp_path, "bad.pdf"), make(tmp_path, "good.pdf")
    original = batch.resolve_output

    def flaky(input_path, output_arg, is_batch, output_format):
        if input_path == bad:
            raise ValueError("saída inválida")
        return original(input_path, output_arg, is_batch, output_format)

    monkeypatch.setattr(batch, "resolve_output", flaky)
    results = run([bad, good])
    assert [r.status for r in results] == ["failed", "converted"]
    assert results[0].output_path is None
