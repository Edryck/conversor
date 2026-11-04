from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from docling.datamodel.base_models import ConversionStatus

from document_conversion.engines import build_converter, save_document
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


@pytest.mark.parametrize("output_format, method", [
    ("markdown", "save_as_markdown"),
    ("json", "save_as_json"),
    ("html", "save_as_html"),
])
def test_save_document_dispatches_format(output_format, method, tmp_path):
    document = Mock()
    save_document(document, tmp_path / "a.out", ConversionOptions(output_format=output_format))
    getattr(document, method).assert_called_once()


def test_non_pdf_rejects_json(tmp_path):
    source = tmp_path / "data.csv"
    source.write_text("a\n1\n", encoding="utf-8")
    convert = build_converter(ConversionOptions(output_format="json"))
    with pytest.raises(ValueError, match="PDF"):
        convert(source, tmp_path / "data.json")


def test_non_pdf_rejects_html(tmp_path):
    source = tmp_path / "data.csv"
    source.write_text("a\n1\n", encoding="utf-8")
    convert = build_converter(ConversionOptions(output_format="html"))
    with pytest.raises(ValueError, match="PDF"):
        convert(source, tmp_path / "data.html")


def fake_docling(monkeypatch, status, texts):
    document = Mock(texts=texts)
    docling = Mock()
    docling.convert.return_value = SimpleNamespace(status=status, document=document)
    monkeypatch.setattr(
        "document_conversion.engines.create_document_converter",
        lambda options: docling,
    )


PARTIAL = "Conversão parcial: algumas páginas podem ter falhado."
EMPTY = "Nenhum texto extraído. Tente novamente com --ocr --force."


@pytest.mark.parametrize("status, texts, expected", [
    (ConversionStatus.PARTIAL_SUCCESS, ["t"], PARTIAL),
    (ConversionStatus.PARTIAL_SUCCESS, [], f"{PARTIAL} {EMPTY}"),
    (ConversionStatus.SUCCESS, [], EMPTY),
    (ConversionStatus.SUCCESS, ["t"], None),
])
def test_pdf_warnings(monkeypatch, tmp_path, status, texts, expected):
    fake_docling(monkeypatch, status, texts)
    convert = build_converter(ConversionOptions())
    assert convert(tmp_path / "a.pdf", tmp_path / "a.md") == expected
