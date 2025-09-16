# ChronoCLI - Personal Time Tracker

⏰ A powerful command-line tool for tracking and analyzing work hours with support for German date formats and flexible data input methods.

## 🎯 Phase 2: Enhanced Flexibility & Configuration

This is the second phase of the ChronoCLI project, focusing on enhanced flexibility, configuration management, and file support.

## ✨ Features

### 📝 Advanced Data Input & Parsing
- **Flexible German Date Parsing**: Supports various formats like `30.6.25`, `13.9`, `01.07.2025`
- **Configurable Time Separators**: Customizable separators like `-`, `–`, `|`, `/`
- **Smart Column Mapping**: Automatic detection of CSV/Excel column names
- **Multiple Location Mappings**: Configurable location codes (C, H, B, T, etc.)
- **Month Header Support**: Ignores month headers like "July", "August", "Sept"

### 📁 File Import Support
- **CSV Files**: Automatic column detection and mapping
- **Excel Files**: Support for `.xlsx` and `.xls` formats
- **Text Files**: Same format as string input
- **JSON Files**: Structured data import
- **File Size Limits**: Configurable maximum file size (default: 10MB)
- **Encoding Support**: Configurable text encoding (default: UTF-8)

### ⚙️ Configuration Management
- **Settings System**: JSON-based configuration file
- **Customizable Parsing**: Date formats, column mappings, time separators
- **Export Settings**: HTML report customization options
- **UI Preferences**: Menu styling, screen clearing, pause behavior
- **File Settings**: Supported formats, encoding, size limits
- **Runtime Configuration**: View and modify settings from within the app

### 🔄 Data Merging & Deduplication
- **Smart Merging**: Combine new data with existing entries
- **Duplicate Detection**: Advanced algorithms to identify duplicate entries
- **Time Tolerance**: Configurable time tolerance for duplicate detection
- **Conflict Detection**: Identify potential conflicts before merging
- **Overlap Detection**: Find overlapping time entries
- **Merge Statistics**: Detailed reports on merge operations

### 🖥️ Enhanced User Interface
- **Professional Console Menu**: Built with `console-menu` library
- **Structured Navigation**: Hierarchical menu system with submenus
- **Import Data Submenu**: Separate options for file and string import
- **Settings Management**: View and modify configuration
- **Real-time Status**: Display current data statistics
- **Help System**: Comprehensive help and usage information

### 📄 Advanced HTML Export
- **Professional Reports**: Styled HTML with inline CSS
- **Comprehensive Statistics**: All calculations and breakdowns
- **Detailed Entries**: Show individual time entries with descriptions
- **Responsive Design**: Reports look good on all devices
- **Customizable Output**: Configurable filenames and styling

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
   python3 -m venv venv
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

### Main Menu Structure
```
⏰ ChronoCLI - Personal Time Tracker
Phase 2: Enhanced Flexibility & Configuration

1. 📥 Import Data
2. 📊 Statistics
3. 📄 Export HTML Report
4. ⚙️  Settings
5. 🗑️  Clear All Data
6. 📖 Help
```

### Import Data Submenu
```
📥 Import Data
1. Load from String
2. Load from File
3. Back to Main Menu
```

### Supported File Formats

#### CSV Files
```csv
Datum,Stunden,Ort,Info
30.6.25,9:00 - 12:00,C,Besprechung Projekt Struktur
30.6.25,13:00 - 17:00,C,WooCommerce Struktur besprochen
1.07.25,9:00 - 12:00,H,Homeoffice Arbeit
```

#### Excel Files (.xlsx/.xls)
Same structure as CSV files with automatic column detection.

#### Text Files (.txt/.json)
Same format as string input data.

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
- **Location**: Configurable codes (default: C=Company, H=Homeoffice)
- **Description**: What you did during that time
- **Month Headers**: Optional (e.g., "July", "August")

## ⚙️ Configuration

### Settings File
Configuration is stored in `config.json` in the ChronoCLI directory:

```json
{
  "version": "2.0.0",
  "parsing": {
    "date_format": "%d.%m.%y",
    "column_names": {
      "date": "Datum",
      "hours": "Stunden",
      "location": "Ort",
      "info": "Info"
    },
    "location_mappings": {
      "C": "Company",
      "H": "Homeoffice",
      "B": "Business Trip",
      "T": "Training"
    },
    "time_separators": ["-", "–", "—"],
    "month_headers": [
      "January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December",
      "Jan", "Feb", "Mar", "Apr", "May", "Jun",
      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
      "Januar", "Februar", "März", "April", "Mai", "Juni",
      "Juli", "August", "September", "Oktober", "November", "Dezember"
    ]
  },
  "export": {
    "template_file": "default",
    "include_raw_data": true,
    "include_charts": false,
    "chart_library": "chart.js",
    "css_theme": "default",
    "output_filename": "report.html"
  },
  "ui": {
    "menu_style": "ascii_border",
    "show_help_text": true,
    "clear_screen": true,
    "pause_after_action": true,
    "max_display_entries": 50
  },
  "files": {
    "supported_formats": [".csv", ".xlsx", ".xls", ".txt", ".json"],
    "encoding": "utf-8",
    "backup_on_save": true,
    "max_file_size_mb": 10
  }
}
```

### Customizing Settings

You can customize settings through the application menu:

1. Launch ChronoCLI
2. Select "⚙️ Settings"
3. Choose "View Current Settings" to see current configuration
4. Use "Reset to Defaults" to restore default settings

## 🔄 Data Merging

### Smart Deduplication
The tool automatically detects and removes duplicate entries based on:
- **Time Similarity**: Entries within configurable time tolerance
- **Date Matching**: Same date with similar time ranges
- **Location Consistency**: Same work location
- **Description Similarity**: Comparable task descriptions

### Conflict Detection
Before merging data, the tool checks for:
- **Overlapping Entries**: Time conflicts between existing and new data
- **Potential Duplicates**: Entries that might be duplicates with different descriptions
- **Data Validation**: Ensures all entries have valid time ranges and durations

### Merge Statistics
After each merge operation, you'll see:
- Total entries before and after merge
- Number of new entries added
- Number of duplicates removed
- Any errors or warnings encountered

## 🧪 Testing

### Running Tests
```bash
# Run all tests (Phase 1 + Phase 2)
python tests/run_tests.py

# Run specific test modules
python -m unittest tests.test_data_parser
python -m unittest tests.test_calculator
python -m unittest tests.test_exporter
python -m unittest tests.test_settings_manager
python -m unittest tests.test_data_parser_phase2
python -m unittest tests.test_data_merger
```

### Test Coverage
The test suite covers:

#### Phase 1 Tests
- **Data Parser**: Date parsing, time range parsing, input validation
- **Calculator**: Time calculations, monthly summaries, overall statistics
- **Exporter**: HTML generation, file saving, content validation

#### Phase 2 Tests
- **Settings Manager**: Configuration loading, saving, validation
- **Data Parser (Phase 2)**: File loading, settings integration, CSV/Excel support
- **Data Merger**: Merging logic, duplicate detection, conflict resolution

## 📁 Project Structure

```
ChronoCLI/
├── main.py                 # Application entry point
├── data_parser.py          # Data parsing logic
├── calculator.py           # Time calculation engine
├── ui_enhanced.py          # Enhanced user interface
├── exporter.py             # HTML report generation
├── settings_manager.py     # Configuration management
├── data_merger.py          # Data merging and deduplication
├── requirements.txt        # Dependencies
├── config.json            # Configuration file (auto-generated)
├── demo.py                 # Standard library demo version
├── tests/                  # Test suite
│   ├── run_tests.py        # Test runner
│   ├── test_data_parser.py
│   ├── test_calculator.py
│   ├── test_exporter.py
│   ├── test_settings_manager.py
│   ├── test_data_parser_phase2.py
│   └── test_data_merger.py
└── README.md              # Documentation
```

## 🛠️ Dependencies

- **pandas**: Data manipulation and Excel file support
- **python-dateutil**: Flexible date/time parsing
- **console-menu**: Interactive console menu interface
- **openpyxl**: Excel file support

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

### Merge Results
```
📊 Data Merge Summary
==============================
Entries before merge: 5
Entries after merge: 7
New entries added: 2
Duplicates removed: 0
```

### File Import
```
📁 Load Data from File
==================================================
Supported file formats:
• CSV files (.csv)
• Excel files (.xlsx, .xls)
• Text files (.txt, .json)
--------------------------------------------------
Max file size: 10MB
--------------------------------------------------
Enter file path: /path/to/your/data.csv
✅ Successfully loaded 15 entries!
🔄 Merging with existing data...
📊 Data Merge Summary
==============================
Entries before merge: 5
Entries after merge: 18
New entries added: 13
Duplicates removed: 0
📊 Total hours: 42.5h
```

## 🔮 Future Phases

This is Phase 2 of the ChronoCLI project. Future phases will include:

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
- **openpyxl**: For Excel file support

---

**Built with ❤️ for time tracking enthusiasts**