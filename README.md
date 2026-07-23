# HealthTrack AI — Intelligent Health Monitoring & Wellness Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-emerald.svg)](https://docs.python.org/3/library/tkinter.html)
[![Analytics](https://img.shields.io/badge/Analytics-Pandas%20%7C%20Matplotlib-orange.svg)](https://pandas.pydata.org/)
[![Database](https://img.shields.io/badge/Database-SQLite3%20WAL-lightgrey.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**HealthTrack AI** is an intelligent, desktop-based personal wellness and bio-analytics platform built with Python, Tkinter, SQLite3, Pandas, and Matplotlib. It enables users to track daily vitals, log physical exercise, analyze long-term health trends, detect underlying health risk patterns, receive personalized recommendations, and manage multiple user profiles with complete dataset isolation.

---

## 🌟 Key Features

* **🌐 Dashboard Overview**: High-level vitals summary, wellness score (0–100), latest weight, daily sleep, hydration metrics, and real-time active health insights.
* **✏️ Daily Vitals & Workout Logging**: 
  * Selectable dropdown activity choices (`Brisk Walk`, `Running`, `Cycling`, `Swimming`, `Yoga`, `Strength Training`, `Cardio`, `Pilates`, `HIIT`).
  * Dynamic date auto-loading that populates actual recorded metrics for selected dates.
  * Baseline default figures for rapid 1-click logging.
* **📈 Interactive Trends & Analytics**:
  * Multi-timeframe filter (`7 Days`, `14 Days`, `30 Days`).
  * 5 view modes: Grid Overview (4-in-1), Sleep & Recovery, Hydration Bars, Weight Trajectory, and Steps vs Resting Heart Rate (Dual Y-Axis).
  * Target health reference bands, filled gradient area curves, and crisp subplot styling.
* **🚩 Pattern Detection & Health Risk Warnings**:
  * **Low Exercise & Inactivity**: Flags activity below WHO 150 min/week recommendations.
  * **Missed Workouts**: Tracks consecutive inactive days.
  * **Severe Sleep Deficit / Shortfall**: Flags sleep deprivation (<6.0 hours: HIGH severity; 6.0–7.0 hours: MEDIUM severity).
  * **Dehydration Risk**: Detects fluid deficits (<1100 mL: HIGH severity; <1500 mL: MEDIUM severity).
  * **Elevated Resting Heart Rate / Stress**: Flags resting HR ≥ 76 bpm (MEDIUM) or ≥ 80 bpm (HIGH).
  * **Rapid Weight Gain Trajectory**: Identifies upward weight shifts (>1.0 kg over 14 days).
* **✔️ Dynamic Recommendations**: Actionable recovery, stress management, hydration, and nutritional guidance aligned with detected pattern severity.
* **⭐ Goals & Badges**: Set target goals with timeline tracking, measure workout streaks, and unlock earned milestone badges.
* **📑 Reports & Data Exporting**: Weekly and monthly aggregated summaries with 1-click export to **JSON** and **CSV**.
* **👤 Multi-User Profile Isolation & Wearable Sync**:
  * Complete dataset separation per user ID via composite `UNIQUE(user_id, date)` database constraints.
  * 7 built-in preset user profile datasets (3 Healthy/Optimal, 4 Unhealthy/High Risk).
  * Simulated wearable device synchronization for steps, heart rate, and sleep.

---

## 👥 Preset Profile Datasets

HealthTrack AI comes pre-loaded with **7 diverse user datasets** representing distinct healthy and high-risk profiles:

| Profile Name | Profile Type | Wellness Score | Pattern Highlights |
| :--- | :--- | :---: | :--- |
| **Rahul Sharma** | Healthy / Athlete | **100/100** | 8.5h sleep, 3000 mL water, 12k+ steps, low HR (58 bpm), frequent workouts |
| **Anjali Patel** | Healthy / Weight Loss | **100/100** | 21-day weight drop (72.5 kg → 68.8 kg), brisk walking & cardio |
| **Priya Nair** | Healthy / Active Professional | **100/100** | Balanced daily habits, 7.8h sleep, 2500 mL water, Pilates & yoga |
| **Vidithanjali** | Unhealthy / Sedentary | **58/100** | Low exercise, missed workouts, sleep shortfall, insufficient hydration |
| **Karan Mehta** | Unhealthy / Overtrained | **76/100** | Intense lifting 5x/wk (12k steps), severe sleep deficit (<5h), elevated HR (80 bpm) |
| **Sneha Rao** | Unhealthy / Severe Dehydration | **50/100** | Very low water (850 mL/day), sleep deficit, 0 workouts logged |
| **Vikram Verma** | Unhealthy / Cardio & Inactivity Risk | **58/100** | Weight gain trajectory (+1.7 kg), high resting HR (84–86 bpm), 2.2k steps/day |

---

## 📁 Project Architecture

```
Healthtrack_app/
├── main.py                  # Main entry point & application bootstrap
├── app_gui.py               # Main Tkinter window, sidebar navigation, view router
├── seed_data.py             # Seeding helper for 7 sample user profile datasets
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
│
├── backend/
│   ├── analytics.py         # Pandas-powered analytics engine & pattern detection
│   ├── database.py          # SQLite DatabaseManager with connection context pool & WAL mode
│   ├── exporter.py          # JSON and CSV report export utilities
│   ├── logger.py            # System logging configuration
│   └── models.py            # Data models (User, DailyMetric, Workout, Goal, Badge, HealthPattern)
│
└── views/
    ├── dashboard_view.py    # Main overview, vitals KPI cards & active insights
    ├── log_data_view.py     # Daily vitals form & workout tracker with selectable options
    ├── trends_view.py       # Interactive Matplotlib charts & timeframe filters
    ├── patterns_view.py     # Scrollable health pattern cards & risk alerts
    ├── recommendations_view.py # Scrollable personalized advice cards
    ├── reports_view.py      # Summary metrics cards & data export buttons
    ├── goals_badges_view.py # Streak tracker, active goals table & badge gallery
    └── profile_view.py      # Profile management, wearable device sync & dataset preset loader
```

---

## 🛠️ Installation & Setup

### Prerequisites
* Python 3.10 or higher
* `pip` package manager

### 1. Install Dependencies
Install required packages using `requirements.txt`:
```bash
pip install -r requirements.txt
```

*Required libraries:*
* `pandas>=2.0.0`
* `numpy>=1.24.0`
* `matplotlib>=3.7.0`

### 2. Run the Application
Launch HealthTrack AI:
```bash
python main.py
```

---

## 🗄️ Database Architecture

HealthTrack AI utilizes an **SQLite3 database** configured in **Write-Ahead Logging (WAL)** mode with connection context management to eliminate lock contentions.

### Key Tables & Constraints:
* `users`: User profiles (`user_id`, `full_name`, `age`, `height_cm`, `gender`, `password_hash`).
* `daily_metrics`: Daily vitals (`metric_id`, `user_id`, `date`, `weight_kg`, `sleep_hours`, `water_ml`, `calories_consumed`, `steps`, `avg_heart_rate`) with composite constraint `UNIQUE(user_id, date)`.
* `workouts`: Recorded exercise sessions (`workout_id`, `user_id`, `date`, `activity_type`, `duration_minutes`, `calories_burned`, `notes`).
* `goals`: Fitness goals (`goal_id`, `user_id`, `goal_type`, `target_value`, `current_value`, `start_date`, `end_date`, `status`).
* `badges`: Milestone badges (`badge_id`, `user_id`, `name`, `description`, `icon`, `earned_date`).
* `wearable_sync_logs`: Wearable device sync history (`sync_id`, `user_id`, `sync_timestamp`, `steps`, `avg_heart_rate`, `sleep_hours`).
* `app_settings`: Persistent application state (`active_user_id`).

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.
