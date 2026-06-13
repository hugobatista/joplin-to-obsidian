import os
import sys


class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


def print_status(message: str) -> None:
    try:
        terminal_width = os.get_terminal_size().columns
    except OSError:
        terminal_width = 80
    if len(message) > terminal_width:
        message = message[: terminal_width - 3] + "..."
    message = message.ljust(terminal_width)
    print(f"\r{message}", end="")
    sys.stdout.flush()


def print_error(message: str) -> None:
    try:
        terminal_width = os.get_terminal_size().columns
    except OSError:
        terminal_width = 80
    print("\r" + " " * terminal_width)
    print(f"\r{Colors.RED}{message}{Colors.RESET}")
    sys.stdout.flush()


def print_step(step_number: int, message: str) -> None:
    print(f"\n{Colors.BLUE}Step {step_number}: {message}{Colors.RESET}")
    print("=" * 50)
