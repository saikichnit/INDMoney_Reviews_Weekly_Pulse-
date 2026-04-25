import streamlit as st
import os
import sys
import traceback
import json

# Standard Path setup
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE2_DIR = os.path.join(ROOT_DIR, "phase2")

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if PHASE2_DIR not in sys.path:
    sys.path.insert(0, PHASE2_DIR)

st.set_page_config(page_title="INDPlus Controller", page_icon="💎", layout="wide")

st.title("💎 INDPlus Strategic Intelligence Controller")
st.caption("Backend Management Console | Diagnostic Boot v3.0")

# Diagnostic Import Area
try:
    from phase2.services.intelligence_orchestrator import IntelligenceOrchestrator
    from phase2.storage.db import DatabaseManager
    
    # If we get here, the system is healthy
    st.sidebar.success("✅ System Core Loaded")
    
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
            
            if report_id:
                st.write("📄 Layer 6-7: Generating Elite PDF & Education Sync...")
                status.update(label=f"✅ Pulse Generated! Report ID: {report_id}", state="complete")
                st.balloons()
                st.success(f"Pulse successfully synchronized across Email, PDF, and Google Workspace.")
            else:
                st.error("Pipeline finished with no results. Check logs for details.")

    # Main Dashboard
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Recent Strategic Pulses")
        db = DatabaseManager()
        try:
            with db._get_connection() as conn:
                import pandas as pd
                df = pd.read_sql_query("SELECT id, review_count, created_at FROM reports ORDER BY id DESC LIMIT 5", conn)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No pulses generated yet. Trigger your first report from the sidebar.")
        except Exception as db_err:
            st.warning(f"Database initialized. Awaiting first pulse data...")

    with col2:
        st.subheader("🏢 Stakeholder Archives")
        st.info("Live Strategic Doc sync is active. Updates will appear in your Google Doc after each pulse.")

except Exception as e:
    st.error("🚨 CRITICAL BOOT ERROR DETECTED")
    st.info("The Safe Bootloader caught a crash during module initialization. See details below:")
    st.code(traceback.format_exc())
    
    st.warning("ENGINEER NOTE: This usually indicates a missing dependency or a pathing collision in the cloud environment.")
