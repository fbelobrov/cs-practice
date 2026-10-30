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


def top_errors(lines: Iterable[str], n: int) -> list[list]:
    """Вернуть n частых сообщений ERROR: частота по убыванию, затем алфавит."""
    if n <= 0:
        return []
    frequencies = {}
    for line in lines:
        if not line.strip():
            continue
        try:
            event = parse_event(line)
        except ValueError:
            continue
        if event["level"] == "ERROR":
            message = event["message"]
            frequencies[message] = frequencies.get(message, 0) + 1

    ordered = sorted(frequencies.items(), key=lambda item: (-item[1], item[0]))
    return [[message, count] for message, count in ordered[:n]]


def format_report(counts: dict, errors: list[list]) -> str:
    """Сформировать отчёт с алфавитным порядком уровней и конечным переносом."""
    report = ["Отчёт по журналу", ""]
    for level in sorted(counts):
        report.append(f"{level}: {counts[level]}")
    report.extend(["", "Частые ошибки:"])
    for message, count in errors:
        report.append(f"- {message} — {count}")
    return "\n".join(report) + "\n"
