import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from backend.logger import logger

class ProfileView(tk.Frame):
    """
    Profile View: Edit profile info, update password, and simulate wearable sync
    matching exact layout from screenshot 1.
    """
    def __init__(self, parent, db, refresh_callback=None):
        super().__init__(parent, bg="#f6f8f5")
        self.db = db
        self.refresh_callback = refresh_callback
        self.build_ui()

    def build_ui(self):
        # Header
        header_frame = tk.Frame(self, bg="#f6f8f5")
        header_frame.pack(fill="x", padx=30, pady=(25, 10))

        sub_label = tk.Label(header_frame, text="ACCOUNT", font=("Segoe UI", 9, "bold"), 
                             fg="#136349", bg="#f6f8f5")
        sub_label.pack(anchor="w")

        title_label = tk.Label(header_frame, text="Profile", font=("Georgia", 24, "bold"), 
                               fg="#1a201c", bg="#f6f8f5")
        title_label.pack(anchor="w")

        container = tk.Frame(self, bg="#f6f8f5")
        container.pack(fill="both", expand=True, padx=30, pady=10)

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

        user = self.db.get_user()

        # --- LEFT PANEL: EDIT PROFILE ---
        card_edit = tk.Frame(container, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=25, pady=20)
        card_edit.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        tk.Label(card_edit, text="EDIT PROFILE", font=("Segoe UI", 9, "bold"), fg="#718096", bg="#ffffff").pack(anchor="w", pady=(0, 15))

        # Full Name
        tk.Label(card_edit, text="Full name", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.name_entry = ttk.Entry(card_edit, font=("Segoe UI", 10))
        self.name_entry.insert(0, user.full_name)
        self.name_entry.pack(fill="x", pady=(2, 12))

        # Age & Height Row
        row_ah = tk.Frame(card_edit, bg="#ffffff")
        row_ah.pack(fill="x", pady=(0, 12))

        # Age
        f_age = tk.Frame(row_ah, bg="#ffffff")
        f_age.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(f_age, text="Age", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.age_entry = ttk.Entry(f_age, font=("Segoe UI", 10))
        self.age_entry.insert(0, str(user.age))
        self.age_entry.pack(fill="x", pady=(2, 0))

        # Height
        f_h = tk.Frame(row_ah, bg="#ffffff")
        f_h.pack(side="right", fill="x", expand=True, padx=(5, 0))
        tk.Label(f_h, text="Height (cm)", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.height_entry = ttk.Entry(f_h, font=("Segoe UI", 10))
        self.height_entry.insert(0, str(int(user.height_cm)))
        self.height_entry.pack(fill="x", pady=(2, 0))

        # Gender
        tk.Label(card_edit, text="Gender", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.gender_combo = ttk.Combobox(card_edit, values=["Female", "Male", "Non-binary", "Other"], font=("Segoe UI", 10))
        self.gender_combo.set(user.gender)
        self.gender_combo.pack(fill="x", pady=(2, 20))

        btn_save_prof = tk.Button(card_edit, text="Save changes", font=("Segoe UI", 10, "bold"), 
                                  fg="#ffffff", bg="#136349", activebackground="#0f4d39", activeforeground="#ffffff", 
                                  relief="flat", pady=7, padx=15, cursor="hand2", command=self.save_profile)
        btn_save_prof.pack(anchor="w")

        # --- RIGHT PANEL: CHANGE PASSWORD & WEARABLE SYNC ---
        card_right = tk.Frame(container, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=25, pady=20)
        card_right.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        # Section 1: Change Password
        tk.Label(card_right, text="CHANGE PASSWORD", font=("Segoe UI", 9, "bold"), fg="#718096", bg="#ffffff").pack(anchor="w", pady=(0, 10))

        tk.Label(card_right, text="Current password", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.curr_pass_entry = ttk.Entry(card_right, show="*", font=("Segoe UI", 10))
        self.curr_pass_entry.pack(fill="x", pady=(2, 8))

        tk.Label(card_right, text="New password", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.new_pass_entry = ttk.Entry(card_right, show="*", font=("Segoe UI", 10))
        self.new_pass_entry.pack(fill="x", pady=(2, 10))

        btn_up_pass = tk.Button(card_right, text="Update password", font=("Segoe UI", 9, "bold"), 
                                fg="#1a201c", bg="#ffffff", activebackground="#edf2f7", activeforeground="#1a201c", 
                                relief="solid", bd=1, pady=4, padx=12, cursor="hand2", command=self.update_pass)
        btn_up_pass.pack(anchor="w", pady=(0, 20))

        # Section 2: Simulate Wearable Sync
        tk.Label(card_right, text="SIMULATE WEARABLE SYNC", font=("Segoe UI", 9, "bold"), fg="#718096", bg="#ffffff").pack(anchor="w", pady=(0, 10))

        row_sh = tk.Frame(card_right, bg="#ffffff")
        row_sh.pack(fill="x", pady=(0, 8))

        # Steps
        f_st = tk.Frame(row_sh, bg="#ffffff")
        f_st.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(f_st, text="Steps", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.steps_entry = ttk.Entry(f_st, font=("Segoe UI", 10))
        self.steps_entry.insert(0, "8500")
        self.steps_entry.pack(fill="x", pady=(2, 0))

        # Avg Heart Rate
        f_hr = tk.Frame(row_sh, bg="#ffffff")
        f_hr.pack(side="right", fill="x", expand=True, padx=(5, 0))
        tk.Label(f_hr, text="Avg heart rate", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.hr_entry = ttk.Entry(f_hr, font=("Segoe UI", 10))
        self.hr_entry.insert(0, "72")
        self.hr_entry.pack(fill="x", pady=(2, 0))

        # Sleep Hours
        tk.Label(card_right, text="Sleep hours", font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.sync_sleep_entry = ttk.Entry(card_right, font=("Segoe UI", 10))
        self.sync_sleep_entry.insert(0, "7.5")
        self.sync_sleep_entry.pack(fill="x", pady=(2, 12))

        btn_sync = tk.Button(card_right, text="Sync device", font=("Segoe UI", 9, "bold"), 
                             fg="#1a201c", bg="#ffffff", activebackground="#edf2f7", activeforeground="#1a201c", 
                             relief="solid", bd=1, pady=4, padx=12, cursor="hand2", command=self.sync_wearable)
        btn_sync.pack(anchor="w")

    def save_profile(self):
        try:
            name = self.name_entry.get().strip()
            age = int(self.age_entry.get())
            height = float(self.height_entry.get())
            gender = self.gender_combo.get().strip()

            self.db.update_user(name, age, height, gender)
            messagebox.showinfo("Success", "Profile changes saved successfully!")
            if self.refresh_callback:
                self.refresh_callback()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values for age and height.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {e}")

    def update_pass(self):
        npass = self.new_pass_entry.get().strip()
        if not npass:
            messagebox.showwarning("Warning", "Please enter a valid new password.")
            return
        self.db.update_password(npass)
        messagebox.showinfo("Success", "Password updated successfully!")
        self.curr_pass_entry.delete(0, tk.END)
        self.new_pass_entry.delete(0, tk.END)

    def sync_wearable(self):
        try:
            steps = int(self.steps_entry.get())
            hr = int(self.hr_entry.get())
            sleep_h = float(self.sync_sleep_entry.get())
            today_str = date.today().strftime("%Y-%m-%d")

            self.db.record_wearable_sync(steps, hr, sleep_h, today_str)
            messagebox.showinfo("Sync Successful", f"Wearable device synced!\nSteps: {steps} | HR: {hr} bpm | Sleep: {sleep_h} h")
            if self.refresh_callback:
                self.refresh_callback()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for steps, heart rate, and sleep hours.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to sync wearable device: {e}")

        # Section 3: Switch Sample Dataset
        dataset_card = tk.Frame(self, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=25, pady=18)
        dataset_card.pack(fill="x", padx=30, pady=(15, 20))

        tk.Label(dataset_card, text="LOAD PRESET SAMPLE DATASETS", font=("Segoe UI", 9, "bold"), fg="#136349", bg="#ffffff").pack(anchor="w", pady=(0, 5))
        tk.Label(dataset_card, text="Select a preset profile below to switch active user and inspect healthy or unhealthy health patterns:", 
                 font=("Segoe UI", 9), fg="#4a5568", bg="#ffffff").pack(anchor="w", pady=(0, 10))

        # Healthy Profiles Row
        tk.Label(dataset_card, text="HEALTHY PROFILES:", font=("Segoe UI", 8, "bold"), fg="#136349", bg="#ffffff").pack(anchor="w", pady=(4, 2))
        btn_box1 = tk.Frame(dataset_card, bg="#ffffff")
        btn_box1.pack(fill="x", pady=(0, 8))

        btn_ath = tk.Button(btn_box1, text="🏆 Rahul Sharma (Athlete / Optimal)", font=("Segoe UI", 8, "bold"),
                            fg="#ffffff", bg="#136349", activebackground="#0f4d39", activeforeground="#ffffff",
                            padx=8, pady=4, relief="flat", cursor="hand2", command=lambda: self.load_dataset("athlete"))
        btn_ath.pack(side="left", padx=(0, 6))

        btn_wl = tk.Button(btn_box1, text="📉 Anjali Patel (Weight Loss Journey)", font=("Segoe UI", 8, "bold"),
                           fg="#1a201c", bg="#edf2f7", activebackground="#cbd5e0", activeforeground="#1a201c",
                           padx=8, pady=4, relief="flat", cursor="hand2", command=lambda: self.load_dataset("weight_loss"))
        btn_wl.pack(side="left", padx=6)

        btn_ap = tk.Button(btn_box1, text="🧘‍♀️ Priya Nair (Active Professional)", font=("Segoe UI", 8, "bold"),
                           fg="#1a201c", bg="#edf2f7", activebackground="#cbd5e0", activeforeground="#1a201c",
                           padx=8, pady=4, relief="flat", cursor="hand2", command=lambda: self.load_dataset("active_prof"))
        btn_ap.pack(side="left", padx=6)

        # Unhealthy Profiles Row
        tk.Label(dataset_card, text="UNHEALTHY / HIGH-RISK PROFILES:", font=("Segoe UI", 8, "bold"), fg="#c53030", bg="#ffffff").pack(anchor="w", pady=(4, 2))
        btn_box2 = tk.Frame(dataset_card, bg="#ffffff")
        btn_box2.pack(fill="x")

        btn_sed = tk.Button(btn_box2, text="🚩 Vidithanjali (Sedentary / Desk)", font=("Segoe UI", 8, "bold"),
                            fg="#742a2a", bg="#fff5f5", activebackground="#fed7d7", activeforeground="#742a2a",
                            padx=8, pady=4, relief="solid", bd=1, cursor="hand2", command=lambda: self.load_dataset("sedentary"))
        btn_sed.pack(side="left", padx=(0, 6))

        btn_ot = tk.Button(btn_box2, text="⚠️ Karan Mehta (Overtrained / Sleep Deficit)", font=("Segoe UI", 8, "bold"),
                           fg="#742a2a", bg="#fff5f5", activebackground="#fed7d7", activeforeground="#742a2a",
                           padx=8, pady=4, relief="solid", bd=1, cursor="hand2", command=lambda: self.load_dataset("overtrained"))
        btn_ot.pack(side="left", padx=6)

        btn_dh = tk.Button(btn_box2, text="💧 Sneha Rao (Severe Dehydration)", font=("Segoe UI", 8, "bold"),
                           fg="#742a2a", bg="#fff5f5", activebackground="#fed7d7", activeforeground="#742a2a",
                           padx=8, pady=4, relief="solid", bd=1, cursor="hand2", command=lambda: self.load_dataset("dehydrated"))
        btn_dh.pack(side="left", padx=6)

        btn_cr = tk.Button(btn_box2, text="❤️ Vikram Verma (Cardio / Inactivity)", font=("Segoe UI", 8, "bold"),
                           fg="#742a2a", bg="#fff5f5", activebackground="#fed7d7", activeforeground="#742a2a",
                           padx=8, pady=4, relief="solid", bd=1, cursor="hand2", command=lambda: self.load_dataset("cardio_risk"))
        btn_cr.pack(side="left", padx=6)

    def load_dataset(self, key):
        from seed_data import seed_dataset
        seed_dataset(key, self.db.db_path)
        user = self.db.get_user()
        messagebox.showinfo("Dataset Loaded", f"Successfully loaded '{key.upper()}' dataset!\nActive Profile: {user.full_name}")
        if self.refresh_callback:
            self.refresh_callback()

        # Section 4: Create New User Profile
        newuser_card = tk.Frame(self, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1, padx=25, pady=18)
        newuser_card.pack(fill="x", padx=30, pady=(0, 25))

        tk.Label(newuser_card, text="REGISTER NEW USER PROFILE", font=("Segoe UI", 9, "bold"), fg="#136349", bg="#ffffff").pack(anchor="w", pady=(0, 5))
        
        nu_row = tk.Frame(newuser_card, bg="#ffffff")
        nu_row.pack(fill="x", pady=5)

        # Name
        f_nu_name = tk.Frame(nu_row, bg="#ffffff")
        f_nu_name.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(f_nu_name, text="Full Name", font=("Segoe UI", 8, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.nu_name_entry = ttk.Entry(f_nu_name, font=("Segoe UI", 9))
        self.nu_name_entry.pack(fill="x")

        # Age
        f_nu_age = tk.Frame(nu_row, bg="#ffffff")
        f_nu_age.pack(side="left", fill="x", expand=True, padx=5)
        tk.Label(f_nu_age, text="Age", font=("Segoe UI", 8, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.nu_age_entry = ttk.Entry(f_nu_age, font=("Segoe UI", 9))
        self.nu_age_entry.pack(fill="x")

        # Height
        f_nu_h = tk.Frame(nu_row, bg="#ffffff")
        f_nu_h.pack(side="left", fill="x", expand=True, padx=5)
        tk.Label(f_nu_h, text="Height (cm)", font=("Segoe UI", 8, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.nu_h_entry = ttk.Entry(f_nu_h, font=("Segoe UI", 9))
        self.nu_h_entry.pack(fill="x")

        # Gender
        f_nu_gen = tk.Frame(nu_row, bg="#ffffff")
        f_nu_gen.pack(side="left", fill="x", expand=True, padx=(5, 0))
        tk.Label(f_nu_gen, text="Gender", font=("Segoe UI", 8, "bold"), fg="#4a5568", bg="#ffffff").pack(anchor="w")
        self.nu_gen_combo = ttk.Combobox(f_nu_gen, values=["Female", "Male", "Non-binary", "Other"], font=("Segoe UI", 9))
        self.nu_gen_combo.set("Female")
        self.nu_gen_combo.pack(fill="x")

        btn_nu_create = tk.Button(newuser_card, text="➕ Create & Switch to New User", font=("Segoe UI", 9, "bold"),
                                  fg="#ffffff", bg="#136349", activebackground="#0f4d39", activeforeground="#ffffff",
                                  relief="flat", pady=6, cursor="hand2", command=self.create_new_user)
        btn_nu_create.pack(anchor="w", pady=(10, 0))

    def create_new_user(self):
        try:
            name = self.nu_name_entry.get().strip()
            if not name:
                messagebox.showwarning("Input Error", "Please enter a valid full name for the new user.")
                return
            age = int(self.nu_age_entry.get() or "25")
            height = float(self.nu_h_entry.get() or "165")
            gender = self.nu_gen_combo.get().strip()

            new_id = self.db.create_user(name, age, height, gender)
            messagebox.showinfo("User Created", f"New user profile '{name}' registered successfully!\nSwitched to User ID: {new_id}")
            if self.refresh_callback:
                self.refresh_callback()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values for age and height.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create user: {e}")


