import json
import csv
import os
from backend.logger import logger

class DataExporter:
    """Exports HealthTrack metrics, workouts, patterns, and reports to JSON and CSV formats."""

    @staticmethod
    def export_to_json(metrics, workouts, summary_data, file_path="healthtrack_report.json"):
        """Exports data to a formatted JSON file."""
        try:
            export_payload = {
                "system": "HealthTrack Wellness Tracking System",
                "export_date": summary_data.get("date_range", ""),
                "summary": summary_data,
                "daily_metrics": [m.to_dict() for m in metrics],
                "workouts": [w.to_dict() for w in workouts]
            }
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_payload, f, indent=4)
            logger.info(f"Report successfully exported to JSON: {file_path}")
            return True, file_path
        except Exception as e:
            logger.error(f"Failed to export JSON report: {e}")
            return False, str(e)

    @staticmethod
    def export_to_csv(metrics, file_path="healthtrack_metrics.csv"):
        """Exports daily metrics to CSV file."""
        try:
            if not metrics:
                return False, "No metric data available to export."

            fieldnames = ["metric_id", "date", "weight_kg", "sleep_hours", "water_ml", "calories_consumed", "steps", "avg_heart_rate"]
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for m in metrics:
                    writer.writerow(m.to_dict())

            logger.info(f"Metrics successfully exported to CSV: {file_path}")
            return True, file_path
        except Exception as e:
            logger.error(f"Failed to export CSV report: {e}")
            return False, str(e)
