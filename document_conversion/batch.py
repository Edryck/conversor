import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from tqdm import tqdm

from document_conversion.discovery import is_up_to_date, resolve_output


@dataclass
class FileResult:
    input_path: Path
    output_path: Path
    status: str
    message: str = ""


def _temporary_path(output_path: Path) -> Path:
    return output_path.with_name(f".{output_path.stem}.tmp{output_path.suffix}")


def _process(
    input_path: Path,
    output_path: Path,
    convert: Callable[[Path, Path], str | None],
    force: bool,
    used: set,
) -> FileResult:
    key = output_path.resolve()
    if key == input_path.resolve():
        return FileResult(
            input_path, output_path, "failed", "A saída coincide com a entrada."
        )
    if key in used:
        return FileResult(
            input_path,
            output_path,
            "failed",
            "Outro arquivo do lote já gera esta mesma saída.",
        )
    used.add(key)
    if not force and is_up_to_date(input_path, output_path):
        return FileResult(input_path, output_path, "skipped")
    temporary = _temporary_path(output_path)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        warning = convert(input_path, temporary)
        os.replace(temporary, output_path)
        return FileResult(input_path, output_path, "converted", warning or "")
    except Exception as error:
        return FileResult(input_path, output_path, "failed", str(error))
    finally:
        temporary.unlink(missing_ok=True)


def run_batch(
    inputs: list[Path],
    convert: Callable[[Path, Path], str | None],
    output_arg: Path | None,
    batch: bool,
    output_format: str,
    force: bool,
) -> list[FileResult]:
    results = []
    used = set()
    for input_path in tqdm(inputs, disable=len(inputs) < 2, file=sys.stderr):
        output_path = resolve_output(input_path, output_arg, batch, output_format)
        results.append(_process(input_path, output_path, convert, force, used))
    return results
