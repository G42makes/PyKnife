#!/usr/bin/env python3
"""
Tests for the touch command.
"""

import os
import sys
import time
import unittest
import tempfile
from io import StringIO
from datetime import datetime, timedelta
from src.commands import touch
from src.testing.reference_tester import compare_with_system


class TestTouch(unittest.TestCase):
    """Test cases for the touch command."""

    def setUp(self):
        """Set up for tests."""
        # Redirect stdout and stderr
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_files = []

    def tearDown(self):
        """Clean up after tests."""
        # Restore stdout and stderr
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        
        # Remove any test files
        for file_path in self.test_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
        
        # Remove test directory
        try:
            os.rmdir(self.test_dir)
        except OSError:
            pass

    def get_test_file_path(self, filename):
        """Get path for a test file."""
        path = os.path.join(self.test_dir, filename)
        self.test_files.append(path)
        return path

    def test_create_new_file(self):
        """Test creating a new file with touch."""
        test_file = self.get_test_file_path("new_file.txt")
        
        # Make sure the file doesn't exist
        if os.path.exists(test_file):
            os.remove(test_file)
        
        # Run touch
        exit_code = touch.main([test_file])
        
        # Check results
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(test_file))
        self.assertEqual(os.path.getsize(test_file), 0)  # Should be an empty file

    def test_update_existing_file(self):
        """Test updating an existing file with touch."""
        test_file = self.get_test_file_path("existing_file.txt")
        
        # Create the file
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Get the original modification time
        original_mtime = os.path.getmtime(test_file)
        
        # Wait a moment to ensure the timestamp will be different
        time.sleep(1)
        
        # Run touch
        exit_code = touch.main([test_file])
        
        # Check results
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(test_file))
        new_mtime = os.path.getmtime(test_file)
        self.assertNotEqual(original_mtime, new_mtime)
        self.assertGreater(new_mtime, original_mtime)

    def test_no_create_option(self):
        """Test the -c option to not create new files."""
        test_file = self.get_test_file_path("nonexistent_file.txt")
        
        # Make sure the file doesn't exist
        if os.path.exists(test_file):
            os.remove(test_file)
        
        # Run touch with -c
        exit_code = touch.main(["-c", test_file])
        
        # Check results
        self.assertEqual(exit_code, 0)
        self.assertFalse(os.path.exists(test_file))

    def test_access_time_only(self):
        """Test the -a option to update only access time."""
        test_file = self.get_test_file_path("access_time_test.txt")
        
        # Create the file
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Get the original times
        original_atime = os.path.getatime(test_file)
        original_mtime = os.path.getmtime(test_file)
        
        # Wait a moment to ensure the timestamp will be different
        time.sleep(1)
        
        # Run touch with -a
        exit_code = touch.main(["-a", test_file])
        
        # Check results
        self.assertEqual(exit_code, 0)
        new_atime = os.path.getatime(test_file)
        new_mtime = os.path.getmtime(test_file)
        self.assertNotEqual(original_atime, new_atime)
        self.assertGreater(new_atime, original_atime)
        # Modification time should remain unchanged
        self.assertAlmostEqual(original_mtime, new_mtime, places=2)

    def test_modification_time_only(self):
        """Test the -m option to update only modification time."""
        test_file = self.get_test_file_path("modification_time_test.txt")
        
        # Create the file
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Get the original times
        original_atime = os.path.getatime(test_file)
        original_mtime = os.path.getmtime(test_file)
        
        # Wait a moment to ensure the timestamp will be different
        time.sleep(1)
        
        # Run touch with -m
        exit_code = touch.main(["-m", test_file])
        
        # Check results
        self.assertEqual(exit_code, 0)
        new_atime = os.path.getatime(test_file)
        new_mtime = os.path.getmtime(test_file)
        # The atime might be updated by the test itself, so we can't reliably test for equality
        self.assertNotEqual(original_mtime, new_mtime)
        self.assertGreater(new_mtime, original_mtime)

    def test_reference_file_option(self):
        """Test the -r option to use another file's timestamps."""
        test_file = self.get_test_file_path("target_file.txt")
        reference_file = self.get_test_file_path("reference_file.txt")
        
        # Create the files with different times
        with open(test_file, 'w') as f:
            f.write("Target file")
        
        # Wait to ensure different timestamps
        time.sleep(1)
        
        with open(reference_file, 'w') as f:
            f.write("Reference file")
        
        # Get the reference file times
        ref_atime = os.path.getatime(reference_file)
        ref_mtime = os.path.getmtime(reference_file)
        
        # Run touch with -r
        exit_code = touch.main(["-r", reference_file, test_file])
        
        # Check results
        self.assertEqual(exit_code, 0)
        new_atime = os.path.getatime(test_file)
        new_mtime = os.path.getmtime(test_file)
        self.assertAlmostEqual(ref_atime, new_atime, places=2)
        self.assertAlmostEqual(ref_mtime, new_mtime, places=2)

    def test_date_option(self):
        """Test the -d option to use a specific date."""
        test_file = self.get_test_file_path("date_test.txt")
        
        # Create the file
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Use a specific date (2023-01-15 10:30:45)
        date_string = "2023-01-15 10:30:45"
        expected_timestamp = datetime(2023, 1, 15, 10, 30, 45).timestamp()
        
        # Run touch with -d
        exit_code = touch.main(["-d", date_string, test_file])
        
        # Check results
        self.assertEqual(exit_code, 0)
        new_atime = os.path.getatime(test_file)
        new_mtime = os.path.getmtime(test_file)
        self.assertAlmostEqual(expected_timestamp, new_atime, places=0)
        self.assertAlmostEqual(expected_timestamp, new_mtime, places=0)

    def test_timestamp_option(self):
        """Test the -t option to use a specific timestamp."""
        test_file = self.get_test_file_path("timestamp_test.txt")
        
        # Create the file
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Use a specific timestamp (January 15, 2023, 10:30:00)
        timestamp_string = "202301151030.00"
        expected_timestamp = datetime(2023, 1, 15, 10, 30, 0).timestamp()
        
        # Run touch with -t
        exit_code = touch.main(["-t", timestamp_string, test_file])
        
        # Check results
        self.assertEqual(exit_code, 0)
        new_atime = os.path.getatime(test_file)
        new_mtime = os.path.getmtime(test_file)
        self.assertAlmostEqual(expected_timestamp, new_atime, places=0)
        self.assertAlmostEqual(expected_timestamp, new_mtime, places=0)

    def test_multiple_files(self):
        """Test touching multiple files at once."""
        test_file1 = self.get_test_file_path("multiple1.txt")
        test_file2 = self.get_test_file_path("multiple2.txt")
        test_file3 = self.get_test_file_path("multiple3.txt")
        
        # Make sure the files don't exist
        for file_path in [test_file1, test_file2, test_file3]:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Run touch on multiple files
        exit_code = touch.main([test_file1, test_file2, test_file3])
        
        # Check results
        self.assertEqual(exit_code, 0)
        for file_path in [test_file1, test_file2, test_file3]:
            self.assertTrue(os.path.exists(file_path))
            self.assertEqual(os.path.getsize(file_path), 0)

    def test_error_nonexistent_reference(self):
        """Test error handling when reference file doesn't exist."""
        test_file = self.get_test_file_path("error_test.txt")
        nonexistent_ref = self.get_test_file_path("nonexistent_reference.txt")
        
        # Make sure the reference file doesn't exist
        if os.path.exists(nonexistent_ref):
            os.remove(nonexistent_ref)
        
        # Create the target file
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Run touch with -r and a nonexistent reference
        exit_code = touch.main(["-r", nonexistent_ref, test_file])
        
        # Check results
        self.assertEqual(exit_code, 1)
        stderr_output = sys.stderr.getvalue()
        self.assertIn("failed to get attributes", stderr_output.lower())

    def test_error_invalid_date(self):
        """Test error handling when date format is invalid."""
        test_file = self.get_test_file_path("error_test.txt")
        
        # Create the target file
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Run touch with -d and an invalid date
        exit_code = touch.main(["-d", "not-a-valid-date", test_file])
        
        # Check results
        self.assertEqual(exit_code, 1)
        stderr_output = sys.stderr.getvalue()
        self.assertIn("invalid date format", stderr_output.lower())

    def test_error_invalid_timestamp(self):
        """Test error handling when timestamp format is invalid."""
        test_file = self.get_test_file_path("error_test.txt")
        
        # Create the target file
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Run touch with -t and an invalid timestamp
        exit_code = touch.main(["-t", "123", test_file])
        
        # Check results
        self.assertEqual(exit_code, 1)
        stderr_output = sys.stderr.getvalue()
        self.assertIn("invalid timestamp format", stderr_output.lower())


@unittest.skipIf(os.environ.get('SKIP_REFERENCE_TESTS'), "Reference tests skipped")
class ReferenceTouchTests(unittest.TestCase):
    """Test PyKnife touch implementation against the system touch command."""
    
    def setUp(self):
        """Set up for reference tests."""
        self.test_dir = tempfile.mkdtemp()
        self.test_files = []

    def tearDown(self):
        """Clean up after reference tests."""
        for file_path in self.test_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
        
        try:
            os.rmdir(self.test_dir)
        except OSError:
            pass

    def get_test_file_path(self, filename):
        """Get path for a test file."""
        path = os.path.join(self.test_dir, filename)
        self.test_files.append(path)
        return path

    def test_reference_basic(self):
        """Compare basic touch with system command."""
        test_file = self.get_test_file_path("ref_test.txt")
        
        # Define a basic touch command
        args = [test_file]
        
        # Compare PyKnife implementation with system command
        # Note: We can't compare stdout/stderr as touch doesn't print anything on success
        result = compare_with_system("touch", args, touch.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'touch' not available: {result['error']}")
        
        # Check if both the PyKnife and system implementations created the file
        self.assertTrue(os.path.exists(test_file))
        
    def test_reference_no_create(self):
        """Compare touch -c with system command."""
        test_file = self.get_test_file_path("ref_no_create.txt")
        
        # Make sure the file doesn't exist
        if os.path.exists(test_file):
            os.remove(test_file)
        
        # Define touch command with -c option
        args = ["-c", test_file]
        
        # Compare PyKnife implementation with system command
        result = compare_with_system("touch", args, touch.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'touch' not available: {result['error']}")
        
        # The file should not exist after touch -c
        self.assertFalse(os.path.exists(test_file))


if __name__ == "__main__":
    unittest.main() 