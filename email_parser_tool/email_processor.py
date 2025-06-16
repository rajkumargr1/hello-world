import argparse
import os
import logging
import shutil
import sys
from .parser import EmailParser
from .exceptions import InvalidEmailFormatException

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def sanitize_filename(filename):
    """Remove or replace characters that are invalid in filenames."""
    # Basic sanitization: replace common problematic characters with underscore
    # This can be expanded based on specific OS limitations or requirements
    if filename is None:
        return None
    return "".join(c if c.isalnum() or c in ('.', '_', '-') else '_' for c in filename)


def main():
    """
    Main function to process emails.
    """
    parser = argparse.ArgumentParser(description="Process email files from an input directory and save results to an output directory.")
    parser.add_argument("input_dir", help="Path to the input directory containing email files.")
    parser.add_argument("output_dir", help="Path to the output directory to save processed files.")

    args = parser.parse_args()

    # Convert to absolute paths
    args.input_dir = os.path.abspath(args.input_dir)
    args.output_dir = os.path.abspath(args.output_dir)

    logging.info(f"Input directory: {args.input_dir}")
    logging.info(f"Output directory: {args.output_dir}")

    # Check if input_dir exists and is a directory
    if not os.path.isdir(args.input_dir):
        logger.error(f"Input directory not found or is not a directory: {args.input_dir}")
        sys.exit(1)

    # Create output directory if it doesn't exist
    try:
        os.makedirs(args.output_dir, exist_ok=True)
        logger.info(f"Ensured output directory exists: {args.output_dir}")
    except OSError as e:
        logger.critical(f"Failed to create or access output directory: {args.output_dir}. Error: {e}")
        sys.exit(1)

    email_parser = EmailParser()

    # Initialize counters
    total_files_scanned = 0
    emails_processed_successfully = 0
    files_skipped = 0
    output_write_errors = 0

    # Traverse the input directory
    for root, dirs, files in os.walk(args.input_dir):
        for file_name in files:
            total_files_scanned += 1
            file_path = os.path.join(root, file_name)
            current_email_save_success = True # Assume success for this email's output ops

            # Simple heuristic to identify email files
            if file_name.lower().endswith(('.eml', '.msg')):
                logger.info(f"Attempting to parse email file: {file_path}")
                try:
                    parsed_data = email_parser.parse_email_file(file_path)
                    if parsed_data:
                        logger.info(f"Successfully parsed: {file_path}, Subject: {parsed_data.get('subject')}")
                        num_attachments = len(parsed_data.get('attachments', []))
                        logger.info(f"Attachments found: {num_attachments}")

                        # Determine relative path for output structure
                        relative_path_to_file_dir = os.path.relpath(os.path.dirname(file_path), args.input_dir)
                        # Sanitize base filename for the extracted folder name
                        base_email_filename = os.path.splitext(os.path.basename(file_path))[0]
                        sanitized_base_email_filename = sanitize_filename(base_email_filename)

                        current_output_subdir_name = f"{sanitized_base_email_filename}_extracted"
                        if relative_path_to_file_dir == ".": # If file is in root of input_dir
                            current_output_subdir = os.path.join(args.output_dir, current_output_subdir_name)
                        else:
                            current_output_subdir = os.path.join(args.output_dir, relative_path_to_file_dir, current_output_subdir_name)


                        try:
                            os.makedirs(current_output_subdir, exist_ok=True)
                            logger.debug(f"Ensured output subdirectory exists: {current_output_subdir}")
                        except OSError as e:
                            logger.error(f"Failed to create output subdirectory {current_output_subdir} for {file_path}: {e}")
                            output_write_errors += 1
                            current_email_save_success = False
                            # Do not continue here; we want to log this email as skipped if dir creation failed.

                        if current_email_save_success: # Only proceed if directory was made
                            # Define output file paths
                            original_email_dest = os.path.join(current_output_subdir, os.path.basename(file_path))
                            subject_file_path = os.path.join(current_output_subdir, "subject.txt")
                            body_file_path = os.path.join(current_output_subdir, "body.txt")
                            subject_body_file_path = os.path.join(current_output_subdir, "subject_body.txt")

                            # Save original email
                            try:
                                shutil.copy2(file_path, original_email_dest)
                                logger.debug(f"Saved original email to: {original_email_dest}")
                            except IOError as e:
                                logger.error(f"Failed to save original email {os.path.basename(file_path)} to {original_email_dest}: {e}")
                                output_write_errors += 1
                                current_email_save_success = False

                            # Save Subject.txt
                            if parsed_data.get('subject') is not None:
                                try:
                                    with open(subject_file_path, "w", encoding="utf-8") as f:
                                        f.write(parsed_data['subject'])
                                    logger.debug(f"Saved subject to: {subject_file_path}")
                                except IOError as e:
                                    logger.error(f"Failed to save subject for {os.path.basename(file_path)} to {subject_file_path}: {e}")
                                    output_write_errors += 1
                                    current_email_save_success = False
                            else:
                                logger.info(f"Subject was empty for {file_path}, subject.txt not created.")

                            # Save Body.txt
                            if parsed_data.get('body') is not None and parsed_data.get('body').strip():
                                try:
                                    with open(body_file_path, "w", encoding="utf-8") as f:
                                        f.write(parsed_data['body'])
                                    logger.debug(f"Saved body to: {body_file_path}")
                                except IOError as e:
                                    logger.error(f"Failed to save body for {os.path.basename(file_path)} to {body_file_path}: {e}")
                                    output_write_errors += 1
                                    current_email_save_success = False
                            else:
                                logger.info(f"Body was empty or None for {file_path}, body.txt not created.")

                            # Save Subject_Body.txt
                            subject_str = parsed_data.get('subject', "")
                            body_str = parsed_data.get('body', "")
                            combined_content = f"Subject: {subject_str}\n\nBody:\n{body_str}"
                            try:
                                with open(subject_body_file_path, "w", encoding="utf-8") as f:
                                    f.write(combined_content)
                                logger.debug(f"Saved subject and body to: {subject_body_file_path}")
                            except IOError as e:
                                logger.error(f"Failed to save subject_body for {os.path.basename(file_path)} to {subject_body_file_path}: {e}")
                                output_write_errors += 1
                                current_email_save_success = False

                            # Save Attachments
                            attachments = parsed_data.get('attachments', [])
                            if attachments:
                                for index, attachment in enumerate(attachments):
                                    attachment_filename = attachment.get('filename')
                                    if not attachment_filename:
                                        _, ext = os.path.splitext(attachment.get('content_type', 'bin'))
                                        attachment_filename = f"unnamed_attachment_{index + 1}{'.' + ext if ext else ''}"

                                    sanitized_attachment_filename = sanitize_filename(attachment_filename)
                                    if not sanitized_attachment_filename:
                                        sanitized_attachment_filename = f"unnamed_attachment_{index + 1}_fallback"

                                    attachment_path = os.path.join(current_output_subdir, sanitized_attachment_filename)
                                    try:
                                        with open(attachment_path, "wb") as f:
                                            f.write(attachment['content'])
                                        logger.debug(f"Saved attachment to: {attachment_path}")
                                    except IOError as e:
                                        logger.error(f"Failed to save attachment {sanitized_attachment_filename} for {os.path.basename(file_path)} to {attachment_path}: {e}")
                                        output_write_errors += 1
                                        current_email_save_success = False
                                    except TypeError as e:
                                         logger.error(f"Attachment content for {sanitized_attachment_filename} in {os.path.basename(file_path)} is None or invalid: {e}")
                                         output_write_errors += 1
                                         current_email_save_success = False
                            else:
                                logger.info(f"No attachments found for {file_path}.")

                        if current_email_save_success:
                            emails_processed_successfully +=1
                        else:
                            # If directory creation failed, this email is effectively skipped in terms of successful processing.
                            # If parsing was successful but output failed, it's not counted in emails_processed_successfully.
                            # The output_write_errors counter will reflect these issues.
                            # If directory creation itself failed, it's already logged and current_email_save_success is false.
                            # We can consider adding it to files_skipped if directory creation failed.
                            if not os.path.isdir(current_output_subdir): # Check if the subdir was the issue
                                files_skipped +=1
                                logger.warning(f"Skipped processing {file_path} due to output directory creation failure.")


                    else: # parsed_data is None
                        logger.warning(f"Could not parse (or file was empty/returned None): {file_path}")
                        files_skipped += 1
                except InvalidEmailFormatException as e:
                    logger.error(f"Invalid email format for {file_path}: {e}")
                    files_skipped += 1
                except Exception as e:
                    logger.error(f"An unexpected error occurred while processing {file_path}: {e.__class__.__name__} - {e}")
                    files_skipped += 1
            else: # Not an .eml or .msg file
                logger.info(f"Skipping non-email file (by extension): {file_path}")
                files_skipped += 1

    # Final Summary Logging
    logger.info("--- Processing Summary ---")
    logger.info(f"Total files scanned: {total_files_scanned}")
    logger.info(f"Emails processed successfully (parsed and all files saved): {emails_processed_successfully}")
    logger.info(f"Files skipped (non-email, parse error, or output dir creation error): {files_skipped}")
    logger.info(f"Errors during output file writing (for successfully parsed emails): {output_write_errors}")
    logger.info("--------------------------")

if __name__ == "__main__":
    main()
