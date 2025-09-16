import unittest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_parser import TimeEntry
from data_merger import DataMerger, MergeResult


class TestDataMerger(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.merger = DataMerger(time_tolerance_minutes=5)
        
        # Create sample entries
        self.existing_entries = [
            TimeEntry(
                start_time=datetime(2025, 6, 30, 9, 0),
                end_time=datetime(2025, 6, 30, 12, 0),
                duration=timedelta(hours=3),
                location="Company",
                description="Morning work"
            ),
            TimeEntry(
                start_time=datetime(2025, 6, 30, 13, 0),
                end_time=datetime(2025, 6, 30, 17, 0),
                duration=timedelta(hours=4),
                location="Company",
                description="Afternoon work"
            )
        ]
        
        self.new_entries = [
            TimeEntry(
                start_time=datetime(2025, 6, 30, 9, 0),
                end_time=datetime(2025, 6, 30, 12, 0),
                duration=timedelta(hours=3),
                location="Company",
                description="Morning work"  # Exact duplicate
            ),
            TimeEntry(
                start_time=datetime(2025, 7, 1, 9, 0),
                end_time=datetime(2025, 7, 1, 12, 0),
                duration=timedelta(hours=3),
                location="Homeoffice",
                description="Home office work"  # New entry
            ),
            TimeEntry(
                start_time=datetime(2025, 6, 30, 13, 2),  # 2 minutes different
                end_time=datetime(2025, 6, 30, 17, 2),   # 2 minutes different
                duration=timedelta(hours=4, minutes=0),
                location="Company",
                description="Afternoon work"  # Within tolerance, should be duplicate
            )
        ]
    
    def test_merge_entries_with_duplicates(self):
        """Test merging entries with duplicates."""
        result = self.merger.merge_entries(self.existing_entries, self.new_entries)
        
        # Should have 3 entries total (2 existing + 1 new)
        self.assertEqual(result.total_entries_before, 2)
        self.assertEqual(result.total_entries_after, 3)
        self.assertEqual(result.new_entries_added, 1)
        self.assertEqual(result.duplicates_removed, 2)
        self.assertEqual(len(result.merge_errors), 0)
    
    def test_merge_entries_no_duplicates(self):
        """Test merging entries with no duplicates."""
        # Create completely new entries
        new_unique_entries = [
            TimeEntry(
                start_time=datetime(2025, 7, 2, 9, 0),
                end_time=datetime(2025, 7, 2, 12, 0),
                duration=timedelta(hours=3),
                location="Company",
                description="New work"
            )
        ]
        
        result = self.merger.merge_entries(self.existing_entries, new_unique_entries)
        
        self.assertEqual(result.total_entries_before, 2)
        self.assertEqual(result.total_entries_after, 3)
        self.assertEqual(result.new_entries_added, 1)
        self.assertEqual(result.duplicates_removed, 0)
    
    def test_merge_entries_all_duplicates(self):
        """Test merging when all new entries are duplicates."""
        # Create entries that are all duplicates
        duplicate_entries = [
            TimeEntry(
                start_time=datetime(2025, 6, 30, 9, 0),
                end_time=datetime(2025, 6, 30, 12, 0),
                duration=timedelta(hours=3),
                location="Company",
                description="Morning work"
            ),
            TimeEntry(
                start_time=datetime(2025, 6, 30, 13, 0),
                end_time=datetime(2025, 6, 30, 17, 0),
                duration=timedelta(hours=4),
                location="Company",
                description="Afternoon work"
            )
        ]
        
        result = self.merger.merge_entries(self.existing_entries, duplicate_entries)
        
        self.assertEqual(result.total_entries_before, 2)
        self.assertEqual(result.total_entries_after, 2)
        self.assertEqual(result.new_entries_added, 0)
        self.assertEqual(result.duplicates_removed, 2)
    
    def test_merge_with_invalid_entries(self):
        """Test merging with invalid entries."""
        # Create entries with invalid data
        invalid_entries = [
            TimeEntry(
                start_time=datetime(2025, 6, 30, 9, 0),
                end_time=datetime(2025, 6, 30, 8, 0),  # End before start
                duration=timedelta(hours=-1),
                location="Company",
                description="Invalid entry"
            ),
            TimeEntry(
                start_time=datetime(2025, 7, 1, 9, 0),
                end_time=datetime(2025, 7, 1, 12, 0),
                duration=timedelta(hours=3),
                location="Homeoffice",
                description="Valid entry"
            )
        ]
        
        result = self.merger.merge_entries(self.existing_entries, invalid_entries)
        
        # Should only add the valid entry
        self.assertEqual(result.total_entries_before, 2)
        self.assertEqual(result.total_entries_after, 3)
        self.assertEqual(result.new_entries_added, 1)
        self.assertEqual(len(result.merge_errors), 1)  # One error for invalid entry
    
    def test_is_duplicate_exact_match(self):
        """Test duplicate detection with exact matches."""
        entry1 = self.existing_entries[0]
        entry2 = TimeEntry(
            start_time=datetime(2025, 6, 30, 9, 0),
            end_time=datetime(2025, 6, 30, 12, 0),
            duration=timedelta(hours=3),
            location="Company",
            description="Morning work"
        )
        
        self.assertTrue(self.merger._is_duplicate(entry1, entry2))
    
    def test_is_duplicate_within_tolerance(self):
        """Test duplicate detection with time tolerance."""
        entry1 = self.existing_entries[0]
        entry2 = TimeEntry(
            start_time=datetime(2025, 6, 30, 9, 3),  # 3 minutes different
            end_time=datetime(2025, 6, 30, 12, 3),   # 3 minutes different
            duration=timedelta(hours=3),
            location="Company",
            description="Morning work"
        )
        
        self.assertTrue(self.merger._is_duplicate(entry1, entry2))
    
    def test_is_duplicate_outside_tolerance(self):
        """Test duplicate detection outside time tolerance."""
        entry1 = self.existing_entries[0]
        entry2 = TimeEntry(
            start_time=datetime(2025, 6, 30, 9, 10),  # 10 minutes different
            end_time=datetime(2025, 6, 30, 12, 10),   # 10 minutes different
            duration=timedelta(hours=3),
            location="Company",
            description="Morning work"
        )
        
        self.assertFalse(self.merger._is_duplicate(entry1, entry2))
    
    def test_is_duplicate_different_location(self):
        """Test duplicate detection with different locations."""
        entry1 = self.existing_entries[0]
        entry2 = TimeEntry(
            start_time=datetime(2025, 6, 30, 9, 0),
            end_time=datetime(2025, 6, 30, 12, 0),
            duration=timedelta(hours=3),
            location="Homeoffice",  # Different location
            description="Morning work"
        )
        
        self.assertFalse(self.merger._is_duplicate(entry1, entry2))
    
    def test_is_duplicate_similar_descriptions(self):
        """Test duplicate detection with similar descriptions."""
        entry1 = self.existing_entries[0]
        entry2 = TimeEntry(
            start_time=datetime(2025, 6, 30, 9, 0),
            end_time=datetime(2025, 6, 30, 12, 0),
            duration=timedelta(hours=3),
            location="Company",
            description="Morning work session"  # Similar description
        )
        
        self.assertTrue(self.merger._is_duplicate(entry1, entry2))
    
    def test_is_duplicate_different_descriptions(self):
        """Test duplicate detection with different descriptions."""
        entry1 = self.existing_entries[0]
        entry2 = TimeEntry(
            start_time=datetime(2025, 6, 30, 9, 0),
            end_time=datetime(2025, 6, 30, 12, 0),
            duration=timedelta(hours=3),
            location="Company",
                description="Completely different task"  # Different description
        )
        
        self.assertFalse(self.merger._is_duplicate(entry1, entry2))
    
    def test_merge_from_multiple_sources(self):
        """Test merging from multiple sources."""
        source1 = [
            TimeEntry(
                start_time=datetime(2025, 7, 1, 9, 0),
                end_time=datetime(2025, 7, 1, 12, 0),
                duration=timedelta(hours=3),
                location="Company",
                description="Source 1 entry"
            )
        ]
        
        source2 = [
            TimeEntry(
                start_time=datetime(2025, 7, 2, 9, 0),
                end_time=datetime(2025, 7, 2, 12, 0),
                duration=timedelta(hours=3),
                location="Homeoffice",
                description="Source 2 entry"
            ),
            TimeEntry(
                start_time=datetime(2025, 7, 1, 9, 0),  # Duplicate with source1
                end_time=datetime(2025, 7, 1, 12, 0),
                duration=timedelta(hours=3),
                location="Company",
                description="Source 1 entry"
            )
        ]
        
        result = self.merger.merge_from_multiple_sources(
            self.existing_entries, [source1, source2]
        )
        
        # Should have 4 entries total (2 existing + 2 new from both sources - 1 duplicate)
        self.assertEqual(result.total_entries_before, 2)
        self.assertEqual(result.total_entries_after, 4)
        self.assertEqual(result.new_entries_added, 2)
        self.assertEqual(result.duplicates_removed, 1)
    
    def test_detect_overlapping_entries(self):
        """Test detection of overlapping entries."""
        overlapping_entries = [
            TimeEntry(
                start_time=datetime(2025, 6, 30, 11, 0),  # Overlaps with first entry
                end_time=datetime(2025, 6, 30, 14, 0),
                duration=timedelta(hours=3),
                location="Company",
                description="Overlapping work"
            ),
            TimeEntry(
                start_time=datetime(2025, 6, 30, 18, 0),  # No overlap
                end_time=datetime(2025, 6, 30, 20, 0),
                duration=timedelta(hours=2),
                location="Homeoffice",
                description="Evening work"
            )
        ]
        
        all_entries = self.existing_entries + overlapping_entries
        overlapping_pairs = self.merger.detect_overlapping_entries(all_entries)
        
        # Should find one overlapping pair
        self.assertEqual(len(overlapping_pairs), 1)
        self.assertEqual(overlapping_pairs[0][0], self.existing_entries[0])  # First existing entry
        self.assertEqual(overlapping_pairs[0][1], overlapping_entries[0])      # Overlapping entry
    
    def test_suggest_merge_conflicts(self):
        """Test conflict detection before merging."""
        conflicting_entries = [
            TimeEntry(
                start_time=datetime(2025, 6, 30, 11, 0),  # Overlaps with existing
                end_time=datetime(2025, 6, 30, 14, 0),
                duration=timedelta(hours=3),
                location="Company",
                description="Conflicting work"
            ),
            TimeEntry(
                start_time=datetime(2025, 6, 30, 9, 0),  # Same time, different description
                end_time=datetime(2025, 6, 30, 12, 0),
                duration=timedelta(hours=3),
                location="Company",
                description="Different description"
            )
        ]
        
        conflicts = self.merger.suggest_merge_conflicts(
            self.existing_entries, conflicting_entries
        )
        
        # Should find conflicts
        self.assertGreater(len(conflicts), 0)
        self.assertTrue(any("overlap" in conflict.lower() for conflict in conflicts))
    
    def test_get_merge_summary(self):
        """Test merge summary generation."""
        result = MergeResult(
            total_entries_before=2,
            total_entries_after=3,
            new_entries_added=1,
            duplicates_removed=0,
            merge_errors=[]
        )
        
        summary = self.merger.get_merge_summary(result)
        
        self.assertIn("Entries before merge: 2", summary)
        self.assertIn("Entries after merge: 3", summary)
        self.assertIn("New entries added: 1", summary)
        self.assertIn("Duplicates removed: 0", summary)
    
    def test_get_merge_summary_with_errors(self):
        """Test merge summary generation with errors."""
        result = MergeResult(
            total_entries_before=2,
            total_entries_after=3,
            new_entries_added=1,
            duplicates_removed=0,
            merge_errors=["Error 1", "Error 2", "Error 3"]
        )
        
        summary = self.merger.get_merge_summary(result)
        
        self.assertIn("Merge Errors:", summary)
        self.assertIn("Error 1", summary)
        self.assertIn("Error 2", summary)
        self.assertIn("Error 3", summary)


if __name__ == '__main__':
    unittest.main()