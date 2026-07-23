import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from backend.logger import logger

class LogDataView(tk.Frame):
    """
    Log Data View: Forms for daily health vitals and exercise activities.
    Provides selectable activity dropdowns, standard metric defaults, and auto-loads existing user records.
    """
    def __init__(self, parent, db, refresh_callback=None):
        super().__init__(parent, bg="#f6f8f5")
        self.db = db
        self.refresh_callback = refresh_callback
        self.build_ui()
        self.load_data_for_selected_date()

    def build_ui(self):
        # Header
        header_frame = tk.Frame(self, bg="#f6f8f5")
        header_frame.pack(fill="x", padx=30, pady=(25, 10))

        sub_label = tk.Label(header_frame, text="DAILY ENTRY", font=("Segoe UI", 9, "bold"), 
                             fg="#136349", bg="#f6f8f5")
        sub_label.pack(anchor="w")

        title_label = tk.Label(header_frame, text="Log Data", font=("Georgia", 24, "bold"), 
                               fg="#1a201c", bg="#f6f8f5")
        title_label.pack(anchor="w")

        # Main Form Container (2 Column layout)
        content_frame = tk.Frame(self, bg="#f6f8f5")
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)

        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)

        # --- LEFT PANEL: LOG DAILY VITALS ---
        vitals_card = tk.Frame(content_frame, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=25, pady=20)
        vitals_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        tk.Label(vitals_card, text="RECORD DAILY VITALS", font=("Segoe UI", 10, "bold"), fg="#1a201c", bg="#ffffff").pack(anchor="w", pady=(0, 5))
        tk.Label(vitals_card, text="Adjust or save your daily health vitals for the selected date.", font=("Segoe UI", 8), fg="#718096", bg="#ffffff").pack(anchor="w", pady=(0, 12))

        # Date Entry with Auto-load binding
        tk.Label(vitals_card, text="Date (YYYY-MM-DD)", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.date_entry = ttk.Entry(vitals_card, font=("Segoe UI", 10))
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.date_entry.pack(fill="x", pady=(2, 10))
        self.date_entry.bind("<FocusOut>", lambda e: self.load_data_for_selected_date())
        self.date_entry.bind("<Return>", lambda e: self.load_data_for_selected_date())

        # Weight
        tk.Label(vitals_card, text="Weight (kg)", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.weight_entry = ttk.Entry(vitals_card, font=("Segoe UI", 10))
        self.weight_entry.pack(fill="x", pady=(2, 10))

        # Sleep Hours
        tk.Label(vitals_card, text="Sleep Duration (hours)", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.sleep_entry = ttk.Entry(vitals_card, font=("Segoe UI", 10))
        self.sleep_entry.pack(fill="x", pady=(2, 10))

        # Water Intake
        tk.Label(vitals_card, text="Water Intake (ml)", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.water_entry = ttk.Entry(vitals_card, font=("Segoe UI", 10))
        self.water_entry.pack(fill="x", pady=(2, 10))

        # Calories Consumed
        tk.Label(vitals_card, text="Calories Consumed (kcal)", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.calories_entry = ttk.Entry(vitals_card, font=("Segoe UI", 10))
        self.calories_entry.pack(fill="x", pady=(2, 15))

        btn_row_v = tk.Frame(vitals_card, bg="#ffffff")
        btn_row_v.pack(fill="x")

        btn_save_vitals = tk.Button(btn_row_v, text="Save Daily Vitals", font=("Segoe UI", 10, "bold"), 
                                    fg="#ffffff", bg="#136349", activebackground="#0f4d39", activeforeground="#ffffff", 
                                    relief="flat", pady=8, cursor="hand2", command=self.save_vitals)
        btn_save_vitals.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_clear_vitals = tk.Button(btn_row_v, text="Reset Defaults", font=("Segoe UI", 9, "bold"),
                                     fg="#4a5568", bg="#edf2f7", activebackground="#cbd5e0", activeforeground="#1a201c",
                                     relief="flat", pady=8, padx=12, cursor="hand2", command=self.reset_default_vitals)
        btn_clear_vitals.pack(side="right")

        # --- RIGHT PANEL: LOG EXERCISE SESSION ---
        workout_card = tk.Frame(content_frame, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=25, pady=20)
        workout_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        tk.Label(workout_card, text="TRACK EXERCISE / ACTIVITY", font=("Segoe UI", 10, "bold"), fg="#1a201c", bg="#ffffff").pack(anchor="w", pady=(0, 5))
        tk.Label(workout_card, text="Select your exercise activity from the dropdown and specify duration.", font=("Segoe UI", 8), fg="#718096", bg="#ffffff").pack(anchor="w", pady=(0, 12))

        # Activity Type Dropdown (User selects their choice)
        tk.Label(workout_card, text="Select Activity Type", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.activity_combo = ttk.Combobox(workout_card, values=[
            "-- Select Activity --", "Brisk Walk", "Running", "Cycling", "Swimming", 
            "Yoga", "Strength Training", "Cardio", "Pilates", "HIIT"
        ], font=("Segoe UI", 10), state="readonly")
        self.activity_combo.set("-- Select Activity --")
        self.activity_combo.pack(fill="x", pady=(2, 10))

        # Duration
        tk.Label(workout_card, text="Duration (minutes)", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.duration_entry = ttk.Entry(workout_card, font=("Segoe UI", 10))
        self.duration_entry.insert(0, "30")
        self.duration_entry.pack(fill="x", pady=(2, 10))

        # Calories Burned
        tk.Label(workout_card, text="Calories Burned (kcal)", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.ex_cal_entry = ttk.Entry(workout_card, font=("Segoe UI", 10))
        self.ex_cal_entry.insert(0, "180")
        self.ex_cal_entry.pack(fill="x", pady=(2, 10))

        # Notes
        tk.Label(workout_card, text="Session Notes (optional)", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.notes_entry = ttk.Entry(workout_card, font=("Segoe UI", 10))
        self.notes_entry.pack(fill="x", pady=(2, 15))

        btn_save_workout = tk.Button(workout_card, text="Log Workout", font=("Segoe UI", 10, "bold"), 
                                     fg="#ffffff", bg="#136349", activebackground="#0f4d39", activeforeground="#ffffff", 
                                     relief="flat", pady=8, cursor="hand2", command=self.save_workout)
        btn_save_workout.pack(fill="x")

    def load_data_for_selected_date(self):
        """Populates active user's saved data if present for date, or populates standard default baselines."""
        target_date = self.date_entry.get().strip()
        metrics = self.db.get_all_metrics()
        
        matched = None
        for m in metrics:
            if m.date == target_date:
                matched = m
                break

        self.clear_vitals_form()
        if matched:
            self.weight_entry.insert(0, str(matched.weight_kg) if matched.weight_kg > 0 else "65.0")
            self.sleep_entry.insert(0, str(matched.sleep_hours) if matched.sleep_hours > 0 else "7.5")
            self.water_entry.insert(0, str(int(matched.water_ml)) if matched.water_ml > 0 else "2000")
            self.calories_entry.insert(0, str(int(matched.calories_consumed)) if matched.calories_consumed > 0 else "2000")
        else:
            # Baseline default values if no record logged yet for selected date
            self.reset_default_vitals()

    def reset_default_vitals(self):
        self.clear_vitals_form()
        metrics = self.db.get_all_metrics()
        latest = metrics[-1] if metrics else None
        
        w_def = str(latest.weight_kg) if latest and latest.weight_kg > 0 else "65.0"
        s_def = str(latest.sleep_hours) if latest and latest.sleep_hours > 0 else "7.5"
        wt_def = str(int(latest.water_ml)) if latest and latest.water_ml > 0 else "2000"
        c_def = str(int(latest.calories_consumed)) if latest and latest.calories_consumed > 0 else "2000"

        self.weight_entry.insert(0, w_def)
        self.sleep_entry.insert(0, s_def)
        self.water_entry.insert(0, wt_def)
        self.calories_entry.insert(0, c_def)

    def clear_vitals_form(self):
        self.weight_entry.delete(0, tk.END)
        self.sleep_entry.delete(0, tk.END)
        self.water_entry.delete(0, tk.END)
        self.calories_entry.delete(0, tk.END)

    def save_vitals(self):
        try:
            d_str = self.date_entry.get().strip()
            w_kg = float(self.weight_entry.get().strip() or "65.0")
            sleep_h = float(self.sleep_entry.get().strip() or "7.5")
            water_m = float(self.water_entry.get().strip() or "2000")
            c_cons = float(self.calories_entry.get().strip() or "2000")

            self.db.add_or_update_metric(d_str, w_kg, sleep_h, water_m, c_cons)
            messagebox.showinfo("Success", f"Daily vitals for {d_str} saved successfully!")
            logger.info(f"User logged vitals for {d_str}")
            if self.refresh_callback:
                self.refresh_callback()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values for weight, sleep, water, or calories.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save vitals: {e}")

    def save_workout(self):
        try:
            d_str = self.date_entry.get().strip()
            act = self.activity_combo.get().strip()
            if not act or act == "-- Select Activity --":
                messagebox.showwarning("Select Activity", "Please select an activity type from the dropdown list.")
                return

            dur = int(self.duration_entry.get().strip() or "30")
            c_burn = float(self.ex_cal_entry.get().strip() or "180")
            notes = self.notes_entry.get().strip()

            self.db.add_workout(d_str, act, dur, c_burn, notes)
            messagebox.showinfo("Success", f"Workout '{act}' ({dur} min) logged successfully for {d_str}!")
            logger.info(f"User logged workout '{act}' for {d_str}")
            
            # Reset workout inputs after saving
            self.activity_combo.set("-- Select Activity --")
            self.notes_entry.delete(0, tk.END)

            if self.refresh_callback:
                self.refresh_callback()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for duration and calories burned.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save workout: {e}")
