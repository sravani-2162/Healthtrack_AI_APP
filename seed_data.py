import sqlite3
from datetime import datetime, timedelta
from backend.database import DatabaseManager
from backend.logger import logger

def get_or_create_user_by_name(db, name, age, height, gender):
    users = db.get_all_users()
    for u in users:
        if u.full_name.lower() == name.lower():
            db.set_active_user(u.user_id)
            return u.user_id
    return db.create_user(name, age, height, gender)

def seed_dataset(dataset_key="sedentary", db_path="healthtrack.db"):
    """
    Populates database with distinct sample health datasets.
    Available keys: 'sedentary', 'athlete', 'weight_loss', 'active_prof', 'overtrained', 'dehydrated', 'cardio_risk'
    """
    db = DatabaseManager(db_path)
    logger.info(f"Seeding HealthTrack database with dataset: '{dataset_key}'...")

    today = datetime.now()

    if dataset_key == "athlete":
        # --- HEALTHY PROFILE 1: ATHLETE / OPTIMAL HEALTH (Rahul Sharma) ---
        get_or_create_user_by_name(db, "Rahul Sharma", 24, 178.0, "Male")
        
        # 14 Days Metrics (High sleep 8-8.5h, High water 3000ml, High steps 11.5k-13.8k, Low HR 58-60 bpm)
        for i in range(14, -1, -1):
            d_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            weight = round(72.0 + (0.02 * i), 1)
            sleep = 8.0 if i % 2 == 0 else 8.5
            water = 3000.0 if i % 3 == 0 else 2800.0
            calories = 2600.0 + (i * 20) % 150
            steps = 11500 if i % 2 == 0 else 13800
            hr = 60 if i % 2 == 0 else 58
            db.add_or_update_metric(d_str, weight, sleep, water, calories, steps, hr)

        activities = [
            (1, "Running", 45, 450, "5k morning run"),
            (2, "Cycling", 60, 520, "Outdoor bike ride"),
            (4, "Swimming", 40, 380, "Lap swimming"),
            (5, "Strength Training", 50, 310, "Upper body lift"),
            (7, "Running", 45, 460, "Tempo run"),
            (9, "Cycling", 75, 620, "Long weekend ride"),
            (11, "Strength Training", 45, 290, "Leg day"),
            (13, "Running", 50, 480, "Interval sprints")
        ]
        for days_ago, act, dur, cal, notes in activities:
            w_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            db.add_workout(w_date, act, dur, cal, notes)

        db.add_badge_if_not_exists("Workout Warrior", "Completed 150+ minutes of exercise in a single week", "🏆")
        db.add_badge_if_not_exists("Hydration Master", "Hit 2500+ ml daily hydration target for 7 straight days", "💧")
        db.add_badge_if_not_exists("7-Day Streak", "Logged exercise consistently for 7 consecutive days", "🔥")

        db.add_goal("Exercise Minutes", 250.0, (today - timedelta(days=7)).strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d"))
        db.add_goal("Water Intake (ml)", 3000.0, (today - timedelta(days=7)).strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d"))

    elif dataset_key == "weight_loss":
        # --- HEALTHY PROFILE 2: WEIGHT LOSS JOURNEY (Anjali Patel) ---
        get_or_create_user_by_name(db, "Anjali Patel", 26, 162.0, "Female")
        
        start_w = 72.5
        for i in range(21, -1, -1):
            d_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            weight = round(start_w - (0.17 * (21 - i)), 1)
            sleep = 7.5 if i % 2 == 0 else 7.0
            water = 2300.0 if i % 2 == 0 else 2500.0
            calories = 1750.0 if i % 2 == 0 else 1850.0
            steps = 9200 if i % 2 == 0 else 10500
            hr = 66
            db.add_or_update_metric(d_str, weight, sleep, water, calories, steps, hr)

        for i in range(18, 0, -3):
            w_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            act = "Brisk Walk" if i % 2 == 0 else "Cardio"
            db.add_workout(w_date, act, 35, 220, "Fat burn routine")

        db.add_badge_if_not_exists("Weight Milestone", "Successfully reduced 3+ kg over 3 weeks", "🎯")
        db.add_badge_if_not_exists("Consistency Champion", "Logged vitals every day for 3 weeks straight", "⭐")

        db.add_goal("Weight Target (kg)", 65.0, (today - timedelta(days=14)).strftime("%Y-%m-%d"), (today + timedelta(days=14)).strftime("%Y-%m-%d"))
        db.add_goal("Exercise Minutes", 180.0, (today - timedelta(days=7)).strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d"))

    elif dataset_key == "active_prof":
        # --- HEALTHY PROFILE 3: ACTIVE PROFESSIONAL (Priya Nair) ---
        get_or_create_user_by_name(db, "Priya Nair", 29, 168.0, "Female")

        for i in range(14, -1, -1):
            d_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            weight = round(58.0 + (0.01 * i), 1)
            sleep = 7.8 if i % 2 == 0 else 7.5
            water = 2400.0 if i % 2 == 0 else 2600.0
            calories = 2100.0 + (i * 10) % 120
            steps = 9800 if i % 2 == 0 else 10200
            hr = 64 if i % 2 == 0 else 62
            db.add_or_update_metric(d_str, weight, sleep, water, calories, steps, hr)

        prof_activities = [
            (1, "Pilates", 40, 210, "Core & flexibility class"),
            (3, "Running", 30, 280, "Evening neighborhood jog"),
            (6, "Power Walking", 45, 220, "Brisk lunch break walk"),
            (8, "Yoga", 50, 180, "Flow session"),
            (10, "Pilates", 40, 210, "Reformer session"),
            (13, "Running", 35, 310, "Weekend park run")
        ]
        for days_ago, act, dur, cal, notes in prof_activities:
            w_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            db.add_workout(w_date, act, dur, cal, notes)

        db.add_badge_if_not_exists("Daily Step Goal", "Averaged 10,000 steps/day over 2 weeks", "🚶‍♀️")
        db.add_badge_if_not_exists("Balanced Mindset", "Logged consistent yoga and wellness activities", "🧘‍♀️")

        db.add_goal("Daily Steps", 10000.0, (today - timedelta(days=7)).strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d"))
        db.add_goal("Water Intake (ml)", 2500.0, (today - timedelta(days=7)).strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d"))

    elif dataset_key == "overtrained":
        # --- UNHEALTHY PROFILE 1: OVERTRAINED & SLEEP DEPRIVED (Karan Mehta) ---
        get_or_create_user_by_name(db, "Karan Mehta", 31, 182.0, "Male")

        # Intense activity (12k steps), but severe sleep deprivation (<5h) & elevated HR (80 bpm)
        for i in range(14, -1, -1):
            d_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            weight = round(80.5 + (0.03 * i), 1)
            sleep = 4.8 if i % 2 == 0 else 5.2 # Severe Sleep Deficit (<6h)
            water = 1800.0 if i % 2 == 0 else 2100.0
            calories = 2900.0 + (i * 25) % 300
            steps = 12400 if i % 2 == 0 else 11800
            hr = 80 if i % 2 == 0 else 82 # Elevated Resting Heart Rate
            db.add_or_update_metric(d_str, weight, sleep, water, calories, steps, hr)

        ot_activities = [
            (1, "HIIT", 60, 620, "High intensity interval workout"),
            (2, "Heavy Lifting", 75, 540, "Chest and triceps"),
            (3, "CrossFit", 50, 580, "Metabolic conditioning"),
            (5, "Heavy Lifting", 70, 510, "Legs and core"),
            (6, "HIIT", 60, 610, "Sprints and agility"),
            (8, "Heavy Lifting", 80, 560, "Back and biceps"),
            (10, "CrossFit", 55, 600, "WOD heavy lifting"),
            (12, "HIIT", 65, 650, "Full body burner")
        ]
        for days_ago, act, dur, cal, notes in ot_activities:
            w_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            db.add_workout(w_date, act, dur, cal, notes)

        db.add_badge_if_not_exists("Gym Rat", "Logged 5+ intense strength workouts in a week", "🏋️‍♂️")
        db.add_goal("Sleep Hours", 8.0, (today - timedelta(days=7)).strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d"))

    elif dataset_key == "dehydrated":
        # --- UNHEALTHY PROFILE 2: SEVERE DEHYDRATION & CHRONIC FATIGUE (Sneha Rao) ---
        get_or_create_user_by_name(db, "Sneha Rao", 27, 160.0, "Female")

        # Very low fluid intake (<1000ml), sleep shortfall (5.5h), low steps (4.2k)
        for i in range(14, -1, -1):
            d_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            weight = round(56.2 + (0.02 * i), 1)
            sleep = 5.5 if i % 2 == 0 else 5.8
            water = 850.0 if i % 2 == 0 else 1050.0 # Severe Dehydration
            calories = 1900.0 + (i * 15) % 180
            steps = 4200 if i % 2 == 0 else 4800
            hr = 76 if i % 2 == 0 else 78
            db.add_or_update_metric(d_str, weight, sleep, water, calories, steps, hr)

        # No workouts logged in last 14 days (triggers Missed Workouts pattern)

        db.add_goal("Water Intake (ml)", 2200.0, (today - timedelta(days=7)).strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d"))

    elif dataset_key == "cardio_risk":
        # --- UNHEALTHY PROFILE 3: CARDIOVASCULAR & INACTIVITY RISK (Vikram Verma) ---
        get_or_create_user_by_name(db, "Vikram Verma", 45, 175.0, "Male")

        # Weight gain (88.5 -> 90.2kg), low steps (2.5k), high resting HR (84 bpm), high calories
        start_w = 88.5
        for i in range(14, -1, -1):
            d_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            weight = round(start_w + (0.12 * (14 - i)), 1) # Rapid Weight Gain Trajectory
            sleep = 5.8 if i % 2 == 0 else 6.2
            water = 1200.0 if i % 2 == 0 else 1350.0
            calories = 2950.0 + (i * 30) % 250
            steps = 2200 if i % 2 == 0 else 2800
            hr = 84 if i % 2 == 0 else 86 # High Resting HR
            db.add_or_update_metric(d_str, weight, sleep, water, calories, steps, hr)

        # No workouts logged in last 14 days

        db.add_goal("Exercise Minutes", 150.0, (today - timedelta(days=7)).strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d"))

    else: # Default: 'sedentary'
        # --- UNHEALTHY PROFILE 4: SEDENTARY / HIGH-RISK DESK WORKER (Vidithanjali) ---
        get_or_create_user_by_name(db, "Vidithanjali", 20, 155.0, "Female")
        
        base_weight = 60.5
        for i in range(14, -1, -1):
            d_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            weight = round(base_weight - (0.05 * (14 - i)), 1)
            sleep = 6.2 if i % 3 == 0 else 6.8 if i % 2 == 0 else 5.8 # Sleep Shortfall
            water = 1350.0 if i > 3 else 1600.0 # Insufficient Hydration
            calories = 1950.0 + (i * 15) % 200
            steps = 3800 if i % 2 == 0 else 5400 # Low steps
            hr = 74 if i % 2 == 0 else 70
            db.add_or_update_metric(d_str, weight, sleep, water, calories, steps, hr)

        w1_date = (today - timedelta(days=10)).strftime("%Y-%m-%d")
        w2_date = (today - timedelta(days=8)).strftime("%Y-%m-%d")
        db.add_workout(w1_date, "Yoga", 25, 120, "Morning flow")
        db.add_workout(w2_date, "Brisk Walk", 20, 95, "Park walk")

        db.add_badge_if_not_exists("First Step", "Started tracking health vitals regularly", "🌱")
        db.add_goal("Daily Steps", 6000.0, (today - timedelta(days=7)).strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d"))

    logger.info(f"Sample dataset '{dataset_key}' seeded successfully.")

def seed_sample_data(db_path="healthtrack.db"):
    """Seeds all 7 preset user profiles with balanced healthy and unhealthy datasets."""
    datasets = ["sedentary", "athlete", "weight_loss", "active_prof", "overtrained", "dehydrated", "cardio_risk"]
    for key in datasets:
        seed_dataset(key, db_path)
    
    # Set default active user to Vidithanjali (User ID 1)
    db = DatabaseManager(db_path)
    users = db.get_all_users()
    if users:
        db.set_active_user(users[0].user_id)

if __name__ == "__main__":
    seed_sample_data()
