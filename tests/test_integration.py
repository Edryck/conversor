from pathlib import Path
import shutil
import pytest
import converter

pytestmark = pytest.mark.integration
FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def workspace(tmp_path):
    shutil.copy(FIXTURES / "sample.pdf", tmp_path)
    shutil.copy(FIXTURES / "sample.docx", tmp_path / "other.docx")
    return tmp_path


def test_directory_batch_converts_both_engines(workspace):
    assert converter.main([str(workspace), "-o", str(workspace / "out")]) == 0
    assert "Texto de exemplo" in (workspace / "out/sample.md").read_text(encoding="utf-8")
    assert "Texto de exemplo" in (workspace / "out/other.md").read_text(encoding="utf-8")


def test_images_link_resolves_from_final_output(workspace):
    source = workspace / "sample.pdf"
    assert converter.main([str(source), "--images"]) == 0
    assert list((workspace / "sample_images").iterdir())
    content = (workspace / "sample.md").read_text(encoding="utf-8")
    assert "](sample_images/" in content
    assert ".tmp" not in content


@pytest.mark.parametrize("output_format, suffix", [("json", ".json"), ("html", ".html")])
def test_pdf_formats(workspace, output_format, suffix):
    source = workspace / "sample.pdf"
    assert converter.main([str(source), "--format", output_format]) == 0
    assert "Texto de exemplo" in source.with_suffix(suffix).read_text(encoding="utf-8")
