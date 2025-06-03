# LCM Learning Tool

A simple desktop application built with Python and Tkinter to help understand and calculate the Least Common Multiple (LCM) using prime factorization for multiple numbers, now with an interactive Practice Mode!

## Features

*   **Calculator Mode:**
    *   Accepts multiple numbers (comma-separated) as input for LCM calculation.
    *   Calculates LCM for the set of provided positive integers.
    *   Displays the prime factorization for each input number.
    *   Provides a step-by-step explanation of how the LCM is derived from the prime factorizations of all numbers.
*   **Interactive Practice Mode:**
    *   Test your LCM skills with predefined questions.
    *   Receive instant visual and auditory feedback:
        *   Fun duck animation with 'quack' sounds for incorrect answers.
        *   Celebration image and sound for correct answers.
*   **General:**
    *   Includes "Next Example" (for calculator) and "Next Question" (for practice) functionality.
    *   Basic help section explaining prime numbers, factorization, and LCM.
    *   Colorful and visually organized interface to improve readability and user experience. The application features a visually enhanced interface with color-coded elements for better understanding of the LCM process.

## Running the Application

You can run the LCM Learning Tool in two main ways:

### Method 1: Running from source (Python required)

This method requires you to have Python 3 installed on your system, along with the `playsound` library.

1.  **Ensure Python 3 is installed.**
    You can download it from [python.org](https://www.python.org/) if you don't have it.
2.  **Install dependencies:**
    Open a terminal or command prompt, navigate to the `lcm_app` directory (or its parent), and run:
    ```bash
    pip install -r requirements.txt
    ```
    (The `requirements.txt` file primarily lists `playsound`.)
3.  **Open a terminal or command prompt.**
4.  **Navigate to the `lcm_app` directory.**
    This is the directory containing `main_app.py`, `calculator.py`, and the `assets` folder.
    ```bash
    cd path/to/your/lcm_app
    ```
5.  **Run the application using the following command:**
    ```bash
    python main_app.py
    ```
    This will launch the LCM Learning Tool GUI.

### Usage

*   **Calculator Mode:**
    Select the "LCM Calculator" tab. In the input field labeled "Enter numbers (comma-separated):", type the numbers you want to find the LCM for, separated by commas (e.g., `12, 18, 20` or `7, 5, 10, 14`). Then click "Calculate LCM".
*   **Practice Mode:**
    Select the "Practice Mode" tab to get started. Questions will be displayed, and you can enter your answer. Click "Submit Answer" to check. Use "Next Question" to try another.

### Method 2: Creating a standalone executable (using PyInstaller)

This method packages the application into a single executable file that can be run on systems without Python installed (though it bundles a Python interpreter and necessary assets).

1.  **Install PyInstaller and dependencies.**
    If you don't have them, open your terminal or command prompt and install them using pip:
    ```bash
    pip install pyinstaller
    pip install -r requirements.txt
    ```
2.  **Open a terminal or command prompt.**
3.  **Navigate to the `lcm_app` directory** (where `main_app.py` is located).
4.  **Run PyInstaller to create the executable:**
    The command needs to include the `assets` directory.
    *   For Linux/macOS:
        ```bash
        pyinstaller --onefile --windowed --name LCM_Calculator --add-data "assets:assets" main_app.py
        ```
    *   For Windows:
        ```bash
        pyinstaller --onefile --windowed --name LCM_Calculator --add-data "assets;assets" main_app.py
        ```
    **Explanation of options:**
    *   `--onefile`: Bundles everything into a single executable file.
    *   `--windowed`: Prevents a command line console window from appearing when the GUI application runs (especially relevant on Windows).
    *   `--name LCM_Calculator`: Sets the name of the output executable file.
    *   `--add-data "assets:assets"` (or `assets;assets` on Windows): This is crucial. It tells PyInstaller to copy the `assets` folder from your source directory into a folder named `assets` inside the packaged application. This makes the images and sounds available to the executable.
5.  **Find the executable.**
    After PyInstaller finishes, you will find the standalone executable in a subdirectory named `dist`. For example, `lcm_app/dist/LCM_Calculator`.

## Assets

The application uses image and sound files located in the `lcm_app/assets/` directory. These include:
*   Duck animation frames (e.g., `duck_frame1.png`, etc.)
*   A celebration icon (`correct_icon.png`)
*   Sound effects (`quack.wav`, `correct.wav`)

These assets are necessary for the Practice Mode feedback to work correctly. Ensure the `assets` folder and its contents are present alongside `main_app.py` when running from source, and are correctly bundled by PyInstaller when creating an executable.

## Dependencies

*   **Python 3:** Required for running from source and for PyInstaller to build the executable.
*   **playsound:** Used for playing sound effects in Practice Mode. Version `1.2.2` is recommended for broad compatibility (especially on Windows), but later versions might work. Listed in `requirements.txt`.
*   **PyInstaller:** Required only if you want to package the application into a standalone executable.

## Project Structure

```
lcm_app/
├── assets/             # Contains images and sound files.
│   ├── .gitkeep
│   ├── duck_frame1.png (example)
│   └── ... (other assets)
├── calculator.py       # Contains the logic for LCM and prime factorization.
├── main_app.py         # The main Tkinter GUI application.
├── README.md           # This file.
├── requirements.txt    # Lists Python package dependencies (e.g., playsound).
├── .gitignore          # Specifies intentionally untracked files that Git should ignore.
└── tests/
    ├── __init__.py
    └── test_calculator.py # Unit tests for calculator.py
```
