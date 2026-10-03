import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import time

from database import init_db, register_user, authenticate_user, save_analysis_history, get_user_history
from crew import AutoInsightCrew

st.set_page_config(page_title="AutoInsight AI", page_icon="📊", layout="wide")

init_db()

st.sidebar.title("🤖 AutoInsight AI")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "current_analysis" not in st.session_state:
    st.session_state.current_analysis = None

if not st.session_state.authenticated:
    auth_mode = st.sidebar.radio("Choose Action", ["Login", "Sign Up"])
    email_input = st.sidebar.text_input("Email")
    password_input = st.sidebar.text_input("Password", type="password")

    if auth_mode == "Sign Up" and st.sidebar.button("Register", use_container_width=True):
        if register_user(email_input, password_input):
            st.sidebar.success("Registered! Please Log In.")
        else:
            st.sidebar.error("Email already exists.")

    elif auth_mode == "Login" and st.sidebar.button("Sign In", use_container_width=True):
        if authenticate_user(email_input, password_input):
            st.session_state.authenticated = True
            st.session_state.user_email = email_input.strip().lower()
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials.")

    st.title("AutoInsight AI")
    st.info("Please log in using the sidebar to begin.")

else:
    st.sidebar.write(f"User: `{st.session_state.user_email}`")
    if st.sidebar.button("Sign Out", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    tab1, tab2 = st.tabs(["🚀 New Analysis", "📜 Saved History"])

    with tab1:
        st.subheader("1. Upload CSV")
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

        if uploaded_file:
            os.makedirs("temp", exist_ok=True)
            temp_path = os.path.join("temp", uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            df = pd.read_csv(temp_path)
            st.dataframe(df.head(5), use_container_width=True)

            user_query = st.text_input("Business Question (Optional)")

            if st.button("Run Multi-Agent Analysis", type="primary", use_container_width=True):
                if not os.environ.get("GROQ_API_KEY") and "GROQ_API_KEY" in st.secrets:
                    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

                with st.spinner("Agents analyzing dataset..."):
                    crew_runner = AutoInsightCrew(file_path=temp_path, user_query=user_query)
                    results = crew_runner.run()

                    save_analysis_history(
                        user_email=st.session_state.user_email,
                        file_name=uploaded_file.name,
                        data_summary=results["data_summary"],
                        executive_report=results["executive_report"]
                    )
                    st.session_state.current_analysis = results
                    st.success("Analysis Complete!")
                    st.rerun()

        if st.session_state.current_analysis:
            st.markdown("---")
            st.subheader("Executive Brief")
            st.markdown(st.session_state.current_analysis["executive_report"])

            pdf_path = st.session_state.current_analysis.get("pdf_path")
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button("📄 Download PDF Report", f, file_name="Report.pdf", mime="application/pdf")

    with tab2:
        st.subheader("Saved Analyses")
        records = get_user_history(st.session_state.user_email)
        for r in records:
            with st.expander(f"{r['file_name']} - {r['created_at']}"):
                st.markdown(r["executive_report"])
