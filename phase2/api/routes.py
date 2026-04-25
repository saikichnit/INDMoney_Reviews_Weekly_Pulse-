from fastapi import APIRouter, HTTPException
from services.intelligence_orchestrator import IntelligenceOrchestrator
from services.email_service.service import EmailDeliveryService
from services.reviews_service import ReviewsService
from services.analytics_service import AnalyticsService
from services.ideation_service import IdeationService
from storage.db import DatabaseManager

router = APIRouter()
db = DatabaseManager()
orchestrator = IntelligenceOrchestrator()
email_service = EmailDeliveryService()

# Module Services
reviews_service = ReviewsService()
analytics_service = AnalyticsService()
ideation_service = IdeationService()

@router.get("/reports")
async def get_reports():
    return db.get_all_reports()

@router.get("/reports/{report_id}")
async def get_report(report_id: int):
    report = db.get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.post("/generate-report")
async def generate_report(days: int = 30, max_reviews: int = 1000, fee_types: str = "exit_load,brokerage_fee"):
    try:
        report_id = orchestrator.run_pipeline(days=days, max_reviews=max_reviews, fee_types=fee_types)
        return {"message": "Report generated successfully", "report_id": report_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-email/{report_id}")
async def send_email(report_id: int, recipient_email: str):
    report = db.get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    success = email_service.deliver(
        recipient_email=recipient_email,
        subject=report.get('email_subject'),
        body=report.get('email_body'),
        attachment_path=report.get('pdf_path')
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Email delivery failed")
    
    return {"message": "Report delivered to stakeholder"}

# --- NEW PLATFORM ENDPOINTS ---

@router.get("/reviews")
async def get_reviews(platform: str = 'all', sentiment: str = None, rating: int = None, time_range: str = '30d', limit: int = 5000, category: str = None):
    # Ensure platform is handled correctly for 'all'
    platform_filter = None if platform.lower() == 'all' else platform.lower()
    return reviews_service.get_reviews(platform=platform_filter, sentiment=sentiment, rating=rating, time_range=time_range, limit=limit, category=category)

@router.get("/reviews/metrics")
async def get_metrics(platform: str = 'all', time_range: str = '30d'):
    platform_filter = None if platform.lower() == 'all' else platform.lower()
    return reviews_service.get_triage_metrics(platform=platform_filter, time_range=time_range)

@router.get("/analytics")
async def get_analytics(time_range: str = '30d'):
    return analytics_service.get_full_analytics(time_range=time_range)

@router.get("/health-metrics")
async def get_health():
    return reviews_service.get_stats()

@router.post("/reviews/sync")
async def sync_reviews():
    count = reviews_service.sync_live_reviews()
    return {"message": f"Successfully ingested {count} live reviews from Android & iOS (last 360 days)", "count": count}

@router.get("/ideas")
async def get_ideas():
    return ideation_service.get_all_ideas()

@router.post("/generate-ideas")
async def generate_ideas():
    ideas = ideation_service.generate_product_ideas()
    return {"message": "AI Ideation complete", "ideas": ideas}

@router.post("/reviews/{id}/assign")
async def assign_review(id: int, body: dict):
    assigned_to = body.get('assigned_to')
    if not assigned_to:
        raise HTTPException(status_code=400, detail="Missing assigned_to")
    
    success = reviews_service.assign_review(id, assigned_to)
    if not success:
        raise HTTPException(status_code=500, detail="Assignment failed")
    
    return {"message": f"Successfully assigned to {assigned_to}", "assigned_to": assigned_to}
