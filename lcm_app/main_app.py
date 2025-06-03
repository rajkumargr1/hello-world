import tkinter as tk
from tkinter import ttk, messagebox
import collections # For Counter
from typing import Optional, Tuple, List, Dict

# Attempt to import calculator functions
try:
    from calculator import calculate_lcm, get_prime_factorization, calculate_lcm_from_factors
except ImportError:
    messagebox.showerror("Import Error", "Could not import calculator module. Ensure it's in the same directory or PYTHONPATH is set.")
    def get_prime_factorization(n: int) -> collections.Counter: return collections.Counter()
    def calculate_lcm(n1: int, n2: int) -> int: return 0
    def calculate_lcm_from_factors(f1: collections.Counter, f2: collections.Counter) -> int: return 0


class LCMLearningToolApp:
    EXAMPLES: List[Tuple[int, int]] = [(12, 18), (4, 6), (15, 25), (7, 5), (1, 8), (99, 88)]

    def __init__(self, root_window):
        self.root = root_window
        self.root.title("LCM Learning Tool")
        self.root.geometry("650x600") # Adjusted for more content

        self.style = ttk.Style()
        self.style.theme_use('clam')

        # StringVars for dynamic content
        self.num1_var = tk.StringVar()
        self.num2_var = tk.StringVar()
        self.factors1_var = tk.StringVar()
        self.factors2_var = tk.StringVar()
        self.lcm_result_var = tk.StringVar()

        self.current_example_index = -1 # Start before the first example

        # --- Main Frame ---
        main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- Input Section ---
        input_frame = ttk.LabelFrame(main_frame, text="Inputs", padding="10")
        input_frame.pack(fill=tk.X, pady=5)
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Number 1:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.num1_entry = ttk.Entry(input_frame, textvariable=self.num1_var, width=25)
        self.num1_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Number 2:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.num2_entry = ttk.Entry(input_frame, textvariable=self.num2_var, width=25)
        self.num2_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # --- Prime Factorization Display ---
        factors_frame = ttk.LabelFrame(main_frame, text="Prime Factorizations", padding="10")
        factors_frame.pack(fill=tk.X, pady=5)

        self.factors1_label = ttk.Label(factors_frame, textvariable=self.factors1_var, wraplength=600, justify=tk.LEFT)
        self.factors1_label.pack(anchor="w", pady=2)
        self.factors2_label = ttk.Label(factors_frame, textvariable=self.factors2_var, wraplength=600, justify=tk.LEFT)
        self.factors2_label.pack(anchor="w", pady=2)

        # --- LCM Explanation/Visualization Area ---
        lcm_steps_frame = ttk.LabelFrame(main_frame, text="LCM Calculation Steps", padding="10")
        lcm_steps_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.lcm_steps_text = tk.Text(lcm_steps_frame, height=10, wrap=tk.WORD, relief=tk.FLAT, borderwidth=1, font=("TkDefaultFont", 9))
        self.lcm_steps_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        steps_scrollbar = ttk.Scrollbar(lcm_steps_frame, orient=tk.VERTICAL, command=self.lcm_steps_text.yview)
        steps_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.lcm_steps_text.config(yscrollcommand=steps_scrollbar.set, state=tk.DISABLED)

        self.lcm_steps_text.tag_configure("bold", font=("TkDefaultFont", 9, "bold"))
        self.lcm_steps_text.tag_configure("italic", font=("TkDefaultFont", 9, "italic"))
        self.lcm_steps_text.tag_configure("heading", font=("TkDefaultFont", 10, "bold", "underline"))
        self.lcm_steps_text.tag_configure("math", font=("Courier New", 10)) # Monospaced for math-like text

        # --- LCM Result Display ---
        result_frame = ttk.LabelFrame(main_frame, text="Result", padding="10")
        result_frame.pack(fill=tk.X, pady=5)

        self.lcm_result_label = ttk.Label(result_frame, textvariable=self.lcm_result_var, font=("TkDefaultFont", 11, "bold"))
        self.lcm_result_label.pack(anchor="w")

        # --- Buttons Section ---
        buttons_frame = ttk.Frame(main_frame, padding="10 0 0 0")
        buttons_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.calculate_button = ttk.Button(buttons_frame, text="Calculate LCM", command=self.handle_calculate_lcm)
        self.calculate_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.next_example_button = ttk.Button(buttons_frame, text="Next Example", command=self.handle_next_example)
        self.next_example_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.clear_button = ttk.Button(buttons_frame, text="Clear", command=self.clear_fields)
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.help_button = ttk.Button(buttons_frame, text="Help/Info", command=self.show_help)
        self.help_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.clear_fields() # Initialize to a clean state
        self.handle_next_example() # Load the first example on startup


    def _update_lcm_steps_text(self, content_tuples: List[Tuple[str, Optional[List[str]]]]):
        self.lcm_steps_text.config(state=tk.NORMAL)
        self.lcm_steps_text.delete("1.0", tk.END)
        for message, tags in content_tuples:
            if tags:
                self.lcm_steps_text.insert(tk.END, message, tuple(tags)) # Ensure tags is a tuple
            else:
                self.lcm_steps_text.insert(tk.END, message)
            self.lcm_steps_text.insert(tk.END, "\n") # Add newline after each message part
        self.lcm_steps_text.config(state=tk.DISABLED)

    def format_factorization(self, factors_counter: collections.Counter) -> str:
        if not factors_counter: # Handles case for number 1 or if factors_counter is empty
            return "1 (is prime or has no prime factors other than itself if > 1, or is 1)"

        sorted_factors = sorted(factors_counter.items())

        return " * ".join([f"{base}^{power}" for base, power in sorted_factors])

    def show_help(self):
        help_text = """
What is a Prime Number?
A prime number is a whole number greater than 1 that has only two divisors: 1 and itself.
Examples: 2, 3, 5, 7, 11, 13...

What is Prime Factorization?
Prime factorization is the process of finding which prime numbers multiply together to make the original number.
Example: The prime factorization of 12 is 2 x 2 x 3 (or 2^2 x 3).

What is LCM (Least Common Multiple)?
The LCM of two or more integers is the smallest positive integer that is divisible by each of the integers.
Example: LCM(12, 18) = 36 because 36 is the smallest number divisible by both 12 and 18.

How is LCM calculated using prime factorization?
1. Find the prime factorization of each number.
2. For each prime factor, find the highest power it appears in any factorization.
3. Multiply these highest powers together to get the LCM.
   Example: 12 = 2^2 * 3^1,  18 = 2^1 * 3^2
   LCM = 2^(max(2,1)) * 3^(max(1,2)) = 2^2 * 3^2 = 4 * 9 = 36.
"""
        messagebox.showinfo("Help/Info - LCM Learning Tool", help_text)

    def handle_calculate_lcm(self):
        steps_content: List[Tuple[str, Optional[List[str]]]] = []
        try:
            num1_str = self.num1_var.get()
            num2_str = self.num2_var.get()

            if not num1_str or not num2_str:
                messagebox.showwarning("Input Error", "Please enter both numbers.")
                return

            num1 = int(num1_str)
            num2 = int(num2_str)

            if num1 < 1 or num2 < 1: # calculator.py also raises ValueError for this
                messagebox.showerror("Input Error", "Numbers must be positive integers greater than 0.")
                self.factors1_var.set("Factors of Number 1: Invalid input.")
                self.factors2_var.set("Factors of Number 2: Invalid input.")
                self._update_lcm_steps_text([("Error: Numbers must be positive integers.", ["italic"])])
                self.lcm_result_var.set("LCM: Error")
                return

            steps_content.append(("Input Numbers:", ["heading"]))
            steps_content.append((f"  Number 1: {num1}", None))
            steps_content.append((f"  Number 2: {num2}", None))
            steps_content.append(("", None)) # Spacer

            factors1 = get_prime_factorization(num1)
            factors2 = get_prime_factorization(num2)

            self.factors1_var.set(f"Factors of {num1}: {self.format_factorization(factors1)}")
            self.factors2_var.set(f"Factors of {num2}: {self.format_factorization(factors2)}")

            steps_content.append(("Prime Factorizations:", ["heading"]))
            steps_content.append((f"  {num1} = {self.format_factorization(factors1)}", ["math"]))
            steps_content.append((f"  {num2} = {self.format_factorization(factors2)}", ["math"]))
            steps_content.append(("", None))

            # Determine all unique prime bases
            all_primes = sorted(list(set(factors1.keys()) | set(factors2.keys())))

            steps_content.append(("Combining Factors for LCM:", ["heading"]))
            if not all_primes and (num1 == 1 and num2 == 1):
                 steps_content.append(("  Both numbers are 1. LCM is 1.", ["italic"]))
            elif not all_primes: # One is 1, other is prime or 1
                if num1 == 1:
                    steps_content.append((f"  {num1} is 1. LCM is the other number: {num2}", ["italic"]))
                else: # num2 == 1
                    steps_content.append((f"  {num2} is 1. LCM is the other number: {num1}", ["italic"]))

            lcm_calculation_str_parts = []
            for prime in all_primes:
                power1 = factors1.get(prime, 0)
                power2 = factors2.get(prime, 0)
                max_power = max(power1, power2)
                steps_content.append((f"  For prime {prime}:", None))
                steps_content.append((f"    In {num1}: {prime}^{power1}", ["math"]))
                steps_content.append((f"    In {num2}: {prime}^{power2}", ["math"]))
                steps_content.append((f"    Highest power is {prime}^{max_power}", ["bold", "math"]))
                lcm_calculation_str_parts.append(f"{prime}^{max_power}")

            if lcm_calculation_str_parts:
                steps_content.append(("", None))
                steps_content.append(("LCM Calculation:", ["heading"]))
                steps_content.append((f"  LCM = {' * '.join(lcm_calculation_str_parts)}", ["math"]))

            # Calculate LCM using the dedicated function from factors
            lcm_val = calculate_lcm_from_factors(factors1, factors2)
            # Or use the direct one: lcm_val = calculate_lcm(num1, num2)

            self.lcm_result_var.set(f"LCM ({num1}, {num2}): {lcm_val}")
            steps_content.append((f"  Final LCM = {lcm_val}", ["bold", "math"]))

            self._update_lcm_steps_text(steps_content)

        except ValueError: # Handles non-integer input or negative numbers from calculator.py
            messagebox.showerror("Input Error", "Invalid input. Please enter valid positive integers.")
            self.factors1_var.set("Factors of Number 1: Invalid input.")
            self.factors2_var.set("Factors of Number 2: Invalid input.")
            self._update_lcm_steps_text([("Error: Please enter valid positive integers.", ["italic"])])
            self.lcm_result_var.set("LCM: Error")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.clear_fields() # Clear fields on unexpected error

    def clear_fields(self):
        self.num1_var.set("")
        self.num2_var.set("")
        self.factors1_var.set("Factors of Number 1: Not calculated yet.")
        self.factors2_var.set("Factors of Number 2: Not calculated yet.")
        self._update_lcm_steps_text([("Inputs cleared. Enter new numbers or load an example.", ["italic"])])
        self.lcm_result_var.set("LCM: -")
        self.num1_entry.focus()

    def handle_next_example(self):
        self.current_example_index = (self.current_example_index + 1) % len(self.EXAMPLES)
        num1_ex, num2_ex = self.EXAMPLES[self.current_example_index]

        self.num1_var.set(str(num1_ex))
        self.num2_var.set(str(num2_ex))
        self.handle_calculate_lcm() # Automatically calculate for the new example


if __name__ == '__main__':
    app_root = tk.Tk()
    app = LCMLearningToolApp(app_root)
    app_root.mainloop()
