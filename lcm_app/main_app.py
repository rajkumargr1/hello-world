import tkinter as tk
from tkinter import ttk, messagebox
import collections # For Counter
from typing import Optional, Tuple, List, Dict, cast

# Attempt to import calculator functions
try:
    from calculator import calculate_lcm, get_prime_factorization # calculate_lcm_from_factors no longer used by GUI
except ImportError:
    messagebox.showerror("Import Error", "Could not import calculator module. Ensure it's in the same directory or PYTHONPATH is set.")
    def get_prime_factorization(n: int) -> collections.Counter: return collections.Counter()
    def calculate_lcm(*numbers: int) -> int: return 0

# --- Color Palette ---
COLOR_BG_ROOT = "#F0F8FF"  # AliceBlue
COLOR_BG_FRAME = "#E6F3FF" # Lighter AliceBlue/PaleCornflowerBlue
COLOR_TEXT_GENERAL = "#333333" # Dark Gray
COLOR_TEXT_RESULT = "#006400"  # DarkGreen
COLOR_ACCENT_BUTTON = "#007ACC" # Medium Blue (for button style if effective)
COLOR_TEXT_HEADING = "#003366" # Dark Blue
COLOR_TEXT_PRIME = "#CC0000"   # Red for primes
COLOR_TEXT_POWER = "#008000"   # Green for powers
COLOR_TEXT_NUMBER_HIGHLIGHT = "#0000CD" # MediumBlue for highlighting numbers

class LCMLearningToolApp:
    EXAMPLES: List[Tuple[int, ...]] = [
        (12, 18),
        (4, 6, 8),
        (15, 25, 30),
        (7, 5),
        (1, 8),
        (99, 88),
        (2, 3, 4, 5),
        (7, 14, 21, 28)
    ]

    def __init__(self, root_window):
        self.root = root_window
        self.root.title("LCM Learning Tool (N-Numbers)")
        self.root.geometry("750x750")
        self.root.configure(bg=COLOR_BG_ROOT)

        self.style = ttk.Style()
        self.style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'

        # Configure ttk styles
        self.style.configure("TLabel", background=COLOR_BG_FRAME, foreground=COLOR_TEXT_GENERAL, padding=3)
        self.style.configure("TEntry", fieldbackground="white", foreground=COLOR_TEXT_GENERAL)
        self.style.configure("TButton", foreground=COLOR_TEXT_GENERAL, padding=5)
        self.style.configure("Accent.TButton", foreground="white", background=COLOR_ACCENT_BUTTON, font=('TkDefaultFont', 9, 'bold'))
        self.style.map("Accent.TButton", background=[('active', '#005999')]) # Darker blue on hover

        self.style.configure("TLabelframe", background=COLOR_BG_FRAME, foreground=COLOR_TEXT_HEADING, relief=tk.GROOVE, borderwidth=2)
        self.style.configure("TLabelframe.Label", background=COLOR_BG_FRAME, foreground=COLOR_TEXT_HEADING, font=('TkDefaultFont', 10, 'bold'))


        # StringVars for dynamic content
        self.numbers_input_var = tk.StringVar()
        self.lcm_result_var = tk.StringVar()

        self.current_example_index = -1

        # --- Main Frame ---
        main_frame = ttk.Frame(self.root, padding="10 10 10 10", style="TFrame") # style TFrame might not exist, use general Frame
        main_frame.configure(style="Main.TFrame") # Use a custom style for main_frame if needed
        self.style.configure("Main.TFrame", background=COLOR_BG_ROOT)
        main_frame.pack(expand=True, fill=tk.BOTH)


        # --- Input Section ---
        input_frame = ttk.LabelFrame(main_frame, text="Inputs", padding="10")
        input_frame.pack(fill=tk.X, pady=10, padx=5)
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Enter numbers (comma-separated):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.numbers_entry = ttk.Entry(input_frame, textvariable=self.numbers_input_var, width=45, font=('TkDefaultFont', 10))
        self.numbers_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # --- Prime Factorization Display ---
        factors_display_frame = ttk.LabelFrame(main_frame, text="Prime Factorizations", padding="10")
        factors_display_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)

        self.factors_text = tk.Text(factors_display_frame, height=6, wrap=tk.WORD,
                                    relief=tk.SUNKEN, borderwidth=1, font=("Arial", 10),
                                    bg="#FFFFFF", fg=COLOR_TEXT_GENERAL, padx=5, pady=5)
        self.factors_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        factors_scrollbar = ttk.Scrollbar(factors_display_frame, orient=tk.VERTICAL, command=self.factors_text.yview)
        factors_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.factors_text.config(yscrollcommand=factors_scrollbar.set, state=tk.DISABLED)
        self.factors_text.tag_configure("bold_num", font=("Arial", 10, "bold"), foreground=COLOR_TEXT_NUMBER_HIGHLIGHT)
        self.factors_text.tag_configure("prime", font=("Courier New", 10, "bold"), foreground=COLOR_TEXT_PRIME)
        self.factors_text.tag_configure("power", font=("Courier New", 10, "bold"), foreground=COLOR_TEXT_POWER)
        self.factors_text.tag_configure("separator", foreground="#888888") # Gray for '*' and '^'

        # --- LCM Explanation/Visualization Area ---
        lcm_steps_frame = ttk.LabelFrame(main_frame, text="LCM Calculation Steps", padding="10")
        lcm_steps_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)

        self.lcm_steps_text = tk.Text(lcm_steps_frame, height=12, wrap=tk.WORD,
                                      relief=tk.SUNKEN, borderwidth=1, font=("Arial", 10),
                                      bg="#FFFFFF", fg=COLOR_TEXT_GENERAL, padx=5, pady=5)
        self.lcm_steps_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        steps_scrollbar = ttk.Scrollbar(lcm_steps_frame, orient=tk.VERTICAL, command=self.lcm_steps_text.yview)
        steps_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.lcm_steps_text.config(yscrollcommand=steps_scrollbar.set, state=tk.DISABLED)
        self.lcm_steps_text.tag_configure("bold", font=("Arial", 10, "bold"))
        self.lcm_steps_text.tag_configure("italic", font=("Arial", 10, "italic"))
        self.lcm_steps_text.tag_configure("heading", font=("Arial", 11, "bold", "underline"), foreground=COLOR_TEXT_HEADING)
        self.lcm_steps_text.tag_configure("math", font=("Courier New", 10))
        self.lcm_steps_text.tag_configure("prime_step", foreground=COLOR_TEXT_PRIME, font=("Courier New", 10, "bold"))
        self.lcm_steps_text.tag_configure("power_step", foreground=COLOR_TEXT_POWER, font=("Courier New", 10, "bold"))
        self.lcm_steps_text.tag_configure("final_lcm", font=("Arial", 11, "bold"), foreground=COLOR_TEXT_RESULT)
        self.lcm_steps_text.tag_configure("number_highlight_step", font=("Arial", 10, "bold"), foreground=COLOR_TEXT_NUMBER_HIGHLIGHT)


        # --- LCM Result Display ---
        result_frame = ttk.LabelFrame(main_frame, text="Result", padding="10")
        result_frame.pack(fill=tk.X, pady=10, padx=5)

        self.lcm_result_label_prefix = ttk.Label(result_frame, text="LCM: ", font=("Arial", 12, "bold"), foreground=COLOR_TEXT_HEADING)
        self.lcm_result_label_prefix.pack(side=tk.LEFT)
        self.lcm_result_value_label = ttk.Label(result_frame, textvariable=self.lcm_result_var, font=("Arial", 12, "bold"), foreground=COLOR_TEXT_RESULT)
        self.lcm_result_value_label.pack(side=tk.LEFT)


        # --- Buttons Section ---
        buttons_frame = ttk.Frame(main_frame, padding="10 5 0 5", style="Main.TFrame") # Use custom style for bg match
        buttons_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.calculate_button = ttk.Button(buttons_frame, text="Calculate LCM", command=self.handle_calculate_lcm, style="Accent.TButton")
        self.calculate_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.next_example_button = ttk.Button(buttons_frame, text="Next Example", command=self.handle_next_example)
        self.next_example_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.clear_button = ttk.Button(buttons_frame, text="Clear", command=self.clear_fields)
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.help_button = ttk.Button(buttons_frame, text="Help/Info", command=self.show_help)
        self.help_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.clear_fields()
        self.handle_next_example()


    def _update_text_widget_formatted(self, text_widget: tk.Text, content_list: List[List[Tuple[str, List[str]]]]):
        """ Inserts list of (text, tags_list) tuples, one list per line """
        text_widget.config(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)
        for line_content in content_list:
            for text_segment, tags in line_content:
                text_widget.insert(tk.END, text_segment, tuple(tags) if tags else None)
            text_widget.insert(tk.END, "\n")
        text_widget.config(state=tk.DISABLED)

    def _update_text_widget_simple(self, text_widget: tk.Text, content: List[Tuple[str, Optional[List[str]]]]):
        """ Original simple update for basic messages or lines """
        text_widget.config(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)
        for message, tags in content:
            if tags:
                text_widget.insert(tk.END, message, tuple(tags))
            else:
                text_widget.insert(tk.END, message)
            text_widget.insert(tk.END, "\n")
        text_widget.config(state=tk.DISABLED)


    def format_factorization_for_display(self, num:int, factors_counter: collections.Counter) -> List[Tuple[str, List[str]]]:
        line_content: List[Tuple[str, List[str]]] = []
        line_content.append((f"Factors of ", []))
        line_content.append((f"{num}", ["bold_num"]))
        line_content.append((f": ", []))

        if not factors_counter:
            line_content.append(("1", ["prime"])) # Number 1
            return line_content

        sorted_factors = sorted(factors_counter.items())
        for i, (base, power) in enumerate(sorted_factors):
            if i > 0:
                line_content.append((" * ", ["separator"]))
            line_content.append((f"{base}", ["prime"]))
            if power > 1:
                line_content.append((f"^", ["separator"]))
                line_content.append((f"{power}", ["power"]))
        return line_content


    def show_help(self):
        help_text = """
What is a Prime Number?
A prime number is a whole number greater than 1 that has only two divisors: 1 and itself. Examples: 2, 3, 5, 7, 11...

What is Prime Factorization?
Prime factorization is the process of finding which prime numbers multiply together to make the original number. Example: 12 = 2^2 * 3.

What is LCM (Least Common Multiple)?
The LCM of two or more integers is the smallest positive integer that is divisible by each of the integers. Example: LCM(12, 18) = 36.

How is LCM calculated using prime factorization?
1. Find the prime factorization of each number.
2. For each prime factor, find the highest power it appears in any factorization.
3. Multiply these highest powers together: LCM = P1^max_power1 * P2^max_power2 * ...
"""
        messagebox.showinfo("Help/Info - LCM Learning Tool", help_text, parent=self.root)


    def handle_calculate_lcm(self):
        input_str = self.numbers_input_var.get()
        if not input_str.strip():
            messagebox.showerror("Input Error", "Please enter at least one number.", parent=self.root)
            return

        num_str_parts = input_str.split(',')
        numbers_list: List[int] = []
        parsed_input_parts: List[str] = []

        for part in num_str_parts:
            stripped_part = part.strip()
            if not stripped_part: continue
            try:
                num = int(stripped_part)
                numbers_list.append(num)
                parsed_input_parts.append(stripped_part)
            except ValueError:
                messagebox.showerror("Input Error", f"Invalid input: '{stripped_part}' is not an integer.", parent=self.root)
                self.clear_fields_output()
                return

        if not numbers_list:
            messagebox.showerror("Input Error", "No valid numbers parsed.", parent=self.root)
            self.clear_fields_output()
            return

        try:
            factorization_display_content_list: List[List[Tuple[str, List[str]]]] = []
            all_factors_counters: List[collections.Counter] = []

            for num_val in numbers_list:
                if num_val < 1:
                    messagebox.showerror("Input Error", f"Number '{num_val}' must be positive.", parent=self.root)
                    self.clear_fields_output()
                    return
                factors = get_prime_factorization(num_val)
                all_factors_counters.append(factors)
                factorization_display_content_list.append(self.format_factorization_for_display(num_val, factors))
            self._update_text_widget_formatted(self.factors_text, factorization_display_content_list)

            lcm_steps_content: List[List[Tuple[str, List[str]]]] = []
            lcm_steps_content.append([(("Input Numbers:", ["heading"]),)])
            lcm_steps_content.append([((f"  {', '.join(parsed_input_parts)}", []),)])
            lcm_steps_content.append([]) # Spacer line

            lcm_steps_content.append([(("Prime Factorizations:", ["heading"]),)])
            for i, num_val in enumerate(numbers_list):
                # Re-use formatted parts from factors_text for consistency
                line = [(f"  ", [])] + self.format_factorization_for_display(num_val, all_factors_counters[i])[2:] # Skip "Factors of num: " part
                lcm_steps_content.append(line)

            lcm_steps_content.append([])

            overall_max_factors = collections.Counter()
            for factors_counter in all_factors_counters:
                for prime, power in factors_counter.items():
                    overall_max_factors[prime] = max(overall_max_factors[prime], power)

            lcm_steps_content.append([(("Combining Factors for LCM:", ["heading"]),)])
            if not overall_max_factors:
                 lcm_steps_content.append([(("  All numbers are 1. LCM is 1.", ["italic"]),)])

            lcm_calc_formula_parts: List[Tuple[str, List[str]]] = []
            sorted_overall_primes = sorted(overall_max_factors.keys())

            for prime_val in sorted_overall_primes:
                max_power_val = overall_max_factors[prime_val]
                lcm_steps_content.append([((f"  For prime ", []), (f"{prime_val}", ["prime_step"]), (f":", []),)])
                lcm_steps_content.append([((f"    Highest power is ", []),
                                         (f"{prime_val}", ["prime_step"]), (f"^", []), (f"{max_power_val}", ["power_step"]),)])
                if lcm_calc_formula_parts:
                    lcm_calc_formula_parts.append((" * ", ["math"]))
                lcm_calc_formula_parts.append((f"{prime_val}", ["prime_step"]))
                if max_power_val > 1:
                    lcm_calc_formula_parts.append((f"^", ["math"]))
                    lcm_calc_formula_parts.append((f"{max_power_val}", ["power_step"]))

            if lcm_calc_formula_parts:
                lcm_steps_content.append([])
                lcm_steps_content.append([(("LCM Calculation Formula:", ["heading"]),)])
                line = [(("  LCM = ", ["math"]),)] + lcm_calc_formula_parts
                lcm_steps_content.append(line) # type: ignore

            lcm_val_calculated = calculate_lcm(*numbers_list)

            self.lcm_result_var.set(f"{lcm_val_calculated}") # Only the value
            lcm_steps_content.append([])
            lcm_steps_content.append([(("Final LCM Value:", ["heading"]),)])
            lcm_steps_content.append([(("  LCM = ", []), (f"{lcm_val_calculated}", ["final_lcm"]),)])
            self._update_text_widget_formatted(self.lcm_steps_text, lcm_steps_content)

        except ValueError as e:
            messagebox.showerror("Calculation Error", str(e), parent=self.root)
            self.clear_fields_output()
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self.root)
            self.clear_fields_output()

    def clear_fields_output(self):
        self._update_text_widget_simple(self.factors_text, [("Factorizations will appear here.", ["italic"])])
        self._update_text_widget_simple(self.lcm_steps_text, [("Calculation steps will appear here.", ["italic"])])
        self.lcm_result_var.set("-")

    def clear_fields(self):
        self.numbers_input_var.set("")
        self.clear_fields_output()
        self.numbers_entry.focus()

    def handle_next_example(self):
        self.current_example_index = (self.current_example_index + 1) % len(self.EXAMPLES)
        current_example_nums = self.EXAMPLES[self.current_example_index]
        self.numbers_input_var.set(", ".join(map(str, current_example_nums)))
        self.handle_calculate_lcm()

if __name__ == '__main__':
    app_root = tk.Tk()
    app = LCMLearningToolApp(app_root)
    app_root.mainloop()
