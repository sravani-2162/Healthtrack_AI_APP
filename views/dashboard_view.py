import tkinter as tk
from tkinter import ttk
from backend.analytics import HealthAnalyticsEngine

class DashboardView(tk.Frame):
    """
    Dashboard View: High level vitals, quick metrics, daily summary, and wellness score.
    """
    def __init__(self, parent, db):
        super().__init__(parent, bg="#f6f8f5")
        self.db = db
        self.build_ui()

    def build_ui(self):
        header_frame = tk.Frame(self, bg="#f6f8f5")
        header_frame.pack(fill="x", padx=30, pady=(25, 10))

        user = self.db.get_user()
        user_fn = user.full_name.split()[0] if user.full_name else "User"

        sub_label = tk.Label(header_frame, text="HEALTH MONITORING & WELLNESS PLATFORM", font=("Segoe UI", 9, "bold"), 
                             fg="#136349", bg="#f6f8f5")
        sub_label.pack(anchor="w")

        title_label = tk.Label(header_frame, text=f"HealthTrack AI — Welcome, {user_fn}! 👋", font=("Georgia", 22, "bold"), 
                               fg="#1a201c", bg="#f6f8f5")
        title_label.pack(anchor="w", pady=(2, 2))

        desc_label = tk.Label(header_frame, text="Intelligent Health Monitoring & Wellness Overview  •  Real-time vitals, habit analytics, and active insights", 
                              font=("Segoe UI", 10), fg="#4a5568", bg="#f6f8f5")
        desc_label.pack(anchor="w")

        # Scrollable container or main container
        container = tk.Frame(self, bg="#f6f8f5")
        container.pack(fill="both", expand=True, padx=30, pady=10)

        # Load metrics & workouts
        metrics = self.db.get_all_metrics()
        workouts = self.db.get_all_workouts()

        df_m = HealthAnalyticsEngine.metrics_to_dataframe(metrics)
        df_w = HealthAnalyticsEngine.workouts_to_dataframe(workouts)

        score, label = HealthAnalyticsEngine.calculate_wellness_score(df_m, df_w)
        latest_metric = metrics[-1] if metrics else None

        # Grid of Cards
        cards_frame = tk.Frame(container, bg="#f6f8f5")
        cards_frame.pack(fill="x", pady=10)

        # Card 1: Wellness Score
        self.create_stat_card(cards_frame, "WELLNESS SCORE", f"{score}", label, "#136349", column=0)

        # Card 2: Latest Weight
        weight_str = f"{latest_metric.weight_kg} kg" if latest_metric and latest_metric.weight_kg > 0 else "-- kg"
        self.create_stat_card(cards_frame, "LATEST WEIGHT", weight_str, "Recorded Vitals", "#2d3748", column=1)

        # Card 3: Avg Sleep
        sleep_str = f"{latest_metric.sleep_hours} h" if latest_metric and latest_metric.sleep_hours > 0 else "-- h"
        self.create_stat_card(cards_frame, "DAILY SLEEP", sleep_str, "Target: 7-8 hours", "#2d3748", column=2)

        # Card 4: Water Intake
        water_str = f"{int(latest_metric.water_ml)} ml" if latest_metric and latest_metric.water_ml > 0 else "-- ml"
        self.create_stat_card(cards_frame, "WATER INTAKE", water_str, "Target: 2000+ ml", "#2d3748", column=3)

        # Lower Section: Detected Patterns Preview
        patterns_header = tk.Label(container, text="Active Health Insights", font=("Georgia", 16, "bold"), 
                                   fg="#1a201c", bg="#f6f8f5")
        patterns_header.pack(anchor="w", pady=(20, 10))

        patterns = HealthAnalyticsEngine.detect_patterns(df_m, df_w)

        if not patterns:
            no_p = tk.Label(container, text="No health risk patterns detected. Keep up the good work!", 
                            font=("Segoe UI", 11), fg="#4a5568", bg="#ffffff", padx=20, pady=20, relief="solid", bd=1)
            no_p.pack(fill="x")
        else:
            for p in patterns[:2]:  # Show top 2 insights
                self.create_insight_card(container, p.title, p.severity, p.description, p.detail_text)

    def create_stat_card(self, parent, title, main_val, sub_val, val_color, column):
        card = tk.Frame(parent, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=20, pady=18)
        card.grid(row=0, column=column, padx=8, pady=5, sticky="nsew")
        parent.columnconfigure(column, weight=1)

        lbl_t = tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), fg="#718096", bg="#ffffff")
        lbl_t.pack(anchor="w")

        lbl_m = tk.Label(card, text=main_val, font=("Segoe UI", 28, "bold"), fg=val_color, bg="#ffffff")
        lbl_m.pack(anchor="w", pady=(5, 2))

        lbl_s = tk.Label(card, text=sub_val, font=("Segoe UI", 9), fg="#a0aec0", bg="#ffffff")
        lbl_s.pack(anchor="w")

    def create_insight_card(self, parent, title, severity, desc, detail):
        card = tk.Frame(parent, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=20, pady=15)
        card.pack(fill="x", pady=6)

        top_f = tk.Frame(card, bg="#ffffff")
        top_f.pack(fill="x")

        t_lbl = tk.Label(top_f, text=title, font=("Segoe UI", 12, "bold"), fg="#1a201c", bg="#ffffff")
        t_lbl.pack(side="left")

        # Severity Badge
        bg_c = "#fdf0ed" if severity == "HIGH" else "#fef6e7"
        fg_c = "#b93815" if severity == "HIGH" else "#b54708"
        badge = tk.Label(top_f, text=f" {severity} ", font=("Segoe UI", 8, "bold"), 
                         fg=fg_c, bg=bg_c, padx=6, pady=2)
        badge.pack(side="left", padx=10)

        desc_lbl = tk.Label(card, text=desc, font=("Segoe UI", 10), fg="#4a5568", bg="#ffffff", 
                            wraplength=700, justify="left")
        desc_lbl.pack(anchor="w", pady=(6, 4))

        detail_lbl = tk.Label(card, text=detail, font=("Courier New", 9), fg="#718096", bg="#ffffff")
        detail_lbl.pack(anchor="w")
