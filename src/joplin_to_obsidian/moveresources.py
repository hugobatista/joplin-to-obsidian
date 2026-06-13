import os
import re
import shutil
from pathlib import Path
from urllib.parse import unquote

from joplin_to_obsidian.utils import print_error, print_status


def move_resources(root_dir: Path) -> None:
    resources_dir = root_dir / "_resources"
    print_status(f"Starting resource migration from: {resources_dir}")
    copied_sources: set[Path] = set()

    for root_str, dir_strs, files in os.walk(root_dir):
        root = Path(root_str)
        for file in files:
            if not file.endswith(".md"):
                continue
            md_path = root / file
            local_resources_dir = root / "_resources"

            content = md_path.read_text(encoding="utf-8")
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
                    print_status(f"Found resource: {resource_decoded}")
                elif not src.exists() and resource_encoded not in resources_to_copy:
                    print_error(f"Resource not found: {src}")

            if resources_to_copy:
                local_resources_dir.mkdir(parents=True, exist_ok=True)
                print_status(f"Created _resources directory: {local_resources_dir}")

                for resource_encoded, (
                    resource_decoded,
                    src,
                ) in resources_to_copy.items():
                    dst = local_resources_dir / resource_decoded
                    if src.resolve() == dst.resolve():
                        print_status(f"Resource already at target: {resource_decoded}")
                        continue
                    print_status(f"Copying: {resource_decoded}")
                    try:
                        shutil.copy2(src, dst)
                        copied_sources.add(src)
                        print_status(f"Copied {resource_decoded} to _resources")
                    except Exception as e:
                        err_msg = "Error copying"
                        ref = f"(referenced in {file}): {e}"
                        print_error(f"{err_msg} {resource_decoded} {ref}")

                for (
                    match,
                    resource_encoded,
                    resource_decoded,
                    link_type,
                ) in all_matches:
                    if resource_encoded in resources_to_copy:
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
                            link_text = (
                                link_text_match.group(1) if link_text_match else ""
                            )
                            new_link = f"[{link_text}](./_resources/{resource_decoded})"
                        content = content.replace(original_link, new_link)
                        update_msg = f"Updated {link_type} link for"
                        print_status(f"{update_msg} {resource_decoded} in {file}")

                md_path.write_text(content, encoding="utf-8")
                print_status(f"Saved updated {file}")
            else:
                print_status(f"No resources found in {file}")

    if copied_sources:
        cleanup_msg = "Cleaning up: deleting"
        print_status(
            f"{cleanup_msg} {len(copied_sources)} original files from {resources_dir}"
        )
        for src in sorted(copied_sources, key=lambda p: str(p)):
            try:
                src.unlink()
                print_status(f"Deleted original: {src.name}")
            except Exception as e:
                print_error(f"Error deleting {src}: {e}")
