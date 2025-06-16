# Email Parser Tool

## Description

This script recursively traverses a specified input directory, identifies email files (primarily `.eml` and `.msg`), parses them to extract metadata (Subject, From, To, Date), body content, and attachments. It then creates a structured output in a specified output directory, mirroring the input directory's hierarchy. For each processed email, it saves the original email, its subject, body, a combined subject-body file, and any attachments.

## Features

*   Recursive traversal of input directory and subdirectories.
*   Parsing of email files (tested with `.eml` and `.msg` like formats).
*   Extraction of email metadata: Subject, From, To, Date.
*   Extraction of email body (prioritizes plain text, falls back to HTML).
*   Extraction and saving of email attachments with sanitized filenames.
*   Creation of a structured output directory:
    *   Mirrors the input directory structure.
    *   Creates a unique subfolder for each processed email (e.g., `original_email_name_extracted/`).
    *   Saves the following into the unique subfolder:
        *   Original email file.
        *   `subject.txt` (email subject).
        *   `body.txt` (email body).
        *   `subject_body.txt` (combined subject and body).
        *   All attachments with their original (sanitized) names.
*   Logging of operations and errors.
*   Summary report of processed files, skips, and errors.

## Requirements

This project uses only Python standard libraries. No external packages need to be installed.

## Usage

To run the script, navigate to the parent directory of `email_parser_tool` and execute it as a module:

```bash
python -m email_parser_tool.email_processor <input_directory> <output_directory>
```

**Command-Line Arguments:**

*   `input_directory`: (Required) The path to the directory containing email files to process.
*   `output_directory`: (Required) The path to the directory where the processed output will be saved. This directory will be created if it doesn't exist.

**Example:**

```bash
python -m email_parser_tool.email_processor ./my_emails ./processed_emails
```

## Input Directory Structure

The script will scan the `input_directory` and all its subdirectories for email files.

## Output Directory Structure

The script will create an output structure in the `output_directory` that mirrors the folder hierarchy of the `input_directory`. For each email file found (e.g., `input_directory/folder_A/email1.eml`), a corresponding folder will be created in the output (e.g., `output_directory/folder_A/email1_extracted/`).

Inside each `_extracted` folder, you will find:
*   The original email file (e.g., `email1.eml`).
*   `subject.txt`: Contains the subject of the email.
*   `body.txt`: Contains the plain text or HTML body of the email.
*   `subject_body.txt`: Contains the subject followed by the body.
*   Any attachments from the email, saved with their original (sanitized) filenames.

## Error Handling

The script includes error handling for issues such as:
*   Inaccessible input or output directories.
*   Files that cannot be parsed as emails.
*   Errors during file read/write operations.
Detailed logs are printed to the console, including a summary at the end of processing.

## Supported Email File Types

The script uses Python's built-in `email` module for parsing. It is primarily intended for `.eml` files and similar formats that the `email` module can handle. `.msg` files might be parsed if they are in a compatible MIME format; however, proprietary binary `.msg` formats (like Outlook's default) might not be fully parsable by this standard library.
