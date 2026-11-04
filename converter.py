import argparse
import os
import sys
import tempfile
from pathlib import Path

from document_conversion.batch import run_batch
from document_conversion.discovery import (
    OUTPUT_SUFFIXES,
    InputNotFoundError,
    collect_inputs,
    is_batch_request,
)
from document_conversion.engines import build_converter
from document_conversion.options import ConversionOptions


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Converte PDFs (com colunas duplas) e outros formatos para Markdown."
    )
    parser.add_argument(
        "inputs", nargs="+", help="Arquivos, pastas ou padrões glob de entrada"
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Arquivo de saída (entrada única) ou pasta de saída (lote, pasta existente ou caminho terminado em /)",
    )
    parser.add_argument(
        "--stdout", action="store_true", help="Imprime o resultado na saída padrão"
    )
    parser.add_argument(
        "--force", action="store_true", help="Reconverte mesmo se a saída estiver atualizada"
    )
    parser.add_argument(
        "--ocr", action="store_true", help="Ativa OCR para PDFs escaneados"
    )
    parser.add_argument(
        "--ocr-lang",
        help="Idiomas do OCR separados por vírgula (ex.: pt,en)",
    )
    parser.add_argument(
        "--images",
        action="store_true",
        help="Extrai imagens do PDF para a pasta <nome>_images (em --format json as imagens ficam embutidas no arquivo)",
    )
    parser.add_argument(
        "--formulas",
        action="store_true",
        help="Enriquece fórmulas (baixa um modelo extra na primeira execução)",
    )
    parser.add_argument(
        "--code",
        action="store_true",
        help="Enriquece blocos de código (baixa um modelo extra na primeira execução)",
    )
    parser.add_argument(
        "--format",
        dest="output_format",
        choices=["markdown", "json", "html"],
        default="markdown",
        help="Formato de saída (json e html apenas para PDFs)",
    )
    args = parser.parse_args(argv)
    if args.stdout and is_batch_request(args.inputs):
        parser.error("--stdout não pode ser usado com várias entradas")
    if args.stdout and args.output:
        parser.error("--stdout não pode ser usado com -o/--output")
    if args.stdout and args.images:
        parser.error("--stdout não pode ser usado com --images")
    return args


def build_options(args: argparse.Namespace) -> ConversionOptions:
    languages = tuple(
        code.strip() for code in (args.ocr_lang or "").split(",") if code.strip()
    )
    return ConversionOptions(
        output_format=args.output_format,
        ocr=args.ocr,
        ocr_languages=languages,
        images=args.images,
        formulas=args.formulas,
        code=args.code,
    )


def is_output_directory(output: str | None) -> bool:
    if not output:
        return False
    return output.endswith(os.sep) or Path(output).is_dir()


def print_summary(results) -> None:
    converted = sum(1 for result in results if result.status == "converted")
    skipped = sum(1 for result in results if result.status == "skipped")
    failed = [result for result in results if result.status == "failed"]
    print(
        f"Convertidos: {converted} | Pulados: {skipped} | Falhas: {len(failed)}",
        file=sys.stderr,
    )
    if skipped:
        print("Use --force para reconverter ou aplicar novas opções.", file=sys.stderr)
    for result in failed:
        print(f"Falha: {result.input_path}: {result.message}", file=sys.stderr)
    for result in results:
        if result.status == "converted" and result.message:
            print(f"Aviso: {result.input_path}: {result.message}", file=sys.stderr)


def run_stdout(inputs: list[Path], convert, output_format: str) -> int:
    with tempfile.TemporaryDirectory() as directory:
        temporary_output = Path(directory) / f"output{OUTPUT_SUFFIXES[output_format]}"
        try:
            warning = convert(inputs[0], temporary_output)
        except Exception as error:
            print(f"Falha: {inputs[0]}: {error}", file=sys.stderr)
            return 1
        if warning:
            print(f"Aviso: {inputs[0]}: {warning}", file=sys.stderr)
        print(temporary_output.read_text(encoding="utf-8"))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    batch = is_batch_request(args.inputs)
    try:
        inputs = collect_inputs(args.inputs)
    except InputNotFoundError as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1
    if not inputs:
        print("Erro: nenhum arquivo suportado encontrado", file=sys.stderr)
        return 1

    options = build_options(args)
    convert = build_converter(options)
    if args.stdout:
        return run_stdout(inputs, convert, options.output_format)

    output_arg = Path(args.output) if args.output else None
    results = run_batch(
        inputs,
        convert,
        output_arg,
        batch or is_output_directory(args.output),
        options.output_format,
        args.force,
    )
    print_summary(results)
    return 1 if any(result.status == "failed" for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())
