import os
import re
import shutil
import logging
from datetime import datetime


class FileManager:
    def __init__(self, base_path: str):
        """
        Initialize the FileManager class.

        Args:
            base_path (str): The root directory where files are located.
        """
        self.base_path = base_path
        self._setup_logging()

    def _setup_logging(self):
        """
        Setup logging configuration to log all file operations.
        """
        log_path = os.path.join(self.base_path, 'logs')
        os.makedirs(log_path, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_path, f'file_manager_{datetime.now().strftime("%Y%m%d")}.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def get_category(self, file_extension: str) -> str:
        """
        Determine the category of a file based on its extension.

        Args:
            file_extension (str): File extension.

        Returns:
            str: Category name.
        """
        categories = {
            'audio': (".mp3", ".wav", ".flac"),
            'video': (".mp4", ".mov"),
            'images': (".jpg", ".jpeg", ".png", ".gif"),
            'documents': (".pdf", ".docx", ".txt", ".xlsx"),
            'database_scripts': (".sql",),
            'python_scripts': (".py",)
        }
        for category, extensions in categories.items():
            if file_extension in extensions:
                return category.capitalize()
        return "Other"

    def parse_comment(self, content: str) -> dict:
        """
        Parse SQL file comments to extract metadata.

        Args:
            content (str): The SQL file content.

        Returns:
            dict: Extracted metadata (ticket, client, date, etc.).
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
        Extract client name from the first USE statement in the SQL file.

        Args:
            content (str): The SQL file content.

        Returns:
            str: Extracted client name.
        """
        match = re.search(r"USE\s+([a-zA-Z0-9_]+)", content, re.IGNORECASE)
        if match:
            db_name = match.group(1)
            client_match = re.match(r"([a-zA-Z]+)", db_name)
            return client_match.group(1) if client_match else db_name
        return "UnknownClient"

    def extract_ticket_from_filename(self, filename: str) -> str:
        """
        Extract the ticket number from the filename if present.

        Args:
            filename (str): The file name.

        Returns:
            str: Extracted ticket number.
        """
        match = re.search(r"(LBDM|LBIN|PROV)-\d+", filename)
        return match.group(0) if match else "UnknownTicket"

    def rename_sql_file(self, file_path: str, destination_folder: str):
        """
        Rename a SQL file based on metadata and content.

        Args:
            file_path (str): Path to the SQL file.
            destination_folder (str): Folder to move the renamed file into.
        """
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

    def organize_files(self):
        """
        Organize files into categories based on type and apply SQL-specific rules.
        """
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
            os.makedirs(destination_folder, exist_ok=True)

            # Apply specific rules for SQL files
            if file_category == "Database_scripts":
                self.rename_sql_file(file_path, destination_folder)
            else:
                # Move other files to their respective category folders
                shutil.move(file_path, os.path.join(destination_folder, filename))
                logging.info(f"Moved {filename} to {destination_folder}")


# Example usage
if __name__ == "__main__":
    # Define the base path where files are located
    base_path = r"C:\Your\Files\Folder"

    # Initialize the FileManager
    manager = FileManager(base_path)

    # Organize files
    manager.organize_files()
