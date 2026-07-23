import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from backend.analytics import HealthAnalyticsEngine

class GoalsBadgesView(tk.Frame):
    """
    Goals & Badges View: Streak counter, badge gallery, new goal creation form,
    and active goals table matching screenshot 2.
    """
    def __init__(self, parent, db):
        super().__init__(parent, bg="#f6f8f5")
        self.db = db
        self.build_ui()

    def build_ui(self):
        # Header
        header_frame = tk.Frame(self, bg="#f6f8f5")
        header_frame.pack(fill="x", padx=30, pady=(25, 10))

        sub_label = tk.Label(header_frame, text="MOTIVATION", font=("Segoe UI", 9, "bold"), 
                             fg="#136349", bg="#f6f8f5")
        sub_label.pack(anchor="w")

        title_label = tk.Label(header_frame, text="Goals & badges", font=("Georgia", 24, "bold"), 
                               fg="#1a201c", bg="#f6f8f5")
        title_label.pack(anchor="w")

        container = tk.Frame(self, bg="#f6f8f5")
        container.pack(fill="both", expand=True, padx=30, pady=10)

        # 3-Column Top Grid
        top_grid = tk.Frame(container, bg="#f6f8f5")
        top_grid.pack(fill="x", pady=10)

        top_grid.columnconfigure(0, weight=1)
        top_grid.columnconfigure(1, weight=1)
        top_grid.columnconfigure(2, weight=1)

        workouts = self.db.get_all_workouts()
        df_w = HealthAnalyticsEngine.workouts_to_dataframe(workouts)
        streak_days = HealthAnalyticsEngine.calculate_streak(df_w)

        # --- Column 1: EXERCISE STREAK ---
        card1 = tk.Frame(top_grid, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=20, pady=25)
        card1.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        tk.Label(card1, text="EXERCISE STREAK", font=("Segoe UI", 9, "bold"), fg="#718096", bg="#ffffff").pack()
        tk.Label(card1, text=f"{streak_days}", font=("Segoe UI", 42, "bold"), fg="#136349", bg="#ffffff").pack(pady=5)
        tk.Label(card1, text="consecutive day(s)", font=("Segoe UI", 10), fg="#4a5568", bg="#ffffff").pack()

        # --- Column 2: BADGES EARNED ---
        card2 = tk.Frame(top_grid, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=20, pady=25)
        card2.grid(row=0, column=1, padx=8, sticky="nsew")

        tk.Label(card2, text="BADGES EARNED", font=("Segoe UI", 9, "bold"), fg="#718096", bg="#ffffff").pack(anchor="w")
        
        badges = self.db.get_earned_badges()
        if not badges:
            tk.Label(card2, text="None yet — log exercise and hydration consistently to earn your first badge.", 
                     font=("Segoe UI", 9), fg="#718096", bg="#ffffff", wraplength=220, justify="left").pack(anchor="w", pady=(15, 0))
        else:
            badges_f = tk.Frame(card2, bg="#ffffff")
            badges_f.pack(fill="both", expand=True, pady=10)
            for b in badges:
                b_lbl = tk.Label(badges_f, text=f"{b.icon} {b.name}", font=("Segoe UI", 10, "bold"), fg="#136349", bg="#f0fff4", padx=8, pady=4)
                b_lbl.pack(anchor="w", pady=3)

        # --- Column 3: NEW GOAL FORM ---
        card3 = tk.Frame(top_grid, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=20, pady=20)
        card3.grid(row=0, column=2, padx=(8, 0), sticky="nsew")

        tk.Label(card3, text="NEW GOAL", font=("Segoe UI", 9, "bold"), fg="#718096", bg="#ffffff").pack(anchor="w", pady=(0, 10))

        # Goal Type
        tk.Label(card3, text="Goal type", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.gtype_combo = ttk.Combobox(card3, values=[
            "-- Select Goal Type --", "Exercise Minutes", "Water Intake (ml)", "Weight Target (kg)", "Sleep Duration (hrs)"
        ], font=("Segoe UI", 9), state="readonly")
        self.gtype_combo.set("-- Select Goal Type --")
        self.gtype_combo.pack(fill="x", pady=(2, 8))

        # Target Value
        tk.Label(card3, text="Target value", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.gtarget_entry = ttk.Entry(card3, font=("Segoe UI", 9))
        self.gtarget_entry.insert(0, "150.0")
        self.gtarget_entry.pack(fill="x", pady=(2, 8))

        # Dates Row
        dates_row = tk.Frame(card3, bg="#ffffff")
        dates_row.pack(fill="x", pady=(0, 12))

        # Start Date
        s_frame = tk.Frame(dates_row, bg="#ffffff")
        s_frame.pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Label(s_frame, text="Start date", font=("Segoe UI", 8, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.sdate_entry = ttk.Entry(s_frame, font=("Segoe UI", 9))
        self.sdate_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.sdate_entry.pack(fill="x", pady=(2, 0))

        # End Date
        e_frame = tk.Frame(dates_row, bg="#ffffff")
        e_frame.pack(side="right", fill="x", expand=True, padx=(4, 0))
        tk.Label(e_frame, text="End date", font=("Segoe UI", 8, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.edate_entry = ttk.Entry(e_frame, font=("Segoe UI", 9))
        from datetime import timedelta
        self.edate_entry.insert(0, (date.today() + timedelta(days=7)).strftime("%Y-%m-%d"))
        self.edate_entry.pack(fill="x", pady=(2, 0))

        btn_create = tk.Button(card3, text="Create goal", font=("Segoe UI", 10, "bold"), 
                               fg="#ffffff", bg="#136349", activebackground="#0f4d39", activeforeground="#ffffff", 
                               relief="flat", pady=6, cursor="hand2", command=self.create_goal)
        btn_create.pack(fill="x")

        # Lower Section: Active Goals
        goals_header = tk.Label(container, text="Active goals", font=("Georgia", 16, "bold"), 
                                fg="#1a201c", bg="#f6f8f5")
        goals_header.pack(anchor="w", pady=(25, 10))

        self.goals_list_frame = tk.Frame(container, bg="#f6f8f5")
        self.goals_list_frame.pack(fill="both", expand=True)

        self.render_active_goals()

    def render_active_goals(self):
        for widget in self.goals_list_frame.winfo_children():
            widget.destroy()

        goals = self.db.get_all_goals()
        if not goals:
            empty_lbl = tk.Label(self.goals_list_frame, text="No goals yet. Create one above.", 
                                 font=("Segoe UI", 10), fg="#718096", bg="#f6f8f5")
            empty_lbl.pack(pady=20)
        else:
            for g in goals:
                g_card = tk.Frame(self.goals_list_frame, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=20, pady=15)
                g_card.pack(fill="x", pady=6)

                top_r = tk.Frame(g_card, bg="#ffffff")
                top_r.pack(fill="x")

                t_lbl = tk.Label(top_r, text=g.goal_type, font=("Segoe UI", 11, "bold"), fg="#1a201c", bg="#ffffff")
                t_lbl.pack(side="left")

                status_lbl = tk.Label(top_r, text=f" {g.status} ", font=("Segoe UI", 8, "bold"), fg="#136349", bg="#e6fffa", padx=6, pady=2)
                status_lbl.pack(side="right")

                val_text = f"Target: {g.target_value}  |  Timeline: {g.start_date} to {g.end_date}"
                v_lbl = tk.Label(g_card, text=val_text, font=("Segoe UI", 9), fg="#4a5568", bg="#ffffff")
                v_lbl.pack(anchor="w", pady=(5, 0))

    def create_goal(self):
        try:
            gtype = self.gtype_combo.get().strip()
            if not gtype or gtype.startswith("e.g."):
                gtype = "Exercise Minutes"

            target_val = float(self.gtarget_entry.get())
            s_date = self.sdate_entry.get().strip()
            e_date = self.edate_entry.get().strip()

            self.db.add_goal(gtype, target_val, s_date, e_date)
            messagebox.showinfo("Success", f"Goal '{gtype}' created successfully!")
            self.render_active_goals()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid numeric target value.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create goal: {e}")
