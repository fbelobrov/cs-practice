"""Построчная обработка журнала без чтения всего файла в память."""

from collections.abc import Iterable


LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR"}


def parse_event(line: str) -> dict:
    """Разобрать время, уровень и сообщение; неверная строка — ValueError."""
    parts = line.strip().split(maxsplit=2)
    if len(parts) != 3:
        raise ValueError("Ожидаются время, уровень и непустое сообщение")
    time, level, message = parts
    if level not in LEVELS:
        raise ValueError(f"Неизвестный уровень журнала: {level}")
    return {"time": time, "level": level, "message": message}


def count_levels(lines: Iterable[str]) -> dict:
    """Посчитать уровни и BROKEN, пропуская пустые строки."""
    counts = {}
    for line in lines:
        if not line.strip():
            continue
        try:
            level = parse_event(line)["level"]
        except ValueError:
            level = "BROKEN"
        counts[level] = counts.get(level, 0) + 1
    return counts
