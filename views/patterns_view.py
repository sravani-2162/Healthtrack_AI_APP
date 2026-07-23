import tkinter as tk
from tkinter import ttk
from backend.analytics import HealthAnalyticsEngine

class PatternsView(tk.Frame):
    """
    Patterns View: Displays detected unhealthy habit patterns and risk warnings.
    Equipped with a scrollable canvas to ensure all cards are completely visible.
    """
    def __init__(self, parent, db):
        super().__init__(parent, bg="#f6f8f5")
        self.db = db
        self.build_ui()

    def build_ui(self):
        # Header
        header_frame = tk.Frame(self, bg="#f6f8f5")
        header_frame.pack(fill="x", padx=30, pady=(25, 10))

        sub_label = tk.Label(header_frame, text="LAST 14 DAYS", font=("Segoe UI", 9, "bold"), 
                             fg="#136349", bg="#f6f8f5")
        sub_label.pack(anchor="w")

        title_label = tk.Label(header_frame, text="Detected patterns", font=("Georgia", 24, "bold"), 
                               fg="#1a201c", bg="#f6f8f5")
        title_label.pack(anchor="w")

        # Scrollable Outer Container
        container = tk.Frame(self, bg="#f6f8f5")
        container.pack(fill="both", expand=True, padx=30, pady=10)

        # Canvas & Scrollbar setup for vertical scrolling
        canvas = tk.Canvas(container, bg="#f6f8f5", highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg="#f6f8f5")

        scroll_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_frame = canvas.create_window((0, 0), window=scroll_content, anchor="nw")
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_frame, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass

        def _bind_mousewheel(event):
            try:
                canvas.bind_all("<MouseWheel>", _on_mousewheel)
            except Exception:
                pass

        def _unbind_mousewheel(event):
            try:
                canvas.unbind_all("<MouseWheel>")
            except Exception:
                pass

        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Fetch Data & Detect Patterns
        metrics = self.db.get_all_metrics()
        workouts = self.db.get_all_workouts()

        df_m = HealthAnalyticsEngine.metrics_to_dataframe(metrics)
        df_w = HealthAnalyticsEngine.workouts_to_dataframe(workouts)

        patterns = HealthAnalyticsEngine.detect_patterns(df_m, df_w)

        if not patterns:
            no_p_card = tk.Frame(scroll_content, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=25, pady=25)
            no_p_card.pack(fill="x", pady=10)
            tk.Label(no_p_card, text="🎉 No unhealthy patterns detected!", font=("Georgia", 14, "bold"), fg="#136349", bg="#ffffff").pack(anchor="w")
            tk.Label(no_p_card, text="Your current sleep, exercise, and hydration levels are well balanced.", font=("Segoe UI", 10), fg="#4a5568", bg="#ffffff").pack(anchor="w", pady=(5, 0))
            return

        for p in patterns:
            self.render_pattern_card(scroll_content, p)

        # Extra padding space at bottom so the final card is completely visible
        spacer = tk.Frame(scroll_content, bg="#f6f8f5", height=30)
        spacer.pack(fill="x")

    def render_pattern_card(self, parent, pattern):
        border_color = "#e53e3e" if pattern.severity == "HIGH" else "#dd6b20"
        
        card = tk.Frame(parent, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=0, pady=0)
        card.pack(fill="x", pady=8)

        # Left color bar
        left_bar = tk.Frame(card, bg=border_color, width=5)
        left_bar.pack(side="left", fill="y")

        card_content = tk.Frame(card, bg="#ffffff", padx=20, pady=18)
        card_content.pack(side="left", fill="both", expand=True)

        # Title & Badge row
        top_row = tk.Frame(card_content, bg="#ffffff")
        top_row.pack(fill="x")

        t_lbl = tk.Label(top_row, text=pattern.title, font=("Segoe UI", 13, "bold"), fg="#1a201c", bg="#ffffff")
        t_lbl.pack(side="left")

        bg_badge = "#fdf0ed" if pattern.severity == "HIGH" else "#fef6e7"
        fg_badge = "#b93815" if pattern.severity == "HIGH" else "#b54708"
        badge = tk.Label(top_row, text=f" {pattern.severity} ", font=("Segoe UI", 8, "bold"), 
                         fg=fg_badge, bg=bg_badge, padx=6, pady=2)
        badge.pack(side="left", padx=10)

        # Description Text
        desc_lbl = tk.Label(card_content, text=pattern.description, font=("Segoe UI", 10), 
                            fg="#4a5568", bg="#ffffff", wraplength=750, justify="left")
        desc_lbl.pack(anchor="w", pady=(8, 6))

        # Monospace Detail Text
        detail_lbl = tk.Label(card_content, text=pattern.detail_text, font=("Consolas", 9), 
                              fg="#718096", bg="#ffffff")
        detail_lbl.pack(anchor="w")
