import unittest
import tempfile
import os
from datetime import datetime, timedelta
import sys
import io

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exporter import HTMLExporter
from calculator import OverallSummary, MonthlySummary
from data_parser import TimeEntry


class TestHTMLExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = HTMLExporter()
        
        # Create sample data for testing
        self.sample_entries = [
            TimeEntry(
                start_time=datetime(2025, 6, 30, 9, 0),
                end_time=datetime(2025, 6, 30, 12, 0),
                duration=timedelta(hours=3),
                location="Company",
                description="Besprechung Projekt Struktur"
            ),
            TimeEntry(
                start_time=datetime(2025, 6, 30, 13, 0),
                end_time=datetime(2025, 6, 30, 17, 0),
                duration=timedelta(hours=4),
                location="Company",
                description="WooCommerce Struktur besprochen"
            )
        ]
        
        self.overall_summary = OverallSummary(
            total_hours=7.0,
            total_minutes=420,
            total_days=1,
            average_hours_per_month=7.0,
            average_hours_per_week=7.0,
            total_months=1,
            total_weeks=1,
            company_hours=7.0,
            homeoffice_hours=0.0
        )
        
        self.monthly_summaries = [
            MonthlySummary(
                year=2025,
                month=6,
                total_hours=7.0,
                total_minutes=420,
                entry_count=2,
                company_hours=7.0,
                homeoffice_hours=0.0
            )
        ]
    
    def test_export_to_html_basic_structure(self):
        """Test basic HTML structure generation"""
        html = self.exporter.export_to_html(
            self.sample_entries, 
            self.overall_summary, 
            self.monthly_summaries
        )
        
        # Check that it's valid HTML
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('<html lang="en">', html)
        self.assertIn('<head>', html)
        self.assertIn('<body>', html)
        self.assertIn('</html>', html)
        
        # Check for title
        self.assertIn('ChronoCLI - Time Tracking Report', html)
        
        # Check for CSS styles
        self.assertIn('<style>', html)
        self.assertIn('</style>', html)
    
    def test_export_to_html_content(self):
        """Test HTML content generation"""
        html = self.exporter.export_to_html(
            self.sample_entries, 
            self.overall_summary, 
            self.monthly_summaries
        )
        
        # Check for overall summary
        self.assertIn('Overall Summary', html)
        self.assertIn('7.0h', html)
        self.assertIn('Total Hours', html)
        
        # Check for monthly breakdown
        self.assertIn('Monthly Breakdown', html)
        self.assertIn('June 2025', html)
        
        # Check for detailed entries
        self.assertIn('Detailed Monthly Data', html)
        self.assertIn('2025-06-30', html)
        self.assertIn('Besprechung Projekt Struktur', html)
        
        # Check for location styling
        self.assertIn('location-company', html)
    
    def test_export_to_html_empty_data(self):
        """Test HTML export with empty data"""
        empty_summary = OverallSummary(0, 0, 0, 0, 0, 0, 0, 0, 0)
        empty_monthly = []
        empty_entries = []
        
        html = self.exporter.export_to_html(
            empty_entries, 
            empty_summary, 
            empty_monthly
        )
        
        # Should still generate valid HTML
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('ChronoCLI - Time Tracking Report', html)
        self.assertIn('Total entries: 0', html)
    
    def test_save_html_report(self):
        """Test saving HTML report to file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as temp_file:
            temp_filename = temp_file.name
        
        try:
            # Save the report
            saved_filename = self.exporter.save_html_report(
                self.sample_entries,
                self.overall_summary,
                self.monthly_summaries,
                temp_filename
            )
            
            # Check that file was created
            self.assertTrue(os.path.exists(saved_filename))
            
            # Check file content
            with open(saved_filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.assertIn('ChronoCLI - Time Tracking Report', content)
            self.assertIn('7.0h', content)
            
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_save_html_report_default_filename(self):
        """Test saving HTML report with default filename"""
        # Test with default filename
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                saved_filename = self.exporter.save_html_report(
                    self.sample_entries,
                    self.overall_summary,
                    self.monthly_summaries
                )
                
                self.assertEqual(saved_filename, "report.html")
                self.assertTrue(os.path.exists(saved_filename))
                
            finally:
                os.chdir(original_cwd)
    
    def test_save_html_report_custom_filename(self):
        """Test saving HTML report with custom filename"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                custom_filename = "my_time_report.html"
                saved_filename = self.exporter.save_html_report(
                    self.sample_entries,
                    self.overall_summary,
                    self.monthly_summaries,
                    custom_filename
                )
                
                self.assertEqual(saved_filename, custom_filename)
                self.assertTrue(os.path.exists(saved_filename))
                
            finally:
                os.chdir(original_cwd)
    
    def test_save_html_report_adds_extension(self):
        """Test that .html extension is added if missing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                filename_without_extension = "my_report"
                saved_filename = self.exporter.save_html_report(
                    self.sample_entries,
                    self.overall_summary,
                    self.monthly_summaries,
                    filename_without_extension
                )
                
                self.assertEqual(saved_filename, "my_report.html")
                self.assertTrue(os.path.exists(saved_filename))
                
            finally:
                os.chdir(original_cwd)


if __name__ == '__main__':
    unittest.main()