import sys
import os
from backend.logger import setup_logger
from seed_data import seed_sample_data
from app_gui import HealthTrackApp

def main():
    # 1. Setup Logging
    logger = setup_logger("healthtrack_app.log")
    logger.info("Initializing HealthTrack AI — Intelligent Health Monitoring & Wellness Platform...")

    # 2. Seed database with initial 14-day sample data if fresh installation
    db_file = "healthtrack.db"
    if not os.path.exists(db_file):
        logger.info("Database file not found. Creating and seeding initial data...")
        seed_sample_data(db_file)
    else:
        # Check if database is empty
        from backend.database import DatabaseManager
        db = DatabaseManager(db_file)
        if len(db.get_all_metrics()) == 0:
            logger.info("Database is empty. Seeding initial data...")
            seed_sample_data(db_file)

    # 3. Start Tkinter Main Application Loop
    logger.info("Starting Tkinter Desktop GUI...")
    app = HealthTrackApp(db_file)
    app.mainloop()

if __name__ == "__main__":
    main()
