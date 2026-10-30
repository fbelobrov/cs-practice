"""Прочитать имя журнала из stdin, напечатать счётчики и сохранить отчёт."""

from pathlib import Path

from logstats import count_levels, format_report, top_errors


def main() -> None:
    path = Path(input().strip())
    script_dir = Path(__file__).resolve().parent
    if not path.is_absolute() and not path.is_file():
        path = script_dir / path

    with open(path, encoding="utf-8") as log:
        counts = count_levels(log)
    with open(path, encoding="utf-8") as log:
        errors = top_errors(log, 3)

    with open(script_dir / "report.txt", "w", encoding="utf-8", newline="\n") as report:
        report.write(format_report(counts, errors))

    print(sum(counts.values()))
    print(counts.get("ERROR", 0))
    print(counts.get("BROKEN", 0))


if __name__ == "__main__":
    main()
