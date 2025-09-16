import unittest
import tempfile
import json
import os
from pathlib import Path
import sys
import csv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings_manager import SettingsManager, AppConfig, ParsingSettings


class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.settings_manager = SettingsManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_config_creation(self):
        """Test that default configuration is created correctly."""
        config = self.settings_manager.get_config()
        
        self.assertIsInstance(config, AppConfig)
        self.assertIsInstance(config.parsing, ParsingSettings)
        self.assertEqual(config.version, "2.0.0")
        self.assertEqual(config.parsing.date_format, "%d.%m.%y")
        self.assertIn("C", config.parsing.location_mappings)
        self.assertIn("H", config.parsing.location_mappings)
    
    def test_config_file_creation(self):
        """Test that config file is created when settings are saved."""
        config_file = Path(self.temp_dir) / "config.json"
        
        # Initially, config file shouldn't exist
        self.assertFalse(config_file.exists())
        
        # Save config
        result = self.settings_manager.save_config()
        self.assertTrue(result)
        
        # Now config file should exist
        self.assertTrue(config_file.exists())
    
    def test_config_loading(self):
        """Test that configuration is loaded correctly from file."""
        # Save a custom config
        self.settings_manager.update_parsing_settings(
            date_format="%m/%d/%Y",
            location_mappings={"W": "Work", "H": "Home"}
        )
        
        # Create a new settings manager to test loading
        new_settings_manager = SettingsManager(self.temp_dir)
        config = new_settings_manager.get_config()
        
        self.assertEqual(config.parsing.date_format, "%m/%d/%Y")
        self.assertEqual(config.parsing.location_mappings["W"], "Work")
        self.assertEqual(config.parsing.location_mappings["H"], "Home")
    
    def test_update_parsing_settings(self):
        """Test updating parsing settings."""
        result = self.settings_manager.update_parsing_settings(
            date_format="%Y-%m-%d",
            time_separators=["|", "/", "-"]
        )
        
        self.assertTrue(result)
        config = self.settings_manager.get_config()
        self.assertEqual(config.parsing.date_format, "%Y-%m-%d")
        self.assertEqual(config.parsing.time_separators, ["|", "/", "-"])
    
    def test_reset_to_defaults(self):
        """Test resetting settings to defaults."""
        # Modify settings
        self.settings_manager.update_parsing_settings(
            date_format="%m/%d/%Y"
        )
        
        # Reset to defaults
        result = self.settings_manager.reset_to_defaults()
        self.assertTrue(result)
        
        # Check that settings are reset
        config = self.settings_manager.get_config()
        self.assertEqual(config.parsing.date_format, "%d.%m.%y")
    
    def test_show_current_settings(self):
        """Test displaying current settings."""
        # This test just ensures the method doesn't crash
        try:
            self.settings_manager.show_current_settings()
        except Exception as e:
            self.fail(f"show_current_settings() raised an exception: {e}")
    
    def test_get_sample_config_content(self):
        """Test getting sample configuration content."""
        sample_content = self.settings_manager.get_sample_config_content()
        
        self.assertIsInstance(sample_content, str)
        self.assertIn("parsing", sample_content)
        self.assertIn("export", sample_content)
        self.assertIn("ui", sample_content)
        self.assertIn("files", sample_content)
        
        # Should be valid JSON
        try:
            json.loads(sample_content)
        except json.JSONDecodeError:
            self.fail("Sample config content is not valid JSON")
    
    def test_create_sample_config_file(self):
        """Test creating sample configuration file."""
        sample_filename = "test_config.sample.json"
        result = self.settings_manager.create_sample_config_file(sample_filename)
        
        self.assertTrue(result)
        
        # Check that file was created
        sample_file = Path(self.temp_dir) / sample_filename
        self.assertTrue(sample_file.exists())
        
        # Check content
        with open(sample_file, 'r') as f:
            content = f.read()
        
        self.assertIn("parsing", content)
        self.assertIn("export", content)


if __name__ == '__main__':
    unittest.main()