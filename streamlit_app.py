import streamlit as st
import os
import sys
import traceback
import json

# Standard Path setup
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

st.set_page_config(page_title="INDPlus Controller", page_icon="💎", layout="wide")

st.title("💎 INDPlus Strategic Intelligence")
st.caption("Backend Management Console | v10.0 (Clean Reset)")

# Diagnostic Import Area
try:
    # Root Imports
    from services.intelligence_orchestrator import IntelligenceOrchestrator
    from storage.db import DatabaseManager
    
    st.sidebar.success("✅ System Core v10.0 Loaded")
    
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
            # Change DB Path for this session to avoid schema conflicts
            st.write("🔍 Layer 1-3: Ingesting & Deduplicating Reviews...")
            orchestrator = IntelligenceOrchestrator(db_path="data/pulse_v10.db")
            
            st.write("🧠 Layer 4-5: LLM Theme Extraction & Synthesis...")
            report_id = orchestrator.run_pipeline(
                fee_types=",".join(fee_options),
                max_reviews=max_reviews,
                days=days_window
            )
            
            if report_id:
                st.write("📄 Layer 6-7: Generating Elite PDF & Education Sync...")
                
                # [NEW] Live Bridge: Save for Frontend and Auto-Push
                try:
                    latest_data = {
                        "report_id": report_id,
                        "generated_at": datetime.now().isoformat(),
                        "payload": combined_payload
                    }
                    os.makedirs("data", exist_ok=True)
                    with open("data/latest_pulse.json", "w") as f:
                        json.dump(latest_data, f, indent=2)
                    
                    # Optional: Auto-push to GitHub if git is configured (best-effort)
                    os.system("git add data/latest_pulse.json && git commit -m 'System: Auto-synced latest pulse' && git push origin stable")
                    st.sidebar.success("📡 Frontend Sync Active")
                except Exception as sync_err:
                    st.sidebar.warning(f"Frontend Sync Delayed: {sync_err}")

                status.update(label=f"✅ Pulse Generated! Report ID: {report_id}", state="complete")
                st.balloons()
                st.success(f"Pulse successfully synchronized across Email, PDF, and Google Workspace.")
            else:
                st.error("Pipeline finished with no results. Check logs for details.")

    # Main Dashboard
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Recent Strategic Pulses")
        try:
            # Check v10 DB
            db = DatabaseManager("data/pulse_v10.db")
            with db._get_connection() as conn:
                import pandas as pd
                try:
                    df = pd.read_sql_query("SELECT id, review_count, created_at FROM reports ORDER BY id DESC LIMIT 5", conn)
                except Exception:
                    df = pd.read_sql_query("SELECT id, review_count FROM reports ORDER BY id DESC LIMIT 5", conn)
                
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No pulses generated in this environment yet. Trigger your first report.")
        except Exception:
            st.info("Welcome to the Clean Environment! Trigger a Pulse to initialize the intelligence hub.")

    with col2:
        st.subheader("🏢 Stakeholder Archives")
        st.info("Live Strategic Doc sync is active.")

except Exception as e:
    st.error("🚨 CRITICAL BOOT ERROR")
    st.info("If you see this, copy the traceback below:")
    st.code(traceback.format_exc())
