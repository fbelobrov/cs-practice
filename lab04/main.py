"""Чтение журнала из стандартного ввода и печать отчёта."""

import sys

from stats import average_by_city, read_valid, warmest_city


def main() -> None:
    lines = sys.stdin.read().splitlines()
    records = read_valid(lines)
    averages = average_by_city(records)
    city = warmest_city(records)

    print(len(records))
    print(0)
    print(f"{averages.get(city, 0.0):.1f}")


if __name__ == "__main__":
    main()
