from pathlib import Path
from typing import Callable

from document_conversion.options import ConversionOptions


def build_pdf_pipeline_options(options: ConversionOptions):
    from docling.datamodel.pipeline_options import PdfPipelineOptions

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = options.ocr
    if options.ocr and options.ocr_languages:
        pipeline_options.ocr_options.lang = list(options.ocr_languages)
    pipeline_options.do_table_structure = True
    if options.images:
        pipeline_options.generate_picture_images = True
        pipeline_options.images_scale = 2.0
    return pipeline_options


def image_artifacts_dir(output_path: Path) -> Path:
    stem = output_path.stem
    if stem.startswith(".") and stem.endswith(".tmp"):
        stem = stem[1:-4]
    return output_path.with_name(f"{stem}_images")


def empty_text_warning(text_count: int, options: ConversionOptions) -> str | None:
    if text_count == 0 and not options.ocr:
        return "Nenhum texto extraído. Tente novamente com --ocr."
    return None


def create_document_converter(options: ConversionOptions):
    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import DocumentConverter, PdfFormatOption

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=build_pdf_pipeline_options(options)
            )
        }
    )


def build_converter(
    options: ConversionOptions,
) -> Callable[[Path, Path], str | None]:
    state = {}

    def convert(input_path: Path, output_path: Path) -> str | None:
        if input_path.suffix.lower() == ".pdf":
            if "docling" not in state:
                state["docling"] = create_document_converter(options)
            result = state["docling"].convert(str(input_path))
            if options.images:
                from docling_core.types.doc import ImageRefMode

                result.document.save_as_markdown(
                    output_path,
                    artifacts_dir=image_artifacts_dir(output_path),
                    image_mode=ImageRefMode.REFERENCED,
                )
            else:
                result.document.save_as_markdown(output_path)
            return empty_text_warning(len(result.document.texts), options)
        if "markitdown" not in state:
            from markitdown import MarkItDown

            state["markitdown"] = MarkItDown(enable_builtins=True)
        markdown = state["markitdown"].convert(str(input_path)).markdown
        output_path.write_text(markdown, encoding="utf-8")
        return None

    return convert
