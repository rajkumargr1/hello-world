# Email-Based Equipment Movement Processor

## Description

This project aims to process incoming emails to extract information related to equipment movement and logistics. It identifies relevant emails, determines the action required (e.g., add, update, delete equipment), and extracts key data from the email subject, body (plain text or tables), and attachments (Excel, PDF). The extracted information is then standardized and saved to a CSV file. The system uses a Large Language Model (LLM) like Gemini for tasks such as relevance classification, action identification, and data extraction.

## Features (Current & Planned)

*   **Email Fetching:** Connects to an IMAP email server and fetches emails.
*   **Email Parsing:** Extracts subject, body, sender, date, and attachments.
*   **Relevance Classification:** Uses an LLM to determine if an email is relevant to equipment movement.
*   **Action Identification:** Uses an LLM to identify the primary action (ADD, UPDATE, DELETE, INFO) from relevant emails.
*   **Attachment Handling:** Saves attachments for processing.
    *   Identifies standard Excel templates from configured senders for automated processing (planned folder: `data/automation`).
*   **Content Extraction Agents (Partially Implemented/Planned):**
    *   Plain text from email subject and body.
    *   Data from Excel attachments.
    *   Data from PDF attachments (text and tables).
    *   (Image processing is currently out of scope).
*   **Configurable LLM Interaction:** Generic LLM handler module, initially supporting Gemini.
*   **Standardized Output:** Saves extracted data to a CSV file (`data/equipment_moves.csv`).
*   **Configuration:** Key settings managed via `config/config.yaml` and environment variables.
*   **Modular Design:** Separated components for email processing, LLM interaction, classification, and output handling.

## Project Structure

```
.
├── config/
│   └── config.yaml         # Main configuration file
├── data/
│   ├── automation/         # For standard Excel templates
│   └── temp_attachments/   # Temporary storage for email attachments
│   └── equipment_moves.csv # Default output CSV file
├── src/
│   ├── __init__.py
│   ├── classification.py   # Relevance and action classification logic
│   ├── email_processor.py  # Fetches and parses emails
│   ├── llm_handler.py      # Handles interaction with the LLM
│   └── output_handler.py   # Manages CSV output
├── tests/
│   ├── __init__.py
│   └── test_config_loading.py # Example test file
├── .env.example            # Example environment variable file (rename to .env)
├── .gitignore
├── main.py                 # Main orchestrator script
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

## Setup and Installation

### Prerequisites

*   Python 3.8 or higher.
*   Access to an IMAP-enabled email account.
*   API key for an LLM provider (e.g., Google Gemini).

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python -m venv venv
    # On Windows
    # venv\Scripts\activate
    # On macOS/Linux
    # source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Configuration File (`config/config.yaml`):**
    *   Copy or review `config/config.yaml`.
    *   Update the `email_server` section with your IMAP host, port, and user email address.
    *   Configure the `llm` section:
        *   `api_key_env_var`: Set the name of the environment variable that will hold your LLM API key (e.g., `GEMINI_API_KEY`).
        *   `model`: Specify the LLM model you intend to use (e.g., `gemini-pro`).
    *   Adjust `processing` settings like `output_csv_file`, `temp_attachment_dir`, and `standard_template_senders` as needed.
    *   Modify `logging` settings if you require a different log level or format.

2.  **Environment Variables:**
    *   Create a `.env` file in the project root (you can copy `.env.example` if provided, or create it manually).
    *   Add the following environment variables to your `.env` file (or set them directly in your system environment):
        ```ini
        # Email account password (or app-specific password)
        EMAIL_PASSWORD="your_email_password"

        # LLM API Key (use the name you set in config.yaml's api_key_env_var)
        GEMINI_API_KEY="your_llm_api_key"
        ```
    *   **Important:** Ensure the variable name for the LLM API key in your `.env` file (e.g., `GEMINI_API_KEY`) matches the value of `llm.api_key_env_var` in `config/config.yaml`.
    *   The `main.py` script will attempt to load `.env` if `python-dotenv` is installed.

## How to Run

### Running the Main Application

To start processing emails:

```bash
python main.py
```

The application will:
1.  Connect to the email server specified in `config.yaml`.
2.  Fetch emails based on the criteria (e.g., "UNSEEN").
3.  Process each email for relevance and action.
4.  Write extracted data to the CSV file specified in `config.yaml` (default: `data/equipment_moves.csv`).
5.  Log activities to the console (and potentially a file, if configured).

### Running Tests

To run the unit tests:

```bash
python -m unittest discover tests
```
Or, to run a specific test file:
```bash
python tests/test_config_loading.py
```

## Future Work / To-Do

*   Implement detailed content extraction agents for:
    *   Plain text from email body (extracting specific fields like Move Code, Date, Equipment ID, etc.).
    *   Tables in email bodies.
    *   Excel attachments (handling standard templates and generic tables).
    *   PDF attachments (extracting text and tables).
*   Refine LLM prompts for better accuracy and more detailed extraction.
*   Implement robust error handling and retries for email fetching and LLM calls.
*   Add more comprehensive unit and integration tests.
*   Develop logic for handling email chains more effectively (identifying the most relevant email in a thread).
*   Securely manage credentials (e.g., using a proper secrets manager instead of just environment variables for production).
*   Add options for different email fetching criteria (e.g., specific folders, date ranges).
```
