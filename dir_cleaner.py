import os
import re
import shutil
from datetime import datetime
import logging

class FileManager:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self._setup_logging()

    def _setup_logging(self):
        log_path = os.path.join(self.base_path, 'logs')
        os.makedirs(log_path, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_path, f'file_manager_{datetime.now().strftime("%Y%m%d")}.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def parse_comment(self, content: str) -> dict:
        """
        Parse SQL file comments to extract metadata.
        
        Args:
            content (str): The SQL file content
        
        Returns:
            dict: Extracted metadata (ticket, client, date, etc.)
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
            content (str): The SQL file content
        
        Returns:
            str: Extracted client name
        """
        match = re.search(r"USE\s+([a-zA-Z0-9_]+)", content, re.IGNORECASE)
        if match:
            # Extract client name from the database name (e.g., "TestClientInterfaceProd" -> "TestClient")
            db_name = match.group(1)
            client_match = re.match(r"([a-zA-Z]+)", db_name)
            return client_match.group(1) if client_match else db_name
        return "UnknownClient"

    def extract_ticket_from_filename(self, filename: str) -> str:
        """
        Extract the ticket number from the filename if present.
        
        Args:
            filename (str): The file name
        
        Returns:
            str: Extracted ticket number
        """
        match = re.search(r"(LBDM|LBIN|PROV)-\d+", filename)
        return match.group(0) if match else "UnknownTicket"

    def rename_sql_file(self, file_path: str):
        """
        Rename a SQL file based on metadata and content.
        
        Args:
            file_path (str): Path to the SQL file
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
        new_file_path = os.path.join(self.base_path, new_filename)

        # Rename file
        shutil.move(file_path, new_file_path)
        logging.info(f"Renamed {os.path.basename(file_path)} -> {new_filename}")

    def process_files(self):
        """
        Process all SQL files in the base path.
        """
        for filename in os.listdir(self.base_path):
            if filename.endswith('.sql'):
                file_path = os.path.join(self.base_path, filename)
                self.rename_sql_file(file_path)

# Example usage
if __name__ == "__main__":
    base_path = r"C:\Your\SQL\Folder"

    # Initialize the FileManager
    manager = FileManager(base_path)

    # Process files
    manager.process_files()
