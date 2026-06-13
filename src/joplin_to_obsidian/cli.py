from pathlib import Path
from typing import Annotated

import typer

from joplin_to_obsidian import (
    move_resources,
    remove_empty_resources_dirs,
    remove_location_frontmatter,
    remove_trailing_underscores,
)
from joplin_to_obsidian.utils import (
    Colors,
    print_error,
    print_status,
    print_step,
)

OPERATIONS: list[str] = [
    "Move resources to _resources folders next to markdown files",
    "Remove trailing underscores and spaces from files and folders",
    "Remove empty _resources directories",
    "Remove location data from YAML front matter",
]

app = typer.Typer(
    help="Migrate Joplin notebook exports to Obsidian vaults.",
    rich_markup_mode="rich",
    add_completion=False,
)


def _version_callback(value: bool) -> None:
    if value:
        from joplin_to_obsidian import __version__

        print(f"joplin-to-obsidian v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            help="Show version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    pass


def _validate_dir(directory: Path) -> Path:
    resolved = directory.resolve()
    if not resolved.exists():
        print_error(f"Error: Directory does not exist: {resolved}")
        raise typer.Exit(code=1)
    return resolved


def _run_all(directory: Path) -> None:
    tool_name = f"{Colors.YELLOW}Obsidian Vault Migration"
    print(f"{tool_name} and Cleanup Tool{Colors.RESET}")
    print("=" * 50)
    print(f"Target directory: {Colors.BLUE}{directory}{Colors.RESET}")
    expected = f"\n{Colors.YELLOW}Expected input:{Colors.RESET}"
    print(f"{expected} Joplin notebook export in markdown + front matter format")
    print("The directory should contain:")
    print("  - Markdown files (.md) exported from Joplin")
    print("  - A '_resources' directory with attachments/images")
    print("  - YAML front matter in markdown files (if applicable)")
    print("\nThis script will perform the following operations:")
    for i, operation in enumerate(OPERATIONS, 1):
        print(f"{i}. {operation}")
    warning = f"\n{Colors.YELLOW}Warning:"
    print(f"{warning} This script will modify files and directories!{Colors.RESET}")

    try:
        response = input("\nDo you want to continue? (y/N): ").strip().lower()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        raise typer.Exit(code=0)

    if response not in ["y", "yes"]:
        print("Operation cancelled.")
        raise typer.Exit(code=0)

    print_status(f"Starting vault processing in: {directory}")

    print_step(1, "Moving resources to _resources folders")
    try:
        move_resources(directory)
    except Exception as e:
        print_error(f"Error during resource movement: {e}")
        raise typer.Exit(code=1)

    print_step(2, "Removing trailing underscores and spaces from files and folders")
    try:
        remove_trailing_underscores(directory)
    except Exception as e:
        print_error(f"Error during underscore cleanup: {e}")
        raise typer.Exit(code=1)

    print_step(3, "Removing empty _resources directories")
    try:
        removed_dirs = remove_empty_resources_dirs(directory)
        print_status(f"Removed {len(removed_dirs)} empty _resources directories")
    except Exception as e:
        print_error(f"Error during empty directory cleanup: {e}")
        raise typer.Exit(code=1)

    print_step(4, "Removing location data from YAML front matter")
    try:
        processed_files = remove_location_frontmatter(directory)
        print_status(f"Processed {len(processed_files)} markdown files")
    except Exception as e:
        print_error(f"Error during frontmatter cleanup: {e}")
        raise typer.Exit(code=1)

    print(f"\n{Colors.GREEN}All operations completed successfully!{Colors.RESET}")


@app.command(
    help="Run all migration steps with an interactive confirmation prompt."
)
def run(
    directory: Annotated[
        Path, typer.Argument(help="Root directory of the Obsidian vault")
    ] = Path.cwd(),
) -> None:
    _run_all(_validate_dir(directory))


@app.command(
    name="move-resources",
    help="Copy resources from the global _resources directory to local _resources "
    "folders next to each markdown file, then delete originals.",
)
def move_resources_command(
    directory: Annotated[
        Path, typer.Argument(help="Root directory of the Obsidian vault")
    ] = Path.cwd(),
) -> None:
    resolved = _validate_dir(directory)
    print_step(1, "Moving resources to _resources folders")
    try:
        move_resources(resolved)
    except Exception as e:
        print_error(f"Error during resource movement: {e}")
        raise typer.Exit(code=1)


@app.command(
    name="cleanup-files",
    help="Remove trailing underscores and spaces from file and folder names, "
    "then delete empty _resources directories.",
)
def cleanup_files_command(
    directory: Annotated[
        Path, typer.Argument(help="Root directory of the Obsidian vault")
    ] = Path.cwd(),
) -> None:
    resolved = _validate_dir(directory)
    print_step(2, "Removing trailing underscores and spaces from files and folders")
    try:
        remove_trailing_underscores(resolved)
    except Exception as e:
        print_error(f"Error during underscore cleanup: {e}")
        raise typer.Exit(code=1)
    print_step(3, "Removing empty _resources directories")
    try:
        removed_dirs = remove_empty_resources_dirs(resolved)
        print_status(f"Removed {len(removed_dirs)} empty _resources directories")
    except Exception as e:
        print_error(f"Error during empty directory cleanup: {e}")
        raise typer.Exit(code=1)


@app.command(
    name="cleanup-location",
    help="Remove latitude, longitude, and altitude from YAML front matter "
    "in all markdown files.",
)
def cleanup_location_command(
    directory: Annotated[
        Path, typer.Argument(help="Root directory of the Obsidian vault")
    ] = Path.cwd(),
) -> None:
    resolved = _validate_dir(directory)
    print_step(4, "Removing location data from YAML front matter")
    try:
        processed_files = remove_location_frontmatter(resolved)
        print_status(f"Processed {len(processed_files)} markdown files")
    except Exception as e:
        print_error(f"Error during frontmatter cleanup: {e}")
        raise typer.Exit(code=1)
