import csv
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Union

# Configure logging
logger = logging.getLogger(__name__)

# Standard CSV Headers
# These can be expanded as more specific data fields are extracted.
DEFAULT_CSV_HEADERS = [
    "ExtractionTimestamp",  # When this row was added to the CSV
    "SourceEmailID",        # Message-ID of the source email
    "EmailReceivedDate",    # Date the email was received/processed by this system
    "IdentifiedAction",     # ADD, UPDATE, DELETE, INFO, OTHER, UNKNOWN
    "RelevanceScore",       # Optional: A score if relevance is not binary
    "MoveCode",             # e.g., MVO12345
    "MoveDate",             # Date of the equipment move
    "EquipmentID",          # e.g., EQ-001, Serial Number
    "EquipmentType",        # e.g., Crane, Forklift
    "OriginLocation",
    "DestinationLocation",
    "Quantity",             # If applicable
    "Carrier",              # Shipping company, if any
    "TrackingNumber",
    "Status",               # e.g., Scheduled, In Transit, Delivered, Cancelled
    "Notes",                # Any other extracted information or comments
    "RawEmailSubject",      # Full subject of the email
    "RawEmailBodySnippet",  # A snippet of the email body for context
    "AttachmentNames",      # Comma-separated list of relevant attachment names
    "SourceSender"          # Email address of the sender
]

class OutputHandler:
    def __init__(self, filepath: str, headers: List[str] = None):
        self.filepath = filepath
        self.headers = headers or DEFAULT_CSV_HEADERS
        self._initialize_csv()

    def _initialize_csv(self):
        """
        Initializes the CSV file with headers if it doesn't exist or is empty.
        """
        try:
            file_exists = os.path.isfile(self.filepath)
            is_empty = file_exists and os.path.getsize(self.filepath) == 0

            if not file_exists or is_empty:
                with open(self.filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=self.headers)
                    writer.writeheader()
                logger.info(f"CSV file initialized with headers at {self.filepath}")
            else:
                # Optional: Validate existing headers if file is not empty
                with open(self.filepath, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    existing_headers = next(reader, None)
                    if existing_headers != self.headers:
                        logger.warning(
                            f"CSV file at {self.filepath} has different headers than expected. "
                            f"Expected: {self.headers}. Found: {existing_headers}. "
                            "This might lead to data misalignment if not handled."
                        )
                        # Decide on a strategy: error out, try to adapt, or overwrite.
                        # For now, we'll log a warning and proceed.
                logger.info(f"CSV file {self.filepath} already exists with headers.")

        except IOError as e:
            logger.error(f"Error initializing CSV file at {self.filepath}: {e}", exc_info=True)
            raise # Re-raise to indicate initialization failure

    def append_data_row(self, data_row_dict: Dict[str, Any]):
        """
        Appends a single data row (dictionary) to the CSV file.

        Args:
            data_row_dict: A dictionary where keys match the CSV headers.
                           Missing keys will result in empty cells for those columns.
                           Extra keys will be ignored.
        """
        try:
            # Ensure all header fields are present in the dict, even if with None/empty value
            # This makes DictWriter behave predictably.
            row_to_write = {header: data_row_dict.get(header) for header in self.headers}

            with open(self.filepath, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.headers)
                writer.writerow(row_to_write)
            logger.debug(f"Data row appended to {self.filepath}: {row_to_write.get('SourceEmailID', 'N/A')}")
        except IOError as e:
            logger.error(f"Error appending data to CSV file {self.filepath}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected error writing to CSV {self.filepath}: {e}", exc_info=True)

    def append_bulk_data(self, data_rows_list: List[Dict[str, Any]]):
        """
        Appends multiple data rows to the CSV file.

        Args:
            data_rows_list: A list of dictionaries, where each dictionary is a row.
        """
        try:
            rows_to_write = []
            for data_row_dict in data_rows_list:
                rows_to_write.append({header: data_row_dict.get(header) for header in self.headers})

            with open(self.filepath, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.headers)
                writer.writerows(rows_to_write)
            logger.info(f"Appended {len(rows_to_write)} data rows to {self.filepath}")
        except IOError as e:
            logger.error(f"Error appending bulk data to CSV file {self.filepath}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected error during bulk CSV write to {self.filepath}: {e}", exc_info=True)


# Example Usage (for testing purposes)
if __name__ == '__main__':
    # Configure basic logging for the example
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    logger.info("Starting OutputHandler example...")

    # Define a test CSV file path
    test_csv_filepath = "data/test_equipment_moves.csv"

    # Ensure the data directory exists for the test file
    os.makedirs(os.path.dirname(test_csv_filepath), exist_ok=True)

    # Clean up old test file if it exists for a fresh run
    if os.path.exists(test_csv_filepath):
        os.remove(test_csv_filepath)
        logger.info(f"Removed old test file: {test_csv_filepath}")

    try:
        # 1. Initialize OutputHandler (this will create the file with headers)
        output_handler = OutputHandler(filepath=test_csv_filepath)
        logger.info(f"OutputHandler initialized for {test_csv_filepath}")

        # 2. Prepare some sample data rows
        sample_data_1 = {
            "ExtractionTimestamp": datetime.now().isoformat(),
            "SourceEmailID": "<email1@example.com>",
            "EmailReceivedDate": "2023-10-01T10:00:00Z",
            "IdentifiedAction": "ADD",
            "MoveCode": "MC123",
            "MoveDate": "2023-10-05",
            "EquipmentID": "EQ-001",
            "EquipmentType": "Crane",
            "OriginLocation": "Warehouse A",
            "DestinationLocation": "Site B",
            "Quantity": 1,
            "Status": "Scheduled",
            "RawEmailSubject": "New Crane Movement MC123",
            "Notes": "Handle with care.",
            "SourceSender": "logistics@example.com"
        }

        sample_data_2 = {
            "ExtractionTimestamp": datetime.now().isoformat(),
            "SourceEmailID": "<email2@example.com>",
            "EmailReceivedDate": "2023-10-02T11:30:00Z",
            "IdentifiedAction": "UPDATE",
            "MoveCode": "MC456", # Different move
            "MoveDate": "2023-10-06",
            "EquipmentID": "EQ-002, EQ-003", # Multiple items
            "EquipmentType": "Forklift",
            "OriginLocation": "Depot X",
            "DestinationLocation": "Factory Y",
            "Status": "In Transit",
            "TrackingNumber": "TRK98765",
            "RawEmailSubject": "Update: Forklifts MC456 now in transit",
            "AttachmentNames": "details.pdf, manifest.xlsx",
            "SourceSender": "dispatch@example.com",
            "RelevanceScore": 0.95 # Example of an optional field
        }

        # An entry with fewer fields (others should be blank)
        sample_data_3 = {
            "ExtractionTimestamp": datetime.now().isoformat(),
            "SourceEmailID": "<email3@example.com>",
            "IdentifiedAction": "INFO",
            "RawEmailSubject": "Maintenance Schedule Q4",
            "Notes": "FYI only."
        }

        # 3. Append a single data row
        output_handler.append_data_row(sample_data_1)
        logger.info("Appended sample_data_1.")

        # 4. Append multiple data rows
        output_handler.append_bulk_data([sample_data_2, sample_data_3])
        logger.info("Appended sample_data_2 and sample_data_3 using bulk method.")

        # 5. Test initialization again (should not overwrite or add headers if file exists and has same headers)
        logger.info("Attempting to initialize OutputHandler again on the same file...")
        output_handler_reinit = OutputHandler(filepath=test_csv_filepath)
        logger.info("Re-initialization test complete.")

        # Verify content (manual check or by reading the CSV)
        logger.info(f"Test CSV file created/updated at: {test_csv_filepath}")
        logger.info("Please inspect the file to verify its contents.")

        # Example of reading it back for verification
        with open(test_csv_filepath, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            logger.info("Reading back content for verification:")
            for row in reader:
                logger.info(dict(row))


    except Exception as e:
        logger.error(f"An error occurred during the OutputHandler example: {e}", exc_info=True)

    logger.info("OutputHandler example finished.")
