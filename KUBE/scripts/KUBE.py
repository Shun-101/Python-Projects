import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime, timedelta
import hashlib
import csv
import threading
import time

class LoadingAnimation:
    """Loading animation overlay"""
    def __init__(self, parent):
        self.parent = parent
        self.overlay = None
        self.running = False
    
    def show(self, message="Loading..."):
        """Show loading animation"""
        self.overlay = tk.Toplevel(self.parent)
        self.overlay.title("Processing")
        self.overlay.geometry("300x150")
        self.overlay.configure(bg="white")
        self.overlay.transient(self.parent)
        self.overlay.grab_set()
        self.overlay.resizable(False, False)
        
        self.overlay.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 150
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 75
        self.overlay.geometry(f"+{x}+{y}")
        
        tk.Label(self.overlay, text=message, font=("Arial", 12), bg="white").pack(pady=30)
        self.dots_label = tk.Label(self.overlay, text="●", font=("Arial", 20), bg="white", fg="#3498db")
        self.dots_label.pack(pady=10)
        
        self.running = True
        self.animate_dots()
    
    def animate_dots(self):
        """Animate loading dots"""
        if self.running and self.overlay.winfo_exists():
            dots = ["●", "●●", "●●●"]
            for dot in dots:
                if self.running and self.overlay.winfo_exists():
                    self.dots_label.config(text=dot)
                    self.overlay.update()
                    time.sleep(0.3)
            self.animate_dots()
    
    def hide(self):
        """Hide loading animation"""
        self.running = False
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.destroy()

class KUBE:
    def __init__(self, root):
        self.root = root
        self.root.title("KUBE - Kitchen Utensil Borrowing Engine")
        self.root.geometry("1400x800")
        self.root.configure(bg="#f5f5f5")
        
        self.colors = {
            "header": "#2c3e50",
            "sidebar": "#34495e",
            "bg": "#f5f5f5",
            "white": "#ffffff",
            "primary": "#3498db",
            "success": "#27ae60",
            "warning": "#f39c12",
            "danger": "#e74c3c",
            "info": "#16a085",
            "secondary": "#8e44ad",
            "dark": "#2c3e50",
            "light": "#ecf0f1"
        }
        
        # File paths
        self.data_dir = "kube_data"
        self.utensils_file = os.path.join(self.data_dir, "utensils.json")
        self.borrowings_file = os.path.join(self.data_dir, "borrowings.json")
        self.admin_file = os.path.join(self.data_dir, "admin.json")
        self.trial_file = os.path.join(self.data_dir, "trial.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        self.borrowers_file = os.path.join(self.data_dir, "borrowers.json")
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        if not self.check_trial():
            self.show_trial_expired()
            return
        
        self.load_data()
        self.show_login_screen()
    
    def check_trial(self):
        """Check if trial period is still valid"""
        if not os.path.exists(self.trial_file):
            trial_data = {
                "start_date": datetime.now().isoformat(),
                "trial_days": 30
            }
            with open(self.trial_file, 'w') as f:
                json.dump(trial_data, f)
            return True
        
        with open(self.trial_file, 'r') as f:
            trial_data = json.load(f)
        
        start_date = datetime.fromisoformat(trial_data["start_date"])
        trial_days = trial_data["trial_days"]
        expiry_date = start_date + timedelta(days=trial_days)
        
        return datetime.now() <= expiry_date
    
    def show_trial_expired(self):
        """Show trial expired message"""
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        tk.Label(frame, text="⏰ Trial Period Expired", font=("Arial", 24, "bold"), bg="#f0f0f0", fg="#e74c3c").pack(pady=30)
        tk.Label(frame, text="Your 30-day free trial has ended.\nPlease contact support to continue.", font=("Arial", 14), bg="#f0f0f0", fg="#555", justify="center").pack(pady=20)
        tk.Button(frame, text="Exit", command=self.root.destroy, font=("Arial", 12), bg="#e74c3c", fg="white", padx=30, pady=10, cursor="hand2").pack(pady=20)
    
    def load_data(self):
        """Load all data from JSON files"""
        if os.path.exists(self.utensils_file):
            with open(self.utensils_file, 'r') as f:
                self.utensils = json.load(f)
        else:
            self.utensils = [
                {"id": 1, "name": "Chef Knife", "quantity": 5, "available": 5, "category": "Cutlery"},
                {"id": 2, "name": "Cutting Board", "quantity": 8, "available": 8, "category": "Preparation"},
                {"id": 3, "name": "Mixing Bowl", "quantity": 10, "available": 10, "category": "Cookware"},
                {"id": 4, "name": "Whisk", "quantity": 6, "available": 6, "category": "Utensils"},
                {"id": 5, "name": "Spatula", "quantity": 7, "available": 7, "category": "Utensils"},
            ]
            self.save_utensils()
        
        self.borrowings = self._load_json(self.borrowings_file, [])
        if not os.path.exists(self.borrowings_file):
            self.save_borrowings()
        
        if os.path.exists(self.admin_file):
            with open(self.admin_file, 'r') as f:
                self.admin_data = json.load(f)
        else:
            self.admin_data = {
                "username": "admin",
                "password": self.hash_password("admin123")
            }
            self.save_admin()
        
        self.settings = self._load_json(self.settings_file, {"max_borrow_limit": 5})
        if not os.path.exists(self.settings_file):
            self.save_settings()
        
        self.borrowers = self._load_json(self.borrowers_file, {})
        if not os.path.exists(self.borrowers_file):
            self.save_borrowers()
    
    def _load_json(self, filepath, default):
        """Helper to load JSON with default fallback"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return default
    
    def _save_json(self, filepath, data):
        """Helper to save JSON"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def save_utensils(self):
        self._save_json(self.utensils_file, self.utensils)
    
    def save_borrowings(self):
        self._save_json(self.borrowings_file, self.borrowings)
    
    def save_admin(self):
        self._save_json(self.admin_file, self.admin_data)
    
    def save_settings(self):
        self._save_json(self.settings_file, self.settings)
    
    def save_borrowers(self):
        self._save_json(self.borrowers_file, self.borrowers)
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def is_overdue(self, borrowing):
        """Check if a borrowing is overdue"""
        if borrowing.get("returned", False):
            return False
        
        due_date_str = borrowing.get("due_date")
        if not due_date_str:
            return False
        
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        return datetime.now() > due_date
    
    def days_overdue(self, borrowing):
        """Calculate how many days overdue a borrowing is"""
        if not self.is_overdue(borrowing):
            return 0
        
        due_date = datetime.strptime(borrowing["due_date"], "%Y-%m-%d")
        return (datetime.now() - due_date).days
    
    def calculate_credit_score(self, borrower_name):
        """Calculate credit score for a borrower (0-100, starting at 100)"""
        borrower_key = borrower_name.lower().strip()
        
        if borrower_key not in self.borrowers:
            return 100
        
        borrower_data = self.borrowers[borrower_key]
        return borrower_data.get("credit_score", 100)
    
    def update_credit_score(self, borrower_name, borrowing):
        """Update credit score based on borrowing behavior with detailed point system"""
        borrower_key = borrower_name.lower().strip()
        
        if borrower_key not in self.borrowers:
            self.borrowers[borrower_key] = {
                "name": borrower_name,
                "credit_score": 100,
                "total_borrowings": 0,
                "on_time_returns": 0,
                "late_returns": 0,
                "damaged_items": 0,
                "contact_info": borrowing.get("contact_info", {})
            }
        
        borrower_data = self.borrowers[borrower_key]
        borrower_data["total_borrowings"] += 1
        
        if borrowing.get("returned"):
            if self.is_overdue(borrowing):
                borrower_data["late_returns"] += 1
                days_late = self.days_overdue(borrowing)
                
                # Scale penalty: -10 for 1 day, up to -25 for 7+ days
                if days_late == 1:
                    penalty = -10
                elif days_late <= 3:
                    penalty = -15
                elif days_late <= 7:
                    penalty = -20
                else:
                    penalty = -25
                
                borrower_data["credit_score"] = max(0, borrower_data["credit_score"] + penalty)
            else:
                borrower_data["on_time_returns"] += 1
                # +5 points for on-time return
                borrower_data["credit_score"] = min(100, borrower_data["credit_score"] + 5)
            
            # Check for damaged/lost items
            condition = borrowing.get("return_condition", "Good")
            if condition in ["Damaged", "Lost"]:
                borrower_data["damaged_items"] += 1
                # -50 points for damaged/lost items
                borrower_data["credit_score"] = max(0, borrower_data["credit_score"] - 50)
            elif condition == "Excellent":
                # +2 bonus for excellent condition
                borrower_data["credit_score"] = min(100, borrower_data["credit_score"] + 2)
            
            # Check for perfect history milestone bonus (+25 points at 10 loans)
            if borrower_data["total_borrowings"] == 10 and borrower_data["late_returns"] == 0 and borrower_data["damaged_items"] == 0:
                borrower_data["credit_score"] = min(100, borrower_data["credit_score"] + 25)
        
        self.save_borrowers()
    
    def get_credit_score_color(self, score):
        """Get color based on credit score"""
        if score >= 70:
            return self.colors["success"]
        elif score >= 40:
            return self.colors["warning"]
        else:
            return self.colors["danger"]
    
    def get_credit_score_label(self, score):
        """Get label based on credit score"""
        if score >= 70:
            return "Excellent"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"
    
    def get_active_borrowings_count(self, borrower_name):
        """Count active borrowings for a borrower"""
        borrower_key = borrower_name.lower().strip()
        count = 0
        for b in self.borrowings:
            if b["borrower_name"].lower().strip() == borrower_key and not b.get("returned", False):
                count += b["quantity"]
        return count
    
    def create_dialog(self, title, width=450, height=350):
        """Helper to create a standard dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        dialog.configure(bg=self.colors["white"])
        dialog.transient(self.root)
        dialog.grab_set()
        return dialog
    
    def create_button(self, parent, text, command, bg_color, side="left", padx=10):
        """Helper to create a standard button"""
        btn = tk.Button(parent, text=text, command=command, font=("Arial", 11, "bold"), 
                       bg=bg_color, fg=self.colors["white"], padx=20, pady=10, 
                       cursor="hand2", relief="flat", bd=0)
        btn.pack(side=side, padx=padx)
        return btn
    
    def show_login_screen(self):
        """Display admin login screen"""
        self.clear_window()
        
        container = tk.Frame(self.root, bg=self.colors["bg"])
        container.pack(expand=True, fill="both")
        
        center_frame = tk.Frame(container, bg=self.colors["bg"])
        center_frame.pack(expand=True)
        
        tk.Label(center_frame, text="🍴", font=("Arial", 60), bg=self.colors["bg"]).pack(pady=(0, 20))
        tk.Label(center_frame, text="KUBE", font=("Arial", 36, "bold"), bg=self.colors["bg"], fg=self.colors["dark"]).pack()
        tk.Label(center_frame, text="Kitchen Utensil Borrowing Engine", font=("Arial", 14), bg=self.colors["bg"], fg="#7f8c8d").pack(pady=(0, 40))
        
        form_frame = tk.Frame(center_frame, bg=self.colors["white"], relief="raised", bd=0)
        form_frame.pack(padx=40, pady=20)
        
        tk.Label(form_frame, text="Admin Login", font=("Arial", 18, "bold"), bg=self.colors["white"], fg=self.colors["dark"]).grid(row=0, column=0, columnspan=2, pady=30)
        
        tk.Label(form_frame, text="Username:", font=("Arial", 11), bg=self.colors["white"]).grid(row=1, column=0, padx=20, pady=15, sticky="e")
        self.username_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        self.username_entry.grid(row=1, column=1, padx=20, pady=15)
        
        tk.Label(form_frame, text="Password:", font=("Arial", 11), bg=self.colors["white"]).grid(row=2, column=0, padx=20, pady=15, sticky="e")
        self.password_entry = tk.Entry(form_frame, font=("Arial", 11), width=25, show="*")
        self.password_entry.grid(row=2, column=1, padx=20, pady=15)
        self.password_entry.bind('<Return>', lambda e: self.admin_login())
        
        tk.Button(form_frame, text="Login", command=self.admin_login, font=("Arial", 12, "bold"), 
                 bg=self.colors["danger"], fg=self.colors["white"], padx=40, pady=12, 
                 cursor="hand2", relief="flat", bd=0).grid(row=3, column=0, columnspan=2, pady=30)
        
        with open(self.trial_file, 'r') as f:
            trial_data = json.load(f)
        start_date = datetime.fromisoformat(trial_data["start_date"])
        days_left = 30 - (datetime.now() - start_date).days
        
        tk.Label(center_frame, text=f"⏰ Trial: {max(0, days_left)} days remaining", 
                font=("Arial", 10), bg=self.colors["bg"], fg=self.colors["warning"]).pack(pady=20)
    
    def admin_login(self):
        """Handle admin login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if username == self.admin_data["username"] and self.hash_password(password) == self.admin_data["password"]:
            self.show_main_dashboard()
        else:
            messagebox.showerror("Error", "Invalid admin credentials")
    
    def show_main_dashboard(self):
        """Modern sidebar layout with main dashboard"""
        self.clear_window()
        
        main_container = tk.Frame(self.root, bg=self.colors["bg"])
        main_container.pack(expand=True, fill="both")
        
        header = tk.Frame(main_container, bg=self.colors["header"], height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="🍴 KUBE - Kitchen Utensil Borrowing Engine", font=("Arial", 16, "bold"), 
                bg=self.colors["header"], fg=self.colors["white"]).pack(side="left", padx=20, pady=15)
        
        tk.Button(header, text="🔑 Change Password", command=self.show_change_password, font=("Arial", 10), 
                 bg=self.colors["secondary"], fg=self.colors["white"], padx=15, pady=8, 
                 cursor="hand2", relief="flat", bd=0).pack(side="right", padx=10, pady=15)
        
        tk.Button(header, text="Logout 🔒", command=self.show_login_screen, font=("Arial", 10, "bold"), 
                 bg=self.colors["danger"], fg=self.colors["white"], padx=15, pady=8, 
                 cursor="hand2", relief="flat", bd=0).pack(side="right", padx=10, pady=15)
        
        content_area = tk.Frame(main_container, bg=self.colors["bg"])
        content_area.pack(expand=True, fill="both")
        
        sidebar = tk.Frame(content_area, bg=self.colors["sidebar"], width=280)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        self.main_content = tk.Frame(content_area, bg=self.colors["bg"])
        self.main_content.pack(side="right", expand=True, fill="both")
        
        sidebar_buttons = [
            ("📊 Dashboard", lambda: self.show_dashboard_content(), self.colors["primary"]),
            ("📋 Utensil Inventory", lambda: self.show_inventory_content(), self.colors["info"]),
            ("📤 Borrow Utensils", lambda: self.show_borrow_content(), self.colors["success"]),
            ("📥 Return Utensils", lambda: self.show_return_content(), self.colors["warning"]),
            ("👥 Borrowers", lambda: self.show_borrowers_content(), self.colors["secondary"]),
            ("📜 Transaction Log", lambda: self.show_transaction_log_content(), self.colors["secondary"]),
            ("🔍 Search Borrowings", lambda: self.show_search_content(), self.colors["secondary"]),
            ("⚙️ Manage Equipment", lambda: self.show_equipment_content(), self.colors["dark"]),
            ("⚙️ System Settings", lambda: self.show_settings_content(), self.colors["dark"]),
        ]
        
        for text, command, color in sidebar_buttons:
            btn = tk.Button(sidebar, text=text, command=command, font=("Arial", 11), bg=color, 
                           fg=self.colors["white"], padx=20, pady=15, cursor="hand2", 
                           relief="flat", bd=0, anchor="w", justify="left")
            btn.pack(fill="x", padx=10, pady=5)
        
        self.show_dashboard_content()
    
    def show_dashboard_content(self):
        """Dashboard content in main area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        title_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        title_frame.pack(fill="x", padx=30, pady=20)
        
        tk.Label(title_frame, text="Dashboard Overview", font=("Arial", 24, "bold"), 
                bg=self.colors["bg"], fg=self.colors["dark"]).pack(anchor="w")
        
        stats_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        stats_frame.pack(fill="x", padx=30, pady=10)
        
        total_utensils = sum(u["quantity"] for u in self.utensils)
        available_utensils = sum(u["available"] for u in self.utensils)
        borrowed_utensils = total_utensils - available_utensils
        
        active_borrowings = [b for b in self.borrowings if not b.get("returned", False)]
        overdue_borrowings = [b for b in active_borrowings if self.is_overdue(b)]
        
        stats = [
            ("Utensils Out", borrowed_utensils, self.colors["warning"]),
            ("Overdue Items", len(overdue_borrowings), self.colors["danger"]),
        ]
        
        for label, value, color in stats:
            card = tk.Frame(stats_frame, bg=self.colors["white"], relief="raised", bd=0)
            card.pack(side="left", expand=True, fill="both", padx=10, pady=10)
            
            tk.Label(card, text=str(value), font=("Arial", 48, "bold"), bg=self.colors["white"], fg=color).pack(pady=(20, 5))
            tk.Label(card, text=label, font=("Arial", 12), bg=self.colors["white"], fg="#7f8c8d").pack(pady=(0, 20))
        
        activity_frame = tk.LabelFrame(self.main_content, text="Recent Activity", font=("Arial", 13, "bold"), 
                                      bg=self.colors["white"], fg=self.colors["dark"], relief="flat", bd=0)
        activity_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        tree_frame = tk.Frame(activity_frame, bg=self.colors["white"])
        tree_frame.pack(expand=True, fill="both", padx=15, pady=15)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        columns = ("Borrower", "Utensil", "Action", "Date")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set, height=8)
        scrollbar.config(command=tree.yview)
        
        for col in columns:
            tree.heading(col, text=col)
        
        tree.column("Borrower", width=200)
        tree.column("Utensil", width=200)
        tree.column("Action", width=150)
        tree.column("Date", width=200)
        
        for borrowing in sorted(self.borrowings, key=lambda x: x.get("borrow_date", ""), reverse=True)[:10]:
            action = "Returned" if borrowing.get("returned") else "Borrowed"
            date = borrowing.get("return_date") if borrowing.get("returned") else borrowing.get("borrow_date")
            tree.insert("", "end", values=(borrowing["borrower_name"], borrowing["utensil_name"], action, date))
        
        tree.pack(expand=True, fill="both")
    
    def show_inventory_content(self):
        """Inventory content"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        title_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        title_frame.pack(fill="x", padx=30, pady=20)
        
        tk.Label(title_frame, text="Utensil Inventory", font=("Arial", 24, "bold"), 
                bg=self.colors["bg"], fg=self.colors["dark"]).pack(anchor="w")
        
        tree_frame = tk.Frame(self.main_content, bg=self.colors["white"])
        tree_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        columns = ("ID", "Name", "Category", "Total", "Available", "Borrowed")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        for col in columns:
            tree.heading(col, text=col)
        
        tree.column("ID", width=50)
        tree.column("Name", width=200)
        tree.column("Category", width=150)
        tree.column("Total", width=100)
        tree.column("Available", width=100)
        tree.column("Borrowed", width=100)
        
        for utensil in self.utensils:
            borrowed = utensil["quantity"] - utensil["available"]
            tree.insert("", "end", values=(utensil["id"], utensil["name"], utensil.get("category", "Uncategorized"), 
                                          utensil["quantity"], utensil["available"], borrowed))
        
        tree.pack(expand=True, fill="both")
    
    def show_borrow_content(self):
        """Borrow utensils content"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        title_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        title_frame.pack(fill="x", padx=30, pady=20)
        
        tk.Label(title_frame, text="Borrow Kitchen Utensils", font=("Arial", 24, "bold"), 
                bg=self.colors["bg"], fg=self.colors["dark"]).pack(anchor="w")
        
        form_frame = tk.Frame(self.main_content, bg=self.colors["white"])
        form_frame.pack(fill="x", padx=30, pady=10)
        
        tk.Label(form_frame, text="Borrower Name:", font=("Arial", 11, "bold"), bg=self.colors["white"]).grid(row=0, column=0, padx=15, pady=15, sticky="e")
        borrower_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        borrower_entry.grid(row=0, column=1, padx=15, pady=15)
        
        tk.Label(form_frame, text="Phone:", font=("Arial", 11, "bold"), bg=self.colors["white"]).grid(row=0, column=2, padx=15, pady=15, sticky="e")
        phone_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        phone_entry.grid(row=0, column=3, padx=15, pady=15)
        
        tk.Label(form_frame, text="Email:", font=("Arial", 11, "bold"), bg=self.colors["white"]).grid(row=1, column=0, padx=15, pady=15, sticky="e")
        email_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        email_entry.grid(row=1, column=1, padx=15, pady=15)
        
        tk.Label(form_frame, text="Due in (days):", font=("Arial", 11, "bold"), bg=self.colors["white"]).grid(row=1, column=2, padx=15, pady=15, sticky="e")
        due_days_var = tk.IntVar(value=7)
        tk.Spinbox(form_frame, from_=1, to=90, textvariable=due_days_var, font=("Arial", 11), width=23).grid(row=1, column=3, padx=15, pady=15)
        
        items_frame = tk.LabelFrame(self.main_content, text="Select Items to Borrow (Ctrl+Click for multiple) - Adjust quantities as needed", 
                                   font=("Arial", 12, "bold"), bg=self.colors["white"], relief="flat", bd=0)
        items_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        tree_frame = tk.Frame(items_frame, bg=self.colors["white"])
        tree_frame.pack(expand=True, fill="both", padx=15, pady=15)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        canvas = tk.Canvas(tree_frame, bg=self.colors["white"], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=canvas.yview)
        canvas.config(yscrollcommand=scrollbar.set)
        
        scrollable_frame = tk.Frame(canvas, bg=self.colors["white"])
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        qty_vars = {}
        selected_items = {}
        
        for utensil in self.utensils:
            if utensil["available"] > 0:
                item_frame = tk.Frame(scrollable_frame, bg=self.colors["light"], relief="raised", bd=1)
                item_frame.pack(fill="x", padx=5, pady=5)
                
                var = tk.BooleanVar()
                selected_items[utensil["id"]] = var
                
                tk.Checkbutton(item_frame, variable=var, bg=self.colors["light"], activebackground=self.colors["light"]).pack(side="left", padx=10, pady=10)
                tk.Label(item_frame, text=utensil["name"], font=("Arial", 11, "bold"), bg=self.colors["light"], width=25, anchor="w").pack(side="left", padx=10, pady=10)
                tk.Label(item_frame, text=f"Available: {utensil['available']}", font=("Arial", 10), bg=self.colors["light"], width=20, anchor="w").pack(side="left", padx=10, pady=10)
                
                tk.Label(item_frame, text="Qty:", font=("Arial", 10), bg=self.colors["light"]).pack(side="left", padx=5, pady=10)
                qty_var = tk.IntVar(value=1)
                qty_vars[utensil["id"]] = qty_var
                tk.Spinbox(item_frame, from_=1, to=utensil["available"], textvariable=qty_var, font=("Arial", 10), width=5).pack(side="left", padx=5, pady=10)
        
        scrollable_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        button_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        button_frame.pack(pady=20)
        
        def process_borrow():
            borrower_name = borrower_entry.get().strip()
            if not borrower_name:
                messagebox.showerror("Error", "Please enter borrower name")
                return
            
            selected_utensils = [uid for uid, var in selected_items.items() if var.get()]
            if not selected_utensils:
                messagebox.showerror("Error", "Please select at least one item")
                return
            
            active_count = self.get_active_borrowings_count(borrower_name)
            total_qty = sum(qty_vars[uid].get() for uid in selected_utensils)
            
            if active_count + total_qty > self.settings["max_borrow_limit"]:
                messagebox.showerror("Error", f"Borrow limit exceeded. Current: {active_count}, Limit: {self.settings['max_borrow_limit']}")
                return
            
            due_date = (datetime.now() + timedelta(days=due_days_var.get())).strftime("%Y-%m-%d")
            
            for uid in selected_utensils:
                utensil = next(u for u in self.utensils if u["id"] == uid)
                qty = qty_vars[uid].get()
                
                if qty > utensil["available"]:
                    messagebox.showerror("Error", f"Not enough {utensil['name']} available")
                    return
                
                borrowing = {
                    "id": len(self.borrowings) + 1,
                    "borrower_name": borrower_name,
                    "utensil_name": utensil["name"],
                    "utensil_id": utensil["id"],
                    "quantity": qty,
                    "borrow_date": datetime.now().strftime("%Y-%m-%d"),
                    "due_date": due_date,
                    "returned": False,
                    "contact_info": {"phone": phone_entry.get(), "email": email_entry.get()}
                }
                
                self.borrowings.append(borrowing)
                utensil["available"] -= qty
                self.update_credit_score(borrower_name, borrowing)
            
            self.save_borrowings()
            self.save_utensils()
            messagebox.showinfo("Success", f"Borrowed {len(selected_utensils)} item(s) successfully!")
            self.show_borrow_content()
        
        self.create_button(button_frame, "🛒 Process Borrowing", process_borrow, self.colors["success"])
    
    def show_return_content(self):
        """Return utensils content"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        title_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        title_frame.pack(fill="x", padx=30, pady=20)
        
        tk.Label(title_frame, text="Return Kitchen Utensils", font=("Arial", 24, "bold"), 
                bg=self.colors["bg"], fg=self.colors["dark"]).pack(anchor="w")
        
        items_frame = tk.LabelFrame(self.main_content, text="Active Borrowings (Ctrl+Click for multiple) - Adjust return quantities", 
                                   font=("Arial", 12, "bold"), bg=self.colors["white"], relief="flat", bd=0)
        items_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        tree_frame = tk.Frame(items_frame, bg=self.colors["white"])
        tree_frame.pack(expand=True, fill="both", padx=15, pady=15)
        
        canvas = tk.Canvas(tree_frame, bg=self.colors["white"], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.config(yscrollcommand=scrollbar.set)
        
        scrollable_frame = tk.Frame(canvas, bg=self.colors["white"])
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        borrowing_data = {}
        selected_items = {}
        return_qty_vars = {}
        condition_vars = {}
        notes_vars = {}
        
        active_borrowings = [b for b in self.borrowings if not b.get("returned", False)]
        
        for borrowing in active_borrowings:
            status = "OVERDUE" if self.is_overdue(borrowing) else "Active"
            bg_color = "#ffcccc" if status == "OVERDUE" else "#fff3cd"
            
            item_frame = tk.Frame(scrollable_frame, bg=bg_color, relief="raised", bd=1)
            item_frame.pack(fill="x", padx=5, pady=5)
            
            var = tk.BooleanVar()
            selected_items[borrowing["id"]] = var
            
            tk.Checkbutton(item_frame, variable=var, bg=bg_color, activebackground=bg_color).pack(side="left", padx=10, pady=10)
            
            info_text = f"{borrowing['borrower_name']} - {borrowing['utensil_name']}"
            tk.Label(item_frame, text=info_text, font=("Arial", 11, "bold"), bg=bg_color, width=35, anchor="w").pack(side="left", padx=10, pady=10)
            tk.Label(item_frame, text=f"Borrowed: {borrowing['quantity']}", font=("Arial", 10), bg=bg_color, width=15, anchor="w").pack(side="left", padx=5, pady=10)
            
            tk.Label(item_frame, text="Return:", font=("Arial", 10), bg=bg_color).pack(side="left", padx=5, pady=10)
            qty_var = tk.IntVar(value=borrowing["quantity"])
            return_qty_vars[borrowing["id"]] = qty_var
            tk.Spinbox(item_frame, from_=1, to=borrowing["quantity"], textvariable=qty_var, font=("Arial", 10), width=5).pack(side="left", padx=5, pady=10)
            
            tk.Label(item_frame, text="Condition:", font=("Arial", 10), bg=bg_color).pack(side="left", padx=5, pady=10)
            cond_var = tk.StringVar(value="Good")
            condition_vars[borrowing["id"]] = cond_var
            ttk.Combobox(item_frame, textvariable=cond_var, values=["Excellent", "Good", "Fair", "Damaged", "Lost"], 
                        font=("Arial", 10), width=12, state="readonly").pack(side="left", padx=5, pady=10)
            
            tk.Label(item_frame, text="Notes:", font=("Arial", 10), bg=bg_color).pack(side="left", padx=5, pady=10)
            notes_var = tk.StringVar()
            notes_vars[borrowing["id"]] = notes_var
            tk.Entry(item_frame, textvariable=notes_var, font=("Arial", 10), width=20).pack(side="left", padx=5, pady=10)
            
            borrowing_data[borrowing["id"]] = borrowing
        
        scrollable_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        button_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        button_frame.pack(pady=20)
        
        def process_return():
            selected_borrowing_ids = [bid for bid, var in selected_items.items() if var.get()]
            if not selected_borrowing_ids:
                messagebox.showerror("Error", "Please select at least one item to return")
                return
            
            for bid in selected_borrowing_ids:
                borrowing = borrowing_data[bid]
                return_qty = return_qty_vars[bid].get()
                borrowed_qty = borrowing["quantity"]
                
                if return_qty < borrowed_qty:
                    remaining_qty = borrowed_qty - return_qty
                    new_borrowing = {
                        "id": len(self.borrowings) + 1,
                        "borrower_name": borrowing["borrower_name"],
                        "utensil_name": borrowing["utensil_name"],
                        "utensil_id": borrowing["utensil_id"],
                        "quantity": remaining_qty,
                        "borrow_date": borrowing["borrow_date"],
                        "due_date": borrowing["due_date"],
                        "returned": False,
                        "contact_info": borrowing.get("contact_info", {})
                    }
                    self.borrowings.append(new_borrowing)
                
                borrowing["returned"] = True
                borrowing["return_date"] = datetime.now().strftime("%Y-%m-%d")
                borrowing["return_condition"] = condition_vars[bid].get()
                borrowing["return_notes"] = notes_vars[bid].get()
                borrowing["return_quantity"] = return_qty
                borrowing["quantity"] = return_qty
                
                for utensil in self.utensils:
                    if utensil["id"] == borrowing["utensil_id"]:
                        utensil["available"] += return_qty
                        break
                
                self.update_credit_score(borrowing["borrower_name"], borrowing)
            
            self.save_borrowings()
            self.save_utensils()
            messagebox.showinfo("Success", f"Returned {len(selected_borrowing_ids)} item(s) successfully!")
            self.show_return_content()
        
        self.create_button(button_frame, "✓ Return Selected Items", process_return, self.colors["warning"])
    
    def show_borrowers_content(self):
        """Borrowers content"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        title_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        title_frame.pack(fill="x", padx=30, pady=20)
        
        tk.Label(title_frame, text="Borrower History", font=("Arial", 24, "bold"), 
                bg=self.colors["bg"], fg=self.colors["dark"]).pack(anchor="w")
        
        tree_frame = tk.Frame(self.main_content, bg=self.colors["white"])
        tree_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        columns = ("Borrower", "Credit Score", "Active Loans", "Total Borrowings", "Late Returns")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        for col in columns:
            tree.heading(col, text=col)
        
        tree.column("Borrower", width=200)
        tree.column("Credit Score", width=150)
        tree.column("Active Loans", width=150)
        tree.column("Total Borrowings", width=150)
        tree.column("Late Returns", width=150)
        
        borrower_names = list(set(b["borrower_name"] for b in self.borrowings))
        for name in sorted(borrower_names):
            score = self.calculate_credit_score(name)
            active = self.get_active_borrowings_count(name)
            borrower_key = name.lower().strip()
            borrower_data = self.borrowers.get(borrower_key, {})
            
            tree.insert("", "end", values=(name, f"{score}/100", active, borrower_data.get("total_borrowings", 0), borrower_data.get("late_returns", 0)))
        
        button_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        button_frame.pack(pady=20)
        
        def view_details():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Error", "Please select a borrower")
                return
            
            item = tree.item(selected[0])
            borrower_name = item["values"][0]
            self.show_borrower_detail(borrower_name)
        
        self.create_button(button_frame, "👁️ View Details", view_details, self.colors["info"])
        
        tree.pack(expand=True, fill="both")
    
    def show_transaction_log_content(self):
        """Transaction log content"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        title_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        title_frame.pack(fill="x", padx=30, pady=20)
        
        tk.Label(title_frame, text="Transaction Log", font=("Arial", 24, "bold"), 
                bg=self.colors["bg"], fg=self.colors["dark"]).pack(anchor="w")
        
        tree_frame = tk.Frame(self.main_content, bg=self.colors["white"])
        tree_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        columns = ("ID", "Borrower", "Utensil", "Qty", "Borrow Date", "Due Date", "Return Date", "Status")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        for col in columns:
            tree.heading(col, text=col)
        
        tree.column("ID", width=50)
        tree.column("Borrower", width=130)
        tree.column("Utensil", width=130)
        tree.column("Qty", width=50)
        tree.column("Borrow Date", width=130)
        tree.column("Due Date", width=100)
        tree.column("Return Date", width=130)
        tree.column("Status", width=100)
        
        for borrowing in sorted(self.borrowings, key=lambda x: x.get("borrow_date", ""), reverse=True):
            status = "Returned" if borrowing.get("returned") else ("Overdue" if self.is_overdue(borrowing) else "Active")
            tree.insert("", "end", values=(borrowing["id"], borrowing["borrower_name"], borrowing["utensil_name"], 
                                          borrowing["quantity"], borrowing["borrow_date"], borrowing.get("due_date", "N/A"), 
                                          borrowing.get("return_date", "N/A"), status), tags=(status,))
        
        tree.tag_configure("Overdue", background="#ffcccc")
        tree.tag_configure("Active", background="#fff3cd")
        tree.tag_configure("Returned", background="#d4edda")
        
        tree.pack(expand=True, fill="both")
        
        button_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        button_frame.pack(pady=20)
        
        def export_to_csv():
            """Export transaction log to CSV file"""
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"transaction_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not file_path:
                return
            
            try:
                with open(file_path, 'w', newline='') as csvfile:
                    fieldnames = ["ID", "Borrower", "Utensil", "Quantity", "Borrow Date", "Due Date", "Return Date", "Status", "Condition", "Notes"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for borrowing in sorted(self.borrowings, key=lambda x: x.get("borrow_date", ""), reverse=True):
                        status = "Returned" if borrowing.get("returned") else ("Overdue" if self.is_overdue(borrowing) else "Active")
                        writer.writerow({
                            "ID": borrowing["id"],
                            "Borrower": borrowing["borrower_name"],
                            "Utensil": borrowing["utensil_name"],
                            "Quantity": borrowing["quantity"],
                            "Borrow Date": borrowing["borrow_date"],
                            "Due Date": borrowing.get("due_date", "N/A"),
                            "Return Date": borrowing.get("return_date", "N/A"),
                            "Status": status,
                            "Condition": borrowing.get("return_condition", "N/A"),
                            "Notes": borrowing.get("return_notes", "")
                        })
                
                messagebox.showinfo("Success", f"Transaction log exported successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
        
        self.create_button(button_frame, "📥 Export to CSV", export_to_csv, self.colors["info"])
    
    def show_search_content(self):
        """Search content"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        title_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        title_frame.pack(fill="x", padx=30, pady=20)
        
        tk.Label(title_frame, text="Search Borrowings", font=("Arial", 24, "bold"), 
                bg=self.colors["bg"], fg=self.colors["dark"]).pack(anchor="w")
        
        search_frame = tk.Frame(self.main_content, bg=self.colors["white"])
        search_frame.pack(fill="x", padx=30, pady=10)
        
        tk.Label(search_frame, text="Search:", font=("Arial", 11, "bold"), bg=self.colors["white"]).pack(side="left", padx=15, pady=15)
        search_entry = tk.Entry(search_frame, font=("Arial", 11), width=30)
        search_entry.pack(side="left", padx=10, pady=15)
        
        tk.Label(search_frame, text="Status:", font=("Arial", 11, "bold"), bg=self.colors["white"]).pack(side="left", padx=15, pady=15)
        status_var = tk.StringVar(value="All")
        status_dropdown = ttk.Combobox(search_frame, textvariable=status_var, values=["All", "Active", "Returned", "Overdue"], 
                                      font=("Arial", 11), width=15, state="readonly")
        status_dropdown.pack(side="left", padx=10, pady=15)
        
        tree_frame = tk.Frame(self.main_content, bg=self.colors["white"])
        tree_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        columns = ("ID", "Borrower", "Utensil", "Qty", "Borrow Date", "Due Date", "Status")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        for col in columns:
            tree.heading(col, text=col)
        
        tree.column("ID", width=50)
        tree.column("Borrower", width=150)
        tree.column("Utensil", width=150)
        tree.column("Qty", width=50)
        tree.column("Borrow Date", width=130)
        tree.column("Due Date", width=100)
        tree.column("Status", width=100)
        
        def update_results():
            for item in tree.get_children():
                tree.delete(item)
            
            search_term = search_entry.get().lower().strip()
            status_filter = status_var.get()
            
            for borrowing in self.borrowings:
                status = "Returned" if borrowing.get("returned") else ("Overdue" if self.is_overdue(borrowing) else "Active")
                
                if status_filter != "All" and status != status_filter:
                    continue
                
                if search_term and search_term not in borrowing["borrower_name"].lower() and search_term not in borrowing["utensil_name"].lower():
                    continue
                
                tree.insert("", "end", values=(borrowing["id"], borrowing["borrower_name"], borrowing["utensil_name"], 
                                              borrowing["quantity"], borrowing["borrow_date"], borrowing.get("due_date", "N/A"), status), tags=(status,))
        
        tree.tag_configure("Overdue", background="#ffcccc")
        tree.tag_configure("Active", background="#fff3cd")
        tree.tag_configure("Returned", background="#d4edda")
        
        tree.pack(expand=True, fill="both")
        
        search_entry.bind('<KeyRelease>', lambda e: update_results())
        status_dropdown.bind('<<ComboboxSelected>>', lambda e: update_results())
        
        update_results()
    
    def show_equipment_content(self):
        """Equipment management content"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        title_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        title_frame.pack(fill="x", padx=30, pady=20)
        
        tk.Label(title_frame, text="Manage Equipment", font=("Arial", 24, "bold"), 
                bg=self.colors["bg"], fg=self.colors["dark"]).pack(anchor="w")
        
        button_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        button_frame.pack(pady=20)
        
        self.create_button(button_frame, "➕ Add New Utensil", self.show_add_utensil_dialog, self.colors["success"])
        self.create_button(button_frame, "✏️ Edit Utensil", self.show_edit_utensil_dialog, self.colors["warning"])
        self.create_button(button_frame, "🗑️ Delete Utensil", self.show_delete_utensil_dialog, self.colors["danger"])
        
        tree_frame = tk.Frame(self.main_content, bg=self.colors["white"])
        tree_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        columns = ("ID", "Name", "Category", "Total", "Available", "Borrowed")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        for col in columns:
            tree.heading(col, text=col)
        
        tree.column("ID", width=50)
        tree.column("Name", width=200)
        tree.column("Category", width=150)
        tree.column("Total", width=100)
        tree.column("Available", width=100)
        tree.column("Borrowed", width=100)
        
        for utensil in self.utensils:
            borrowed = utensil["quantity"] - utensil["available"]
            tree.insert("", "end", values=(utensil["id"], utensil["name"], utensil.get("category", "Uncategorized"), 
                                          utensil["quantity"], utensil["available"], borrowed))
        
        tree.pack(expand=True, fill="both")
    
    def show_add_utensil_dialog(self):
        """Show dialog to add new utensil"""
        dialog = self.create_dialog("Add New Utensil", 450, 350)
        main_frame = tk.Frame(dialog, bg=self.colors["white"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="Add New Utensil", font=("Arial", 16, "bold"), 
                bg=self.colors["white"], fg=self.colors["dark"]).pack(pady=20)
        
        form_frame = tk.Frame(main_frame, bg=self.colors["white"])
        form_frame.pack(fill="x", pady=10)
        
        tk.Label(form_frame, text="Utensil Name:", font=("Arial", 11), bg=self.colors["white"]).grid(row=0, column=0, padx=10, pady=15, sticky="e")
        name_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        name_entry.grid(row=0, column=1, padx=10, pady=15)
        
        tk.Label(form_frame, text="Category:", font=("Arial", 11), bg=self.colors["white"]).grid(row=1, column=0, padx=10, pady=15, sticky="e")
        category_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        category_entry.grid(row=1, column=1, padx=10, pady=15)
        
        tk.Label(form_frame, text="Quantity:", font=("Arial", 11), bg=self.colors["white"]).grid(row=2, column=0, padx=10, pady=15, sticky="e")
        qty_var = tk.IntVar(value=1)
        tk.Spinbox(form_frame, from_=1, to=100, textvariable=qty_var, font=("Arial", 11), width=23).grid(row=2, column=1, padx=10, pady=15)
        
        def add():
            name = name_entry.get().strip()
            category = category_entry.get().strip()
            qty = qty_var.get()
            
            if not name:
                messagebox.showerror("Error", "Please enter utensil name")
                return
            
            new_id = max([u["id"] for u in self.utensils], default=0) + 1
            new_utensil = {"id": new_id, "name": name, "category": category or "Uncategorized", "quantity": qty, "available": qty}
            
            self.utensils.append(new_utensil)
            self.save_utensils()
            messagebox.showinfo("Success", f"Utensil '{name}' added successfully!")
            dialog.destroy()
            self.show_equipment_content()
        
        button_frame = tk.Frame(main_frame, bg=self.colors["white"])
        button_frame.pack(pady=20)
        
        self.create_button(button_frame, "Add", add, self.colors["success"])
        self.create_button(button_frame, "Cancel", dialog.destroy, self.colors["dark"])
    
    def show_edit_utensil_dialog(self):
        """Show dialog to edit utensil"""
        if not self.utensils:
            messagebox.showerror("Error", "No utensils to edit")
            return
        
        dialog = self.create_dialog("Edit Utensil", 450, 350)
        main_frame = tk.Frame(dialog, bg=self.colors["white"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="Edit Utensil", font=("Arial", 16, "bold"), 
                bg=self.colors["white"], fg=self.colors["dark"]).pack(pady=20)
        
        form_frame = tk.Frame(main_frame, bg=self.colors["white"])
        form_frame.pack(fill="x", pady=10)
        
        tk.Label(form_frame, text="Select Utensil:", font=("Arial", 11), bg=self.colors["white"]).grid(row=0, column=0, padx=10, pady=15, sticky="e")
        utensil_names = [u["name"] for u in self.utensils]
        selected_utensil_var = tk.StringVar(value=utensil_names[0] if utensil_names else "")
        utensil_combo = ttk.Combobox(form_frame, textvariable=selected_utensil_var, values=utensil_names, 
                                    font=("Arial", 11), width=23, state="readonly")
        utensil_combo.grid(row=0, column=1, padx=10, pady=15)
        
        tk.Label(form_frame, text="New Name:", font=("Arial", 11), bg=self.colors["white"]).grid(row=1, column=0, padx=10, pady=15, sticky="e")
        name_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        name_entry.grid(row=1, column=1, padx=10, pady=15)
        
        tk.Label(form_frame, text="Category:", font=("Arial", 11), bg=self.colors["white"]).grid(row=2, column=0, padx=10, pady=15, sticky="e")
        category_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        category_entry.grid(row=2, column=1, padx=10, pady=15)
        
        tk.Label(form_frame, text="Total Quantity:", font=("Arial", 11), bg=self.colors["white"]).grid(row=3, column=0, padx=10, pady=15, sticky="e")
        qty_var = tk.IntVar(value=1)
        tk.Spinbox(form_frame, from_=1, to=100, textvariable=qty_var, font=("Arial", 11), width=23).grid(row=3, column=1, padx=10, pady=15)
        
        def load_utensil_data(event=None):
            selected_name = selected_utensil_var.get()
            utensil = next((u for u in self.utensils if u["name"] == selected_name), None)
            if utensil:
                name_entry.delete(0, tk.END)
                name_entry.insert(0, utensil["name"])
                category_entry.delete(0, tk.END)
                category_entry.insert(0, utensil.get("category", ""))
                qty_var.set(utensil["quantity"])
        
        utensil_combo.bind('<<ComboboxSelected>>', load_utensil_data)
        load_utensil_data()
        
        def edit():
            selected_name = selected_utensil_var.get()
            utensil = next((u for u in self.utensils if u["name"] == selected_name), None)
            
            if not utensil:
                messagebox.showerror("Error", "Utensil not found")
                return
            
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showerror("Error", "Please enter utensil name")
                return
            
            utensil["name"] = new_name
            utensil["category"] = category_entry.get().strip() or "Uncategorized"
            old_qty = utensil["quantity"]
            new_qty = qty_var.get()
            
            if new_qty > old_qty:
                utensil["available"] += (new_qty - old_qty)
            elif new_qty < old_qty:
                borrowed = old_qty - utensil["available"]
                if borrowed > new_qty:
                    messagebox.showerror("Error", f"Cannot reduce quantity below borrowed amount ({borrowed})")
                    return
                utensil["available"] = new_qty - borrowed
            
            utensil["quantity"] = new_qty
            self.save_utensils()
            messagebox.showinfo("Success", "Utensil updated successfully!")
            dialog.destroy()
            self.show_equipment_content()
        
        button_frame = tk.Frame(main_frame, bg=self.colors["white"])
        button_frame.pack(pady=20)
        
        self.create_button(button_frame, "Update", edit, self.colors["warning"])
        self.create_button(button_frame, "Cancel", dialog.destroy, self.colors["dark"])
    
    def show_delete_utensil_dialog(self):
        """Show dialog to delete utensil"""
        if not self.utensils:
            messagebox.showerror("Error", "No utensils to delete")
            return
        
        dialog = self.create_dialog("Delete Utensil", 450, 250)
        main_frame = tk.Frame(dialog, bg=self.colors["white"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="Delete Utensil", font=("Arial", 16, "bold"), 
                bg=self.colors["white"], fg=self.colors["dark"]).pack(pady=20)
        
        form_frame = tk.Frame(main_frame, bg=self.colors["white"])
        form_frame.pack(fill="x", pady=10)
        
        tk.Label(form_frame, text="Select Utensil:", font=("Arial", 11), bg=self.colors["white"]).grid(row=0, column=0, padx=10, pady=15, sticky="e")
        utensil_names = [u["name"] for u in self.utensils]
        selected_utensil_var = tk.StringVar(value=utensil_names[0] if utensil_names else "")
        ttk.Combobox(form_frame, textvariable=selected_utensil_var, values=utensil_names, 
                    font=("Arial", 11), width=23, state="readonly").grid(row=0, column=1, padx=10, pady=15)
        
        def delete():
            selected_name = selected_utensil_var.get()
            utensil = next((u for u in self.utensils if u["name"] == selected_name), None)
            
            if not utensil:
                messagebox.showerror("Error", "Utensil not found")
                return
            
            borrowed_count = sum(b["quantity"] for b in self.borrowings if b["utensil_id"] == utensil["id"] and not b.get("returned", False))
            if borrowed_count > 0:
                messagebox.showerror("Error", f"Cannot delete utensil with {borrowed_count} active borrowing(s)")
                return
            
            if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{selected_name}'?"):
                self.utensils.remove(utensil)
                self.save_utensils()
                messagebox.showinfo("Success", "Utensil deleted successfully!")
                dialog.destroy()
                self.show_equipment_content()
        
        button_frame = tk.Frame(main_frame, bg=self.colors["white"])
        button_frame.pack(pady=20)
        
        self.create_button(button_frame, "Delete", delete, self.colors["danger"])
        self.create_button(button_frame, "Cancel", dialog.destroy, self.colors["dark"])
    
    def show_borrower_detail(self, borrower_name):
        """Show detailed view of a borrower"""
        dialog = self.create_dialog(f"Borrower Details - {borrower_name}", 900, 600)
        main_frame = tk.Frame(dialog, bg=self.colors["white"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        header_frame = tk.Frame(main_frame, bg=self.colors["light"])
        header_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(header_frame, text=f"Borrower: {borrower_name}", font=("Arial", 14, "bold"), 
                bg=self.colors["light"]).pack(anchor="w", padx=15, pady=10)
        
        borrower_key = borrower_name.lower().strip()
        borrower_data = self.borrowers.get(borrower_key, {})
        score = self.calculate_credit_score(borrower_name)
        score_color = self.get_credit_score_color(score)
        score_label = self.get_credit_score_label(score)
        
        info_frame = tk.Frame(main_frame, bg=self.colors["white"])
        info_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(info_frame, text=f"Credit Score: {score}/100 ({score_label})", font=("Arial", 11, "bold"), 
                bg=self.colors["white"], fg=score_color).pack(anchor="w", pady=5)
        tk.Label(info_frame, text=f"Total Borrowings: {borrower_data.get('total_borrowings', 0)}", 
                font=("Arial", 11), bg=self.colors["white"]).pack(anchor="w", pady=5)
        tk.Label(info_frame, text=f"On-Time Returns: {borrower_data.get('on_time_returns', 0)}", 
                font=("Arial", 11), bg=self.colors["white"]).pack(anchor="w", pady=5)
        tk.Label(info_frame, text=f"Late Returns: {borrower_data.get('late_returns', 0)}", 
                font=("Arial", 11), bg=self.colors["white"]).pack(anchor="w", pady=5)
        tk.Label(info_frame, text=f"Damaged Items: {borrower_data.get('damaged_items', 0)}", 
                font=("Arial", 11), bg=self.colors["white"]).pack(anchor="w", pady=5)
        
        contact_info = borrower_data.get("contact_info", {})
        if contact_info:
            contact_frame = tk.LabelFrame(main_frame, text="Contact Information", font=("Arial", 11, "bold"), 
                                         bg=self.colors["light"], relief="flat", bd=0)
            contact_frame.pack(fill="x", padx=10, pady=10)
            
            phone = contact_info.get("phone", "N/A")
            email = contact_info.get("email", "N/A")
            
            tk.Label(contact_frame, text=f"Phone: {phone}", font=("Arial", 10), bg=self.colors["light"]).pack(anchor="w", padx=15, pady=5)
            tk.Label(contact_frame, text=f"Email/FB: {email}", font=("Arial", 10), bg=self.colors["light"]).pack(anchor="w", padx=15, pady=5)
        
        history_frame = tk.LabelFrame(main_frame, text="Borrowing History (with Return Notes)", font=("Arial", 12, "bold"), 
                                     bg=self.colors["white"], relief="flat", bd=0)
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tree_frame = tk.Frame(history_frame, bg=self.colors["white"])
        tree_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        columns = ("Utensil", "Qty", "Borrow Date", "Due Date", "Return Date", "Condition", "Notes", "Status")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        for col in columns:
            tree.heading(col, text=col)
        
        tree.column("Utensil", width=120)
        tree.column("Qty", width=40)
        tree.column("Borrow Date", width=100)
        tree.column("Due Date", width=90)
        tree.column("Return Date", width=100)
        tree.column("Condition", width=80)
        tree.column("Notes", width=150)
        tree.column("Status", width=80)
        
        for borrowing in self.borrowings:
            if borrowing["borrower_name"] == borrower_name:
                status = "Returned" if borrowing.get("returned") else ("Overdue" if self.is_overdue(borrowing) else "Active")
                condition = borrowing.get("return_condition", "N/A")
                notes = borrowing.get("return_notes", "N/A")
                tree.insert("", "end", values=(
                    borrowing["utensil_name"],
                    borrowing["quantity"],
                    borrowing["borrow_date"],
                    borrowing.get("due_date", "N/A"),
                    borrowing.get("return_date", "N/A"),
                    condition,
                    notes,
                    status
                ), tags=(status,))
        
        tree.tag_configure("Overdue", background="#ffcccc")
        tree.tag_configure("Active", background="#fff3cd")
        tree.tag_configure("Returned", background="#d4edda")
        
        tree.pack(expand=True, fill="both")
    
    def show_settings_content(self):
        """Settings content"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        title_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        title_frame.pack(fill="x", padx=30, pady=20)
        
        tk.Label(title_frame, text="System Settings", font=("Arial", 24, "bold"), 
                bg=self.colors["bg"], fg=self.colors["dark"]).pack(anchor="w")
        
        settings_frame = tk.Frame(self.main_content, bg=self.colors["white"])
        settings_frame.pack(padx=30, pady=20)
        
        tk.Label(settings_frame, text="Maximum Borrow Limit per Person:", font=("Arial", 12, "bold"), 
                bg=self.colors["white"]).grid(row=0, column=0, padx=20, pady=20, sticky="e")
        
        limit_var = tk.IntVar(value=self.settings["max_borrow_limit"])
        tk.Spinbox(settings_frame, from_=1, to=50, textvariable=limit_var, font=("Arial", 12), width=10).grid(row=0, column=1, padx=20, pady=20, sticky="w")
        
        def save_settings():
            self.settings["max_borrow_limit"] = limit_var.get()
            self.save_settings()
            messagebox.showinfo("Success", "Settings saved successfully!")
        
        tk.Button(settings_frame, text="Save Settings", command=save_settings, font=("Arial", 11, "bold"), 
                 bg=self.colors["success"], fg=self.colors["white"], padx=20, pady=10, 
                 cursor="hand2", relief="flat", bd=0).grid(row=1, column=0, columnspan=2, pady=20)
    
    def show_change_password(self):
        """Show change password dialog"""
        dialog = self.create_dialog("Change Admin Password", 450, 350)
        main_frame = tk.Frame(dialog, bg=self.colors["white"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="Change Admin Password", font=("Arial", 16, "bold"), 
                bg=self.colors["white"], fg=self.colors["dark"]).pack(pady=20)
        
        form_frame = tk.Frame(main_frame, bg=self.colors["white"])
        form_frame.pack(fill="x", pady=10)
        
        tk.Label(form_frame, text="Current Password:", font=("Arial", 11), bg=self.colors["white"]).grid(row=0, column=0, padx=10, pady=15, sticky="e")
        current_pass = tk.Entry(form_frame, font=("Arial", 11), width=25, show="*")
        current_pass.grid(row=0, column=1, padx=10, pady=15)
        
        tk.Label(form_frame, text="New Password:", font=("Arial", 11), bg=self.colors["white"]).grid(row=1, column=0, padx=10, pady=15, sticky="e")
        new_pass = tk.Entry(form_frame, font=("Arial", 11), width=25, show="*")
        new_pass.grid(row=1, column=1, padx=10, pady=15)
        
        tk.Label(form_frame, text="Confirm Password:", font=("Arial", 11), bg=self.colors["white"]).grid(row=2, column=0, padx=10, pady=15, sticky="e")
        confirm_pass = tk.Entry(form_frame, font=("Arial", 11), width=25, show="*")
        confirm_pass.grid(row=2, column=1, padx=10, pady=15)
        
        def change():
            if self.hash_password(current_pass.get()) != self.admin_data["password"]:
                messagebox.showerror("Error", "Current password is incorrect")
                return
            
            if new_pass.get() != confirm_pass.get():
                messagebox.showerror("Error", "New passwords do not match")
                return
            
            if len(new_pass.get()) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters")
                return
            
            self.admin_data["password"] = self.hash_password(new_pass.get())
            self.save_admin()
            messagebox.showinfo("Success", "Password changed successfully!")
            dialog.destroy()
        
        button_frame = tk.Frame(main_frame, bg=self.colors["white"])
        button_frame.pack(pady=20)
        
        self.create_button(button_frame, "Change", change, self.colors["success"])
        self.create_button(button_frame, "Cancel", dialog.destroy, self.colors["dark"])

if __name__ == "__main__":
    root = tk.Tk()
    app = KUBE(root)
    root.mainloop()
