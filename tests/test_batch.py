import os
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
