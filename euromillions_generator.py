import tkinter as tk
from tkinter import ttk
import random

class EuroMillionsGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("EuroMillions Number Generator")
        self.root.geometry("500x400")
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(main_frame, text="EuroMillions Number Generator", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        generate_btn = ttk.Button(main_frame, text="Generate 3 Sets of Numbers", 
                                 command=self.generate_numbers, 
                                 style="Accent.TButton")
        generate_btn.grid(row=1, column=0, pady=(0, 20))
        
        self.results_frame = ttk.LabelFrame(main_frame, text="Generated Numbers", padding="10")
        self.results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def generate_numbers(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        for i in range(3):
            main_numbers = sorted(random.sample(range(1, 51), 5))
            lucky_stars = sorted(random.sample(range(1, 13), 2))
            
            set_frame = ttk.Frame(self.results_frame)
            set_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)
            
            set_label = ttk.Label(set_frame, text=f"Set {i+1}:", font=("Arial", 12, "bold"))
            set_label.grid(row=0, column=0, sticky=tk.W)
            
            main_numbers_str = " - ".join(map(str, main_numbers))
            stars_str = " - ".join(map(str, lucky_stars))
            
            numbers_label = ttk.Label(set_frame, 
                                    text=f"Main: {main_numbers_str}   Stars: {stars_str}",
                                    font=("Arial", 11))
            numbers_label.grid(row=1, column=0, sticky=tk.W, padx=(20, 0))
            
            set_frame.columnconfigure(0, weight=1)
        
        self.results_frame.columnconfigure(0, weight=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = EuroMillionsGenerator(root)
    root.mainloop()