import os
import sys
from pathlib import Path
from typing import List, Optional
from consolemenu import ConsoleMenu
from consolemenu.items import FunctionItem, SubmenuItem
from consolemenu.format import AsciiBorderStyle
from consolemenu.selection_menu import SelectionMenu

from settings_manager import SettingsManager
from data_parser import DataParser, TimeEntry
from calculator import TimeCalculator, OverallSummary, MonthlySummary
from exporter import HTMLExporter
from data_merger import DataMerger, MergeResult


class ChronoCLIUI:
    def __init__(self):
        self.settings_manager = SettingsManager()
        self.config = self.settings_manager.get_config()
        
        self.parser = DataParser(self.settings_manager)
        self.calculator = TimeCalculator()
        self.exporter = HTMLExporter()
        self.merger = DataMerger()
        
        self.entries: List[TimeEntry] = []
        self.overall_summary: Optional[OverallSummary] = None
        self.monthly_summaries: Optional[List[MonthlySummary]] = None
    
    def clear_screen(self):
        """Clear the console screen."""
        if self.config.ui.clear_screen:
            os.system('cls' if os.name == 'nt' else 'clear')
    
    def pause(self):
        """Pause execution and wait for user input."""
        if self.config.ui.pause_after_action:
            input("\nPress Enter to continue...")
    
    def update_summaries(self):
        """Update overall and monthly summaries."""
        if self.entries:
            self.overall_summary = self.calculator.calculate_overall_summary(self.entries)
            self.monthly_summaries = self.calculator.calculate_monthly_summary(self.entries)
    
    def load_data_from_string(self):
        """Load data from user input string with flexible separators."""
        self.clear_screen()
        print("📝 Load Data from String")
        print("=" * 50)
        print("Paste your time tracking data below.")
        print("Enter an empty line when finished.")
        print("-" * 50)
        print("Supported formats:")
        print("• German dates: 30.6.25, 13.9, 01.07.2025")
        print("• Time ranges: 9:00 - 12:00, 13:00-17:00")
        print("• Locations: C (Company), H (Homeoffice)")
        print("• Column separators: comma (,), semicolon (;), tab")
        print("• Row separators: newline (\\n), double newline (\\n\\n), double comma (,,), double semicolon (;;)")
        print("-" * 50)
        
        lines = []
        while True:
            try:
                line = input()
                if line == "":
                    break
                lines.append(line)
            except EOFError:
                break
        
        if not lines:
            print("❌ No data entered.")
            self.pause()
            return
        
        try:
            text_data = '\n'.join(lines)
            # Use enhanced parsing with flexible separators
            new_entries = self.parser.parse_input_with_separators(text_data)
            
            if not new_entries:
                print("❌ No valid entries found in the data.")
                self.pause()
                return
            
            # Merge with existing entries
            if self.entries:
                print("🔄 Merging with existing data...")
                merge_result = self.merger.merge_entries(self.entries, new_entries)
                self.entries = [entry for entry in self.entries + new_entries 
                              if entry not in self.merger._find_duplicates(self.entries, new_entries)]
                
                print(self.merger.get_merge_summary(merge_result))
            else:
                self.entries = new_entries
                print(f"✅ Successfully loaded {len(new_entries)} entries!")
            
            self.update_summaries()
            print(f"📊 Total hours: {self.overall_summary.total_hours}h")
            self.pause()
            
        except Exception as e:
            print(f"❌ Error parsing data: {e}")
            self.pause()
    
    def load_data_from_file(self):
        """Load data from file."""
        self.clear_screen()
        print("📁 Load Data from File")
        print("=" * 50)
        print("Supported file formats:")
        print("• CSV files (.csv)")
        print("• Excel files (.xlsx, .xls)")
        print("• Text files (.txt, .json)")
        print("-" * 50)
        print(f"Max file size: {self.config.files.max_file_size_mb}MB")
        print("-" * 50)
        
        file_path = input("Enter file path: ").strip()
        
        if not file_path:
            print("❌ No file path provided.")
            self.pause()
            return
        
        try:
            new_entries = self.parser.load_from_file(file_path)
            
            if not new_entries:
                print("❌ No valid entries found in the file.")
                self.pause()
                return
            
            # Check for potential conflicts
            if self.entries:
                conflicts = self.merger.suggest_merge_conflicts(self.entries, new_entries)
                if conflicts:
                    print("⚠️  Potential conflicts detected:")
                    for conflict in conflicts[:3]:  # Show first 3 conflicts
                        print(f"  • {conflict}")
                    if len(conflicts) > 3:
                        print(f"  • ... and {len(conflicts) - 3} more conflicts")
                    
                    if input("\nContinue anyway? (y/N): ").lower() != 'y':
                        print("❌ Import cancelled.")
                        self.pause()
                        return
            
            # Merge with existing entries
            if self.entries:
                print("🔄 Merging with existing data...")
                merge_result = self.merger.merge_entries(self.entries, new_entries)
                self.entries = [entry for entry in self.entries + new_entries 
                              if entry not in self.merger._find_duplicates(self.entries, new_entries)]
                
                print(self.merger.get_merge_summary(merge_result))
            else:
                self.entries = new_entries
                print(f"✅ Successfully loaded {len(new_entries)} entries!")
            
            self.update_summaries()
            print(f"📊 Total hours: {self.overall_summary.total_hours}h")
            self.pause()
            
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            self.pause()
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            self.pause()
    
    def view_current_settings(self):
        """View current configuration settings."""
        self.clear_screen()
        self.settings_manager.show_current_settings()
        self.pause()
    
    def reset_settings_to_defaults(self):
        """Reset settings to default values."""
        self.clear_screen()
        print("🔄 Reset Settings to Defaults")
        print("=" * 50)
        
        if input("Are you sure you want to reset all settings to defaults? (y/N): ").lower() == 'y':
            if self.settings_manager.reset_to_defaults():
                print("✅ Settings reset to defaults successfully!")
                self.config = self.settings_manager.get_config()
                self.parser = DataParser(self.settings_manager)  # Reinitialize parser with new settings
            else:
                print("❌ Failed to reset settings.")
        else:
            print("❌ Settings reset cancelled.")
        
        self.pause()
    
    def view_overall_summary(self):
        """Display overall summary statistics."""
        if not self.overall_summary:
            print("❌ No data loaded. Please load data first.")
            self.pause()
            return
        
        self.clear_screen()
        print("📊 Overall Summary")
        print("=" * 50)
        
        summary = self.overall_summary
        print(f"📈 Total Hours: {summary.total_hours}h ({summary.total_minutes} minutes)")
        print(f"📅 Days Worked: {summary.total_days}")
        print(f"📊 Total Months: {summary.total_months}")
        print(f"📊 Total Weeks: {summary.total_weeks}")
        print(f"📈 Average Hours per Month: {summary.average_hours_per_month}h")
        print(f"📈 Average Hours per Week: {summary.average_hours_per_week}h")
        print()
        print("🏢 Location Breakdown:")
        print(f"   Company: {summary.company_hours}h")
        print(f"   Homeoffice: {summary.homeoffice_hours}h")
        
        self.pause()
    
    def view_monthly_breakdown(self):
        """Display monthly breakdown and allow selection of specific months."""
        if not self.monthly_summaries:
            print("❌ No data loaded. Please load data first.")
            self.pause()
            return
        
        while True:
            self.clear_screen()
            print("📅 Monthly Breakdown")
            print("=" * 50)
            
            # Display monthly summaries
            for i, summary in enumerate(self.monthly_summaries):
                month_name = self.calculator.format_month_name(summary.year, summary.month)
                print(f"{i + 1}. {month_name}: {summary.total_hours}h ({summary.entry_count} entries)")
            
            print("\n0. Back to statistics menu")
            print("-" * 50)
            
            try:
                choice = input("Select a month to view details (or 0 to go back): ").strip()
                
                if choice == "0":
                    break
                
                month_index = int(choice) - 1
                if 0 <= month_index < len(self.monthly_summaries):
                    self.view_month_details(self.monthly_summaries[month_index])
                else:
                    print("❌ Invalid selection.")
                    self.pause()
                    
            except ValueError:
                print("❌ Please enter a valid number.")
                self.pause()
            except KeyboardInterrupt:
                break
    
    def view_month_details(self, month_summary: MonthlySummary):
        """Display detailed information for a specific month."""
        self.clear_screen()
        month_name = self.calculator.format_month_name(month_summary.year, month_summary.month)
        
        print(f"📅 {month_name} Details")
        print("=" * 50)
        
        print(f"📊 Total Hours: {month_summary.total_hours}h")
        print(f"📝 Total Entries: {month_summary.entry_count}")
        print(f"🏢 Company Hours: {month_summary.company_hours}h")
        print(f"🏠 Homeoffice Hours: {month_summary.homeoffice_hours}h")
        print()
        
        # Get entries for this month
        month_entries = self.calculator.get_entries_for_month(
            self.entries, month_summary.year, month_summary.month
        )
        
        # Limit display entries
        display_entries = month_entries[:self.config.ui.max_display_entries]
        
        print(f"📋 Detailed Entries (showing first {len(display_entries)} of {len(month_entries)}):")
        print("-" * 80)
        print(f"{'Date':<12} {'Time':<20} {'Duration':<10} {'Location':<12} {'Description'}")
        print("-" * 80)
        
        for entry in sorted(display_entries, key=lambda x: x.start_time):
            date_str = entry.start_time.strftime('%Y-%m-%d')
            time_str = f"{entry.start_time.strftime('%H:%M')} - {entry.end_time.strftime('%H:%M')}"
            duration_str = f"{entry.duration.total_seconds() / 3600:.1f}h"
            
            description = entry.description[:40] + "..." if len(entry.description) > 40 else entry.description
            print(f"{date_str:<12} {time_str:<20} {duration_str:<10} {entry.location:<12} {description}")
        
        if len(month_entries) > len(display_entries):
            print(f"\n... and {len(month_entries) - len(display_entries)} more entries")
        
        self.pause()
    
    def view_raw_data(self):
        """Display all parsed entries in a table format."""
        if not self.entries:
            print("❌ No data loaded. Please load data first.")
            self.pause()
            return
        
        self.clear_screen()
        print("📋 Raw Data")
        print("=" * 50)
        print(f"Total entries: {len(self.entries)}")
        
        # Limit display entries
        display_entries = self.entries[:self.config.ui.max_display_entries]
        
        print("-" * 80)
        print(f"{'Date':<12} {'Time':<20} {'Duration':<10} {'Location':<12} {'Description'}")
        print("-" * 80)
        
        for entry in sorted(display_entries, key=lambda x: x.start_time):
            date_str = entry.start_time.strftime('%Y-%m-%d')
            time_str = f"{entry.start_time.strftime('%H:%M')} - {entry.end_time.strftime('%H:%M')}"
            duration_str = f"{entry.duration.total_seconds() / 3600:.1f}h"
            
            description = entry.description[:40] + "..." if len(entry.description) > 40 else entry.description
            print(f"{date_str:<12} {time_str:<20} {duration_str:<10} {entry.location:<12} {description}")
        
        if len(self.entries) > len(display_entries):
            print(f"\n... and {len(self.entries) - len(display_entries)} more entries")
        
        self.pause()
    
    def export_html_report(self):
        """Export data to HTML report."""
        if not self.entries or not self.overall_summary or not self.monthly_summaries:
            print("❌ No data loaded. Please load data first.")
            self.pause()
            return
        
        self.clear_screen()
        print("📄 Export HTML Report")
        print("=" * 50)
        
        filename = input("Enter filename (default: report.html): ").strip()
        if not filename:
            filename = "report.html"
        
        if not filename.endswith('.html'):
            filename += '.html'
        
        try:
            saved_filename = self.exporter.save_html_report(
                self.entries, self.overall_summary, self.monthly_summaries, filename
            )
            print(f"✅ Report saved as: {saved_filename}")
            print(f"📁 Full path: {os.path.abspath(saved_filename)}")
        except Exception as e:
            print(f"❌ Error saving report: {e}")
        
        self.pause()
    
    def clear_all_data(self):
        """Clear all loaded data."""
        self.clear_screen()
        print("🗑️  Clear All Data")
        print("=" * 50)
        
        if not self.entries:
            print("ℹ️  No data to clear.")
            self.pause()
            return
        
        print(f"Current data: {len(self.entries)} entries, {self.overall_summary.total_hours}h total")
        print()
        
        if input("Are you sure you want to clear all data? (y/N): ").lower() == 'y':
            self.entries = []
            self.overall_summary = None
            self.monthly_summaries = None
            print("✅ All data cleared successfully!")
        else:
            print("❌ Data clearing cancelled.")
        
        self.pause()
    
    def show_help(self):
        """Show help information."""
        self.clear_screen()
        print("📖 ChronoCLI Help")
        print("=" * 50)
        print("ChronoCLI - Personal Time Tracker (Phase 2)")
        print("=" * 50)
        print()
        print("🎯 Features:")
        print("• Import data from strings or files")
        print("• Support for German date formats")
        print("• Automatic data merging and deduplication")
        print("• Comprehensive statistics and reports")
        print("• HTML report generation")
        print("• Configurable settings")
        print()
        print("📝 Supported Data Formats:")
        print("• Dates: 30.6.25, 13.9, 01.07.2025")
        print("• Time ranges: 9:00 - 12:00, 13:00-17:00")
        print("• Locations: C (Company), H (Homeoffice)")
        print("• Files: CSV, Excel (.xlsx/.xls), Text (.txt/.json)")
        print()
        print("📁 File Import:")
        print("• CSV files with columns: Date, Hours, Location, Info")
        print("• Excel files with similar structure")
        print("• Text files with same format as string input")
        print()
        print("⚙️  Configuration:")
        print("• Settings stored in config.json")
        print("• Customizable date formats, column mappings")
        print("• Configurable location mappings and separators")
        print()
        print("📊 Statistics:")
        print("• Overall summary with totals and averages")
        print("• Monthly breakdowns with detailed entries")
        print("• Location-based analysis")
        print("• HTML report generation")
        print()
        print("🔗 For more information, see README.md")
        print("=" * 50)
        
        self.pause()
    
    def create_main_menu(self):
        """Create and return the main menu."""
        menu = ConsoleMenu(
            "⏰ ChronoCLI - Personal Time Tracker",
            "Phase 2: Enhanced Flexibility & Configuration",
            exit_option_text="Exit"
        )
        
        if self.config.ui.menu_style == "ascii_border":
            menu.border_style = AsciiBorderStyle()
        
        # Import Data Submenu
        import_menu = ConsoleMenu("📥 Import Data", "Choose data source:")
        import_menu.append_item(FunctionItem("Load from String", self.load_data_from_string))
        import_menu.append_item(FunctionItem("Load from File", self.load_data_from_file))
        import_menu.append_item(FunctionItem("Back to Main Menu", menu.show))
        
        # Statistics Submenu
        stats_menu = ConsoleMenu("📊 Statistics", "View statistics:")
        stats_menu.append_item(FunctionItem("Overall Summary", self.view_overall_summary))
        stats_menu.append_item(FunctionItem("Monthly Breakdown", self.view_monthly_breakdown))
        stats_menu.append_item(FunctionItem("View Raw Data", self.view_raw_data))
        stats_menu.append_item(FunctionItem("Back to Main Menu", menu.show))
        
        # Settings Submenu
        settings_menu = ConsoleMenu("⚙️  Settings", "Configuration options:")
        settings_menu.append_item(FunctionItem("View Current Settings", self.view_current_settings))
        settings_menu.append_item(FunctionItem("Reset to Defaults", self.reset_settings_to_defaults))
        settings_menu.append_item(FunctionItem("Back to Main Menu", menu.show))
        
        # Add main menu items
        menu.append_item(SubmenuItem("📥 Import Data", import_menu))
        menu.append_item(SubmenuItem("📊 Statistics", stats_menu))
        menu.append_item(FunctionItem("📄 Export HTML Report", self.export_html_report))
        menu.append_item(SubmenuItem("⚙️  Settings", settings_menu))
        menu.append_item(FunctionItem("🗑️  Clear All Data", self.clear_all_data))
        menu.append_item(FunctionItem("📖 Help", self.show_help))
        
        # Show current data status if available
        if self.entries and self.overall_summary:
            menu.append_item(FunctionItem(
                f"📊 Current: {len(self.entries)} entries, {self.overall_summary.total_hours}h",
                lambda: None
            ))
        
        return menu
    
    def run(self):
        """Run the main application."""
        try:
            # Show welcome message
            self.clear_screen()
            print("⏰ Welcome to ChronoCLI - Personal Time Tracker")
            print("=" * 60)
            print("Phase 2: Enhanced Flexibility & Configuration")
            print("=" * 60)
            
            if self.config.ui.show_help_text:
                print("💡 Tip: Use the 'Help' option to see all features and formats")
                print()
            
            self.pause()
            
            # Create and show main menu
            menu = self.create_main_menu()
            menu.show()
            
            print("\n👋 Thank you for using ChronoCLI!")
            
        except KeyboardInterrupt:
            print("\n\n👋 Thank you for using ChronoCLI!")
        except Exception as e:
            print(f"\n\n❌ An unexpected error occurred: {e}")
            if self.config.ui.show_help_text:
                print("💡 Please check your data format and try again.")
            sys.exit(1)


# Add method to TimeCalculator class for month name formatting
def format_month_name(self, year: int, month: int) -> str:
    """Format year and month as readable string."""
    from datetime import datetime
    return datetime(year, month, 1).strftime('%B %Y')


TimeCalculator.format_month_name = format_month_name