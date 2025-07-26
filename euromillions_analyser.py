import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import csv
import os
import random
from collections import Counter, defaultdict
from datetime import datetime
import threading
from itertools import combinations

class EuroMillionsAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("EuroMillions Lottery Analyzer")
        self.root.geometry("800x600")
        
        self.data = []
        self.main_numbers = []
        self.lucky_stars = []
        
        # Saved numbers
        self.saved_numbers_file = "saved_numbers.json"
        self.saved_numbers = self.load_saved_numbers()
        
        # Data cache
        self.data_cache_file = "euromillions_data_cache.json"
        
        self.setup_ui()
        self.load_cached_data()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Download section
        download_frame = ttk.LabelFrame(main_frame, text="Data Download", padding="5")
        download_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.download_btn = ttk.Button(download_frame, text="Download Latest Data", 
                                     command=self.download_data)
        self.download_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.save_csv_btn = ttk.Button(download_frame, text="Save as CSV", 
                                     command=self.save_as_csv, state="disabled")
        self.save_csv_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.status_label = ttk.Label(download_frame, text="Loading cached data...")
        self.status_label.grid(row=0, column=2, columnspan=2, sticky=tk.W)
        
        # Data freshness indicator
        self.freshness_label = ttk.Label(download_frame, text="", foreground="orange")
        self.freshness_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # Statistics section
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="5")
        stats_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create notebook for different statistics
        self.notebook = ttk.Notebook(stats_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Statistics tabs
        self.create_frequency_tab()
        self.create_overdue_tab()
        self.create_patterns_tab()
        self.create_generator_tab()
        self.create_saved_numbers_tab()
        self.create_user_numbers_tab()
        self.create_winners_analysis_tab()
        self.create_bias_analysis_tab()
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(0, weight=1)
    
    def create_frequency_tab(self):
        freq_frame = ttk.Frame(self.notebook)
        self.notebook.add(freq_frame, text="Most/Least Drawn")
        
        self.freq_text = scrolledtext.ScrolledText(freq_frame, height=15, width=70)
        self.freq_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        freq_frame.columnconfigure(0, weight=1)
        freq_frame.rowconfigure(0, weight=1)
    
    def create_overdue_tab(self):
        overdue_frame = ttk.Frame(self.notebook)
        self.notebook.add(overdue_frame, text="Overdue Numbers")
        
        self.overdue_text = scrolledtext.ScrolledText(overdue_frame, height=15, width=70)
        self.overdue_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        overdue_frame.columnconfigure(0, weight=1)
        overdue_frame.rowconfigure(0, weight=1)
    
    def create_patterns_tab(self):
        patterns_frame = ttk.Frame(self.notebook)
        self.notebook.add(patterns_frame, text="Patterns")
        
        self.patterns_text = scrolledtext.ScrolledText(patterns_frame, height=15, width=70)
        self.patterns_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        patterns_frame.columnconfigure(0, weight=1)
        patterns_frame.rowconfigure(0, weight=1)
    
    def create_generator_tab(self):
        generator_frame = ttk.Frame(self.notebook)
        self.notebook.add(generator_frame, text="Number Generator")
        
        # Generator controls
        controls_frame = ttk.Frame(generator_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(controls_frame, text="Generate tickets based on patterns:").grid(row=0, column=0, sticky=tk.W)
        
        generate_btn = ttk.Button(controls_frame, text="Generate Smart Numbers", 
                                command=self.generate_smart_numbers)
        generate_btn.grid(row=1, column=0, pady=(10, 0))
        
        # Results section
        self.generator_text = scrolledtext.ScrolledText(generator_frame, height=12, width=70)
        self.generator_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        generator_frame.columnconfigure(0, weight=1)
        generator_frame.rowconfigure(1, weight=1)
    
    def create_saved_numbers_tab(self):
        saved_frame = ttk.Frame(self.notebook)
        self.notebook.add(saved_frame, text="Saved Numbers")
        
        # Controls section
        controls_frame = ttk.Frame(saved_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(controls_frame, text="Add New Number Set:").grid(row=0, column=0, sticky=tk.W)
        
        # Input fields
        input_frame = ttk.Frame(controls_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, sticky=tk.W)
        self.save_name_entry = ttk.Entry(input_frame, width=20)
        self.save_name_entry.grid(row=0, column=1, padx=(5, 10))
        
        ttk.Label(input_frame, text="Main:").grid(row=0, column=2, sticky=tk.W)
        self.save_main_entry = ttk.Entry(input_frame, width=15)
        self.save_main_entry.grid(row=0, column=3, padx=(5, 10))
        
        ttk.Label(input_frame, text="Stars:").grid(row=0, column=4, sticky=tk.W)
        self.save_stars_entry = ttk.Entry(input_frame, width=10)
        self.save_stars_entry.grid(row=0, column=5, padx=(5, 10))
        
        save_btn = ttk.Button(input_frame, text="Save", command=self.save_number_set)
        save_btn.grid(row=0, column=6, padx=(5, 0))
        
        # Management buttons
        mgmt_frame = ttk.Frame(controls_frame)
        mgmt_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        analyze_all_btn = ttk.Button(mgmt_frame, text="Analyze All Sets", 
                                   command=self.analyze_all_saved_sets)
        analyze_all_btn.grid(row=0, column=0, padx=(0, 10))
        
        load_btn = ttk.Button(mgmt_frame, text="Load Selected", 
                            command=self.load_selected_set)
        load_btn.grid(row=0, column=1, padx=(0, 10))
        
        delete_btn = ttk.Button(mgmt_frame, text="Delete Selected", 
                              command=self.delete_selected_set)
        delete_btn.grid(row=0, column=2, padx=(0, 10))
        
        # Saved numbers list
        list_frame = ttk.Frame(saved_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Treeview for saved numbers
        columns = ('Name', 'Main Numbers', 'Lucky Stars', 'Date Saved')
        self.saved_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.saved_tree.heading(col, text=col)
            self.saved_tree.column(col, width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.saved_tree.yview)
        self.saved_tree.configure(yscrollcommand=v_scrollbar.set)
        
        self.saved_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Analysis results
        self.saved_analysis_text = scrolledtext.ScrolledText(saved_frame, height=8, width=70)
        self.saved_analysis_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        saved_frame.columnconfigure(0, weight=1)
        saved_frame.rowconfigure(2, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.refresh_saved_numbers_display()
    
    def create_user_numbers_tab(self):
        user_frame = ttk.Frame(self.notebook)
        self.notebook.add(user_frame, text="Your Numbers")
        
        # Input section
        input_frame = ttk.Frame(user_frame)
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(input_frame, text="Main Numbers (1-50):").grid(row=0, column=0, sticky=tk.W)
        self.main_entry = ttk.Entry(input_frame, width=30)
        self.main_entry.grid(row=0, column=1, padx=(5, 0))
        
        ttk.Label(input_frame, text="Lucky Stars (1-12):").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.stars_entry = ttk.Entry(input_frame, width=30)
        self.stars_entry.grid(row=1, column=1, padx=(5, 0), pady=(5, 0))
        
        analyze_btn = ttk.Button(input_frame, text="Analyze My Numbers", 
                               command=self.analyze_user_numbers)
        analyze_btn.grid(row=2, column=0, pady=(10, 0))
        
        save_current_btn = ttk.Button(input_frame, text="Save This Set", 
                                    command=self.save_current_numbers)
        save_current_btn.grid(row=2, column=1, padx=(10, 0), pady=(10, 0))
        
        # Results section
        self.user_results_text = scrolledtext.ScrolledText(user_frame, height=12, width=70)
        self.user_results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        user_frame.columnconfigure(0, weight=1)
        user_frame.rowconfigure(1, weight=1)
    
    def create_winners_analysis_tab(self):
        winners_frame = ttk.Frame(self.notebook)
        self.notebook.add(winners_frame, text="Historical Winners")
        
        # Controls section
        controls_frame = ttk.Frame(winners_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(controls_frame, text="Analyze historical winning combinations:").grid(row=0, column=0, sticky=tk.W)
        
        analyze_winners_btn = ttk.Button(controls_frame, text="Analyze All Winners", 
                                       command=self.analyze_historical_winners)
        analyze_winners_btn.grid(row=1, column=0, pady=(10, 0), padx=(0, 10))
        
        analyze_jackpots_btn = ttk.Button(controls_frame, text="Jackpot Winners Only", 
                                        command=self.analyze_jackpot_winners)
        analyze_jackpots_btn.grid(row=1, column=1, pady=(10, 0), padx=(0, 10))
        
        analyze_top_prizes_btn = ttk.Button(controls_frame, text="Top 3 Prize Levels", 
                                          command=self.analyze_top_prize_winners)
        analyze_top_prizes_btn.grid(row=1, column=2, pady=(10, 0))
        
        analyze_duplicates_btn = ttk.Button(controls_frame, text="Duplicate Jackpots", 
                                          command=self.analyze_duplicate_jackpots)
        analyze_duplicates_btn.grid(row=1, column=3, pady=(10, 0), padx=(10, 0))
        
        # Results section
        self.winners_results_text = scrolledtext.ScrolledText(winners_frame, height=20, width=80)
        self.winners_results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        winners_frame.columnconfigure(0, weight=1)
        winners_frame.rowconfigure(1, weight=1)
    
    def create_bias_analysis_tab(self):
        bias_frame = ttk.Frame(self.notebook)
        self.notebook.add(bias_frame, text="Bias Analysis")
        
        # Controls section
        controls_frame = ttk.Frame(bias_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(controls_frame, text="Statistical Anomaly & Physical Bias Detection:").grid(row=0, column=0, sticky=tk.W, columnspan=4)
        
        # Analysis buttons
        chi_square_btn = ttk.Button(controls_frame, text="Chi-Square Test", 
                                   command=self.analyze_chi_square)
        chi_square_btn.grid(row=1, column=0, pady=(10, 0), padx=(0, 10))
        
        coefficient_var_btn = ttk.Button(controls_frame, text="Coefficient of Variation", 
                                       command=self.analyze_coefficient_variation)
        coefficient_var_btn.grid(row=1, column=1, pady=(10, 0), padx=(0, 10))
        
        temporal_bias_btn = ttk.Button(controls_frame, text="Temporal Bias", 
                                     command=self.analyze_temporal_bias)
        temporal_bias_btn.grid(row=1, column=2, pady=(10, 0), padx=(0, 10))
        
        autocorr_btn = ttk.Button(controls_frame, text="Autocorrelation", 
                                command=self.analyze_autocorrelation)
        autocorr_btn.grid(row=1, column=3, pady=(10, 0))
        
        # Equipment analysis buttons
        ttk.Label(controls_frame, text="Equipment & Environmental Analysis:").grid(row=2, column=0, sticky=tk.W, columnspan=4, pady=(20, 0))
        
        ball_wear_btn = ttk.Button(controls_frame, text="Ball Wear Analysis", 
                                 command=self.analyze_ball_wear)
        ball_wear_btn.grid(row=3, column=0, pady=(10, 0), padx=(0, 10))
        
        machine_bias_btn = ttk.Button(controls_frame, text="Machine Bias", 
                                    command=self.analyze_machine_bias)
        machine_bias_btn.grid(row=3, column=1, pady=(10, 0), padx=(0, 10))
        
        seasonal_btn = ttk.Button(controls_frame, text="Seasonal Effects", 
                                command=self.analyze_seasonal_effects)
        seasonal_btn.grid(row=3, column=2, pady=(10, 0), padx=(0, 10))
        
        anomaly_detect_btn = ttk.Button(controls_frame, text="Anomaly Detection", 
                                      command=self.detect_anomalies)
        anomaly_detect_btn.grid(row=3, column=3, pady=(10, 0))
        
        # Results section
        self.bias_results_text = scrolledtext.ScrolledText(bias_frame, height=25, width=90)
        self.bias_results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        bias_frame.columnconfigure(0, weight=1)
        bias_frame.rowconfigure(1, weight=1)
    
    def get_next_draw_date(self):
        """Calculate the next EuroMillions draw date (Tuesday or Friday)"""
        from datetime import datetime, timedelta
        
        today = datetime.now()
        
        # EuroMillions draws are on Tuesdays (1) and Fridays (4)
        # weekday() returns 0=Monday, 1=Tuesday, etc.
        current_weekday = today.weekday()
        
        if current_weekday < 1:  # Monday
            days_until_next = 1 - current_weekday  # Next Tuesday
        elif current_weekday == 1:  # Tuesday
            # If it's Tuesday, next draw is Friday
            days_until_next = 3
        elif current_weekday < 4:  # Wednesday or Thursday
            days_until_next = 4 - current_weekday  # Next Friday
        elif current_weekday == 4:  # Friday
            # If it's Friday, next draw is Tuesday
            days_until_next = 4  # Next Tuesday (7-3)
        else:  # Weekend (Saturday, Sunday)
            days_until_next = 8 - current_weekday  # Next Tuesday
        
        next_draw = today + timedelta(days=days_until_next)
        return next_draw.replace(hour=20, minute=0, second=0, microsecond=0)  # Draws are around 8 PM
    
    def get_last_expected_draw_date(self):
        """Get the date of the most recent draw that should have happened"""
        from datetime import datetime, timedelta
        
        today = datetime.now()
        current_weekday = today.weekday()
        current_hour = today.hour
        
        # If it's Tuesday or Friday after 8 PM, the draw has happened
        if (current_weekday == 1 and current_hour >= 20) or (current_weekday == 4 and current_hour >= 20):
            return today.replace(hour=20, minute=0, second=0, microsecond=0)
        
        # Otherwise, find the last draw date
        if current_weekday < 1 or (current_weekday == 1 and current_hour < 20):
            # Last draw was Friday
            days_back = (current_weekday + 3) if current_weekday <= 1 else (current_weekday - 4)
            last_draw = today - timedelta(days=days_back)
        elif current_weekday < 4 or (current_weekday == 4 and current_hour < 20):
            # Last draw was Tuesday
            days_back = current_weekday - 1
            last_draw = today - timedelta(days=days_back)
        else:  # Weekend
            # Last draw was Friday
            days_back = current_weekday - 4
            last_draw = today - timedelta(days=days_back)
        
        return last_draw.replace(hour=20, minute=0, second=0, microsecond=0)
    
    def is_data_current(self):
        """Check if cached data is up to date"""
        if not self.data:
            return False
        
        last_expected_draw = self.get_last_expected_draw_date()
        latest_data_date = max(draw['date'] for draw in self.data)
        
        # Convert latest_data_date to datetime if it's just a date
        if hasattr(latest_data_date, 'date'):
            latest_data_date = latest_data_date
        else:
            latest_data_date = datetime.combine(latest_data_date, datetime.min.time())
        
        # Data is current if our latest data is from the last expected draw date or later
        return latest_data_date.date() >= last_expected_draw.date()
    
    def update_freshness_indicator(self):
        """Update the UI to show data freshness status"""
        if not self.data:
            self.freshness_label.config(text="No data loaded", foreground="red")
            return
        
        if self.is_data_current():
            self.freshness_label.config(text="✓ Data is up to date", foreground="green")
        else:
            last_expected = self.get_last_expected_draw_date()
            next_draw = self.get_next_draw_date()
            
            self.freshness_label.config(
                text=f"⚠ Data may be outdated. Expected draw: {last_expected.strftime('%a %Y-%m-%d')}. Next draw: {next_draw.strftime('%a %Y-%m-%d')}",
                foreground="orange"
            )
    
    def save_data_cache(self):
        """Save current data to cache file"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': []
            }
            
            for draw in self.data:
                cache_data['data'].append({
                    'date': draw['date'].isoformat(),
                    'main_numbers': draw['main_numbers'],
                    'lucky_stars': draw['lucky_stars']
                })
            
            with open(self.data_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving data cache: {e}")
    
    def load_cached_data(self):
        """Load data from cache file if it exists"""
        try:
            if os.path.exists(self.data_cache_file):
                with open(self.data_cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                self.data = []
                self.main_numbers = []
                self.lucky_stars = []
                
                for draw_data in cache_data['data']:
                    try:
                        draw_date = datetime.fromisoformat(draw_data['date'])
                        main_nums = draw_data['main_numbers']
                        star_nums = draw_data['lucky_stars']
                        
                        draw = {
                            'date': draw_date,
                            'main_numbers': main_nums,
                            'lucky_stars': star_nums
                        }
                        
                        self.data.append(draw)
                        self.main_numbers.extend(main_nums)
                        self.lucky_stars.extend(star_nums)
                        
                    except (ValueError, KeyError, TypeError) as e:
                        print(f"Skipping invalid cached draw: {e}")
                        continue
                
                if self.data:
                    # Sort data by date (oldest first)
                    self.data.sort(key=lambda x: x['date'])
                    
                    earliest = min(self.data, key=lambda x: x['date'])['date']
                    latest = max(self.data, key=lambda x: x['date'])['date']
                    
                    status_text = f"Loaded {len(self.data)} draws from cache ({earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')})"
                    self.status_label.config(text=status_text)
                    self.save_csv_btn.config(state="normal")
                    self.update_statistics()
                    self.update_freshness_indicator()
                    return
            
            # No cache file or cache is empty
            self.status_label.config(text="No cached data found - click 'Download Latest Data'")
            self.update_freshness_indicator()
            
        except Exception as e:
            print(f"Error loading cached data: {e}")
            self.status_label.config(text="Error loading cache - click 'Download Latest Data'")
            self.update_freshness_indicator()
    
    def download_data(self):
        def download():
            try:
                self.status_label.config(text="Downloading...")
                self.download_btn.config(state="disabled")
                
                url = "https://euromillions.api.pedromealha.dev/v1/draws"
                response = requests.get(url, timeout=60)
                response.raise_for_status()
                
                # Parse JSON data
                json_data = response.json()
                
                self.data = []
                self.main_numbers = []
                self.lucky_stars = []
                
                for draw in json_data:
                    try:
                        # Parse date from YYYY-MM-DD format
                        draw_date = datetime.strptime(draw['date'], '%Y-%m-%d')
                        
                        # Convert number strings to integers
                        main_nums = [int(num) for num in draw['numbers']]
                        star_nums = [int(star) for star in draw['stars']]
                        
                        draw_data = {
                            'date': draw_date,
                            'main_numbers': main_nums,
                            'lucky_stars': star_nums
                        }
                        
                        self.data.append(draw_data)
                        self.main_numbers.extend(main_nums)
                        self.lucky_stars.extend(star_nums)
                        
                    except (ValueError, KeyError, TypeError) as e:
                        print("Skipping invalid draw: {}".format(e))
                        continue
                
                if self.data:
                    # Sort data by date (oldest first)
                    self.data.sort(key=lambda x: x['date'])
                    
                    earliest = min(self.data, key=lambda x: x['date'])['date']
                    latest = max(self.data, key=lambda x: x['date'])['date']
                    
                    status_text = "Downloaded {} draws ({} to {})".format(
                        len(self.data), 
                        earliest.strftime('%Y-%m-%d'),
                        latest.strftime('%Y-%m-%d')
                    )
                    self.status_label.config(text=status_text)
                    self.save_csv_btn.config(state="normal")
                    self.update_statistics()
                    self.save_data_cache()  # Save to cache
                    self.update_freshness_indicator()  # Update freshness status
                else:
                    self.status_label.config(text="No valid data found")
                    
            except requests.RequestException as e:
                messagebox.showerror("Download Error", "Failed to download data: {}".format(str(e)))
                self.status_label.config(text="Download failed")
            except Exception as e:
                messagebox.showerror("Error", "An error occurred: {}".format(str(e)))
                self.status_label.config(text="Error occurred")
            finally:
                self.download_btn.config(state="normal")
        
        # Run download in separate thread to prevent UI freezing
        thread = threading.Thread(target=download)
        thread.daemon = True
        thread.start()
    
    def save_as_csv(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please download data first!")
            return
        
        try:
            # Create filename with current timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = "euromillions_data_{}.csv".format(timestamp)
            filepath = os.path.join(os.getcwd(), filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['DrawDate', 'Ball1', 'Ball2', 'Ball3', 'Ball4', 'Ball5', 'LuckyStar1', 'LuckyStar2']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write data
                for draw in self.data:
                    row_data = {
                        'DrawDate': draw['date'].strftime('%Y-%m-%d'),
                        'Ball1': draw['main_numbers'][0],
                        'Ball2': draw['main_numbers'][1],
                        'Ball3': draw['main_numbers'][2],
                        'Ball4': draw['main_numbers'][3],
                        'Ball5': draw['main_numbers'][4],
                        'LuckyStar1': draw['lucky_stars'][0],
                        'LuckyStar2': draw['lucky_stars'][1]
                    }
                    writer.writerow(row_data)
            
            messagebox.showinfo("Success", "Data saved as: {}".format(filename))
            
        except Exception as e:
            messagebox.showerror("Save Error", "Failed to save CSV file: {}".format(str(e)))
    
    def update_statistics(self):
        self.update_frequency_stats()
        self.update_overdue_stats()
        self.update_pattern_stats()
    
    def update_frequency_stats(self):
        if not self.data:
            return
        
        main_counter = Counter(self.main_numbers)
        stars_counter = Counter(self.lucky_stars)
        
        text = "MAIN NUMBERS FREQUENCY\n"
        text += "=" * 50 + "\n\n"
        
        text += "MOST DRAWN MAIN NUMBERS:\n"
        most_drawn_main = main_counter.most_common(10)
        for number, count in most_drawn_main:
            text += "Number {:2d}: {:3d} times\n".format(number, count)
        
        text += "\nLEAST DRAWN MAIN NUMBERS:\n"
        least_drawn_main = main_counter.most_common()[:-11:-1]
        for number, count in least_drawn_main:
            text += "Number {:2d}: {:3d} times\n".format(number, count)
        
        text += "\n" + "=" * 50 + "\n"
        text += "LUCKY STARS FREQUENCY\n"
        text += "=" * 50 + "\n\n"
        
        text += "MOST DRAWN LUCKY STARS:\n"
        most_drawn_stars = stars_counter.most_common(6)
        for number, count in most_drawn_stars:
            text += "Star {:2d}: {:3d} times\n".format(number, count)
        
        text += "\nLEAST DRAWN LUCKY STARS:\n"
        least_drawn_stars = stars_counter.most_common()[:-7:-1]
        for number, count in least_drawn_stars:
            text += "Star {:2d}: {:3d} times\n".format(number, count)
        
        self.freq_text.delete(1.0, tk.END)
        self.freq_text.insert(1.0, text)
    
    def update_overdue_stats(self):
        if not self.data:
            return
        
        # Calculate days since last appearance for each number
        main_overdue = {}
        stars_overdue = {}
        latest_date = max(draw['date'] for draw in self.data)
        
        # Initialize all numbers
        for i in range(1, 51):
            main_overdue[i] = float('inf')
        for i in range(1, 13):
            stars_overdue[i] = float('inf')
        
        # Find last appearance of each number
        for draw in sorted(self.data, key=lambda x: x['date'], reverse=True):
            for num in draw['main_numbers']:
                if main_overdue[num] == float('inf'):
                    main_overdue[num] = (latest_date - draw['date']).days
            for star in draw['lucky_stars']:
                if stars_overdue[star] == float('inf'):
                    stars_overdue[star] = (latest_date - draw['date']).days
        
        text = "LONGEST OVERDUE NUMBERS\n"
        text += "=" * 50 + "\n\n"
        
        text += "MOST OVERDUE MAIN NUMBERS:\n"
        sorted_main_overdue = sorted(main_overdue.items(), key=lambda x: x[1], reverse=True)[:15]
        for number, days in sorted_main_overdue:
            if days == float('inf'):
                text += "Number {:2d}: Never drawn\n".format(number)
            else:
                text += "Number {:2d}: {:3d} days ago\n".format(number, days)
        
        text += "\nMOST OVERDUE LUCKY STARS:\n"
        sorted_stars_overdue = sorted(stars_overdue.items(), key=lambda x: x[1], reverse=True)[:8]
        for number, days in sorted_stars_overdue:
            if days == float('inf'):
                text += "Star {:2d}: Never drawn\n".format(number)
            else:
                text += "Star {:2d}: {:3d} days ago\n".format(number, days)
        
        self.overdue_text.delete(1.0, tk.END)
        self.overdue_text.insert(1.0, text)
    
    def update_pattern_stats(self):
        if not self.data:
            return
        
        text = "ADVANCED PATTERN ANALYSIS\n"
        text += "=" * 50 + "\n\n"
        
        # Hot/Cold Streaks
        text += "HOT/COLD STREAKS (Last 20 draws):\n"
        text += "-" * 30 + "\n"
        hot_cold = self.analyze_hot_cold_streaks()
        text += "Hot Numbers (appearing frequently): {}\n".format(', '.join(map(str, hot_cold['hot'])))
        text += "Cold Numbers (avoiding draws): {}\n\n".format(', '.join(map(str, hot_cold['cold'])))
        
        # Sum Analysis
        text += "SUM RANGE ANALYSIS:\n"
        text += "-" * 20 + "\n"
        sum_stats = self.analyze_sum_ranges()
        text += "Most common sum range: {} - {} ({}% of draws)\n".format(
            sum_stats['most_common_range'][0], sum_stats['most_common_range'][1], 
            sum_stats['most_common_percentage'])
        text += "Average sum: {:.1f}\n".format(sum_stats['average'])
        text += "Recommended sum range: {} - {}\n\n".format(
            sum_stats['recommended_min'], sum_stats['recommended_max'])
        
        # Odd/Even Patterns
        text += "ODD/EVEN PATTERNS:\n"
        text += "-" * 18 + "\n"
        odd_even = self.analyze_odd_even_patterns()
        text += "Most common odd/even ratio: {} odd, {} even ({}% of draws)\n".format(
            odd_even['most_common'][0], odd_even['most_common'][1], odd_even['percentage'])
        
        # Number Pairs
        text += "\nTOP NUMBER PAIRS:\n"
        text += "-" * 17 + "\n"
        pairs = self.analyze_number_pairs()
        for i, (pair, count) in enumerate(pairs[:10]):
            text += "{}. {} & {}: {} times\n".format(i+1, pair[0], pair[1], count)
        
        # Consecutive Numbers
        text += "\nCONSECUTIVE NUMBERS:\n"
        text += "-" * 19 + "\n"
        consecutive_stats = self.analyze_consecutive_numbers()
        text += "Draws with consecutive numbers: {}% ({} draws)\n".format(
            consecutive_stats['percentage'], consecutive_stats['count'])
        text += "Most common consecutive pairs: {}\n".format(
            ', '.join(['{}-{}'.format(p[0], p[1]) for p in consecutive_stats['top_pairs'][:5]]))
        
        self.patterns_text.delete(1.0, tk.END)
        self.patterns_text.insert(1.0, text)
    
    def analyze_hot_cold_streaks(self):
        recent_draws = self.data[-20:] if len(self.data) >= 20 else self.data
        recent_numbers = []
        for draw in recent_draws:
            recent_numbers.extend(draw['main_numbers'])
        
        number_count = Counter(recent_numbers)
        avg_frequency = len(recent_numbers) / 50  # Average appearances per number
        
        hot_numbers = [num for num, count in number_count.items() if count > avg_frequency * 1.5]
        cold_numbers = [num for num in range(1, 51) if number_count.get(num, 0) < avg_frequency * 0.5]
        
        return {
            'hot': sorted(hot_numbers)[:8],
            'cold': sorted(cold_numbers)[:8]
        }
    
    def analyze_sum_ranges(self):
        sums = [sum(draw['main_numbers']) for draw in self.data]
        sum_counter = Counter(sums)
        
        # Group into ranges
        ranges = {}
        for s in sums:
            range_key = (s // 10) * 10
            ranges[range_key] = ranges.get(range_key, 0) + 1
        
        most_common_range_start = max(ranges.keys(), key=ranges.get)
        most_common_percentage = round(ranges[most_common_range_start] / len(sums) * 100, 1)
        
        return {
            'average': sum(sums) / len(sums),
            'most_common_range': (most_common_range_start, most_common_range_start + 9),
            'most_common_percentage': most_common_percentage,
            'recommended_min': int(sum(sums) / len(sums) - 25),
            'recommended_max': int(sum(sums) / len(sums) + 25)
        }
    
    def analyze_odd_even_patterns(self):
        patterns = []
        for draw in self.data:
            odd_count = sum(1 for num in draw['main_numbers'] if num % 2 == 1)
            even_count = 5 - odd_count
            patterns.append((odd_count, even_count))
        
        pattern_counter = Counter(patterns)
        most_common = pattern_counter.most_common(1)[0]
        percentage = round(most_common[1] / len(patterns) * 100, 1)
        
        return {
            'most_common': most_common[0],
            'percentage': percentage
        }
    
    def analyze_number_pairs(self):
        pair_counter = Counter()
        for draw in self.data:
            pairs = list(combinations(sorted(draw['main_numbers']), 2))
            pair_counter.update(pairs)
        
        return pair_counter.most_common(15)
    
    def analyze_consecutive_numbers(self):
        consecutive_count = 0
        consecutive_pairs = Counter()
        
        for draw in self.data:
            numbers = sorted(draw['main_numbers'])
            has_consecutive = False
            
            for i in range(len(numbers) - 1):
                if numbers[i + 1] == numbers[i] + 1:
                    has_consecutive = True
                    consecutive_pairs[(numbers[i], numbers[i + 1])] += 1
            
            if has_consecutive:
                consecutive_count += 1
        
        percentage = round(consecutive_count / len(self.data) * 100, 1)
        
        return {
            'count': consecutive_count,
            'percentage': percentage,
            'top_pairs': consecutive_pairs.most_common(10)
        }
    
    def generate_smart_numbers(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please download data first!")
            return
        
        try:
            text = "SMART NUMBER GENERATION\n"
            text += "=" * 50 + "\n\n"
            
            # Generate 5 different tickets using different strategies
            strategies = [
                ("Balanced Strategy", self.generate_balanced_ticket),
                ("Hot Numbers Strategy", self.generate_hot_ticket),
                ("Pattern-Based Strategy", self.generate_pattern_ticket),
                ("Overdue Strategy", self.generate_overdue_ticket),
                ("Hybrid Strategy", self.generate_hybrid_ticket)
            ]
            
            for strategy_name, generator_func in strategies:
                main_nums, stars = generator_func()
                text += "{}: \n".format(strategy_name)
                text += "Main: {} | Stars: {}\n".format(
                    ', '.join(['{:2d}'.format(n) for n in sorted(main_nums)]),
                    ', '.join(['{:2d}'.format(s) for s in sorted(stars)])
                )
                text += "Sum: {} | Odd/Even: {}/{}\n\n".format(
                    sum(main_nums),
                    sum(1 for n in main_nums if n % 2 == 1),
                    sum(1 for n in main_nums if n % 2 == 0)
                )
            
            self.generator_text.delete(1.0, tk.END)
            self.generator_text.insert(1.0, text)
            
        except Exception as e:
            messagebox.showerror("Generation Error", "Failed to generate numbers: {}".format(str(e)))
    
    def generate_balanced_ticket(self):
        # Generate based on optimal sum range and odd/even balance
        sum_stats = self.analyze_sum_ranges()
        target_sum = random.randint(sum_stats['recommended_min'], sum_stats['recommended_max'])
        
        # Aim for 2-3 odd, 2-3 even
        odd_count = random.choice([2, 3])
        even_count = 5 - odd_count
        
        # Generate numbers in different decades
        main_numbers = set()
        decades = [range(1, 11), range(11, 21), range(21, 31), range(31, 41), range(41, 51)]
        
        for decade in decades:
            if len(main_numbers) < 5:
                available = [n for n in decade if n not in main_numbers]
                if available:
                    main_numbers.add(random.choice(available))
        
        # Fill remaining spots if needed
        while len(main_numbers) < 5:
            num = random.randint(1, 50)
            main_numbers.add(num)
        
        # Generate lucky stars
        stars = set()
        while len(stars) < 2:
            stars.add(random.randint(1, 12))
        
        return list(main_numbers), list(stars)
    
    def generate_hot_ticket(self):
        # Use hot numbers from recent draws
        hot_cold = self.analyze_hot_cold_streaks()
        hot_numbers = hot_cold['hot']
        
        main_numbers = set()
        
        # Use 3-4 hot numbers
        hot_to_use = min(4, len(hot_numbers))
        main_numbers.update(random.sample(hot_numbers, hot_to_use))
        
        # Fill remaining with random numbers
        while len(main_numbers) < 5:
            num = random.randint(1, 50)
            main_numbers.add(num)
        
        # Random lucky stars
        stars = random.sample(range(1, 13), 2)
        
        return list(main_numbers), stars
    
    def generate_pattern_ticket(self):
        # Use most common number pairs
        pairs = self.analyze_number_pairs()
        
        main_numbers = set()
        
        # Use top pair
        if pairs:
            main_numbers.update(pairs[0][0])
        
        # Add more numbers ensuring good distribution
        while len(main_numbers) < 5:
            num = random.randint(1, 50)
            main_numbers.add(num)
        
        # Lucky stars based on frequency
        stars_counter = Counter(self.lucky_stars)
        popular_stars = [star for star, count in stars_counter.most_common(6)]
        stars = random.sample(popular_stars, 2)
        
        return list(main_numbers), stars
    
    def generate_overdue_ticket(self):
        # Use overdue numbers
        latest_date = max(draw['date'] for draw in self.data)
        overdue_numbers = []
        
        for num in range(1, 51):
            last_seen = None
            for draw in sorted(self.data, key=lambda x: x['date'], reverse=True):
                if num in draw['main_numbers']:
                    last_seen = draw['date']
                    break
            
            if last_seen:
                days_overdue = (latest_date - last_seen).days
                if days_overdue > 30:  # Consider overdue if not seen in 30+ days
                    overdue_numbers.append(num)
        
        main_numbers = set()
        
        # Use 2-3 overdue numbers
        if overdue_numbers:
            overdue_to_use = min(3, len(overdue_numbers))
            main_numbers.update(random.sample(overdue_numbers, overdue_to_use))
        
        # Fill remaining
        while len(main_numbers) < 5:
            num = random.randint(1, 50)
            main_numbers.add(num)
        
        # Random lucky stars
        stars = random.sample(range(1, 13), 2)
        
        return list(main_numbers), stars
    
    def generate_hybrid_ticket(self):
        # Combine multiple strategies
        main_numbers = set()
        
        # Add one hot number
        hot_cold = self.analyze_hot_cold_streaks()
        if hot_cold['hot']:
            main_numbers.add(random.choice(hot_cold['hot']))
        
        # Add one from top pair
        pairs = self.analyze_number_pairs()
        if pairs:
            main_numbers.add(random.choice(pairs[0][0]))
        
        # Add one overdue number (if available)
        latest_date = max(draw['date'] for draw in self.data)
        overdue_candidates = []
        for num in range(1, 51):
            if num in main_numbers:
                continue
            last_seen = None
            for draw in sorted(self.data, key=lambda x: x['date'], reverse=True):
                if num in draw['main_numbers']:
                    last_seen = draw['date']
                    break
            if last_seen and (latest_date - last_seen).days > 20:
                overdue_candidates.append(num)
        
        if overdue_candidates:
            main_numbers.add(random.choice(overdue_candidates))
        
        # Fill remaining with balanced selection
        while len(main_numbers) < 5:
            num = random.randint(1, 50)
            main_numbers.add(num)
        
        # Lucky stars - one frequent, one less frequent
        stars_counter = Counter(self.lucky_stars)
        frequent_stars = [s for s, c in stars_counter.most_common(6)]
        less_frequent_stars = [s for s, c in stars_counter.most_common()[-6:]]
        
        stars = []
        if frequent_stars:
            stars.append(random.choice(frequent_stars))
        if less_frequent_stars and len(stars) < 2:
            candidates = [s for s in less_frequent_stars if s not in stars]
            if candidates:
                stars.append(random.choice(candidates))
        
        while len(stars) < 2:
            star = random.randint(1, 12)
            if star not in stars:
                stars.append(star)
        
        return list(main_numbers), stars
    
    def load_saved_numbers(self):
        try:
            if os.path.exists(self.saved_numbers_file):
                with open(self.saved_numbers_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print("Error loading saved numbers: {}".format(e))
            return {}
    
    def save_saved_numbers(self):
        try:
            with open(self.saved_numbers_file, 'w') as f:
                json.dump(self.saved_numbers, f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", "Failed to save numbers: {}".format(str(e)))
    
    def save_number_set(self):
        try:
            name = self.save_name_entry.get().strip()
            main_input = self.save_main_entry.get().strip()
            stars_input = self.save_stars_entry.get().strip()
            
            if not name:
                messagebox.showwarning("Invalid Input", "Please enter a name for this set!")
                return
            
            if not main_input or not stars_input:
                messagebox.showwarning("Invalid Input", "Please enter both main numbers and lucky stars!")
                return
            
            # Validate numbers
            main_nums = [int(x.strip()) for x in main_input.split(',')]
            stars = [int(x.strip()) for x in stars_input.split(',')]
            
            if len(main_nums) != 5 or len(stars) != 2:
                messagebox.showwarning("Invalid Input", "Please enter exactly 5 main numbers and 2 lucky stars!")
                return
            
            if not all(1 <= num <= 50 for num in main_nums):
                messagebox.showwarning("Invalid Input", "Main numbers must be between 1 and 50!")
                return
            
            if not all(1 <= star <= 12 for star in stars):
                messagebox.showwarning("Invalid Input", "Lucky stars must be between 1 and 12!")
                return
            
            # Check for duplicates
            if name in self.saved_numbers:
                if not messagebox.askyesno("Duplicate Name", "A set with this name already exists. Overwrite?"):
                    return
            
            # Save the set
            self.saved_numbers[name] = {
                'main_numbers': sorted(main_nums),
                'lucky_stars': sorted(stars),
                'date_saved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.save_saved_numbers()
            self.refresh_saved_numbers_display()
            
            # Clear input fields
            self.save_name_entry.delete(0, tk.END)
            self.save_main_entry.delete(0, tk.END)
            self.save_stars_entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", "Number set '{}' saved successfully!".format(name))
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers separated by commas!")
        except Exception as e:
            messagebox.showerror("Error", "Failed to save number set: {}".format(str(e)))
    
    def save_current_numbers(self):
        # Pre-fill save form with current user input
        main_input = self.main_entry.get().strip()
        stars_input = self.stars_entry.get().strip()
        
        if not main_input or not stars_input:
            messagebox.showwarning("No Numbers", "Please enter numbers in the 'Your Numbers' tab first!")
            return
        
        # Switch to saved numbers tab and pre-fill
        self.notebook.select(4)  # Saved Numbers tab
        self.save_main_entry.delete(0, tk.END)
        self.save_main_entry.insert(0, main_input)
        self.save_stars_entry.delete(0, tk.END)
        self.save_stars_entry.insert(0, stars_input)
        
        # Suggest a name
        suggested_name = "Set {}".format(len(self.saved_numbers) + 1)
        self.save_name_entry.delete(0, tk.END)
        self.save_name_entry.insert(0, suggested_name)
        self.save_name_entry.select_range(0, tk.END)
    
    def refresh_saved_numbers_display(self):
        # Clear existing items
        for item in self.saved_tree.get_children():
            self.saved_tree.delete(item)
        
        # Add saved number sets
        for name, data in self.saved_numbers.items():
            main_str = ', '.join(map(str, data['main_numbers']))
            stars_str = ', '.join(map(str, data['lucky_stars']))
            date_str = data['date_saved']
            
            self.saved_tree.insert('', 'end', values=(name, main_str, stars_str, date_str))
    
    def load_selected_set(self):
        selection = self.saved_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a number set to load!")
            return
        
        item = self.saved_tree.item(selection[0])
        name = item['values'][0]
        
        if name in self.saved_numbers:
            data = self.saved_numbers[name]
            
            # Load into Your Numbers tab
            main_str = ', '.join(map(str, data['main_numbers']))
            stars_str = ', '.join(map(str, data['lucky_stars']))
            
            self.main_entry.delete(0, tk.END)
            self.main_entry.insert(0, main_str)
            self.stars_entry.delete(0, tk.END)
            self.stars_entry.insert(0, stars_str)
            
            # Switch to Your Numbers tab
            self.notebook.select(5)  # Your Numbers tab
            
            messagebox.showinfo("Loaded", "Number set '{}' loaded into Your Numbers tab!".format(name))
    
    def delete_selected_set(self):
        selection = self.saved_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a number set to delete!")
            return
        
        item = self.saved_tree.item(selection[0])
        name = item['values'][0]
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete '{}'?".format(name)):
            if name in self.saved_numbers:
                del self.saved_numbers[name]
                self.save_saved_numbers()
                self.refresh_saved_numbers_display()
                messagebox.showinfo("Deleted", "Number set '{}' deleted successfully!".format(name))
    
    def analyze_all_saved_sets(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please download lottery data first!")
            return
        
        if not self.saved_numbers:
            messagebox.showwarning("No Saved Sets", "No saved number sets to analyze!")
            return
        
        try:
            text = "ANALYSIS OF ALL SAVED NUMBER SETS\n"
            text += "=" * 60 + "\n\n"
            
            # Define win values for sorting
            win_values = {
                (5, 2): ("Jackpot", 52),
                (5, 1): ("2nd Prize", 51), 
                (5, 0): ("3rd Prize", 50),
                (4, 2): ("4th Prize", 42),
                (4, 1): ("5th Prize", 41),
                (4, 0): ("6th Prize", 40),
                (3, 2): ("7th Prize", 32),
                (2, 2): ("8th Prize", 22),
                (3, 1): ("9th Prize", 31),
                (3, 0): ("10th Prize", 30),
                (1, 2): ("11th Prize", 12),
                (2, 1): ("12th Prize", 21),
                (2, 0): ("13th Prize", 20)
            }
            
            # Analyze each set
            set_analysis = []
            main_counter = Counter(self.main_numbers)
            stars_counter = Counter(self.lucky_stars)
            
            for name, data in self.saved_numbers.items():
                main_nums = data['main_numbers']
                stars = data['lucky_stars']
                
                # Calculate wins for this set
                wins = []
                for draw in self.data:
                    main_matches = len(set(main_nums) & set(draw['main_numbers']))
                    star_matches = len(set(stars) & set(draw['lucky_stars']))
                    
                    if (main_matches, star_matches) in win_values:
                        prize_info = win_values[(main_matches, star_matches)]
                        wins.append({
                            'date': draw['date'],
                            'main_matches': main_matches,
                            'star_matches': star_matches,
                            'prize_level': prize_info[0],
                            'sort_value': prize_info[1]
                        })
                
                # Calculate statistics
                total_wins = len(wins)
                highest_win_value = max([w['sort_value'] for w in wins]) if wins else 0
                highest_win_name = next((w['prize_level'] for w in wins if w['sort_value'] == highest_win_value), "None")
                
                set_analysis.append({
                    'name': name,
                    'data': data,
                    'total_wins': total_wins,
                    'highest_win_value': highest_win_value,
                    'highest_win_name': highest_win_name,
                    'wins': wins
                })
            
            # Sort sets by most wins, then by highest win value
            set_analysis.sort(key=lambda x: (x['total_wins'], x['highest_win_value']), reverse=True)
            
            # Display top performing sets
            text += "TOP PERFORMING SETS (Most Wins):\n"
            text += "=" * 40 + "\n"
            for i, analysis in enumerate(set_analysis[:5]):
                text += "{}. {} - {} wins (Best: {})\n".format(
                    i+1, analysis['name'], analysis['total_wins'], analysis['highest_win_name']
                )
            text += "\n"
            
            # Sort by highest win value, then by total wins
            set_analysis_by_value = sorted(set_analysis, key=lambda x: (x['highest_win_value'], x['total_wins']), reverse=True)
            
            text += "HIGHEST VALUE WINS:\n"
            text += "=" * 20 + "\n"
            for i, analysis in enumerate(set_analysis_by_value[:5]):
                if analysis['highest_win_value'] > 0:
                    text += "{}. {} - {} (Total wins: {})\n".format(
                        i+1, analysis['name'], analysis['highest_win_name'], analysis['total_wins']
                    )
            text += "\n"
            
            # Detailed analysis for each set
            text += "DETAILED ANALYSIS:\n"
            text += "=" * 20 + "\n"
            
            for analysis in set_analysis:
                name = analysis['name']
                data = analysis['data']
                main_nums = data['main_numbers']
                stars = data['lucky_stars']
                wins = analysis['wins']
                
                text += "{}:\n".format(name.upper())
                text += "Numbers: {} | Stars: {}\n".format(
                    ', '.join(['{:2d}'.format(n) for n in main_nums]),
                    ', '.join(['{:2d}'.format(s) for s in stars])
                )
                
                # Quick frequency analysis
                avg_main_freq = sum(main_counter[n] for n in main_nums) / 5
                avg_stars_freq = sum(stars_counter[s] for s in stars) / 2
                
                text += "Avg frequency: Main {:.1f}, Stars {:.1f}\n".format(avg_main_freq, avg_stars_freq)
                
                # Sum and odd/even
                total_sum = sum(main_nums)
                odd_count = sum(1 for n in main_nums if n % 2 == 1)
                
                text += "Sum: {} | Odd/Even: {}/{}\n".format(total_sum, odd_count, 5 - odd_count)
                
                # Win details
                text += "Prize wins: {} | Highest: {}\n".format(
                    analysis['total_wins'], analysis['highest_win_name']
                )
                
                # Show recent wins (last 3)
                if wins:
                    recent_wins = sorted(wins, key=lambda x: x['date'], reverse=True)[:3]
                    text += "Recent wins: "
                    win_strings = []
                    for win in recent_wins:
                        win_strings.append("{} ({})".format(
                            win['prize_level'], win['date'].strftime('%Y-%m-%d')
                        ))
                    text += ", ".join(win_strings) + "\n"
                
                text += "-" * 50 + "\n\n"
            
            # Summary statistics
            text += "SUMMARY:\n"
            text += "Total saved sets: {}\n".format(len(self.saved_numbers))
            
            # Most common numbers across all sets
            all_saved_mains = []
            all_saved_stars = []
            for data in self.saved_numbers.values():
                all_saved_mains.extend(data['main_numbers'])
                all_saved_stars.extend(data['lucky_stars'])
            
            if all_saved_mains:
                saved_main_counter = Counter(all_saved_mains)
                saved_stars_counter = Counter(all_saved_stars)
                
                text += "Most used main numbers: {}\n".format(
                    ', '.join([str(n) for n, c in saved_main_counter.most_common(10)])
                )
                text += "Most used lucky stars: {}\n".format(
                    ', '.join([str(s) for s, c in saved_stars_counter.most_common(6)])
                )
            
            # Overall win statistics
            total_wins_all_sets = sum(analysis['total_wins'] for analysis in set_analysis)
            if total_wins_all_sets > 0:
                text += "Total wins across all sets: {}\n".format(total_wins_all_sets)
                avg_wins_per_set = total_wins_all_sets / len(set_analysis)
                text += "Average wins per set: {:.1f}\n".format(avg_wins_per_set)
            
            self.saved_analysis_text.delete(1.0, tk.END)
            self.saved_analysis_text.insert(1.0, text)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", "Failed to analyze saved sets: {}".format(str(e)))
    
    def analyze_user_numbers(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please download data first!")
            return
        
        try:
            # Parse user input
            main_input = self.main_entry.get().strip()
            stars_input = self.stars_entry.get().strip()
            
            if not main_input or not stars_input:
                messagebox.showwarning("Invalid Input", "Please enter both main numbers and lucky stars!")
                return
            
            user_main = [int(x.strip()) for x in main_input.split(',')]
            user_stars = [int(x.strip()) for x in stars_input.split(',')]
            
            if len(user_main) != 5 or len(user_stars) != 2:
                messagebox.showwarning("Invalid Input", "Please enter exactly 5 main numbers and 2 lucky stars!")
                return
            
            if not all(1 <= num <= 50 for num in user_main):
                messagebox.showwarning("Invalid Input", "Main numbers must be between 1 and 50!")
                return
            
            if not all(1 <= star <= 12 for star in user_stars):
                messagebox.showwarning("Invalid Input", "Lucky stars must be between 1 and 12!")
                return
            
            # Analyze user numbers
            results = self.get_user_number_analysis(user_main, user_stars)
            
            self.user_results_text.delete(1.0, tk.END)
            self.user_results_text.insert(1.0, results)
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers separated by commas!")
    
    def get_user_number_analysis(self, user_main, user_stars):
        main_counter = Counter(self.main_numbers)
        stars_counter = Counter(self.lucky_stars)
        
        text = "ANALYSIS FOR YOUR NUMBERS\n"
        text += "Main: {}\n".format(', '.join(map(str, user_main)))
        text += "Stars: {}\n".format(', '.join(map(str, user_stars)))
        text += "=" * 50 + "\n\n"
        
        # Frequency analysis
        text += "FREQUENCY ANALYSIS:\n"
        text += "-" * 20 + "\n"
        text += "Main Numbers:\n"
        for num in user_main:
            count = main_counter[num]
            text += "  Number {:2d}: drawn {:3d} times\n".format(num, count)
        
        text += "\nLucky Stars:\n"
        for star in user_stars:
            count = stars_counter[star]
            text += "  Star {:2d}: drawn {:3d} times\n".format(star, count)
        
        # Last appearance analysis
        text += "\nLAST APPEARANCE:\n"
        text += "-" * 20 + "\n"
        latest_date = max(draw['date'] for draw in self.data)
        
        text += "Main Numbers:\n"
        for num in user_main:
            last_seen = None
            for draw in sorted(self.data, key=lambda x: x['date'], reverse=True):
                if num in draw['main_numbers']:
                    last_seen = draw['date']
                    break
            
            if last_seen:
                days_ago = (latest_date - last_seen).days
                text += "  Number {:2d}: {} ({} days ago)\n".format(num, last_seen.strftime('%Y-%m-%d'), days_ago)
            else:
                text += "  Number {:2d}: Never drawn\n".format(num)
        
        text += "\nLucky Stars:\n"
        for star in user_stars:
            last_seen = None
            for draw in sorted(self.data, key=lambda x: x['date'], reverse=True):
                if star in draw['lucky_stars']:
                    last_seen = draw['date']
                    break
            
            if last_seen:
                days_ago = (latest_date - last_seen).days
                text += "  Star {:2d}: {} ({} days ago)\n".format(star, last_seen.strftime('%Y-%m-%d'), days_ago)
            else:
                text += "  Star {:2d}: Never drawn\n".format(star)
        
        # Historical wins
        text += "\nHISTORICAL WINS:\n"
        text += "-" * 20 + "\n"
        wins = []
        
        # Define win values based on EuroMillions prize structure
        win_values = {
            (5, 2): "Jackpot",
            (5, 1): "2nd Prize", 
            (5, 0): "3rd Prize",
            (4, 2): "4th Prize",
            (4, 1): "5th Prize",
            (4, 0): "6th Prize",
            (3, 2): "7th Prize",
            (2, 2): "8th Prize",
            (3, 1): "9th Prize",
            (3, 0): "10th Prize",
            (1, 2): "11th Prize",
            (2, 1): "12th Prize",
            (2, 0): "13th Prize"
        }
        
        for draw in self.data:
            main_matches = len(set(user_main) & set(draw['main_numbers']))
            star_matches = len(set(user_stars) & set(draw['lucky_stars']))
            
            # Only count actual prize wins (2+ main or 1+ main with 1+ star)
            if (main_matches, star_matches) in win_values:
                wins.append({
                    'date': draw['date'],
                    'main_matches': main_matches,
                    'star_matches': star_matches,
                    'draw': draw,
                    'prize_level': win_values[(main_matches, star_matches)],
                    'sort_value': main_matches * 10 + star_matches  # For sorting by win value
                })
        
        if wins:
            # Sort by win value (highest first), then by date (most recent first)
            wins.sort(key=lambda x: (x['sort_value'], x['date']), reverse=True)
            text += "Found {} historical prize wins:\n\n".format(len(wins))
            
            for win in wins:
                text += "{}: {} ({} main + {} stars) ".format(
                    win['date'].strftime('%Y-%m-%d'), 
                    win['prize_level'],
                    win['main_matches'], 
                    win['star_matches']
                )
                text += "({} | ".format(', '.join(map(str, win['draw']['main_numbers'])))
                text += "{})\n".format(', '.join(map(str, win['draw']['lucky_stars'])))
        else:
            text += "No historical prize wins found with these numbers.\n"
        
        return text
    
    def analyze_historical_winners(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please download data first!")
            return
        
        try:
            text = "HISTORICAL WINNING COMBINATIONS ANALYSIS\n"
            text += "=" * 60 + "\n\n"
            
            # Define prize structure
            prize_levels = {
                (5, 2): ("Jackpot", 100),
                (5, 1): ("2nd Prize", 80), 
                (5, 0): ("3rd Prize", 60),
                (4, 2): ("4th Prize", 40),
                (4, 1): ("5th Prize", 30),
                (4, 0): ("6th Prize", 20),
                (3, 2): ("7th Prize", 15),
                (2, 2): ("8th Prize", 10),
                (3, 1): ("9th Prize", 8),
                (3, 0): ("10th Prize", 6),
                (1, 2): ("11th Prize", 4),
                (2, 1): ("12th Prize", 3),
                (2, 0): ("13th Prize", 1)
            }
            
            # Analyze all combinations that would have won prizes if played consistently
            combination_analysis = {}
            
            text += "Analyzing {} historical draws for winning patterns...\n\n".format(len(self.data))
            
            # For computational efficiency, we'll analyze a sample of popular number combinations
            # and check how they would have performed historically
            
            # Generate test combinations based on most frequent numbers
            main_counter = Counter(self.main_numbers)
            stars_counter = Counter(self.lucky_stars)
            
            most_frequent_mains = [num for num, count in main_counter.most_common(20)]
            most_frequent_stars = [star for star, count in stars_counter.most_common(8)]
            
            # Test various combinations
            test_combinations = []
            
            # Top frequency combinations
            from itertools import combinations
            for main_combo in combinations(most_frequent_mains[:15], 5):
                for star_combo in combinations(most_frequent_stars[:6], 2):
                    test_combinations.append((sorted(main_combo), sorted(star_combo)))
            
            # Add some balanced combinations (mix of frequent and less frequent)
            less_frequent_mains = [num for num, count in main_counter.most_common()[-20:]]
            for main_combo in combinations(most_frequent_mains[:10] + less_frequent_mains[:10], 5):
                for star_combo in combinations(most_frequent_stars[:4] + [star for star, count in stars_counter.most_common()[-4:]], 2):
                    test_combinations.append((sorted(main_combo), sorted(star_combo)))
                    if len(test_combinations) >= 1000:  # Limit for performance
                        break
                if len(test_combinations) >= 1000:
                    break
            
            # Analyze each combination
            for main_nums, stars in test_combinations[:500]:  # Analyze top 500 combinations
                total_wins = 0
                total_value = 0
                highest_prize = ""
                highest_value = 0
                wins_detail = []
                
                for draw in self.data:
                    main_matches = len(set(main_nums) & set(draw['main_numbers']))
                    star_matches = len(set(stars) & set(draw['lucky_stars']))
                    
                    if (main_matches, star_matches) in prize_levels:
                        prize_name, prize_value = prize_levels[(main_matches, star_matches)]
                        total_wins += 1
                        total_value += prize_value
                        wins_detail.append((draw['date'], prize_name, main_matches, star_matches))
                        
                        if prize_value > highest_value:
                            highest_value = prize_value
                            highest_prize = prize_name
                
                if total_wins > 0:
                    combination_key = (tuple(main_nums), tuple(stars))
                    combination_analysis[combination_key] = {
                        'total_wins': total_wins,
                        'total_value': total_value,
                        'highest_prize': highest_prize,
                        'highest_value': highest_value,
                        'wins_detail': wins_detail,
                        'avg_value': total_value / total_wins if total_wins > 0 else 0
                    }
            
            # Sort by different criteria
            by_total_value = sorted(combination_analysis.items(), key=lambda x: x[1]['total_value'], reverse=True)
            by_total_wins = sorted(combination_analysis.items(), key=lambda x: x[1]['total_wins'], reverse=True)
            by_highest_prize = sorted(combination_analysis.items(), key=lambda x: x[1]['highest_value'], reverse=True)
            
            # Display results
            text += "TOP COMBINATIONS BY TOTAL WIN VALUE:\n"
            text += "=" * 40 + "\n"
            for i, (combo, stats) in enumerate(by_total_value[:10]):
                main_nums, stars = combo
                text += "{}. {} | {} - {} wins, value: {}, best: {}\n".format(
                    i+1, 
                    ', '.join(map(str, main_nums)),
                    ', '.join(map(str, stars)),
                    stats['total_wins'],
                    stats['total_value'],
                    stats['highest_prize']
                )
            
            text += "\nTOP COMBINATIONS BY TOTAL WINS:\n"
            text += "=" * 35 + "\n"
            for i, (combo, stats) in enumerate(by_total_wins[:10]):
                main_nums, stars = combo
                text += "{}. {} | {} - {} wins, avg value: {:.1f}\n".format(
                    i+1,
                    ', '.join(map(str, main_nums)),
                    ', '.join(map(str, stars)),
                    stats['total_wins'],
                    stats['avg_value']
                )
            
            text += "\nHIGHEST INDIVIDUAL PRIZES:\n"
            text += "=" * 30 + "\n"
            for i, (combo, stats) in enumerate(by_highest_prize[:10]):
                main_nums, stars = combo
                text += "{}. {} | {} - Best: {} ({} total wins)\n".format(
                    i+1,
                    ', '.join(map(str, main_nums)),
                    ', '.join(map(str, stars)),
                    stats['highest_prize'],
                    stats['total_wins']
                )
            
            # Show details for top performer
            if by_total_value:
                text += "\nDETAILS FOR TOP PERFORMING COMBINATION:\n"
                text += "=" * 45 + "\n"
                top_combo, top_stats = by_total_value[0]
                main_nums, stars = top_combo
                text += "Numbers: {} | Stars: {}\n".format(
                    ', '.join(map(str, main_nums)), ', '.join(map(str, stars))
                )
                text += "Total wins: {} | Total value: {} | Best prize: {}\n".format(
                    top_stats['total_wins'], top_stats['total_value'], top_stats['highest_prize']
                )
                
                # Show recent wins
                recent_wins = sorted(top_stats['wins_detail'], key=lambda x: x[0], reverse=True)[:10]
                text += "\nRecent wins:\n"
                for date, prize, main_m, star_m in recent_wins:
                    text += "  {}: {} ({} main + {} stars)\n".format(
                        date.strftime('%Y-%m-%d'), prize, main_m, star_m
                    )
            
            text += "\nSTATISTICS:\n"
            text += "=" * 15 + "\n"
            text += "Combinations analyzed: {}\n".format(len(test_combinations))
            text += "Winning combinations found: {}\n".format(len(combination_analysis))
            if combination_analysis:
                avg_wins = sum(stats['total_wins'] for stats in combination_analysis.values()) / len(combination_analysis)
                text += "Average wins per winning combination: {:.1f}\n".format(avg_wins)
            
            self.winners_results_text.delete(1.0, tk.END)
            self.winners_results_text.insert(1.0, text)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", "Failed to analyze winners: {}".format(str(e)))
    
    def analyze_jackpot_winners(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please download data first!")
            return
        
        try:
            text = "JACKPOT WINNING COMBINATIONS\n"
            text += "=" * 40 + "\n\n"
            
            jackpot_draws = []
            for draw in self.data:
                # Jackpot = all 5 main numbers + 2 lucky stars
                jackpot_draws.append({
                    'date': draw['date'],
                    'main_numbers': draw['main_numbers'],
                    'lucky_stars': draw['lucky_stars']
                })
            
            text += "Total jackpot winning combinations: {}\n\n".format(len(jackpot_draws))
            
            # Analyze patterns in jackpot wins
            all_jackpot_mains = []
            all_jackpot_stars = []
            
            for draw in jackpot_draws:
                all_jackpot_mains.extend(draw['main_numbers'])
                all_jackpot_stars.extend(draw['lucky_stars'])
            
            main_counter = Counter(all_jackpot_mains)
            stars_counter = Counter(all_jackpot_stars)
            
            text += "MOST FREQUENT NUMBERS IN JACKPOT WINS:\n"
            text += "-" * 40 + "\n"
            text += "Main numbers:\n"
            for num, count in main_counter.most_common(15):
                percentage = (count / len(jackpot_draws)) * 100
                text += "  {:2d}: {} times ({:.1f}%)\n".format(num, count, percentage)
            
            text += "\nLucky stars:\n"
            for star, count in stars_counter.most_common(8):
                percentage = (count / len(jackpot_draws)) * 100
                text += "  {:2d}: {} times ({:.1f}%)\n".format(star, count, percentage)
            
            # Show recent jackpot wins
            text += "\nRECENT JACKPOT COMBINATIONS:\n"
            text += "-" * 30 + "\n"
            recent_jackpots = sorted(jackpot_draws, key=lambda x: x['date'], reverse=True)[:20]
            
            for draw in recent_jackpots:
                text += "{}: {} | {}\n".format(
                    draw['date'].strftime('%Y-%m-%d'),
                    ', '.join(['{:2d}'.format(n) for n in draw['main_numbers']]),
                    ', '.join(['{:2d}'.format(s) for s in draw['lucky_stars']])
                )
            
            # Analyze patterns
            text += "\nJACKPOT PATTERN ANALYSIS:\n"
            text += "-" * 25 + "\n"
            
            # Odd/Even analysis
            odd_even_patterns = []
            for draw in jackpot_draws:
                odd_count = sum(1 for n in draw['main_numbers'] if n % 2 == 1)
                odd_even_patterns.append(odd_count)
            
            odd_even_counter = Counter(odd_even_patterns)
            text += "Odd/Even distribution in jackpots:\n"
            for odd_count in sorted(odd_even_counter.keys()):
                even_count = 5 - odd_count
                percentage = (odd_even_counter[odd_count] / len(jackpot_draws)) * 100
                text += "  {} odd, {} even: {} times ({:.1f}%)\n".format(
                    odd_count, even_count, odd_even_counter[odd_count], percentage
                )
            
            # Sum analysis
            sums = [sum(draw['main_numbers']) for draw in jackpot_draws]
            text += "\nSum statistics:\n"
            text += "  Average sum: {:.1f}\n".format(sum(sums) / len(sums))
            text += "  Min sum: {}, Max sum: {}\n".format(min(sums), max(sums))
            
            self.winners_results_text.delete(1.0, tk.END)
            self.winners_results_text.insert(1.0, text)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", "Failed to analyze jackpots: {}".format(str(e)))
    
    def analyze_top_prize_winners(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please download data first!")
            return
        
        try:
            text = "TOP 3 PRIZE LEVELS ANALYSIS\n"
            text += "=" * 35 + "\n\n"
            
            # Jackpot, 2nd Prize, 3rd Prize combinations
            top_prizes = []
            
            for draw in self.data:
                main_nums = draw['main_numbers']
                stars = draw['lucky_stars']
                
                # These are the actual winning combinations for top 3 prizes
                top_prizes.append({
                    'date': draw['date'],
                    'main_numbers': main_nums,
                    'lucky_stars': stars,
                    'prize_level': 'Jackpot'  # All draws are jackpot combinations
                })
            
            text += "ANALYSIS OF TOP PRIZE WINNING NUMBERS:\n"
            text += "=" * 40 + "\n"
            text += "Total top prize combinations: {}\n\n".format(len(top_prizes))
            
            # Frequency analysis
            all_mains = []
            all_stars = []
            for prize in top_prizes:
                all_mains.extend(prize['main_numbers'])
                all_stars.extend(prize['lucky_stars'])
            
            main_counter = Counter(all_mains)
            stars_counter = Counter(all_stars)
            
            text += "HOTTEST NUMBERS IN TOP PRIZES:\n"
            text += "-" * 30 + "\n"
            text += "Main numbers (most frequent):\n"
            for num, count in main_counter.most_common(10):
                percentage = (count / len(top_prizes)) * 100
                text += "  {:2d}: appeared {} times ({:.1f}% of top wins)\n".format(num, count, percentage)
            
            text += "\nLucky stars (most frequent):\n"
            for star, count in stars_counter.most_common(6):
                percentage = (count / len(top_prizes)) * 100
                text += "  {:2d}: appeared {} times ({:.1f}% of top wins)\n".format(star, count, percentage)
            
            text += "\nCOOLEST NUMBERS IN TOP PRIZES:\n"
            text += "-" * 30 + "\n"
            text += "Main numbers (least frequent):\n"
            for num, count in main_counter.most_common()[-10:]:
                percentage = (count / len(top_prizes)) * 100
                text += "  {:2d}: appeared {} times ({:.1f}% of top wins)\n".format(num, count, percentage)
            
            text += "\nLucky stars (least frequent):\n"
            for star, count in stars_counter.most_common()[-6:]:
                percentage = (count / len(top_prizes)) * 100
                text += "  {:2d}: appeared {} times ({:.1f}% of top wins)\n".format(star, count, percentage)
            
            # Decade analysis
            text += "\nNUMBER RANGE ANALYSIS:\n"
            text += "-" * 20 + "\n"
            decades = {
                '1-10': (1, 10),
                '11-20': (11, 20), 
                '21-30': (21, 30),
                '31-40': (31, 40),
                '41-50': (41, 50)
            }
            
            for decade_name, (start, end) in decades.items():
                count = sum(1 for num in all_mains if start <= num <= end)
                percentage = (count / len(all_mains)) * 100
                text += "  {}: {} numbers ({:.1f}%)\n".format(decade_name, count, percentage)
            
            # Recent patterns
            text += "\nRECENT TOP PRIZE PATTERNS (Last 20):\n"
            text += "-" * 35 + "\n"
            recent_prizes = sorted(top_prizes, key=lambda x: x['date'], reverse=True)[:20]
            
            for prize in recent_prizes:
                text += "{}: {} | {}\n".format(
                    prize['date'].strftime('%Y-%m-%d'),
                    ', '.join(['{:2d}'.format(n) for n in sorted(prize['main_numbers'])]),
                    ', '.join(['{:2d}'.format(s) for s in sorted(prize['lucky_stars'])])
                )
            
            # Generate recommended combinations based on top prize patterns
            text += "\nRECOMMENDED COMBINATIONS (Based on Top Prize Patterns):\n"
            text += "-" * 55 + "\n"
            
            # Get most successful numbers
            top_mains = [num for num, count in main_counter.most_common(15)]
            top_stars = [star for star, count in stars_counter.most_common(6)]
            
            import random
            random.seed(42)  # For reproducible results
            
            text += "Hot number combinations:\n"
            for i in range(3):
                selected_mains = sorted(random.sample(top_mains[:12], 5))
                selected_stars = sorted(random.sample(top_stars[:4], 2))
                text += "  {}: {} | {}\n".format(
                    i+1,
                    ', '.join(['{:2d}'.format(n) for n in selected_mains]),
                    ', '.join(['{:2d}'.format(s) for s in selected_stars])
                )
            
            self.winners_results_text.delete(1.0, tk.END)
            self.winners_results_text.insert(1.0, text)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", "Failed to analyze top prizes: {}".format(str(e)))
    
    def analyze_duplicate_jackpots(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please download data first!")
            return
        
        try:
            text = "DUPLICATE JACKPOT COMBINATIONS ANALYSIS\n"
            text += "=" * 50 + "\n\n"
            
            # Group all draws by their number combinations
            combination_groups = {}
            
            for draw in self.data:
                # Create a unique key for each combination (sorted numbers + sorted stars)
                main_key = tuple(sorted(draw['main_numbers']))
                stars_key = tuple(sorted(draw['lucky_stars']))
                combo_key = (main_key, stars_key)
                
                if combo_key not in combination_groups:
                    combination_groups[combo_key] = []
                
                combination_groups[combo_key].append(draw)
            
            # Find combinations that appeared more than once
            duplicate_combinations = {k: v for k, v in combination_groups.items() if len(v) > 1}
            
            if duplicate_combinations:
                text += f"FOUND {len(duplicate_combinations)} DUPLICATE JACKPOT COMBINATIONS!\n"
                text += "=" * 55 + "\n\n"
                
                # Sort by number of occurrences (most frequent first)
                sorted_duplicates = sorted(duplicate_combinations.items(), 
                                         key=lambda x: len(x[1]), reverse=True)
                
                for i, (combo_key, draws) in enumerate(sorted_duplicates):
                    main_nums, stars = combo_key
                    text += f"{i+1}. COMBINATION: {', '.join(map(str, main_nums))} | {', '.join(map(str, stars))}\n"
                    text += f"   Appeared {len(draws)} times:\n"
                    
                    # Show all dates this combination won
                    for j, draw in enumerate(sorted(draws, key=lambda x: x['date'])):
                        text += f"   • {draw['date'].strftime('%Y-%m-%d (%A)')}\n"
                    
                    # Calculate time between occurrences
                    if len(draws) >= 2:
                        sorted_draws = sorted(draws, key=lambda x: x['date'])
                        text += f"   Time between wins:\n"
                        for k in range(len(sorted_draws) - 1):
                            days_diff = (sorted_draws[k+1]['date'] - sorted_draws[k]['date']).days
                            years = days_diff // 365
                            remaining_days = days_diff % 365
                            if years > 0:
                                text += f"   • {days_diff} days ({years} years, {remaining_days} days)\n"
                            else:
                                text += f"   • {days_diff} days\n"
                    
                    text += "\n" + "-" * 60 + "\n\n"
                
                # Statistics about duplicates
                text += "DUPLICATE STATISTICS:\n"
                text += "=" * 25 + "\n"
                
                total_duplicate_occurrences = sum(len(draws) for draws in duplicate_combinations.values())
                text += f"Total duplicate occurrences: {total_duplicate_occurrences}\n"
                text += f"Percentage of all draws that are duplicates: {(total_duplicate_occurrences / len(self.data)) * 100:.2f}%\n"
                
                # Most frequent duplicate
                most_frequent = max(duplicate_combinations.items(), key=lambda x: len(x[1]))
                main_nums, stars = most_frequent[0]
                text += f"Most frequent combination: {', '.join(map(str, main_nums))} | {', '.join(map(str, stars))} ({len(most_frequent[1])} times)\n"
                
                # Average time between duplicates
                all_gaps = []
                for draws in duplicate_combinations.values():
                    if len(draws) >= 2:
                        sorted_draws = sorted(draws, key=lambda x: x['date'])
                        for i in range(len(sorted_draws) - 1):
                            gap = (sorted_draws[i+1]['date'] - sorted_draws[i]['date']).days
                            all_gaps.append(gap)
                
                if all_gaps:
                    avg_gap = sum(all_gaps) / len(all_gaps)
                    text += f"Average time between duplicate wins: {avg_gap:.0f} days ({avg_gap/365:.1f} years)\n"
                    text += f"Shortest gap: {min(all_gaps)} days\n"
                    text += f"Longest gap: {max(all_gaps)} days ({max(all_gaps)/365:.1f} years)\n"
                
                # Pattern analysis of duplicates
                text += "\nPATTERN ANALYSIS OF DUPLICATES:\n"
                text += "-" * 35 + "\n"
                
                # Analyze number frequency in duplicates
                duplicate_mains = []
                duplicate_stars = []
                for (main_nums, stars), draws in duplicate_combinations.items():
                    # Weight by number of occurrences
                    for _ in range(len(draws)):
                        duplicate_mains.extend(main_nums)
                        duplicate_stars.extend(stars)
                
                main_counter = Counter(duplicate_mains)
                stars_counter = Counter(duplicate_stars)
                
                text += "Most common numbers in duplicate jackpots:\n"
                text += "Main numbers: {}\n".format(
                    ', '.join([str(num) for num, count in main_counter.most_common(10)])
                )
                text += "Lucky stars: {}\n".format(
                    ', '.join([str(star) for star, count in stars_counter.most_common(6)])
                )
                
                # Odd/even analysis
                odd_even_patterns = []
                for (main_nums, stars), draws in duplicate_combinations.items():
                    odd_count = sum(1 for num in main_nums if num % 2 == 1)
                    odd_even_patterns.extend([odd_count] * len(draws))
                
                odd_even_counter = Counter(odd_even_patterns)
                text += f"\nOdd/Even distribution in duplicates:\n"
                for odd_count in sorted(odd_even_counter.keys()):
                    even_count = 5 - odd_count
                    percentage = (odd_even_counter[odd_count] / len(odd_even_patterns)) * 100
                    text += f"  {odd_count} odd, {even_count} even: {odd_even_counter[odd_count]} times ({percentage:.1f}%)\n"
                
            else:
                text += "NO DUPLICATE JACKPOT COMBINATIONS FOUND!\n"
                text += "=" * 40 + "\n\n"
                text += "Every single jackpot draw in the EuroMillions history has been unique.\n"
                text += f"Total draws analyzed: {len(self.data)}\n"
                text += f"All {len(self.data)} combinations are completely different!\n\n"
                text += "This demonstrates the astronomical odds of the EuroMillions lottery:\n"
                text += f"• Odds of winning jackpot: 1 in 139,838,160\n"
                text += f"• With {len(self.data)} draws, we've only seen {len(self.data)/139838160*100:.6f}% of all possible combinations\n"
                text += f"• Statistical probability of seeing a duplicate by now: {(1 - ((139838159/139838160)**len(self.data)))*100:.4f}%\n"
            
            # Show some interesting statistics regardless
            text += "\nINTERESTING FACTS:\n"
            text += "=" * 20 + "\n"
            text += f"Total possible EuroMillions combinations: 139,838,160\n"
            text += f"Combinations drawn so far: {len(self.data)}\n"
            text += f"Percentage of all possibilities used: {(len(self.data)/139838160)*100:.6f}%\n"
            text += f"Remaining possible combinations: {139838160 - len(self.data):,}\n"
            
            self.winners_results_text.delete(1.0, tk.END)
            self.winners_results_text.insert(1.0, text)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", "Failed to analyze duplicate jackpots: {}".format(str(e)))
    
    def analyze_chi_square(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please download data first!")
            return
        
        try:
            text = "CHI-SQUARE GOODNESS OF FIT TEST\n"
            text += "=" * 40 + "\n\n"
            text += "Tests if number frequencies deviate significantly from expected uniform distribution.\n"
            text += "This can detect physical biases in ball selection.\n\n"
            
            # Calculate chi-square for main numbers
            main_counter = Counter(self.main_numbers)
            expected_frequency = len(self.data) * 5 / 50  # Expected draws per number
            
            chi_square_main = 0
            text += "MAIN NUMBERS (1-50):\n"
            text += "-" * 25 + "\n"
            text += f"Expected frequency per number: {expected_frequency:.2f}\n"
            text += f"Total observations: {len(self.main_numbers)}\n\n"
            
            significant_deviations = []
            for num in range(1, 51):
                observed = main_counter.get(num, 0)
                deviation = (observed - expected_frequency) ** 2 / expected_frequency
                chi_square_main += deviation
                
                # Flag significant deviations (>2 standard deviations)
                z_score = (observed - expected_frequency) / (expected_frequency ** 0.5)
                if abs(z_score) > 2:
                    significant_deviations.append((num, observed, z_score))
            
            # Calculate p-value approximation
            degrees_freedom = 49  # 50 numbers - 1
            text += f"Chi-square statistic: {chi_square_main:.3f}\n"
            text += f"Degrees of freedom: {degrees_freedom}\n"
            
            # Critical values for chi-square distribution
            critical_values = {
                0.05: 66.339,  # 5% significance
                0.01: 76.154,  # 1% significance
                0.001: 88.379  # 0.1% significance
            }
            
            significant = False
            for alpha, critical in critical_values.items():
                if chi_square_main > critical:
                    text += f"SIGNIFICANT at α = {alpha} (critical value: {critical:.3f})\n"
                    significant = True
                    break
            
            if not significant:
                text += "NOT SIGNIFICANT - distribution appears random\n"
            
            # Show significant deviations
            if significant_deviations:
                text += f"\nSIGNIFICANT DEVIATIONS (|z| > 2):\n"
                text += "-" * 35 + "\n"
                for num, observed, z_score in significant_deviations:
                    bias_type = "OVER-REPRESENTED" if z_score > 0 else "UNDER-REPRESENTED"
                    text += f"Number {num:2d}: {observed:3d} times (z={z_score:+.2f}) - {bias_type}\n"
            
            # Lucky stars analysis
            stars_counter = Counter(self.lucky_stars)
            expected_frequency_stars = len(self.data) * 2 / 12
            
            chi_square_stars = 0
            text += f"\n\nLUCKY STARS (1-12):\n"
            text += "-" * 20 + "\n"
            text += f"Expected frequency per star: {expected_frequency_stars:.2f}\n"
            
            star_deviations = []
            for star in range(1, 13):
                observed = stars_counter.get(star, 0)
                deviation = (observed - expected_frequency_stars) ** 2 / expected_frequency_stars
                chi_square_stars += deviation
                
                z_score = (observed - expected_frequency_stars) / (expected_frequency_stars ** 0.5)
                if abs(z_score) > 2:
                    star_deviations.append((star, observed, z_score))
            
            degrees_freedom_stars = 11
            text += f"Chi-square statistic: {chi_square_stars:.3f}\n"
            text += f"Degrees of freedom: {degrees_freedom_stars}\n"
            
            # Critical values for stars
            star_critical_values = {
                0.05: 19.675,
                0.01: 24.725,
                0.001: 31.264
            }
            
            star_significant = False
            for alpha, critical in star_critical_values.items():
                if chi_square_stars > critical:
                    text += f"SIGNIFICANT at α = {alpha} (critical value: {critical:.3f})\n"
                    star_significant = True
                    break
            
            if not star_significant:
                text += "NOT SIGNIFICANT - distribution appears random\n"
            
            if star_deviations:
                text += f"\nSIGNIFICANT STAR DEVIATIONS:\n"
                text += "-" * 25 + "\n"
                for star, observed, z_score in star_deviations:
                    bias_type = "OVER-REPRESENTED" if z_score > 0 else "UNDER-REPRESENTED"
                    text += f"Star {star:2d}: {observed:3d} times (z={z_score:+.2f}) - {bias_type}\n"
            
            # Interpretation
            text += f"\n\nINTERPRETATION:\n"
            text += "=" * 15 + "\n"
            if significant or star_significant:
                text += "⚠️  POTENTIAL BIAS DETECTED!\n\n"
                text += "This could indicate:\n"
                text += "• Physical ball irregularities\n"
                text += "• Machine mechanical bias\n"
                text += "• Manufacturing defects\n"
                text += "• Statistical anomaly (false positive)\n\n"
                text += "Professional recommendation:\n"
                text += "• Monitor these numbers in future draws\n"
                text += "• Consider slight betting adjustments\n"
                text += "• Verify with additional statistical tests\n"
            else:
                text += "✅ NO SIGNIFICANT BIAS DETECTED\n\n"
                text += "The lottery appears to be operating fairly with\n"
                text += "proper random distribution. Any patterns observed\n"
                text += "are likely due to natural statistical variation.\n"
            
            self.bias_results_text.delete(1.0, tk.END)
            self.bias_results_text.insert(1.0, text)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to perform chi-square test: {str(e)}")
    
    def analyze_coefficient_variation(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please download data first!")
            return
        
        try:
            text = "COEFFICIENT OF VARIATION ANALYSIS\n"
            text += "=" * 40 + "\n\n"
            text += "Measures relative variability in number frequencies.\n"
            text += "CV = (Standard Deviation / Mean) × 100\n"
            text += "Lower CV = more uniform (less bias)\n"
            text += "Higher CV = more variation (potential bias)\n\n"
            
            # Main numbers analysis
            main_counter = Counter(self.main_numbers)
            frequencies = [main_counter.get(i, 0) for i in range(1, 51)]
            
            mean_freq = sum(frequencies) / len(frequencies)
            variance = sum((f - mean_freq) ** 2 for f in frequencies) / len(frequencies)
            std_dev = variance ** 0.5
            cv_main = (std_dev / mean_freq) * 100
            
            text += f"MAIN NUMBERS (1-50):\n"
            text += "-" * 25 + "\n"
            text += f"Mean frequency: {mean_freq:.2f}\n"
            text += f"Standard deviation: {std_dev:.2f}\n"
            text += f"Coefficient of Variation: {cv_main:.2f}%\n"
            
            # Expected CV for truly random distribution
            expected_std = (mean_freq) ** 0.5  # Poisson approximation
            expected_cv = (expected_std / mean_freq) * 100
            text += f"Expected CV (random): {expected_cv:.2f}%\n"
            
            cv_ratio = cv_main / expected_cv
            text += f"CV Ratio (observed/expected): {cv_ratio:.3f}\n"
            
            if cv_ratio > 1.2:
                text += "⚠️  HIGHER than expected - possible bias\n"
            elif cv_ratio < 0.8:
                text += "⚠️  LOWER than expected - unusually uniform\n"
            else:
                text += "✅ Within expected range\n"
            
            # Lucky stars analysis
            stars_counter = Counter(self.lucky_stars)
            star_frequencies = [stars_counter.get(i, 0) for i in range(1, 13)]
            
            star_mean = sum(star_frequencies) / len(star_frequencies)
            star_variance = sum((f - star_mean) ** 2 for f in star_frequencies) / len(star_frequencies)
            star_std = star_variance ** 0.5
            cv_stars = (star_std / star_mean) * 100
            
            text += f"\nLUCKY STARS (1-12):\n"
            text += "-" * 20 + "\n"
            text += f"Mean frequency: {star_mean:.2f}\n"
            text += f"Standard deviation: {star_std:.2f}\n"
            text += f"Coefficient of Variation: {cv_stars:.2f}%\n"
            
            expected_star_std = (star_mean) ** 0.5
            expected_star_cv = (expected_star_std / star_mean) * 100
            text += f"Expected CV (random): {expected_star_cv:.2f}%\n"
            
            star_cv_ratio = cv_stars / expected_star_cv
            text += f"CV Ratio: {star_cv_ratio:.3f}\n"
            
            if star_cv_ratio > 1.2:
                text += "⚠️  HIGHER than expected - possible bias\n"
            elif star_cv_ratio < 0.8:
                text += "⚠️  LOWER than expected - unusually uniform\n"
            else:
                text += "✅ Within expected range\n"
            
            # Detailed frequency distribution
            text += f"\nDETAILED FREQUENCY DISTRIBUTION:\n"
            text += "=" * 35 + "\n"
            
            # Sort by frequency for main numbers
            sorted_mains = sorted([(main_counter.get(i, 0), i) for i in range(1, 51)], reverse=True)
            
            text += "Main numbers (most to least frequent):\n"
            for i, (freq, num) in enumerate(sorted_mains[:10]):
                deviation = freq - mean_freq
                text += f"{i+1:2d}. Number {num:2d}: {freq:3d} times ({deviation:+.1f})\n"
            
            text += "...\n"
            
            for i, (freq, num) in enumerate(sorted_mains[-5:]):
                deviation = freq - mean_freq
                text += f"{46+i:2d}. Number {num:2d}: {freq:3d} times ({deviation:+.1f})\n"
            
            # Professional interpretation
            text += f"\nPROFESSIONAL ANALYSIS:\n"
            text += "=" * 25 + "\n"
            
            if cv_ratio > 1.5 or star_cv_ratio > 1.5:
                text += "🔴 HIGH VARIATION DETECTED\n"
                text += "• Significant deviation from randomness\n"
                text += "• Potential equipment issues\n"
                text += "• Worth monitoring for advantage play\n"
            elif cv_ratio > 1.2 or star_cv_ratio > 1.2:
                text += "🟡 MODERATE VARIATION\n"
                text += "• Slightly higher than expected\n"
                text += "• Monitor trends over time\n"
                text += "• Possible minor equipment bias\n"
            else:
                text += "🟢 NORMAL VARIATION\n"
                text += "• Equipment appears to be functioning properly\n"
                text += "• No detectable bias for advantage play\n"
                text += "• Results consistent with fair random draws\n"
            
            self.bias_results_text.delete(1.0, tk.END)
            self.bias_results_text.insert(1.0, text)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze coefficient of variation: {str(e)}")
    
    def analyze_temporal_bias(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please download data first!")
            return
        
        try:
            text = "TEMPORAL BIAS ANALYSIS\n"
            text += "=" * 30 + "\n\n"
            text += "Analyzes if certain numbers appear more frequently\n"
            text += "in recent draws vs. historical averages.\n"
            text += "This can detect equipment degradation or ball wear.\n\n"
            
            # Split data into time periods
            total_draws = len(self.data)
            recent_draws = self.data[-100:] if total_draws >= 200 else self.data[-total_draws//2:]
            historical_draws = self.data[:-len(recent_draws)]
            
            text += f"Analysis periods:\n"
            text += f"• Historical: {len(historical_draws)} draws\n"
            text += f"• Recent: {len(recent_draws)} draws\n\n"
            
            # Historical frequencies
            historical_mains = []
            for draw in historical_draws:
                historical_mains.extend(draw['main_numbers'])
            historical_counter = Counter(historical_mains)
            
            # Recent frequencies  
            recent_mains = []
            for draw in recent_draws:
                recent_mains.extend(draw['main_numbers'])
            recent_counter = Counter(recent_mains)
            
            # Expected frequencies
            historical_expected = len(historical_mains) / 50
            recent_expected = len(recent_mains) / 50
            
            text += f"MAIN NUMBERS TEMPORAL ANALYSIS:\n"
            text += "-" * 35 + "\n"
            text += f"Historical expected per number: {historical_expected:.2f}\n"
            text += f"Recent expected per number: {recent_expected:.2f}\n\n"
            
            # Find numbers with significant temporal changes
            temporal_changes = []
            for num in range(1, 51):
                hist_freq = historical_counter.get(num, 0)
                recent_freq = recent_counter.get(num, 0)
                
                # Calculate relative change
                hist_rate = hist_freq / len(historical_draws) if len(historical_draws) > 0 else 0
                recent_rate = recent_freq / len(recent_draws) if len(recent_draws) > 0 else 0
                
                if hist_rate > 0:
                    change_ratio = recent_rate / hist_rate
                    change_percent = (change_ratio - 1) * 100
                    
                    # Flag significant changes (>50% increase/decrease)
                    if abs(change_percent) > 50 and recent_freq >= 3:  # Must have some recent activity
                        temporal_changes.append((num, hist_freq, recent_freq, change_percent))
            
            if temporal_changes:
                # Sort by magnitude of change
                temporal_changes.sort(key=lambda x: abs(x[3]), reverse=True)
                
                text += f"SIGNIFICANT TEMPORAL CHANGES:\n"
                text += "-" * 30 + "\n"
                for num, hist, recent, change in temporal_changes[:15]:
                    trend = "↗️ INCREASING" if change > 0 else "↘️ DECREASING"
                    text += f"Number {num:2d}: {hist:2d}→{recent:2d} ({change:+.1f}%) {trend}\n"
                
                # Analyze patterns
                increasing = [x for x in temporal_changes if x[3] > 50]
                decreasing = [x for x in temporal_changes if x[3] < -50]
                
                text += f"\nPATTERN ANALYSIS:\n"
                text += f"• Numbers increasing in frequency: {len(increasing)}\n"
                text += f"• Numbers decreasing in frequency: {len(decreasing)}\n"
                
                if len(increasing) > 3:
                    text += f"\n🔴 EQUIPMENT ALERT: Multiple numbers showing increased frequency\n"
                    text += f"Possible causes: Ball wear, machine calibration drift\n"
                    
                    hot_numbers = [x[0] for x in increasing[:5]]
                    text += f"Consider monitoring: {hot_numbers}\n"
                
            else:
                text += "✅ NO SIGNIFICANT TEMPORAL CHANGES DETECTED\n"
                text += "Number frequencies remain stable over time.\n"
            
            # Day of week analysis
            text += f"\n\nDAY-OF-WEEK BIAS ANALYSIS:\n"
            text += "-" * 30 + "\n"
            
            tuesday_draws = [d for d in self.data if d['date'].weekday() == 1]  # Tuesday
            friday_draws = [d for d in self.data if d['date'].weekday() == 4]   # Friday
            
            text += f"Tuesday draws: {len(tuesday_draws)}\n"
            text += f"Friday draws: {len(friday_draws)}\n"
            
            if len(tuesday_draws) > 0 and len(friday_draws) > 0:
                # Compare average sums
                tuesday_sums = [sum(d['main_numbers']) for d in tuesday_draws]
                friday_sums = [sum(d['main_numbers']) for d in friday_draws]
                
                tue_avg = sum(tuesday_sums) / len(tuesday_sums)
                fri_avg = sum(friday_sums) / len(friday_sums)
                
                text += f"Average sum Tuesday: {tue_avg:.2f}\n"
                text += f"Average sum Friday: {fri_avg:.2f}\n"
                text += f"Difference: {abs(tue_avg - fri_avg):.2f}\n"
                
                if abs(tue_avg - fri_avg) > 5:
                    text += "⚠️  Significant day-of-week difference detected\n"
                else:
                    text += "✅ No significant day-of-week bias\n"
            
            self.bias_results_text.delete(1.0, tk.END)
            self.bias_results_text.insert(1.0, text)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze temporal bias: {str(e)}")
    
    def analyze_autocorrelation(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please download data first!")
            return
        
        try:
            text = "AUTOCORRELATION ANALYSIS\n"
            text += "=" * 30 + "\n\n"
            text += "Tests if numbers in consecutive draws are correlated.\n"
            text += "Strong correlation suggests mechanical memory effects\n"
            text += "or non-random behavior in the drawing process.\n\n"
            
            # Prepare sequences for analysis
            sequences = []
            for i in range(len(self.data) - 1):
                current_draw = sorted(self.data[i]['main_numbers'])
                next_draw = sorted(self.data[i + 1]['main_numbers'])
                sequences.append((current_draw, next_draw))
            
            text += f"Analyzing {len(sequences)} consecutive draw pairs...\n\n"
            
            # Calculate autocorrelations at different lags
            def calculate_number_autocorr(lag=1):
                matches = 0
                total_comparisons = 0
                
                for i in range(len(self.data) - lag):
                    current_numbers = set(self.data[i]['main_numbers'])
                    future_numbers = set(self.data[i + lag]['main_numbers'])
                    
                    # Count overlapping numbers
                    overlap = len(current_numbers & future_numbers)
                    matches += overlap
                    total_comparisons += 1
                
                expected_overlap = 5 * 5 / 50  # Expected overlap for random draws
                actual_overlap = matches / total_comparisons if total_comparisons > 0 else 0
                
                return actual_overlap, expected_overlap
            
            # Test different lag periods
            text += "AUTOCORRELATION BY LAG:\n"
            text += "-" * 25 + "\n"
            
            significant_lags = []
            for lag in [1, 2, 3, 5, 10]:
                actual, expected = calculate_number_autocorr(lag)
                correlation = (actual - expected) / expected if expected > 0 else 0
                
                text += f"Lag {lag:2d}: {actual:.3f} overlap (expected: {expected:.3f}, "
                text += f"correlation: {correlation:+.3f})\n"
                
                if abs(correlation) > 0.1:  # Arbitrary threshold for significance
                    significant_lags.append((lag, correlation))
            
            # Analyze consecutive number patterns
            text += f"\nCONSECUTIVE NUMBER PERSISTENCE:\n"
            text += "-" * 35 + "\n"
            
            consecutive_persistence = {}
            for i in range(len(self.data) - 1):
                current_numbers = sorted(self.data[i]['main_numbers'])
                next_numbers = sorted(self.data[i + 1]['main_numbers'])
                
                # Find consecutive pairs in current draw
                current_consecutive = []
                for j in range(len(current_numbers) - 1):
                    if current_numbers[j + 1] == current_numbers[j] + 1:
                        pair = (current_numbers[j], current_numbers[j + 1])
                        current_consecutive.append(pair)
                
                # Check if these consecutive pairs appear in next draw
                for pair in current_consecutive:
                    if pair[0] in next_numbers and pair[1] in next_numbers:
                        consecutive_persistence[pair] = consecutive_persistence.get(pair, 0) + 1
            
            if consecutive_persistence:
                text += "Consecutive pairs that repeated in next draw:\n"
                for pair, count in sorted(consecutive_persistence.items(), key=lambda x: x[1], reverse=True)[:10]:
                    text += f"  {pair[0]}-{pair[1]}: {count} times\n"
            else:
                text += "No consecutive pairs repeated in immediate next draws.\n"
            
            # Sum correlation analysis
            text += f"\nSUM AUTOCORRELATION:\n"
            text += "-" * 20 + "\n"
            
            sums = [sum(draw['main_numbers']) for draw in self.data]
            
            def sum_autocorrelation(lag=1):
                if len(sums) <= lag:
                    return 0
                
                # Calculate correlation coefficient
                n = len(sums) - lag
                sum1 = sums[:-lag] if lag > 0 else sums
                sum2 = sums[lag:]
                
                mean1 = sum(sum1) / len(sum1)
                mean2 = sum(sum2) / len(sum2)
                
                numerator = sum((x - mean1) * (y - mean2) for x, y in zip(sum1, sum2))
                denom1 = sum((x - mean1) ** 2 for x in sum1) ** 0.5
                denom2 = sum((y - mean2) ** 2 for y in sum2) ** 0.5
                
                if denom1 == 0 or denom2 == 0:
                    return 0
                
                return numerator / (denom1 * denom2)
            
            for lag in [1, 2, 3, 5]:
                corr = sum_autocorrelation(lag)
                text += f"Sum lag {lag}: {corr:+.4f}\n"
                if abs(corr) > 0.1:
                    text += f"  ⚠️  Significant correlation detected!\n"
            
            # Overall assessment
            text += f"\nOVERALL ASSESSMENT:\n"
            text += "=" * 20 + "\n"
            
            if significant_lags or any(abs(sum_autocorrelation(lag)) > 0.1 for lag in [1, 2, 3]):
                text += "🔴 SIGNIFICANT AUTOCORRELATION DETECTED\n\n"
                text += "This suggests:\n"
                text += "• Non-random mechanical behavior\n"
                text += "• Possible equipment memory effects\n"
                text += "• Ball mixing insufficient between draws\n"
                text += "• Potential advantage play opportunity\n\n"
                text += "Recommendations:\n"
                text += "• Monitor patterns in real-time\n"
                text += "• Consider exploiting detected correlations\n"
                text += "• Verify findings with additional analysis\n"
            else:
                text += "✅ NO SIGNIFICANT AUTOCORRELATION\n\n"
                text += "The drawing process appears to have proper\n"
                text += "independence between consecutive draws.\n"
                text += "No mechanical memory effects detected.\n"
            
            self.bias_results_text.delete(1.0, tk.END)
            self.bias_results_text.insert(1.0, text)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze autocorrelation: {str(e)}")
    
    def analyze_ball_wear(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please download data first!")
            return
        
        try:
            text = "BALL WEAR & USAGE PATTERN ANALYSIS\n"
            text += "=" * 40 + "\n\n"
            text += "Analyzes usage patterns that might indicate physical\n"
            text += "wear effects on individual balls over time.\n\n"
            
            # Estimate ball replacement cycles (every ~6 months for EuroMillions)
            total_days = (max(d['date'] for d in self.data) - min(d['date'] for d in self.data)).days
            estimated_cycles = max(1, total_days // 180)  # Assume 6-month cycles
            
            text += f"Dataset spans: {total_days} days\n"
            text += f"Estimated ball replacement cycles: {estimated_cycles}\n"
            text += f"Average draws per cycle: {len(self.data) // estimated_cycles}\n\n"
            
            # Split data into cycles
            draws_per_cycle = len(self.data) // estimated_cycles
            cycles = []
            
            for cycle in range(estimated_cycles):
                start_idx = cycle * draws_per_cycle
                end_idx = start_idx + draws_per_cycle if cycle < estimated_cycles - 1 else len(self.data)
                cycle_data = self.data[start_idx:end_idx]
                cycles.append(cycle_data)
            
            text += f"WEAR PATTERN ANALYSIS BY CYCLE:\n"
            text += "-" * 35 + "\n"
            
            # Analyze frequency changes across cycles
            cycle_frequencies = []
            for i, cycle_data in enumerate(cycles):
                cycle_mains = []
                for draw in cycle_data:
                    cycle_mains.extend(draw['main_numbers'])
                
                cycle_counter = Counter(cycle_mains)
                cycle_frequencies.append(cycle_counter)
                
                # Calculate most/least used in this cycle
                most_used = cycle_counter.most_common(5)
                least_used = cycle_counter.most_common()[-5:]
                
                text += f"Cycle {i+1} ({len(cycle_data)} draws):\n"
                text += f"  Most used: {[f'{num}({count})' for num, count in most_used]}\n"
                text += f"  Least used: {[f'{num}({count})' for num, count in least_used]}\n"
            
            # Detect numbers showing wear patterns (declining frequency over time)
            text += f"\nWEAR DEGRADATION ANALYSIS:\n"
            text += "-" * 30 + "\n"
            
            wear_candidates = []
            
            for num in range(1, 51):
                frequencies = [counter.get(num, 0) for counter in cycle_frequencies]
                
                if len(frequencies) >= 3:  # Need at least 3 cycles
                    # Simple linear trend analysis
                    n = len(frequencies)
                    x_sum = sum(range(n))
                    y_sum = sum(frequencies)
                    xy_sum = sum(i * freq for i, freq in enumerate(frequencies))
                    x2_sum = sum(i * i for i in range(n))
                    
                    if n * x2_sum - x_sum * x_sum != 0:
                        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
                        
                        # Significant declining trend
                        if slope < -0.5 and sum(frequencies) > n:  # Must have some usage
                            wear_candidates.append((num, slope, frequencies))
            
            if wear_candidates:
                wear_candidates.sort(key=lambda x: x[1])  # Sort by slope (most declining first)
                
                text += "Numbers showing potential wear effects:\n"
                for num, slope, freqs in wear_candidates[:10]:
                    trend_desc = "DECLINING" if slope < -0.5 else "STABLE"
                    text += f"  Number {num:2d}: slope={slope:.2f} {freqs} - {trend_desc}\n"
                
                text += f"\n⚠️  {len(wear_candidates)} numbers show declining usage patterns\n"
                text += "This could indicate:\n"
                text += "• Physical wear making balls less likely to be selected\n"
                text += "• Weight changes affecting ball behavior\n"
                text += "• Surface roughness changes\n"
                
                # Numbers that might be 'fresh' (increasing usage)
                fresh_candidates = []
                for num in range(1, 51):
                    frequencies = [counter.get(num, 0) for counter in cycle_frequencies]
                    if len(frequencies) >= 3:
                        n = len(frequencies)
                        x_sum = sum(range(n))
                        y_sum = sum(frequencies)
                        xy_sum = sum(i * freq for i, freq in enumerate(frequencies))
                        x2_sum = sum(i * i for i in range(n))
                        
                        if n * x2_sum - x_sum * x_sum != 0:
                            slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
                            
                            if slope > 0.5:  # Increasing trend
                                fresh_candidates.append((num, slope, frequencies))
                
                if fresh_candidates:
                    fresh_candidates.sort(key=lambda x: x[1], reverse=True)
                    text += f"\nNumbers showing 'fresh ball' patterns:\n"
                    for num, slope, freqs in fresh_candidates[:5]:
                        text += f"  Number {num:2d}: slope={slope:.2f} {freqs} - INCREASING\n"
                
            else:
                text += "✅ No clear wear patterns detected.\n"
                text += "Ball usage appears consistent across time periods.\n"
            
            # Manufacturing batch analysis (speculative)
            text += f"\nMANUFACTURING BATCH ANALYSIS:\n"
            text += "-" * 35 + "\n"
            text += "Grouping numbers by potential manufacturing characteristics...\n\n"
            
            # Group by number ranges (might indicate production batches)
            ranges = [(1, 10), (11, 20), (21, 30), (31, 40), (41, 50)]
            range_stats = []
            
            for start, end in ranges:
                range_numbers = list(range(start, end + 1))
                total_appearances = sum(Counter(self.main_numbers).get(num, 0) for num in range_numbers)
                avg_appearances = total_appearances / len(range_numbers)
                range_stats.append((f"{start}-{end}", avg_appearances, total_appearances))
            
            expected_avg = len(self.main_numbers) / 50
            
            text += "Average appearances by number range:\n"
            for range_name, avg, total in range_stats:
                deviation = avg - expected_avg
                bias_indicator = "HIGH" if deviation > expected_avg * 0.1 else "LOW" if deviation < -expected_avg * 0.1 else "NORMAL"
                text += f"  {range_name}: {avg:.1f} avg ({total} total) - {bias_indicator}\n"
            
            # Professional recommendations
            text += f"\nPROFESSIONAL RECOMMENDATIONS:\n"
            text += "=" * 30 + "\n"
            
            if wear_candidates:
                text += "🟡 POTENTIAL EQUIPMENT BIAS DETECTED\n\n"
                text += "Strategy recommendations:\n"
                
                declining_numbers = [x[0] for x in wear_candidates[:5]]
                text += f"• AVOID (declining): {declining_numbers}\n"
                
                if fresh_candidates:
                    rising_numbers = [x[0] for x in fresh_candidates[:5]]
                    text += f"• FAVOR (rising): {rising_numbers}\n"
                
                text += f"• Monitor these patterns in future draws\n"
                text += f"• Consider slight betting weight adjustments\n"
            else:
                text += "✅ NO ACTIONABLE WEAR PATTERNS\n\n"
                text += "Equipment appears to maintain consistent\n"
                text += "performance across all time periods.\n"
            
            self.bias_results_text.delete(1.0, tk.END)
            self.bias_results_text.insert(1.0, text)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze ball wear: {str(e)}")
    
    def analyze_machine_bias(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please download data first!")
            return
        
        try:
            text = "MECHANICAL BIAS ANALYSIS\n"
            text += "=" * 30 + "\n\n"
            text += "Analyzes systematic biases that could result from\n"
            text += "mechanical imperfections in the drawing equipment.\n\n"
            
            # Position bias analysis (ball position effects)
            text += "POSITIONAL BIAS ANALYSIS:\n"
            text += "-" * 25 + "\n"
            
            # Analyze if certain numbers appear in certain positions more often
            position_counts = {i: Counter() for i in range(5)}  # 5 positions in main draw
            
            for draw in self.data:
                # Sort numbers to analyze positional bias
                sorted_numbers = sorted(draw['main_numbers'])
                for pos, number in enumerate(sorted_numbers):
                    position_counts[pos][number] += 1
            
            # Check for significant positional biases
            total_draws = len(self.data)
            expected_pos_freq = total_draws / 50  # Expected frequency per number per position
            
            significant_pos_biases = []
            
            for pos in range(5):
                text += f"Position {pos + 1} (sorted order):\n"
                most_common = position_counts[pos].most_common(5)
                least_common = position_counts[pos].most_common()[-5:]
                
                text += f"  Most common: {[(num, count) for num, count in most_common]}\n"
                text += f"  Least common: {[(num, count) for num, count in least_common]}\n"
                
                # Find numbers with > 50% deviation from expected
                for number, count in position_counts[pos].items():
                    deviation = abs(count - expected_pos_freq) / expected_pos_freq
                    if deviation > 0.5 and count > 5:  # Must have some activity
                        significant_pos_biases.append((pos + 1, number, count, deviation))
            
            if significant_pos_biases:
                text += f"\nSIGNIFICANT POSITIONAL BIASES:\n"
                significant_pos_biases.sort(key=lambda x: x[3], reverse=True)
                for pos, num, count, deviation in significant_pos_biases[:10]:
                    bias_type = "OVER" if count > expected_pos_freq else "UNDER"
                    text += f"  Position {pos}, Number {num:2d}: {count} times ({deviation:.1%} {bias_type})\n"
            
            # Mechanical sequence analysis
            text += f"\n\nMECHANICAL SEQUENCE PATTERNS:\n"
            text += "-" * 30 + "\n"
            
            # Look for numbers that frequently appear together (mechanical clustering)
            from itertools import combinations
            pair_distances = Counter()
            
            for draw in self.data:
                sorted_nums = sorted(draw['main_numbers'])
                for i, num1 in enumerate(sorted_nums):
                    for j, num2 in enumerate(sorted_nums[i+1:], i+1):
                        distance = num2 - num1
                        pair_distances[distance] += 1
            
            text += "Number distance frequency (mechanical clustering analysis):\n"
            expected_distance_freq = len(self.data) * 10 / 49  # Rough expected frequency
            
            for distance in sorted(pair_distances.keys())[:20]:
                count = pair_distances[distance]
                deviation = (count - expected_distance_freq) / expected_distance_freq if expected_distance_freq > 0 else 0
                if abs(deviation) > 0.3:  # Significant deviation
                    bias_indicator = "HIGH" if deviation > 0 else "LOW"
                    text += f"  Distance {distance:2d}: {count:3d} pairs ({deviation:+.1%}) - {bias_indicator}\n"
            
            # Draw timing analysis (if dates suggest machine maintenance patterns)
            text += f"\nMAINTENANCE CYCLE ANALYSIS:\n"
            text += "-" * 25 + "\n"
            
            # Group draws by month to look for maintenance-related patterns
            monthly_stats = {}
            for draw in self.data:
                month_key = (draw['date'].year, draw['date'].month)
                if month_key not in monthly_stats:
                    monthly_stats[month_key] = []
                monthly_stats[month_key].extend(draw['main_numbers'])
            
            # Calculate monthly averages
            monthly_averages = {}
            for month_key, numbers in monthly_stats.items():
                if len(numbers) >= 10:  # Need sufficient data
                    avg_sum = sum(numbers) / len(numbers)
                    monthly_averages[month_key] = avg_sum
            
            if len(monthly_averages) > 12:  # Need at least a year of data
                overall_avg = sum(monthly_averages.values()) / len(monthly_averages)
                
                text += f"Monthly average number analysis:\n"
                text += f"Overall average: {overall_avg:.2f}\n\n"
                
                # Find months with significant deviations
                monthly_deviations = []
                for month_key, avg in monthly_averages.items():
                    deviation = abs(avg - overall_avg)
                    if deviation > 2:  # Arbitrary threshold
                        monthly_deviations.append((month_key, avg, deviation))
                
                if monthly_deviations:
                    monthly_deviations.sort(key=lambda x: x[2], reverse=True)
                    text += "Months with unusual average numbers:\n"
                    for (year, month), avg, deviation in monthly_deviations[:6]:
                        text += f"  {year}-{month:02d}: {avg:.2f} (deviation: {deviation:.2f})\n"
                    
                    text += "\nThis could indicate:\n"
                    text += "• Seasonal maintenance schedules\n"
                    text += "• Equipment calibration cycles\n"
                    text += "• Environmental factors (temperature/humidity)\n"
                else:
                    text += "✅ No significant monthly variations detected.\n"
            
            # Sum distribution analysis (mechanical bias indicator)
            text += f"\nSUM DISTRIBUTION ANALYSIS:\n"
            text += "-" * 25 + "\n"
            
            sums = [sum(draw['main_numbers']) for draw in self.data]
            sum_counter = Counter(sums)
            
            mean_sum = sum(sums) / len(sums)
            sum_std = (sum((s - mean_sum) ** 2 for s in sums) / len(sums)) ** 0.5
            
            text += f"Sum statistics:\n"
            text += f"  Mean: {mean_sum:.2f}\n"
            text += f"  Std Dev: {sum_std:.2f}\n"
            text += f"  Range: {min(sums)} - {max(sums)}\n"
            
            # Expected normal distribution parameters for truly random draws
            # (This is complex to calculate exactly, so we use approximations)
            expected_mean = 127.5  # (1+2+...+50)/50 * 5 = 25.5 * 5
            expected_std = 29.0    # Approximate for 5 numbers from 1-50
            
            text += f"\nComparison to expected random distribution:\n"
            text += f"  Expected mean: {expected_mean}\n"
            text += f"  Expected std: {expected_std:.1f}\n"
            text += f"  Mean deviation: {abs(mean_sum - expected_mean):.2f}\n"
            text += f"  Std deviation: {abs(sum_std - expected_std):.2f}\n"
            
            # Professional assessment
            text += f"\nPROFESSIONAL ASSESSMENT:\n"
            text += "=" * 25 + "\n"
            
            bias_score = 0
            
            if significant_pos_biases:
                bias_score += len(significant_pos_biases) * 2
                text += f"🟡 Positional biases detected ({len(significant_pos_biases)} instances)\n"
            
            if abs(mean_sum - expected_mean) > 5:
                bias_score += 10
                text += f"🟡 Sum distribution deviation detected\n"
            
            if monthly_deviations:
                bias_score += len(monthly_deviations)
                text += f"🟡 Temporal maintenance patterns detected\n"
            
            text += f"\nOverall bias score: {bias_score}\n"
            
            if bias_score > 15:
                text += "🔴 SIGNIFICANT MECHANICAL BIAS DETECTED\n"
                text += "• Strong evidence of equipment irregularities\n"
                text += "• Potential advantage play opportunity\n"
                text += "• Recommend detailed monitoring and exploitation\n"
            elif bias_score > 5:
                text += "🟡 MINOR MECHANICAL IRREGULARITIES\n"
                text += "• Some evidence of equipment bias\n"
                text += "• Worth monitoring for patterns\n"
                text += "• Consider light betting adjustments\n"
            else:
                text += "✅ MECHANICAL SYSTEM APPEARS FAIR\n"
                text += "• No significant bias detected\n"
                text += "• Equipment operating within normal parameters\n"
                text += "• Random distribution maintained\n"
            
            self.bias_results_text.delete(1.0, tk.END)
            self.bias_results_text.insert(1.0, text)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze machine bias: {str(e)}")
    
    def analyze_seasonal_effects(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please download data first!")
            return
        
        try:
            text = "SEASONAL & ENVIRONMENTAL EFFECTS ANALYSIS\n"
            text += "=" * 45 + "\n\n"
            text += "Analyzes how environmental factors might affect\n"
            text += "ball behavior and drawing equipment performance.\n\n"
            
            # Seasonal grouping
            seasonal_data = {'Spring': [], 'Summer': [], 'Autumn': [], 'Winter': []}
            
            for draw in self.data:
                month = draw['date'].month
                if month in [3, 4, 5]:
                    seasonal_data['Spring'].append(draw)
                elif month in [6, 7, 8]:
                    seasonal_data['Summer'].append(draw)
                elif month in [9, 10, 11]:
                    seasonal_data['Autumn'].append(draw)
                else:  # 12, 1, 2
                    seasonal_data['Winter'].append(draw)
            
            text += "SEASONAL DISTRIBUTION:\n"
            text += "-" * 20 + "\n"
            for season, draws in seasonal_data.items():
                text += f"{season:8s}: {len(draws):4d} draws\n"
            
            text += "\nSEASONAL STATISTICAL ANALYSIS:\n"
            text += "-" * 30 + "\n"
            
            seasonal_stats = {}
            overall_numbers = []
            
            for season, draws in seasonal_data.items():
                if len(draws) > 10:  # Need sufficient data
                    season_numbers = []
                    season_sums = []
                    season_odds = 0
                    
                    for draw in draws:
                        season_numbers.extend(draw['main_numbers'])
                        season_sums.append(sum(draw['main_numbers']))
                        season_odds += sum(1 for num in draw['main_numbers'] if num % 2 == 1)
                    
                    overall_numbers.extend(season_numbers)
                    
                    avg_sum = sum(season_sums) / len(season_sums)
                    avg_odd_ratio = season_odds / (len(draws) * 5)
                    
                    # Most/least frequent numbers this season
                    season_counter = Counter(season_numbers)
                    most_frequent = season_counter.most_common(5)
                    least_frequent = season_counter.most_common()[-5:]
                    
                    seasonal_stats[season] = {
                        'avg_sum': avg_sum,
                        'avg_odd_ratio': avg_odd_ratio,
                        'most_frequent': most_frequent,
                        'least_frequent': least_frequent,
                        'total_numbers': len(season_numbers)
                    }
                    
                    text += f"{season}:\n"
                    text += f"  Average sum: {avg_sum:.2f}\n"
                    text += f"  Odd number ratio: {avg_odd_ratio:.3f}\n"
                    text += f"  Most frequent: {[f'{num}({count})' for num, count in most_frequent]}\n"
                    text += f"  Least frequent: {[f'{num}({count})' for num, count in least_frequent]}\n\n"
            
            # Environmental effect analysis
            text += "ENVIRONMENTAL BIAS DETECTION:\n"
            text += "-" * 30 + "\n"
            
            if len(seasonal_stats) >= 4:
                # Compare seasonal averages
                sum_values = [stats['avg_sum'] for stats in seasonal_stats.values()]
                odd_values = [stats['avg_odd_ratio'] for stats in seasonal_stats.values()]
                
                sum_range = max(sum_values) - min(sum_values)
                odd_range = max(odd_values) - min(odd_values)
                
                text += f"Seasonal variation ranges:\n"
                text += f"  Sum range: {sum_range:.2f}\n"
                text += f"  Odd ratio range: {odd_range:.3f}\n"
                
                # Flag significant seasonal effects
                seasonal_effects = []
                
                if sum_range > 5:
                    seasonal_effects.append("Significant sum variation between seasons")
                    
                if odd_range > 0.1:
                    seasonal_effects.append("Significant odd/even ratio variation")
                
                # Find season with most extreme values
                max_sum_season = max(seasonal_stats.items(), key=lambda x: x[1]['avg_sum'])
                min_sum_season = min(seasonal_stats.items(), key=lambda x: x[1]['avg_sum'])
                
                text += f"\nExtreme seasons:\n"
                text += f"  Highest sums: {max_sum_season[0]} ({max_sum_season[1]['avg_sum']:.2f})\n"
                text += f"  Lowest sums: {min_sum_season[0]} ({min_sum_season[1]['avg_sum']:.2f})\n"
                
                if seasonal_effects:
                    text += f"\n⚠️  SEASONAL EFFECTS DETECTED:\n"
                    for effect in seasonal_effects:
                        text += f"• {effect}\n"
                else:
                    text += f"\n✅ No significant seasonal effects detected.\n"
            
            # Temperature correlation analysis (speculative)
            text += f"\nTEMPERATURE CORRELATION ANALYSIS:\n"
            text += "-" * 35 + "\n"
            text += "Analyzing potential temperature effects on equipment...\n\n"
            
            # Group by month for finer temperature analysis
            monthly_data = {}
            for draw in self.data:
                month = draw['date'].month
                if month not in monthly_data:
                    monthly_data[month] = []
                monthly_data[month].append(sum(draw['main_numbers']))
            
            # Approximate temperature correlation (Northern hemisphere assumption)
            temp_months = {
                1: 0, 2: 2, 3: 8, 4: 15, 5: 20, 6: 25,    # Winter to Spring
                7: 28, 8: 27, 9: 22, 10: 15, 11: 8, 12: 2  # Summer to Winter
            }
            
            if len(monthly_data) >= 12:
                correlation_data = []
                for month, sums in monthly_data.items():
                    if len(sums) >= 5:  # Need sufficient data
                        avg_sum = sum(sums) / len(sums)
                        approx_temp = temp_months[month]
                        correlation_data.append((approx_temp, avg_sum))
                
                if len(correlation_data) >= 6:
                    # Simple correlation calculation
                    n = len(correlation_data)
                    temp_vals = [x[0] for x in correlation_data]
                    sum_vals = [x[1] for x in correlation_data]
                    
                    temp_mean = sum(temp_vals) / n
                    sum_mean = sum(sum_vals) / n
                    
                    numerator = sum((t - temp_mean) * (s - sum_mean) for t, s in correlation_data)
                    denom_temp = sum((t - temp_mean) ** 2 for t in temp_vals) ** 0.5
                    denom_sum = sum((s - sum_mean) ** 2 for s in sum_vals) ** 0.5
                    
                    if denom_temp > 0 and denom_sum > 0:
                        correlation = numerator / (denom_temp * denom_sum)
                        
                        text += f"Temperature-Sum correlation: {correlation:+.3f}\n"
                        
                        if abs(correlation) > 0.3:
                            effect_type = "positive" if correlation > 0 else "negative"
                            text += f"⚠️  Moderate {effect_type} temperature correlation detected!\n"
                            text += f"This suggests:\n"
                            text += f"• Air density effects on ball behavior\n"
                            text += f"• Thermal expansion of equipment\n"
                            text += f"• Humidity correlation effects\n"
                        else:
                            text += f"✅ No significant temperature correlation.\n"
            
            # Holiday effects analysis
            text += f"\nHOLIDAY & SPECIAL DATE ANALYSIS:\n"
            text += "-" * 35 + "\n"
            
            # Check draws around major holidays (Christmas, New Year, etc.)
            holiday_periods = []
            special_draws = []
            
            for draw in self.data:
                month = draw['date'].month
                day = draw['date'].day
                
                # Christmas/New Year period
                if (month == 12 and day >= 20) or (month == 1 and day <= 10):
                    holiday_periods.append(draw)
                
                # Check for special dates (could be maintenance periods)
                if month == 1 and day == 1:  # New Year's Day
                    special_draws.append(("New Year", draw))
                elif month == 12 and day == 25:  # Christmas
                    special_draws.append(("Christmas", draw))
            
            text += f"Holiday period draws: {len(holiday_periods)}\n"
            text += f"Special date draws: {len(special_draws)}\n"
            
            if len(holiday_periods) > 10:
                holiday_sums = [sum(draw['main_numbers']) for draw in holiday_periods]
                regular_sums = [sum(draw['main_numbers']) for draw in self.data if draw not in holiday_periods]
                
                holiday_avg = sum(holiday_sums) / len(holiday_sums)
                regular_avg = sum(regular_sums) / len(regular_sums)
                
                text += f"Holiday period average sum: {holiday_avg:.2f}\n"
                text += f"Regular period average sum: {regular_avg:.2f}\n"
                text += f"Difference: {abs(holiday_avg - regular_avg):.2f}\n"
                
                if abs(holiday_avg - regular_avg) > 3:
                    text += f"⚠️  Significant holiday effect detected!\n"
                    text += f"Possible causes:\n"
                    text += f"• Reduced maintenance during holidays\n"
                    text += f"• Different staff operating equipment\n"
                    text += f"• Environmental changes (heating/cooling)\n"
            
            # Professional recommendations
            text += f"\nPROFESSIONAL STRATEGY RECOMMENDATIONS:\n"
            text += "=" * 40 + "\n"
            
            if seasonal_effects or abs(correlation) > 0.3 if 'correlation' in locals() else False:
                text += f"🟡 ENVIRONMENTAL EFFECTS DETECTED\n\n"
                
                # Seasonal strategy
                current_month = datetime.now().month
                current_season = None
                if current_month in [3, 4, 5]:
                    current_season = 'Spring'
                elif current_month in [6, 7, 8]:
                    current_season = 'Summer'
                elif current_month in [9, 10, 11]:
                    current_season = 'Autumn'
                else:
                    current_season = 'Winter'
                
                if current_season in seasonal_stats:
                    current_stats = seasonal_stats[current_season]
                    text += f"Current season ({current_season}) strategy:\n"
                    
                    if current_stats['avg_sum'] > 130:
                        text += f"• Favor higher numbers (season tends toward high sums)\n"
                    elif current_stats['avg_sum'] < 125:
                        text += f"• Favor lower numbers (season tends toward low sums)\n"
                    
                    if current_stats['avg_odd_ratio'] > 0.52:
                        text += f"• Slightly favor odd numbers this season\n"
                    elif current_stats['avg_odd_ratio'] < 0.48:
                        text += f"• Slightly favor even numbers this season\n"
                    
                    # Seasonal hot numbers
                    seasonal_hot = [num for num, count in current_stats['most_frequent']]
                    text += f"• Consider seasonal hot numbers: {seasonal_hot}\n"
                
            else:
                text += f"✅ NO SIGNIFICANT ENVIRONMENTAL BIAS\n\n"
                text += f"Environmental factors do not appear to\n"
                text += f"significantly affect the lottery equipment.\n"
                text += f"Stick to mathematical strategies.\n"
            
            from datetime import datetime
            
            self.bias_results_text.delete(1.0, tk.END)
            self.bias_results_text.insert(1.0, text)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze seasonal effects: {str(e)}")
    
    def detect_anomalies(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please download data first!")
            return
        
        try:
            text = "COMPREHENSIVE ANOMALY DETECTION\n"
            text += "=" * 40 + "\n\n"
            text += "Advanced statistical analysis to detect any\n"
            text += "unusual patterns or systematic biases.\n\n"
            
            # Multi-dimensional anomaly detection
            anomalies_detected = []
            
            # 1. Frequency anomaly detection
            text += "1. FREQUENCY ANOMALY DETECTION:\n"
            text += "-" * 35 + "\n"
            
            main_counter = Counter(self.main_numbers)
            expected_freq = len(self.main_numbers) / 50
            
            frequency_anomalies = []
            for num in range(1, 51):
                observed = main_counter.get(num, 0)
                # Z-score for frequency
                z_score = (observed - expected_freq) / (expected_freq ** 0.5)
                if abs(z_score) > 3:  # 3-sigma rule
                    frequency_anomalies.append((num, observed, z_score))
            
            if frequency_anomalies:
                text += f"Extreme frequency deviations (|z| > 3):\n"
                for num, obs, z in frequency_anomalies:
                    direction = "OVER" if z > 0 else "UNDER"
                    text += f"  Number {num:2d}: {obs} times (z={z:+.2f}) - {direction}\n"
                anomalies_detected.append("Frequency")
            else:
                text += "✅ No extreme frequency anomalies detected.\n"
            
            # 2. Sequential anomaly detection
            text += f"\n2. SEQUENTIAL PATTERN ANOMALIES:\n"
            text += "-" * 35 + "\n"
            
            # Look for impossible or highly improbable sequences
            sequential_anomalies = []
            
            for i, draw in enumerate(self.data):
                sorted_nums = sorted(draw['main_numbers'])
                
                # Check for perfect sequences (e.g., 1,2,3,4,5)
                is_consecutive = all(sorted_nums[j+1] == sorted_nums[j] + 1 for j in range(4))
                if is_consecutive:
                    sequential_anomalies.append(("Perfect consecutive", i, draw['date'], sorted_nums))
                
                # Check for arithmetic progressions
                if len(set(sorted_nums[j+1] - sorted_nums[j] for j in range(4))) == 1:
                    diff = sorted_nums[1] - sorted_nums[0]
                    if diff > 1:  # Already caught consecutive above
                        sequential_anomalies.append(("Arithmetic progression", i, draw['date'], sorted_nums))
                
                # Check for repeated digits patterns
                digit_pattern = ''.join(str(num)[-1] for num in sorted_nums)
                if len(set(digit_pattern)) == 1:  # All end in same digit
                    sequential_anomalies.append(("Same last digit", i, draw['date'], sorted_nums))
            
            if sequential_anomalies:
                text += f"Sequential pattern anomalies found:\n"
                for pattern_type, draw_idx, date, numbers in sequential_anomalies:
                    text += f"  {date.strftime('%Y-%m-%d')}: {numbers} - {pattern_type}\n"
                anomalies_detected.append("Sequential")
            else:
                text += "✅ No sequential anomalies detected.\n"
            
            # 3. Statistical distribution anomalies
            text += f"\n3. DISTRIBUTION ANOMALIES:\n"
            text += "-" * 25 + "\n"
            
            sums = [sum(draw['main_numbers']) for draw in self.data]
            
            # Kolmogorov-Smirnov-like test for normality
            mean_sum = sum(sums) / len(sums)
            sum_variance = sum((s - mean_sum) ** 2 for s in sums) / len(sums)
            sum_std = sum_variance ** 0.5
            
            # Check for distribution shape anomalies
            skewness_sum = sum((s - mean_sum) ** 3 for s in sums) / (len(sums) * sum_std ** 3)
            kurtosis_sum = sum((s - mean_sum) ** 4 for s in sums) / (len(sums) * sum_std ** 4) - 3
            
            text += f"Sum distribution analysis:\n"
            text += f"  Mean: {mean_sum:.2f}\n"
            text += f"  Std Dev: {sum_std:.2f}\n"
            text += f"  Skewness: {skewness_sum:.3f}\n"
            text += f"  Kurtosis: {kurtosis_sum:.3f}\n"
            
            distribution_anomalies = []
            if abs(skewness_sum) > 0.5:
                distribution_anomalies.append(f"High skewness ({skewness_sum:.3f})")
            if abs(kurtosis_sum) > 1.0:
                distribution_anomalies.append(f"High kurtosis ({kurtosis_sum:.3f})")
            
            if distribution_anomalies:
                text += f"Distribution anomalies:\n"
                for anomaly in distribution_anomalies:
                    text += f"  • {anomaly}\n"
                anomalies_detected.append("Distribution")
            else:
                text += "✅ Distribution appears normal.\n"
            
            # 4. Temporal clustering anomalies
            text += f"\n4. TEMPORAL CLUSTERING ANALYSIS:\n"
            text += "-" * 35 + "\n"
            
            # Look for numbers that cluster in time
            recent_window = 50  # Last 50 draws
            if len(self.data) >= recent_window:
                recent_draws = self.data[-recent_window:]
                recent_numbers = []
                for draw in recent_draws:
                    recent_numbers.extend(draw['main_numbers'])
                
                recent_counter = Counter(recent_numbers)
                expected_recent = recent_window * 5 / 50  # Expected appearances in recent window
                
                temporal_clusters = []
                for num, count in recent_counter.items():
                    if count > expected_recent * 2:  # More than double expected
                        temporal_clusters.append((num, count, expected_recent))
                
                if temporal_clusters:
                    text += f"Recent temporal clustering (last {recent_window} draws):\n"
                    for num, count, expected in temporal_clusters:
                        text += f"  Number {num:2d}: {count} times (expected: {expected:.1f})\n"
                    anomalies_detected.append("Temporal Clustering")
                else:
                    text += "✅ No significant temporal clustering.\n"
            
            # 5. Cross-correlation anomalies
            text += f"\n5. CROSS-CORRELATION ANOMALIES:\n"
            text += "-" * 35 + "\n"
            
            # Look for numbers that appear together more often than chance
            from itertools import combinations
            pair_counter = Counter()
            for draw in self.data:
                pairs = list(combinations(sorted(draw['main_numbers']), 2))
                pair_counter.update(pairs)
            
            expected_pair_freq = len(self.data) * (5 * 4 / 2) / (50 * 49 / 2)  # Expected pair frequency
            
            correlation_anomalies = []
            for pair, count in pair_counter.most_common(20):
                if count > expected_pair_freq * 3:  # More than 3x expected
                    correlation_anomalies.append((pair, count, expected_pair_freq))
            
            if correlation_anomalies:
                text += f"Highly correlated number pairs:\n"
                for pair, count, expected in correlation_anomalies:
                    text += f"  {pair[0]}-{pair[1]}: {count} times (expected: {expected:.1f})\n"
                anomalies_detected.append("Cross-correlation")
            else:
                text += "✅ No unusual number correlations.\n"
            
            # 6. Equipment signature detection
            text += f"\n6. EQUIPMENT SIGNATURE DETECTION:\n"
            text += "-" * 35 + "\n"
            
            # Look for mechanical signatures in the data
            signatures = []
            
            # Signature 1: Consistent sum bias over time
            window_size = 100
            if len(self.data) >= window_size * 2:
                windows = []
                for i in range(0, len(self.data) - window_size, window_size // 2):
                    window_data = self.data[i:i + window_size]
                    window_sums = [sum(draw['main_numbers']) for draw in window_data]
                    window_avg = sum(window_sums) / len(window_sums)
                    windows.append(window_avg)
                
                # Check for consistent drift
                if len(windows) > 4:
                    linear_trend = sum((i - len(windows)/2) * (avg - sum(windows)/len(windows)) 
                                     for i, avg in enumerate(windows))
                    
                    if abs(linear_trend) > 50:  # Arbitrary threshold
                        signatures.append(f"Linear sum trend detected (strength: {linear_trend:.1f})")
            
            # Signature 2: Mechanical position preference
            position_variance = []
            for pos in range(5):
                pos_numbers = []
                for draw in self.data:
                    sorted_nums = sorted(draw['main_numbers'])
                    pos_numbers.append(sorted_nums[pos])
                
                pos_mean = sum(pos_numbers) / len(pos_numbers)
                pos_var = sum((n - pos_mean) ** 2 for n in pos_numbers) / len(pos_numbers)
                position_variance.append(pos_var)
            
            # Check if some positions have unusually low variance (mechanical preference)
            avg_variance = sum(position_variance) / len(position_variance)
            for pos, var in enumerate(position_variance):
                if var < avg_variance * 0.7:  # Significantly lower variance
                    signatures.append(f"Position {pos+1} shows mechanical preference (low variance)")
            
            if signatures:
                text += f"Equipment signatures detected:\n"
                for signature in signatures:
                    text += f"  • {signature}\n"
                anomalies_detected.append("Equipment Signature")
            else:
                text += "✅ No equipment signatures detected.\n"
            
            # FINAL ASSESSMENT
            text += f"\n" + "=" * 50 + "\n"
            text += f"COMPREHENSIVE ANOMALY ASSESSMENT\n"
            text += f"=" * 50 + "\n\n"
            
            if anomalies_detected:
                text += f"🔴 ANOMALIES DETECTED: {len(anomalies_detected)} categories\n\n"
                text += f"Anomaly categories found:\n"
                for i, anomaly_type in enumerate(anomalies_detected, 1):
                    text += f"{i}. {anomaly_type}\n"
                
                text += f"\n🎯 ADVANTAGE PLAY RECOMMENDATIONS:\n"
                text += f"=" * 35 + "\n"
                
                if "Frequency" in anomalies_detected:
                    extreme_over = [x[0] for x in frequency_anomalies if x[2] > 3]
                    extreme_under = [x[0] for x in frequency_anomalies if x[2] < -3]
                    if extreme_over:
                        text += f"• FAVOR (over-performing): {extreme_over}\n"
                    if extreme_under:
                        text += f"• AVOID (under-performing): {extreme_under}\n"
                
                if "Temporal Clustering" in anomalies_detected:
                    hot_clusters = [x[0] for x in temporal_clusters]
                    text += f"• CURRENT HOT CLUSTER: {hot_clusters}\n"
                
                if "Cross-correlation" in anomalies_detected:
                    top_pairs = [f"{pair[0]}-{pair[1]}" for pair, count, expected in correlation_anomalies[:3]]
                    text += f"• PAIR TOGETHER: {top_pairs}\n"
                
                text += f"\n⚠️  CONFIDENCE LEVEL: "
                confidence = len(anomalies_detected) * 15  # Rough confidence score
                if confidence > 70:
                    text += f"HIGH ({confidence}%) - Strong evidence of exploitable bias\n"
                elif confidence > 40:
                    text += f"MEDIUM ({confidence}%) - Moderate evidence, proceed with caution\n"
                else:
                    text += f"LOW ({confidence}%) - Weak evidence, may be statistical noise\n"
                
            else:
                text += f"✅ NO SIGNIFICANT ANOMALIES DETECTED\n\n"
                text += f"The EuroMillions lottery appears to be operating\n"
                text += f"with proper randomness and fairness. All statistical\n"
                text += f"tests indicate normal behavior within expected\n"
                text += f"parameters for a truly random drawing system.\n\n"
                text += f"RECOMMENDATION: Stick to mathematical strategies\n"
                text += f"rather than attempting to exploit non-existent biases.\n"
            
            self.bias_results_text.delete(1.0, tk.END)
            self.bias_results_text.insert(1.0, text)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to detect anomalies: {str(e)}")

def main():
    root = tk.Tk()
    app = EuroMillionsAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()