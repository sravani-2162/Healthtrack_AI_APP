import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backend.logger import logger
from backend.models import HealthPattern, Recommendation

class HealthAnalyticsEngine:
    """
    Pandas-powered analytics engine for HealthTrack.
    Computes rolling averages, wellness scores, 14-day unhealthy patterns, 
    personalized recommendations, and summary reports.
    """

    @staticmethod
    def metrics_to_dataframe(metrics_list):
        if not metrics_list:
            return pd.DataFrame(columns=[
                "date", "weight_kg", "sleep_hours", "water_ml", 
                "calories_consumed", "steps", "avg_heart_rate"
            ])
        
        data = [m.to_dict() for m in metrics_list]
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        return df

    @staticmethod
    def workouts_to_dataframe(workouts_list):
        if not workouts_list:
            return pd.DataFrame(columns=["date", "activity_type", "duration_minutes", "calories_burned"])
        
        data = [w.to_dict() for w in workouts_list]
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        return df

    @classmethod
    def calculate_wellness_score(cls, df_metrics, df_workouts):
        """
        Calculates a personalized wellness score between 0 and 100.
        Evaluates 7-day rolling performance:
        - Sleep (target: 7-9 hrs) -> 25 pts
        - Hydration (target: 2000-3000 ml) -> 25 pts
        - Physical Activity (target: 20-30 mins/day or 150m/week) -> 30 pts
        - Consistency/Log frequency -> 20 pts
        """
        if df_metrics.empty:
            return 50, "Needs Data"

        recent = df_metrics.tail(7)
        
        # 1. Sleep score (max 25)
        avg_sleep = recent["sleep_hours"].mean() if not recent.empty else 0
        if 7.0 <= avg_sleep <= 9.0:
            sleep_score = 25
        elif 5.5 <= avg_sleep < 7.0 or 9.0 < avg_sleep <= 10.0:
            sleep_score = 18
        elif avg_sleep > 0:
            sleep_score = 10
        else:
            sleep_score = 0

        # 2. Water score (max 25)
        avg_water = recent["water_ml"].mean() if not recent.empty else 0
        if avg_water >= 2000:
            water_score = 25
        elif avg_water >= 1200:
            water_score = 16
        elif avg_water > 0:
            water_score = 8
        else:
            water_score = 0

        # 3. Exercise score (max 30)
        recent_workouts = df_workouts[df_workouts["date"] >= (pd.Timestamp.now() - pd.Timedelta(days=7))] if not df_workouts.empty else pd.DataFrame()
        total_ex_mins = recent_workouts["duration_minutes"].sum() if not recent_workouts.empty else 0
        if total_ex_mins >= 150:
            ex_score = 30
        elif total_ex_mins >= 90:
            ex_score = 22
        elif total_ex_mins >= 30:
            ex_score = 12
        else:
            ex_score = 4

        # 4. Consistency score (max 20)
        logged_days = len(recent)
        consistency_score = min(20, logged_days * 3)

        total_score = int(sleep_score + water_score + ex_score + consistency_score)
        total_score = max(0, min(100, total_score))

        if total_score >= 80:
            status = "Optimal"
        elif total_score >= 60:
            status = "Moderate"
        else:
            status = "Needs Improvement"

        return total_score, status

    @classmethod
    def detect_patterns(cls, df_metrics, df_workouts):
        """
        Analyzes the last 14 days of data to detect unhealthy patterns.
        """
        patterns = []

        # Filter last 14 days
        cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=14)
        m_14 = df_metrics[df_metrics["date"] >= cutoff_date] if not df_metrics.empty else pd.DataFrame()
        w_14 = df_workouts[df_workouts["date"] >= cutoff_date] if not df_workouts.empty else pd.DataFrame()

        # Pattern 1: Low Exercise (HIGH severity)
        total_mins_2w = w_14["duration_minutes"].sum() if not w_14.empty else 0
        estimated_weekly = int(total_mins_2w / 2) if len(m_14) > 7 else total_mins_2w

        if estimated_weekly < 150:
            patterns.append(HealthPattern(
                title="Low Exercise",
                severity="HIGH",
                description="The WHO recommends at least 150 minutes of moderate activity per week. Physical inactivity increases risk of cardiovascular disease, weakens musculoskeletal health, and negatively affects mood and sleep quality.",
                detail_text=f"Estimated weekly activity: {estimated_weekly} minutes (recommended: 150)."
            ))

        # Pattern 2: Missed Workouts / Consecutive inactive days (MEDIUM severity)
        if w_14.empty:
            patterns.append(HealthPattern(
                title="Missed Workouts",
                severity="MEDIUM",
                description="Consecutive missed workout days can break momentum and habit formation, making it progressively harder to resume a consistent exercise routine.",
                detail_text="No exercise logged in the last 14 days."
            ))
        else:
            last_workout_date = w_14["date"].max()
            days_since = (pd.Timestamp.now() - last_workout_date).days
            if days_since >= 3:
                patterns.append(HealthPattern(
                    title="Missed Workouts",
                    severity="MEDIUM",
                    description="Consecutive missed workout days can break momentum and habit formation, making it progressively harder to resume a consistent exercise routine.",
                    detail_text=f"No exercise logged in the last {days_since} days."
                ))

        # Pattern 3: Sleep Deficit (HIGH / MEDIUM severity)
        if not m_14.empty:
            avg_sleep = m_14["sleep_hours"].mean()
            if avg_sleep < 6.0:
                patterns.append(HealthPattern(
                    title="Sleep Deficit",
                    severity="HIGH",
                    description="Chronic sleep deprivation (<6 hours/night) impairs cognitive function, weakens immune response, and increases stress levels.",
                    detail_text=f"14-day average sleep: {avg_sleep:.1f} hours/night (recommended: 7-8h)."
                ))
            elif avg_sleep < 7.0:
                patterns.append(HealthPattern(
                    title="Mild Sleep Shortfall",
                    severity="MEDIUM",
                    description="Slightly below optimal sleep target. Adequate sleep enhances recovery and daily energy.",
                    detail_text=f"14-day average sleep: {avg_sleep:.1f} hours/night."
                ))

        # Pattern 4: Dehydration Risk (HIGH / MEDIUM severity)
        if not m_14.empty:
            avg_water = m_14["water_ml"].mean()
            if avg_water < 1100:
                patterns.append(HealthPattern(
                    title="Severe Dehydration Risk",
                    severity="HIGH",
                    description="Extremely low fluid intake (<1100 ml/day) poses high risks of acute fatigue, impaired cognitive performance, kidney strain, and electrolyte imbalance.",
                    detail_text=f"14-day average hydration: {int(avg_water)} ml/day (recommended: 2000+ ml)."
                ))
            elif avg_water < 1500:
                patterns.append(HealthPattern(
                    title="Insufficient Hydration",
                    severity="MEDIUM",
                    description="Inadequate daily fluid intake leads to fatigue, reduced muscle performance, and sluggish metabolism.",
                    detail_text=f"14-day average hydration: {int(avg_water)} ml/day (recommended: 2000+ ml)."
                ))

        # Pattern 5: Elevated Resting Heart Rate / Stress Warning (HIGH / MEDIUM severity)
        if not m_14.empty and "avg_heart_rate" in m_14.columns:
            avg_hr = m_14["avg_heart_rate"].mean()
            if avg_hr >= 80:
                patterns.append(HealthPattern(
                    title="Elevated Resting Heart Rate",
                    severity="HIGH",
                    description="Persistent resting heart rate above 80 bpm suggests high autonomic nervous system stress, overtraining, anxiety, or systemic inflammation.",
                    detail_text=f"14-day average resting HR: {int(avg_hr)} bpm (optimal target: 58-70 bpm)."
                ))
            elif avg_hr >= 76:
                patterns.append(HealthPattern(
                    title="Mild Heart Rate Elevation",
                    severity="MEDIUM",
                    description="Slightly elevated resting heart rate indicates potential physical fatigue or inadequate sleep recovery.",
                    detail_text=f"14-day average resting HR: {int(avg_hr)} bpm."
                ))

        # Pattern 6: Upward Weight Trajectory (MEDIUM severity)
        if not m_14.empty and len(m_14) >= 7 and "weight_kg" in m_14.columns:
            first_w = m_14.iloc[0]["weight_kg"]
            last_w = m_14.iloc[-1]["weight_kg"]
            if first_w > 0 and last_w > 0 and (last_w - first_w) >= 1.0:
                diff = round(last_w - first_w, 1)
                patterns.append(HealthPattern(
                    title="Rapid Weight Gain Trajectory",
                    severity="MEDIUM",
                    description="Upward weight trend observed over 14 days. Ensure balanced calorie intake and consistent daily physical activity.",
                    detail_text=f"14-day weight shift: +{diff} kg ({first_w:.1f} kg -> {last_w:.1f} kg)."
                ))

        return patterns

    @classmethod
    def generate_recommendations(cls, patterns, df_metrics):
        """
        Produces actionable health recommendations aligned with detected patterns.
        """
        recs = []
        added_categories = set()

        for p in patterns:
            if ("Exercise" in p.title or "Workouts" in p.title) and "Exercise" not in added_categories:
                recs.append(Recommendation(
                    category="Exercise",
                    priority="HIGH",
                    recommendation_text="Schedule at least 20-30 minutes of moderate activity (brisk walk, cycling, or yoga) today to rebuild momentum."
                ))
                added_categories.add("Exercise")
            elif "Sleep" in p.title and "Sleep" not in added_categories:
                recs.append(Recommendation(
                    category="Sleep",
                    priority="HIGH" if p.severity == "HIGH" else "MEDIUM",
                    recommendation_text="Establish a wind-down routine 45 minutes before bedtime. Avoid blue light and target 7.5 to 8 hours of sleep."
                ))
                added_categories.add("Sleep")
            elif "Hydration" in p.title and "Hydration" not in added_categories:
                recs.append(Recommendation(
                    category="Hydration",
                    priority="HIGH" if p.severity == "HIGH" else "MEDIUM",
                    recommendation_text="Increase fluid intake - keep a bottle at your desk and aim for a glass of water every 1-2 hours to reach 2000+ ml."
                ))
                added_categories.add("Hydration")
            elif ("Heart Rate" in p.title or "Stress" in p.title) and "Stress" not in added_categories:
                recs.append(Recommendation(
                    category="Stress & Recovery",
                    priority="HIGH" if p.severity == "HIGH" else "MEDIUM",
                    recommendation_text="Incorporate active recovery, stress management techniques (breathwork, meditation), and prioritize uninterrupted sleep to lower resting HR."
                ))
                added_categories.add("Stress")
            elif "Weight" in p.title and "Nutrition" not in added_categories:
                recs.append(Recommendation(
                    category="Nutrition & Weight",
                    priority="MEDIUM",
                    recommendation_text="Monitor daily caloric balance and emphasize whole foods, high protein, and low sugar to stabilize weight."
                ))
                added_categories.add("Nutrition")

        if "Hydration" not in added_categories:
            recs.append(Recommendation(
                category="Hydration",
                priority="MEDIUM",
                recommendation_text="Increase water intake - keep a bottle at your desk and aim for a glass every 1-2 hours to hit your daily goal."
            ))

        if "Exercise" not in added_categories:
            recs.append(Recommendation(
                category="Exercise",
                priority="MEDIUM",
                recommendation_text="Maintain your weekly exercise schedule to protect cardiovascular health and boost energy."
            ))

        return recs

    @classmethod
    def compute_reports_summary(cls, df_metrics, df_workouts, timeframe="weekly"):
        """
        Computes aggregated summary stats for Reports view (Weekly vs Monthly).
        """
        days = 7 if timeframe == "weekly" else 30
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)

        m_sub = df_metrics[df_metrics["date"] >= cutoff] if not df_metrics.empty else pd.DataFrame()
        w_sub = df_workouts[df_workouts["date"] >= cutoff] if not df_workouts.empty else pd.DataFrame()

        avg_sleep = round(m_sub["sleep_hours"].mean(), 1) if not m_sub.empty and "sleep_hours" in m_sub.columns else 0.0
        avg_water = int(m_sub["water_ml"].mean()) if not m_sub.empty and "water_ml" in m_sub.columns else 0

        # Weight change calculation
        weight_change_str = "- kg"
        date_range_str = f"{cutoff.strftime('%Y-%m-%d')} -> {pd.Timestamp.now().strftime('%Y-%m-%d')}"
        
        if not m_sub.empty and len(m_sub) >= 2:
            first_w = m_sub.iloc[0]["weight_kg"]
            last_w = m_sub.iloc[-1]["weight_kg"]
            if first_w > 0 and last_w > 0:
                diff = round(last_w - first_w, 1)
                sign = "+" if diff > 0 else ""
                weight_change_str = f"{sign}{diff} kg"

        workout_count = len(w_sub) if not w_sub.empty else 0
        total_workout_mins = int(w_sub["duration_minutes"].sum()) if not w_sub.empty else 0
        total_calories_burned = int(w_sub["calories_burned"].sum()) if not w_sub.empty else 0

        wellness_score, score_label = cls.calculate_wellness_score(df_metrics, df_workouts)

        return {
            "timeframe": timeframe,
            "wellness_score": wellness_score,
            "score_label": score_label,
            "avg_sleep": avg_sleep,
            "avg_water": avg_water,
            "weight_change": weight_change_str,
            "date_range": date_range_str,
            "workout_count": workout_count,
            "workout_mins": total_workout_mins,
            "calories_burned": total_calories_burned
        }

    @classmethod
    def calculate_streak(cls, df_workouts):
        """Calculates consecutive workout days streak."""
        if df_workouts.empty:
            return 0

        dates = df_workouts["date"].dt.date.unique()
        dates = sorted(dates, reverse=True)
        
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        if not dates:
            return 0

        if dates[0] not in (today, yesterday):
            return 0

        streak = 0
        current_check = dates[0]
        for d in dates:
            if d == current_check:
                streak += 1
                current_check -= timedelta(days=1)
            else:
                break
        return streak
