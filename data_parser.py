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
            
            # Check for month name format (e.g., "01. Jul", "30. June")
            month_names = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
                'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            
            # Pattern for dd. MonthName format
            month_name_pattern = r'^(\d{1,2})\.\s*([A-Za-z]{3,9})$'
            month_match = re.match(month_name_pattern, date_str)
            if month_match:
                day = int(month_match.group(1))
                month_name = month_match.group(2)
                year = datetime.now().year
                
                if month_name in month_names:
                    month = month_names[month_name]
                    return datetime(year, month, day)
                else:
                    raise ValueError(f"Unknown month name: {month_name}")
            
            # Remove spaces for consistent parsing (e.g., "01. Jul" -> "01.Jul")
            date_str = date_str.replace(' ', '')
            
            # Handle cases like "13.9" instead of "13.09"
            if re.match(r'^\d{1,2}\.\d{1,2}(\.\d{2,4})?$', date_str):
                parts = date_str.split('.')
                if len(parts) == 2:
                    # Format: dd.mm - add current year
                    day, month = parts
                    year = datetime.now().year
                    # Ensure day and month are 2 digits
                    day = day.zfill(2)
                    month = month.zfill(2)
                    date_str = f"{day}.{month}.{year}"
                elif len(parts) == 3:
                    # Format: dd.mm.yy or dd.mm.yyyy
                    day, month, year = parts
                    # Ensure day and month are 2 digits
                    day = day.zfill(2)
                    month = month.zfill(2)
                    
                    # Handle year
                    if len(year) == 2:
                        # For 2-digit years, assume 20xx if year is 00-99
                        year = f"20{year}"
                    elif len(year) == 4:
                        # Keep 4-digit year as is
                        pass
                    else:
                        # Invalid year length, use current year
                        year = str(datetime.now().year)
                    
                    date_str = f"{day}.{month}.{year}"
            
            # Parse with dateutil if available, otherwise use fallback
            if DATEUTIL_AVAILABLE:
                # Use explicit format parsing to avoid ambiguity
                try:
                    # Try parsing with dayfirst=True for German format
                    parsed_date = date_parse(date_str, dayfirst=True, yearfirst=False)
                except ValueError:
                    # If that fails, try with explicit format
                    try:
                        parsed_date = datetime.strptime(date_str, '%d.%m.%Y')
                    except ValueError:
                        try:
                            parsed_date = datetime.strptime(date_str, '%d.%m.%y')
                        except ValueError:
                            raise ValueError(f"Could not parse date '{date_str}' with German format")
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
    
    def parse_input_with_separators(self, text_data: str) -> List[TimeEntry]:
        """Parse input text data with flexible column and row separators."""
        entries = []
        
        # Normalize different line endings
        text_data = text_data.replace('\r\n', '\n').replace('\r', '\n')
        
        # Split into rows using various row separators
        rows = self._split_into_rows(text_data)
        
        for row in rows:
            # Split row into columns using various column separators
            columns = self._split_into_columns(row)
            
            if len(columns) >= 2:  # Need at least date and time
                try:
                    entry = self._parse_columns_to_entry(columns)
                    if entry:
                        entries.append(entry)
                except Exception as e:
                    print(f"Warning: Could not parse row '{row}': {e}")
        
        return entries
    
    def _split_into_rows(self, text_data: str) -> List[str]:
        """Split text data into rows using various separators."""
        rows = []
        
        # Normalize different line endings
        text_data = text_data.replace('\r\n', '\n').replace('\r', '\n')
        
        # First split by single newlines to get all lines
        all_lines = [line.strip() for line in text_data.split('\n') if line.strip()]
        
        # Check if this looks like Excel/CSV format with semicolon separators
        # If most lines contain semicolons, treat as CSV-style data
        semicolon_lines = sum(1 for line in all_lines if ';' in line)
        if semicolon_lines > len(all_lines) * 0.5:  # More than 50% have semicolons
            # Treat as CSV-style data, each line is a separate row
            for line in all_lines:
                # Skip month headers
                if self._is_month_header(line):
                    continue
                # Skip lines that start with * (Excel sub-rows) - they'll be handled in Excel parsing
                if line.startswith('*'):
                    continue
                rows.append(line)
            return rows
        
        # Group lines into logical entries (for text-style data)
        current_entry = []
        
        for line in all_lines:
            # Skip month headers
            if self._is_month_header(line):
                continue
            
            # If line contains a date, start new entry
            if self._is_date_line(line):
                if current_entry:
                    # Join with the same separator that was used in the line
                    separator = self._detect_separator(current_entry[0])
                    rows.append(separator.join(current_entry))
                    current_entry = []
                current_entry.append(line)
            # If line contains time range, add to current entry
            elif self._is_time_range_line(line):
                current_entry.append(line)
            # If line is location or description, add to current entry
            elif line in self.location_mappings or len(line) > 3:
                current_entry.append(line)
        
        # Add the last entry if exists
        if current_entry:
            separator = self._detect_separator(current_entry[0]) if current_entry else ', '
            rows.append(separator.join(current_entry))
        
        # Now check for double separators in the rows we created
        final_rows = []
        for row in rows:
            # Check if row contains double comma or double semicolon separators
            if ',,' in row or ';;' in row:
                # Split by double separators
                if ',,' in row and ';;' in row:
                    # Use the one that appears more frequently
                    comma_count = row.count(',,')
                    semicolon_count = row.count(';;')
                    separator = ',,' if comma_count >= semicolon_count else ';;'
                elif ',,' in row:
                    separator = ',,'
                else:
                    separator = ';;'
                
                sub_rows = [r.strip() for r in row.split(separator) if r.strip()]
                final_rows.extend(sub_rows)
            else:
                # Check if this row contains multiple dates (multiple entries)
                # Try different separators to split multiple entries
                for separator in [',', ';']:
                    date_parts = [part.strip() for part in row.split(separator) if self._is_date_line(part.strip())]
                    if len(date_parts) > 1:
                        # Split by this separator to create separate entries
                        parts = [part.strip() for part in row.split(separator)]
                        current_sub_entry = []
                        
                        for part in parts:
                            if self._is_date_line(part):
                                if current_sub_entry:
                                    final_rows.append(', '.join(current_sub_entry))
                                    current_sub_entry = []
                                current_sub_entry.append(part)
                            else:
                                current_sub_entry.append(part)
                        
                        if current_sub_entry:
                            final_rows.append(', '.join(current_sub_entry))
                        break
                else:
                    final_rows.append(row)
        
        return final_rows
    
    def _detect_separator(self, text: str) -> str:
        """Detect the separator used in the text."""
        if ';' in text:
            return '; '
        elif ',' in text:
            return ', '
        else:
            return ', '
    
    def _is_structured_data(self, lines: List[str]) -> bool:
        """Check if lines represent structured data with dates and times."""
        date_count = sum(1 for line in lines if self._is_date_line(line))
        time_count = sum(1 for line in lines if self._is_time_range_line(line))
        
        # Consider structured if we have at least one date and one time
        return date_count > 0 and time_count > 0
    
    def _process_structured_data(self, lines: List[str]) -> List[str]:
        """Process structured data lines into individual entries."""
        entries = []
        current_entry = []
        
        for line in lines:
            # Skip month headers
            if self._is_month_header(line):
                continue
            
            # If line contains a date, start new entry
            if self._is_date_line(line):
                if current_entry:
                    entries.append(' | '.join(current_entry))
                    current_entry = []
                current_entry.append(line)
            # If line contains time range, add to current entry
            elif self._is_time_range_line(line):
                current_entry.append(line)
            # If line is location or description, add to current entry
            elif line in self.location_mappings or len(line) > 3:
                current_entry.append(line)
        
        # Add the last entry if exists
        if current_entry:
            entries.append(' | '.join(current_entry))
        
        return entries
    
    def _split_into_columns(self, row: str) -> List[str]:
        """Split a row into columns using various separators."""
        # Try different separators in order of preference
        separators = [';', '\t', ',']
        
        for separator in separators:
            if separator in row:
                columns = [col.strip() for col in row.split(separator) if col.strip()]
                if len(columns) >= 2:  # Found a good separator
                    return columns
        
        # If no separator found, try to parse as single entry with time range
        if self._is_time_range_line(row):
            return [row.strip()]
        
        # If no separator found and no time range, treat as single column
        return [row.strip()] if row.strip() else []
    
    def _group_lines_into_entries(self, lines: List[str]) -> List[str]:
        """Group consecutive lines into logical entries."""
        entries = []
        current_entry = []
        
        for line in lines:
            # Skip month headers
            if self._is_month_header(line):
                continue
            
            # If line contains a date, start new entry
            if self._is_date_line(line):
                if current_entry:
                    entries.append(' | '.join(current_entry))
                    current_entry = []
                current_entry.append(line)
            # If line contains time range, add to current entry
            elif self._is_time_range_line(line):
                current_entry.append(line)
            # If line is location or description, add to current entry
            elif line in self.location_mappings or len(line) > 3:
                current_entry.append(line)
            # Empty line or separator - finish current entry
            else:
                if current_entry:
                    entries.append(' | '.join(current_entry))
                    current_entry = []
        
        # Add the last entry if exists
        if current_entry:
            entries.append(' | '.join(current_entry))
        
        return entries
    
    def _parse_columns_to_entry(self, columns: List[str]) -> Optional[TimeEntry]:
        """Parse columns into a TimeEntry object."""
        if len(columns) < 2:
            return None
        
        # Try to identify which column contains what
        date_str = None
        time_str = None
        location_str = None
        description = None
        
        for col in columns:
            col = col.strip()
            if not col:
                continue
                
            # Check if it's a date
            if self._is_date_line(col):
                date_str = col
            # Check if it's a time range
            elif self._is_time_range_line(col):
                time_str = col
            # Check if it's a location
            elif col in self.location_mappings:
                location_str = col
            # Otherwise, treat as description
            elif len(col) > 2:
                description = col
        
        if not date_str or not time_str:
            return None
        
        try:
            # Parse date
            current_date = self.parse_german_date(date_str)
            
            # Parse time range
            start_time, end_time = self.parse_time_range(time_str, current_date)
            duration = end_time - start_time
            
            # Map location
            location = self.location_mappings.get(location_str, location_str or "Unknown")
            
            return TimeEntry(
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                location=location,
                description=description or ""
            )
            
        except Exception as e:
            raise ValueError(f"Could not parse entry from columns {columns}: {e}")
    
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
        # Pattern for dates like dd.mm, dd.mm.yy, dd.mm.yyyy, dd. MonthName
        # More strict pattern to avoid false positives
        line = line.strip()
        
        # Pattern 1: dd.mm, dd.mm.yy, dd.mm.yyyy with optional spaces
        date_pattern1 = r'^\d{1,2}\.\s*\d{1,2}(\.\s*\d{2,4})?$'
        
        # Pattern 2: dd. MonthName (e.g., "01. Jul", "30. June")
        month_names = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)'
        date_pattern2 = rf'^\d{{1,2}}\.\s*{month_names}'
        
        if re.match(date_pattern1, line) or re.match(date_pattern2, line):
            # Additional validation for pattern 1
            if re.match(date_pattern1, line):
                # Remove spaces for parsing
                clean_line = line.replace(' ', '')
                parts = clean_line.split('.')
                if len(parts) >= 2:
                    try:
                        day, month = int(parts[0]), int(parts[1])
                        # Validate day and month ranges
                        if 1 <= day <= 31 and 1 <= month <= 12:
                            return True
                    except ValueError:
                        pass
            else:
                # Pattern 2 matched, it's a valid date format
                return True
        return False
    
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
        """Load data from Excel file with enhanced multi-row handling."""
        try:
            import pandas as pd
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Clean the data - remove empty rows and columns
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            # Find column mappings
            date_column = self._find_column_mapping(df.columns.tolist(), ['date', 'datum', 'day'])
            hours_column = self._find_column_mapping(df.columns.tolist(), ['hours', 'stunden', 'time', 'duration'])
            location_column = self._find_column_mapping(df.columns.tolist(), ['location', 'ort', 'place'])
            info_column = self._find_column_mapping(df.columns.tolist(), ['info', 'description', 'notes', 'comment'])
            
            entries = []
            
            # Group rows by date to handle multi-row entries
            current_date = None
            current_description_parts = []
            
            for _, row in df.iterrows():
                try:
                    # Extract data from row - handle datetime objects properly
                    date_val = row.get(date_column, '')
                    hours_val = row.get(hours_column, '')
                    location_val = row.get(location_column, '')
                    description_val = row.get(info_column, '')
                    
                    # Convert to strings, handling datetime objects
                    if pd.isna(date_val):
                        date_str = 'nan'
                    elif hasattr(date_val, 'strftime'):  # datetime object
                        date_str = date_val.strftime('%d.%m.%Y')
                    else:
                        date_str = str(date_val).strip()
                    
                    if pd.isna(hours_val):
                        hours_str = 'nan'
                    elif hasattr(hours_val, 'strftime'):  # datetime object
                        # Extract just the time part if it's a datetime
                        hours_str = hours_val.strftime('%H:%M')
                    else:
                        hours_str = str(hours_val).strip()
                    
                    location_str = str(location_val).strip() if not pd.isna(location_val) else 'nan'
                    description = str(description_val).strip() if not pd.isna(description_val) else 'nan'
                    
                    # Skip completely empty rows
                    if (date_str == 'nan' and hours_str == 'nan' and 
                        location_str == 'nan' and description == 'nan'):
                        continue
                    
                    # Handle date inheritance (sub-rows)
                    if date_str != 'nan' and date_str:
                        # If we have accumulated descriptions, create entry first
                        if current_date and current_description_parts:
                            # This shouldn't happen in normal flow, but handle it
                            pass
                        current_date = date_str
                        current_description_parts = []
                    elif current_date is None:
                        continue  # Skip row without date
                    
                    # Handle time inheritance (sub-rows)
                    if hours_str != 'nan' and hours_str:
                        # Combine all description parts
                        full_description = description if description != 'nan' else ''
                        if current_description_parts:
                            all_descriptions = current_description_parts + ([full_description] if full_description else [])
                            full_description = ' '.join(all_descriptions)
                        
                        # Parse this as a main entry
                        entry = self._create_entry_from_row(
                            current_date, hours_str, location_str, full_description
                        )
                        if entry:
                            entries.append(entry)
                        
                        # Reset description accumulator
                        current_description_parts = []
                    else:
                        # This is a sub-row, accumulate description
                        if description != 'nan' and description:
                            current_description_parts.append(description)
                    
                except Exception as e:
                    print(f"Warning: Could not parse row {row.to_dict()}: {e}")
                    continue
            
            # No remaining entries to add since we process immediately
            
            return entries
            
        except ImportError:
            raise ImportError("Excel support requires pandas library")
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {e}")
    
    def _create_entry_from_row(self, date_str: str, hours_str: str, 
                              location_str: str, description: str) -> Optional[TimeEntry]:
        """Create a TimeEntry from row data."""
        try:
            # Clean up malformed date strings (like '2025-09-1000:00:00')
            if date_str and '00:00:00' in date_str:
                # Extract just the date part before time
                date_str = date_str.split('00:00:00')[0]
                # Remove any trailing non-date characters
                date_str = date_str.rstrip('T -')
            
            # Handle Excel serial dates (numeric values)
            if date_str.replace('.', '').replace('-', '').isdigit():
                try:
                    # Try as Excel serial date first
                    excel_date = float(date_str)
                    # Excel dates are days since 1900-01-01, but 1900 is incorrectly treated as leap year
                    if excel_date > 59:
                        excel_date -= 1  # Adjust for Excel leap year bug
                    current_date = datetime(1899, 12, 30) + timedelta(days=excel_date)
                except (ValueError, TypeError):
                    # If conversion fails, try normal parsing
                    current_date = self.parse_german_date(date_str)
            else:
                # Parse date normally
                current_date = self.parse_german_date(date_str)
            
            # Parse time range
            start_time, end_time = self.parse_time_range(hours_str, current_date)
            duration = end_time - start_time
            
            # Map location
            location = self.location_mappings.get(location_str, location_str or "Unknown")
            
            # Clean description
            if description == 'nan':
                description = ""
            
            return TimeEntry(
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                location=location,
                description=description.strip()
            )
            
        except Exception as e:
            print(f"Warning: Could not create entry from row data: {e}")
            return None
    
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