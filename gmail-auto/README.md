# Email Polling and Code Extraction Bot

This project provides a modular and configurable bot to automatically poll a Gmail inbox, find emails matching specific criteria, and extract information (like verification codes) from the email body using regular expressions or Google's Generative AI.

## Features

- **Modular Design**: Code is separated into logical components (`EmailClient`, `EmailPoller`, `CodeParser`) for maintainability and extensibility.
- **AI-Powered Parsing**: Optionally uses Google's Gemini model to intelligently extract codes, providing resilience against changing email formats. Falls back to regex if AI is disabled or fails.
- **Configuration Driven**: All sensitive data and operational parameters (email filters, regex patterns, AI settings) are managed in a `config.json` file.
- **Gmail API Integration**: Uses the official Google API Client Library for robust and secure access to Gmail.
- **Automated Polling**: Continuously checks for new, unread emails at a configurable interval.
- **Targeted Filtering**: Filters emails by sender and/or subject to process only relevant messages.
- **Action Trigger**: Includes a placeholder `trigger_action` callback function that can be extended to perform actions with the extracted code.

## Project Structure

```.
├── config.json # Main configuration file
├── credentials.json # Your Google API credentials (you must provide this)
├── token.json # Stores the API access token after first authentication
├── main.py # The main entry point for the application
├── email_client.py # Handles all communication with the Gmail API
├── email_poller.py # Orchestrates the polling and processing loop
└── code_parser.py # Responsible for parsing email content and extracting codes
```

## Setup Instructions

### 1. Google Cloud & API Setup

1.  **Gmail API**: Follow the steps below to enable the Gmail API and get your `credentials.json`.

    1.  **Create a Google Cloud Project**: Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
    2.  **Enable the Gmail API**: In your project's dashboard, navigate to "APIs & Services" > "Library". Search for "Gmail API" and click **Enable**.
    3.  **Configure OAuth Consent Screen**: Go to "APIs & Services" > "OAuth consent screen", choose **External**, and fill in the required app and contact details. Add your email address as a **Test user**.
    4.  **Create Credentials**: Go to "Credentials", click **+ CREATE CREDENTIALS** > **OAuth client ID**, select **Desktop app**, and download the JSON file. Rename it to `credentials.json` and place it in your project directory.

2.  **Generative AI API Key (for AI Parsing)**:
    1.  Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
    2.  Click **Create API key** and copy your new key.
    3.  **Important**: For security, do not paste the key into your code. Instead, set it as an environment variable.
        - **Linux/macOS**: `export GOOGLE_API_KEY='YOUR_API_KEY'`
        - **Windows**: `set GOOGLE_API_KEY=YOUR_API_KEY`

### 2. Python Environment Setup

1.  **Install Libraries**: You need the Google client libraries and the new generative AI library. Open your terminal and run:
    ```bash
    pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib google-generativeai
    ```

### 3. Application Configuration

1.  Open `config.json` and edit it:
    - **`ai_parser`**: Set `enabled` to `true` to use AI parsing. You can also customize the `prompt`.
    - **`email_client.scopes`**: `https://www.googleapis.com/auth/gmail.modify` is required to mark emails as read.
    - **`email_poller.filters`**: Set the `sender` and/or `subject` to match the emails you are targeting.
    - **`code_parser.regex`**: Define a fallback regular expression.

## How to Run

1.  Make sure your `config.json` and `credentials.json` files are correctly set up.
2.  Ensure the `GOOGLE_API_KEY` environment variable is set if you are using the AI feature.
3.  Run the main script from your terminal:
    ```bash
    python main.py
    ```
4.  **First-Time Authorization**: The first time you run it, a browser window will open for Google authentication. Approve the permissions to allow the script to access your Gmail. A `token.json` file will be created to save your authorization.
5.  The script will then begin polling your inbox.

## Notes on AI Usage

This project uses Google's Generative AI to intelligently parse email content. Here’s how it works and what to consider.

- **How It Works**: When AI parsing is enabled, the cleaned text from an email body is sent to the Gemini Pro model. The model is guided by a prompt (defined in `config.json`) to identify and extract the specific code.

- **Fallback Mechanism**: The system is designed to be resilient. If the AI is disabled, fails to initialize (e.g., due to a missing API key), or doesn't return a valid-looking code, the `CodeParser` automatically falls back to using the local regex pattern defined in your configuration. This ensures the bot can still function even if the AI component fails.

- **Customizing the Prompt**: You can change the AI's behavior by editing the `prompt` in the `ai_parser` section of `config.json`. A good prompt is specific and clearly states the desired output format.

- **Trade-offs**:
  - **Pros**: The AI is highly flexible and can adapt to variations in email templates where a rigid regex might fail.
  - **Cons**: Using the AI introduces an external API dependency, which adds a small amount of latency to the extraction process.

## Product Demo

The demo videos for the project can be found on: [Google Drive](https://drive.google.com/drive/folders/1Bfgh7MSzqtyTwgj0KNnS1N8tFyEphEYc?usp=drive_link)
