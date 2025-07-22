# Email Polling and Code Extraction Bot

This project provides a modular and configurable bot to automatically poll a Gmail inbox, find emails matching specific criteria, and extract information (like verification codes) from the email body using regular expressions.

## Features

- **Modular Design**: Code is separated into logical components (`EmailClient`, `EmailPoller`, `CodeParser`) for maintainability and extensibility.
- **Configuration Driven**: All sensitive data and operational parameters (email filters, regex patterns, API settings) are managed in a `config.json` file, not hardcoded.
- **Gmail API Integration**: Uses the official Google API Client Library for robust and secure access to Gmail.
- **Automated Polling**: Continuously checks for new, unread emails at a configurable interval.
- **Targeted Filtering**: Filters emails by sender and/or subject to process only relevant messages.
- **Regex-Based Extraction**: Uses regular expressions to parse the email body and extract specific codes or links.
- **Action Trigger**: Includes a placeholder `trigger_action` callback function that can be extended to perform actions with the extracted code, such as automating website interactions.

## Project Structure

```
.
├── config.json # Main configuration file
├── credentials.json # Your Google API credentials (you must provide this)
├── token.json # Stores the API access token after first authentication
├── main.py # The main entry point for the application
├── email_client.py # Handles all communication with the Gmail API
├── email_poller.py # Orchestrates the polling and processing loop
└── code_parser.py # Responsible for parsing email content and extracting codes
```

## Setup Instructions

### 1. Google Cloud & Gmail API Setup

Before you can run the script, you need to authorize it to access your Gmail account.

1.  **Create a Google Cloud Project**: Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2.  **Enable the Gmail API**: In your project's dashboard, navigate to "APIs & Services" > "Library". Search for "Gmail API" and click **Enable**.
3.  **Configure OAuth Consent Screen**:
    - Go to "APIs & Services" > "OAuth consent screen".
    - Choose **External** for the User Type and click **Create**.
    - Fill in the required fields (App name, User support email, Developer contact information). You can use your own email for these.
    - On the "Scopes" page, you can click "Save and Continue" for now. The script will request the necessary scopes.
    - On the "Test users" page, click **+ Add Users** and add the Gmail address of the account you want the bot to read.
4.  **Create Credentials**:
    - Go to "APIs & Services" > "Credentials".
    - Click **+ CREATE CREDENTIALS** and select **OAuth client ID**.
    - For the "Application type", select **Desktop app**.
    - Give it a name and click **Create**.
    - A window will pop up with your Client ID and Client Secret. Click **DOWNLOAD JSON**.
    - Rename the downloaded file to `credentials.json` and place it in the same directory as the Python scripts.

### 2. Python Environment Setup

1.  **Install Libraries**: You need the Google API client library. Open your terminal and run:
    ```bash
    pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
    ```

### 3. Application Configuration

1.  Open the `config.json` file and edit it to match your needs:
    - `email_client.scopes`: For this project, `https://www.googleapis.com/auth/gmail.modify` is required to mark emails as read.
    - `email_poller.filters`: Set the `sender` and/or `subject` to match the emails you are targeting.
    - `code_parser.regex`: Define the regular expression to extract the code. The `()` creates a capturing group for the part you want to extract.

## How to Run

1.  Make sure your `config.json` and `credentials.json` files are correctly set up in the project directory.
2.  Run the main script from your terminal:
    ```bash
    python main.py
    ```
3.  **First-Time Authorization**: The first time you run the script, a browser window will open, asking you to log in to your Google account and grant the application the permissions it requested. After you approve, a `token.json` file will be created. This file stores your authorization so you won't have to log in every time.
4.  The script will then begin polling your inbox according to the settings in your `config.json`.

## Notes on AI Usage (Optional Bonus)

While this project uses a robust regex-based approach, it could be extended with an AI model for more flexible parsing, especially if the email format varies significantly.

- **How it would work**: Instead of using a regex, the cleaned email body could be sent as a prompt to a Large Language Model (LLM) like Gemini.
- **Example Prompt**: `"From the following email text, extract the 6-digit verification code. Return only the code. Text: [email body text here]"`
- **Implementation**: You would replace the `re.search` logic in `CodeParser.extract_code` with an API call to the AI model.
- **Trade-offs**:
  - **Pros**: More resilient to changes in email templates.
  - **Cons**: Introduces external API dependency, potential costs, and higher latency compared to a local regex operation.
