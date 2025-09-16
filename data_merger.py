from typing import List, Set, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from data_parser import TimeEntry
from calculator import TimeCalculator


@dataclass
class MergeResult:
    """Result of data merging operation."""
    total_entries_before: int
    total_entries_after: int
    new_entries_added: int
    duplicates_removed: int
    merge_errors: List[str]


class DataMerger:
    """Handles data merging and deduplication."""
    
    def __init__(self, time_tolerance_minutes: int = 5):
        """
        Initialize data merger.
        
        Args:
            time_tolerance_minutes: Time tolerance for considering entries as duplicates
        """
        self.time_tolerance = timedelta(minutes=time_tolerance_minutes)
        self.calculator = TimeCalculator()
    
    def merge_entries(self, existing_entries: List[TimeEntry], 
                     new_entries: List[TimeEntry]) -> MergeResult:
        """
        Merge new entries with existing entries, removing duplicates.
        
        Args:
            existing_entries: List of existing TimeEntry objects
            new_entries: List of new TimeEntry objects to merge
            
        Returns:
            MergeResult with statistics about the merge operation
        """
        merge_errors = []
        
        # Validate entries
        valid_existing = self._validate_entries(existing_entries, merge_errors)
        valid_new = self._validate_entries(new_entries, merge_errors)
        
        # Find duplicates
        duplicates = self._find_duplicates(valid_existing, valid_new)
        
        # Add non-duplicate entries
        non_duplicate_new = [entry for entry in valid_new if entry not in duplicates]
        
        # Merge entries
        merged_entries = valid_existing + non_duplicate_new
        
        # Sort by start time
        merged_entries.sort(key=lambda x: x.start_time)
        
        return MergeResult(
            total_entries_before=len(existing_entries),
            total_entries_after=len(merged_entries),
            new_entries_added=len(non_duplicate_new),
            duplicates_removed=len(duplicates),
            merge_errors=merge_errors
        )
    
    def _validate_entries(self, entries: List[TimeEntry], errors: List[str]) -> List[TimeEntry]:
        """Validate entries and return only valid ones."""
        valid_entries = []
        
        for i, entry in enumerate(entries):
            try:
                # Check if entry has valid data
                if not isinstance(entry.start_time, datetime):
                    errors.append(f"Entry {i}: Invalid start_time type")
                    continue
                
                if not isinstance(entry.end_time, datetime):
                    errors.append(f"Entry {i}: Invalid end_time type")
                    continue
                
                if not isinstance(entry.duration, timedelta):
                    errors.append(f"Entry {i}: Invalid duration type")
                    continue
                
                if entry.end_time <= entry.start_time:
                    errors.append(f"Entry {i}: End time is before or equal to start time")
                    continue
                
                if entry.duration.total_seconds() <= 0:
                    errors.append(f"Entry {i}: Invalid duration (<= 0)")
                    continue
                
                valid_entries.append(entry)
                
            except Exception as e:
                errors.append(f"Entry {i}: Validation error - {e}")
        
        return valid_entries
    
    def _find_duplicates(self, existing_entries: List[TimeEntry], 
                        new_entries: List[TimeEntry]) -> Set[TimeEntry]:
        """
        Find duplicate entries between existing and new entries.
        
        Args:
            existing_entries: List of existing entries
            new_entries: List of new entries to check for duplicates
            
        Returns:
            Set of duplicate entries from new_entries
        """
        duplicates = set()
        
        for new_entry in new_entries:
            for existing_entry in existing_entries:
                if self._is_duplicate(new_entry, existing_entry):
                    duplicates.add(new_entry)
                    break
        
        return duplicates
    
    def _is_duplicate(self, entry1: TimeEntry, entry2: TimeEntry) -> bool:
        """
        Check if two entries are duplicates.
        
        Args:
            entry1: First TimeEntry
            entry2: Second TimeEntry
            
        Returns:
            True if entries are considered duplicates
        """
        # Check if dates are the same
        if entry1.start_time.date() != entry2.start_time.date():
            return False
        
        # Check if start times are within tolerance
        time_diff = abs(entry1.start_time - entry2.start_time)
        if time_diff > self.time_tolerance:
            return False
        
        # Check if end times are within tolerance
        time_diff = abs(entry1.end_time - entry2.end_time)
        if time_diff > self.time_tolerance:
            return False
        
        # Check if durations are similar (within 5 minutes tolerance)
        duration_diff = abs(entry1.duration - entry2.duration)
        if duration_diff > timedelta(minutes=5):
            return False
        
        # Check if locations are the same
        if entry1.location != entry2.location:
            return False
        
        # Optional: Check if descriptions are similar (if both exist)
        if entry1.description and entry2.description:
            # Simple similarity check - can be enhanced
            desc1_lower = entry1.description.lower().strip()
            desc2_lower = entry2.description.lower().strip()
            
            # Check if one description contains the other or vice versa
            if (desc1_lower in desc2_lower or desc2_lower in desc1_lower):
                return True
            
            # Check for high similarity (simple approach)
            words1 = set(desc1_lower.split())
            words2 = set(desc2_lower.split())
            
            if words1 and words2:
                intersection = words1.intersection(words2)
                union = words1.union(words2)
                similarity = len(intersection) / len(union)
                
                if similarity > 0.7:  # 70% similarity threshold
                    return True
        elif not entry1.description and not entry2.description:
            # Both have no description, consider them duplicates based on time
            return True
        
        return False
    
    def merge_from_multiple_sources(self, existing_entries: List[TimeEntry],
                                  sources: List[List[TimeEntry]]) -> MergeResult:
        """
        Merge entries from multiple sources with existing entries.
        
        Args:
            existing_entries: List of existing TimeEntry objects
            sources: List of entry lists from different sources
            
        Returns:
            MergeResult with statistics about the merge operation
        """
        current_entries = existing_entries.copy()
        total_new_added = 0
        total_duplicates = 0
        all_errors = []
        
        for i, source_entries in enumerate(sources):
            result = self.merge_entries(current_entries, source_entries)
            
            current_entries = [
                entry for entry in current_entries + source_entries 
                if entry not in self._find_duplicates(current_entries, source_entries)
            ]
            
            total_new_added += result.new_entries_added
            total_duplicates += result.duplicates_removed
            all_errors.extend([f"Source {i}: {error}" for error in result.merge_errors])
        
        return MergeResult(
            total_entries_before=len(existing_entries),
            total_entries_after=len(current_entries),
            new_entries_added=total_new_added,
            duplicates_removed=total_duplicates,
            merge_errors=all_errors
        )
    
    def get_merge_summary(self, merge_result: MergeResult) -> str:
        """Generate a human-readable summary of merge results."""
        summary_lines = [
            "📊 Data Merge Summary",
            "=" * 30,
            f"Entries before merge: {merge_result.total_entries_before}",
            f"Entries after merge: {merge_result.total_entries_after}",
            f"New entries added: {merge_result.new_entries_added}",
            f"Duplicates removed: {merge_result.duplicates_removed}",
        ]
        
        if merge_result.merge_errors:
            summary_lines.extend([
                "",
                "⚠️  Merge Errors:",
                "-" * 15
            ])
            for error in merge_result.merge_errors[:5]:  # Show first 5 errors
                summary_lines.append(f"  • {error}")
            
            if len(merge_result.merge_errors) > 5:
                summary_lines.append(f"  • ... and {len(merge_result.merge_errors) - 5} more errors")
        
        return "\n".join(summary_lines)
    
    def detect_overlapping_entries(self, entries: List[TimeEntry]) -> List[tuple]:
        """
        Detect overlapping entries in the list.
        
        Args:
            entries: List of TimeEntry objects
            
        Returns:
            List of tuples containing overlapping entry pairs
        """
        overlapping_pairs = []
        
        # Sort entries by start time
        sorted_entries = sorted(entries, key=lambda x: x.start_time)
        
        for i in range(len(sorted_entries)):
            for j in range(i + 1, len(sorted_entries)):
                entry1 = sorted_entries[i]
                entry2 = sorted_entries[j]
                
                # Check for overlap
                if self._entries_overlap(entry1, entry2):
                    overlapping_pairs.append((entry1, entry2))
                else:
                    # Since entries are sorted, no need to check further
                    break
        
        return overlapping_pairs
    
    def _entries_overlap(self, entry1: TimeEntry, entry2: TimeEntry) -> bool:
        """Check if two entries overlap in time."""
        return (entry1.start_time < entry2.end_time and 
                entry2.start_time < entry1.end_time)
    
    def suggest_merge_conflicts(self, existing_entries: List[TimeEntry],
                               new_entries: List[TimeEntry]) -> List[str]:
        """
        Suggest potential merge conflicts before performing the merge.
        
        Args:
            existing_entries: List of existing TimeEntry objects
            new_entries: List of new TimeEntry objects
            
        Returns:
            List of conflict descriptions
        """
        conflicts = []
        
        # Check for overlapping entries
        all_entries = existing_entries + new_entries
        overlapping_pairs = self.detect_overlapping_entries(all_entries)
        
        for entry1, entry2 in overlapping_pairs:
            if (entry1 in existing_entries and entry2 in new_entries) or \
               (entry1 in new_entries and entry2 in existing_entries):
                
                conflict_desc = (
                    f"Time overlap: {entry1.start_time.strftime('%Y-%m-%d %H:%M')} - "
                    f"{entry1.end_time.strftime('%H:%M')} overlaps with "
                    f"{entry2.start_time.strftime('%Y-%m-%d %H:%M')} - "
                    f"{entry2.end_time.strftime('%H:%M')}"
                )
                conflicts.append(conflict_desc)
        
        # Check for potential duplicates with different descriptions
        for new_entry in new_entries:
            for existing_entry in existing_entries:
                if self._is_potential_duplicate_different_desc(new_entry, existing_entry):
                    conflict_desc = (
                        f"Potential duplicate with different description: "
                        f"{new_entry.start_time.strftime('%Y-%m-%d %H:%M')} - "
                        f"{new_entry.end_time.strftime('%H:%M')}"
                    )
                    conflicts.append(conflict_desc)
        
        return conflicts
    
    def _is_potential_duplicate_different_desc(self, entry1: TimeEntry, entry2: TimeEntry) -> bool:
        """Check if entries are potential duplicates but have different descriptions."""
        # Same date and similar times
        if entry1.start_time.date() != entry2.start_time.date():
            return False
        
        time_diff = abs(entry1.start_time - entry2.start_time)
        if time_diff > timedelta(minutes=10):  # Slightly larger tolerance for this check
            return False
        
        # Different descriptions
        if entry1.description and entry2.description:
            if entry1.description.lower().strip() != entry2.description.lower().strip():
                return True
        
        return False