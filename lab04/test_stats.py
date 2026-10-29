"""Проверки функций и запуска программы: python -m unittest discover -s lab04 -v."""

import contextlib
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import unittest

from stats import average_by_city, parse_record, read_valid, warmest_city


class StatsTests(unittest.TestCase):
    def test_parse_record(self):
        self.assertEqual(
            parse_record("Азов;24.5;2026-07-01"),
            {"city": "Азов", "temperature": 24.5, "date": "2026-07-01"},
        )

    def test_spaces_and_decimal_comma(self):
        self.assertEqual(
            parse_record(" Азов ; -3,5 ; 2026-01-09 "),
            {"city": "Азов", "temperature": -3.5, "date": "2026-01-09"},
        )

    def test_invalid_records(self):
        for line in ["", "мусор", "Азов;24", "Азов;24;дата;лишнее",
                     ";24;дата", "   ;24;дата", "Азов;24;  ",
                     "Азов;н/д;дата", "Азов;;дата"]:
            with self.subTest(line=line):
                with self.assertRaises(ValueError) as error:
                    parse_record(line)
                self.assertTrue(str(error.exception))

    def test_read_valid_continues_after_error(self):
        lines = ["", "  ", "Азов;24.5;дата", "мусор", "Таганрог;30;дата"]
        self.assertEqual(read_valid(lines), [parse_record(lines[2]), parse_record(lines[4])])

    def test_empty_collections(self):
        self.assertEqual(read_valid([]), [])
        self.assertEqual(average_by_city([]), {})
        self.assertEqual(warmest_city([]), "")

    def test_average_by_city(self):
        records = [
            {"city": "Азов", "temperature": 24.5},
            {"city": "Азов", "temperature": 25.5},
            {"city": "Таганрог", "temperature": 30.0},
        ]
        self.assertEqual(average_by_city(records), {"Азов": 25.0, "Таганрог": 30.0})
        self.assertEqual(warmest_city(records), "Таганрог")

    def test_average_rounding(self):
        records = [{"city": "Ростов", "temperature": 1.0},
                   {"city": "Ростов", "temperature": 2.0},
                   {"city": "Ростов", "temperature": 2.0}]
        self.assertEqual(average_by_city(records), {"Ростов": 1.7})

    def test_alphabetical_tie_with_negative_temperatures(self):
        records = [{"city": "Батайск", "temperature": -3.0},
                   {"city": "Азов", "temperature": -3.0},
                   {"city": "Ростов", "temperature": -10.0}]
        self.assertEqual(warmest_city(records), "Азов")

    def test_import_has_no_input_or_output(self):
        for filename in ("stats.py", "main.py"):
            with self.subTest(filename=filename):
                path = Path(__file__).with_name(filename)
                spec = importlib.util.spec_from_file_location("import_check", path)
                module = importlib.util.module_from_spec(spec)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    spec.loader.exec_module(module)
                self.assertEqual(output.getvalue(), "")


class MainTests(unittest.TestCase):
    def run_main(self, data):
        result = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("main.py"))],
            input=data, text=True, encoding="utf-8", capture_output=True,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}, check=True,
        )
        self.assertEqual(result.stderr, "")
        return result.stdout

    def test_assignment_example(self):
        self.assertEqual(
            self.run_main("Азов;24.5;2026-07-01\nмусор\nАзов;25.5;2026-07-02\nТаганрог;30;2026-07-01\n"),
            "3\n1\n30.0\n",
        )

    def test_blank_lines_are_not_errors(self):
        self.assertEqual(self.run_main("\n  \nАзов;-3,5;дата\nмусор\n\t\n"), "1\n1\n-3.5\n")

    def test_no_valid_records(self):
        for data, expected in [("", "0\n0\n0.0\n"), ("\n  \n", "0\n0\n0.0\n"),
                               ("мусор\n;24;дата\n", "0\n2\n0.0\n")]:
            with self.subTest(data=data):
                self.assertEqual(self.run_main(data), expected)


if __name__ == "__main__":
    unittest.main()
