from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import re
from pathlib import Path
try:
    from dateutil.parser import parse as date_parse
    from dateutil.relativedelta import relativedelta
    DATEUTIL_AVAILABLE = True
except ImportError:
    DATEUTIL_AVAILABLE = False

from settings_manager import SettingsManager, AppConfig


@dataclass(frozen=True)
class TimeEntry:
    start_time: datetime
    end_time: datetime
    duration: timedelta
    location: str
    description: str


class DataParser:
    def __init__(self, settings_manager: SettingsManager = None):
        self.settings_manager = settings_manager or SettingsManager()
        self.config = self.settings_manager.get_config()
        
        # Use settings from config
        self.location_mappings = self.config.parsing.location_mappings
        self.time_separators = self.config.parsing.time_separators
        self.month_headers = self.config.parsing.month_headers
        self.column_names = self.config.parsing.column_names
    
    def parse_german_date(self, date_str: str) -> datetime:
        """Parse German date format (dd.mm.yy or dd.mm) and return datetime object."""
        try:
            # Handle various German date formats
            date_str = date_str.strip()
            
            # Handle cases like "13.9" instead of "13.09"
            if re.match(r'^\d{1,2}\.\d{1,2}(\.\d{2,4})?$', date_str):
                parts = date_str.split('.')
                if len(parts) == 2:
                    # Format: dd.mm - add current year
                    day, month = parts
                    year = datetime.now().year
                    date_str = f"{day.zfill(2)}.{month.zfill(2)}.{year}"
                elif len(parts) == 3:
                    # Format: dd.mm.yy or dd.mm.yyyy
                    day, month, year = parts
                    if len(year) == 2:
                        year = f"20{year}"
                    date_str = f"{day.zfill(2)}.{month.zfill(2)}.{year}"
            
            # Parse with dateutil if available, otherwise use fallback
            if DATEUTIL_AVAILABLE:
                parsed_date = date_parse(date_str, dayfirst=True, yearfirst=False)
            else:
                # Fallback parsing without dateutil
                parsed_date = self._parse_date_fallback(date_str)
            
            return parsed_date
        except Exception as e:
            raise ValueError(f"Could not parse date '{date_str}': {e}")
    
    def _parse_date_fallback(self, date_str: str) -> datetime:
        """Fallback date parsing when dateutil is not available."""
        # Simple parsing for common formats
        if re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}$', date_str):
            day, month, year = map(int, date_str.split('.'))
            return datetime(year, month, day)
        elif re.match(r'^\d{1,2}\.\d{1,2}\.\d{2}$', date_str):
            day, month, year_short = map(int, date_str.split('.'))
            year = 2000 + year_short
            return datetime(year, month, day)
        elif re.match(r'^\d{1,2}\.\d{1,2}$', date_str):
            day, month = map(int, date_str.split('.'))
            year = datetime.now().year
            return datetime(year, month, day)
        else:
            raise ValueError(f"Unsupported date format: {date_str}")
    
    def parse_time_range(self, time_str: str, current_date: datetime) -> tuple[datetime, datetime]:
        """Parse time range like '9:00 - 12:00' and return start and end datetime."""
        try:
            # Handle various time formats
            time_str = time_str.strip()
            
            # Split by configured separators
            parts = None
            for separator in self.time_separators:
                if separator in time_str:
                    parts = [p.strip() for p in time_str.split(separator)]
                    break
            
            if not parts:
                raise ValueError(f"Invalid time range format: {time_str}")
            
            if len(parts) != 2:
                raise ValueError(f"Time range must have exactly two parts: {time_str}")
            
            # Parse start and end times
            start_time_str = parts[0]
            end_time_str = parts[1]
            
            # Parse times with dateutil if available, otherwise use fallback
            if DATEUTIL_AVAILABLE:
                start_time = date_parse(start_time_str, default=current_date)
                end_time = date_parse(end_time_str, default=current_date)
            else:
                start_time = self._parse_time_fallback(start_time_str, current_date)
                end_time = self._parse_time_fallback(end_time_str, current_date)
            
            # Handle cases where end time is earlier than start time (next day)
            if end_time <= start_time:
                end_time += timedelta(days=1)
            
            return start_time, end_time
        except Exception as e:
            raise ValueError(f"Could not parse time range '{time_str}': {e}")
    
    def _parse_time_fallback(self, time_str: str, default_date: datetime) -> datetime:
        """Fallback time parsing when dateutil is not available."""
        try:
            hour, minute = map(int, time_str.split(':'))
            return default_date.replace(hour=hour, minute=minute)
        except Exception:
            raise ValueError(f"Invalid time format: {time_str}")
    
    def parse_input(self, text_data: str) -> List[TimeEntry]:
        """Parse input text data and return list of TimeEntry objects."""
        entries = []
        lines = text_data.strip().split('\n')
        
        current_date = None
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Skip month headers like "July", "August", "Sept"
            if self._is_month_header(line):
                i += 1
                continue
            
            # Check if line contains a date
            if self._is_date_line(line):
                try:
                    current_date = self.parse_german_date(line)
                    i += 1
                    continue
                except ValueError:
                    # If date parsing fails, treat as regular line
                    pass
            
            # Check if line contains a time range
            if current_date and self._is_time_range_line(line):
                try:
                    start_time, end_time = self.parse_time_range(line, current_date)
                    duration = end_time - start_time
                    
                    # Look ahead for location and description
                    location = "Unknown"
                    description = ""
                    
                    # Check next line for location
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line in self.location_mappings:
                            location = self.location_mappings[next_line]
                            i += 1
                            
                            # Check line after location for description
                            if i + 1 < len(lines):
                                desc_line = lines[i + 1].strip()
                                if desc_line and not self._is_date_line(desc_line) and not self._is_time_range_line(desc_line):
                                    description = desc_line
                                    i += 1
                    
                    entry = TimeEntry(
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                        location=location,
                        description=description
                    )
                    entries.append(entry)
                    
                except ValueError as e:
                    print(f"Warning: Could not parse line '{line}': {e}")
            
            i += 1
        
        return entries
    
    def _is_month_header(self, line: str) -> bool:
        """Check if line is a month header."""
        return line.strip() in self.month_headers
    
    def _is_date_line(self, line: str) -> bool:
        """Check if line contains a date."""
        # Pattern for dates like dd.mm, dd.mm.yy, dd.mm.yyyy
        date_pattern = r'^\d{1,2}\.\d{1,2}(\.\d{2,4})?$'
        return bool(re.match(date_pattern, line.strip()))
    
    def _is_time_range_line(self, line: str) -> bool:
        """Check if line contains a time range."""
        # Pattern for time ranges like 9:00 - 12:00, 13:00-17:00, etc.
        # Use configured time separators
        separator_pattern = '|'.join(re.escape(sep) for sep in self.time_separators)
        time_pattern = rf'\d{{1,2}}:\d{{2}}\s*[{separator_pattern}]\s*\d{{1,2}}:\d{{2}}'
        return bool(re.search(time_pattern, line.strip()))
    
    def load_from_file(self, file_path: str) -> List[TimeEntry]:
        """Load data from file (CSV, Excel, or text file)."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file size
        max_size_bytes = self.config.files.max_file_size_mb * 1024 * 1024
        if file_path.stat().st_size > max_size_bytes:
            raise ValueError(f"File too large. Maximum size: {self.config.files.max_file_size_mb}MB")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.csv':
            return self._load_from_csv(file_path)
        elif file_extension in ['.xlsx', '.xls']:
            return self._load_from_excel(file_path)
        elif file_extension in ['.txt', '.json']:
            return self._load_from_text_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _load_from_csv(self, file_path: Path) -> List[TimeEntry]:
        """Load data from CSV file."""
        try:
            import csv
            entries = []
            
            with open(file_path, 'r', encoding=self.config.files.encoding) as file:
                reader = csv.DictReader(file)
                
                # Find column mappings
                date_column = self._find_column_mapping(reader.fieldnames, ['date', 'datum', 'day'])
                hours_column = self._find_column_mapping(reader.fieldnames, ['hours', 'stunden', 'time', 'duration'])
                location_column = self._find_column_mapping(reader.fieldnames, ['location', 'ort', 'place'])
                info_column = self._find_column_mapping(reader.fieldnames, ['info', 'description', 'notes', 'comment'])
                
                for row in reader:
                    try:
                        # Extract data from row
                        date_str = row.get(date_column, '').strip()
                        hours_str = row.get(hours_column, '').strip()
                        location_str = row.get(location_column, '').strip()
                        description = row.get(info_column, '').strip()
                        
                        if not date_str or not hours_str:
                            continue
                        
                        # Parse date
                        current_date = self.parse_german_date(date_str)
                        
                        # Parse time range
                        start_time, end_time = self.parse_time_range(hours_str, current_date)
                        duration = end_time - start_time
                        
                        # Map location
                        location = self.location_mappings.get(location_str, location_str or "Unknown")
                        
                        entry = TimeEntry(
                            start_time=start_time,
                            end_time=end_time,
                            duration=duration,
                            location=location,
                            description=description
                        )
                        entries.append(entry)
                        
                    except Exception as e:
                        print(f"Warning: Could not parse row {row}: {e}")
                        continue
            
            return entries
            
        except ImportError:
            raise ImportError("CSV support requires the csv module (built-in)")
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")
    
    def _load_from_excel(self, file_path: Path) -> List[TimeEntry]:
        """Load data from Excel file."""
        try:
            import pandas as pd
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Find column mappings
            date_column = self._find_column_mapping(df.columns.tolist(), ['date', 'datum', 'day'])
            hours_column = self._find_column_mapping(df.columns.tolist(), ['hours', 'stunden', 'time', 'duration'])
            location_column = self._find_column_mapping(df.columns.tolist(), ['location', 'ort', 'place'])
            info_column = self._find_column_mapping(df.columns.tolist(), ['info', 'description', 'notes', 'comment'])
            
            entries = []
            
            for _, row in df.iterrows():
                try:
                    # Extract data from row
                    date_str = str(row.get(date_column, '')).strip()
                    hours_str = str(row.get(hours_column, '')).strip()
                    location_str = str(row.get(location_column, '')).strip()
                    description = str(row.get(info_column, '')).strip()
                    
                    if not date_str or not hours_str or date_str == 'nan' or hours_str == 'nan':
                        continue
                    
                    # Parse date
                    current_date = self.parse_german_date(date_str)
                    
                    # Parse time range
                    start_time, end_time = self.parse_time_range(hours_str, current_date)
                    duration = end_time - start_time
                    
                    # Map location
                    location = self.location_mappings.get(location_str, location_str or "Unknown")
                    
                    entry = TimeEntry(
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                        location=location,
                        description=description
                    )
                    entries.append(entry)
                    
                except Exception as e:
                    print(f"Warning: Could not parse row {row.to_dict()}: {e}")
                    continue
            
            return entries
            
        except ImportError:
            raise ImportError("Excel support requires pandas library")
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {e}")
    
    def _load_from_text_file(self, file_path: Path) -> List[TimeEntry]:
        """Load data from text file."""
        try:
            with open(file_path, 'r', encoding=self.config.files.encoding) as file:
                text_data = file.read()
            
            return self.parse_input(text_data)
            
        except Exception as e:
            raise ValueError(f"Error reading text file: {e}")
    
    def _find_column_mapping(self, available_columns: List[str], possible_names: List[str]) -> str:
        """Find the best matching column name."""
        available_lower = [col.lower() for col in available_columns]
        
        for possible_name in possible_names:
            if possible_name.lower() in available_lower:
                index = available_lower.index(possible_name.lower())
                return available_columns[index]
        
        # If no direct match, try partial matches
        for col in available_columns:
            col_lower = col.lower()
            for possible_name in possible_names:
                if possible_name.lower() in col_lower or col_lower in possible_name.lower():
                    return col
        
        # Return first column if no match found
        return available_columns[0] if available_columns else 'unknown'