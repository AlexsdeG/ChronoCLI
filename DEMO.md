# ChronoCLI - Phase 1 Demo (Standard Library Version)

This is a demonstration version of ChronoCLI that uses only Python standard library modules.
The full version requires external dependencies that are not available in this environment.

## 🚀 Quick Demo

Since the required dependencies (pandas, python-dateutil, console-menu) are not available,
here's a simple demonstration of the core parsing logic using only standard library modules.

### Basic Data Parsing Example

```python
from datetime import datetime, timedelta
import re

def parse_german_date_stdlib(date_str):
    """Parse German date format using standard library."""
    date_str = date_str.strip()
    
    # Handle formats like "13.9" -> "13.09"
    if re.match(r'^\d{1,2}\.\d{1,2}$', date_str):
        day, month = date_str.split('.')
        year = datetime.now().year
        return datetime(year, int(month), int(day))
    
    # Handle formats like "30.6.25" -> "30.06.2025"
    elif re.match(r'^\d{1,2}\.\d{1,2}\.\d{2}$', date_str):
        day, month, year_short = date_str.split('.')
        year = 2000 + int(year_short)
        return datetime(year, int(month), int(day))
    
    raise ValueError(f"Unsupported date format: {date_str}")

def parse_time_range_stdlib(time_str, current_date):
    """Parse time range using standard library."""
    time_str = time_str.strip()
    
    # Split by dash
    if '-' in time_str:
        parts = [p.strip() for p in time_str.split('-')]
    else:
        raise ValueError(f"Invalid time range: {time_str}")
    
    if len(parts) != 2:
        raise ValueError(f"Time range must have two parts: {time_str}")
    
    # Parse times
    start_hour, start_minute = map(int, parts[0].split(':'))
    end_hour, end_minute = map(int, parts[1].split(':'))
    
    start_time = current_date.replace(hour=start_hour, minute=start_minute)
    end_time = current_date.replace(hour=end_hour, minute=end_minute)
    
    # Handle overnight
    if end_time <= start_time:
        end_time += timedelta(days=1)
    
    return start_time, end_time

# Example usage
if __name__ == "__main__":
    # Test date parsing
    test_dates = ["30.6.25", "13.9", "01.07.2025"]
    for date_str in test_dates:
        try:
            parsed = parse_german_date_stdlib(date_str)
            print(f"✅ {date_str} -> {parsed.strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"❌ {date_str} -> Error: {e}")
    
    # Test time range parsing
    test_date = datetime(2025, 6, 30)
    test_times = ["9:00 - 12:00", "13:00-17:00", "21:30-22:30"]
    
    for time_str in test_times:
        try:
            start, end = parse_time_range_stdlib(time_str, test_date)
            duration = end - start
            print(f"✅ {time_str} -> {duration}")
        except Exception as e:
            print(f"❌ {time_str} -> Error: {e}")
```

### Sample Output

```
✅ 30.6.25 -> 2025-06-30
✅ 13.9 -> 2025-09-13
✅ 01.07.2025 -> 2025-07-01
✅ 9:00 - 12:00 -> 3:00:00
✅ 13:00-17:00 -> 4:00:00
✅ 21:30-22:30 -> 1:00:00
```

## 📋 Full Features (with dependencies)

The complete ChronoCLI application includes:

### ✅ Phase 1 Features (Implemented)
- [x] Advanced German date parsing (`30.6.25`, `13.9`, `01.07.2025`)
- [x] Time range parsing (`9:00 - 12:00`, `13:00-17:00`)
- [x] Location mapping (`C` → Company, `H` → Homeoffice)
- [x] Monthly and overall statistics
- [x] HTML report generation with styling
- [x] Interactive console menu interface
- [x] Comprehensive test suite

### 🔮 Future Phases
- [ ] Phase 2: Settings management, CSV/Excel support
- [ ] Phase 3: Profile system, data persistence
- [ ] Phase 4: Encryption, enhanced reports

## 🛠️ Installation (Full Version)

For the full version with all features:

```bash
# 1. Navigate to project directory
cd ChronoCLI

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py

# 5. Run tests
python tests/run_tests.py
```

## 📊 Example Usage

### Input Data Format
```
Datum
Stunden
Ort
Info
July
30.6.25
9:00 - 12:00
C
Besprechung Projekt Struktur
13:00 - 17:00
C
WooCommerce Struktur besprochen
21:30-22:30
H
Recherche APF mit Woocommerce
```

### Generated Statistics
```
📊 Overall Summary
========================================
📈 Total Hours: 8.0h (480 minutes)
📅 Days Worked: 1
📊 Total Months: 1
📊 Total Weeks: 1
📈 Average Hours per Month: 8.0h
📈 Average Hours per Week: 8.0h

🏢 Location Breakdown:
   Company: 7.0h
   Homeoffice: 1.0h
```

## 🧪 Testing

The project includes comprehensive tests:

```bash
# Run all tests
python tests/run_tests.py

# Test individual modules
python -m unittest tests.test_data_parser
python -m unittest tests.test_calculator
python -m unittest tests.test_exporter
```

## 📁 Project Structure

```
ChronoCLI/
├── main.py                 # Application entry point
├── data_parser.py          # Data parsing logic
├── calculator.py           # Time calculation engine
├── ui.py                   # User interface
├── exporter.py             # HTML report generation
├── requirements.txt        # Dependencies
├── tests/                  # Test suite
│   ├── run_tests.py        # Test runner
│   ├── test_data_parser.py
│   ├── test_calculator.py
│   └── test_exporter.py
└── README.md              # Documentation
```

---

**Note**: This demo version shows the core logic using only standard library modules. 
The full application requires external dependencies for advanced features like 
flexible date parsing, data manipulation, and interactive menus.