#!/usr/bin/env python3
"""
ChronoCLI Demo - Standard Library Version

This is a demonstration version that uses only Python standard library modules
to show the core parsing logic of ChronoCLI.
"""

from datetime import datetime, timedelta
import re
import sys
import os


class ChronoCLIDemo:
    def __init__(self):
        self.entries = []
    
    def parse_german_date(self, date_str):
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
        
        # Handle formats like "30.6.2025"
        elif re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}$', date_str):
            day, month, year = date_str.split('.')
            return datetime(int(year), int(month), int(day))
        
        raise ValueError(f"Unsupported date format: {date_str}")
    
    def parse_time_range(self, time_str, current_date):
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
    
    def parse_demo_data(self, text_data):
        """Parse demo data and show results."""
        lines = text_data.strip().split('\n')
        current_date = None
        entries = []
        
        print("📝 Parsing Data...")
        print("=" * 50)
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Skip month headers
            if line in ['July', 'August', 'Sept']:
                print(f"📅 Skipping month header: {line}")
                continue
            
            # Check if line contains a date
            if re.match(r'^\d{1,2}\.\d{1,2}(\.\d{2,4})?$', line):
                try:
                    current_date = self.parse_german_date(line)
                    print(f"📅 Set current date: {current_date.strftime('%Y-%m-%d')}")
                    continue
                except ValueError as e:
                    print(f"❌ Date parsing error: {e}")
            
            # Check if line contains a time range
            if current_date and re.search(r'\d{1,2}:\d{2}\s*[-]\s*\d{1,2}:\d{2}', line):
                try:
                    start_time, end_time = self.parse_time_range(line, current_date)
                    duration = end_time - start_time
                    
                    entry = {
                        'date': current_date.strftime('%Y-%m-%d'),
                        'start': start_time.strftime('%H:%M'),
                        'end': end_time.strftime('%H:%M'),
                        'duration': duration,
                        'duration_hours': duration.total_seconds() / 3600,
                        'line': line
                    }
                    entries.append(entry)
                    
                    print(f"✅ Parsed: {entry['date']} {entry['start']}-{entry['end']} ({entry['duration_hours']:.1f}h)")
                    
                except ValueError as e:
                    print(f"❌ Time parsing error: {e}")
        
        self.entries = entries
        return entries
    
    def calculate_statistics(self):
        """Calculate basic statistics."""
        if not self.entries:
            return None
        
        total_hours = sum(entry['duration_hours'] for entry in self.entries)
        total_minutes = int(total_hours * 60)
        
        # Group by date
        dates = set(entry['date'] for entry in self.entries)
        
        stats = {
            'total_hours': total_hours,
            'total_minutes': total_minutes,
            'total_entries': len(self.entries),
            'unique_dates': len(dates),
            'average_hours_per_day': total_hours / len(dates) if dates else 0
        }
        
        return stats
    
    def display_statistics(self):
        """Display calculated statistics."""
        stats = self.calculate_statistics()
        if not stats:
            print("❌ No data to calculate statistics.")
            return
        
        print("\n📊 Statistics Summary")
        print("=" * 50)
        print(f"📈 Total Hours: {stats['total_hours']:.1f}h ({stats['total_minutes']} minutes)")
        print(f"📅 Days Worked: {stats['unique_dates']}")
        print(f"📝 Total Entries: {stats['total_entries']}")
        print(f"📊 Average Hours per Day: {stats['average_hours_per_day']:.1f}h")
    
    def display_entries(self):
        """Display all parsed entries."""
        if not self.entries:
            print("❌ No entries to display.")
            return
        
        print("\n📋 Parsed Entries")
        print("=" * 50)
        print(f"{'Date':<12} {'Time':<15} {'Duration':<10} {'Original Line'}")
        print("-" * 70)
        
        for entry in self.entries:
            time_str = f"{entry['start']}-{entry['end']}"
            duration_str = f"{entry['duration_hours']:.1f}h"
            print(f"{entry['date']:<12} {time_str:<15} {duration_str:<10} {entry['line'][:30]}...")
    
    def run_demo(self):
        """Run the demo with sample data."""
        print("⏰ ChronoCLI Demo - Standard Library Version")
        print("=" * 60)
        print("This demo shows core parsing logic using only Python standard library.")
        print("=" * 60)
        
        # Sample data from the user's example
        sample_data = """
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
WooCommerce Produkte Varianten mit Eigenschaften
APF nur füe spezial Felder wie File Upload / Image Layer Preview
13:00 - 17:00
C
Analyse ProDir & Ado Pen CSV Datei, welche Columns für was
Swatches Plugin mit API Hooks?
Angefangen Server CSV Importer zu schreiben
"""
        
        # Parse the data
        entries = self.parse_demo_data(sample_data)
        
        if entries:
            # Display entries
            self.display_entries()
            
            # Display statistics
            self.display_statistics()
            
            print("\n🎉 Demo completed successfully!")
            print("=" * 60)
            print("This demo shows the core parsing logic of ChronoCLI.")
            print("The full version includes additional features like:")
            print("• Interactive console menu")
            print("• HTML report generation")
            print("• Advanced date parsing with dateutil")
            print("• Location and description parsing")
            print("• Monthly breakdowns")
            print("• Comprehensive error handling")
            print("=" * 60)
        else:
            print("❌ No entries were parsed from the sample data.")


def main():
    """Main entry point for the demo."""
    try:
        demo = ChronoCLIDemo()
        demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user.")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()