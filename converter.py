# converter.py — versão definitiva
import argparse
import sys
from pathlib import Path

# PDF → Docling (resolve colunas duplas de verdade)
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import PdfFormatOption

# Outros formatos → MarkItDown
from markitdown import MarkItDown


def convert_pdf_with_docling(pdf_path: Path) -> str:
    """
    Converte PDF usando Docling.
    Docling detecta colunas, resolve ordem de leitura e extrai tabelas.
    """
    pipeline_options = PdfPipelineOptions()
    # do_ocr=True ativa OCR para PDFs escaneados ou com encoding ruim.
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True  # tabelas como Markdown

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    result = converter.convert(str(pdf_path))
    return result.document.export_to_markdown()


def convert_other_with_markitdown(file_path: Path) -> str:
    """Converte PPTX, DOCX, XLSX, etc. com MarkItDown."""
    md = MarkItDown(enable_builtins=True)
    return md.convert(str(file_path)).markdown


def main():
    parser = argparse.ArgumentParser(
        description="Converte PDFs (com colunas duplas) e outros formatos para Markdown."
    )
    parser.add_argument("input", help="Arquivo de entrada")
    parser.add_argument("-o", "--output", help="Arquivo Markdown de saída")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Erro: {input_path} não encontrado", file=sys.stderr)
        sys.exit(1)

    ext = input_path.suffix.lower()
    try:
        if ext == ".pdf":
            markdown_text = convert_pdf_with_docling(input_path)
        else:
            markdown_text = convert_other_with_markitdown(input_path)
    except Exception as e:
        print(f"Erro na conversão: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        Path(args.output).write_text(markdown_text, encoding="utf-8")
        print(f"Salvo em: {args.output}")
    else:
        print(markdown_text)


if __name__ == "__main__":
    main()
