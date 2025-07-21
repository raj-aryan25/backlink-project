# Enhanced Test Automation Framework

## 1. Objective

This framework executes specific, multi-step test cases against websites with complex Shadow DOM elements. It has been significantly enhanced with a robust, data-driven architecture and a comprehensive reporting system that includes detailed logs, screenshots, and Playwright traces.

## 2. Framework Design

- **Data-Driven**: Test cases, including target URLs and step-by-step actions, are defined in `test_cases/test_data.py`. This complete separation of test data from execution logic makes the framework highly modular and easy to extend.

- **Robust Locators**: The framework uses specific JavaScript paths via Playwright's `page.evaluate_handle()` to precisely and reliably target elements, especially those nested within complex or multiple Shadow DOMs.

- **Modular Flow Execution**: The `SiteFlowHandler` class is responsible for executing a sequence of test steps (e.g., clicks, form fills) for any given test case defined in the data file.

- **Comprehensive Reporting**: The framework automatically generates detailed reports for each test run, which is crucial for debugging and analysis.

## 3. How to Set Up and Run

- **Prerequisites**:

  - Python 3.8+
  - pip

- **Installation**:

  1.  **Install dependencies**:
      ```bash
      pip install playwright
      ```
  2.  **Install browser binaries**:
      ```bash
      playwright install
      ```

- **Execution**:
  - Run the main script from your terminal:
    ```bash
    python main.py
    ```

## 4. Interpreting the Results

After a test run completes, check the `results/` directory for the following outputs:

- **`logs/test_run.log`**: A complete, timestamped log of every step, success, and failure across all test cases. This provides a detailed narrative of the execution.

- **`screenshots/`**: Screenshots are automatically saved for every successful step and for any test case failure. This provides a clear visual record, making it easy to see what the application looked like at a specific point in time.

- **`traces/`**: This directory contains `*.zip` files that can be opened with the Playwright Trace Viewer. Traces are a powerful debugging tool that provides an interactive, step-by-step replay of the test execution, complete with DOM snapshots, network requests, and console logs. To view a trace, run:
  ```bash
  playwright show-trace results/traces/your_trace_file.zip
  ```
