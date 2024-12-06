import os
import re
import shutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional


class FileManager:
    """
    A comprehensive file management utility for organizing and categorizing files.

    This class provides advanced file organization capabilities including:
    - Categorization of files based on extensions
    - SQL file metadata extraction and renaming
    - Logging of all file operations
    - Optional backup and dry run modes
    """

    def __init__(self, base_path: str, custom_categories: Optional[Dict[str, tuple]] = None, log_retention_days: int = 30):
        """
        Initialize the FileManager with configuration options.

        Args:
            base_path (str): Root directory where files are located.
            custom_categories (dict, optional): Custom file extension categories.
            log_retention_days (int, optional): Number of days to retain log files.

        Raises:
            ValueError: If base path is invalid.
            PermissionError: If insufficient permissions exist.
        """
        # Validate base path
        if not os.path.exists(base_path):
            raise ValueError(f"Base path does not exist: {base_path}")
        
        if not os.path.isdir(base_path):
            raise ValueError(f"Base path is not a directory: {base_path}")
        
        if not os.access(base_path, os.W_OK):
            raise PermissionError(f"Insufficient permissions for base path: {base_path}")

        # Set default and custom file categories
        self.default_categories = {
            'audio': (".mp3", ".wav", ".flac", ".aac"),
            'video': (".mp4", ".mov", ".avi", ".mkv"),
            'images': (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"),
            'documents': (".pdf", ".docx", ".txt", ".xlsx", ".csv", ".pptx"),
            'database_scripts': (".sql",),
            'python_scripts': (".py", ".ipynb"),
            'compressed': (".zip", ".rar", ".7z", ".gz")
        }
        
        # Merge custom categories if provided
        self.categories = {**self.default_categories, **custom_categories} if custom_categories else self.default_categories
        
        # Set configuration
        self.base_path = os.path.abspath(base_path)
        self.log_retention_days = log_retention_days
        
        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """
        Configure logging to track file management operations.
        
        Creates a log directory and sets up daily log files with detailed formatting.
        """
        log_path = os.path.join(self.base_path, 'logs')
        os.makedirs(log_path, exist_ok=True)
        
        log_file = os.path.join(log_path, f'file_manager_{datetime.now().strftime("%Y%m%d")}.log')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def get_category(self, file_extension: str) -> str:
        """
        Determine the category of a file based on its extension.

        Args:
            file_extension (str): File extension to categorize.

        Returns:
            str: Categorized file type (capitalized).
        """
        file_extension = file_extension.lower()
        for category, extensions in self.categories.items():
            if file_extension in [ext.lower() for ext in extensions]:
                return category.capitalize()
        return "Other"

    def parse_comment(self, content: str) -> dict:
        """
        Extract metadata from SQL file comments.

        Searches for a comment block with ticket, client, and date information.

        Args:
            content (str): The SQL file content.

        Returns:
            dict: Extracted metadata or empty dict if not found.
        """
        pattern = r"/\*\*+\s*Ticket:\s*(.*?);\s*Client:\s*(.*?);\s*Date:\s*(.*?);\s*.*?\*/"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return {
                'ticket': match.group(1).strip(),
                'client': match.group(2).strip(),
                'date': match.group(3).strip().replace("/", "-")
            }
        return {}

    def parse_use_statement(self, content: str) -> str:
        """
        Extract client name from the first USE statement in an SQL file.

        Args:
            content (str): The SQL file content.

        Returns:
            str: Extracted client name or 'UnknownClient'.
        """
        match = re.search(r"USE\s+([a-zA-Z0-9_]+)", content, re.IGNORECASE)
        if match:
            db_name = match.group(1)
            client_match = re.match(r"([a-zA-Z]+)", db_name)
            return client_match.group(1) if client_match else db_name
        return "UnknownClient"

    def extract_ticket_from_filename(self, filename: str) -> str:
        """
        Extract ticket number from filename if present.

        Args:
            filename (str): The file name to parse.

        Returns:
            str: Extracted ticket number or 'UnknownTicket'.
        """
        match = re.search(r"(LBDM|LBIN|PROV)-\d+", filename)
        return match.group(0) if match else "UnknownTicket"

    def rename_sql_file(self, file_path: str, destination_folder: str):
        """
        Rename SQL files based on extracted metadata.

        Attempts to extract ticket, client, and date information 
        to create a meaningful filename.

        Args:
            file_path (str): Path to the SQL file.
            destination_folder (str): Folder to move the renamed file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Parse metadata from comments
            metadata = self.parse_comment(content)

            # Extract ticket number from filename if comment is not available
            ticket = metadata.get('ticket') or self.extract_ticket_from_filename(os.path.basename(file_path))

            # Extract client name from comment or USE statement
            client = metadata.get('client') or self.parse_use_statement(content)

            # Use current date if no date is available
            date = metadata.get('date') or datetime.now().strftime("%Y-%m-%d")

            # Construct new file name
            new_filename = f"{ticket}_{client}_{date}.sql"
            new_file_path = os.path.join(destination_folder, new_filename)

            # Move and rename the file
            shutil.move(file_path, new_file_path)
            logging.info(f"Renamed {os.path.basename(file_path)} -> {new_filename}")
        
        except Exception as e:
            logging.error(f"Error renaming SQL file {file_path}: {e}")

    def organize_files(self, dry_run: bool = False, create_backup: bool = True):
        """
        Organize files into categories with optional backup and dry run.

        Args:
            dry_run (bool): If True, simulate organization without moving files.
            create_backup (bool): If True, create a backup before organizing.
        """
        # Create backup if requested
        if create_backup:
            backup_folder = os.path.join(self.base_path, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copytree(self.base_path, backup_folder, ignore=shutil.ignore_patterns('logs', '*.log'))
            logging.info(f"Created backup at {backup_folder}")

        # Process files
        for filename in os.listdir(self.base_path):
            file_path = os.path.join(self.base_path, filename)

            # Skip directories
            if os.path.isdir(file_path):
                continue

            # Identify file category
            file_extension = os.path.splitext(filename)[1].lower()
            file_category = self.get_category(file_extension)

            # Create destination folder for the file category
            destination_folder = os.path.join(self.base_path, file_category)

            # Skip processing in dry run
            if dry_run:
                logging.info(f"Would move {filename} to {destination_folder}")
                continue

            # Create destination folder
            os.makedirs(destination_folder, exist_ok=True)

            try:
                # Apply specific rules for SQL files
                if file_category == "Database_scripts":
                    self.rename_sql_file(file_path, destination_folder)
                else:
                    # Move other files to their respective category folders
                    shutil.move(file_path, os.path.join(destination_folder, filename))
                    logging.info(f"Moved {filename} to {destination_folder}")
            except Exception as e:
                logging.error(f"Error processing {filename}: {e}")

    def cleanup_old_logs(self):
        """
        Remove log files older than the specified retention period.
        """
        log_path = os.path.join(self.base_path, 'logs')
        current_time = datetime.now()
        
        for log_file in os.listdir(log_path):
            file_path = os.path.join(log_path, log_file)
            if os.path.isfile(file_path):
                file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if (current_time - file_modified).days > self.log_retention_days:
                    os.remove(file_path)
                    logging.info(f"Removed old log file: {log_file}")


def main():
    """
    Example usage of FileManager.
    """
    # Define the base path where files are located
    base_path = r"C:\Your\Files\Folder"  # Replace with your actual path

    try:
        # Create FileManager instance with custom configuration
        custom_categories = {
            'design': (".psd", ".ai", ".sketch"),
            'web': (".html", ".css", ".js")
        }
        
        manager = FileManager(
            base_path, 
            custom_categories=custom_categories, 
            log_retention_days=60
        )

        # Optional: Perform a dry run to preview organization
        print("Performing dry run...")
        manager.organize_files(dry_run=True, create_backup=False)

        # Confirm before actual organization
        proceed = input("Would you like to proceed with file organization? (yes/no): ").lower()
        if proceed == 'yes':
            print("Organizing files...")
            manager.organize_files(dry_run=False, create_backup=True)
            
            # Optional log cleanup
            manager.cleanup_old_logs()
            print("File organization complete.")
        else:
            print("File organization cancelled.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
