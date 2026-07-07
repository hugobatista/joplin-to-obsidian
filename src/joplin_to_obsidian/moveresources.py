import os
import re
import shutil
from pathlib import Path
from urllib.parse import unquote

from joplin_to_obsidian.utils import atomic_write_text, print_error, print_status


def move_resources(root_dir: Path, dry_run: bool = False) -> None:
    resources_dir = root_dir / "_resources"
    if dry_run:
        print(f"Would process resources from: {resources_dir}")
        md_count = 0
        copied_names: set[str] = set()
        update_count = 0
        save_count = 0
        saved_names: set[str] = set()
    else:
        print_status(f"Starting resource migration from: {resources_dir}")
    copied_sources: set[Path] = set()
    would_cleanup: set[Path] = set()
    already_at_target: list[str] = []

    for root_str, dir_strs, files in os.walk(root_dir):
        root = Path(root_str)
        for file in files:
            if not file.endswith(".md"):
                continue
            md_path = root / file
            local_resources_dir = root / "_resources"

            content = md_path.read_text(encoding="utf-8")
            content = content.replace("\r\n", "\n")

            if dry_run:
                md_count += 1
            else:
                print_status(f"Processing Markdown file: {md_path}")

            resources_to_copy: dict[str, tuple[str, Path]] = {}
            all_matches: list[tuple[re.Match[str], str, str, str]] = []

            for match in re.finditer(
                r'!?\[[^\]]*\]\((?:\.\./)*_resources/([^) "]+)[^)]*\)', content
            ):
                resource_encoded = match.group(1)
                resource_decoded = unquote(resource_encoded)
                basename = resource_decoded.rsplit("/", 1)[-1]
                if basename != resource_decoded or resource_decoded in (
                    ".",
                    "..",
                ):
                    print_error(f"Invalid resource path in link: {resource_encoded}")
                    continue
                src = resources_dir / resource_decoded
                all_matches.append(
                    (match, resource_encoded, resource_decoded, "markdown")
                )
                if src.exists() and resource_encoded not in resources_to_copy:
                    resources_to_copy[resource_encoded] = (
                        resource_decoded,
                        src,
                    )
                    if not dry_run:
                        print_status(f"Found resource: {resource_decoded}")
                elif not src.exists() and resource_encoded not in resources_to_copy:
                    print_error(f"Resource not found: {src}")

            for match in re.finditer(
                r'<img[^>]+src="(?:\.\./)*_resources/([^"]+)"[^>]*>', content
            ):
                resource_encoded = match.group(1)
                resource_decoded = unquote(resource_encoded)
                basename = resource_decoded.rsplit("/", 1)[-1]
                if basename != resource_decoded or resource_decoded in (
                    ".",
                    "..",
                ):
                    print_error(f"Invalid resource path in link: {resource_encoded}")
                    continue
                src = resources_dir / resource_decoded
                all_matches.append((match, resource_encoded, resource_decoded, "html"))
                if src.exists() and resource_encoded not in resources_to_copy:
                    resources_to_copy[resource_encoded] = (
                        resource_decoded,
                        src,
                    )
                    if not dry_run:
                        print_status(f"Found resource: {resource_decoded}")
                elif not src.exists() and resource_encoded not in resources_to_copy:
                    print_error(f"Resource not found: {src}")

            if resources_to_copy:
                if not dry_run:
                    local_resources_dir.mkdir(parents=True, exist_ok=True)
                    print_status(f"Created _resources directory: {local_resources_dir}")

                for resource_encoded, (
                    resource_decoded,
                    src,
                ) in resources_to_copy.items():
                    dst = local_resources_dir / resource_decoded
                    if src.resolve() == dst.resolve():
                        already_at_target.append(resource_decoded)
                        continue
                    if dry_run:
                        copied_names.add(resource_decoded)
                        would_cleanup.add(src)
                    else:
                        print_status(f"Copying: {resource_decoded}")
                        try:
                            shutil.copy2(src, dst)
                            copied_sources.add(src)
                            print_status(f"Copied {resource_decoded} to _resources")
                        except Exception as e:
                            err_msg = "Error copying"
                            ref = f"(referenced in {file}): {e}"
                            print_error(f"{err_msg} {resource_decoded} {ref}")

                cursor = 0
                segments: list[str] = []
                for (
                    match,
                    resource_encoded,
                    resource_decoded,
                    link_type,
                ) in all_matches:
                    if resource_encoded not in resources_to_copy:
                        continue
                    segments.append(content[cursor : match.start()])
                    original_link = match.group(0)
                    if link_type == "html":
                        new_link = re.sub(
                            r'src="(?:\.\./)*_resources/[^"]*"',
                            f'src="./_resources/{resource_decoded}"',
                            original_link,
                        )
                    elif original_link.startswith("!["):
                        new_link = f"![](./_resources/{resource_decoded})"
                    else:
                        link_text_match = re.match(r"\[([^\]]*)\]", original_link)
                        link_text = link_text_match.group(1) if link_text_match else ""
                        new_link = f"[{link_text}](./_resources/{resource_decoded})"
                    segments.append(new_link)
                    cursor = match.end()
                    if dry_run:
                        update_count += 1

                segments.append(content[cursor:])
                content = "".join(segments)

                if dry_run:
                    save_count += 1
                    saved_names.add(str(md_path.relative_to(root_dir)))
                else:
                    atomic_write_text(md_path, content)
                    print_status(f"Saved updated {file}")

    if dry_run:
        if md_count:
            print(f"  scanned {md_count} markdown files")
        if copied_names:
            names = sorted(copied_names)
            print(f"  would copy {len(names)} resource(s):")
            for name in names:
                print(f"    - {name}")
        if already_at_target:
            names = sorted(set(already_at_target))
            print(f"  {len(names)} resource(s) already at target:")
            for name in names:
                print(f"    - {name}")
        if update_count:
            print(f"  would update {update_count} link(s)")
        if save_count:
            print(f"  would save {save_count} file(s):")
            for name in sorted(saved_names):
                print(f"    - {name}")
        if would_cleanup:
            names = sorted(s.name for s in would_cleanup)
            print(f"  would delete {len(names)} original(s):")
            for name in names:
                print(f"    - {name}")
    elif copied_sources:
        print_status(
            f"Cleaning up: deleting {len(copied_sources)} "
            f"original files from {resources_dir}"
        )
        for src in sorted(copied_sources, key=lambda p: str(p)):
            try:
                src.unlink()
                print_status(f"Deleted original: {src.name}")
            except Exception as e:
                print_error(f"Error deleting {src}: {e}")
