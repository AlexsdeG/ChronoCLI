# ChronoCLI - Personal Time Tracker

⏰ A powerful command-line tool for tracking and analyzing work hours with support for German date formats and flexible data input methods.

## 🎯 Phase 1: Core Functionality & MVP

This is the first phase of the ChronoCLI project, focusing on core functionality and minimum viable product features.

## ✨ Features

### 📝 Data Input & Parsing
- **Flexible German Date Parsing**: Supports various formats like `30.6.25`, `13.9`, `01.07.2025`
- **Time Range Parsing**: Handles formats like `9:00 - 12:00`, `13:00-17:00`
- **Smart Data Structure**: Automatically detects dates, time ranges, locations, and descriptions
- **Month Header Support**: Ignores month headers like "July", "August", "Sept"
- **Location Mapping**: Maps `C` to "Company" and `H` to "Homeoffice"

### 🧮 Calculation Engine
- **Total Hours Calculation**: Sums all work hours across entries
- **Monthly Summaries**: Groups entries by month with detailed statistics
- **Averages**: Calculates average hours per week and per month
- **Location Breakdown**: Separate tracking for company and homeoffice hours

### 🖥️ User Interface
- **Interactive Console Menu**: Built with `console-menu` for intuitive navigation
- **Data Loading**: Paste data directly into the console
- **Statistics View**: Browse overall and monthly statistics
- **Raw Data View**: Display all parsed entries in table format

### 📄 HTML Export
- **Professional Reports**: Generate styled HTML reports with CSS
- **Comprehensive Statistics**: Include all calculations and breakdowns
- **Detailed Entries**: Show individual time entries with descriptions
- **Responsive Design**: Reports look good on all devices

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Setup
1. Navigate to the ChronoCLI directory:
   ```bash
   cd ChronoCLI
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Usage

### Running the Application
```bash
python main.py
```

### Main Menu Options
1. **Load Data from String**: Paste your time tracking data
2. **View Statistics**: Access detailed statistics and breakdowns
3. **Export HTML Report**: Generate a professional HTML report
4. **Exit**: Close the application

### Data Format

The tool accepts data in the following format:

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
mit Nicklas DB Struktur analysiert und Produkt kreierung
21:30-22:30
H
Recherche APF mit Woocommerce
Variation Skus oder APF mit Php/Python Field to Sku translater
1.07
9:00 - 12:00
C
iMac update
Terminal und SFTP Client einrichten
```

### Key Features of Data Format
- **Date**: Set once per day (e.g., `30.6.25`, `13.9`, `01.07.2025`)
- **Time Range**: Working hours (e.g., `9:00 - 12:00`, `13:00-17:00`)
- **Location**: `C` for Company, `H` for Homeoffice
- **Description**: What you did during that time
- **Month Headers**: Optional (e.g., "July", "August")

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python tests/run_tests.py

# Run specific test modules
python -m unittest tests.test_data_parser
python -m unittest tests.test_calculator
python -m unittest tests.test_exporter
```

### Test Coverage
The test suite covers:
- **Data Parser**: Date parsing, time range parsing, input validation
- **Calculator**: Time calculations, monthly summaries, overall statistics
- **Exporter**: HTML generation, file saving, content validation

## 📁 Project Structure

```
ChronoCLI/
├── main.py                 # Application entry point
├── data_parser.py          # Data parsing logic
├── calculator.py           # Time calculation engine
├── ui.py                   # User interface
├── exporter.py             # HTML report generation
├── requirements.txt        # Project dependencies
├── tests/                  # Test suite
│   ├── run_tests.py        # Test runner
│   ├── test_data_parser.py # Data parser tests
│   ├── test_calculator.py  # Calculator tests
│   └── test_exporter.py    # Exporter tests
└── README.md              # This file
```

## 🛠️ Dependencies

- **pandas**: Data manipulation and analysis
- **python-dateutil**: Flexible date/time parsing
- **console-menu**: Interactive console menu interface

## 📊 Example Output

### Console Statistics
```
📊 Overall Summary
========================================
📈 Total Hours: 15.5h (930 minutes)
📅 Days Worked: 3
📊 Total Months: 1
📊 Total Weeks: 1
📈 Average Hours per Month: 15.5h
📈 Average Hours per Week: 15.5h

🏢 Location Breakdown:
   Company: 12.5h
   Homeoffice: 3.0h
```

### HTML Report Features
- Professional styling with CSS
- Responsive design for all devices
- Comprehensive statistics display
- Monthly breakdown tables
- Detailed entry listings
- Location-based color coding

## 🔮 Future Phases

This is Phase 1 of the ChronoCLI project. Future phases will include:

### Phase 2: Enhanced Flexibility & Configuration
- Settings management with `config.json`
- CSV and Excel file support
- Data merging and deduplication
- Configurable column mappings

### Phase 3: Profiles & Data Persistence
- Multiple profile support
- Data persistence between sessions
- Goal tracking and overtime calculation
- Profile management interface

### Phase 4: Security & Final Polish
- Data encryption with password protection
- Enhanced HTML reports with charts
- Robust error handling
- Comprehensive documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **console-menu**: For providing the excellent CLI menu interface
- **pandas**: For powerful data manipulation capabilities
- **python-dateutil**: For flexible date parsing

---

**Built with ❤️ for time tracking enthusiasts**