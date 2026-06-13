import os
import re
import shutil
from urllib.parse import unquote
from utils import print_status, print_error

def move_resources(root_dir):
    """Copy resources from _resources directory to _resources folders next to markdown files,
    then delete originals from the root _resources directory after all files are processed."""
    resources_dir = os.path.join(root_dir, '_resources')

    print_status(f"Starting resource migration from: {resources_dir}")

    # Track all source files that were successfully copied (across all markdown files)
    copied_sources = set()

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.md'):
                md_path = os.path.join(root, file)
                local_resources_dir = os.path.join(root, '_resources')

                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print_status(f"Processing Markdown file: {md_path}")

                # Collect all resources referenced in this file
                # resources_to_copy: encoded_name -> (decoded_name, src_path)
                resources_to_copy = {}
                all_matches = []

                # Match markdown image/link syntax: ![...](.../_resources/...) or [...](.../_resources/...)
                #
                # FIX 1: unquote() decodes percent-encoded filenames, e.g. %281%29 -> (1)
                # FIX 3: capture group ([^) "]+) stops at ), space, or " so that:
                #   - optional Markdown title  ![alt](file.jpg "My title")  is not included
                #   - linked images  [![](file.png)](http://...)  don't bleed into the URL
                #   - [^)]* then consumes the optional title before \) closes the link
                for match in re.finditer(r'!?\[[^\]]*\]\((?:\.\./)*_resources/([^) "]+)[^)]*\)', content):
                    resource_encoded = match.group(1)
                    resource_decoded = unquote(resource_encoded)
                    if os.path.basename(resource_decoded) != resource_decoded or resource_decoded in ('.', '..'):
                        print_error(f"Invalid resource path in link: {resource_encoded}")
                        continue
                    src = os.path.join(resources_dir, resource_decoded)
                    all_matches.append((match, resource_encoded, resource_decoded, 'markdown'))

                    if os.path.exists(src) and resource_encoded not in resources_to_copy:
                        resources_to_copy[resource_encoded] = (resource_decoded, src)
                        print_status(f"Found resource: {resource_decoded}")
                    elif not os.path.exists(src) and resource_encoded not in resources_to_copy:
                        print_error(f"Resource not found: {src}")

                # Match HTML img tags: <img ... src=".../_resources/..." ...>
                for match in re.finditer(r'<img[^>]+src="(?:\.\./)*_resources/([^"]+)"[^>]*>', content):
                    resource_encoded = match.group(1)
                    resource_decoded = unquote(resource_encoded)
                    if os.path.basename(resource_decoded) != resource_decoded or resource_decoded in ('.', '..'):
                        print_error(f"Invalid resource path in link: {resource_encoded}")
                        continue
                    src = os.path.join(resources_dir, resource_decoded)
                    all_matches.append((match, resource_encoded, resource_decoded, 'html'))

                    if os.path.exists(src) and resource_encoded not in resources_to_copy:
                        resources_to_copy[resource_encoded] = (resource_decoded, src)
                        print_status(f"Found resource: {resource_decoded}")
                    elif not os.path.exists(src) and resource_encoded not in resources_to_copy:
                        print_error(f"Resource not found: {src}")

                if resources_to_copy:
                    if not os.path.exists(local_resources_dir):
                        os.makedirs(local_resources_dir)
                        print_status(f"Created _resources directory: {local_resources_dir}")

                    # FIX 2: copy instead of move; track source paths for bulk cleanup at end
                    for resource_encoded, (resource_decoded, src) in resources_to_copy.items():
                        dst = os.path.join(local_resources_dir, resource_decoded)
                        print_status(f"Copying: {resource_decoded}")
                        try:
                            shutil.copy2(src, dst)
                            copied_sources.add(src)
                            print_status(f"Copied {resource_decoded} to _resources")
                        except Exception as e:
                            print_error(f"Error copying {resource_decoded} (referenced in {file}): {e}")

                    # Update all links in the markdown content
                    for match, resource_encoded, resource_decoded, link_type in all_matches:
                        if resource_encoded in resources_to_copy:
                            original_link = match.group(0)

                            if link_type == 'html':
                                new_link = re.sub(
                                    r'src="(?:\.\./)*_resources/[^"]*"',
                                    f'src="./_resources/{resource_decoded}"',
                                    original_link
                                )
                            elif original_link.startswith('!['):
                                new_link = f'![](./_resources/{resource_decoded})'
                            else:
                                link_text_match = re.match(r'\[([^\]]*)\]', original_link)
                                if link_text_match:
                                    link_text = link_text_match.group(1)
                                    new_link = f'[{link_text}](./_resources/{resource_decoded})'
                                else:
                                    new_link = f'[](./_resources/{resource_decoded})'

                            content = content.replace(original_link, new_link)
                            print_status(f"Updated {link_type} link for {resource_decoded} in {file}")

                    with open(md_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        print_status(f"Saved updated {file}")
                else:
                    print_status(f"No resources found in {file}")

    # FIX 2 (cont.): after all markdown files processed, delete originals from root _resources
    if copied_sources:
        print_status(f"Cleaning up: deleting {len(copied_sources)} original files from {resources_dir}")
        for src in sorted(copied_sources):
            try:
                os.remove(src)
                print_status(f"Deleted original: {os.path.basename(src)}")
            except Exception as e:
                print_error(f"Error deleting {src}: {e}")
