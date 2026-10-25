import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class BMIDatabase:
    """Handles all SQLite database operations with error handling."""

    def __init__(self, db_name="bmi_records.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        try:
            return sqlite3.connect(self.db_name)
        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error", f"Failed to connect to database: {e}"
            )
            return None

    def init_db(self):
        conn = self.get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    weight REAL,
                    height REAL,
                    bmi REAL,
                    category TEXT,
                    date TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """
            )
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error", f"Failed to initialize database tables: {e}"
            )
        finally:
            conn.close()

    def get_users(self):
        conn = self.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM users ORDER BY name")
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error", f"Failed to fetch users: {e}"
            )
            return []
        finally:
            conn.close()

    def add_user(self, name):
        conn = self.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO users (name) VALUES (?)", (name,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add user: {e}")
            return False
        finally:
            conn.close()

    def save_record(self, user_name, weight, height, bmi, category, date_str):
        conn = self.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            # Ensure user exists and get ID
            cursor.execute("SELECT id FROM users WHERE name = ?", (user_name,))
            res = cursor.fetchone()
            if not res:
                cursor.execute("INSERT INTO users (name) VALUES (?)", (user_name,))
                user_id = cursor.lastrowid
            else:
                user_id = res[0]

            cursor.execute(
                """
                INSERT INTO records (user_id, weight, height, bmi, category, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (user_id, weight, height, bmi, category, date_str),
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error", f"Failed to save BMI record: {e}"
            )
            return False
        finally:
            conn.close()

    def get_history(self, user_name):
        conn = self.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT r.date, r.weight, r.height, r.bmi, r.category 
                FROM records r
                JOIN users u ON r.user_id = u.id
                WHERE u.name = ?
                ORDER BY r.id ASC
            """,
                (user_name,),
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error", f"Failed to retrieve history: {e}"
            )
            return []
        finally:
            conn.close()


class BMIApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Multi-User BMI Calculator")
        self.root.geometry("600x650")
        self.root.config(bg="#f4f6f9")

        self.db = BMIDatabase()

        # Styles
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        # Title Label
        title_label = tk.Label(
            self.root,
            text="BMI Tracker & Analyzer",
            font=("Arial", 18, "bold"),
            bg="#f4f6f9",
            fg="#2c3e50",
        )
        title_label.pack(pady=10)

        # User Management Frame
        user_frame = tk.LabelFrame(
            self.root,
            text=" User Profile ",
            font=("Arial", 11, "bold"),
            bg="#f4f6f9",
            fg="#34495e",
        )
        user_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(
            user_frame, text="Select/Add User:", bg="#f4f6f9", font=("Arial", 10)
        ).grid(row=0, column=0, padx=10, pady=8, sticky="w")

        self.user_combo = ttk.Combobox(
            user_frame, state="normal", width=18, font=("Arial", 10)
        )
        self.user_combo.grid(row=0, column=1, padx=5, pady=8)

        add_user_btn = tk.Button(
            user_frame,
            text="Add User",
            command=self.handle_add_user,
            bg="#3498db",
            fg="white",
            font=("Arial", 9, "bold"),
        )
        add_user_btn.grid(row=0, column=2, padx=10, pady=8)

        # Input Frame
        input_frame = tk.LabelFrame(
            self.root,
            text=" Measurements ",
            font=("Arial", 11, "bold"),
            bg="#f4f6f9",
            fg="#34495e",
        )
        input_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(
            input_frame, text="Weight (kg):", bg="#f4f6f9", font=("Arial", 10)
        ).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.weight_entry = tk.Entry(
            input_frame, font=("Arial", 10), width=15
        )
        self.weight_entry.grid(row=0, column=1, padx=10, pady=8)

        tk.Label(
            input_frame, text="Height (cm):", bg="#f4f6f9", font=("Arial", 10)
        ).grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.height_entry = tk.Entry(
            input_frame, font=("Arial", 10), width=15
        )
        self.height_entry.grid(row=1, column=1, padx=10, pady=8)

        calc_btn = tk.Button(
            input_frame,
            text="Calculate & Save BMI",
            command=self.calculate_bmi,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 10, "bold"),
        )
        calc_btn.grid(row=2, column=0, columnspan=2, pady=12)

        # Result Display Frame
        self.result_frame = tk.Frame(self.root, bg="#f4f6f9")
        self.result_frame.pack(fill="x", padx=20, pady=5)

        self.result_label = tk.Label(
            self.result_frame,
            text="BMI: -- | Category: --",
            font=("Arial", 12, "bold"),
            bg="#f4f6f9",
            fg="#7f8c8d",
        )
        self.result_label.pack()

        # Action Buttons for Visualizing
        action_frame = tk.Frame(self.root, bg="#f4f6f9")
        action_frame.pack(fill="x", padx=20, pady=10)

        graph_btn = tk.Button(
            action_frame,
            text="Show BMI Trend Graph",
            command=self.show_graph_window,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 10, "bold"),
        )
        graph_btn.pack(side="left", expand=True, fill="x", padx=5)

        history_btn = tk.Button(
            action_frame,
            text="View History Table",
            command=self.show_history_window,
            bg="#e67e22",
            fg="white",
            font=("Arial", 10, "bold"),
        )
        history_btn.pack(side="right", expand=True, fill="x", padx=5)

    def load_users(self):
        users = self.db.get_users()
        self.user_combo["values"] = users
        if users:
            self.user_combo.set(users[0])

    def handle_add_user(self):
        name = self.user_combo.get().strip()
        if not name:
            messagebox.showwarning(
                "Warning", "Please enter a valid name for the user."
            )
            return
        if self.db.add_user(name):
            messagebox.Success = messagebox.showinfo(
                "Success", f"User '{name}' added successfully."
            )
            self.load_users()
            self.user_combo.set(name)

    def calculate_bmi(self):
        user_name = self.user_combo.get().strip()
        if not user_name:
            messagebox.showerror(
                "Error", "Please select or enter a user name first."
            )
            return

        try:
            weight = float(self.weight_entry.get())
            height_cm = float(self.height_entry.get())

            if weight <= 0 or height_cm <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Please enter valid numeric values for weight and height.",
            )
            return

        # BMI Calculation
        height_m = height_cm / 100.0
        bmi = round(weight / (height_m**2), 2)

        # Determine category and color feedback
        if bmi < 18.5:
            category = "Underweight"
            color = "#3498db"  # Blue
        elif 18.5 <= bmi < 25.0:
            category = "Normal weight"
            color = "#2ecc71"  # Green
        elif 25.0 <= bmi < 30.0:
            category = "Overweight"
            color = "#f1c40f"  # Yellow/Orange
        else:
            category = "Obese"
            color = "#e74c3c"  # Red

        # Update UI feedback
        self.result_label.config(
            text=f"BMI: {bmi} | Category: {category}", fg=color
        )

        import datetime

        date_str = datetime.date.today().strftime("%Y-%m-%d")

        # Save to database
        self.db.save_record(user_name, weight, height_cm, bmi, category, date_str)
        self.load_users()

    def show_history_window(self):
        user_name = self.user_combo.get().strip()
        if not user_name:
            messagebox.showerror("Error", "Please select a user.")
            return

        history = self.db.get_history(user_name)

        hist_win = tk.Toplevel(self.root)
        hist_win.title(f"History for {user_name}")
        hist_win.geometry("500x350")

        cols = ("Date", "Weight (kg)", "Height (cm)", "BMI", "Category")
        tree = ttk.Treeview(hist_win, columns=cols, show="headings")

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=90, anchor="center")

        for row in history:
            tree.insert("", "end", values=row)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

    def show_graph_window(self):
        user_name = self.user_combo.get().strip()
        if not user_name:
            messagebox.showerror("Error", "Please select a user.")
            return

        history = self.db.get_history(user_name)
        if not history:
            messagebox.showinfo(
                "No Data", f"No records found for user '{user_name}'."
            )
            return

        dates = [row[0] for row in history]
        bmis = [row[3] for row in history]

        graph_win = tk.Toplevel(self.root)
        graph_win.title(f"BMI Trend - {user_name}")
        graph_win.geometry("600x400")

        # Create Matplotlib figure
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(dates, bmis, marker="o", linestyle="-", color="#2980b9")
        ax.set_title(f"BMI Progress Over Time ({user_name})")
        ax.set_xlabel("Date")
        ax.set_ylabel("BMI Value")
        ax.grid(True, linestyle="--", alpha=0.6)
        plt.xticks(rotation=45)
        fig.tight_layout()

        # Embed matplotlib graph inside Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=graph_win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = BMIApp(root)
    root.mainloop()