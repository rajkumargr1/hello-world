import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import collections # For Counter
from typing import Optional, Tuple, List, Dict, cast
import random # For potential future random question generation
import os

# Attempt to import sound library
try:
    from playsound import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    PLAYSOUND_AVAILABLE = False
    # print("playsound library not found. Sound effects will be disabled. Install with: pip install playsound")

# Attempt to import calculator functions
try:
    from calculator import calculate_lcm, get_prime_factorization
except ImportError:
    messagebox.showerror("Import Error", "Could not import calculator module. Ensure it's in the same directory or PYTHONPATH is set.")
    def get_prime_factorization(n: int) -> collections.Counter: return collections.Counter()
    def calculate_lcm(*numbers: int) -> int: return 0

# --- Color Palette ---
COLOR_BG_ROOT = "#F0F8FF"
COLOR_BG_FRAME = "#E6F3FF"
COLOR_TEXT_GENERAL = "#333333"
COLOR_TEXT_RESULT = "#006400"
COLOR_ACCENT_BUTTON = "#007ACC"
COLOR_TEXT_HEADING = "#003366"
COLOR_TEXT_PRIME = "#CC0000"
COLOR_TEXT_POWER = "#008000"
COLOR_TEXT_NUMBER_HIGHLIGHT = "#0000CD"
COLOR_FEEDBACK_CORRECT = "#28A745"
COLOR_FEEDBACK_INCORRECT = "#DC3545"
COLOR_PRACTICE_QUESTION = "#4B0082"

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
DUCK_ANIMATION_FRAMES = 4 # Number of duck frames (duck_frame1.png to duck_frame4.png)
DUCK_FRAME_DELAY_MS = 300 # Delay between duck animation frames
FEEDBACK_CLEAR_DELAY_MS = 2000 # Delay to clear feedback canvas

class LCMLearningToolApp:
    EXAMPLES: List[Tuple[int, ...]] = [(12, 18), (4, 6, 8), (15, 25, 30), (7, 5), (1, 8), (99, 88), (2, 3, 4, 5), (7, 14, 21, 28)]
    PRACTICE_QUESTIONS: List[Tuple[Tuple[int, ...], int]] = [((4, 6), 12), ((15, 25), 75), ((8, 12), 24), ((7, 5), 35), ((10, 15, 20), 60), ((3, 5, 7), 105), ((2, 4, 8), 8), ((9, 6), 18)]

    def __init__(self, root_window):
        self.root = root_window
        self.root.title("LCM Learning Tool")
        self.root.geometry("800x800")
        self.root.configure(bg=COLOR_BG_ROOT)

        self._load_assets()

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._configure_styles()

        self.in_practice_mode = False
        self.current_practice_question_numbers: Optional[Tuple[int, ...]] = None
        self.current_practice_correct_lcm: Optional[int] = None
        self.current_question_index = -1
        self.calculator_mode_active = True
        self.duck_animation_job_id: Optional[str] = None # To cancel ongoing animation

        self.numbers_input_var = tk.StringVar()
        self.lcm_result_var = tk.StringVar()
        self.practice_question_var = tk.StringVar()
        self.practice_answer_var = tk.StringVar()
        self.practice_feedback_var = tk.StringVar()

        self.notebook = ttk.Notebook(self.root)
        self.calculator_tab = ttk.Frame(self.notebook, style="Main.TFrame")
        self.practice_tab = ttk.Frame(self.notebook, style="Main.TFrame")
        self.notebook.add(self.calculator_tab, text='LCM Calculator')
        self.notebook.add(self.practice_tab, text='Practice Mode')
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        self._create_calculator_ui(self.calculator_tab)
        self._create_practice_ui(self.practice_tab)

        self.clear_fields()
        self.handle_next_example()
        self._update_ui_for_mode()

        if not PLAYSOUND_AVAILABLE:
            print("INFO: playsound library not found. Sound effects will be disabled. Install with: pip install playsound")


    def _load_assets(self):
        self.duck_frames: List[PhotoImage] = []
        # Ensure there's at least one placeholder if all frames fail to load
        default_placeholder = PhotoImage(width=100, height=100) # Create once

        for i in range(1, DUCK_ANIMATION_FRAMES + 1):
            try:
                image_path = os.path.join(ASSETS_DIR, f"duck_frame{i}.png")
                if os.path.exists(image_path):
                    self.duck_frames.append(PhotoImage(file=image_path))
                else:
                    # print(f"Warning: Duck image not found {image_path}. Using placeholder.")
                    self.duck_frames.append(default_placeholder)
            except tk.TclError as e:
                # print(f"Error loading {image_path}: {e}. Using placeholder.")
                self.duck_frames.append(default_placeholder)

        if not self.duck_frames : # If loop didn't run or all failed
             self.duck_frames.append(default_placeholder)


        try:
            correct_image_path = os.path.join(ASSETS_DIR, "correct_icon.png")
            if os.path.exists(correct_image_path):
                self.correct_image = PhotoImage(file=correct_image_path)
            else:
                # print(f"Warning: Correct icon not found {correct_image_path}. Using placeholder.")
                self.correct_image = default_placeholder
        except tk.TclError as e:
            # print(f"Error loading correct_icon.png: {e}. Using placeholder.")
            self.correct_image = default_placeholder

        self.quack_sound_path = os.path.join(ASSETS_DIR, "quack.wav")
        self.correct_sound_path = os.path.join(ASSETS_DIR, "correct.wav")


    def _configure_styles(self): # ... (same as before)
        self.style.configure("TLabel", background=COLOR_BG_FRAME, foreground=COLOR_TEXT_GENERAL, padding=3)
        self.style.configure("TEntry", fieldbackground="white", foreground=COLOR_TEXT_GENERAL)
        self.style.configure("TButton", foreground=COLOR_TEXT_GENERAL, padding=5)
        self.style.configure("Accent.TButton", foreground="white", background=COLOR_ACCENT_BUTTON, font=('TkDefaultFont', 9, 'bold'))
        self.style.map("Accent.TButton", background=[('active', '#005999')])
        self.style.configure("TLabelframe", background=COLOR_BG_FRAME, foreground=COLOR_TEXT_HEADING, relief=tk.GROOVE, borderwidth=2)
        self.style.configure("TLabelframe.Label", background=COLOR_BG_FRAME, foreground=COLOR_TEXT_HEADING, font=('TkDefaultFont', 10, 'bold'))
        self.style.configure("Main.TFrame", background=COLOR_BG_ROOT)
        self.style.configure("TNotebook", background=COLOR_BG_ROOT)
        self.style.configure("TNotebook.Tab", background=COLOR_BG_FRAME, foreground=COLOR_TEXT_HEADING, padding=[8,3])
        self.style.map("TNotebook.Tab", background=[("selected", COLOR_ACCENT_BUTTON)], foreground=[("selected", "white")])

    def _create_calculator_ui(self, parent_frame): # ... (same as before)
        input_frame = ttk.LabelFrame(parent_frame, text="Inputs", padding="10")
        input_frame.pack(fill=tk.X, pady=10, padx=5)
        input_frame.columnconfigure(1, weight=1)
        ttk.Label(input_frame, text="Enter numbers (comma-separated):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.numbers_entry = ttk.Entry(input_frame, textvariable=self.numbers_input_var, width=45, font=('TkDefaultFont', 10))
        self.numbers_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        factors_display_frame = ttk.LabelFrame(parent_frame, text="Prime Factorizations", padding="10")
        factors_display_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)
        self.factors_text = tk.Text(factors_display_frame, height=6, wrap=tk.WORD, relief=tk.SUNKEN, borderwidth=1, font=("Arial", 10), bg="#FFFFFF", fg=COLOR_TEXT_GENERAL, padx=5, pady=5)
        factors_scrollbar = ttk.Scrollbar(factors_display_frame, orient=tk.VERTICAL, command=self.factors_text.yview)
        factors_scrollbar.pack(side=tk.RIGHT, fill=tk.Y); self.factors_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.factors_text.config(yscrollcommand=factors_scrollbar.set, state=tk.DISABLED)
        self.factors_text.tag_configure("bold_num", font=("Arial", 10, "bold"), foreground=COLOR_TEXT_NUMBER_HIGHLIGHT)
        self.factors_text.tag_configure("prime", font=("Courier New", 10, "bold"), foreground=COLOR_TEXT_PRIME)
        self.factors_text.tag_configure("power", font=("Courier New", 10, "bold"), foreground=COLOR_TEXT_POWER)
        self.factors_text.tag_configure("separator", foreground="#888888")

        lcm_steps_frame = ttk.LabelFrame(parent_frame, text="LCM Calculation Steps", padding="10")
        lcm_steps_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)
        self.lcm_steps_text = tk.Text(lcm_steps_frame, height=12, wrap=tk.WORD, relief=tk.SUNKEN, borderwidth=1, font=("Arial", 10), bg="#FFFFFF", fg=COLOR_TEXT_GENERAL, padx=5, pady=5)
        steps_scrollbar = ttk.Scrollbar(lcm_steps_frame, orient=tk.VERTICAL, command=self.lcm_steps_text.yview)
        steps_scrollbar.pack(side=tk.RIGHT, fill=tk.Y); self.lcm_steps_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.lcm_steps_text.config(yscrollcommand=steps_scrollbar.set, state=tk.DISABLED)
        self.lcm_steps_text.tag_configure("bold", font=("Arial", 10, "bold"))
        self.lcm_steps_text.tag_configure("italic", font=("Arial", 10, "italic"))
        self.lcm_steps_text.tag_configure("heading", font=("Arial", 11, "bold", "underline"), foreground=COLOR_TEXT_HEADING)
        self.lcm_steps_text.tag_configure("math", font=("Courier New", 10))
        self.lcm_steps_text.tag_configure("prime_step", foreground=COLOR_TEXT_PRIME, font=("Courier New", 10, "bold"))
        self.lcm_steps_text.tag_configure("power_step", foreground=COLOR_TEXT_POWER, font=("Courier New", 10, "bold"))
        self.lcm_steps_text.tag_configure("final_lcm", font=("Arial", 11, "bold"), foreground=COLOR_TEXT_RESULT)

        result_frame = ttk.LabelFrame(parent_frame, text="Result", padding="10")
        result_frame.pack(fill=tk.X, pady=10, padx=5)
        self.lcm_result_label_prefix = ttk.Label(result_frame, text="LCM: ", font=("Arial", 12, "bold"), foreground=COLOR_TEXT_HEADING)
        self.lcm_result_label_prefix.pack(side=tk.LEFT)
        self.lcm_result_value_label = ttk.Label(result_frame, textvariable=self.lcm_result_var, font=("Arial", 12, "bold"), foreground=COLOR_TEXT_RESULT)
        self.lcm_result_value_label.pack(side=tk.LEFT)

        calc_buttons_frame = ttk.Frame(parent_frame, padding="10 5 0 5", style="Main.TFrame")
        calc_buttons_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.calculate_button = ttk.Button(calc_buttons_frame, text="Calculate LCM", command=self.handle_calculate_lcm, style="Accent.TButton")
        self.calculate_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.next_example_button = ttk.Button(calc_buttons_frame, text="Next Example", command=self.handle_next_example)
        self.next_example_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.clear_calc_button = ttk.Button(calc_buttons_frame, text="Clear", command=self.clear_fields)
        self.clear_calc_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.help_button_calc = ttk.Button(calc_buttons_frame, text="Help/Info", command=self.show_help)
        self.help_button_calc.pack(side=tk.RIGHT, padx=5, pady=5)

    def _create_practice_ui(self, parent_frame): # ... (canvas renamed to self.feedback_canvas)
        question_frame = ttk.LabelFrame(parent_frame, text="Practice Question", padding="10")
        question_frame.pack(fill=tk.X, pady=10, padx=5, expand=False)
        self.practice_question_label = ttk.Label(question_frame, textvariable=self.practice_question_var, font=("Arial", 12, "bold"), foreground=COLOR_PRACTICE_QUESTION, wraplength=700)
        self.practice_question_label.pack(pady=10)

        answer_frame = ttk.LabelFrame(parent_frame, text="Your Answer", padding="10")
        answer_frame.pack(fill=tk.X, pady=10, padx=5, expand=False)
        self.practice_answer_entry = ttk.Entry(answer_frame, textvariable=self.practice_answer_var, font=('TkDefaultFont', 11), width=20)
        self.practice_answer_entry.pack(pady=5)
        self.practice_answer_entry.bind("<Return>", lambda event: self.handle_submit_answer())

        self.feedback_canvas = tk.Canvas(parent_frame, width=120, height=120, bg=COLOR_BG_FRAME, highlightthickness=0)
        self.feedback_canvas.pack(pady=10)

        feedback_frame = ttk.LabelFrame(parent_frame, text="Feedback", padding="10")
        feedback_frame.pack(fill=tk.X, pady=10, padx=5, expand=False)
        self.practice_feedback_label = ttk.Label(feedback_frame, textvariable=self.practice_feedback_var, font=("Arial", 11, "italic"), wraplength=700)
        self.practice_feedback_label.pack(pady=5)

        practice_buttons_frame = ttk.Frame(parent_frame, padding="10 5 0 5", style="Main.TFrame")
        practice_buttons_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.submit_answer_button = ttk.Button(practice_buttons_frame, text="Submit Answer", command=self.handle_submit_answer, style="Accent.TButton")
        self.submit_answer_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.next_question_button = ttk.Button(practice_buttons_frame, text="Next Question", command=self.load_next_practice_question)
        self.next_question_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.help_button_practice = ttk.Button(practice_buttons_frame, text="Help/Info", command=self.show_help)
        self.help_button_practice.pack(side=tk.RIGHT, padx=5, pady=5)

    def _on_tab_change(self, event): # ... (same)
        selected_tab_index = self.notebook.index(self.notebook.select())
        if selected_tab_index == 0:
            self.in_practice_mode = False; self.calculator_mode_active = True
        elif selected_tab_index == 1:
            self.in_practice_mode = True; self.calculator_mode_active = False
            if not self.current_practice_question_numbers: self.start_practice_session()
        self._update_ui_for_mode()

    def _update_ui_for_mode(self): # ... (same)
        if self.in_practice_mode:
            self.practice_answer_entry.focus()
            if not self.current_practice_question_numbers: self.load_next_practice_question()
        else: self.numbers_entry.focus()

    def start_practice_session(self): # ... (same)
        self.current_question_index = -1
        self.load_next_practice_question()

    def _clear_feedback_canvas(self):
        if hasattr(self, 'feedback_canvas'):
            self.feedback_canvas.delete("all")
        if self.duck_animation_job_id:
            self.root.after_cancel(self.duck_animation_job_id)
            self.duck_animation_job_id = None

    def load_next_practice_question(self):
        self._clear_feedback_canvas() # Clear canvas for new question
        if not self.PRACTICE_QUESTIONS:
            self.practice_question_var.set("No practice questions available.")
            self.submit_answer_button.config(state=tk.DISABLED)
            self.next_question_button.config(state=tk.DISABLED)
            return

        self.current_question_index = (self.current_question_index + 1) % len(self.PRACTICE_QUESTIONS)
        q_data = self.PRACTICE_QUESTIONS[self.current_question_index]
        self.current_practice_question_numbers = q_data[0]
        self.current_practice_correct_lcm = q_data[1]
        numbers_str = ", ".join(map(str, self.current_practice_question_numbers))
        self.practice_question_var.set(f"What is the LCM of: {numbers_str}?")
        self.practice_answer_var.set("")
        self.practice_feedback_var.set("Enter your answer above.")
        self.practice_feedback_label.configure(foreground=COLOR_TEXT_GENERAL)
        self.submit_answer_button.config(state=tk.NORMAL)
        self.practice_answer_entry.focus()

        # Display initial duck frame (frame 0)
        if self.duck_frames and len(self.duck_frames) > 0:
             self.feedback_canvas.create_image(60, 60, image=self.duck_frames[0], tags="duck_image", anchor="center")


    def _animate_duck(self, frame_index=0):
        self._clear_feedback_canvas() # Clear previous frame/icon

        if frame_index < len(self.duck_frames):
            current_frame_image = self.duck_frames[frame_index]
            self.feedback_canvas.create_image(60, 60, image=current_frame_image, anchor="center", tags="duck_image")

            # Play quack sound on specific frames (e.g., frame 1 or 2)
            if PLAYSOUND_AVAILABLE and os.path.exists(self.quack_sound_path) and frame_index in [1, 2]:
                try:
                    playsound(self.quack_sound_path, block=False)
                except Exception as e:
                    print(f"Error playing quack sound: {e}")

            self.duck_animation_job_id = self.root.after(DUCK_FRAME_DELAY_MS, lambda: self._animate_duck(frame_index + 1))
        else:
            # Animation finished, optionally keep last frame or clear after a delay
            self.duck_animation_job_id = self.root.after(FEEDBACK_CLEAR_DELAY_MS - (DUCK_ANIMATION_FRAMES * DUCK_FRAME_DELAY_MS), self._clear_feedback_canvas)


    def handle_submit_answer(self): # ... (same validation logic)
        if not self.current_practice_question_numbers or self.current_practice_correct_lcm is None:
            messagebox.showwarning("No Question", "Please load a question first.", parent=self.root); return
        try:
            student_answer_str = self.practice_answer_var.get()
            if not student_answer_str.strip(): messagebox.showwarning("Input Required", "Please enter an answer.", parent=self.root); return
            student_answer = int(student_answer_str)
        except ValueError: messagebox.showerror("Invalid Input", "Please enter a valid number.", parent=self.root); self.practice_answer_var.set(""); return

        self._clear_feedback_canvas() # Clear previous animation/icon before new feedback

        if student_answer == self.current_practice_correct_lcm: self.trigger_correct_answer_feedback()
        else: self.trigger_incorrect_answer_feedback(self.current_practice_correct_lcm)
        self.submit_answer_button.config(state=tk.DISABLED)


    def trigger_correct_answer_feedback(self):
        self.practice_feedback_var.set("Correct! Well done. Click 'Next Question'.")
        self.practice_feedback_label.configure(foreground=COLOR_FEEDBACK_CORRECT)

        if hasattr(self, 'correct_image') and self.correct_image:
            self.feedback_canvas.create_image(60, 60, image=self.correct_image, anchor="center")

        if PLAYSOUND_AVAILABLE and os.path.exists(self.correct_sound_path):
            try: playsound(self.correct_sound_path, block=False)
            except Exception as e: print(f"Error playing correct sound: {e}")

        self.root.after(FEEDBACK_CLEAR_DELAY_MS, self._clear_feedback_canvas)


    def trigger_incorrect_answer_feedback(self, correct_answer: int):
        self.practice_feedback_var.set(f"Incorrect. The correct LCM is {correct_answer}. Try the next question.")
        self.practice_feedback_label.configure(foreground=COLOR_FEEDBACK_INCORRECT)
        self._animate_duck(0) # Start duck animation from frame 0


    # --- Calculator Mode Methods (largely unchanged) ---
    def _update_text_widget_formatted(self, text_widget: tk.Text, content_list: List[List[Tuple[str, List[str]]]]): # ... (same)
        text_widget.config(state=tk.NORMAL); text_widget.delete("1.0", tk.END)
        for line_content in content_list:
            for text_segment, tags in line_content: text_widget.insert(tk.END, text_segment, tuple(tags) if tags else None)
            text_widget.insert(tk.END, "\n")
        text_widget.config(state=tk.DISABLED)

    def _update_text_widget_simple(self, text_widget: tk.Text, content: List[Tuple[str, Optional[List[str]]]]): # ... (same)
        text_widget.config(state=tk.NORMAL); text_widget.delete("1.0", tk.END)
        for message, tags in content:
            if tags: text_widget.insert(tk.END, message, tuple(tags))
            else: text_widget.insert(tk.END, message)
            text_widget.insert(tk.END, "\n")
        text_widget.config(state=tk.DISABLED)

    def format_factorization_for_display(self, num:int, factors_counter: collections.Counter) -> List[Tuple[str, List[str]]]: # ... (same)
        line_content: List[Tuple[str, List[str]]] = [ (f"Factors of ", []), (f"{num}", ["bold_num"]), (f": ", []) ]
        if not factors_counter: line_content.append(("1", ["prime"])); return line_content
        sorted_factors = sorted(factors_counter.items())
        for i, (base, power) in enumerate(sorted_factors):
            if i > 0: line_content.append((" * ", ["separator"]))
            line_content.append((f"{base}", ["prime"]))
            if power > 1: line_content.append((f"^", ["separator"])); line_content.append((f"{power}", ["power"]))
        return line_content

    def show_help(self): # ... (same)
        help_text = "Prime Numbers: Divisible by 1 and self (e.g., 2, 3, 5).\nPrime Factorization: Breaking a number into prime multiples (e.g., 12 = 2^2 * 3).\nLCM: Smallest number divisible by all given numbers.\nCalculated via highest powers of all prime factors involved."
        messagebox.showinfo("Help/Info - LCM Learning Tool", help_text, parent=self.root)

    def handle_calculate_lcm(self): # ... (same calculator logic)
        input_str = self.numbers_input_var.get()
        if not input_str.strip(): messagebox.showerror("Input Error", "Please enter at least one number.", parent=self.root); return
        num_str_parts = input_str.split(','); numbers_list: List[int] = []; parsed_input_parts: List[str] = []
        for part in num_str_parts:
            stripped_part = part.strip()
            if not stripped_part: continue
            try: num = int(stripped_part); numbers_list.append(num); parsed_input_parts.append(stripped_part)
            except ValueError: messagebox.showerror("Input Error", f"Invalid input: '{stripped_part}' is not an integer.", parent=self.root); self.clear_fields_output_calc(); return
        if not numbers_list: messagebox.showerror("Input Error", "No valid numbers parsed.", parent=self.root); self.clear_fields_output_calc(); return
        try:
            factorization_display_content_list: List[List[Tuple[str, List[str]]]] = []
            all_factors_counters: List[collections.Counter] = []
            for num_val in numbers_list:
                if num_val < 1: messagebox.showerror("Input Error", f"Number '{num_val}' must be positive.", parent=self.root); self.clear_fields_output_calc(); return
                factors = get_prime_factorization(num_val); all_factors_counters.append(factors)
                factorization_display_content_list.append(self.format_factorization_for_display(num_val, factors))
            self._update_text_widget_formatted(self.factors_text, factorization_display_content_list)
            lcm_steps_content: List[List[Tuple[str, List[str]]]] = []
            lcm_steps_content.append([(("Input Numbers:", ["heading"]),)]); lcm_steps_content.append([((f"  {', '.join(parsed_input_parts)}", []),)]); lcm_steps_content.append([])
            lcm_steps_content.append([(("Prime Factorizations:", ["heading"]),)])
            for i, num_val in enumerate(numbers_list): line = [(f"  ", [])] + self.format_factorization_for_display(num_val, all_factors_counters[i])[2:]; lcm_steps_content.append(line)
            lcm_steps_content.append([])
            overall_max_factors = collections.Counter()
            for factors_counter in all_factors_counters:
                for prime, power in factors_counter.items(): overall_max_factors[prime] = max(overall_max_factors[prime], power)
            lcm_steps_content.append([(("Combining Factors for LCM:", ["heading"]),)])
            if not overall_max_factors: lcm_steps_content.append([(("  All numbers are 1. LCM is 1.", ["italic"]),)])
            lcm_calc_formula_parts: List[Tuple[str, List[str]]] = []
            for prime_val in sorted(overall_max_factors.keys()):
                max_power_val = overall_max_factors[prime_val]
                lcm_steps_content.append([((f"  For prime ", []), (f"{prime_val}", ["prime_step"]), (f": highest power is ",[]), (f"{prime_val}",["prime_step"]), (f"^",[]), (f"{max_power_val}",["power_step"]) )])
                if lcm_calc_formula_parts: lcm_calc_formula_parts.append((" * ", ["math"]))
                lcm_calc_formula_parts.append((f"{prime_val}", ["prime_step"]))
                if max_power_val > 1: lcm_calc_formula_parts.append((f"^", ["math"])); lcm_calc_formula_parts.append((f"{max_power_val}", ["power_step"]))
            if lcm_calc_formula_parts: lcm_steps_content.append([]); lcm_steps_content.append([(("LCM Calculation Formula:", ["heading"]),)]); line = [(("  LCM = ", ["math"]),)] + lcm_calc_formula_parts; lcm_steps_content.append(line) # type: ignore
            lcm_val_calculated = calculate_lcm(*numbers_list)
            self.lcm_result_var.set(f"{lcm_val_calculated}")
            lcm_steps_content.append([]); lcm_steps_content.append([(("Final LCM Value:", ["heading"]),)]); lcm_steps_content.append([(("  LCM = ", []), (f"{lcm_val_calculated}", ["final_lcm"]),)])
            self._update_text_widget_formatted(self.lcm_steps_text, lcm_steps_content)
        except ValueError as e: messagebox.showerror("Calculation Error", str(e), parent=self.root); self.clear_fields_output_calc()
        except Exception as e: messagebox.showerror("Error", f"An unexpected error: {e}", parent=self.root); self.clear_fields_output_calc()

    def clear_fields_output_calc(self): # ... (same)
        self._update_text_widget_simple(self.factors_text, [("Factorizations will appear here.", ["italic"])])
        self._update_text_widget_simple(self.lcm_steps_text, [("Calculation steps will appear here.", ["italic"])])
        self.lcm_result_var.set("-")

    def clear_fields(self): # ... (Updated to include feedback_canvas clearing)
        self.numbers_input_var.set("")
        self.clear_fields_output_calc()
        if hasattr(self, 'numbers_entry'): self.numbers_entry.focus()
        if hasattr(self, 'practice_answer_var'): self.practice_answer_var.set("")
        if hasattr(self, 'practice_feedback_var'): self.practice_feedback_var.set("Select a tab to start.")
        if hasattr(self, 'practice_question_var'): self.practice_question_var.set("Switch to 'Practice Mode' tab for questions.")
        self._clear_feedback_canvas()


    def handle_next_example(self): # ... (same)
        self.current_example_index = (self.current_example_index + 1) % len(self.EXAMPLES)
        current_example_nums = self.EXAMPLES[self.current_example_index]
        self.numbers_input_var.set(", ".join(map(str, current_example_nums)))
        self.handle_calculate_lcm()

if __name__ == '__main__':
    app_root = tk.Tk()
    app = LCMLearningToolApp(app_root)
    app_root.mainloop()
