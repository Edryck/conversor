import glob
from pathlib import Path

SUPPORTED_EXTENSIONS = frozenset(
    {".pdf", ".docx", ".pptx", ".xlsx", ".xls", ".html", ".htm", ".csv", ".epub"}
)

OUTPUT_SUFFIXES = {"markdown": ".md", "json": ".json", "html": ".html"}

GLOB_CHARACTERS = ("*", "?", "[")


class InputNotFoundError(Exception):
    pass


def _has_glob(raw: str) -> bool:
    return any(character in raw for character in GLOB_CHARACTERS)


def _list_directory(directory: Path) -> list[Path]:
    return sorted(
        entry
        for entry in directory.iterdir()
        if entry.is_file() and entry.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def _expand(raw: str) -> list[Path]:
    if _has_glob(raw):
        matches = [Path(match) for match in sorted(glob.glob(raw))]
        expanded = []
        for match in matches:
            if match.is_dir():
                expanded.extend(_list_directory(match))
            elif match.is_file():
                expanded.append(match)
        return expanded
    path = Path(raw)
    if path.is_dir():
        return _list_directory(path)
    if path.is_file():
        return [path]
    raise InputNotFoundError(f"Entrada não encontrada: {raw}")


def collect_inputs(raw_inputs: list[str]) -> list[Path]:
    collected = []
    seen = set()
    for raw in raw_inputs:
        for path in _expand(raw):
            key = path.resolve()
            if key in seen:
                continue
            seen.add(key)
            collected.append(path)
    return collected


def is_batch_request(raw_inputs: list[str]) -> bool:
    if len(raw_inputs) != 1:
        return True
    raw = raw_inputs[0]
    return _has_glob(raw) or Path(raw).is_dir()


def resolve_output(
    input_path: Path, output_arg: Path | None, batch: bool, output_format: str
) -> Path:
    suffix = OUTPUT_SUFFIXES[output_format]
    if output_arg is None:
        return input_path.with_suffix(suffix)
    if batch:
        return output_arg / f"{input_path.stem}{suffix}"
    return output_arg


def is_up_to_date(input_path: Path, output_path: Path) -> bool:
    if not output_path.exists():
        return False
    return output_path.stat().st_mtime >= input_path.stat().st_mtime
