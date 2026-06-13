import os
import re
from pathlib import Path

from joplin_to_obsidian.utils import print_error, print_status


def remove_trailing_underscores(directory: Path) -> None:
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
                new_path = root / new_name
                counter = 1
                base_new_path = new_path
                while new_path.exists():
                    new_path = base_new_path.with_stem(
                        f"{base_new_path.stem}_{counter}"
                    )
                    counter += 1
                print_status(f"Renaming file: {old_path} -> {new_path}")
                old_path.rename(new_path)
        for dir_name in dirs:
            if (dir_name.endswith("_") or dir_name.endswith(" ")) and not re.match(
                r"^[_ ]+$", dir_name
            ):
                old_path = root / dir_name
                new_name = dir_name.rstrip("_ ")
                new_path = root / new_name
                counter = 1
                base_new_path = new_path
                while new_path.exists():
                    new_path = Path(f"{base_new_path}_{counter}")
                    counter += 1
                print_status(f"Renaming directory: {old_path} -> {new_path}")
                old_path.rename(new_path)


def remove_empty_resources_dirs(directory: Path) -> list[Path]:
    removed_dirs: list[Path] = []
    for root_str, dir_strs, files in os.walk(directory):
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
                    if content.startswith("---\n"):
                        parts = content.split("---\n", 2)
                        if len(parts) >= 3:
                            front_matter = parts[1]
                            body = parts[2]
                            original_front_matter = front_matter
                            front_matter = re.sub(
                                r"^latitude:\s*[-+]?[0-9]*\.?[0-9]+\s*$",
                                "",
                                front_matter,
                                flags=re.MULTILINE,
                            )
                            front_matter = re.sub(
                                r"^longitude:\s*[-+]?[0-9]*\.?[0-9]+\s*$",
                                "",
                                front_matter,
                                flags=re.MULTILINE,
                            )
                            front_matter = re.sub(
                                r"^altitude:\s*[-+]?[0-9]*\.?[0-9]+\s*$",
                                "",
                                front_matter,
                                flags=re.MULTILINE,
                            )
                            front_matter = re.sub(r"\n\n+", "\n\n", front_matter)
                            front_matter = front_matter.strip()
                            if front_matter != original_front_matter:
                                if front_matter:
                                    new_content = f"---\n{front_matter}\n---\n{body}"
                                else:
                                    new_content = body
                                file_path.write_text(new_content, encoding="utf-8")
                                print_status(f"Removed location data from: {file_path}")
                                processed_files.append(file_path)
                except Exception as e:
                    print_error(f"Error processing file {file_path}: {e}")
    return processed_files
