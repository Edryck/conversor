from dataclasses import dataclass


@dataclass(frozen=True)
class ConversionOptions:
    output_format: str = "markdown"
    ocr: bool = False
    ocr_languages: tuple[str, ...] = ()
    images: bool = False
    formulas: bool = False
    code: bool = False
