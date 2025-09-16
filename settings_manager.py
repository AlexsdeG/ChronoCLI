import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ParsingSettings:
    """Settings for data parsing configuration."""
    date_format: str = "%d.%m.%y"
    column_names: Dict[str, str] = None
    location_mappings: Dict[str, str] = None
    time_separators: list = None
    month_headers: list = None
    
    def __post_init__(self):
        """Initialize default values if not provided."""
        if self.column_names is None:
            self.column_names = {
                "date": "Datum",
                "hours": "Stunden", 
                "location": "Ort",
                "info": "Info"
            }
        
        if self.location_mappings is None:
            self.location_mappings = {
                "C": "Company",
                "H": "Homeoffice",
                "B": "Business Trip",
                "T": "Training"
            }
        
        if self.time_separators is None:
            self.time_separators = ["-", "–", "—"]
        
        if self.month_headers is None:
            self.month_headers = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December",
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
                "Januar", "Februar", "März", "April", "Mai", "Juni",
                "Juli", "August", "September", "Oktober", "November", "Dezember"
            ]


@dataclass
class ExportSettings:
    """Settings for HTML export configuration."""
    template_file: str = "default"
    include_raw_data: bool = True
    include_charts: bool = False
    chart_library: str = "chart.js"
    css_theme: str = "default"
    output_filename: str = "report.html"


@dataclass
class UISettings:
    """Settings for user interface configuration."""
    menu_style: str = "ascii_border"
    show_help_text: bool = True
    clear_screen: bool = True
    pause_after_action: bool = True
    max_display_entries: int = 50


@dataclass
class FileSettings:
    """Settings for file handling configuration."""
    supported_formats: list = None
    encoding: str = "utf-8"
    backup_on_save: bool = True
    max_file_size_mb: int = 10
    
    def __post_init__(self):
        """Initialize default values if not provided."""
        if self.supported_formats is None:
            self.supported_formats = [".csv", ".xlsx", ".xls", ".txt", ".json"]


@dataclass
class AppConfig:
    """Main application configuration."""
    parsing: ParsingSettings = None
    export: ExportSettings = None
    ui: UISettings = None
    files: FileSettings = None
    version: str = "2.0.0"
    
    def __post_init__(self):
        """Initialize default settings if not provided."""
        if self.parsing is None:
            self.parsing = ParsingSettings()
        if self.export is None:
            self.export = ExportSettings()
        if self.ui is None:
            self.ui = UISettings()
        if self.files is None:
            self.files = FileSettings()


class SettingsManager:
    """Manages application configuration loading and saving."""
    
    def __init__(self, config_dir: str = None):
        """Initialize settings manager."""
        if config_dir is None:
            # Use ChronoCLI directory as config location
            self.config_dir = Path(__file__).parent
        else:
            self.config_dir = Path(config_dir)
        
        self.config_file = self.config_dir / "config.json"
        
        # Create config file if it doesn't exist
        if not self.config_file.exists():
            self._create_default_config()
        
        self.config = self.load_config()
    
    def _create_default_config(self):
        """Create a default configuration file."""
        try:
            # Create default config
            default_config = AppConfig()
            config_data = asdict(default_config)
            
            # Ensure config directory exists
            self.config_dir.mkdir(exist_ok=True)
            
            # Save to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Created default configuration file: {self.config_file}")
            
        except Exception as e:
            print(f"Warning: Could not create default config file: {e}")
            print("Using default configuration in memory.")
    
    def load_config(self) -> AppConfig:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Convert dict to AppConfig
                return AppConfig(
                    parsing=ParsingSettings(**config_data.get('parsing', {})),
                    export=ExportSettings(**config_data.get('export', {})),
                    ui=UISettings(**config_data.get('ui', {})),
                    files=FileSettings(**config_data.get('files', {})),
                    version=config_data.get('version', '2.0.0')
                )
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                print("Using default configuration.")
        
        # Return default configuration
        return AppConfig()
    
    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            # Convert AppConfig to dict
            config_data = asdict(self.config)
            
            # Ensure config directory exists
            self.config_dir.mkdir(exist_ok=True)
            
            # Save to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_config(self) -> AppConfig:
        """Get current configuration."""
        return self.config
    
    def update_config(self, **kwargs) -> bool:
        """Update configuration with new values."""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                else:
                    print(f"Warning: Unknown config key: {key}")
            
            return self.save_config()
        except Exception as e:
            print(f"Error updating config: {e}")
            return False
    
    def update_parsing_settings(self, **kwargs) -> bool:
        """Update parsing settings."""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.parsing, key):
                    setattr(self.config.parsing, key, value)
                else:
                    print(f"Warning: Unknown parsing setting: {key}")
            
            return self.save_config()
        except Exception as e:
            print(f"Error updating parsing settings: {e}")
            return False
    
    def update_export_settings(self, **kwargs) -> bool:
        """Update export settings."""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.export, key):
                    setattr(self.config.export, key, value)
                else:
                    print(f"Warning: Unknown export setting: {key}")
            
            return self.save_config()
        except Exception as e:
            print(f"Error updating export settings: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values."""
        try:
            self.config = AppConfig()
            return self.save_config()
        except Exception as e:
            print(f"Error resetting config: {e}")
            return False
    
    def show_current_settings(self) -> None:
        """Display current configuration in a readable format."""
        print("📋 Current Configuration")
        print("=" * 50)
        
        print(f"🔧 Version: {self.config.version}")
        print()
        
        print("📝 Parsing Settings:")
        print(f"   Date Format: {self.config.parsing.date_format}")
        print(f"   Column Names: {self.config.parsing.column_names}")
        print(f"   Location Mappings: {self.config.parsing.location_mappings}")
        print(f"   Time Separators: {self.config.parsing.time_separators}")
        print()
        
        print("📄 Export Settings:")
        print(f"   Template: {self.config.export.template_file}")
        print(f"   Include Raw Data: {self.config.export.include_raw_data}")
        print(f"   Include Charts: {self.config.export.include_charts}")
        print(f"   CSS Theme: {self.config.export.css_theme}")
        print()
        
        print("🖥️ UI Settings:")
        print(f"   Menu Style: {self.config.ui.menu_style}")
        print(f"   Clear Screen: {self.config.ui.clear_screen}")
        print(f"   Pause After Action: {self.config.ui.pause_after_action}")
        print()
        
        print("📁 File Settings:")
        print(f"   Supported Formats: {self.config.files.supported_formats}")
        print(f"   Encoding: {self.config.files.encoding}")
        print(f"   Backup on Save: {self.config.files.backup_on_save}")
        print()
        
        print(f"📁 Config File: {self.config_file}")
        print("=" * 50)
    
    def get_sample_config_content(self) -> str:
        """Get sample configuration content for documentation."""
        sample_config = AppConfig()
        config_dict = asdict(sample_config)
        
        return json.dumps(config_dict, indent=2, ensure_ascii=False)
    
    def create_sample_config_file(self, filename: str = "config.sample.json") -> bool:
        """Create a sample configuration file."""
        try:
            sample_file = self.config_dir / filename
            with open(sample_file, 'w', encoding='utf-8') as f:
                f.write(self.get_sample_config_content())
            
            print(f"✅ Sample config created: {sample_file}")
            return True
        except Exception as e:
            print(f"Error creating sample config: {e}")
            return False