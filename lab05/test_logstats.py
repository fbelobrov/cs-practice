"""Проверки: python -m unittest discover -s lab05 -v."""

from contextlib import redirect_stdout
import importlib.util
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from logstats import count_levels, format_report, parse_event, top_errors


class OnePassLines:
    """Источник разрешает только один последовательный проход."""

    def __init__(self, lines):
        self.lines = iter(lines)
        self.started = False

    def __iter__(self):
        if self.started:
            raise AssertionError("Повторный проход по одному источнику")
        self.started = True
        return self.lines

    def __getitem__(self, index):
        raise AssertionError("Индексация входных строк запрещена")

    def read(self):
        raise AssertionError("Чтение всего журнала запрещено")

    def readlines(self):
        raise AssertionError("Чтение всего журнала запрещено")


class LogstatsTests(unittest.TestCase):
    def test_parse_event(self):
        self.assertEqual(
            parse_event("2026-03-01T09:03:55 ERROR Не удалось открыть файл data.csv\n"),
            {"time": "2026-03-01T09:03:55", "level": "ERROR",
             "message": "Не удалось открыть файл data.csv"},
        )

    def test_whitespace_and_all_levels(self):
        for level in ("DEBUG", "INFO", "WARNING", "ERROR"):
            with self.subTest(level=level):
                self.assertEqual(
                    parse_event(f"  2026-03-01T09:12:30\t{level}   Два  слова  \n"),
                    {"time": "2026-03-01T09:12:30", "level": level, "message": "Два  слова"},
                )

    def test_invalid_event(self):
        for line in ("", "  ", "мусор", "t INFO", "t ERROR   ",
                     "t UNKNOWN текст", "t BROKEN текст", "t info текст"):
            with self.subTest(line=line):
                with self.assertRaises(ValueError):
                    parse_event(line)

    def test_count_levels_and_broken(self):
        lines = OnePassLines(["t INFO один", "t ERROR два", "t INFO три",
                              "неправильно", "t FATAL ошибка", "", " \n"])
        self.assertEqual(count_levels(lines), {"INFO": 2, "ERROR": 1, "BROKEN": 2})

    def test_empty_counts(self):
        self.assertEqual(count_levels([]), {})
        self.assertEqual(count_levels(iter(["", "\n", "  "])), {})

    def test_stream_many_lines(self):
        lines = OnePassLines("t INFO сообщение\n" for _ in range(100_000))
        self.assertEqual(count_levels(lines), {"INFO": 100_000})

    def test_error_frequency_and_tie(self):
        lines = OnePassLines(["t ERROR Бета", "t ERROR Альфа", "t ERROR Частая",
                              "t ERROR Частая", "t INFO Альфа", "t FATAL Альфа",
                              "плохая строка", "", " "])
        self.assertEqual(top_errors(lines, 3), [["Частая", 2], ["Альфа", 1], ["Бета", 1]])

    def test_top_limit_and_empty(self):
        self.assertEqual(top_errors(["t ERROR Б", "t ERROR А"], 1), [["А", 1]])
        self.assertEqual(top_errors(["t ERROR А"], 10), [["А", 1]])
        self.assertEqual(top_errors([], 3), [])
        self.assertEqual(top_errors(["t INFO текст", "мусор"], 3), [])
        self.assertEqual(top_errors(["t ERROR А"], 0), [])
        self.assertEqual(top_errors(["t ERROR А"], -1), [])

    def test_open_file_interface(self):
        self.assertEqual(count_levels(io.StringIO("t INFO один\nt ERROR два\n")),
                         {"INFO": 1, "ERROR": 1})
        self.assertEqual(top_errors(io.StringIO("t ERROR два\nt ERROR два\n"), 3),
                         [["два", 2]])

    def test_exact_report(self):
        self.assertEqual(
            format_report({"INFO": 1, "ERROR": 2}, [["Нет доступа", 2]]),
            "Отчёт по журналу\n\nERROR: 2\nINFO: 1\n\nЧастые ошибки:\n- Нет доступа — 2\n",
        )

    def test_report_empty(self):
        self.assertEqual(format_report({}, []), "Отчёт по журналу\n\n\nЧастые ошибки:\n")

    def test_imports_without_io(self):
        for filename in ("logstats.py", "main.py"):
            with self.subTest(filename=filename):
                spec = importlib.util.spec_from_file_location("import_check", Path(__file__).with_name(filename))
                module = importlib.util.module_from_spec(spec)
                output = io.StringIO()
                with patch("builtins.input", side_effect=AssertionError("Ввод при импорте")):
                    with redirect_stdout(output):
                        spec.loader.exec_module(module)
                self.assertEqual(output.getvalue(), "")


class AssignmentFilesTests(unittest.TestCase):
    def test_full_log(self):
        path = Path(__file__).with_name("events.log")
        with open(path, encoding="utf-8") as log:
            self.assertEqual(count_levels(log),
                             {"BROKEN": 2, "DEBUG": 4, "ERROR": 7, "INFO": 11, "WARNING": 5})
        with open(path, encoding="utf-8") as log:
            self.assertEqual(top_errors(log, 3), [
                ["Не удалось открыть файл data.csv", 4],
                ["Превышено время ожидания", 2],
                ["Нет доступа к каталогу /var/log", 1],
            ])

    def test_small_log(self):
        path = Path(__file__).with_name("events-small.log")
        with open(path, encoding="utf-8") as log:
            self.assertEqual(count_levels(log), {"INFO": 1, "ERROR": 2, "WARNING": 1})
        with open(path, encoding="utf-8") as log:
            self.assertEqual(top_errors(log, 3), [["Нет доступа к каталогу /var/log", 2]])


class MainTests(unittest.TestCase):
    def test_selected_file_and_report_location(self):
        cases = [
            ("custom.log", "t INFO Запуск\nt ERROR Сбой\nмусор\n\n \nt ERROR Сбой\n", "4\n2\n1\n"),
            ("empty.log", " \n\n", "0\n0\n0\n"),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            app = root / "app"
            app.mkdir()
            for name in ("main.py", "logstats.py"):
                shutil.copy2(Path(__file__).with_name(name), app / name)
            for name, contents, expected in cases:
                with self.subTest(filename=name):
                    (root / name).write_text(contents, encoding="utf-8")
                    result = subprocess.run(
                        [sys.executable, str(app / "main.py")], input=name + "\n", cwd=root,
                        text=True, encoding="utf-8", capture_output=True,
                        env={**os.environ, "PYTHONIOENCODING": "utf-8"}, check=True,
                    )
                    self.assertEqual(result.stdout, expected)
                    self.assertEqual(result.stderr, "")
                    report = app / "report.txt"
                    self.assertTrue(report.exists())
                    self.assertFalse((root / "report.txt").exists())
                    raw = report.read_bytes()
                    self.assertTrue(raw.endswith(b"\n"))
                    self.assertNotIn(b"\r", raw)
                    self.assertTrue(raw.decode("utf-8").startswith("Отчёт по журналу\n"))
                    if name == "custom.log":
                        self.assertEqual(raw.decode("utf-8"),
                            "Отчёт по журналу\n\nBROKEN: 1\nERROR: 2\nINFO: 1\n\nЧастые ошибки:\n- Сбой — 2\n")


if __name__ == "__main__":
    unittest.main()
