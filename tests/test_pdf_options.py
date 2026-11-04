import converter
from document_conversion.engines import build_pdf_pipeline_options, empty_text_warning
from document_conversion.options import ConversionOptions


def test_ocr_is_off_by_default():
    assert build_pdf_pipeline_options(ConversionOptions()).do_ocr is False


def test_ocr_languages_are_forwarded():
    options = ConversionOptions(ocr=True, ocr_languages=("pt", "en"))
    pipeline = build_pdf_pipeline_options(options)
    assert pipeline.do_ocr is True
    assert pipeline.ocr_options.lang == ["pt", "en"]


def test_cli_parses_ocr_flags():
    args = converter.parse_args(["a.pdf", "--ocr", "--ocr-lang", "pt,en"])
    assert converter.build_options(args).ocr_languages == ("pt", "en")


def test_empty_text_warning_only_without_ocr():
    assert "--ocr" in empty_text_warning(0, ConversionOptions())
    assert empty_text_warning(0, ConversionOptions(ocr=True)) is None
    assert empty_text_warning(3, ConversionOptions()) is None
