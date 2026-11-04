from pathlib import Path

import pytest

import converter
from document_conversion.engines import (
    build_pdf_pipeline_options,
    empty_text_warning,
    image_artifacts_dir,
)
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


def test_images_enable_picture_generation():
    pipeline = build_pdf_pipeline_options(ConversionOptions(images=True))
    assert pipeline.generate_picture_images is True
    assert pipeline.images_scale == 2.0


def test_artifacts_dir_ignores_temporary_name():
    assert image_artifacts_dir(Path("out/.a.tmp.md")) == Path("out/a_images")


def test_artifacts_dir_for_final_name():
    assert image_artifacts_dir(Path("out/a.md")) == Path("out/a_images")


def test_stdout_rejects_images():
    with pytest.raises(SystemExit) as error:
        converter.main(["a.pdf", "--stdout", "--images"])
    assert error.value.code == 2


def test_enrichment_flags_reach_pipeline():
    args = converter.parse_args(["a.pdf", "--formulas", "--code"])
    pipeline = build_pdf_pipeline_options(converter.build_options(args))
    assert pipeline.do_formula_enrichment is True
    assert pipeline.do_code_enrichment is True
