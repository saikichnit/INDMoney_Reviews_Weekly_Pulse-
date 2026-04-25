import os
import sys
from scheduler import run_weekly_pulse

# Add root to path for CLI subprocess
sys.path.append(os.getcwd())

if __name__ == "__main__":
    print("Simulating a scheduled run...")
    run_weekly_pulse()
