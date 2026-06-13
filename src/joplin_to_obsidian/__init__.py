"""Migrate Joplin notebook exports to Obsidian vaults."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("joplin-to-obsidian")
except PackageNotFoundError:
    __version__ = "dev"

from joplin_to_obsidian.cleanup import (
    remove_empty_resources_dirs,
    remove_location_frontmatter,
    remove_trailing_underscores,
)
from joplin_to_obsidian.moveresources import move_resources

__all__ = [
    "move_resources",
    "remove_trailing_underscores",
    "remove_empty_resources_dirs",
    "remove_location_frontmatter",
]
