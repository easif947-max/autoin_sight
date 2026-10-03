import pandas as pd
import json
import os
from crewai.tools import tool
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

@tool("CSV Data Profiler")
def profile_csv_dataset(file_path: str) -> str:
    """Profiles a CSV file to return record counts, missing values, and column summaries."""
    try:
        df = pd.read_csv(file_path)
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        summary = {
            "overview": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "duplicate_rows": int(df.duplicated().sum()),
                "numeric_columns_count": len(num_cols)
            },
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_summary": df[num_cols].describe().to_dict() if num_cols else {}
        }
        return json.dumps(summary, default=str)
    except Exception as e:
        return f"Error profiling dataset: {str(e)}"

@tool("PDF Report Generator")
def create_pdf_report(report_text: str, output_path: str = "reports/AutoInsight_Executive_Report.pdf") -> str:
    """Generates a styled PDF report from text content."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        story = []
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, spaceAfter=12)
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14)
        
        story.append(Paragraph("AutoInsight AI - Executive Brief", title_style))
        story.append(Spacer(1, 12))
        
        for line in report_text.split('\n'):
            if line.strip():
                clean_line = line.replace('*', '').replace('#', '')
                story.append(Paragraph(clean_line, body_style))
                story.append(Spacer(1, 6))
                
        doc.build(story)
        return f"PDF generated successfully at {output_path}"
    except Exception as e:
        return f"Error generating PDF: {str(e)}"
