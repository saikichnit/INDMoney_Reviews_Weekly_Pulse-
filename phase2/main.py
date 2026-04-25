from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from api.routes import router as api_router
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="INDMoney Pulse Production")
templates = Jinja2Templates(directory="phase2/templates")

# CORS for UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API
app.include_router(api_router, prefix="/api")

# Scheduler
scheduler = BackgroundScheduler()

def scheduled_job():
    print("MOCK: Running weekly scheduled pulse...")
    # This would call the same logic as /generate-report
    pass

scheduler.add_job(scheduled_job, 'cron', day_of_week='mon', hour=9)
scheduler.start()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
