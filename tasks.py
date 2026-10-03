from crewai import Task

def create_analysis_task(agent, file_path: str, user_query: str = ""):
    query_context = f" User Specific Focus/Question: '{user_query}'" if user_query else ""
    
    return Task(
        description=(
            f"Analyze the dataset located at '{file_path}'.{query_context}\n"
            "Use the 'profile_csv_dataset' tool to execute statistical profiling.\n"
            "Identify key metrics, missing values, column distribution patterns, top correlations, and potential anomalies."
        ),
        expected_output=(
            "A structured markdown summary containing numerical statistics, data quality insights, "
            "correlations, and key analytical takeaways."
        ),
        agent=agent
    )

def create_report_task(agent, context_tasks: list):
    return Task(
        description=(
            "Synthesize the statistical findings from the quantitative analysis into a polished, executive-ready BI report.\n"
            "Generate actionable recommendations based on data insights.\n"
            "Finally, call the 'create_pdf_report' tool to compile and export the final report into a PDF file."
        ),
        expected_output=(
            "An executive intelligence report written in clear Markdown, formatted with strategic insights, "
            "bulleted takeaways, and confirmation that the PDF report has been generated."
        ),
        agent=agent,
        context=context_tasks
    )
