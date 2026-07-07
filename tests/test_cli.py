from pathlib import Path

from typer.testing import CliRunner

from joplin_to_obsidian.cli import app

runner = CliRunner()


class TestCli:
    def test_run_migration(self, vault: Path) -> None:
        result = runner.invoke(app, ["run", str(vault)], input="y\n")
        assert result.exit_code == 0

    def test_run_declines_with_n(self, vault: Path) -> None:
        result = runner.invoke(app, ["run", str(vault)], input="n\n")
        assert result.exit_code == 0
        assert "cancelled" in result.stdout.lower()

    def test_run_declines_with_no(self, vault: Path) -> None:
        result = runner.invoke(app, ["run", str(vault)], input="no\n")
        assert result.exit_code == 0

    def test_run_keyboard_interrupt(self, vault: Path, monkeypatch) -> None:
        def raise_keyboard(*args, **kwargs):
            raise KeyboardInterrupt()

        monkeypatch.setattr("builtins.input", raise_keyboard)
        result = runner.invoke(app, ["run", str(vault)])
        assert result.exit_code == 0
        assert "cancelled" in result.stdout.lower()

    def test_move_resources_command(self, vault: Path) -> None:
        result = runner.invoke(app, ["move-resources", str(vault)])
        assert result.exit_code == 0
        assert "Moving resources" in result.stdout

    def test_cleanup_files_command(self, vault: Path) -> None:
        result = runner.invoke(app, ["cleanup-files", str(vault)])
        assert result.exit_code == 0

    def test_cleanup_location_command(self, vault: Path) -> None:
        md = vault / "loc.md"
        md.write_text("---\nlatitude: 1.0\n---\ncontent")
        result = runner.invoke(app, ["cleanup-location", str(vault)])
        assert result.exit_code == 0
        assert "Removing location data" in result.stdout

    def test_dry_run(self, vault: Path) -> None:
        result = runner.invoke(app, ["--dry-run", "run", str(vault)], input="y\n")
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "will modify files" not in result.stdout

    def test_dry_run_preserves_files(self, vault: Path) -> None:
        (vault / "note_.md").write_text("trailing underscore")
        (vault / "loc.md").write_text("---\nlatitude: 1.0\n---\ncontent")
        (vault / "nested" / "_resources").mkdir(parents=True)
        result = runner.invoke(app, ["--dry-run", "run", str(vault)], input="y\n")
        assert result.exit_code == 0
        assert (vault / "note_.md").exists()
        assert (vault / "loc.md").read_text() == "---\nlatitude: 1.0\n---\ncontent"
        assert (vault / "nested" / "_resources").exists()
        assert "Would rename" in result.stdout
        assert "Would remove" in result.stdout
        assert "will modify files" not in result.stdout

    def test_errors_on_nonexistent_directory(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["run", str(tmp_path / "nope")])
        assert result.exit_code == 1

    def test_version(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "joplin-to-obsidian v0.2.0" in result.stdout

    def test_help_output(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Migrate Joplin notebook" in result.stdout


class TestCliErrorHandlers:
    def test_run_move_resources_error(self, vault: Path, monkeypatch) -> None:
        def broken(*args, **kwargs):
            raise RuntimeError("move failed")

        monkeypatch.setattr("joplin_to_obsidian.cli.move_resources", broken)
        result = runner.invoke(app, ["run", str(vault)], input="y\n")
        assert result.exit_code == 1

    def test_run_cleanup_trailing_error(self, vault: Path, monkeypatch) -> None:
        def broken(*args, **kwargs):
            raise RuntimeError("trailing failed")

        monkeypatch.setattr(
            "joplin_to_obsidian.cli.remove_trailing_underscores", broken
        )
        result = runner.invoke(app, ["run", str(vault)], input="y\n")
        assert result.exit_code == 1

    def test_run_cleanup_empty_dirs_error(self, vault: Path, monkeypatch) -> None:
        def broken(*args, **kwargs):
            raise RuntimeError("empty dirs failed")

        monkeypatch.setattr(
            "joplin_to_obsidian.cli.remove_empty_resources_dirs", broken
        )
        result = runner.invoke(app, ["run", str(vault)], input="y\n")
        assert result.exit_code == 1

    def test_run_cleanup_location_error(self, vault: Path, monkeypatch) -> None:
        def broken(*args, **kwargs):
            raise RuntimeError("location failed")

        monkeypatch.setattr(
            "joplin_to_obsidian.cli.remove_location_frontmatter", broken
        )
        result = runner.invoke(app, ["run", str(vault)], input="y\n")
        assert result.exit_code == 1

    def test_subcommand_move_resources_error(self, vault: Path, monkeypatch) -> None:
        def broken(*args, **kwargs):
            raise RuntimeError("move failed")

        monkeypatch.setattr("joplin_to_obsidian.cli.move_resources", broken)
        result = runner.invoke(app, ["move-resources", str(vault)])
        assert result.exit_code == 1

    def test_subcommand_cleanup_files_trailing_error(
        self, vault: Path, monkeypatch
    ) -> None:
        def broken(*args, **kwargs):
            raise RuntimeError("trailing failed")

        monkeypatch.setattr(
            "joplin_to_obsidian.cli.remove_trailing_underscores", broken
        )
        result = runner.invoke(app, ["cleanup-files", str(vault)])
        assert result.exit_code == 1

    def test_subcommand_cleanup_files_empty_dirs_error(
        self, vault: Path, monkeypatch
    ) -> None:
        def broken(*args, **kwargs):
            raise RuntimeError("empty dirs failed")

        monkeypatch.setattr(
            "joplin_to_obsidian.cli.remove_empty_resources_dirs", broken
        )
        result = runner.invoke(app, ["cleanup-files", str(vault)])
        assert result.exit_code == 1

    def test_subcommand_cleanup_location_error(self, vault: Path, monkeypatch) -> None:
        def broken(*args, **kwargs):
            raise RuntimeError("location failed")

        monkeypatch.setattr(
            "joplin_to_obsidian.cli.remove_location_frontmatter", broken
        )
        result = runner.invoke(app, ["cleanup-location", str(vault)])
        assert result.exit_code == 1
