from joplin_to_obsidian.utils import Colors


class TestColors:
    def test_has_color_codes(self) -> None:
        assert Colors.RED.startswith("\033")
        assert Colors.GREEN.startswith("\033")
        assert Colors.YELLOW.startswith("\033")
        assert Colors.BLUE.startswith("\033")
        assert Colors.RESET == "\033[0m"
