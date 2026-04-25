import os
from fpdf import FPDF
from datetime import datetime

class PDFService:
    def __init__(self, storage_dir: str = "data/reports/pdf"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def generate_report_pdf(self, note: dict, themes: list, fee_scenarios: list = None) -> str:
        """
        Generates a pure-vector, high-contrast 2-page elite executive report.
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)
        
        def safe_text(t):
            if not t: return "N/A"
            clean = str(t).replace('\u2022', '-').replace('\u2013', '-').replace('\u2014', '-').replace('\u201c', '"').replace('\u201d', '"').replace('\u2019', "'")
            return clean.encode('latin-1', 'replace').decode('latin-1')

        # 1. Solid Elite Header (Pure Vector)
        pdf.set_fill_color(0, 102, 204) # INDPlus Elite Blue
        pdf.rect(0, 0, 210, 35, 'F')
        
        pdf.set_xy(10, 10)
        pdf.set_font("Helvetica", "B", 20)
        pdf.set_text_color(255, 255, 255) # White
        pdf.cell(190, 10, safe_text("INDPlus Strategic Intelligence"), ln=True)
        
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(200, 220, 255) # Soft Light Blue
        pdf.cell(100, 5, safe_text(f"REPORT ID: {datetime.now().strftime('%Y%m%d%H%M')}"), ln=False)
        pdf.cell(90, 5, safe_text(f"PUBLISHED: {datetime.now().strftime('%B %d, %Y')}"), ln=True, align='R')
        
        # 2. Executive Metadata (Below Header)
        pdf.set_y(40)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(100, 116, 139) # Slate-500
        pdf.cell(190, 5, safe_text("STAKEHOLDER CONFIDENTIAL | EXECUTIVE ACCESS ONLY"), ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(8)

        # 3. Executive Spotlight (High Contrast)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(0, 102, 204)
        pdf.cell(180, 8, safe_text("EXECUTIVE SPOTLIGHT"), ln=True)
        
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(15, 23, 42) # Slate-900 (Ultra Dark Charcoal)
        summary_text = safe_text(note.get('summary', 'Elite synthesis pending...'))
        pdf.multi_cell(180, 6.5, summary_text) # Increased line spacing
        pdf.ln(10)

        # 4. Strategic Themes (Thick Visual Bars)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(190, 10, safe_text("STRATEGIC THEME ANALYSIS"), ln=True)
        pdf.ln(2)
        
        pdf.set_font("Helvetica", "B", 10)
        if themes:
            for t in themes[:5]:
                name = t.get('name') if isinstance(t, dict) else t
                percent = int(t.get('percentage', 0)) if isinstance(t, dict) else 0
                
                # Label
                pdf.set_text_color(30, 41, 59)
                pdf.cell(100, 7, safe_text(name), ln=False)
                pdf.set_text_color(100, 116, 139)
                pdf.cell(90, 7, safe_text(f"{percent}% Impact"), ln=True, align='R')
                
                # Thick Bar
                curr_y = pdf.get_y()
                pdf.set_fill_color(241, 245, 249)
                pdf.rect(10, curr_y, 190, 3, 'F') # 3mm Thick
                pdf.set_fill_color(0, 102, 204)
                pdf.rect(10, curr_y, (percent / 100) * 190, 3, 'F')
                pdf.ln(7)

        # 5. Golden User Quotes (Clean Callouts)
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(190, 10, safe_text("VOICE OF CUSTOMER: CRITICAL SIGNALS"), ln=True)
        pdf.ln(2)
        
        for q in note.get('quotes', [])[:3]:
            start_q_y = pdf.get_y()
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(51, 65, 85) # Slate-700
            pdf.set_x(15)
            pdf.multi_cell(175, 6, safe_text(f'"{q}"'))
            end_q_y = pdf.get_y()
            
            # Heavy Blue accent line
            pdf.set_fill_color(0, 102, 204)
            pdf.rect(10, start_q_y, 2, (max(6, end_q_y - start_q_y)), 'F')
            pdf.ln(4)

        # 6. Tactical Roadmap
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(190, 10, safe_text("STRATEGIC ACTION ROADMAP"), ln=True)
        pdf.ln(2)
        
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 41, 59)
        for a in note.get('action_items', [])[:4]:
            pdf.cell(8, 7, safe_text("•"), ln=False, align='C')
            pdf.multi_cell(180, 7, safe_text(a))
            pdf.ln(1)

        # 7. Financial Education
        if fee_scenarios:
            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(190, 10, safe_text("STRATEGIC FINANCIAL EDUCATION"), ln=True)
            pdf.ln(2)
            
            for fee in fee_scenarios[:2]:
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(0, 102, 204)
                pdf.cell(190, 7, safe_text(fee.get('scenario_name')), ln=True)
                
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(51, 65, 85)
                for bullet in fee.get('explanation_bullets', [])[:3]:
                    pdf.cell(8, 6, safe_text("-"), ln=False, align='C')
                    pdf.multi_cell(180, 6, safe_text(bullet))
                
                # Source Link
                if fee.get('source_links'):
                    pdf.set_font("Helvetica", "I", 8)
                    pdf.set_text_color(100, 116, 139)
                    pdf.cell(190, 6, safe_text(f"Source: {fee.get('source_links')[0]}"), ln=True)
                pdf.ln(4)

        # Footer
        pdf.set_y(-15)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(148, 163, 184) # Slate-400
        pdf.cell(190, 10, safe_text("CONFIDENTIAL | ELITE STAKEHOLDER ARCHIVE | INDPLUS PROFESSIONAL v2.5"), align='C')
        
        filename = f"INDPlus_Elite_Pulse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.storage_dir, filename)
        pdf.output(filepath)
        
        return filepath
