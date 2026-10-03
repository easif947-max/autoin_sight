import os
from crewai import Crew, Process
from agents import create_manager_agent, create_analyst_agent, create_reporter_agent
from tasks import create_analysis_task, create_report_task

class AutoInsightCrew:
    def __init__(self, file_path: str, user_query: str = ""):
        self.file_path = file_path
        self.user_query = user_query

    def run(self):
        # Instantiate agents
        manager = create_manager_agent()
        analyst = create_analyst_agent()
        reporter = create_reporter_agent()

        # Instantiate tasks
        analysis_task = create_analysis_task(analyst, self.file_path, self.user_query)
        report_task = create_report_task(reporter, [analysis_task])

        # Instantiate Crew
        crew = Crew(
            agents=[manager, analyst, reporter],
            tasks=[analysis_task, report_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()

        # Extract output cleanly
        data_summary = analysis_task.output.raw if hasattr(analysis_task, 'output') and analysis_task.output else ""
        executive_report = str(result)

        return {
            "data_summary": data_summary,
            "executive_report": executive_report,
            "pdf_path": "reports/AutoInsight_Executive_Report.pdf"
        }
