import os
import subprocess
import yaml
import time
import pytz
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Configure Logging
LOG_FILE = os.path.join(os.getcwd(), "logs", "scheduler.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

# Load config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

def log_event(msg, level="INFO"):
    print(f"[{datetime.now()}] {msg}")
    if level == "INFO":
        logging.info(msg)
    elif level == "ERROR":
        logging.error(msg)

def run_weekly_pulse():
    log_event("Triggering Weekly Review Pulse Workflow...")
    
    try:
        # Step 1: Generate Report via CLI
        cli_path = os.path.join(os.getcwd(), "phase4", "cli", "pulse_cli.py")
        
        # Enforce Constraints: 1000 reviews, 8 weeks
        gen_cmd = [
            "python3", cli_path, "generate-report", 
            "--name", config['delivery']['recipient_name'],
            "--max-reviews", str(config['constraints'].get('max_reviews', 1000)),
            "--weeks", str(config['constraints'].get('review_window_weeks', 8))
        ]
        
        log_event(f"Executing CLI Generate: {' '.join(gen_cmd)}")
        gen_res = subprocess.run(
            gen_cmd, 
            capture_output=True, 
            text=True, 
            cwd=os.getcwd(),
            env=os.environ.copy()
        )
        
        if gen_res.returncode == 0 and "SUCCESS" in gen_res.stdout:
            # Extract report ID
            report_id = gen_res.stdout.split('#')[1].split(' ')[0]
            log_event(f"Generation SUCCESS. Report ID: {report_id}")
            
            # Step 2: Send Email via CLI
            send_cmd = [
                "python3", cli_path, "send-email",
                "--id", report_id,
                "--name", config['delivery']['recipient_name'],
                "--email", config['delivery']['recipient_email']
            ]
            log_event(f"Executing CLI Send: {' '.join(send_cmd)}")
            send_res = subprocess.run(
                send_cmd, 
                capture_output=True, 
                text=True, 
                cwd=os.getcwd(),
                env=os.environ.copy()
            )
            
            if send_res.returncode == 0:
                log_event(f"Workflow COMPLETED successfully for {config['delivery']['recipient_email']}")
            else:
                log_event(f"Send FAILED: {send_res.stderr}", "ERROR")
        else:
            log_event(f"Generation FAILED: {gen_res.stderr} {gen_res.stdout}", "ERROR")
            
    except Exception as e:
        log_event(f"CRITICAL ERROR in scheduler trigger: {e}", "ERROR")

if __name__ == "__main__":
    scheduler = BackgroundScheduler(timezone=pytz.timezone(config['schedule']['timezone']))
    
    # Change to 5-minute interval for testing
    # Note: To rollback to weekly, use CronTrigger with config['schedule']['time']
    trigger = IntervalTrigger(minutes=5)
    
    scheduler.add_job(run_weekly_pulse, trigger, next_run_time=datetime.now())
    scheduler.start()
    
    log_event("Scheduler started in TESTING MODE (Interval: 5 mins)")
    log_event(f"Constraints: Max {config['constraints'].get('max_reviews')} reviews, {config['constraints'].get('review_window_weeks')} weeks")
    
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        log_event("Scheduler stopped.")
