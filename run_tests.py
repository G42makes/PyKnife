#!/usr/bin/env python3
"""
Test runner for PyKnife.

This script discovers and runs all unit tests in the project,
and provides a consolidated report of the results.
"""

import os
import sys
import unittest
import time
import argparse
from datetime import datetime


def run_tests(include_reference=False):
    """
    Discover and run all tests in the project.
    
    Args:
        include_reference (bool): Whether to include reference tests that
            compare against system commands.
    """
    # Print header
    print("\n" + "=" * 70)
    print(f"PyKnife Test Runner - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Start timing
    start_time = time.time()
    
    # Set environment variable to control reference tests
    if not include_reference:
        os.environ['SKIP_REFERENCE_TESTS'] = '1'
    else:
        if 'SKIP_REFERENCE_TESTS' in os.environ:
            del os.environ['SKIP_REFERENCE_TESTS']
    
    # Discover all tests
    print("\nDiscovering tests...")
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Create a test result collector
    result = unittest.TestResult()
    
    # Run the tests
    print(f"Running tests from {start_dir}...")
    if include_reference:
        print("Reference tests ENABLED - comparing with system commands")
    else:
        print("Reference tests DISABLED - use --reference to enable")
    print("")
    
    suite.run(result)
    
    # Calculate run time
    run_time = time.time() - start_time
    
    # Print results
    print("\n" + "=" * 70)
    print("Test Results Summary")
    print("=" * 70)
    
    print(f"\nRan {result.testsRun} tests in {run_time:.2f} seconds")
    
    # Count skipped tests (requires Python 3.5+)
    skipped_tests = []
    for test, reason in getattr(result, 'skipped', []):
        skipped_tests.append((test, reason))
    
    if skipped_tests:
        print(f"\nSKIPPED: {len(skipped_tests)}")
        for i, (test, reason) in enumerate(skipped_tests, 1):
            print(f"  {i}. {test}: {reason}")
    
    if result.wasSuccessful():
        print("\nSUCCESS: All tests passed!")
    else:
        print(f"\nFAILURES: {len(result.failures)}")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"\n--- Failure {i} ---")
            print(f"Test: {test}")
            print(f"Traceback:\n{traceback}")
        
        print(f"\nERRORS: {len(result.errors)}")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"\n--- Error {i} ---")
            print(f"Test: {test}")
            print(f"Traceback:\n{traceback}")
    
    print("\n" + "=" * 70)
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1


def main():
    """Parse command line arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run PyKnife tests")
    parser.add_argument(
        "--reference", 
        action="store_true",
        help="Include reference tests (compare with system commands)"
    )
    args = parser.parse_args()
    
    return run_tests(include_reference=args.reference)


if __name__ == "__main__":
    sys.exit(main()) 