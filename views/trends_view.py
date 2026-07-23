import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from backend.analytics import HealthAnalyticsEngine

class TrendsView(tk.Frame):
    """
    Trends View: Premium Matplotlib visualizations for long-term health metrics.
    Supports interactive timeframe filtering (7D, 14D, 30D), view mode switching,
    KPI summary metrics, filled area gradients, target goal reference bands, 
    and dual-axis step/heart rate analytics.
    """
    def __init__(self, parent, db):
        super().__init__(parent, bg="#f6f8f5")
        self.db = db
        self.days_filter = 14
        self.view_mode = "2x2" # Options: "2x2", "sleep", "water", "weight", "steps_hr"
        self.canvas = None
        self.build_ui()

    def build_ui(self):
        # Header
        header_frame = tk.Frame(self, bg="#f6f8f5")
        header_frame.pack(fill="x", padx=30, pady=(20, 5))

        sub_label = tk.Label(header_frame, text="ANALYTICS & VISUALIZATION", font=("Segoe UI", 9, "bold"), 
                             fg="#136349", bg="#f6f8f5")
        sub_label.pack(anchor="w")

        title_label = tk.Label(header_frame, text="Health Trends & Analytics", font=("Georgia", 22, "bold"), 
                               fg="#1a201c", bg="#f6f8f5")
        title_label.pack(anchor="w")

        # Top KPI Summary Cards & Controls Container
        ctrl_frame = tk.Frame(self, bg="#f6f8f5")
        ctrl_frame.pack(fill="x", padx=30, pady=(5, 10))

        # Timeframe Filter Pills (7 Days, 14 Days, 30 Days)
        tf_box = tk.Frame(ctrl_frame, bg="#f6f8f5")
        tf_box.pack(side="left")

        tk.Label(tf_box, text="Timeframe:", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#f6f8f5").pack(side="left", padx=(0, 6))

        self.btn_7d = tk.Button(tf_box, text="7 Days", font=("Segoe UI", 8, "bold"),
                                fg="#4a5568", bg="#ffffff", activebackground="#edf2f7",
                                padx=10, pady=3, relief="flat", cursor="hand2", command=lambda: self.set_days(7))
        self.btn_7d.pack(side="left", padx=2)

        self.btn_14d = tk.Button(tf_box, text="14 Days", font=("Segoe UI", 8, "bold"),
                                 fg="#ffffff", bg="#136349", activebackground="#0f4d39",
                                 padx=10, pady=3, relief="flat", cursor="hand2", command=lambda: self.set_days(14))
        self.btn_14d.pack(side="left", padx=2)

        self.btn_30d = tk.Button(tf_box, text="30 Days", font=("Segoe UI", 8, "bold"),
                                 fg="#4a5568", bg="#ffffff", activebackground="#edf2f7",
                                 padx=10, pady=3, relief="flat", cursor="hand2", command=lambda: self.set_days(30))
        self.btn_30d.pack(side="left", padx=2)

        # View Mode Dropdown
        vm_box = tk.Frame(ctrl_frame, bg="#f6f8f5")
        vm_box.pack(side="right")

        tk.Label(vm_box, text="Graph Layout:", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#f6f8f5").pack(side="left", padx=(0, 6))

        self.vm_combo = ttk.Combobox(vm_box, values=[
            "Grid Overview (4-in-1)", 
            "Sleep & Recovery Curve", 
            "Hydration & Goal Bars", 
            "Weight Trajectory Line", 
            "Steps vs Heart Rate (Dual Axis)"
        ], state="readonly", font=("Segoe UI", 9), width=28)
        self.vm_combo.set("Grid Overview (4-in-1)")
        self.vm_combo.pack(side="left")
        self.vm_combo.bind("<<ComboboxSelected>>", self.on_view_mode_change)

        # Main Graph Render Container
        self.chart_container = tk.Frame(self, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1)
        self.chart_container.pack(fill="both", expand=True, padx=30, pady=(0, 15))

        self.render_charts()

    def set_days(self, days):
        self.days_filter = days
        self.btn_7d.config(bg="#136349" if days == 7 else "#ffffff", fg="#ffffff" if days == 7 else "#4a5568")
        self.btn_14d.config(bg="#136349" if days == 14 else "#ffffff", fg="#ffffff" if days == 14 else "#4a5568")
        self.btn_30d.config(bg="#136349" if days == 30 else "#ffffff", fg="#ffffff" if days == 30 else "#4a5568")
        self.render_charts()

    def on_view_mode_change(self, event):
        sel = self.vm_combo.get()
        if "Grid" in sel:
            self.view_mode = "2x2"
        elif "Sleep" in sel:
            self.view_mode = "sleep"
        elif "Hydration" in sel:
            self.view_mode = "water"
        elif "Weight" in sel:
            self.view_mode = "weight"
        elif "Steps" in sel:
            self.view_mode = "steps_hr"
        self.render_charts()

    def render_charts(self):
        # Clear previous canvas
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        metrics = self.db.get_all_metrics()
        df_m = HealthAnalyticsEngine.metrics_to_dataframe(metrics)

        if df_m.empty:
            no_data = tk.Label(self.chart_container, text="No metrics logged yet for active user. Log vitals to render graph visualizer.", 
                               font=("Segoe UI", 11), fg="#718096", bg="#ffffff", pady=50)
            no_data.pack(fill="both", expand=True)
            return

        # Filter by timeframe
        cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=self.days_filter)
        df_sub = df_m[df_m["date"] >= cutoff_date] if not df_m.empty else df_m
        if df_sub.empty:
            df_sub = df_m

        dates_str = df_sub["date"].dt.strftime("%m-%d")

        plt.close('all')
        plt.style.use('default')

        if self.view_mode == "2x2":
            fig, axes = plt.subplots(2, 2, figsize=(10, 6.2), dpi=100)
            fig.patch.set_facecolor('#ffffff')

            # 1. Sleep Duration
            ax1 = axes[0, 0]
            self.style_subplot(ax1, "Sleep Duration (Hours)", "Hours")
            ax1.plot(dates_str, df_sub["sleep_hours"], marker='o', color='#10b981', linewidth=2.5, label="Sleep Hours")
            ax1.fill_between(dates_str, df_sub["sleep_hours"], color='#10b981', alpha=0.12)
            ax1.axhspan(7.0, 9.0, color='#34d399', alpha=0.15, label="Target Zone (7-9h)")
            ax1.legend(loc="upper left", fontsize=7.5, frameon=True, facecolor="#ffffff", edgecolor="#cbd5e0")

            # 2. Water Intake
            ax2 = axes[0, 1]
            self.style_subplot(ax2, "Water Hydration (mL)", "mL")
            bars = ax2.bar(dates_str, df_sub["water_ml"], color='#3b82f6', alpha=0.75, width=0.55, label="Water (mL)")
            ax2.axhline(y=2000, color='#2563eb', linestyle='--', linewidth=1.5, label="Target (2000ml)")
            ax2.legend(loc="upper left", fontsize=7.5, frameon=True, facecolor="#ffffff", edgecolor="#cbd5e0")

            # 3. Weight Progression
            ax3 = axes[1, 0]
            self.style_subplot(ax3, "Weight Trend (kg)", "kg")
            ax3.plot(dates_str, df_sub["weight_kg"], marker='s', color='#f59e0b', linewidth=2.5, label="Weight (kg)")
            if not df_sub.empty and df_sub["weight_kg"].max() > 0:
                min_w = df_sub["weight_kg"].min() * 0.98
                max_w = df_sub["weight_kg"].max() * 1.02
                ax3.set_ylim(min_w, max_w)
            ax3.legend(loc="upper left", fontsize=7.5, frameon=True, facecolor="#ffffff", edgecolor="#cbd5e0")

            # 4. Activity Steps & Heart Rate (Dual Y-Axis)
            ax4 = axes[1, 1]
            self.style_subplot(ax4, "Steps & Resting Heart Rate", "Steps")
            ax4.plot(dates_str, df_sub["steps"], marker='^', color='#8b5cf6', linewidth=2, label="Steps")
            ax4.legend(loc="upper left", fontsize=7.5, frameon=True, facecolor="#ffffff", edgecolor="#cbd5e0")

            if "avg_heart_rate" in df_sub.columns and df_sub["avg_heart_rate"].max() > 0:
                ax4_r = ax4.twinx()
                ax4_r.plot(dates_str, df_sub["avg_heart_rate"], marker='o', color='#ef4444', linestyle=':', linewidth=1.8, label="Resting HR (bpm)")
                ax4_r.set_ylabel("HR (bpm)", color='#ef4444', fontsize=8, fontweight='bold')
                ax4_r.tick_params(axis='y', labelcolor='#ef4444', labelsize=8)
                ax4_r.spines['top'].set_visible(False)
                ax4_r.legend(loc="upper right", fontsize=7.5, frameon=True, facecolor="#ffffff", edgecolor="#cbd5e0")

            fig.tight_layout(pad=2.2)

        elif self.view_mode == "sleep":
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
            fig.patch.set_facecolor('#ffffff')
            self.style_subplot(ax, f"Sleep & Recovery Analysis ({self.days_filter}-Day View)", "Sleep Duration (Hours)")
            ax.plot(dates_str, df_sub["sleep_hours"], marker='o', color='#10b981', linewidth=3, markersize=7, label="Daily Sleep (hrs)")
            ax.fill_between(dates_str, df_sub["sleep_hours"], color='#10b981', alpha=0.18)
            ax.axhspan(7.0, 9.0, color='#34d399', alpha=0.2, label="Optimal Target Band (7.0 - 9.0 hrs)")
            ax.axhline(y=6.0, color='#ef4444', linestyle='--', linewidth=1.5, label="Sleep Deficit Warning Threshold (<6h)")
            
            # Annotate peak and lowest
            max_idx = df_sub["sleep_hours"].idxmax()
            min_idx = df_sub["sleep_hours"].idxmin()
            if max_idx in df_sub.index:
                ax.annotate(f"Peak: {df_sub.loc[max_idx, 'sleep_hours']}h", 
                            (df_sub.loc[max_idx, 'date'].strftime("%m-%d"), df_sub.loc[max_idx, 'sleep_hours']),
                            textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, fontweight='bold', color='#047857')
            
            ax.legend(loc="upper left", fontsize=9, frameon=True, facecolor="#ffffff", edgecolor="#cbd5e0")
            fig.tight_layout(pad=2.0)

        elif self.view_mode == "water":
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
            fig.patch.set_facecolor('#ffffff')
            self.style_subplot(ax, f"Hydration & Daily Water Goals ({self.days_filter}-Day View)", "Water Intake (mL)")
            bars = ax.bar(dates_str, df_sub["water_ml"], color='#3b82f6', alpha=0.75, width=0.5, label="Water Intake (mL)")
            ax.axhline(y=2000, color='#1d4ed8', linestyle='--', linewidth=2, label="Daily Recommended Goal (2000 mL)")
            ax.axhline(y=1100, color='#ef4444', linestyle=':', linewidth=1.5, label="Dehydration Danger Line (1100 mL)")
            ax.legend(loc="upper left", fontsize=9, frameon=True, facecolor="#ffffff", edgecolor="#cbd5e0")
            fig.tight_layout(pad=2.0)

        elif self.view_mode == "weight":
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
            fig.patch.set_facecolor('#ffffff')
            self.style_subplot(ax, f"Body Weight Trajectory ({self.days_filter}-Day View)", "Weight (kg)")
            ax.plot(dates_str, df_sub["weight_kg"], marker='s', color='#f59e0b', linewidth=3, markersize=7, label="Weight (kg)")
            ax.fill_between(dates_str, df_sub["weight_kg"], color='#f59e0b', alpha=0.12)
            if not df_sub.empty and df_sub["weight_kg"].max() > 0:
                ax.set_ylim(df_sub["weight_kg"].min() - 0.5, df_sub["weight_kg"].max() + 0.5)
            ax.legend(loc="upper left", fontsize=9, frameon=True, facecolor="#ffffff", edgecolor="#cbd5e0")
            fig.tight_layout(pad=2.0)

        else: # "steps_hr"
            fig, ax1 = plt.subplots(figsize=(10, 6), dpi=100)
            fig.patch.set_facecolor('#ffffff')
            self.style_subplot(ax1, f"Physical Activity Steps vs Resting Heart Rate ({self.days_filter}-Day View)", "Daily Steps")
            ax1.bar(dates_str, df_sub["steps"], color='#8b5cf6', alpha=0.6, width=0.45, label="Steps Count")
            ax1.axhline(y=10000, color='#6d28d9', linestyle='--', linewidth=1.5, label="Recommended 10,000 Step Goal")

            if "avg_heart_rate" in df_sub.columns:
                ax2 = ax1.twinx()
                ax2.plot(dates_str, df_sub["avg_heart_rate"], marker='o', color='#ef4444', linewidth=2.5, markersize=6, label="Resting HR (bpm)")
                ax2.axhline(y=76, color='#b91c1c', linestyle=':', linewidth=1.2, label="Elevated HR Line (76 bpm)")
                ax2.set_ylabel("Resting Heart Rate (bpm)", color='#ef4444', fontsize=9, fontweight='bold')
                ax2.tick_params(axis='y', labelcolor='#ef4444', labelsize=8)
                ax2.spines['top'].set_visible(False)

            ax1.legend(loc="upper left", fontsize=8.5, frameon=True, facecolor="#ffffff", edgecolor="#cbd5e0")
            fig.tight_layout(pad=2.0)

        # Embed Matplotlib Figure in Canvas
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def style_subplot(self, ax, title, ylabel):
        ax.set_facecolor('#ffffff')
        ax.set_title(title, fontsize=10, fontweight='bold', color='#1a201c', pad=10)
        ax.set_ylabel(ylabel, fontsize=8, fontweight='bold', color='#4a5568')
        ax.tick_params(axis='x', rotation=35, labelsize=8, colors='#4a5568')
        ax.tick_params(axis='y', labelsize=8, colors='#4a5568')
        ax.grid(True, linestyle='--', alpha=0.5, color='#cbd5e0')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cbd5e0')
        ax.spines['bottom'].set_color('#cbd5e0')
