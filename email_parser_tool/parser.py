import email
from email.parser import BytesParser
import logging
from .exceptions import InvalidEmailFormatException

logger = logging.getLogger(__name__)

class EmailParser:
    """
    A class to parse email messages from files.
    """
    def __init__(self):
        # No specific initialization needed for now
        pass

    def parse_email_file(self, file_path: str):
        """
        Parses an email file and extracts its content.

        Args:
            file_path (str): The path to the email file.

        Returns:
            dict: A dictionary containing the parsed email data (subject, from, to, date, body, attachments)
                  or None if parsing fails.
        """
        try:
            with open(file_path, 'rb') as f:
                msg = BytesParser().parse(f)

            subject = msg.get('Subject')
            from_ = msg.get('From')
            to = msg.get('To')
            date = msg.get('Date')

            body_text = ""
            html_body_text = "" # Store html body separately if no plain text is found

            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = part.get("Content-Disposition")

                if content_disposition is None: # Not an attachment
                    if part.get_content_maintype() == 'text':
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8' # Default to utf-8
                        try:
                            if part.get_content_subtype() == 'plain':
                                body_text = payload.decode(charset, errors='replace')
                            elif part.get_content_subtype() == 'html':
                                html_body_text = payload.decode(charset, errors='replace')
                        except (UnicodeDecodeError, AttributeError) as e:
                            logger.warning(f"Could not decode part of email {file_path} with charset {charset}: {e}")
                            # Fallback, try to decode with utf-8 if it wasn't already
                            if charset != 'utf-8':
                                try:
                                    if part.get_content_subtype() == 'plain':
                                        body_text = payload.decode('utf-8', errors='replace')
                                    elif part.get_content_subtype() == 'html':
                                        html_body_text = payload.decode('utf-8', errors='replace')
                                except (UnicodeDecodeError, AttributeError):
                                    logger.error(f"Fallback decode failed for part of email {file_path}")


            # Prioritize plain text body, but use HTML if plain is empty
            if not body_text and html_body_text:
                body_text = html_body_text
            elif not body_text and not html_body_text:
                 # Try to get body directly from message if walk didn't find text parts (for very simple emails)
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or 'utf-8'
                    try:
                        body_text = payload.decode(charset, errors='replace')
                    except (UnicodeDecodeError, AttributeError) as e:
                        logger.warning(f"Could not decode main payload of email {file_path}: {e}")
                        try: # Fallback
                           body_text = payload.decode('utf-8', errors='replace')
                        except (UnicodeDecodeError, AttributeError):
                           logger.error(f"Fallback decode failed for main payload of email {file_path}")


            attachments_list = []
            for part in msg.walk():
                # Check if the part is an attachment.
                # Parts with Content-Disposition 'attachment' are attachments.
                # Also, parts that are not 'multipart' and have a filename via get_filename()
                # but not 'inline' Content-Disposition can be considered attachments.
                # A more robust check might be needed if various email clients are targeted,
                # but `part.get('Content-Disposition') is not None` is a strong indicator.
                if part.get('Content-Disposition') is not None and "attachment" in part.get('Content-Disposition').lower():
                    filename = part.get_filename() # This can be None
                    try:
                        attachment_content = part.get_payload(decode=True)
                        attachments_list.append({
                            'filename': filename, # Store None if no filename
                            'content': attachment_content
                        })
                    except Exception as e:
                        # Use filename in log if available, otherwise a generic message
                        fn_for_log = filename if filename else "unnamed attachment"
                        logger.error(f"Could not get payload for {fn_for_log} in {file_path}: {e}")
                elif part.get_content_maintype() != 'multipart' and \
                     part.get_content_maintype() != 'text' and \
                     part.get_filename(): # Catch other potential attachments without explicit disposition
                    # This is a heuristic for parts that have a filename but are not text and not explicitly dispositioned
                    # Might catch things like embedded images not marked as 'inline' if not careful
                    # For now, let's keep it simple and focus on Content-Disposition based.
                    # The original code was:
                    # if part.get_content_maintype() != 'multipart' and part.get('Content-Disposition') is not None:
                    # This change makes it more specific to 'attachment' disposition.
                    pass # Keeping the structure, but this elif might be removed if only explicit attachments are desired.


            # Stricter definition for an email: must have some essential headers
            # This is to help with the non_email_file test case.
            if subject is None and from_ is None and to is None and date is None and not attachments_list:
                is_likely_email = False
                # If it's a multipart message, it's structured like an email.
                if msg.is_multipart():
                    is_likely_email = True
                # If it has a body and a recognized email content type, it might be a very simple email.
                elif body_text and ('text/plain' in msg.get_content_type() or 'text/html' in msg.get_content_type()):
                     # Check if it has at least one header that is common in emails
                    if msg.items(): # .items() gives list of (header_name, header_value)
                        is_likely_email = True

                if not is_likely_email:
                    logger.warning(f"File {file_path} does not appear to be a structured email (missing common headers/structure). Returning None.")
                    return None

            return {
                'subject': str(subject) if subject else None,
                'from': str(from_) if from_ else None,
                'to': str(to) if to else None,
                'date': str(date) if date else None,
                'body': body_text,
                'attachments': attachments_list
            }

        except FileNotFoundError:
            logger.error(f"Email file not found: {file_path}")
            return None
        except InvalidEmailFormatException: # Catch our custom exception if raised by a sub-parser in future
            logger.error(f"Invalid email format for file: {file_path}")
            raise # Re-raise it for the processor to handle
        except Exception as e:
            logger.error(f"Failed to parse email file {file_path}: {e.__class__.__name__} - {e}")
            # Optionally, re-raise as InvalidEmailFormatException or a new specific one
            # For now, returning None as per original plan for general errors
            return None
