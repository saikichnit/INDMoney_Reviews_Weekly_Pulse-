import os
import json
from datetime import datetime

# Layer 1-3 Services
from services.ingestion_service.service import IngestionService
from services.preprocessing_service.service import PreprocessingService
from services.discovery_service.service import DiscoveryService
from services.classification_service.service import ClassificationService

# Layer 4-5 Services
from services.note_service.service import NoteService

# Layer 6-7 Delivery
from services.email_service.service import EmailDeliveryService
from services.fee_explainer_service.service import FeeExplainerService
from services.mcp_service.service import MCPService
from services.json_builder.service import JSONBuilder
from services.mcp_service.mcp_client import MCPClient
from services.pdf_service.service import PDFService
from storage.db import DatabaseManager

class IntelligenceOrchestrator:
    def __init__(self, db_path="data/pulse_production.db"):
        # Absolute path for cloud stability
        abs_db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(abs_db_path), exist_ok=True)
        
        self.db = DatabaseManager(abs_db_path)
        self.ingestor = IngestionService(self.db)
        self.preprocessor = PreprocessingService(self.db)
        self.discoverer = DiscoveryService()
        self.classifier = ClassificationService()
        self.note_gen = NoteService()
        self.mailer = EmailDeliveryService()
        self.fee_explainer = FeeExplainerService()
        self.mcp_client = MCPClient()
        self.pdf_service = PDFService()

    def run_pipeline(self, fee_types="exit_load,brokerage_fee", max_reviews=300, days=60):
        # 1. Ingestion: Try Live API first in Cloud/Prod
        try:
            from services.ingestion_service.real_ingestor import RealIngestor
            real_ingestor = RealIngestor(self.db)
            raw_data = real_ingestor.fetch_reviews(limit=max_reviews)
        except Exception as e:
            print(f"⚠️ Live Ingestion failed/skipped: {e}")
            raw_data = self.ingestor.fetch_from_local("data/raw", limit=max_reviews, days=days)

        if not raw_data:
            return None, None

        # 2-4. Core Synthesis
        filtered_data = self.preprocessor.process(raw_data)
        signals = self.discoverer.discover_signals(filtered_data)
        themes_data = self.classifier.classify_themes(signals)
        
        # 5. Strategic Intelligence
        themes_list = themes_data.get("themes", [])
        note_data = self.note_gen.generate_note(themes_list, filtered_data)
        
        # Add sentiment to filtered_data if missing (Hybrid Logic)
        for r in filtered_data:
            if not r.get('sentiment'):
                rating = int(r.get('rating', 3))
                text = r.get('review_text', '')
                
                # Rule 1: High Rating -> Positive
                if rating >= 4:
                    r['sentiment'] = "Positive"
                # Rule 2: Low Rating -> Negative
                elif rating <= 2:
                    r['sentiment'] = "Negative"
                # Rule 3: Mid Rating -> AI Triage
                else:
                    r['sentiment'] = self.classifier.detect_sentiment(text)
        
        # 7. Financial Education (Elite Layer)
        fee_scenarios = self.fee_explainer.explain_multiple(fee_types.split(","))
        
        # Build Payload
        combined_payload = {
            "summary": note_data.get("summary", "No summary available."),
            "themes": themes_data.get("themes", []),
            "quotes": note_data.get("quotes", []),
            "action_ideas": note_data.get("action_items", []),
            "fee_scenarios": fee_scenarios,
            "review_count": len(filtered_data)
        }

        # 6. Cross-Platform Delivery
        report_id = self.db.save_report(combined_payload, combined_payload['review_count'])
        self.pdf_service.generate_report_pdf(combined_payload, combined_payload['themes'], combined_payload['fee_scenarios'])
        self.mcp_client.append_to_google_docs(combined_payload)
        
        return report_id, combined_payload
