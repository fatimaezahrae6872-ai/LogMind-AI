
from pathlib import Path
from dataclasses import dataclass


# Extensions autorisées
ALLOWED_EXTENSIONS = {".log", ".txt", ".csv"}

# Taille maximale : 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024


@dataclass
class LogFileInfo:
    filename: str
    extension: str
    size_bytes: int
    total_lines: int
    empty_lines: int
    content: list[str]


class LogIngestionError(Exception):
    """Erreur liée à l'importation d'un fichier log."""
    pass


def ingest_log_file(file_path: str) -> LogFileInfo:
    """
    Read and validate a log file.

    Args:
        file_path: Path to the log file.

    Returns:
        LogFileInfo containing file metadata and lines.
    """

    path = Path(file_path)

    # 1. Vérifier l'existence du fichier
    if not path.exists():
        raise LogIngestionError("File does not exist.")

    # 2. Vérifier qu'il s'agit d'un fichier
    if not path.is_file():
        raise LogIngestionError("The provided path is not a file.")

    # 3. Vérifier l'extension
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise LogIngestionError(
            f"Unsupported file extension: {path.suffix}"
        )

    # 4. Vérifier la taille
    size_bytes = path.stat().st_size

    if size_bytes == 0:
        raise LogIngestionError("The file is empty.")

    if size_bytes > MAX_FILE_SIZE:
        raise LogIngestionError("File exceeds the 10 MB limit.")

    # 5. Lire le contenu
    try:
        with path.open(
            mode="r",
            encoding="utf-8-sig",
            errors="replace"
        ) as file:
            lines = [
                line.rstrip("\r\n")
                for line in file
            ]

    except OSError as error:
        raise LogIngestionError(
            f"Unable to read file: {error}"
        ) from error

    # 6. Calculer les statistiques
    total_lines = len(lines)

    empty_lines = sum(
        1 for line in lines if not line.strip()
    )

    # 7. Retourner les informations
    return LogFileInfo(
        filename=path.name,
        extension=path.suffix.lower(),
        size_bytes=size_bytes,
        total_lines=total_lines,
        empty_lines=empty_lines,
        content=lines
    )
