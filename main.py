import logging
import os
import shutil
from datetime import datetime

# Attempt to load .env file if it exists for local development
try:
    from dotenv import load_dotenv
    if os.path.exists(".env"):
        load_dotenv()
        logging.info("Loaded .env file")
    else:
        logging.info(".env file not found, relying on environment variables set externally.")
except ImportError:
    logging.info("python-dotenv not installed, .env file will not be loaded. Relying on environment variables.")


from src.email_processor import EmailProcessor, load_config
from src.llm_handler import LLMHandler
from src.classification import is_email_relevant, identify_action
from src.output_handler import OutputHandler, DEFAULT_CSV_HEADERS

# Configure basic logging for the main application
# The level and format can be further customized in config.yaml if needed
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(message)s')
logger = logging.getLogger(__name__) # Use __name__ for the logger

def cleanup_attachments(attachment_paths: list):
    """Deletes specified attachment files."""
    for path in attachment_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                logger.debug(f"Cleaned up attachment: {path}")
        except OSError as e:
            logger.error(f"Error deleting attachment {path}: {e}")

def main():
    logger.info("Starting Main Email Processing Orchestrator...")

    try:
        # 1. Load Configuration
        config = load_config() # Uses default 'config/config.yaml'

        # Apply logging configuration from file if present
        log_cfg = config.get('logging', {})
        log_level = log_cfg.get('level', 'INFO').upper()
        log_format = log_cfg.get('format', '%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(message)s')

        # Reconfigure root logger if settings are in config
        # This will affect all loggers unless they have specific handlers
        logging.basicConfig(level=getattr(logging, log_level, logging.INFO), format=log_format, force=True)
        logger.info(f"Logging configured to level {log_level}.")


        # 2. Initialize Handlers
        logger.info("Initializing LLMHandler...")
        llm_handler = LLMHandler(config=config) # Pass the whole config

        output_csv_file = config.get('processing', {}).get('output_csv_file', 'data/equipment_moves.csv')
        # Ensure data directory exists for CSV
        os.makedirs(os.path.dirname(output_csv_file), exist_ok=True)
        logger.info(f"Initializing OutputHandler for CSV: {output_csv_file}")
        output_handler = OutputHandler(filepath=output_csv_file, headers=DEFAULT_CSV_HEADERS)

        # 3. Process Emails
        logger.info("Initializing EmailProcessor...")
        # EmailProcessor handles its own connection/disconnection via context manager
        with EmailProcessor(config=config) as email_processor:
            logger.info("Fetching emails...")
            # For testing, you might want to change criteria e.g., "ALL" or "SUBJECT \"test\""
            # emails_to_process = email_processor.fetch_unseen_emails(criteria="ALL")
            emails_to_process = email_processor.fetch_unseen_emails(criteria="UNSEEN")

            if not emails_to_process:
                logger.info("No new emails to process.")
                return

            logger.info(f"Fetched {len(emails_to_process)} email(s). Starting processing loop...")
            for i, email_data in enumerate(emails_to_process):
                email_id_for_log = email_data.get('message_id') or email_data.get('id', f"unknown_id_{i}")
                logger.info(f"--- Processing email {i+1}/{len(emails_to_process)} (ID: {email_id_for_log}) ---")
                logger.info(f"Subject: {email_data.get('subject')}")
                logger.info(f"From: {email_data.get('from')}")
                logger.info(f"Date: {email_data.get('date')}")

                attachment_files = [att['filepath'] for att in email_data.get('attachments', [])]
                attachment_names = [att['filename'] for att in email_data.get('attachments', [])]

                try:
                    # 4. Relevance Classification
                    logger.info("Performing relevance classification...")
                    relevant = is_email_relevant(
                        email_subject=email_data.get('subject', ''),
                        email_body=email_data.get('body', ''),
                        llm_handler=llm_handler,
                        raw_email_id=email_id_for_log
                    )
                    logger.info(f"Email relevance: {'RELEVANT' if relevant else 'NOT RELEVANT'}")

                    identified_action = "N/A" # Default if not relevant
                    if relevant:
                        # 5. Action Identification (only if relevant)
                        logger.info("Performing action identification...")
                        identified_action = identify_action(
                            email_subject=email_data.get('subject', ''),
                            email_body=email_data.get('body', ''),
                            llm_handler=llm_handler,
                            raw_email_id=email_id_for_log
                        )
                        logger.info(f"Identified action: {identified_action}")

                    # 6. Prepare data for CSV output
                    # This is a basic set of fields. More will be populated by specific content extractors later.
                    output_data = {
                        "ExtractionTimestamp": datetime.now().isoformat(),
                        "SourceEmailID": email_data.get('message_id', email_data.get('id')),
                        "EmailReceivedDate": email_data.get('date'),
                        "IdentifiedAction": identified_action if relevant else "NOT_RELEVANT", # Store action or relevance status
                        "RelevanceScore": 1.0 if relevant else 0.0, # Simple binary score for now
                        "MoveCode": None, # Placeholder - to be extracted by content agents
                        "MoveDate": None, # Placeholder
                        "EquipmentID": None, # Placeholder
                        "EquipmentType": None, # Placeholder
                        "OriginLocation": None, # Placeholder
                        "DestinationLocation": None, # Placeholder
                        "Quantity": None, # Placeholder
                        "Carrier": None, # Placeholder
                        "TrackingNumber": None, # Placeholder
                        "Status": None, # Placeholder
                        "Notes": "Initial classification.", # Placeholder
                        "RawEmailSubject": email_data.get('subject', ''),
                        "RawEmailBodySnippet": (email_data.get('body', '')[:250] + '...') if email_data.get('body') else '',
                        "AttachmentNames": ", ".join(attachment_names) if attachment_names else None,
                        "SourceSender": email_data.get('from')
                    }

                    output_handler.append_data_row(output_data)
                    logger.info(f"Data for email ID {email_id_for_log} written to CSV.")

                except Exception as e_proc:
                    logger.error(f"Error processing email ID {email_id_for_log}: {e_proc}", exc_info=True)
                    # Optionally, write an error entry to CSV or a separate error log
                finally:
                    # 7. Cleanup attachments for this email
                    if attachment_files:
                        logger.info(f"Cleaning up {len(attachment_files)} attachments for email ID {email_id_for_log}...")
                        cleanup_attachments(attachment_files)

            logger.info(f"Finished processing {len(emails_to_process)} email(s).")

    except ConnectionRefusedError as e: # More specific connection error
        logger.critical(f"CRITICAL: Could not connect to email server. Check credentials and server status: {e}", exc_info=True)
    except imaplib.IMAP4.error as e: # From email_processor if connection fails badly
         logger.critical(f"CRITICAL: IMAP specific error: {e}", exc_info=True)
    except ValueError as e: # Often from config issues
        logger.critical(f"CRITICAL: Configuration error or missing critical value: {e}", exc_info=True)
    except Exception as e:
        logger.critical(f"CRITICAL: An unexpected error occurred in the main orchestrator: {e}", exc_info=True)
    finally:
        logger.info("Main Email Processing Orchestrator finished.")

if __name__ == '__main__':
    # This allows running the main orchestrator directly
    # Ensure config/config.yaml is set up and environment variables (EMAIL_PASSWORD, LLM_API_KEY) are set.
    main()
