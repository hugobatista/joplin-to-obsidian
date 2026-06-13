# Joplin to Obsidian Migration Tool 🔄

[![GitHub Tag](https://img.shields.io/github/v/tag/hugobatista/joplin-to-obsidian?logo=github&label=latest)](https://go.hugobatista.com/gh/joplin-to-obsidian/releases)
[![Lint](https://img.shields.io/github/actions/workflow/status/hugobatista/joplin-to-obsidian/lint.yml?label=Lint)](https://go.hugobatista.com/gh/joplin-to-obsidian/actions/workflows/lint.yml)
[![Test](https://img.shields.io/github/actions/workflow/status/hugobatista/joplin-to-obsidian/test.yml?label=Test)](https://go.hugobatista.com/gh/joplin-to-obsidian/actions/workflows/test.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/joplin-to-obsidian.svg)](https://pypi.org/project/joplin-to-obsidian)
[![GHCR Tag](https://img.shields.io/github/v/tag/hugobatista/joplin-to-obsidian?logo=docker&logoColor=white&label=GHCR)](https://go.hugobatista.com/gh/joplin-to-obsidian/packages)
[![Renovate](https://img.shields.io/badge/renovate-enabled-brightgreen?logo=renovatebot)](https://docs.renovatebot.com)

A Python tool to convert Joplin notebook exports (markdown + front matter format) into a format suitable for Obsidian vaults. It reorganizes resources, cleans up file names, and removes Joplin-specific metadata.

## Migration Workflow

1. **Export from Joplin**: Create an export using the "Markdown + Front Matter" format
2. **Process with this tool**: Run the migration tool against your Joplin export
3. **Import to Obsidian**: Import the processed files into your Obsidian vault

## ⚠️ Important Disclaimer

**This tool modifies your files and directories!** Always create a backup before running. The changes are irreversible.

## What This Tool Does

| Step | Operation | Subcommand |
|------|-----------|------------|
| 1 | Move resources from global `_resources` to local folders | `move-resources` |
| 2 | Remove trailing underscores/spaces from files & folders | — |
| 3 | Remove empty `_resources` directories | `cleanup-files` |
| 4 | Remove location data (latitude, longitude, altitude) from YAML front matter | `cleanup-location` |

## Installation

### pip

```bash
pip install joplin-to-obsidian
```

### uv

```bash
uv tool install joplin-to-obsidian
```

### Docker

```bash
docker pull ghcr.io/hugobatista/joplin-to-obsidian:latest
```

## Usage

### Run all steps (with confirmation prompt)

```bash
joplin-to-obsidian run /path/to/export
```

### Run individual steps

```bash
joplin-to-obsidian move-resources /path/to/export
joplin-to-obsidian cleanup-files /path/to/export
joplin-to-obsidian cleanup-location /path/to/export
```

Run `joplin-to-obsidian --help` for all options.

### Docker

```bash
# Run all steps
docker run -it --rm -v /path/to/export:/data ghcr.io/hugobatista/joplin-to-obsidian:latest run /data

# Build from source
docker build -t joplin-to-obsidian .
docker run -it --rm -v /path/to/export:/data joplin-to-obsidian run /data
```

## Input Structure

```
your-export-folder/
├── _resources/
│   ├── image1.png
│   ├── document.pdf
│   └── attachment.jpg
├── Note 1.md
├── Note 2.md
├── Subfolder/
│   ├── Note 3.md
│   └── Note 4.md
└── ...
```

## Output Structure

```
your-export-folder/
├── Note 1.md
├── _resources/
│   └── image1.png
├── Note 2.md
├── _resources/
│   └── document.pdf
├── Subfolder/
│   ├── Note 3.md
│   ├── _resources/
│   │   └── attachment.jpg
│   └── Note 4.md
└── ...
```

## Technical Details

- **Language**: Python 3.10+
- **Dependencies**: Typer (for CLI), otherwise standard library
- **File Encoding**: UTF-8

## Troubleshooting

### "Resource not found" errors

Markdown files may reference resources that don't exist in the `_resources` directory. The tool skips these and continues.

### Permission errors

Ensure you have write permissions for the directory and all its contents.

### File conflicts

If cleanup creates duplicate names, the tool automatically appends numbers to avoid conflicts.

### Validation

After running, verify that:
- All markdown files still open correctly
- Images and attachments are still accessible
- No important data was lost

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE).
