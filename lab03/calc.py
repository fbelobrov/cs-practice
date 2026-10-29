"""Калькулятор: операция в аргументе запуска, два числа — в stdin."""

import sys


def calculate(a: float, b: float, operation: str = "+") -> float:
    """Выполнить выбранную арифметическую операцию."""
    if operation == "+":
        return a + b
    if operation == "-":
        return a - b
    if operation == "*":
        return a * b
    if operation == "/":
        if b == 0:
            raise ValueError("Деление на ноль невозможно")
        return a / b
    raise ValueError(f"Неизвестная операция: {operation}")


def main() -> None:
    operation = sys.argv[1] if len(sys.argv) > 1 else "+"
    try:
        a = float(input())
        b = float(input())
        print(calculate(a, b, operation))
    except ValueError as error:
        sys.exit(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
