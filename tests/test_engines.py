from pathlib import Path
from document_conversion.engines import build_converter
from document_conversion.options import ConversionOptions


def test_non_pdf_writes_markdown(tmp_path):
    source = tmp_path / "data.csv"
    source.write_text("name,age\nAna,30\n", encoding="utf-8")
    target = tmp_path / "data.md"
    assert build_converter(ConversionOptions())(source, target) is None
    assert "Ana" in target.read_text(encoding="utf-8")


def test_build_converter_does_not_load_docling_for_non_pdf(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "document_conversion.engines.create_document_converter",
        lambda options: (_ for _ in ()).throw(AssertionError),
    )
    source = tmp_path / "data.csv"
    source.write_text("a\n1\n", encoding="utf-8")
    build_converter(ConversionOptions())(source, tmp_path / "data.md")
