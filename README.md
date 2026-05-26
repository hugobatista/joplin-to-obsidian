# Joplin to Obsidian Migration Tool 🔄

A Python tool to convert Joplin notebook exports (markdown + front matter format) into a format suitable for Obsidian vaults. This tool reorganizes resources, cleans up file names, and removes Joplin-specific metadata to create a cleaner Obsidian-compatible structure.

## Migration Workflow

This tool is designed to help you migrate your notes from Joplin to Obsidian in three steps:

1. **Export from Joplin**: Create an export from Joplin using the "Markdown + Front Matter" format
2. **Process with this tool**: Run this migration tool against your Joplin export to clean and reorganize the files
3. **Import to Obsidian**: Import the processed files into your Obsidian vault

## ⚠️ Important Disclaimer

**This tool modifies your files and directories!** Always create a backup of your data before running this tool. The changes are irreversible, and while the tool is designed to be safe, unexpected issues can occur.

## What This Tool Does

This tool processes Joplin exports and performs the following operations:

1. **Resource Organization**: Moves resources from the global `_resources` directory to local `_resources` folders next to each markdown file that references them
2. **File Cleanup**: Removes trailing underscores and spaces from file and folder names
3. **Directory Cleanup**: Removes empty `_resources` directories after processing
4. **Metadata Cleanup**: Removes location data (latitude, longitude, altitude) from YAML front matter

## Prerequisites

- Python 3.6 or higher
- A Joplin export in "Markdown + Front Matter" format

## Installation

Clone this repository:
```bash
git clone https://go.hugobatista.com/gh/joplin-to-obsidian.git
cd joplin-to-obsidian
```

No additional dependencies are required - the tool uses only Python standard library modules.

## Usage

### Basic Usage

Run the tool in the directory containing your Joplin export:

```bash
python main.py
```

### Specify a Different Directory

```bash
python main.py --dir /path/to/your/joplin/export
```

### Get Help

```bash
python main.py --help
```

## Input Structure

Your Joplin export should have the following structure:

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

Where:
- **Markdown files** (`.md`) contain your notes with YAML front matter
- **`_resources` directory** contains all attachments and images
- **Resource links** in markdown files point to `_resources/filename`

## Output Structure

After processing, the structure becomes:

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

## Processing Steps

### Step 1: Resource Migration

The tool scans all markdown files for resource references and moves the corresponding files from the global `_resources` directory to local `_resources` folders next to each markdown file.

**Supported link formats:**
- Markdown images: `![alt text](../_resources/image.png)`
- Markdown links: `[link text](../_resources/document.pdf)`
- HTML images: `<img src="../_resources/image.png" />`

**After processing:**
- `![alt text](../_resources/image.png)` → `![alt text](./_resources/image.png)`
- `[link text](../_resources/document.pdf)` → `[link text](./_resources/document.pdf)`

### Step 2: File Name Cleanup

Removes trailing underscores and spaces from files and folders while avoiding conflicts:

**Examples:**
- `My Note_.md` → `My Note.md`
- `Folder Name_ /` → `Folder Name/`
- `Document   .pdf` → `Document.pdf`

### Step 3: Directory Cleanup

Removes empty `_resources` directories that no longer contain any files after the migration.

### Step 4: Metadata Cleanup

Removes location-specific metadata from YAML front matter:

**Before:**
```yaml
---
title: My Note
created: 2023-01-01T10:00:00.000Z
latitude: 40.7128
longitude: -74.0060
altitude: 10.5
---
```

**After:**
```yaml
---
title: My Note
created: 2023-01-01T10:00:00.000Z
---
```

## Examples

### Example 1: Basic Migration

```bash
# Navigate to your Joplin export directory
cd ~/Downloads/joplin-export

# Run the migration tool
python /path/to/joplin-to-obsidian/main.py

# The tool will show what it will do and ask for confirmation
```

### Example 2: Process a Specific Directory

```bash
# Process a specific directory
python main.py --dir ~/Documents/my-joplin-notes

# The tool will process the specified directory
```

### Example 3: Batch Processing

```bash
# You can process multiple exports by running the tool multiple times
for dir in ~/Downloads/joplin-export-*; do
    echo "Processing $dir"
    python main.py --dir "$dir"
done
```

## Troubleshooting

### Common Issues

1. **"Resource not found" errors**: This happens when markdown files reference resources that don't exist in the `_resources` directory. The tool will skip these references and continue processing.

2. **Permission errors**: Make sure you have write permissions for the directory and all its contents.

3. **File conflicts**: If the cleanup process would create duplicate names, the tool automatically appends numbers to avoid conflicts.

### Validation

After running the tool, verify that:
- All your markdown files still open correctly
- Images and attachments are still accessible
- No important data was lost (this is why backups are crucial!)

## Technical Details

- **Language**: Python 3.6+
- **Dependencies**: None (uses only standard library)
- **File Encoding**: UTF-8
- **Supported Platforms**: Cross-platform (Windows, macOS, Linux)

## Contributing

Issues and pull requests are welcome! Please feel free to contribute improvements or report bugs.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Remember**: Always backup your data before using this tool!
