"""Функции обработки журнала метеонаблюдений."""


def parse_record(line: str) -> dict:
    """Разобрать строку в запись о температуре."""
    city, temperature, date = line.split(";")
    return {"city": city, "temperature": float(temperature), "date": date}


def read_valid(lines: list[str]) -> list[dict]:
    """Преобразовать строки журнала в записи."""
    return [parse_record(line) for line in lines]


def average_by_city(records: list[dict]) -> dict:
    """Вычислить среднюю температуру каждого города до десятых."""
    totals = {}
    counts = {}
    for record in records:
        city = record["city"]
        totals[city] = totals.get(city, 0.0) + record["temperature"]
        counts[city] = counts.get(city, 0) + 1
    return {city: round(totals[city] / counts[city], 1) for city in totals}


def warmest_city(records: list[dict]) -> str:
    """Найти самый тёплый город; при равенстве выбрать по алфавиту."""
    averages = average_by_city(records)
    if not averages:
        return ""
    return min(averages, key=lambda city: (-averages[city], city))
