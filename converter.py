import argparse
import sys
import tempfile
from pathlib import Path

from document_conversion.engines import build_converter
from document_conversion.options import ConversionOptions


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

    convert = build_converter(ConversionOptions())
    try:
        if args.output:
            warning = convert(input_path, Path(args.output))
            if warning:
                print(warning, file=sys.stderr)
            print(f"Salvo em: {args.output}")
        else:
            with tempfile.TemporaryDirectory() as directory:
                temporary_output = Path(directory) / "output.md"
                warning = convert(input_path, temporary_output)
                if warning:
                    print(warning, file=sys.stderr)
                print(temporary_output.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Erro na conversão: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
