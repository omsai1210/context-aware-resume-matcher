import streamlit as st
import requests
import json
import os
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
from datetime import datetime

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(
    page_title="GraphRAG-ATS Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for modern look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .skill-tag {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        margin: 5px;
        font-size: 0.9em;
        font-weight: 500;
    }
    .exact-match { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .multihop-match { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
    .missing-match { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; 
        white-space: pre-wrap; 
        background-color: #f0f2f6; 
        border-radius: 10px 10px 0 0; 
        padding: 0 30px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] { background-color: #ffffff; font-weight: bold; border-top: 3px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

# --- App Navigation ---
tab1, tab2, tab3 = st.tabs([
    "🚀 Unified Dashboard", 
    "🔗 Graph Training Loop", 
    "📊 EdTech Analytics"
])

# --- TAB 1: 🚀 Unified Dashboard ---
with tab1:
    st.title("🚀 Unified Recruitment Dashboard")
    st.markdown("### Upload one or multiple resumes to begin analysis")
    
    # 1. Upload Section
    with st.expander("📂 Ingestion Console", expanded=True):
        batch_files = st.file_uploader("Upload Resumes (PDF/DOCX)", accept_multiple_files=True, type=["pdf", "docx"], key="bulk_upload")
        batch_job_id = st.text_input("Target Job ID / Competency", placeholder="e.g. Senior-Dev-2024", key="bulk_job")
        bulk_process_btn = st.button("⚡ Start Multi-Threaded Analysis", type="primary", use_container_width=True)

    if bulk_process_btn and batch_files and batch_job_id:
        with st.spinner(f"Processing {len(batch_files)} candidates..."):
            try:
                files = [("files", (f.name, f.getvalue())) for f in batch_files]
                resp = requests.post(f"{API_BASE_URL}/bulk-process", params={"job_id": batch_job_id}, files=files)
                if resp.status_code == 200:
                    st.success("Analysis complete!")
                else:
                    st.error(f"Error: {resp.text}")
            except Exception as e:
                st.error(f"Backend Error: {e}")

    # 2. Results & Leaderboard
    st.divider()
    try:
        results_resp = requests.get(f"{API_BASE_URL}/admin/batch-results")
        if results_resp.status_code == 200:
            raw_data = results_resp.json()
            if raw_data:
                df = pd.DataFrame(raw_data)
                
                # Metrics
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total", len(df))
                m2.metric("Shortlisted", len(df[df['match_score'] >= 80]))
                m3.metric("Rejected", len(df[df['match_score'] < 80]))
                m4.metric("Emails Sent", len(df[df['email_sent_status'] == True]))

                # Main Table
                st.markdown("#### 🏆 Live Leaderboard")
                def highlight_status(row):
                    return ['background-color: #d4edda' if row.get('match_score', 0) >= 80 else 'background-color: #f8d7da'] * len(row)
                
                if 'candidate_name' in df.columns:
                    df_display = df[['candidate_name', 'match_score', 'status', 'email_sent_status']].sort_values(by='match_score', ascending=False)
                    st.dataframe(df_display.style.apply(highlight_status, axis=1), use_container_width=True)
                else:
                    st.info("No candidates processed yet.")

                # Action Buttons
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("🚀 Dispatch Batch Emails", use_container_width=True):
                        with st.spinner("Dispatching..."):
                            requests.post(f"{API_BASE_URL}/admin/dispatch-bulk")
                            st.rerun()
                
                # 3. CANDIDATE INSPECTOR
                st.divider()
                st.markdown("### 🔎 Deep Candidate Inspector")
                
                candidate_list = df['candidate_name'].tolist() if 'candidate_name' in df.columns else []
                selected_candidate = st.selectbox("Select a candidate to view their Knowledge Graph and LLM Feedback:", candidate_list)
                
                if selected_candidate:
                    candidate_row = df[df['candidate_name'] == selected_candidate].iloc[0]
                    
                    if 'match_details' in candidate_row and candidate_row['match_details']:
                        detail = candidate_row['match_details']
                        
                        # Graph Rendering
                        net = Network(height="400px", width="100%", bgcolor="#ffffff", font_color="black")
                        net.add_node("Candidate", label="Candidate", color="#2c3e50", size=30)
                        net.add_node("Job", label="Job Role", color="#e67e22", size=30)
                        
                        for s in detail.get('exact_matches', []):
                            net.add_node(s, label=s, color="#27ae60")
                            net.add_edge("Candidate", s)
                            net.add_edge("Job", s)
                        for s in detail.get('multi_hop_matches', []):
                            net.add_node(s, label=s, color="#2980b9")
                            net.add_edge("Candidate", s, dashes=True)
                            net.add_edge("Job", s)
                        for s in detail.get('missing_skills', []):
                            net.add_node(s, label=s, color="#c0392b")
                            net.add_edge("Job", s)

                        net.save_graph("temp_inspector.html")
                        with open("temp_inspector.html", 'r', encoding='utf-8') as f:
                            components.html(f.read(), height=450)
                        
                        # Feedback
                        st.markdown("#### 💬 Glass Box reasoning")
                        st.info(candidate_row['llm_feedback'])
                    else:
                        st.warning("No detailed match data found for this candidate. Please re-run the process.")
            else:
                st.info("Upload resumes to generate the recruitment leaderboard.")
    except Exception as e:
        st.error(f"Dashboard Error: {e}")

# --- TAB 3: 🔗 Graph Training Loop ---
with tab3:
    st.title("🔗 Neuro-Symbolic Evolution")
    st.markdown("### Continuous Knowledge Graph Learning")
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.markdown("#### 🔍 Discovered Semantic Gaps")
        if st.button("Fetch Unmapped Skills"):
            try:
                resp = requests.get(f"{API_BASE_URL}/admin/unmapped-skills")
                if resp.status_code == 200:
                    st.session_state['unmapped'] = resp.json()
                    if not st.session_state['unmapped']:
                        st.info("No unmapped skills found yet!")
                else:
                    st.error("Failed to fetch skills.")
            except Exception as e:
                st.error(f"Error: {e}")
        
        if 'unmapped' in st.session_state and st.session_state['unmapped']:
            selected_skill = st.selectbox("Select An Unknown Skill to Teach the System:", st.session_state['unmapped'])
            st.info(f"The system encountered **{selected_skill}** but cannot find a verified mapping in the ESCO taxonomy.")
        else:
            selected_skill = None
            
    with col_b:
        st.markdown("#### 🧠 Update Knowledge Logic")
        with st.form("kg_training"):
            skill_to_map = selected_skill if selected_skill else ""
            st.text_input("Skill to Map", value=skill_to_map, disabled=True)
            parent_node = st.text_input("Parent Skill / Category", placeholder="e.g. Web Development")
            evolve_btn = st.form_submit_button("Evolve Knowledge Graph")
            
            if evolve_btn and skill_to_map and parent_node:
                try:
                    update_resp = requests.post(
                        f"{API_BASE_URL}/admin/update-graph", 
                        json={"new_skill": skill_to_map, "parent_skill": parent_node}
                    )
                    if update_resp.status_code == 200:
                        st.success(f"System logic expanded: '{skill_to_map}' is now linked to '{parent_node}'.")
                    else:
                        st.error(f"Graph update failed: {update_resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

# --- TAB 3: 📊 EdTech Analytics ---
with tab3:
    st.title("📊 EdTech Skill Gap Analytics")
    st.markdown("### Longitudinal Insights into Candidate Rejections")
    
    try:
        analytics_resp = requests.get(f"{API_BASE_URL}/analytics/export")
        if analytics_resp.status_code == 200:
            with open("temp_analytics_tab.csv", "wb") as f:
                f.write(analytics_resp.content)
            
            df_analytics = pd.read_csv("temp_analytics_tab.csv")
            
            # Download Section
            st.markdown("#### 📥 Export Rejection Data")
            st.download_button(
                label="Download Rejected Candidates CSV",
                data=analytics_resp.content,
                file_name="rejected_candidate_skill_gaps.csv",
                mime="text/csv"
            )
            
            # Visualization
            st.divider()
            st.markdown("#### 📉 Top 10 Most Frequent Skill Gaps")
            if "Missing_Skills" in df_analytics.columns:
                all_missing = ",".join(df_analytics["Missing_Skills"].dropna()).split(",")
                all_missing = [s.strip() for s in all_missing if s.strip()]
                if all_missing:
                    gap_data = pd.Series(all_missing).value_counts().head(10)
                    st.bar_chart(gap_data)
                else:
                    st.info("No missing skills recorded yet.")
        else:
            st.warning("No analytics data found. Rejected candidates will appear here.")
    except Exception as e:
        st.error(f"Analytics Service Error: {e}")

# Footer
st.markdown("---")
st.markdown("🚀 Built with GraphRAG-ATS Engine | © 2026 Recruitment Intelligence Suite")
