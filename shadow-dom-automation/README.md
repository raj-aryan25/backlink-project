# Cross-Site Shadow DOM Automation Framework

## 1. Objective

This framework provides a generalized, modular solution for automating interactions with Shadow DOM elements across diverse websites. It is built using Python and Playwright and is designed to be robust and easily extensible. The core challenge it solves is interacting with elements inside Shadow DOMs without requiring site-specific selectors.

## 2. Design Choices

- **Modularity**: The project uses a Page Object Model (POM) architecture to separate the site interaction logic from the main execution script. This makes the framework cleaner and easier to maintain.

- **Generic Handlers**: Instead of creating a separate page object for each website, a single `SiteHandler` class contains generalized logic to handle common web interactions like closing pop-ups and filling forms. This is achieved by using dynamic, attribute-based selectors (e.g., `input[type="email"]`) rather than brittle, site-specific ones.

- **Shadow DOM Strategy**: The core `shadow_dom_helper` uses a recursive JavaScript function injected into the browser to reliably find elements within open and nested Shadow DOMs. This approach is more robust than relying on Playwright's built-in methods alone, which can sometimes struggle with complex or nested shadow boundaries.

## 3. How to Set Up and Run

- **Prerequisites**:

  - Python 3.8+
  - pip (or another package manager like Poetry)

- **Installation**:

  1.  **Clone the repository.**
  2.  **Install dependencies**:
      ```bash
      pip install playwright
      ```
  3.  **Install browser binaries**:
      ```bash
      playwright install
      ```

- **Execution**:
  - To run the automation script, execute the following command in your terminal:
    ```bash
    python main.py
    ```

## 4. How to Add a New Site

Adding a new website to the automation framework is simple:

1.  Open the `config.py` file.
2.  Add the new URL to the `TARGET_URLS` list.
3.  The existing `SiteHandler` logic will attempt to work on the new site. If the pop-up or input fields use standard HTML practices (e.g., buttons with clear text like "Accept", inputs with `type="email"`), no further changes may be needed.
4.  If the new site requires unique logic, you can add a simple conditional check in `main.py` or extend the `SiteHandler` class while maintaining its generic nature.
