import unittest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_parser import DataParser, TimeEntry


class TestDataParser(unittest.TestCase):
    def setUp(self):
        self.parser = DataParser()
    
    def test_parse_german_date_dd_mm_yy(self):
        """Test parsing German date format dd.mm.yy"""
        result = self.parser.parse_german_date("30.6.25")
        expected = datetime(2025, 6, 30)
        self.assertEqual(result.date(), expected.date())
    
    def test_parse_german_date_dd_mm(self):
        """Test parsing German date format dd.mm"""
        result = self.parser.parse_german_date("13.9")
        expected_year = datetime.now().year
        expected = datetime(expected_year, 9, 13)
        self.assertEqual(result.date(), expected.date())
    
    def test_parse_german_date_dd_mm_yyyy(self):
        """Test parsing German date format dd.mm.yyyy"""
        result = self.parser.parse_german_date("01.07.2025")
        expected = datetime(2025, 7, 1)
        self.assertEqual(result.date(), expected.date())
    
    def test_parse_time_range_simple(self):
        """Test parsing simple time range"""
        current_date = datetime(2025, 6, 30)
        start, end = self.parser.parse_time_range("9:00 - 12:00", current_date)
        
        expected_start = datetime(2025, 6, 30, 9, 0)
        expected_end = datetime(2025, 6, 30, 12, 0)
        
        self.assertEqual(start, expected_start)
        self.assertEqual(end, expected_end)
    
    def test_parse_time_range_different_separators(self):
        """Test parsing time range with different separators"""
        current_date = datetime(2025, 6, 30)
        start, end = self.parser.parse_time_range("13:00-17:00", current_date)
        
        expected_start = datetime(2025, 6, 30, 13, 0)
        expected_end = datetime(2025, 6, 30, 17, 0)
        
        self.assertEqual(start, expected_start)
        self.assertEqual(end, expected_end)
    
    def test_parse_time_range_overnight(self):
        """Test parsing time range that goes overnight"""
        current_date = datetime(2025, 6, 30)
        start, end = self.parser.parse_time_range("21:30 - 22:30", current_date)
        
        expected_start = datetime(2025, 6, 30, 21, 30)
        expected_end = datetime(2025, 6, 30, 22, 30)
        
        self.assertEqual(start, expected_start)
        self.assertEqual(end, expected_end)
    
    def test_parse_input_basic(self):
        """Test parsing basic input data"""
        test_data = """
30.6.25
9:00 - 12:00
C
Besprechung Projekt Struktur
13:00 - 17:00
C
WooCommerce Struktur besprochen
"""
        
        entries = self.parser.parse_input(test_data)
        self.assertEqual(len(entries), 2)
        
        # Check first entry
        first_entry = entries[0]
        self.assertEqual(first_entry.location, "Company")
        self.assertEqual(first_entry.description, "Besprechung Projekt Struktur")
        self.assertEqual(first_entry.duration, timedelta(hours=3))
        
        # Check second entry
        second_entry = entries[1]
        self.assertEqual(second_entry.location, "Company")
        self.assertEqual(second_entry.description, "WooCommerce Struktur besprochen")
        self.assertEqual(second_entry.duration, timedelta(hours=4))
    
    def test_parse_input_with_month_header(self):
        """Test parsing input with month header"""
        test_data = """
July
30.6.25
9:00 - 12:00
C
Besprechung Projekt Struktur
"""
        
        entries = self.parser.parse_input(test_data)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].location, "Company")
    
    def test_parse_input_with_homeoffice(self):
        """Test parsing input with homeoffice entries"""
        test_data = """
30.6.25
21:30-22:30
H
Recherche APF mit Woocommerce
"""
        
        entries = self.parser.parse_input(test_data)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].location, "Homeoffice")
        self.assertEqual(entries[0].duration, timedelta(hours=1))
    
    def test_is_month_header(self):
        """Test month header detection"""
        self.assertTrue(self.parser._is_month_header("July"))
        self.assertTrue(self.parser._is_month_header("August"))
        self.assertTrue(self.parser._is_month_header("Sept"))
        self.assertFalse(self.parser._is_month_header("30.6.25"))
        self.assertFalse(self.parser._is_month_header("9:00 - 12:00"))
    
    def test_is_date_line(self):
        """Test date line detection"""
        self.assertTrue(self.parser._is_date_line("30.6.25"))
        self.assertTrue(self.parser._is_date_line("13.9"))
        self.assertTrue(self.parser._is_date_line("01.07.2025"))
        self.assertFalse(self.parser._is_date_line("July"))
        self.assertFalse(self.parser._is_date_line("9:00 - 12:00"))
    
    def test_is_time_range_line(self):
        """Test time range line detection"""
        self.assertTrue(self.parser._is_time_range_line("9:00 - 12:00"))
        self.assertTrue(self.parser._is_time_range_line("13:00-17:00"))
        self.assertTrue(self.parser._is_time_range_line("21:30-22:30"))
        self.assertFalse(self.parser._is_time_range_line("30.6.25"))
        self.assertFalse(self.parser._is_time_range_line("C"))
        self.assertFalse(self.parser._is_time_range_line("Besprechung"))


if __name__ == '__main__':
    unittest.main()