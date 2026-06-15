from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import subprocess

app = Flask(__name__)

def get_db():
    return sqlite3.connect("onboarding.db")

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        department TEXT,
        job_title TEXT,
        manager TEXT,
        start_date TEXT,
        laptop_needed TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        task_name TEXT,
        status TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(id)
    )
    """)

    conn.commit()
    conn.close()

def create_onboarding_tasks(employee_id, laptop_needed):
    tasks = [
        "Create Microsoft 365 account",
        "Assign Microsoft 365 license",
        "Add user to Teams group",
        "Add user to email distribution list",
        "Create onboarding ticket documentation",
        "Send welcome email"
    ]

    if laptop_needed == "Yes":
        tasks.append("Image and prepare laptop")
        tasks.append("Install standard applications")

    conn = get_db()
    cursor = conn.cursor()

    for task in tasks:
        cursor.execute(
            "INSERT INTO tasks (employee_id, task_name, status) VALUES (?, ?, ?)",
            (employee_id, task, "Pending")
        )

    conn.commit()
    conn.close()

def run_powershell_script(first_name, last_name, email, department):
    try:
        subprocess.run([
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-File", "scripts/create_user.ps1",
            "-FirstName", first_name,
            "-LastName", last_name,
            "-Email", email,
            "-Department", department
        ])
    except Exception as e:
        print("PowerShell script failed:", e)

@app.route("/")
def index():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM employees ORDER BY id DESC")
    employees = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM employees")
    total_employees = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Pending'")
    pending_tasks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Completed'")
    completed_tasks = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        employees=employees,
        total_employees=total_employees,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks
    )

@app.route("/new", methods=["GET", "POST"])
def new_employee():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        department = request.form["department"]
        job_title = request.form["job_title"]
        manager = request.form["manager"]
        start_date = request.form["start_date"]
        laptop_needed = request.form["laptop_needed"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO employees 
        (first_name, last_name, email, department, job_title, manager, start_date, laptop_needed, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            first_name,
            last_name,
            email,
            department,
            job_title,
            manager,
            start_date,
            laptop_needed,
            "Onboarding Started",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        employee_id = cursor.lastrowid
        conn.commit()
        conn.close()

        create_onboarding_tasks(employee_id, laptop_needed)
        run_powershell_script(first_name, last_name, email, department)

        return redirect("/")

    return render_template("new_employee.html")

@app.route("/employee/<int:employee_id>")
def employee_detail(employee_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
    employee = cursor.fetchone()

    cursor.execute("SELECT * FROM tasks WHERE employee_id = ?", (employee_id,))
    tasks = cursor.fetchall()

    conn.close()

    return render_template("employee_detail.html", employee=employee, tasks=tasks)

@app.route("/task/<int:task_id>/complete")
def complete_task(task_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE tasks SET status = 'Completed' WHERE id = ?", (task_id,))

    conn.commit()
    conn.close()

    return redirect(request.referrer)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)