import subprocess
import time
import webbrowser
import os

# Full path to main.py
app_path = "/Volumes/D_Drive/business insights pro 21 Jun 2025/main.py"

# Optional: Set working directory so Streamlit can access files correctly
os.chdir(os.path.dirname(app_path))

# Launch Streamlit in the background
process = subprocess.Popen(["streamlit", "run", app_path])

# Wait until server starts (safe buffer)
time.sleep(5)

# Open default web browser to Streamlit port
webbrowser.open_new("http://localhost:8501")
