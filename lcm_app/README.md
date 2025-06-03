# LCM Learning Tool

A simple desktop application built with Python and Tkinter to help understand and calculate the Least Common Multiple (LCM) using prime factorization for multiple numbers.

## Features

*   Accepts multiple numbers (comma-separated) as input for LCM calculation.
*   Calculates LCM for the set of provided positive integers.
*   Displays the prime factorization for each input number.
*   Provides a step-by-step explanation of how the LCM is derived from the prime factorizations of all numbers.
*   Includes "Next Example" functionality to quickly load and see solutions for predefined sets of numbers.
*   Basic help section explaining prime numbers, factorization, and LCM.
*   Colorful and visually organized interface to improve readability and user experience. The application features a visually enhanced interface with color-coded elements for better understanding of the LCM process.

## Running the Application

You can run the LCM Learning Tool in two main ways:

### Method 1: Running from source (Python required)

This method requires you to have Python 3 installed on your system.

1.  **Ensure Python 3 is installed.**
    You can download it from [python.org](https://www.python.org/) if you don't have it.
2.  **Open a terminal or command prompt.**
3.  **Navigate to the `lcm_app` directory.**
    This is the directory containing `main_app.py` and `calculator.py`.
    ```bash
    cd path/to/your/lcm_app
    ```
4.  **Run the application using the following command:**
    ```bash
    python main_app.py
    ```
    This will launch the LCM Learning Tool GUI.

5.  **Usage:**
    In the input field labeled "Enter numbers (comma-separated):", type the numbers you want to find the LCM for, separated by commas (e.g., `12, 18, 20` or `7, 5, 10, 14`). Then click "Calculate LCM".

### Method 2: Creating a standalone executable (using PyInstaller)

This method packages the application into a single executable file that can be run on systems without Python installed (though it bundles a Python interpreter).

1.  **Install PyInstaller.**
    If you don't have PyInstaller, open your terminal or command prompt and install it using pip:
    ```bash
    pip install pyinstaller
    ```
2.  **Open a terminal or command prompt.**
3.  **Navigate to the `lcm_app` directory** (where `main_app.py` is located).
4.  **Run PyInstaller to create the executable:**
    ```bash
    pyinstaller --onefile --windowed --name LCM_Calculator main_app.py
    ```
    *   `--onefile`: Bundles everything into a single executable file.
    *   `--windowed`: Prevents a command line console window from appearing when the GUI application runs (especially relevant on Windows).
    *   `--name LCM_Calculator`: Sets the name of the output executable file to `LCM_Calculator.exe` (on Windows) or `LCM_Calculator` (on macOS/Linux).
    *   You might need to add `--add-data "calculator.py:."` or ensure PyInstaller picks up `calculator.py` if it's not automatically found, though for simple same-directory imports it usually works. If you encounter `ModuleNotFoundError` for `calculator` when running the executable, this is an area to investigate.
5.  **Find the executable.**
    After PyInstaller finishes, you will find the standalone executable in a subdirectory named `dist`. For example, `lcm_app/dist/LCM_Calculator`.

## Dependencies

*   **Python 3:** Required for running from source and for PyInstaller to build the executable. The application itself uses only Python's standard library (Tkinter, collections, math).
*   **PyInstaller:** Required only if you want to package the application into a standalone executable.

## Project Structure

```
lcm_app/
├── calculator.py       # Contains the logic for LCM and prime factorization.
├── main_app.py         # The main Tkinter GUI application.
├── README.md           # This file.
├── .gitignore          # Specifies intentionally untracked files that Git should ignore.
└── tests/
    ├── __init__.py
    └── test_calculator.py # Unit tests for calculator.py
```
