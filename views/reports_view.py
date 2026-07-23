import tkinter as tk
from tkinter import messagebox, filedialog
from backend.analytics import HealthAnalyticsEngine
from backend.exporter import DataExporter

class ReportsView(tk.Frame):
    """
    Reports View: Displays Weekly and Monthly summaries, 6 key metrics cards, 
    detected patterns, and export features (JSON / CSV).
    """
    def __init__(self, parent, db):
        super().__init__(parent, bg="#f6f8f5")
        self.db = db
        self.timeframe = "weekly"
        self.build_ui()

    def build_ui(self):
        # Header
        header_frame = tk.Frame(self, bg="#f6f8f5")
        header_frame.pack(fill="x", padx=30, pady=(25, 10))

        sub_label = tk.Label(header_frame, text="SUMMARIES", font=("Segoe UI", 9, "bold"), 
                             fg="#136349", bg="#f6f8f5")
        sub_label.pack(anchor="w")

        title_label = tk.Label(header_frame, text="Reports", font=("Georgia", 24, "bold"), 
                               fg="#1a201c", bg="#f6f8f5")
        title_label.pack(anchor="w")

        # Control Bar: Toggle Pill & Export Buttons
        ctrl_frame = tk.Frame(self, bg="#f6f8f5")
        ctrl_frame.pack(fill="x", padx=30, pady=(5, 15))

        # Timeframe toggle buttons
        self.btn_weekly = tk.Button(ctrl_frame, text="Weekly", font=("Segoe UI", 9, "bold"),
                                    fg="#ffffff", bg="#1a201c", activebackground="#2d3748", activeforeground="#ffffff",
                                    padx=15, pady=4, relief="flat", cursor="hand2", command=lambda: self.set_timeframe("weekly"))
        self.btn_weekly.pack(side="left", padx=(0, 5))

        self.btn_monthly = tk.Button(ctrl_frame, text="Monthly", font=("Segoe UI", 9, "bold"),
                                     fg="#4a5568", bg="#ffffff", activebackground="#edf2f7", activeforeground="#1a201c",
                                     padx=15, pady=4, relief="flat", cursor="hand2", command=lambda: self.set_timeframe("monthly"))
        self.btn_monthly.pack(side="left")

        # Export Buttons on right
        btn_exp_json = tk.Button(ctrl_frame, text="📥 Export JSON", font=("Segoe UI", 9, "bold"),
                                 fg="#ffffff", bg="#136349", activebackground="#0f4d39", activeforeground="#ffffff",
                                 padx=12, pady=4, relief="flat", cursor="hand2", command=self.export_json)
        btn_exp_json.pack(side="right", padx=(5, 0))

        btn_exp_csv = tk.Button(ctrl_frame, text="📄 Export CSV", font=("Segoe UI", 9, "bold"),
                                fg="#1a201c", bg="#ffffff", activebackground="#edf2f7", activeforeground="#1a201c",
                                padx=12, pady=4, relief="flat", cursor="hand2", command=self.export_csv)
        btn_exp_csv.pack(side="right")

        # Main Scrollable Content
        self.content_container = tk.Frame(self, bg="#f6f8f5")
        self.content_container.pack(fill="both", expand=True, padx=30, pady=5)

        self.render_report_content()

    def set_timeframe(self, tf):
        self.timeframe = tf
        if tf == "weekly":
            self.btn_weekly.config(bg="#1a201c", fg="#ffffff")
            self.btn_monthly.config(bg="#ffffff", fg="#4a5568")
        else:
            self.btn_weekly.config(bg="#ffffff", fg="#4a5568")
            self.btn_monthly.config(bg="#1a201c", fg="#ffffff")

        self.render_report_content()

    def render_report_content(self):
        # Clear content container
        for widget in self.content_container.winfo_children():
            widget.destroy()

        metrics = self.db.get_all_metrics()
        workouts = self.db.get_all_workouts()

        df_m = HealthAnalyticsEngine.metrics_to_dataframe(metrics)
        df_w = HealthAnalyticsEngine.workouts_to_dataframe(workouts)

        summary = HealthAnalyticsEngine.compute_reports_summary(df_m, df_w, timeframe=self.timeframe)
        avg_label = "7-day average" if self.timeframe == "weekly" else "30-day average"

        # Grid of 6 Cards (2 rows x 3 cols)
        cards_frame = tk.Frame(self.content_container, bg="#f6f8f5")
        cards_frame.pack(fill="x", pady=5)

        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.columnconfigure(2, weight=1)

        # Row 0
        self.create_report_card(cards_frame, 0, 0, "WELLNESS SCORE", f"{summary['wellness_score']}", summary['score_label'])
        self.create_report_card(cards_frame, 0, 1, "AVG SLEEP", f"{summary['avg_sleep']} h", avg_label)
        self.create_report_card(cards_frame, 0, 2, "AVG WATER", f"{summary['avg_water']} ml", avg_label)

        # Row 1
        self.create_report_card(cards_frame, 1, 0, "WEIGHT CHANGE", summary['weight_change'], summary['date_range'])
        self.create_report_card(cards_frame, 1, 1, "WORKOUT SESSIONS", f"{summary['workout_count']}", f"{summary['workout_mins']} min total")
        self.create_report_card(cards_frame, 1, 2, "CALORIES BURNED", f"{summary['calories_burned']}", "from workouts")

        # Lower Section: Detected patterns
        patterns_header = tk.Label(self.content_container, text="Detected patterns", font=("Georgia", 16, "bold"), 
                                   fg="#1a201c", bg="#f6f8f5")
        patterns_header.pack(anchor="w", pady=(20, 10))

        patterns = HealthAnalyticsEngine.detect_patterns(df_m, df_w)

        if not patterns:
            no_p = tk.Label(self.content_container, text="No health risks detected in this period.", 
                            font=("Segoe UI", 10), fg="#4a5568", bg="#ffffff", padx=20, pady=15)
            no_p.pack(fill="x")
        else:
            for p in patterns:
                self.render_pattern_summary_card(self.content_container, p)

    def create_report_card(self, parent, row, col, title, main_val, sub_val):
        card = tk.Frame(parent, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=20, pady=15)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        lbl_t = tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg="#718096", bg="#ffffff")
        lbl_t.pack(anchor="w")

        lbl_m = tk.Label(card, text=main_val, font=("Segoe UI", 26, "bold"), fg="#1a201c", bg="#ffffff")
        lbl_m.pack(anchor="w", pady=(4, 2))

        lbl_s = tk.Label(card, text=sub_val, font=("Segoe UI", 9), fg="#a0aec0", bg="#ffffff")
        lbl_s.pack(anchor="w")

    def render_pattern_summary_card(self, parent, pattern):
        border_color = "#e53e3e" if pattern.severity == "HIGH" else "#dd6b20"
        card = tk.Frame(parent, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=0, pady=0)
        card.pack(fill="x", pady=6)

        left_bar = tk.Frame(card, bg=border_color, width=4)
        left_bar.pack(side="left", fill="y")

        card_content = tk.Frame(card, bg="#ffffff", padx=15, pady=12)
        card_content.pack(side="left", fill="both", expand=True)

        top_row = tk.Frame(card_content, bg="#ffffff")
        top_row.pack(fill="x")

        t_lbl = tk.Label(top_row, text=pattern.title, font=("Segoe UI", 11, "bold"), fg="#1a201c", bg="#ffffff")
        t_lbl.pack(side="left")

        bg_badge = "#fdf0ed" if pattern.severity == "HIGH" else "#fef6e7"
        fg_badge = "#b93815" if pattern.severity == "HIGH" else "#b54708"
        badge = tk.Label(top_row, text=f" {pattern.severity} ", font=("Segoe UI", 8, "bold"), 
                         fg=fg_badge, bg=bg_badge, padx=5, pady=1)
        badge.pack(side="left", padx=8)

        desc_lbl = tk.Label(card_content, text=pattern.description, font=("Segoe UI", 9), 
                            fg="#4a5568", bg="#ffffff", wraplength=700, justify="left")
        desc_lbl.pack(anchor="w", pady=(4, 4))

        detail_lbl = tk.Label(card_content, text=pattern.detail_text, font=("Consolas", 9), 
                              fg="#718096", bg="#ffffff")
        detail_lbl.pack(anchor="w")

    def export_json(self):
        metrics = self.db.get_all_metrics()
        workouts = self.db.get_all_workouts()
        df_m = HealthAnalyticsEngine.metrics_to_dataframe(metrics)
        df_w = HealthAnalyticsEngine.workouts_to_dataframe(workouts)
        summary = HealthAnalyticsEngine.compute_reports_summary(df_m, df_w, self.timeframe)

        fpath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if fpath:
            success, res = DataExporter.export_to_json(metrics, workouts, summary, fpath)
            if success:
                messagebox.showinfo("Export Successful", f"Health report successfully saved to:\n{res}")
            else:
                messagebox.showerror("Export Failed", f"Error exporting JSON: {res}")

    def export_csv(self):
        metrics = self.db.get_all_metrics()
        fpath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if fpath:
            success, res = DataExporter.export_to_csv(metrics, fpath)
            if success:
                messagebox.showinfo("Export Successful", f"Metrics CSV successfully saved to:\n{res}")
            else:
                messagebox.showerror("Export Failed", f"Error exporting CSV: {res}")
