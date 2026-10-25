from datetime import datetime
import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# Optional matplotlib import for graph view
try:
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = True  # Will fallback with an error message if missing


class BMIDatabase:

  def __init__(self, db_name="bmi_records.db"):
    self.db_name = db_name
    self.init_db()

  def get_connection(self):
    try:
      return sqlite3.connect(self.db_name)
    except sqlite3.Error as e:
      messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
      return None

  def init_db(self):
    conn = self.get_connection()
    if conn:
      try:
        cursor = conn.cursor()
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL
                    )
                """)
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        date TEXT,
                        weight REAL,
                        height REAL,
                        bmi REAL,
                        category TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
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
      users = [row[0] for row in cursor.fetchall()]
      return users
    except sqlite3.Error as e:
      messagebox.showerror(
          "Database Error", f"Failed to read users from database: {e}"
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
      messagebox.showerror("Database Error", f"Failed to save user: {e}")
      return False
    finally:
      conn.close()

  def save_record(self, username, weight, height, bmi, category):
    conn = self.get_connection()
    if not conn:
      return False
    try:
      cursor = conn.cursor()
      cursor.execute("SELECT id FROM users WHERE name = ?", (username,))
      result = cursor.fetchone()
      if not result:
        return False
      user_id = result[0]
      date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
      cursor.execute(
          """
                INSERT INTO records (user_id, date, weight, height, bmi, category)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
          (user_id, date_str, weight, height, bmi, category),
      )
      conn.commit()
      return True
    except sqlite3.Error as e:
      messagebox.showerror("Database Error", f"Failed to save BMI record: {e}")
      return False
    finally:
      conn.close()

  def get_history(self, username):
    conn = self.get_connection()
    if not conn:
      return []
    try:
      cursor = conn.cursor()
      cursor.execute(
          """
                r.date, r.weight, r.height, r.bmi, r.category
                FROM records r
                JOIN users u ON r.user_id = u.id
                WHERE u.name = ?
                ORDER BY r.id ASC
            """,
          (username,),
      )
      return cursor.fetchall()
    except sqlite3.Error as e:
      messagebox.showerror("Database Error", f"Failed to fetch history: {e}")
      return []
    finally:
      conn.close()


class AdvancedBMICalculatorApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Advanced BMI Calculator")
    self.root.geometry("480px620")
    self.root.minsize(450, 580)

    self.db = BMIDatabase()

    # Styling colors
    self.bg_color = "#f4f6f9"
    self.root.configure(bg=self.bg_color)

    self.create_widgets()
    self.load_users()

  def create_widgets(self):
    # Main Title
    title_label = tk.Label(
        self.root,
        text="BMI Calculator & Tracker",
        font=("Arial", 16, "bold"),
        bg=self.bg_color,
        fg="#333333",
    )
    title_label.pack(pady=10)

    # User Selection Frame
    user_frame = tk.LabelFrame(
        self.root,
        text=" User Management ",
        font=("Arial", 10, "bold"),
        bg=self.bg_color,
        padx=10,
        pady=10,
    )
    user_frame.pack(fill="x", padx=20, pady=5)

    tk.Label(
        user_frame, text="Select User:", bg=self.bg_color, font=("Arial", 10)
    ).grid(row=0, column=0, sticky="w", padx=5)

    self.user_combobox = ttk.Combobox(
        user_frame, state="readonly", width=18, font=("Arial", 10)
    )
    self.user_combobox.grid(row=0, column=1, padx=5)
    self.user_combobox.bind("<<ComboboxSelected>>", self.on_user_select)

    self.new_user_entry = tk.Entry(
        user_frame, width=15, font=("Arial", 10)
    )
    self.new_user_entry.grid(row=0, column=2, padx=5)
    self.new_user_entry.insert(0, "New User Name")

    add_user_btn = tk.Button(
        user_frame,
        text="Add User",
        command=self.handle_add_user,
        bg="#007bff",
        fg="white",
        font=("Arial", 9, "bold"),
    )
    add_user_btn.grid(row=0, column=3, padx=5)

    # Input Frame
    input_frame = tk.LabelFrame(
        self.root,
        text=" Enter Measurements ",
        font=("Arial", 10, "bold"),
        bg=self.bg_color,
        padx=10,
        pady=10,
    )
    input_frame.pack(fill="x", padx=20, pady=10)

    tk.Label(
        input_frame, text="Weight (kg):", bg=self.bg_color, font=("Arial", 10)
    ).grid(row=0, column=0, sticky="w", pady=8, padx=5)
    self.weight_entry = tk.Entry(input_frame, font=("Arial", 11), width=15)
    self.weight_entry.grid(row=0, column=1, pady=8, padx=5)

    tk.Label(
        input_frame, text="Height (m):", bg=self.bg_color, font=("Arial", 10)
    ).grid(row=1, column=0, sticky="w", pady=8, padx=5)
    self.height_entry = tk.Entry(input_frame, font=("Arial", 11), width=15)
    self.height_entry.grid(row=1, column=1, pady=8, padx=5)

    # Calculate Button
    calc_btn = tk.Button(
        self.root,
        text="Calculate & Save BMI",
        command=self.calculate_bmi,
        bg="#28a745",
        fg="white",
        font=("Arial", 11, "bold"),
        pady=5,
    )
    calc_btn.pack(fill="x", padx=20, pady=5)

    # Result Display Frame
    result_frame = tk.Frame(self.root, bg=self.bg_color, pady=5)
    result_frame.pack(fill="x", padx=20)

    self.result_label = tk.Label(
        result_frame,
        text="BMI: --",
        font=("Arial", 12, "bold"),
        bg=self.bg_color,
        fg="#333",
    )
    self.result_label.pack(anchor="w")

    self.category_label = tk.Label(
        result_frame,
        text="Category: --",
        font=("Arial", 12, "bold"),
        bg=self.bg_color,
        fg="#333",
    )
    self.category_label.pack(anchor="w", pady=2)

    # History & Graph Frame
    history_frame = tk.LabelFrame(
        self.root,
        text=" History & Trends ",
        font=("Arial", 10, "bold"),
        bg=self.bg_color,
        padx=10,
        pady=10,
    )
    history_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Treeview for history log
    columns = ("Date", "Weight", "Height", "BMI", "Category")
    self.tree = ttk.Treeview(
        history_frame, columns=columns, show="headings", height=5
    )
    for col in columns:
      self.tree.heading(col, text=col)
      self.tree.column(col, width=75, anchor="center")
    self.tree.pack(fill="both", expand=True, pady=5)

    # Graph Button
    graph_btn = tk.Button(
        history_frame,
        text="Show Trend Graph",
        command=self.show_trend_graph,
        bg="#17a2b8",
        fg="white",
        font=("Arial", 10, "bold"),
    )
    graph_btn.pack(fill="x", pady=5)

  def load_users(self):
    users = self.db.get_users()
    self.user_combobox["values"] = users
    if users:
      self.user_combobox.set(users[0])
      self.update_history_table(users[0])

  def handle_add_user(self):
    name = self.new_user_entry.get().strip()
    if not name or name == "New User Name":
      messagebox.showerror("Error", "Please enter a valid user name.")
      return
    success = self.db.add_user(name)
    if success:
      self.load_users()
      self.user_combobox.set(name)
      self.update_history_table(name)
      self.new_user_entry.delete(0, tk.END)

  def on_user_select(self, event):
    selected_user = self.user_combobox.get()
    if selected_user:
      self.update_history_table(selected_user)

  def update_history_table(self, username):
    for row in self.tree.get_children():
      self.tree.delete(row)
    records = self.db.get_history(username)
    for rec in records:
      # rec format: (date, weight, height, bmi, category)
      formatted_rec = (
          rec[0],
          f"{rec[1]:.1f}",
          f"{rec[2]:.2f}",
          f"{rec[3]:.2f}",
          rec[4],
      )
      self.tree.insert("", tk.END, values=formatted_rec)

  def calculate_bmi(self):
    current_user = self.user_combobox.get()
    if not current_user:
      messagebox.showerror("Error", "Please select or add a user profile first.")
      return

    # Input Validation: non-numeric check and negative values
    try:
      weight_str = self.weight_entry.get().strip()
      height_str = self.height_entry.get().strip()

      if not weight_str or not height_str:
        raise ValueError("Fields cannot be empty.")

      weight = float(weight_str)
      height = float(height_str)

      if weight <= 0 or height <= 0:
        raise ValueError("Weight and height must be positive numbers.")
    except ValueError as e:
      messagebox.showerror(
          "Invalid Input",
          f"Please enter valid numeric values for weight and height.\n({e})",
      )
      return

    # Formula: BMI = weight / (height²)
    bmi = weight / (height**2)
    bmi_rounded = round(bmi, 2)

    # Standard Categories & Colour-Coded Feedback
    if bmi < 18.5:
      category = "Underweight"
      color = "#ffc107"  # Yellow / Orange
    elif 18.5 <= bmi <= 24.9:
      category = "Normal"
      color = "#28a745"  # Green
    elif 25.0 <= bmi <= 29.9:
      category = "Overweight"
      color = "#fd7e14"  # Dark Orange
    else:
      category = "Obese"
      color = "#dc3545"  # Red

    # Display results with color-coded feedback
    self.result_label.config(
        text=f"BMI: {bmi_rounded}", fg=color
    )
    self.category_label.config(
        text=f"Category: {category}", fg=color
    )

    # Save to SQLite database
    success = self.db.save_record(
        current_user, weight, height, bmi_rounded, category
    )
    if success:
      self.update_history_table(current_user)

  def show_trend_graph(self):
    current_user = self.user_combobox.get()
    if not current_user:
      messagebox.showerror("Error", "No user selected.")
      return

    records = self.db.get_history(current_user)
    if not records:
      messagebox.showinfo(
          "No Data", f"No historical records found for {current_user}."
      )
      return

    dates = [rec[0] for rec in records]
    bmis = [rec[3] for rec in records]

    # Plot trend using matplotlib
    try:
      plt.figure(figsize=(7, 4))
      plt.plot(dates, bmis, marker="o", linestyle="-", color="#007bff", linewidth=2)
      plt.axhline(
          y=18.5, color="orange", linestyle="--", label="Underweight Limit"
      )
      plt.axhline(y=24.9, color="green", linestyle="--", label="Normal Max")
      plt.axhline(y=29.9, color="red", linestyle="--", label="Overweight Max")

      plt.title(f"BMI Trend Over Time - {current_user}")
      plt.xlabel("Date & Time")
      plt.ylabel("BMI Value")
      plt.xticks(rotation=30, ha="right")
      plt.legend()
      plt.tight_layout()
      plt.show()
    except Exception as e:
      messagebox.showerror("Graph Error", f"Could not generate graph: {e}")


if __name__ == "__main__":
  root = tk.Tk()
  app = AdvancedBMICalculatorApp(root)
  root.mainloop()