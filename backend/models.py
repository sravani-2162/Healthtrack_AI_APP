from datetime import datetime, date

class User:
    """Represents the user profile in HealthTrack."""
    def __init__(self, user_id=1, full_name="Vidithanjali", age=20, height_cm=155.0, gender="Female", password_hash=""):
        self.user_id = user_id
        self.full_name = full_name
        self.age = age
        self.height_cm = height_cm
        self.gender = gender
        self.password_hash = password_hash

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "full_name": self.full_name,
            "age": self.age,
            "height_cm": self.height_cm,
            "gender": self.gender
        }


class DailyMetric:
    """Represents daily health vitals (weight, sleep, water, calories)."""
    def __init__(self, metric_id=None, date_str=None, weight_kg=0.0, sleep_hours=0.0, 
                 water_ml=0.0, calories_consumed=0.0, steps=0, avg_heart_rate=0):
        self.metric_id = metric_id
        self.date_str = date_str or date.today().strftime("%Y-%m-%d")
        self.weight_kg = float(weight_kg)
        self.sleep_hours = float(sleep_hours)
        self.water_ml = float(water_ml)
        self.calories_consumed = float(calories_consumed)
        self.steps = int(steps)
        self.avg_heart_rate = int(avg_heart_rate)

    @property
    def date(self):
        return self.date_str

    def to_dict(self):
        return {
            "metric_id": self.metric_id,
            "date": self.date_str,
            "weight_kg": self.weight_kg,
            "sleep_hours": self.sleep_hours,
            "water_ml": self.water_ml,
            "calories_consumed": self.calories_consumed,
            "steps": self.steps,
            "avg_heart_rate": self.avg_heart_rate
        }


class Workout:
    """Represents an exercise/workout session."""
    def __init__(self, workout_id=None, date_str=None, activity_type="Exercise", 
                 duration_minutes=0, calories_burned=0, notes=""):
        self.workout_id = workout_id
        self.date_str = date_str or date.today().strftime("%Y-%m-%d")
        self.activity_type = activity_type
        self.duration_minutes = int(duration_minutes)
        self.calories_burned = float(calories_burned)
        self.notes = notes

    @property
    def date(self):
        return self.date_str

    def to_dict(self):
        return {
            "workout_id": self.workout_id,
            "date": self.date_str,
            "activity_type": self.activity_type,
            "duration_minutes": self.duration_minutes,
            "calories_burned": self.calories_burned,
            "notes": self.notes
        }


class Goal:
    """Represents a wellness target set by the user."""
    def __init__(self, goal_id=None, goal_type="Exercise Minutes", target_value=150.0, 
                 current_value=0.0, start_date=None, end_date=None, status="Active"):
        self.goal_id = goal_id
        self.goal_type = goal_type
        self.target_value = float(target_value)
        self.current_value = float(current_value)
        self.start_date = start_date or date.today().strftime("%Y-%m-%d")
        self.end_date = end_date or ""
        self.status = status

    @property
    def progress_percent(self):
        if self.target_value <= 0:
            return 0.0
        return min(100.0, round((self.current_value / self.target_value) * 100, 1))

    def to_dict(self):
        return {
            "goal_id": self.goal_id,
            "goal_type": self.goal_type,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "progress_percent": self.progress_percent,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status
        }


class Badge:
    """Represents an earned milestone or achievement badge."""
    def __init__(self, badge_id=None, name="", description="", icon="🏆", earned_date=""):
        self.badge_id = badge_id
        self.name = name
        self.description = description
        self.icon = icon
        self.earned_date = earned_date or date.today().strftime("%Y-%m-%d")

    def to_dict(self):
        return {
            "badge_id": self.badge_id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "earned_date": self.earned_date
        }


class HealthPattern:
    """Represents an identified unhealthy pattern or habit risk."""
    def __init__(self, title, severity, description, detail_text):
        self.title = title
        self.severity = severity  # 'HIGH', 'MEDIUM', 'LOW'
        self.description = description
        self.detail_text = detail_text

    def to_dict(self):
        return {
            "title": self.title,
            "severity": self.severity,
            "description": self.description,
            "detail_text": self.detail_text
        }


class Recommendation:
    """Represents dynamic personalized health & wellness advice."""
    def __init__(self, category, priority, recommendation_text):
        self.category = category  # e.g., 'Hydration', 'Exercise', 'Sleep'
        self.priority = priority  # 'HIGH', 'MEDIUM', 'LOW'
        self.recommendation_text = recommendation_text

    def to_dict(self):
        return {
            "category": self.category,
            "priority": self.priority,
            "recommendation_text": self.recommendation_text
        }
