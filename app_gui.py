import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from backend.database import DatabaseManager
from backend.logger import logger

from views.dashboard_view import DashboardView
from views.log_data_view import LogDataView
from views.trends_view import TrendsView
from views.patterns_view import PatternsView
from views.recommendations_view import RecommendationsView
from views.reports_view import ReportsView
from views.goals_badges_view import GoalsBadgesView
from views.profile_view import ProfileView

class HealthTrackApp(tk.Tk):
    """
    Main Tkinter Desktop Application for HealthTrack.
    Manages left navigation sidebar, theme styles, user login/registration, and view switching.
    """
    def __init__(self, db_path="healthtrack.db"):
        super().__init__()
        self.title("HealthTrack AI — Intelligent Health Monitoring & Wellness Platform")
        self.geometry("1180x740")
        self.minsize(980, 660)
        self.configure(bg="#f6f8f5")

        self.db = DatabaseManager(db_path)
        self.current_view_name = "Dashboard"
        self.nav_buttons = {}

        self.setup_styles()
        self.build_ui()
        self.show_view("Dashboard")

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Custom TTK entry & combobox styles
        style.configure("TEntry", fieldbackground="#ffffff", bordercolor="#cbd5e0", padding=5)
        style.configure("TCombobox", fieldbackground="#ffffff", bordercolor="#cbd5e0", padding=5)

    def build_ui(self):
        # 1. Main Horizontal Split (Left Sidebar + Right Main Content)
        self.main_container = tk.Frame(self, bg="#f6f8f5")
        self.main_container.pack(fill="both", expand=True)

        # 2. Left Navigation Sidebar
        self.sidebar = tk.Frame(self.main_container, bg="#0d2b20", width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # --- Sidebar Header ---
        header_f = tk.Frame(self.sidebar, bg="#0d2b20", padx=15, pady=20)
        header_f.pack(fill="x")

        top_b_f = tk.Frame(header_f, bg="#0d2b20")
        top_b_f.pack(anchor="w")

        dot_lbl = tk.Label(top_b_f, text="●", font=("Segoe UI", 11), fg="#38a169", bg="#0d2b20")
        dot_lbl.pack(side="left", padx=(0, 6))

        brand_lbl = tk.Label(top_b_f, text="HEALTHTRACK AI", font=("Georgia", 13, "bold"), fg="#ffffff", bg="#0d2b20")
        brand_lbl.pack(side="left")

        sub_brand_lbl = tk.Label(header_f, text="Intelligent Health Monitoring & Wellness Platform", font=("Segoe UI", 7, "bold"), fg="#809488", bg="#0d2b20", wraplength=200, justify="left")
        sub_brand_lbl.pack(anchor="w", pady=(4, 0))

        # --- Navigation Items ---
        self.nav_frame = tk.Frame(self.sidebar, bg="#0d2b20", padx=10, pady=10)
        self.nav_frame.pack(fill="x", expand=True, anchor="n")

        nav_items = [
            ("Dashboard", "🌐  Dashboard"),
            ("Log Data", "✏  Log Data"),
            ("Trends", "📈  Trends"),
            ("Patterns", "🚩  Patterns"),
            ("Recommendations", "✔️  Recommendations"),
            ("Reports", "📑  Reports"),
            ("Goals & Badges", "⭐  Goals & Badges"),
            ("Profile", "👤  Profile")
        ]

        for key, label in nav_items:
            btn = tk.Button(self.nav_frame, text=label, font=("Segoe UI", 10, "bold"),
                            fg="#a0aec0", bg="#0d2b20", activebackground="#16382b", activeforeground="#ffffff",
                            anchor="w", padx=15, pady=8, bd=0, relief="flat", cursor="hand2",
                            command=lambda k=key: self.show_view(k))
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn

        # --- Sidebar Footer (Logged-in user & Log out button) ---
        footer_f = tk.Frame(self.sidebar, bg="#0d2b20", padx=20, pady=20)
        footer_f.pack(side="bottom", fill="x")

        user = self.db.get_user()
        user_fn = user.full_name.split()[0] if user.full_name else "User"

        tk.Label(footer_f, text="Signed in as", font=("Segoe UI", 8), fg="#718096", bg="#0d2b20").pack(anchor="w")
        self.user_lbl = tk.Label(footer_f, text=user_fn, font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#0d2b20")
        self.user_lbl.pack(anchor="w", pady=(0, 10))

        btn_logout = tk.Button(footer_f, text="⏻ Log out", font=("Segoe UI", 9, "bold"),
                               fg="#e53e3e", bg="#0d2b20", activebackground="#16382b", activeforeground="#e53e3e",
                               anchor="w", bd=0, relief="flat", cursor="hand2", command=self.handle_logout)
        btn_logout.pack(anchor="w")

        # 3. Right Content View Container
        self.content_area = tk.Frame(self.main_container, bg="#f6f8f5")
        self.content_area.pack(side="right", fill="both", expand=True)

    def show_view(self, view_name):
        self.current_view_name = view_name
        logger.info(f"Switching view to: {view_name}")

        # Update button sidebar highlighting
        for k, btn in self.nav_buttons.items():
            if k == view_name:
                btn.config(bg="#16382b", fg="#ffffff")
            else:
                btn.config(bg="#0d2b20", fg="#a0aec0")

        # Clear active content area
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Instantiate requested view frame
        if view_name == "Dashboard":
            view = DashboardView(self.content_area, self.db)
        elif view_name == "Log Data":
            view = LogDataView(self.content_area, self.db, refresh_callback=self.update_user_label)
        elif view_name == "Trends":
            view = TrendsView(self.content_area, self.db)
        elif view_name == "Patterns":
            view = PatternsView(self.content_area, self.db)
        elif view_name == "Recommendations":
            view = RecommendationsView(self.content_area, self.db)
        elif view_name == "Reports":
            view = ReportsView(self.content_area, self.db)
        elif view_name == "Goals & Badges":
            view = GoalsBadgesView(self.content_area, self.db)
        elif view_name == "Profile":
            view = ProfileView(self.content_area, self.db, refresh_callback=self.update_user_label)
        else:
            view = DashboardView(self.content_area, self.db)

        view.pack(fill="both", expand=True)

    def update_user_label(self):
        user = self.db.get_user()
        user_fn = user.full_name.split()[0] if user.full_name else "User"
        self.user_lbl.config(text=user_fn)

    def handle_logout(self):
        """Log out dialog allowing switching user, creating new user, or exiting."""
        dlg = tk.Toplevel(self)
        dlg.title("Log Out & Switch User")
        dlg.geometry("420x350")
        dlg.configure(bg="#ffffff")
        dlg.transient(self)
        dlg.grab_set()

        tk.Label(dlg, text="USER ACCOUNT MENU", font=("Segoe UI", 9, "bold"), fg="#136349", bg="#ffffff").pack(pady=(20, 5))
        tk.Label(dlg, text="Select an action to continue", font=("Georgia", 14, "bold"), fg="#1a201c", bg="#ffffff").pack()

        users = self.db.get_all_users()
        users_dict = {f"{u.full_name} (ID: {u.user_id})": u.user_id for u in users}

        # Switch User Section
        f_sw = tk.Frame(dlg, bg="#ffffff", padx=20, pady=10)
        f_sw.pack(fill="x")
        tk.Label(f_sw, text="Switch Active User:", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")

        user_combo = ttk.Combobox(f_sw, values=list(users_dict.keys()), font=("Segoe UI", 10), state="readonly")
        curr_u = self.db.get_user()
        user_combo.set(f"{curr_u.full_name} (ID: {curr_u.user_id})")
        user_combo.pack(fill="x", pady=5)

        def switch_user_action():
            sel = user_combo.get()
            if sel in users_dict:
                uid = users_dict[sel]
                self.db.set_active_user(uid)
                self.update_user_label()
                self.show_view("Dashboard")
                dlg.destroy()
                messagebox.showinfo("Logged In", f"Switched user account to {sel}!")

        btn_sw = tk.Button(f_sw, text="Switch Account", font=("Segoe UI", 9, "bold"), 
                           fg="#ffffff", bg="#136349", activebackground="#0f4d39", activeforeground="#ffffff", 
                           relief="flat", pady=5, cursor="hand2", command=switch_user_action)
        btn_sw.pack(fill="x", pady=5)

        # Create New User Button
        f_create = tk.Frame(dlg, bg="#ffffff", padx=20, pady=5)
        f_create.pack(fill="x")
        
        def open_create_user_modal():
            dlg.destroy()
            self.show_view("Profile")

        btn_new = tk.Button(f_create, text="➕ Create New User Profile", font=("Segoe UI", 9, "bold"),
                            fg="#1a201c", bg="#edf2f7", activebackground="#cbd5e0", activeforeground="#1a201c",
                            relief="flat", pady=6, cursor="hand2", command=open_create_user_modal)
        btn_new.pack(fill="x")

        # Exit App Button
        f_exit = tk.Frame(dlg, bg="#ffffff", padx=20, pady=15)
        f_exit.pack(fill="x")

        def exit_app_action():
            dlg.destroy()
            self.quit_app()

        btn_exit = tk.Button(f_exit, text="⏻ Exit Application", font=("Segoe UI", 9, "bold"),
                             fg="#e53e3e", bg="#ffffff", activebackground="#fff5f5", activeforeground="#e53e3e",
                             relief="solid", bd=1, pady=5, cursor="hand2", command=exit_app_action)
        btn_exit.pack(fill="x")

    def quit_app(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to close HealthTrack?"):
            logger.info("Application closed by user.")
            self.destroy()
