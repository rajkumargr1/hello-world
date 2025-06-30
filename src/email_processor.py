from email import message as email_message
import imaplib
import os
import yaml
from email.header import decode_header
from email.utils import parsedate_to_datetime
import logging
from typing import List, Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = 'config/config.yaml'

def load_config(config_path: str = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    """Loads the YAML configuration file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        # Basic validation
        if not config:
            raise ValueError("Config file is empty or invalid.")
        if 'email_server' not in config or 'processing' not in config:
            raise ValueError("Config file missing required sections: 'email_server' or 'processing'.")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found at {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}")
        raise
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise

class EmailProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.imap_server: Optional[imaplib.IMAP4_SSL] = None
        self.email_server_config = config.get('email_server', {})
        self.processing_config = config.get('processing', {})

        self.imap_host = self.email_server_config.get('host')
        self.imap_port = self.email_server_config.get('port', 993)
        self.imap_user = self.email_server_config.get('user')
        self.imap_password = os.environ.get(self.email_server_config.get('password_env_var', 'EMAIL_PASSWORD'))

        if not all([self.imap_host, self.imap_user, self.imap_password]):
            raise ValueError("Missing IMAP host, user, or password in config or environment variables.")

        self.temp_attachment_dir = self.processing_config.get('temp_attachment_dir', 'data/temp_attachments')
        if not os.path.exists(self.temp_attachment_dir):
            os.makedirs(self.temp_attachment_dir, exist_ok=True)
            logger.info(f"Created temporary attachment directory: {self.temp_attachment_dir}")

    def connect(self):
        """Connects to the IMAP server."""
        try:
            logger.info(f"Connecting to IMAP server: {self.imap_host}:{self.imap_port}")
            self.imap_server = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            self.imap_server.login(self.imap_user, self.imap_password)
            logger.info("Successfully connected and logged in to IMAP server.")
            self.imap_server.select("inbox") # Select inbox by default
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP connection error: {e}")
            self.imap_server = None
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during IMAP connection: {e}")
            self.imap_server = None
            raise

    def disconnect(self):
        """Disconnects from the IMAP server."""
        if self.imap_server:
            try:
                self.imap_server.logout()
                logger.info("Successfully logged out from IMAP server.")
            except imaplib.IMAP4.error as e:
                logger.warning(f"Error during IMAP logout: {e}")
            finally:
                self.imap_server = None

    def _decode_header(self, header_value: str) -> str:
        """Decodes email header, handling different charsets."""
        if not header_value:
            return ""
        decoded_parts = []
        for part, charset in decode_header(header_value):
            if isinstance(part, bytes):
                try:
                    decoded_parts.append(part.decode(charset or 'utf-8', errors='replace'))
                except LookupError: # Unknown encoding
                    decoded_parts.append(part.decode('utf-8', errors='replace')) # Fallback
            else:
                decoded_parts.append(part)
        return "".join(decoded_parts)

    def fetch_unseen_emails(self, criteria: str = "UNSEEN") -> List[Dict[str, Any]]:
        """Fetches emails based on criteria (e.g., "UNSEEN", "ALL", "SINCE <date>")."""
        if not self.imap_server:
            logger.error("Not connected to IMAP server. Call connect() first.")
            raise ConnectionError("Not connected to IMAP server.")

        processed_emails: List[Dict[str, Any]] = []
        try:
            status, messages = self.imap_server.search(None, criteria)
            if status != "OK":
                logger.error(f"Failed to search emails with criteria '{criteria}': {messages[0].decode()}")
                return processed_emails

            email_ids = messages[0].split()
            logger.info(f"Found {len(email_ids)} email(s) with criteria '{criteria}'.")

            for email_id in email_ids:
                email_data: Dict[str, Any] = {"id": email_id.decode()}
                try:
                    status, msg_data = self.imap_server.fetch(email_id, "(RFC822)")
                    if status != "OK":
                        logger.warning(f"Failed to fetch email ID {email_id.decode()}: {msg_data[0].decode()}")
                        continue

                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email_message.message_from_bytes(response_part[1])

                            email_data["subject"] = self._decode_header(msg.get("Subject"))
                            email_data["from"] = self._decode_header(msg.get("From"))
                            email_data["to"] = self._decode_header(msg.get("To"))
                            raw_date = msg.get("Date")
                            email_data["date"] = parsedate_to_datetime(raw_date).isoformat() if raw_date else None
                            email_data["message_id"] = msg.get("Message-ID")

                            body, attachments = self._parse_email_parts(msg)
                            email_data["body"] = body
                            email_data["attachments"] = attachments

                            processed_emails.append(email_data)
                            # Mark email as seen (optional, depends on workflow)
                            # self.imap_server.store(email_id, '+FLAGS', '\\Seen')

                except Exception as e:
                    logger.error(f"Error processing email ID {email_id.decode()}: {e}", exc_info=True)

            return processed_emails

        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP error while fetching emails: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching emails: {e}", exc_info=True)
            raise

    def _parse_email_parts(self, msg: email_message.Message) -> Tuple[str, List[Dict[str, str]]]:
        """Parses email parts to extract body and attachments."""
        body = ""
        attachments: List[Dict[str, str]] = []

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        filename = self._decode_header(filename)
                        filepath = os.path.join(self.temp_attachment_dir, filename)
                        try:
                            with open(filepath, "wb") as f:
                                f.write(part.get_payload(decode=True))
                            attachments.append({"filename": filename, "filepath": filepath, "content_type": content_type})
                            logger.info(f"Saved attachment: {filename} to {filepath}")
                        except Exception as e:
                            logger.error(f"Failed to save attachment {filename}: {e}")
                elif content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        body += part.get_payload(decode=True).decode(charset, errors='replace')
                    except Exception as e:
                        logger.warning(f"Could not decode plain text part with charset {part.get_content_charset()}: {e}")
                        # Fallback or skip part
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    # For now, we are primarily interested in plain text.
                    # HTML body could be parsed later if needed.
                    # Could add HTML to plain text conversion here.
                    pass # logger.debug("Skipping HTML part for now.")
        else: # Not a multipart email, just a single part
            content_type = msg.get_content_type()
            if content_type == "text/plain":
                try:
                    charset = msg.get_content_charset() or 'utf-8'
                    body = msg.get_payload(decode=True).decode(charset, errors='replace')
                except Exception as e:
                    logger.warning(f"Could not decode non-multipart plain text body with charset {msg.get_content_charset()}: {e}")

        return body.strip(), attachments

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

# Example Usage (for testing purposes, will be moved to main.py or tests)
if __name__ == '__main__':
    logger.info("Starting email processor example...")
    try:
        # Create a dummy .env file for this example if EMAIL_PASSWORD is not set
        if not os.getenv('EMAIL_PASSWORD'):
            logger.warning("EMAIL_PASSWORD environment variable not set. Create a .env file or set it.")
            logger.warning("Attempting to use placeholder credentials from config (if any) - this will likely fail.")
            # Example: with open(".env", "w") as f:
            # f.write("EMAIL_PASSWORD=your_actual_password\n")
            # from dotenv import load_dotenv
            # load_dotenv()

        config = load_config() # Loads from config/config.yaml by default

        # Override with actual credentials for local testing if not using .env
        # Ensure your config.yaml has your actual test server details if not using env vars
        # config['email_server']['user'] = "your_test_email@example.com"
        # config['email_server']['host'] = "imap.your_test_provider.com"
        # Note: Storing passwords directly in config is not recommended for production.
        # Use environment variables loaded via python-dotenv or a proper secrets manager.

        if not config['email_server'].get('user') or \
           not config['email_server'].get('host') or \
           not os.environ.get(config['email_server'].get('password_env_var', 'EMAIL_PASSWORD')):
            logger.error("Email server credentials or host not fully configured. Aborting example.")
            exit(1)

        with EmailProcessor(config) as processor:
            logger.info("Fetching unseen emails...")
            # For testing, you might want to fetch 'ALL' if 'UNSEEN' yields nothing
            # emails = processor.fetch_unseen_emails(criteria="ALL SUBJECT 'test'")
            unseen_emails = processor.fetch_unseen_emails()

            if unseen_emails:
                logger.info(f"\nFetched {len(unseen_emails)} unseen email(s):")
                for i, email_info in enumerate(unseen_emails):
                    logger.info(f"\n--- Email {i+1} ---")
                    logger.info(f"  ID: {email_info['id']}")
                    logger.info(f"  From: {email_info['from']}")
                    logger.info(f"  To: {email_info['to']}")
                    logger.info(f"  Date: {email_info['date']}")
                    logger.info(f"  Subject: {email_info['subject']}")
                    logger.info(f"  Message-ID: {email_info['message_id']}")
                    logger.info(f"  Body Preview (first 200 chars): {email_info['body'][:200].replace('\\n', ' ')}...")
                    if email_info['attachments']:
                        logger.info(f"  Attachments ({len(email_info['attachments'])}):")
                        for att in email_info['attachments']:
                            logger.info(f"    - File: {att['filename']}, Type: {att['content_type']}, Saved: {att['filepath']}")
                    else:
                        logger.info("  No attachments.")
            else:
                logger.info("No unseen emails found.")

            # Example: Fetching ALL emails (use with caution on large mailboxes)
            # all_emails = processor.fetch_unseen_emails(criteria="ALL")
            # logger.info(f"\nFetched {len(all_emails)} ALL email(s). First one: {all_emails[0]['subject'] if all_emails else 'None'}")

    except ConnectionError as e:
        logger.error(f"Could not connect to email server: {e}")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred in the example: {e}", exc_info=True)

    logger.info("Email processor example finished.")
