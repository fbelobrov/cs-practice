"""Запуск из корня репозитория: python -m unittest discover -s lab06 -v."""

from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch

from solution import count_by_extension, deepest_path, human_size


class SolutionTests(unittest.TestCase):
    def test_extension_example(self):
        paths = ["docs/report.PDF", "notes.txt", "docs/img/logo.png", "Makefile"]
        self.assertEqual(count_by_extension(paths), {"pdf": 1, "txt": 1, "png": 1, "": 1})

    def test_extensions_case_and_repeated_entries(self):
        self.assertEqual(count_by_extension(["a.TXT", "b.txt", "a.TXT"]), {"txt": 3})

    def test_last_dot_and_hidden_file(self):
        self.assertEqual(count_by_extension(["archive.tar.gz", ".gitignore", "dir/.env", "file."]),
                         {"gz": 1, "": 3})

    def test_hidden_file_with_real_extension(self):
        self.assertEqual(count_by_extension([".config.JSON", "dir/.settings.toml", "...hidden"]),
                         {"json": 1, "toml": 1, "": 1})

    def test_dots_in_directories(self):
        self.assertEqual(count_by_extension(["folder.name/Makefile", "v1.2/docs/report.PDF"]),
                         {"": 1, "pdf": 1})

    def test_empty_extensions(self):
        self.assertEqual(count_by_extension([]), {})

    def test_deepest_example(self):
        self.assertEqual(deepest_path(["docs/report.pdf", "notes.txt", "docs/img/logo.png"]),
                         "docs/img/logo.png")

    def test_alphabetical_tie(self):
        self.assertEqual(deepest_path(["x/y/z.txt", "a/b/c.txt"]), "a/b/c.txt")
        self.assertEqual(deepest_path(["z.txt", "a.txt"]), "a.txt")

    def test_depth_counts_slashes_literally(self):
        self.assertEqual(deepest_path(["long-directory/long-file.txt", "a/b/c"]), "a/b/c")
        self.assertEqual(deepest_path(["a/b/c", "/x/y/z"]), "/x/y/z")

    def test_empty_deepest(self):
        self.assertEqual(deepest_path([]), "")

    def test_input_unchanged(self):
        paths = ["z/Z.TXT", "a/b/c.py", "Makefile"]
        before = paths.copy()
        count_by_extension(paths)
        deepest_path(paths)
        self.assertEqual(paths, before)

    def test_sizes_from_assignment(self):
        for size, expected in [(900, "900 Б"), (1536, "1.5 КБ"),
                               (5242880, "5.0 МБ"), (0, "0 Б"), (3221225472, "3.0 ГБ")]:
            with self.subTest(size=size):
                self.assertEqual(human_size(size), expected)

    def test_unit_boundaries(self):
        for size, expected in [(1, "1 Б"), (1023, "1023 Б"), (1024, "1.0 КБ"),
                               (1024**2, "1.0 МБ"), (1024**3, "1.0 ГБ"),
                               (1024**4, "1.0 ТБ"), (1024**5, "1024.0 ТБ")]:
            with self.subTest(size=size):
                self.assertEqual(human_size(size), expected)

    def test_rounding_to_one_decimal(self):
        self.assertEqual(human_size(1280), "1.2 КБ")
        self.assertEqual(human_size(2047), "2.0 КБ")

    def test_import_and_calls_have_no_io(self):
        spec = importlib.util.spec_from_file_location("import_check", Path(__file__).with_name("solution.py"))
        module = importlib.util.module_from_spec(spec)
        output = io.StringIO()
        with patch("builtins.input", side_effect=AssertionError("Не нужен ввод")):
            with patch("builtins.open", side_effect=AssertionError("Не нужны файлы")):
                with redirect_stdout(output):
                    spec.loader.exec_module(module)
                    module.count_by_extension(["nonexistent/a.txt"])
                    module.deepest_path(["nonexistent/a.txt"])
                    module.human_size(1536)
        self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
