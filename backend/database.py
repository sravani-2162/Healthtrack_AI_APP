import sqlite3
import os
from datetime import datetime, date
from contextlib import contextmanager
from backend.logger import logger
from backend.models import User, DailyMetric, Workout, Goal, Badge

class DatabaseError(Exception):
    """Custom exception raised for SQLite database errors."""
    pass

class DatabaseManager:
    """Manages SQLite database connections and table creation for HealthTrack."""
    def __init__(self, db_path="healthtrack.db"):
        self.db_path = db_path
        self._init_db()

    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path, timeout=60.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA busy_timeout=60000;")
            return conn
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to SQLite database at {self.db_path}: {e}")
            raise DatabaseError(f"Database connection error: {e}")

    @contextmanager
    def get_db_connection(self):
        """
        Context manager helper that manages transactions and ALWAYS closes
        the connection on exit, preventing database locking errors.
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        """Creates tables if they do not exist."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # App Settings table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """)

                # Users table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    age INTEGER,
                    height_cm REAL,
                    gender TEXT,
                    password_hash TEXT
                );
                """)

                # Daily Metrics table (Composite UNIQUE on user_id, date)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_metrics (
                    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    date TEXT NOT NULL,
                    weight_kg REAL DEFAULT 0.0,
                    sleep_hours REAL DEFAULT 0.0,
                    water_ml REAL DEFAULT 0.0,
                    calories_consumed REAL DEFAULT 0.0,
                    steps INTEGER DEFAULT 0,
                    avg_heart_rate INTEGER DEFAULT 0,
                    UNIQUE(user_id, date)
                );
                """)

                # Workouts table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS workouts (
                    workout_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    date TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    duration_minutes INTEGER DEFAULT 0,
                    calories_burned REAL DEFAULT 0.0,
                    notes TEXT
                );
                """)

                # Goals table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    goal_type TEXT NOT NULL,
                    target_value REAL NOT NULL,
                    current_value REAL DEFAULT 0.0,
                    start_date TEXT,
                    end_date TEXT,
                    status TEXT DEFAULT 'Active'
                );
                """)

                # Badges table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS badges (
                    badge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    name TEXT NOT NULL,
                    description TEXT,
                    icon TEXT,
                    earned_date TEXT
                );
                """)

                # Wearable Sync Logs
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS wearable_sync_logs (
                    sync_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    sync_timestamp TEXT NOT NULL,
                    steps INTEGER,
                    avg_heart_rate INTEGER,
                    sleep_hours REAL
                );
                """)

                # Ensure missing user_id columns are added if tables already existed
                tables = ["daily_metrics", "workouts", "goals", "badges", "wearable_sync_logs"]
                for tbl in tables:
                    try:
                        cursor.execute(f"ALTER TABLE {tbl} ADD COLUMN user_id INTEGER DEFAULT 1")
                    except sqlite3.OperationalError:
                        pass # Column already exists

                # Migration check for legacy single-column date UNIQUE constraint on daily_metrics
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='daily_metrics'")
                row_sql = cursor.fetchone()
                if row_sql and "date TEXT UNIQUE" in row_sql["sql"]:
                    cursor.execute("ALTER TABLE daily_metrics RENAME TO daily_metrics_old;")
                    cursor.execute("""
                    CREATE TABLE daily_metrics (
                        metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER DEFAULT 1,
                        date TEXT NOT NULL,
                        weight_kg REAL DEFAULT 0.0,
                        sleep_hours REAL DEFAULT 0.0,
                        water_ml REAL DEFAULT 0.0,
                        calories_consumed REAL DEFAULT 0.0,
                        steps INTEGER DEFAULT 0,
                        avg_heart_rate INTEGER DEFAULT 0,
                        UNIQUE(user_id, date)
                    );
                    """)
                    cursor.execute("""
                    INSERT OR IGNORE INTO daily_metrics (metric_id, user_id, date, weight_kg, sleep_hours, water_ml, calories_consumed, steps, avg_heart_rate)
                    SELECT metric_id, user_id, date, weight_kg, sleep_hours, water_ml, calories_consumed, steps, avg_heart_rate FROM daily_metrics_old;
                    """)
                    cursor.execute("DROP TABLE daily_metrics_old;")

                logger.info("Database schema initialized successfully with WAL mode.")

                # Initialize default user if empty
                cursor.execute("SELECT COUNT(*) FROM users")
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                    INSERT INTO users (full_name, age, height_cm, gender, password_hash)
                    VALUES ('Vidithanjali', 20, 155.0, 'Female', 'defaultpass');
                    """)

                # Initialize active_user_id setting if empty
                cursor.execute("SELECT value FROM app_settings WHERE key='active_user_id'")
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO app_settings (key, value) VALUES ('active_user_id', '1')")

        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise DatabaseError(f"Database setup failed: {e}")

    # --- ACTIVE USER & USER MANAGEMENT ---
    def get_active_user_id(self):
        try:
            with self.get_db_connection() as conn:
                row = conn.cursor().execute("SELECT value FROM app_settings WHERE key='active_user_id'").fetchone()
                if row:
                    return int(row["value"])
        except Exception:
            pass
        return 1

    def set_active_user(self, user_id):
        with self.get_db_connection() as conn:
            conn.cursor().execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES ('active_user_id', ?)", (str(user_id),))
        logger.info(f"Switched persistent active user ID to: {user_id}")

    def get_user(self, user_id=None):
        uid = user_id or self.get_active_user_id()
        with self.get_db_connection() as conn:
            row = conn.cursor().execute("SELECT * FROM users WHERE user_id=?", (uid,)).fetchone()
            if not row:
                row = conn.cursor().execute("SELECT * FROM users ORDER BY user_id ASC LIMIT 1").fetchone()
            if row:
                return User(row["user_id"], row["full_name"], row["age"], row["height_cm"], row["gender"], row["password_hash"])
            return User()

    def get_all_users(self):
        with self.get_db_connection() as conn:
            rows = conn.cursor().execute("SELECT * FROM users ORDER BY user_id ASC").fetchall()
            return [User(r["user_id"], r["full_name"], r["age"], r["height_cm"], r["gender"], r["password_hash"]) for r in rows]

    def create_user(self, full_name, age, height_cm, gender, password="pass"):
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO users (full_name, age, height_cm, gender, password_hash)
            VALUES (?, ?, ?, ?, ?)
            """, (full_name, age, height_cm, gender, password))
            new_id = cursor.lastrowid
        
        self.set_active_user(new_id)
        logger.info(f"Created new user '{full_name}' with ID {new_id} and set as active user.")
        return new_id

    def update_user(self, full_name, age, height_cm, gender):
        uid = self.get_active_user_id()
        with self.get_db_connection() as conn:
            conn.cursor().execute("""
            UPDATE users SET full_name=?, age=?, height_cm=?, gender=? WHERE user_id=?
            """, (full_name, age, height_cm, gender, uid))
            logger.info(f"Updated user profile for ID {uid}.")

    def update_password(self, new_password):
        uid = self.get_active_user_id()
        with self.get_db_connection() as conn:
            conn.cursor().execute("UPDATE users SET password_hash=? WHERE user_id=?", (new_password, uid))
            logger.info("Updated user password.")

    # --- METRIC OPERATIONS ---
    def add_or_update_metric(self, date_str, weight_kg, sleep_hours, water_ml, calories_consumed, steps=0, avg_heart_rate=0):
        uid = self.get_active_user_id()
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT metric_id FROM daily_metrics WHERE date=? AND user_id=?", (date_str, uid))
            existing = cursor.fetchone()
            if existing:
                cursor.execute("""
                UPDATE daily_metrics 
                SET weight_kg=?, sleep_hours=?, water_ml=?, calories_consumed=?, steps=?, avg_heart_rate=?
                WHERE metric_id=?
                """, (weight_kg, sleep_hours, water_ml, calories_consumed, steps, avg_heart_rate, existing["metric_id"]))
            else:
                cursor.execute("""
                INSERT INTO daily_metrics (user_id, date, weight_kg, sleep_hours, water_ml, calories_consumed, steps, avg_heart_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (uid, date_str, weight_kg, sleep_hours, water_ml, calories_consumed, steps, avg_heart_rate))

    def get_all_metrics(self, user_id=None):
        uid = user_id or self.get_active_user_id()
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM daily_metrics WHERE user_id=? ORDER BY date ASC", (uid,))
            rows = cursor.fetchall()
            return [DailyMetric(r["metric_id"], r["date"], r["weight_kg"], r["sleep_hours"], 
                               r["water_ml"], r["calories_consumed"], r["steps"], r["avg_heart_rate"]) for r in rows]

    # --- WORKOUT OPERATIONS ---
    def add_workout(self, date_str, activity_type, duration_minutes, calories_burned, notes=""):
        uid = self.get_active_user_id()
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO workouts (user_id, date, activity_type, duration_minutes, calories_burned, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (uid, date_str, activity_type, duration_minutes, calories_burned, notes))

    def get_all_workouts(self, user_id=None):
        uid = user_id or self.get_active_user_id()
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM workouts WHERE user_id=? ORDER BY date ASC", (uid,))
            rows = cursor.fetchall()
            return [Workout(r["workout_id"], r["date"], r["activity_type"], r["duration_minutes"], 
                           r["calories_burned"], r["notes"]) for r in rows]

    # --- GOALS OPERATIONS ---
    def add_goal(self, goal_type, target_value, start_date, end_date):
        uid = self.get_active_user_id()
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO goals (user_id, goal_type, target_value, current_value, start_date, end_date, status)
            VALUES (?, ?, ?, 0.0, ?, ?, 'Active')
            """, (uid, goal_type, target_value, start_date, end_date))

    def get_all_goals(self, user_id=None):
        uid = user_id or self.get_active_user_id()
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM goals WHERE user_id=? ORDER BY goal_id DESC", (uid,))
            rows = cursor.fetchall()
            return [Goal(r["goal_id"], r["goal_type"], r["target_value"], r["current_value"], 
                         r["start_date"], r["end_date"], r["status"]) for r in rows]

    # --- BADGES OPERATIONS ---
    def get_earned_badges(self, user_id=None):
        uid = user_id or self.get_active_user_id()
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM badges WHERE user_id=? ORDER BY earned_date DESC", (uid,))
            rows = cursor.fetchall()
            return [Badge(r["badge_id"], r["name"], r["description"], r["icon"], r["earned_date"]) for r in rows]

    def add_badge_if_not_exists(self, name, description, icon="🏆", earned_date=""):
        uid = self.get_active_user_id()
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT badge_id FROM badges WHERE name=? AND user_id=?", (name, uid))
            if not cursor.fetchone():
                e_date = earned_date or date.today().strftime("%Y-%m-%d")
                cursor.execute("""
                INSERT INTO badges (user_id, name, description, icon, earned_date)
                VALUES (?, ?, ?, ?, ?)
                """, (uid, name, description, icon, e_date))

    # --- WEARABLE SYNC ---
    def record_wearable_sync(self, steps, avg_heart_rate, sleep_hours, date_str):
        uid = self.get_active_user_id()
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
            INSERT INTO wearable_sync_logs (user_id, sync_timestamp, steps, avg_heart_rate, sleep_hours)
            VALUES (?, ?, ?, ?, ?)
            """, (uid, now_ts, steps, avg_heart_rate, sleep_hours))
            
            cursor.execute("SELECT weight_kg, water_ml, calories_consumed FROM daily_metrics WHERE date=? AND user_id=?", (date_str, uid))
            existing = cursor.fetchone()
            w_kg = existing["weight_kg"] if existing else 60.0
            w_ml = existing["water_ml"] if existing else 1500.0
            c_cons = existing["calories_consumed"] if existing else 2000.0

        self.add_or_update_metric(date_str, w_kg, sleep_hours, w_ml, c_cons, steps, avg_heart_rate)
        logger.info(f"Recorded wearable sync data for user ID {uid} successfully.")
