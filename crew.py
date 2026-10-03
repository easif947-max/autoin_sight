import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from typing import Dict, Any
from crewai import Task, Crew, Process
from agents import create_manager_agent, create_analyst_agent, create_reporter_agent
from tools import profile_csv_dataset

class AutoInsightCrew:
    def __init__(self, file_path: str, user_query: str = ""):
        self.file_path = file_path
        self.user_query = user_query if user_query else "Provide a complete statistical analysis."
        
        self.manager = create_manager_agent()
        self.analyst = create_analyst_agent()
        self.reporter = create_reporter_agent()

    def run(self) -> Dict[str, Any]:
        task1 = Task(
            description=f"Profile CSV file at '{self.file_path}'. Answer user request: '{self.user_query}'",
            expected_output="Detailed metrics and analytical summary.",
            agent=self.analyst
        )

        task2 = Task(
            description=f"Review metrics from Analyst. Direct core themes for user request: '{self.user_query}'",
            expected_output="Key business observations and executive outline.",
            agent=self.manager
        )

        task3 = Task(
            description="Create executive report with: 1. Executive Summary, 2. Key Insights, 3. Recommendations. Export PDF using tool.",
            expected_output="Markdown brief and PDF export confirmation.",
            agent=self.reporter
        )

        crew = Crew(
            agents=[self.manager, self.analyst, self.reporter],
            tasks=[task1, task2, task3],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        raw_json = profile_csv_dataset.run(file_path=self.file_path)
        
        try:
            parsed_summary = json.loads(raw_json)
        except Exception:
            parsed_summary = {"raw": raw_json}

        return {
            "status": "completed",
            "data_summary": parsed_summary,
            "executive_report": str(result),
            "pdf_path": "reports/AutoInsight_Executive_Report.pdf"
        }
