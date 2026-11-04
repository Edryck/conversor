import glob
from pathlib import Path

SUPPORTED_EXTENSIONS = frozenset(
    {".pdf", ".docx", ".pptx", ".xlsx", ".xls", ".html", ".htm", ".csv", ".epub"}
)

OUTPUT_SUFFIXES = {"markdown": ".md", "json": ".json", "html": ".html"}

GLOB_CHARACTERS = ("*", "?", "[")

HTML_EXTENSIONS = frozenset({".html", ".htm"})


class InputNotFoundError(Exception):
    pass


def _has_glob(raw: str) -> bool:
    return any(character in raw for character in GLOB_CHARACTERS)


def _has_pdf_sibling(path: Path) -> bool:
    return any(
        sibling.stem == path.stem and sibling.suffix.lower() == ".pdf"
        for sibling in path.parent.iterdir()
    )


def _is_discoverable(path: Path) -> bool:
    suffix = path.suffix.lower()
    if not path.is_file() or suffix not in SUPPORTED_EXTENSIONS:
        return False
    return suffix not in HTML_EXTENSIONS or not _has_pdf_sibling(path)


def _list_directory(directory: Path) -> list[Path]:
    return sorted(entry for entry in directory.iterdir() if _is_discoverable(entry))


def _expand(raw: str) -> list[Path]:
    path = Path(raw)
    if not path.exists() and _has_glob(raw):
        matches = [Path(match) for match in sorted(glob.glob(raw))]
        expanded = []
        for match in matches:
            if match.is_dir():
                expanded.extend(_list_directory(match))
            elif _is_discoverable(match):
                expanded.append(match)
        return expanded
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
    path = Path(raw)
    if path.exists():
        return path.is_dir()
    return _has_glob(raw)


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
