#!/usr/bin/env python3
"""
Test runner for ChronoCLI Phase 2

This script runs all tests for the ChronoCLI project and provides
a nice interface for viewing test results.
"""

import unittest
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from test_data_parser import TestDataParser
from test_calculator import TestTimeCalculator
from test_exporter import TestHTMLExporter
from test_settings_manager import TestSettingsManager
from test_data_parser_phase2 import TestDataParserPhase2
from test_data_merger import TestDataMerger


class ChronoCLITestRunner:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.error_tests = 0
    
    def run_tests(self):
        """Run all tests and collect results."""
        print("🧪 ChronoCLI Test Runner - Phase 2")
        print("=" * 60)
        print(f"Running tests at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Create test suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add Phase 1 test cases
        suite.addTests(loader.loadTestsFromTestCase(TestDataParser))
        suite.addTests(loader.loadTestsFromTestCase(TestTimeCalculator))
        suite.addTests(loader.loadTestsFromTestCase(TestHTMLExporter))
        
        # Add Phase 2 test cases
        suite.addTests(loader.loadTestsFromTestCase(TestSettingsManager))
        suite.addTests(loader.loadTestsFromTestCase(TestDataParserPhase2))
        suite.addTests(loader.loadTestsFromTestCase(TestDataMerger))
        
        # Run tests with custom result handler
        runner = unittest.TextTestRunner(verbosity=2, stream=open(os.devnull, 'w'))
        result = runner.run(suite)
        
        # Collect results
        self.total_tests = result.testsRun
        self.passed_tests = result.testsRun - len(result.failures) - len(result.errors)
        self.failed_tests = len(result.failures)
        self.error_tests = len(result.errors)
        
        # Store detailed results
        self.test_results = []
        
        # Process failures
        for test, traceback in result.failures:
            self.test_results.append({
                'test': str(test),
                'status': 'FAILED',
                'message': traceback.split('\n')[0] if traceback else 'Unknown error'
            })
        
        # Process errors
        for test, traceback in result.errors:
            self.test_results.append({
                'test': str(test),
                'status': 'ERROR',
                'message': traceback.split('\n')[0] if traceback else 'Unknown error'
            })
        
        return result.wasSuccessful()
    
    def display_results(self):
        """Display test results in a nice format."""
        print("\n📊 Test Results Summary")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"💥 Errors: {self.error_tests}")
        
        if self.failed_tests > 0 or self.error_tests > 0:
            print("\n🚨 Failed Tests:")
            print("-" * 60)
            for result in self.test_results:
                status_icon = "❌" if result['status'] == 'FAILED' else "💥"
                print(f"{status_icon} {result['test']}")
                print(f"   Message: {result['message']}")
                print()
        
        # Calculate success rate
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("=" * 60)
        
        if self.failed_tests == 0 and self.error_tests == 0:
            print("🎉 All tests passed! ChronoCLI Phase 2 is working correctly!")
        else:
            print("⚠️  Some tests failed. Please check the implementation.")
    
    def display_phase_info(self):
        """Display information about test phases."""
        print("\n📋 Test Coverage")
        print("=" * 60)
        print("🔵 Phase 1 Tests:")
        print("   • Data Parser - German date/time parsing")
        print("   • Calculator - Time calculations and statistics")
        print("   • Exporter - HTML report generation")
        print()
        print("🟢 Phase 2 Tests:")
        print("   • Settings Manager - Configuration management")
        print("   • Data Parser (Phase 2) - File loading and settings integration")
        print("   • Data Merger - Data merging and deduplication")
        print("=" * 60)
    
    def run(self):
        """Run the complete test suite."""
        try:
            self.display_phase_info()
            success = self.run_tests()
            self.display_results()
            return success
        except KeyboardInterrupt:
            print("\n\n⏹️  Tests interrupted by user.")
            return False
        except Exception as e:
            print(f"\n\n💥 Unexpected error during testing: {e}")
            return False


def main():
    """Main entry point for the test runner."""
    runner = ChronoCLITestRunner()
    success = runner.run()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()