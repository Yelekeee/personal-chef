import subprocess
import sys
import time
import signal
import os

processes = []


def shutdown(sig=None, frame=None):
    for p in processes:
        p.terminate()
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

env = os.environ.copy()

fastapi = subprocess.Popen(
    [sys.executable, "server.py"],
    env=env,
)
processes.append(fastapi)

# Give FastAPI a moment to bind the port before Streamlit starts
time.sleep(2)

streamlit = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"],
    env=env,
)
processes.append(streamlit)

print("FastAPI  → http://localhost:8000")
print("Streamlit → http://localhost:8501")
print("Press Ctrl+C to stop both.")

for p in processes:
    p.wait()
