import streamlit as st
import os
import sys
from datetime import datetime

# Add phase2 to path for service discovery
sys.path.append(os.path.join(os.getcwd(), "phase2"))
sys.path.append(os.path.join(os.getcwd(), "phase3"))

from services.intelligence_orchestrator import IntelligenceOrchestrator
from storage.db import DatabaseManager

st.set_page_config(
    page_title="INDPlus | Intelligence Controller",
    page_icon="💎",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .status-card { padding: 20px; background-color: white; border-radius: 12px; border: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

st.title("💎 INDPlus Strategic Intelligence Controller")
st.caption("Backend Management Console | 7-Layer Intelligence Model v2.5")

# Sidebar Configuration
st.sidebar.header("🕹️ Control Panel")
fee_options = st.sidebar.multiselect(
    "Financial Education Targets",
    ["exit_load", "brokerage_fee"],
    default=["exit_load", "brokerage_fee"]
)
days_window = st.sidebar.slider("Rolling Window (Days)", 7, 360, 30)
max_reviews = st.sidebar.number_input("Max Review Capacity", 100, 5000, 300)

if st.sidebar.button("🚀 TRIGGER EXECUTIVE PULSE"):
    with st.status("Initializing Strategic Synthesis...", expanded=True) as status:
        st.write("🔍 Layer 1-3: Ingesting & Deduplicating Reviews...")
        orchestrator = IntelligenceOrchestrator()
        
        st.write("🧠 Layer 4-5: LLM Theme Extraction & Synthesis...")
        report_id = orchestrator.run_pipeline(
            fee_types=",".join(fee_options),
            max_reviews=max_reviews,
            days=days_window
        )
        
        st.write("📄 Layer 6-7: Generating Elite PDF & Education Sync...")
        status.update(label=f"✅ Pulse Generated! Report ID: {report_id}", state="complete")
        st.balloons()
        st.success(f"Pulse successfully synchronized across Email, PDF, and Google Workspace.")

# Main Dashboard
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Recent Strategic Pulses")
    db = DatabaseManager()
    with db._get_connection() as conn:
        import pandas as pd
        df = pd.read_sql_query("SELECT id, review_count, ingested_at FROM reports ORDER BY id DESC LIMIT 5", conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No pulses generated yet. Trigger your first report from the sidebar.")

with col2:
    st.subheader("🏢 Stakeholder Archives")
    st.markdown("""
        <div class="status-card">
            <p><b>Strategic Google Doc</b></p>
            <a href="https://docs.google.com/document/d/18CMQaITOJK02gX2BfQwL1Rkw4QWC6sJDMjim865-bOk" target="_blank">
                <button style="width:100%; padding:10px; background:#0066CC; color:white; border:none; border-radius:5px; cursor:pointer;">
                    View Live Strategic Note
                </button>
            </a>
            <p style="font-size:10px; color:#64748b; margin-top:10px;">
                Standalone sync active: Document reflects latest report only.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🛠️ System Health")
    st.write(f"**Database:** `data/pulse_production.db`")
    st.write(f"**Storage Dir:** `data/reports/`")
    st.write(f"**Environment:** Production-Candidate")

st.info("💡 **Expert Tip:** Your Next.js frontend on Vercel will automatically reflect the data stored in this controller's database.")
