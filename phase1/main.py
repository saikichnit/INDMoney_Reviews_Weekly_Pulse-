from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import json
import yaml
from dotenv import load_dotenv
from ingestion.ingestor import Ingestor
from preprocessing.processor import Processor
from llm_pipeline.orchestrator import GroqOrchestrator

# Load environment variables from .env
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="phase1/templates")

# Load config
with open("phase1/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize Services
ingestor = Ingestor(max_reviews=config['max_reviews'])
processor = Processor(min_words=config['min_word_count'])
orchestrator = GroqOrchestrator()

RAW_DATA_PATH = config['paths']['raw_data']
OUTPUT_DIR = config['paths']['output_dir']

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    reports = []
    if os.path.exists(OUTPUT_DIR):
        reports = sorted(os.listdir(OUTPUT_DIR), reverse=True)
    return templates.TemplateResponse("index.html", {"request": request, "reports": reports})

@app.post("/generate")
async def generate_report():
    # 1. Ingest
    files = [f for f in os.listdir(RAW_DATA_PATH) if f.endswith(('.csv', '.json'))]
    if not files: return {"error": "No raw data found."}
    
    all_reviews = []
    for f in files:
        all_reviews.extend(ingestor.load_from_file(os.path.join(RAW_DATA_PATH, f)))
    
    # Global sort by date (latest first) and cap at max_reviews
    all_reviews.sort(key=lambda x: x.get('date', ''), reverse=True)
    all_reviews = all_reviews[:config['max_reviews']]
    
    # 2. Preprocess (Word count, Language, PII)
    processed = processor.process_batch(all_reviews)
    
    # 3. LLM Pipeline
    report = orchestrator.generate_report(processed)
    
    # 4. Save Output
    if "error" not in report:
        report['metadata'] = {
            "reviews_processed": len(processed),
            "original_count": len(all_reviews)
        }
        filename = f"pulse_{len(os.listdir(OUTPUT_DIR)) + 1}.json"
        with open(os.path.join(OUTPUT_DIR, filename), 'w') as f:
            json.dump(report, f, indent=4)
            
    return report

@app.get("/report/{filename}")
async def get_report(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {"error": "Not found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
