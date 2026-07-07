import sys

from joplin_to_obsidian.utils import Colors, print_error, print_status


class TestColors:
    def test_has_color_codes(self) -> None:
        assert Colors.RED.startswith("\033")
        assert Colors.GREEN.startswith("\033")
        assert Colors.YELLOW.startswith("\033")
        assert Colors.BLUE.startswith("\033")
        assert Colors.RESET == "\033[0m"


class TestOutput:
    def test_print_status_tty_truncated(self, monkeypatch) -> None:
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
        monkeypatch.setattr(
            "os.get_terminal_size",
            lambda: type("Size", (), {"columns": 5})(),
        )
        print_status("hello world")

    def test_print_status_tty_oserror(self, monkeypatch) -> None:
        import os as os_module

        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)

        def raise_oserror():
            raise OSError("no terminal")

        monkeypatch.setattr(os_module, "get_terminal_size", raise_oserror)
        print_status("hello")

    def test_print_error_tty(self, monkeypatch) -> None:
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
        print_error("error")
