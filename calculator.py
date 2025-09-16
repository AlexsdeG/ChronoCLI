from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import defaultdict
from dataclasses import dataclass

from data_parser import TimeEntry


@dataclass
class MonthlySummary:
    year: int
    month: int
    total_hours: float
    total_minutes: int
    entry_count: int
    company_hours: float
    homeoffice_hours: float


@dataclass
class OverallSummary:
    total_hours: float
    total_minutes: int
    total_days: int
    average_hours_per_month: float
    average_hours_per_week: float
    total_months: int
    total_weeks: int
    company_hours: float
    homeoffice_hours: float


class TimeCalculator:
    def __init__(self):
        pass
    
    def calculate_total_hours(self, entries: List[TimeEntry]) -> Tuple[float, int]:
        """Calculate total hours and minutes from all entries."""
        total_duration = timedelta()
        
        for entry in entries:
            total_duration += entry.duration
        
        total_seconds = total_duration.total_seconds()
        total_hours = total_seconds / 3600
        total_minutes = int(total_seconds / 60)
        
        return round(total_hours, 2), total_minutes
    
    def calculate_monthly_summary(self, entries: List[TimeEntry]) -> List[MonthlySummary]:
        """Calculate summary for each month."""
        monthly_data = defaultdict(lambda: {
            'total_duration': timedelta(),
            'entry_count': 0,
            'company_duration': timedelta(),
            'homeoffice_duration': timedelta()
        })
        
        for entry in entries:
            month_key = (entry.start_time.year, entry.start_time.month)
            monthly_data[month_key]['total_duration'] += entry.duration
            monthly_data[month_key]['entry_count'] += 1
            
            if entry.location == 'Company':
                monthly_data[month_key]['company_duration'] += entry.duration
            elif entry.location == 'Homeoffice':
                monthly_data[month_key]['homeoffice_duration'] += entry.duration
        
        summaries = []
        for (year, month), data in monthly_data.items():
            total_seconds = data['total_duration'].total_seconds()
            company_seconds = data['company_duration'].total_seconds()
            homeoffice_seconds = data['homeoffice_duration'].total_seconds()
            
            summary = MonthlySummary(
                year=year,
                month=month,
                total_hours=round(total_seconds / 3600, 2),
                total_minutes=int(total_seconds / 60),
                entry_count=data['entry_count'],
                company_hours=round(company_seconds / 3600, 2),
                homeoffice_hours=round(homeoffice_seconds / 3600, 2)
            )
            summaries.append(summary)
        
        # Sort by year and month
        summaries.sort(key=lambda x: (x.year, x.month))
        return summaries
    
    def calculate_overall_summary(self, entries: List[TimeEntry]) -> OverallSummary:
        """Calculate overall statistics."""
        if not entries:
            return OverallSummary(0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        total_hours, total_minutes = self.calculate_total_hours(entries)
        
        # Calculate unique days, months, and weeks
        unique_days = set()
        unique_months = set()
        unique_weeks = set()
        
        company_duration = timedelta()
        homeoffice_duration = timedelta()
        
        for entry in entries:
            unique_days.add(entry.start_time.date())
            unique_months.add((entry.start_time.year, entry.start_time.month))
            
            # Get week number (ISO week)
            year, week, _ = entry.start_time.isocalendar()
            unique_weeks.add((year, week))
            
            if entry.location == 'Company':
                company_duration += entry.duration
            elif entry.location == 'Homeoffice':
                homeoffice_duration += entry.duration
        
        total_days = len(unique_days)
        total_months = len(unique_months)
        total_weeks = len(unique_weeks)
        
        company_hours = round(company_duration.total_seconds() / 3600, 2)
        homeoffice_hours = round(homeoffice_duration.total_seconds() / 3600, 2)
        
        # Calculate averages
        average_hours_per_month = round(total_hours / total_months, 2) if total_months > 0 else 0
        average_hours_per_week = round(total_hours / total_weeks, 2) if total_weeks > 0 else 0
        
        return OverallSummary(
            total_hours=total_hours,
            total_minutes=total_minutes,
            total_days=total_days,
            average_hours_per_month=average_hours_per_month,
            average_hours_per_week=average_hours_per_week,
            total_months=total_months,
            total_weeks=total_weeks,
            company_hours=company_hours,
            homeoffice_hours=homeoffice_hours
        )
    
    def get_entries_for_month(self, entries: List[TimeEntry], year: int, month: int) -> List[TimeEntry]:
        """Get all entries for a specific month."""
        return [
            entry for entry in entries
            if entry.start_time.year == year and entry.start_time.month == month
        ]
    
    def format_duration(self, duration: timedelta) -> str:
        """Format duration as human-readable string."""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}m"
    
    def format_hours_decimal(self, hours: float) -> str:
        """Format decimal hours as human-readable string."""
        whole_hours = int(hours)
        minutes = int((hours - whole_hours) * 60)
        
        if minutes > 0:
            return f"{whole_hours}h {minutes}m"
        else:
            return f"{whole_hours}h"