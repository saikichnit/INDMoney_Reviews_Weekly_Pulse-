from services.ingestion_service.service import IngestionService
from services.preprocessing_service.service import PreprocessingService
from services.discovery_service.service import DiscoveryService
from services.classification_service.service import ClassificationService
from services.note_service.service import NoteService
from services.email_service.service import EmailDeliveryService
from services.fee_explainer_service.service import FeeExplainerService
from services.mcp_service.service import MCPService
from services.json_builder.service import JSONBuilder
from services.mcp_service.mcp_client import MCPClient
from services.pdf_service.service import PDFService
from storage.db import DatabaseManager

class IntelligenceOrchestrator:
    def __init__(self):
        self.db = DatabaseManager()
        self.ingestor = IngestionService(self.db)
        self.preprocessor = PreprocessingService(self.db)
        self.discoverer = DiscoveryService()
        self.classifier = ClassificationService()
        self.noter = NoteService()
        self.mailer = EmailDeliveryService()
        self.fee_explainer = FeeExplainerService()
        self.json_builder = JSONBuilder()
        self.mcp_client = MCPClient()
        self.pdf_service = PDFService()

    def run_pipeline(self, fee_types="exit_load,brokerage_fee", max_reviews=300, days=60):
        # Ensure directory structure
        os.makedirs("data/raw", exist_ok=True)
        os.makedirs("data/reports/pdf", exist_ok=True)
        os.makedirs("data/reports/json", exist_ok=True)

        # 1. Ingestion: Try Live API first if in Cloud, fallback to local
        try:
            from services.ingestion_service.real_ingestor import RealIngestor
            real_ingestor = RealIngestor(self.db)
            print("🚀 Cloud Mode: Fetching LIVE reviews from App Stores...")
            raw_data = real_ingestor.fetch_reviews(limit=max_reviews)
        except Exception as e:
            print(f"⚠️ Live Ingestion failed, falling back to local: {e}")
            raw_data = self.ingestor.fetch_from_local("data/raw", limit=max_reviews, days=days)

        if not raw_data:
            print("❌ No reviews found to process.")
            return None

        # 2-4. Preprocessing, Discovery, Classification
        filtered_data = self.preprocessor.process(raw_data)
        signals = self.discoverer.discover_signals(filtered_data)
        themes_data = self.classifier.classify_themes(signals)
        themes = themes_data.get('themes', [])
        
        # 5. Note Generation
        note = self.noter.generate_note(themes, filtered_data)
        
        # 6. Fee Explainer
        requested_fees = fee_types.split(",") if fee_types else ["exit_load"]
        fee_scenarios = self.fee_explainer.explain_multiple(requested_fees)
        
        # 7. Email Delivery Service (Drafting)
        email_draft = self.mailer.prepare_email(note, themes, recipient_name="Stakeholder", fee_scenarios=fee_scenarios)
        
        # 8. Phase 5 Automation: JSON Builder & MCP & PDF
        json_path = None
        pdf_path = None
        try:
            combined_payload, json_path = self.json_builder.build_combined_payload(note, themes, fee_scenarios)
            self.mcp_client.append_to_google_docs(combined_payload)
            pdf_path = self.pdf_service.generate_report_pdf(note, themes, fee_scenarios)
        except Exception as e:
            print(f"Phase 5 (Optional) skipped or failed: {e}")

        # Finalize Report Data & Persistence
        report_data = {
            "weekly_pulse": {
                "summary": note.get('summary'),
                "themes": themes,
                "quotes": note.get('quotes'),
                "action_items": note.get('action_items')
            },
            "fee_scenarios": fee_scenarios,
            "email_draft": email_draft
        }
        
        report_id = self.db.save_report(report_data, len(filtered_data), json_path=json_path, pdf_path=pdf_path)
        return report_id
