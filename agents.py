import os
from crewai import Agent, LLM
from tools import profile_csv_dataset, create_pdf_report

def get_llm():
    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key:
        raise ValueError("GROQ_API_KEY is missing! Set it in Streamlit Secrets.")
    
    # Ensure environment variable is explicitly set for LiteLLM
    os.environ["GROQ_API_KEY"] = groq_key

    # Use the official production Groq model identifier in CrewAI
    return LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=groq_key
    )

def create_manager_agent():
    return Agent(
        role="Data Strategy Director",
        goal="Parse dataset metrics, evaluate user questions, and guide the analytical direction.",
        backstory="An experienced AI Data Architect who coordinates analytics workflows.",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False
    )

def create_analyst_agent():
    return Agent(
        role="Lead Quantitative Data Analyst",
        goal="Execute statistical data profiling and identify key trends and outliers.",
        backstory="A meticulous Data Scientist who works strictly with factual metrics.",
        tools=[profile_csv_dataset],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False
    )

def create_reporter_agent():
    return Agent(
        role="Chief Business Intelligence Officer",
        goal="Synthesize raw statistical findings into executive summaries and PDF reports.",
        backstory="An executive consultant skilled at translating raw data into clear business insights.",
        tools=[create_pdf_report],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False
    )
