# Legacy browser demonstration

The unified framework is documented in [the root README](../README.md). This demo has not yet been migrated to the new configuration API. Its password_env field documents a future credential reference; the legacy runner currently fills only login/email identifiers.

# Cross-Site Shadow DOM Automation Framework

## Overview

This project is a generalized automation framework designed to robustly interact with Shadow DOM elements (pop-ups, nested inputs, cookie banners, login forms, etc.) across diverse websites and UI environments. It leverages Playwright for browser automation and Google Gemini AI for dynamic element identification, enabling resilient automation even on sites with complex or changing DOM structures.

---

## Setup Instructions

1. **Clone the Repository**

   ```sh
   git clone https://github.com/raj-aryan25/scaile-backlink.git
   cd shadowdom-auto
   ```

2. **Install Python Dependencies**

   ```sh
   cd ..
   conda run -n autoweb python -m pip install -e ".[ai]"
   conda run -n autoweb python -m playwright install
   cd shadowdom-auto
   ```

3. **Configure API Keys**

   - Create a `.env` file.
   - Add your Google Gemini API key to `.env`:
     ```
     GOOGLE_API_KEY="your-google-api-key"
     ```

4. **Run the Framework**
   ```sh
   conda run -n autoweb python main.py
   ```

---

## Design Choices

- **Playwright**: Chosen for its robust support for modern web features, including Shadow DOM and iframe traversal.
- **Google Gemini AI**: Used to analyze page screenshots and dynamically identify UI elements (e.g., cookie accept buttons, login fields) by their visible text, making the framework resilient to UI changes and localization.
- **Task-Driven Architecture**: Automation steps are defined in `tasks/tasks.json`, allowing easy extension and customization.
- **Modular Structure**:
  - `core/browser_handler.py`: Orchestrates browser actions using AI and Playwright.
  - `core/helper_functions.py`: Contains reusable automation helpers.
  - `ai/gemini_wrapper.py`: Encapsulates Gemini API calls.
  - `utils/prompts.py`: Centralizes AI prompt templates.
  - `utils/task_loader.py`: Loads and parses task definitions.

---

## Adding New Sites

1. **Edit `tasks/tasks.json`**

   - Add a new entry with the target URL and desired actions.
   - Example:
     ```json
     {
       "url": "https://example.com/",
       "actions": [
         { "task": "accept_cookies", "task_description": "Accept Cookies" },
         {
           "task": "click_login_button",
           "task_description": "Click Login Button"
         },
         {
           "task": "fill_login_details",
           "task_description": "Fill Login Details",
           "details": { "login": "user@example.com", "password_env": "DASOERTLICHE_PASSWORD" }
         }
       ]
     }
     ```

2. **Supported Actions**
   - `accept_cookies`
   - `click_login_button`
   - `click_signup_button`
   - `fill_login_details`
   - `fill_signup_details`
   - Extend `core/browser_handler.py` for custom actions if needed.

---

## AI Usage

- **Element Identification**: Gemini analyzes screenshots and returns the exact text label or placeholder for target elements (e.g., cookie accept buttons, login fields).
- **Prompts**: Prompts for Gemini are defined in `utils/prompts.py` and cover multiple languages and UI variations.
- **Robustness**: By relying on visible text and AI interpretation, the framework adapts to UI changes, localization, and Shadow DOM encapsulation.

---

## Evaluation Notes

- **Strengths**
  - Handles Shadow DOM and iframe elements seamlessly.
  - Adapts to UI changes and localization via AI.
  - Easily extensible for new sites and actions.
- **Limitations**
  - Requires a valid Google Gemini API key.
  - AI-based element identification may occasionally misinterpret ambiguous UIs.
  - Some sites may require custom logic for non-standard flows.
- **Extensibility**
  - New actions and prompts can be added modularly.
  - Task definitions are decoupled from code, enabling non-developer contributions.

---

## File Reference

- `main.py`: Entry point.
- `core/automation_engine.py`: Task runner.
- `core/browser_handler.py`: Browser actions.
- `core/helper_functions.py`: Low-level helpers.
- `ai/gemini_wrapper.py`: Gemini API integration.
- `utils/prompts.py`: AI prompt templates.
- `utils/task_loader.py`: Task loader.
- `tasks/tasks.json`: Task definitions.

---

## Product Demo

The demo videos for the project can be found on: [Google Drive](https://drive.google.com/drive/folders/1EAdQxLDGa_BhSemCNbDNi5y7kvW3jAx6?usp=drive_link)
