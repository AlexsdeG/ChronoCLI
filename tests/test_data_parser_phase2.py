import unittest
import tempfile
import csv
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_parser import DataParser, TimeEntry
from settings_manager import SettingsManager
from datetime import datetime, timedelta


class TestDataParserPhase2(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.settings_manager = SettingsManager(self.temp_dir)
        self.parser = DataParser(self.settings_manager)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_parser_uses_settings(self):
        """Test that parser uses settings from settings manager."""
        config = self.parser.config
        self.assertEqual(config.parsing.date_format, "%d.%m.%y")
        self.assertIn("C", config.parsing.location_mappings)
        self.assertIn("H", config.parsing.location_mappings)
        self.assertIn("-", config.parsing.time_separators)
    
    def test_custom_location_mappings(self):
        """Test parser with custom location mappings."""
        # Update settings with custom mappings
        self.settings_manager.update_parsing_settings(
            location_mappings={"W": "Work", "H": "Home", "O": "Office"}
        )
        
        # Create new parser with updated settings
        parser = DataParser(self.settings_manager)
        
        # Test data with custom location codes
        test_data = """
30.6.25
9:00 - 12:00
W
Morning work
13:00 - 17:00
O
Afternoon work
"""
        
        entries = parser.parse_input(test_data)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].location, "Work")
        self.assertEqual(entries[1].location, "Office")
    
    def test_custom_time_separators(self):
        """Test parser with custom time separators."""
        # Update settings with custom separators
        self.settings_manager.update_parsing_settings(
            time_separators=["|", "/", "–"]
        )
        
        # Create new parser with updated settings
        parser = DataParser(self.settings_manager)
        
        # Test data with custom separators
        test_data = """
30.6.25
9:00 | 12:00
C
Morning work
13:00 / 17:00
C
Afternoon work
"""
        
        entries = parser.parse_input(test_data)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].duration, timedelta(hours=3))
        self.assertEqual(entries[1].duration, timedelta(hours=4))
    
    def test_load_from_csv_file(self):
        """Test loading data from CSV file."""
        # Create a test CSV file
        csv_file = Path(self.temp_dir) / "test_data.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Datum', 'Stunden', 'Ort', 'Info'])
            writer.writerow(['30.6.25', '9:00 - 12:00', 'C', 'Morning work'])
            writer.writerow(['30.6.25', '13:00 - 17:00', 'C', 'Afternoon work'])
            writer.writerow(['1.7.25', '9:00 - 12:00', 'H', 'Home office'])
        
        # Load from CSV
        entries = self.parser.load_from_file(str(csv_file))
        
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0].location, "Company")
        self.assertEqual(entries[1].location, "Company")
        self.assertEqual(entries[2].location, "Homeoffice")
    
    def test_load_from_csv_with_different_columns(self):
        """Test loading CSV with different column names."""
        # Create a test CSV file with different column names
        csv_file = Path(self.temp_dir) / "test_data.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Time', 'Location', 'Description'])
            writer.writerow(['30.6.25', '9:00 - 12:00', 'C', 'Morning work'])
            writer.writerow(['1.7.25', '13:00 - 17:00', 'H', 'Afternoon work'])
        
        # Load from CSV
        entries = self.parser.load_from_file(str(csv_file))
        
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].location, "Company")
        self.assertEqual(entries[1].location, "Homeoffice")
    
    def test_load_from_text_file(self):
        """Test loading data from text file."""
        # Create a test text file
        text_file = Path(self.temp_dir) / "test_data.txt"
        
        test_data = """
30.6.25
9:00 - 12:00
C
Morning work
13:00 - 17:00
C
Afternoon work
1.7.25
9:00 - 12:00
H
Home office
"""
        
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(test_data)
        
        # Load from text file
        entries = self.parser.load_from_file(str(text_file))
        
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0].location, "Company")
        self.assertEqual(entries[1].location, "Company")
        self.assertEqual(entries[2].location, "Homeoffice")
    
    def test_load_from_nonexistent_file(self):
        """Test loading from non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.parser.load_from_file("nonexistent_file.csv")
    
    def test_load_from_unsupported_format(self):
        """Test loading from unsupported file format."""
        # Create a test file with unsupported extension
        unsupported_file = Path(self.temp_dir) / "test_data.xyz"
        unsupported_file.write_text("some content")
        
        with self.assertRaises(ValueError) as context:
            self.parser.load_from_file(str(unsupported_file))
        
        self.assertIn("Unsupported file format", str(context.exception))
    
    def test_file_size_limit(self):
        """Test file size limit enforcement."""
        # Update settings with small file size limit
        self.settings_manager.update_config(
            files={'max_file_size_mb': 0.001}  # 1KB limit
        )
        
        # Create new parser with updated settings
        parser = DataParser(self.settings_manager)
        
        # Create a large test file
        large_file = Path(self.temp_dir) / "large_file.csv"
        with open(large_file, 'w') as f:
            f.write("x" * 2000)  # 2KB file
        
        with self.assertRaises(ValueError) as context:
            parser.load_from_file(str(large_file))
        
        self.assertIn("File too large", str(context.exception))
    
    def test_find_column_mapping(self):
        """Test column mapping functionality."""
        # Test exact match
        columns = ['Date', 'Time', 'Location', 'Description']
        mapped = self.parser._find_column_mapping(columns, ['date'])
        self.assertEqual(mapped, 'Date')
        
        # Test case insensitive match
        columns = ['datum', 'stunden', 'ort', 'info']
        mapped = self.parser._find_column_mapping(columns, ['date'])
        self.assertEqual(mapped, 'datum')
        
        # Test partial match
        columns = ['Start Date', 'End Time', 'Work Location', 'Notes']
        mapped = self.parser._find_column_mapping(columns, ['date'])
        self.assertEqual(mapped, 'Start Date')
        
        # Test fallback
        columns = ['Column1', 'Column2', 'Column3']
        mapped = self.parser._find_column_mapping(columns, ['date'])
        self.assertEqual(mapped, 'Column1')
    
    def test_fallback_date_parsing(self):
        """Test fallback date parsing without dateutil."""
        # Temporarily disable dateutil
        original_dateutil = self.parser.settings_manager.config.parsing.date_format
        
        # Test various date formats
        test_cases = [
            ("30.06.2025", datetime(2025, 6, 30)),
            ("30.6.25", datetime(2025, 6, 30)),
            ("13.9", datetime(2025, 9, 13)),
        ]
        
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                result = self.parser._parse_date_fallback(date_str)
                self.assertEqual(result.date(), expected.date())
    
    def test_fallback_time_parsing(self):
        """Test fallback time parsing without dateutil."""
        default_date = datetime(2025, 6, 30)
        
        test_cases = [
            ("9:00", datetime(2025, 6, 30, 9, 0)),
            ("13:30", datetime(2025, 6, 30, 13, 30)),
            ("23:59", datetime(2025, 6, 30, 23, 59)),
        ]
        
        for time_str, expected in test_cases:
            with self.subTest(time_str=time_str):
                result = self.parser._parse_time_fallback(time_str, default_date)
                self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()