"""Чтение журнала из стандартного ввода и печать отчёта."""

import sys

from stats import average_by_city, read_valid, warmest_city


def main() -> None:
    lines = sys.stdin.read().splitlines()
    records = read_valid(lines)
    averages = average_by_city(records)
    city = warmest_city(records)
    nonempty_count = sum(1 for line in lines if line.strip())
    skipped_count = nonempty_count - len(records)

    print(len(records))
    print(skipped_count)
    print(f"{averages.get(city, 0.0):.1f}")


if __name__ == "__main__":
    main()
