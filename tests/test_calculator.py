import unittest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculator import TimeCalculator, OverallSummary, MonthlySummary
from data_parser import TimeEntry


class TestTimeCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = TimeCalculator()
        
        # Create sample entries for testing
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
            ),
            TimeEntry(
                start_time=datetime(2025, 6, 30, 21, 30),
                end_time=datetime(2025, 6, 30, 22, 30),
                duration=timedelta(hours=1),
                location="Homeoffice",
                description="Recherche APF mit Woocommerce"
            ),
            TimeEntry(
                start_time=datetime(2025, 7, 1, 9, 0),
                end_time=datetime(2025, 7, 1, 12, 0),
                duration=timedelta(hours=3),
                location="Company",
                description="iMac update"
            ),
            TimeEntry(
                start_time=datetime(2025, 7, 1, 13, 0),
                end_time=datetime(2025, 7, 1, 17, 0),
                duration=timedelta(hours=4),
                location="Company",
                description="Analyse ProDir & Ado Pen CSV Datei"
            )
        ]
    
    def test_calculate_total_hours(self):
        """Test total hours calculation"""
        total_hours, total_minutes = self.calculator.calculate_total_hours(self.sample_entries)
        
        # Total should be 3 + 4 + 1 + 3 + 4 = 15 hours
        self.assertEqual(total_hours, 15.0)
        self.assertEqual(total_minutes, 900)  # 15 hours * 60 minutes
    
    def test_calculate_total_hours_empty(self):
        """Test total hours calculation with empty list"""
        total_hours, total_minutes = self.calculator.calculate_total_hours([])
        
        self.assertEqual(total_hours, 0.0)
        self.assertEqual(total_minutes, 0)
    
    def test_calculate_monthly_summary(self):
        """Test monthly summary calculation"""
        summaries = self.calculator.calculate_monthly_summary(self.sample_entries)
        
        # Should have 2 months: June 2025 and July 2025
        self.assertEqual(len(summaries), 2)
        
        # Check June 2025 summary
        june_summary = next(s for s in summaries if s.month == 6 and s.year == 2025)
        self.assertEqual(june_summary.total_hours, 8.0)  # 3 + 4 + 1
        self.assertEqual(june_summary.entry_count, 3)
        self.assertEqual(june_summary.company_hours, 7.0)  # 3 + 4
        self.assertEqual(june_summary.homeoffice_hours, 1.0)
        
        # Check July 2025 summary
        july_summary = next(s for s in summaries if s.month == 7 and s.year == 2025)
        self.assertEqual(july_summary.total_hours, 7.0)  # 3 + 4
        self.assertEqual(july_summary.entry_count, 2)
        self.assertEqual(july_summary.company_hours, 7.0)
        self.assertEqual(july_summary.homeoffice_hours, 0.0)
    
    def test_calculate_monthly_summary_empty(self):
        """Test monthly summary calculation with empty list"""
        summaries = self.calculator.calculate_monthly_summary([])
        self.assertEqual(len(summaries), 0)
    
    def test_calculate_overall_summary(self):
        """Test overall summary calculation"""
        summary = self.calculator.calculate_overall_summary(self.sample_entries)
        
        self.assertEqual(summary.total_hours, 15.0)
        self.assertEqual(summary.total_minutes, 900)
        self.assertEqual(summary.total_days, 2)  # June 30 and July 1
        self.assertEqual(summary.total_months, 2)  # June and July
        self.assertEqual(summary.total_weeks, 1)  # Both dates in same week (assuming)
        self.assertEqual(summary.company_hours, 14.0)  # 3+4+3+4
        self.assertEqual(summary.homeoffice_hours, 1.0)
        
        # Check averages
        self.assertEqual(summary.average_hours_per_month, 7.5)  # 15 / 2
        self.assertEqual(summary.average_hours_per_week, 15.0)  # 15 / 1
    
    def test_calculate_overall_summary_empty(self):
        """Test overall summary calculation with empty list"""
        summary = self.calculator.calculate_overall_summary([])
        
        self.assertEqual(summary.total_hours, 0.0)
        self.assertEqual(summary.total_minutes, 0)
        self.assertEqual(summary.total_days, 0)
        self.assertEqual(summary.total_months, 0)
        self.assertEqual(summary.total_weeks, 0)
        self.assertEqual(summary.company_hours, 0.0)
        self.assertEqual(summary.homeoffice_hours, 0.0)
        self.assertEqual(summary.average_hours_per_month, 0.0)
        self.assertEqual(summary.average_hours_per_week, 0.0)
    
    def test_get_entries_for_month(self):
        """Test getting entries for specific month"""
        june_entries = self.calculator.get_entries_for_month(self.sample_entries, 2025, 6)
        july_entries = self.calculator.get_entries_for_month(self.sample_entries, 2025, 7)
        
        self.assertEqual(len(june_entries), 3)
        self.assertEqual(len(july_entries), 2)
        
        # Check that all entries are for the correct month
        for entry in june_entries:
            self.assertEqual(entry.start_time.month, 6)
        
        for entry in july_entries:
            self.assertEqual(entry.start_time.month, 7)
    
    def test_get_entries_for_month_no_results(self):
        """Test getting entries for month with no data"""
        august_entries = self.calculator.get_entries_for_month(self.sample_entries, 2025, 8)
        self.assertEqual(len(august_entries), 0)
    
    def test_format_duration(self):
        """Test duration formatting"""
        # Test hours and minutes
        duration = timedelta(hours=2, minutes=30)
        formatted = self.calculator.format_duration(duration)
        self.assertEqual(formatted, "2h 30m")
        
        # Test only hours
        duration = timedelta(hours=3)
        formatted = self.calculator.format_duration(duration)
        self.assertEqual(formatted, "3h")
        
        # Test only minutes
        duration = timedelta(minutes=45)
        formatted = self.calculator.format_duration(duration)
        self.assertEqual(formatted, "45m")
    
    def test_format_hours_decimal(self):
        """Test decimal hours formatting"""
        # Test hours with minutes
        formatted = self.calculator.format_hours_decimal(2.5)
        self.assertEqual(formatted, "2h 30m")
        
        # Test whole hours
        formatted = self.calculator.format_hours_decimal(3.0)
        self.assertEqual(formatted, "3h")
        
        # Test zero hours
        formatted = self.calculator.format_hours_decimal(0.0)
        self.assertEqual(formatted, "0h")
    
    def test_format_month_name(self):
        """Test month name formatting"""
        formatted = self.calculator.format_month_name(2025, 6)
        self.assertEqual(formatted, "June 2025")
        
        formatted = self.calculator.format_month_name(2025, 7)
        self.assertEqual(formatted, "July 2025")


if __name__ == '__main__':
    unittest.main()