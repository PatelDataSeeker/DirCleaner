# FileManager - Advanced File Organization Utility

## Overview

FileManager is a powerful Python script designed to automatically organize and categorize files in a specified directory. It provides advanced features for file management, including:

- Automatic file categorization based on file extensions
- SQL file metadata extraction and intelligent renaming
- Logging of all file operations
- Optional backup before file organization
- Customizable file categories
- Log file retention management

## Features

- **Smart Categorization**: Automatically sorts files into categories like audio, video, documents, etc.
- **SQL File Handling**: 
  - Extracts metadata from SQL file comments
  - Renames SQL files based on ticket, client, and date information
- **Logging**: 
  - Comprehensive logging of all file operations
  - Daily log files with detailed information
- **Backup**: Optional backup creation before file organization
- **Dry Run Mode**: Preview file organization without making changes

## Prerequisites

- Python 3.7+
- Required libraries:
  ```
  No external libraries required beyond standard Python libraries
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/filemanager.git
   cd filemanager
   ```

2. No additional installation required. The script uses standard Python libraries.

## Usage

### Basic Usage

```python
from file_manager import FileManager

# Initialize FileManager with base path
manager = FileManager(r"C:\Your\Files\Folder")

# Organize files
manager.organize_files()
```

### Advanced Usage

```python
# Custom categories and configuration
custom_categories = {
    'design': (".psd", ".ai", ".sketch"),
    'web': (".html", ".css", ".js")
}

manager = FileManager(
    base_path=r"C:\Your\Files\Folder", 
    custom_categories=custom_categories, 
    log_retention_days=60
)

# Dry run to preview organization
manager.organize_files(dry_run=True, create_backup=False)

# Actual organization with backup
manager.organize_files(dry_run=False, create_backup=True)

# Optional log cleanup
manager.cleanup_old_logs()
```

## Configuration Options

- `base_path`: Root directory for file management
- `custom_categories`: Optional dictionary to add or modify file categories
- `log_retention_days`: Number of days to keep log files (default: 30)

## File Categorization

Default categories include:
- Audio
- Video
- Images
- Documents
- Database Scripts
- Python Scripts
- Compressed Files
- Other

## SQL File Naming Convention

For SQL files, the script attempts to extract:
- Ticket number (from comments or filename)
- Client name (from comments or USE statement)
- Date (from comments or current date)

Resulting in filenames like: `LBDM-123_ClientName_2023-12-05.sql`

## Error Handling

The script includes robust error handling:
- Validates base path existence and permissions
- Logs errors during file processing
- Prevents script from stopping on individual file errors

## Logging

- Log files are stored in a `logs` subdirectory
- Daily log files with timestamps
- Includes information about file movements and operations

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Your Name - your.email@example.com

Project Link: https://github.com/yourusername/filemanager
