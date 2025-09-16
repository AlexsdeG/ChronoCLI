from typing import List
from datetime import datetime
from calculator import MonthlySummary, OverallSummary
from data_parser import TimeEntry


class HTMLExporter:
    def __init__(self):
        pass
    
    def export_to_html(self, entries: List[TimeEntry], overall_summary: OverallSummary, 
                      monthly_summaries: List[MonthlySummary]) -> str:
        """Generate HTML report with all statistics."""
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChronoCLI - Time Tracking Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        .summary-card h3 {{
            margin-top: 0;
            border-bottom: none;
            color: #3498db;
        }}
        .summary-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .location-company {{
            color: #27ae60;
            font-weight: bold;
        }}
        .location-homeoffice {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .month-section {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .stats-highlight {{
            background: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .raw-data {{
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⏰ ChronoCLI Time Tracking Report</h1>
        <p style="text-align: center; color: #666;">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>📊 Overall Summary</h2>
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Total Hours</h3>
                <div class="summary-value">{overall_summary.total_hours}h</div>
                <p>({overall_summary.total_minutes} minutes)</p>
            </div>
            <div class="summary-card">
                <h3>Days Worked</h3>
                <div class="summary-value">{overall_summary.total_days}</div>
            </div>
            <div class="summary-card">
                <h3>Avg per Month</h3>
                <div class="summary-value">{overall_summary.average_hours_per_month}h</div>
            </div>
            <div class="summary-card">
                <h3>Avg per Week</h3>
                <div class="summary-value">{overall_summary.average_hours_per_week}h</div>
            </div>
        </div>
        
        <div class="stats-highlight">
            <h3>🏢 Location Breakdown</h3>
            <p><strong>Company:</strong> {overall_summary.company_hours}h</p>
            <p><strong>Homeoffice:</strong> {overall_summary.homeoffice_hours}h</p>
        </div>
        
        <h2>📅 Monthly Breakdown</h2>
        <table>
            <thead>
                <tr>
                    <th>Month</th>
                    <th>Total Hours</th>
                    <th>Entries</th>
                    <th>Company</th>
                    <th>Homeoffice</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for summary in monthly_summaries:
            month_name = datetime(summary.year, summary.month, 1).strftime('%B %Y')
            html_content += f"""
                <tr>
                    <td>{month_name}</td>
                    <td><strong>{summary.total_hours}h</strong></td>
                    <td>{summary.entry_count}</td>
                    <td class="location-company">{summary.company_hours}h</td>
                    <td class="location-homeoffice">{summary.homeoffice_hours}h</td>
                </tr>
"""
        
        html_content += """
            </tbody>
        </table>
        
        <h2>📝 Detailed Monthly Data</h2>
"""
        
        for summary in monthly_summaries:
            month_entries = [entry for entry in entries 
                           if entry.start_time.year == summary.year 
                           and entry.start_time.month == summary.month]
            
            month_name = datetime(summary.year, summary.month, 1).strftime('%B %Y')
            html_content += f"""
        <div class="month-section">
            <h3>{month_name}</h3>
            <div class="stats-highlight">
                <strong>Total:</strong> {summary.total_hours}h | 
                <strong>Company:</strong> {summary.company_hours}h | 
                <strong>Homeoffice:</strong> {summary.homeoffice_hours}h | 
                <strong>Entries:</strong> {summary.entry_count}
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Time</th>
                        <th>Duration</th>
                        <th>Location</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
"""
            
            for entry in sorted(month_entries, key=lambda x: x.start_time):
                date_str = entry.start_time.strftime('%Y-%m-%d')
                time_str = f"{entry.start_time.strftime('%H:%M')} - {entry.end_time.strftime('%H:%M')}"
                duration_str = f"{entry.duration.total_seconds() / 3600:.1f}h"
                location_class = "location-company" if entry.location == "Company" else "location-homeoffice"
                
                html_content += f"""
                    <tr>
                        <td>{date_str}</td>
                        <td>{time_str}</td>
                        <td>{duration_str}</td>
                        <td class="{location_class}">{entry.location}</td>
                        <td>{entry.description}</td>
                    </tr>
"""
            
            html_content += """
                </tbody>
            </table>
        </div>
"""
        
        html_content += f"""
        <div class="footer">
            <p>Report generated by ChronoCLI | Total entries: {len(entries)} | Report time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html_content
    
    def save_html_report(self, entries: List[TimeEntry], overall_summary: OverallSummary, 
                        monthly_summaries: List[MonthlySummary], filename: str = "report.html") -> str:
        """Save HTML report to file and return the filename."""
        html_content = self.export_to_html(entries, overall_summary, monthly_summaries)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename