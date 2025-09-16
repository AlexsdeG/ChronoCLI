from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
import re
from dateutil.parser import parse as date_parse
from dateutil.relativedelta import relativedelta


@dataclass
class TimeEntry:
    start_time: datetime
    end_time: datetime
    duration: timedelta
    location: str
    description: str


class DataParser:
    def __init__(self):
        self.location_mappings = {
            'C': 'Company',
            'H': 'Homeoffice'
        }
    
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
            
            # Parse with dateutil for flexibility
            parsed_date = date_parse(date_str, dayfirst=True, yearfirst=False)
            return parsed_date
        except Exception as e:
            raise ValueError(f"Could not parse date '{date_str}': {e}")
    
    def parse_time_range(self, time_str: str, current_date: datetime) -> tuple[datetime, datetime]:
        """Parse time range like '9:00 - 12:00' and return start and end datetime."""
        try:
            # Handle various time formats
            time_str = time_str.strip()
            
            # Split by dash or other separators
            if '-' in time_str:
                parts = [p.strip() for p in time_str.split('-')]
            elif '–' in time_str:  # en dash
                parts = [p.strip() for p in time_str.split('–')]
            else:
                raise ValueError(f"Invalid time range format: {time_str}")
            
            if len(parts) != 2:
                raise ValueError(f"Time range must have exactly two parts: {time_str}")
            
            # Parse start and end times
            start_time_str = parts[0]
            end_time_str = parts[1]
            
            # Parse times
            start_time = date_parse(start_time_str, default=current_date)
            end_time = date_parse(end_time_str, default=current_date)
            
            # Handle cases where end time is earlier than start time (next day)
            if end_time <= start_time:
                end_time += timedelta(days=1)
            
            return start_time, end_time
        except Exception as e:
            raise ValueError(f"Could not parse time range '{time_str}': {e}")
    
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
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December',
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
            'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
            'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
        ]
        return line.strip() in month_names
    
    def _is_date_line(self, line: str) -> bool:
        """Check if line contains a date."""
        # Pattern for dates like dd.mm, dd.mm.yy, dd.mm.yyyy
        date_pattern = r'^\d{1,2}\.\d{1,2}(\.\d{2,4})?$'
        return bool(re.match(date_pattern, line.strip()))
    
    def _is_time_range_line(self, line: str) -> bool:
        """Check if line contains a time range."""
        # Pattern for time ranges like 9:00 - 12:00, 13:00-17:00, etc.
        time_pattern = r'\d{1,2}:\d{2}\s*[-–]\s*\d{1,2}:\d{2}'
        return bool(re.search(time_pattern, line.strip()))