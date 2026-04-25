from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import sys

# Add phase2 and phase3 to path for cross-phase access
sys.path.append(os.path.join(os.getcwd(), 'phase2'))
sys.path.append(os.path.join(os.getcwd(), 'phase3'))

from storage.db import DatabaseManager
from services.ingestion_service.service import IngestionService
from services.preprocessing_service.service import PreprocessingService
from llm_orchestrator.orchestrator import ParallelOrchestratorV3
from analytics.trends import AnalyticsEngine

load_dotenv()

app = FastAPI(title="INDMoney Pulse Advanced - Phase 3")
templates = Jinja2Templates(directory="phase3/templates")

db = DatabaseManager()
ingestor = IngestionService(db)
preprocessor = PreprocessingService(db)
orchestrator = ParallelOrchestratorV3()
analytics = AnalyticsEngine(db)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    reports = db.get_all_reports()
    trends = analytics.get_weekly_trends()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "reports": reports,
        "trends": trends
    })

@app.post("/api/v3/generate")
async def generate_advanced_report():
    try:
        # 1. Ingestion (Phase 2 Logic)
        raw_data = ingestor.fetch_from_local("data/raw")
        
        # 2. Preprocessing (Phase 2 Logic)
        filtered_data = preprocessor.process(raw_data)
        
        # 3. Parallel LLM Analysis (Phase 3 New)
        final_output = await orchestrator.run_pipeline(filtered_data)
        
        # 4. Storage & Feedback Loop
        # We store the final aggregated report
        report_id = db.save_report(final_output, len(filtered_data))
        
        return {"report_id": report_id, "output": final_output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
