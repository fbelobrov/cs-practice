"""Разбор строк путей и размеров без обращения к файловой системе."""


def count_by_extension(paths: list[str]) -> dict[str, int]:
    """Посчитать расширения имён файлов без точки и в нижнем регистре."""
    counts = {}
    for path in paths:
        filename = path.rsplit("/", 1)[-1]
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        counts[extension] = counts.get(extension, 0) + 1
    return counts


def deepest_path(paths: list[str]) -> str:
    """Выбрать максимум разделителей '/', при равенстве — по алфавиту."""
    return min(paths, key=lambda path: (-path.count("/"), path), default="")
