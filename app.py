import sys
import os

# Fix import paths for Streamlit Cloud execution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import time

from database import init_db, register_user, authenticate_user, save_analysis_history, get_user_history
from crew import AutoInsightCrew

# Page Configuration
st.set_page_config(
    page_title="AutoInsight AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database Schema
init_db()

# Sidebar Navigation & Authentication
st.sidebar.title("🤖 AutoInsight AI")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "current_analysis" not in st.session_state:
    st.session_state.current_analysis = None

if not st.session_state.authenticated:
    st.sidebar.subheader("Authentication")
    auth_mode = st.sidebar.radio("Choose Action", ["Login", "Sign Up"])
    
    email_input = st.sidebar.text_input("Email Address")
    password_input = st.sidebar.text_input("Password", type="password")

    if auth_mode == "Sign Up":
        if st.sidebar.button("Register Account", use_container_width=True):
            if email_input and password_input:
                if register_user(email_input, password_input):
                    st.sidebar.success("Account created! Please log in.")
                else:
                    st.sidebar.error("Email already registered.")
            else:
                st.sidebar.warning("Please fill out all fields.")

    elif auth_mode == "Login":
        if st.sidebar.button("Sign In", use_container_width=True):
            if authenticate_user(email_input, password_input):
                st.session_state.authenticated = True
                st.session_state.user_email = email_input.strip().lower()
                st.rerun()
            else:
                st.sidebar.error("Invalid email or password.")

    st.title("AutoInsight AI")
    st.markdown("### Autonomous Multi-Agent Data Analytics Platform")
    st.info("👈 Please **Sign In** or **Register** using the sidebar to begin analyzing your datasets.")

else:
    # Authenticated View
    st.sidebar.markdown(f"**Logged in as:** `{st.session_state.user_email}`")
    if st.sidebar.button("Sign Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_email = ""
        st.session_state.current_analysis = None
        st.rerun()

    st.title("AutoInsight AI Analytics Hub")
    st.markdown("Transform raw datasets into actionable executive intelligence.")

    tab_analytics, tab_history = st.tabs(["🚀 New Analysis", "📜 Saved History"])

    # TAB 1: CSV Upload & Pipeline
    with tab_analytics:
        st.subheader("1. Upload CSV Dataset")
        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

        if uploaded_file is not None:
            os.makedirs("temp", exist_ok=True)
            temp_path = os.path.join("temp", uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            df_preview = pd.read_csv(temp_path)
            st.markdown(f"**Loaded File:** `{uploaded_file.name}` | **Rows:** {df_preview.shape[0]:,} | **Columns:** {df_preview.shape[1]}")

            with st.expander("🔍 Preview Raw Dataset", expanded=False):
                st.dataframe(df_preview.head(5), use_container_width=True)

            st.subheader("2. Analytical Focus")
            user_query = st.text_input(
                "Optional Business Question",
                placeholder="e.g., Identify main revenue drivers and outlier trends."
            )

            if st.button("▶ Run Multi-Agent Analysis Pipeline", type="primary", use_container_width=True):
                # Ensure GROQ_API_KEY is synced from Streamlit secrets into environment variables
                if "GROQ_API_KEY" in st.secrets:
                    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

                if not os.environ.get("GROQ_API_KEY"):
                    st.error("⚠️ GROQ_API_KEY is missing! Please set it in Streamlit Cloud under App Settings > Secrets.")
                else:
                    with st.spinner("🤖 Multi-Agent Crew analyzing dataset... Please wait..."):
                        crew_runner = AutoInsightCrew(file_path=temp_path, user_query=user_query)
                        results = crew_runner.run()

                        # Save results to database
                        save_analysis_history(
                            user_email=st.session_state.user_email,
                            file_name=uploaded_file.name,
                            data_summary=results["data_summary"],
                            executive_report=results["executive_report"]
                        )

                        st.session_state.current_analysis = results
                        st.success("✅ Multi-Agent Analysis Complete!")
                        st.rerun()

        # Display Current Analysis Results
        if st.session_state.current_analysis:
            st.markdown("---")
            st.subheader("3. Executive Brief & Findings")

            analysis_data = st.session_state.current_analysis
            report_text = analysis_data.get("executive_report", "")

            st.markdown(report_text)

            # PDF Download Button
            pdf_file_path = analysis_data.get("pdf_path", "reports/AutoInsight_Executive_Report.pdf")
            if os.path.exists(pdf_file_path):
                with open(pdf_file_path, "rb") as pdf_file:
                    st.download_button(
                        label="📄 Download Executive PDF Report",
                        data=pdf_file,
                        file_name=f"AutoInsight_Report_{int(time.time())}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

    # TAB 2: User Analysis History
    with tab_history:
        st.subheader("My Saved Historical Analyses")
        user_records = get_user_history(st.session_state.user_email)

        if not user_records:
            st.info("No saved historical analyses found. Run a new analysis in Tab 1!")
        else:
            for record in user_records:
                with st.expander(f"📁 {record['file_name']} — Analyzed on {record['created_at']}", expanded=False):
                    st.markdown("**Executive Report:**")
                    st.markdown(record["executive_report"])
