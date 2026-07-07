import os
import sys
from pathlib import Path

import click


def red(text: str) -> str:
    return click.style(text, fg="red")


def green(text: str) -> str:
    return click.style(text, fg="green")


def yellow(text: str) -> str:
    return click.style(text, fg="yellow")


def blue(text: str) -> str:
    return click.style(text, fg="blue")


def print_status(message: str) -> None:
    if sys.stdout.isatty():
        try:
            terminal_width = os.get_terminal_size().columns
        except OSError:
            terminal_width = 80
        if len(message) > terminal_width:
            message = message[: terminal_width - 3] + "..."
        message = message.ljust(terminal_width)
        print(f"\r{message}", end="")
        sys.stdout.flush()
    else:
        print(message)


def print_error(message: str) -> None:
    if sys.stdout.isatty():
        try:
            terminal_width = os.get_terminal_size().columns
        except OSError:
            terminal_width = 80
        print("\r" + " " * terminal_width)
    click.echo(f"\r{red(message)}")
    sys.stdout.flush()


def print_step(step_number: int, message: str) -> None:
    click.echo(f"\n{blue(f'Step {step_number}: {message}')}")
    print("=" * 50)


def atomic_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding=encoding)
    tmp.replace(path)
