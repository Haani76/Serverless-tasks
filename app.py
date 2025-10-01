import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import shutil

# --- Database Setup (keep from Day 1) ---
def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        timestamp TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )""")
    conn.commit()
    conn.close()

def log_task(task):
    """Records a task in the logs table"""
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("INSERT INTO logs (task, timestamp) VALUES (?, ?)", 
              (task, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# --- Task Functions ---
def backup_files():
    """Backs up the database file"""
    try:
        # Create backup folder if it doesn't exist
        os.makedirs("backup", exist_ok=True)
        
        # Copy the database
        shutil.copy("tasks.db", "backup/tasks_backup.db")
        
        # Log the action
        log_task("Backup completed")
        return True
    except Exception as e:
        st.error(f"Backup failed: {str(e)}")
        return False

def provision_user():
    """Creates a new simulated user"""
    try:
        conn = sqlite3.connect("tasks.db")
        c = conn.cursor()
        
        # Generate a unique username
        username = f"User_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Insert into users table
        c.execute("INSERT INTO users (name) VALUES (?)", (username,))
        conn.commit()
        conn.close()
        
        log_task(f"User provisioned: {username}")
        return username
    except Exception as e:
        st.error(f"User provisioning failed: {str(e)}")
        return None

def generate_report():
    """Generates a CSV report of all task logs"""
    try:
        conn = sqlite3.connect("tasks.db")
        
        # Read logs from database
        df = pd.read_sql("SELECT * FROM logs ORDER BY id DESC", conn)
        
        # Save to CSV
        df.to_csv("task_report.csv", index=False)
        conn.close()
        
        log_task("Report generated")
        return df
    except Exception as e:
        st.error(f"Report generation failed: {str(e)}")
        return None

# --- Initialize ---
init_db()

# --- UI ---

st.title("⚡ Serverless Task Automation Platform")

st.markdown("""
Welcome! This platform automates common IT tasks:
- 📦 **Backup Files**: Saves a copy of your database
- 👤 **Provision User**: Creates a new simulated user
- 📊 **Generate Report**: Exports task logs to CSV
""")

st.divider()



# Task selector dropdown
task = st.selectbox(
    "Pick a task:",
    ["Backup Files", "Provision User", "Generate Report"]
)


# Run button
if st.button("▶️ Run Now", type="primary"):
    st.info(f"Running: {task}...")
    
    if task == "Backup Files":
        if backup_files():
            st.success("✅ Backup completed! Check the 'backup' folder.")
    
    elif task == "Provision User":
        username = provision_user()
        if username:
            st.success(f"✅ User created: {username}")
    
    elif task == "Generate Report":
        df = generate_report()
        if df is not None:
            st.success("✅ Report generated as 'task_report.csv'")
            st.dataframe(df)



# --- Display Logs ---
st.divider()
st.subheader("📜 Task Logs")

conn = sqlite3.connect("tasks.db")
logs_df = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 50", conn)
conn.close()

if not logs_df.empty:
    st.dataframe(logs_df, use_container_width=True)
else:
    st.info("No tasks have been run yet!")



st.divider()
st.subheader("👥 Provisioned Users")

conn = sqlite3.connect("tasks.db")
users_df = pd.read_sql("SELECT * FROM users ORDER BY id DESC", conn)
conn.close()

if not users_df.empty:
    st.dataframe(users_df, use_container_width=True)
else:
    st.info("No users have been provisioned yet!")