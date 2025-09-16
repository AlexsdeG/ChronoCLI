from consolemenu import ConsoleMenu, SelectionMenu
from typing import List, Optional
import os
import sys

from data_parser import DataParser, TimeEntry
from calculator import TimeCalculator, OverallSummary, MonthlySummary
from exporter import HTMLExporter


class ChronoCLIUI:
    def __init__(self):
        self.parser = DataParser()
        self.calculator = TimeCalculator()
        self.exporter = HTMLExporter()
        self.entries: List[TimeEntry] = []
        self.overall_summary: Optional[OverallSummary] = None
        self.monthly_summaries: Optional[List[MonthlySummary]] = None
    
    def clear_screen(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def pause(self):
        """Pause execution and wait for user input."""
        input("\nPress Enter to continue...")
    
    def load_data_from_string(self):
        """Load data from user input string."""
        self.clear_screen()
        print("📝 Load Data from String")
        print("=" * 40)
        print("Paste your time tracking data below.")
        print("Enter an empty line when finished.")
        print("-" * 40)
        
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
            self.entries = self.parser.parse_input(text_data)
            
            if not self.entries:
                print("❌ No valid entries found in the data.")
                self.pause()
                return
            
            # Calculate summaries
            self.overall_summary = self.calculator.calculate_overall_summary(self.entries)
            self.monthly_summaries = self.calculator.calculate_monthly_summary(self.entries)
            
            print(f"✅ Successfully loaded {len(self.entries)} entries!")
            print(f"📊 Total hours: {self.overall_summary.total_hours}h")
            self.pause()
            
        except Exception as e:
            print(f"❌ Error parsing data: {e}")
            self.pause()
    
    def view_overall_summary(self):
        """Display overall summary statistics."""
        if not self.overall_summary:
            print("❌ No data loaded. Please load data first.")
            self.pause()
            return
        
        self.clear_screen()
        print("📊 Overall Summary")
        print("=" * 40)
        
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
            print("=" * 40)
            
            # Display monthly summaries
            for i, summary in enumerate(self.monthly_summaries):
                month_name = self.calculator.format_month_name(summary.year, summary.month)
                print(f"{i + 1}. {month_name}: {summary.total_hours}h ({summary.entry_count} entries)")
            
            print("\n0. Back to main menu")
            print("-" * 40)
            
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
        print("=" * 40)
        
        print(f"📊 Total Hours: {month_summary.total_hours}h")
        print(f"📝 Total Entries: {month_summary.entry_count}")
        print(f"🏢 Company Hours: {month_summary.company_hours}h")
        print(f"🏠 Homeoffice Hours: {month_summary.homeoffice_hours}h")
        print()
        
        # Get entries for this month
        month_entries = self.calculator.get_entries_for_month(
            self.entries, month_summary.year, month_summary.month
        )
        
        print("📋 Detailed Entries:")
        print("-" * 80)
        print(f"{'Date':<12} {'Time':<20} {'Duration':<10} {'Location':<12} {'Description'}")
        print("-" * 80)
        
        for entry in sorted(month_entries, key=lambda x: x.start_time):
            date_str = entry.start_time.strftime('%Y-%m-%d')
            time_str = f"{entry.start_time.strftime('%H:%M')} - {entry.end_time.strftime('%H:%M')}"
            duration_str = f"{entry.duration.total_seconds() / 3600:.1f}h"
            
            print(f"{date_str:<12} {time_str:<20} {duration_str:<10} {entry.location:<12} {entry.description[:40]}...")
        
        self.pause()
    
    def view_raw_data(self):
        """Display all parsed entries in a table format."""
        if not self.entries:
            print("❌ No data loaded. Please load data first.")
            self.pause()
            return
        
        self.clear_screen()
        print("📋 Raw Data")
        print("=" * 40)
        print(f"Total entries: {len(self.entries)}")
        print("-" * 80)
        print(f"{'Date':<12} {'Time':<20} {'Duration':<10} {'Location':<12} {'Description'}")
        print("-" * 80)
        
        for entry in sorted(self.entries, key=lambda x: x.start_time):
            date_str = entry.start_time.strftime('%Y-%m-%d')
            time_str = f"{entry.start_time.strftime('%H:%M')} - {entry.end_time.strftime('%H:%M')}"
            duration_str = f"{entry.duration.total_seconds() / 3600:.1f}h"
            
            print(f"{date_str:<12} {time_str:<20} {duration_str:<10} {entry.location:<12} {entry.description[:40]}...")
        
        self.pause()
    
    def export_html_report(self):
        """Export data to HTML report."""
        if not self.entries or not self.overall_summary or not self.monthly_summaries:
            print("❌ No data loaded. Please load data first.")
            self.pause()
            return
        
        self.clear_screen()
        print("📄 Export HTML Report")
        print("=" * 40)
        
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
    
    def statistics_menu(self):
        """Display statistics submenu."""
        while True:
            self.clear_screen()
            print("📊 Statistics Menu")
            print("=" * 40)
            print("1. Overall Summary")
            print("2. Monthly Breakdown")
            print("3. View Raw Data")
            print("0. Back to Main Menu")
            print("-" * 40)
            
            choice = input("Select an option: ").strip()
            
            if choice == "1":
                self.view_overall_summary()
            elif choice == "2":
                self.view_monthly_breakdown()
            elif choice == "3":
                self.view_raw_data()
            elif choice == "0":
                break
            else:
                print("❌ Invalid option. Please try again.")
                self.pause()
    
    def main_menu(self):
        """Display main menu and handle user input."""
        while True:
            self.clear_screen()
            print("⏰ ChronoCLI - Personal Time Tracker")
            print("=" * 40)
            print("1. Load Data from String")
            print("2. View Statistics")
            print("3. Export HTML Report")
            print("0. Exit")
            print("-" * 40)
            
            if self.entries:
                print(f"📊 Current data: {len(self.entries)} entries, {self.overall_summary.total_hours}h total")
            
            choice = input("Select an option: ").strip()
            
            if choice == "1":
                self.load_data_from_string()
            elif choice == "2":
                self.statistics_menu()
            elif choice == "3":
                self.export_html_report()
            elif choice == "0":
                print("👋 Thank you for using ChronoCLI!")
                break
            else:
                print("❌ Invalid option. Please try again.")
                self.pause()
    
    def run(self):
        """Run the main application."""
        try:
            self.main_menu()
        except KeyboardInterrupt:
            print("\n\n👋 Thank you for using ChronoCLI!")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
            sys.exit(1)


# Add method to TimeCalculator class for month name formatting
def format_month_name(self, year: int, month: int) -> str:
    """Format year and month as readable string."""
    from datetime import datetime
    return datetime(year, month, 1).strftime('%B %Y')


TimeCalculator.format_month_name = format_month_name