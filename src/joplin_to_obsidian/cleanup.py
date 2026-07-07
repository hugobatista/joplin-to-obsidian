import os
import re
from pathlib import Path

from joplin_to_obsidian.utils import atomic_write_text, print_error, print_status


def _available_path(base: Path) -> Path:
    path = base
    counter = 1
    while path.exists():
        path = base.with_stem(f"{base.stem}_{counter}")
        counter += 1
    return path


def remove_trailing_underscores(directory: Path) -> None:
    renames: list[tuple[Path, Path]] = []
    for root_str, dir_strs, files in os.walk(directory):
        root = Path(root_str)
        dirs: list[str] = dir_strs
        for file in files:
            name, ext = os.path.splitext(file)
            if (name.endswith("_") or name.endswith(" ")) and not re.match(
                r"^[_ ]+$", name
            ):
                old_path = root / file
                new_name = name.rstrip("_ ") + ext
                renames.append((old_path, _available_path(root / new_name)))
        for dir_name in dirs:
            if (dir_name.endswith("_") or dir_name.endswith(" ")) and not re.match(
                r"^[_ ]+$", dir_name
            ):
                old_path = root / dir_name
                new_name = dir_name.rstrip("_ ")
                renames.append((old_path, _available_path(root / new_name)))

    # Sort deepest-first so children are renamed before parents
    renames.sort(key=lambda r: str(r[0]), reverse=True)

    for old_path, new_path in renames:
        print_status(f"Renaming: {old_path} -> {new_path}")
        old_path.rename(new_path)


def remove_empty_resources_dirs(directory: Path) -> list[Path]:
    removed_dirs: list[Path] = []
    for root_str, dir_strs, files in os.walk(directory, topdown=False):
        root = Path(root_str)
        dirs: list[str] = dir_strs
        for dir_name in dirs:
            if dir_name == "_resources":
                dir_path = root / dir_name
                try:
                    if not any(dir_path.iterdir()):
                        print_status(f"Removing empty _resources directory: {dir_path}")
                        dir_path.rmdir()
                        removed_dirs.append(dir_path)
                    else:
                        msg = "_resources directory not empty, skipping: "
                        print_status(msg + str(dir_path))
                        contents = [p.name for p in dir_path.iterdir()]
                        print_status(f"  Contents: {contents}")
                except OSError as e:
                    print_error(f"Error checking/removing directory {dir_path}: {e}")
    return removed_dirs


def remove_location_frontmatter(directory: Path) -> list[Path]:
    processed_files: list[Path] = []
    for root_str, dir_strs, files in os.walk(directory):
        root = Path(root_str)
        for file in files:
            if file.lower().endswith((".md", ".markdown")):
                file_path = root / file
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if not content.startswith("---"):
                        continue
                    # Normalize Windows line endings
                    content = content.replace("\r\n", "\n")
                    parts = content.split("---\n", 2)
                    if len(parts) < 3:
                        continue
                    front_matter = parts[1]
                    body = parts[2]
                    original_front_matter = front_matter
                    front_matter = re.sub(
                        r"^(latitude|longitude|altitude)\s*:.*$",
                        "",
                        front_matter,
                        flags=re.MULTILINE,
                    )
                    # Remove blank lines that were adjacent to removed fields
                    front_matter = re.sub(r"\n\n+", "\n", front_matter)
                    front_matter = front_matter.strip()
                    if front_matter != original_front_matter:
                        if front_matter:
                            new_content = f"---\n{front_matter}\n---\n{body}"
                        else:
                            new_content = body
                        atomic_write_text(file_path, new_content)
                        print_status(f"Removed location data from: {file_path}")
                        processed_files.append(file_path)
                except Exception as e:
                    print_error(f"Error processing file {file_path}: {e}")
    return processed_files
