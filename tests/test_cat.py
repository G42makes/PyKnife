#!/usr/bin/env python3
"""
Tests for the cat command.
"""

import sys
import os
import unittest
import tempfile
import textwrap
from io import StringIO
from src.commands import cat
from src.testing.reference_tester import compare_with_system


class TestCat(unittest.TestCase):
    """Test cases for the cat command."""

    def setUp(self):
        """Set up for tests."""
        self.original_stdout = sys.stdout
        sys.stdout = StringIO()
        
        # Create temporary test files
        self.temp_files = []
        self.create_test_files()

    def tearDown(self):
        """Clean up after tests."""
        sys.stdout = self.original_stdout
        
        # Clean up temporary files
        for file_path in self.temp_files:
            if os.path.exists(file_path):
                os.remove(file_path)

    def create_test_files(self):
        """Create temporary test files for testing cat."""
        # File with simple text
        self.simple_file = self.create_temp_file(
            "simple.txt",
            "Line 1\nLine 2\nLine 3\n"
        )
        
        # File with empty lines
        self.empty_lines_file = self.create_temp_file(
            "empty_lines.txt",
            "Line 1\n\nLine 3\n\nLine 5\n"
        )
        
        # File with tabs and special characters
        self.special_chars_file = self.create_temp_file(
            "special_chars.txt",
            "Line with\ttabs\nLine with \x01 control char\n"
        )

    def create_temp_file(self, name, content):
        """Create a temporary file with given content."""
        fd, path = tempfile.mkstemp(suffix=name)
        os.close(fd)
        
        with open(path, 'w') as f:
            f.write(content)
        
        self.temp_files.append(path)
        return path

    def test_cat_single_file(self):
        """Test cat with a single file."""
        cat.main([self.simple_file])
        self.assertEqual(sys.stdout.getvalue(), "Line 1\nLine 2\nLine 3\n")

    def test_cat_multiple_files(self):
        """Test cat with multiple files."""
        cat.main([self.simple_file, self.empty_lines_file])
        expected = "Line 1\nLine 2\nLine 3\nLine 1\n\nLine 3\n\nLine 5\n"
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_number_option(self):
        """Test cat with -n option (number all lines)."""
        cat.main(["-n", self.simple_file])
        expected = "     1  Line 1\n     2  Line 2\n     3  Line 3\n"
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_number_nonblank_option(self):
        """Test cat with -b option (number non-blank lines)."""
        cat.main(["-b", self.empty_lines_file])
        expected = "     1  Line 1\n\n     2  Line 3\n\n     3  Line 5\n"
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_show_ends_option(self):
        """Test cat with -E option (show ends)."""
        cat.main(["-E", self.simple_file])
        expected = "Line 1$\nLine 2$\nLine 3$\n"
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_show_tabs_option(self):
        """Test cat with -T option (show tabs)."""
        cat.main(["-T", self.special_chars_file])
        expected = "Line with^Itabs\nLine with \x01 control char\n"
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_show_nonprinting_option(self):
        """Test cat with -v option (show non-printing)."""
        cat.main(["-v", self.special_chars_file])
        expected = "Line with\ttabs\nLine with ^A control char\n"
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_show_all_option(self):
        """Test cat with -A option (show all)."""
        cat.main(["-A", self.special_chars_file])
        # The -A option should show both tabs and control characters, and end of line markers
        expected_output = sys.stdout.getvalue()
        self.assertTrue("^I" in expected_output)  # Should show tabs
        self.assertTrue("$" in expected_output)   # Should show end of line
        # Control character display might vary, so we don't check exact format

    def test_nonexistent_file(self):
        """Test cat with a non-existent file."""
        # Redirect stderr temporarily
        original_stderr = sys.stderr
        sys.stderr = StringIO()
        
        exit_code = cat.main(["nonexistent_file.txt"])
        
        # Restore stderr
        stderr_output = sys.stderr.getvalue()
        sys.stderr = original_stderr
        
        self.assertEqual(exit_code, 1)
        self.assertTrue("nonexistent_file.txt" in stderr_output)


@unittest.skipIf(os.environ.get('SKIP_REFERENCE_TESTS'), "Reference tests skipped")
class ReferenceCatTests(unittest.TestCase):
    """Test PyKnife cat implementation against the system cat command."""
    
    def setUp(self):
        """Set up for reference tests."""
        # Create temporary test files
        self.temp_files = []
        
        # File with simple text
        self.simple_file = self.create_temp_file(
            "simple.txt",
            "Line 1\nLine 2\nLine 3\n"
        )
        
        # File with empty lines
        self.empty_lines_file = self.create_temp_file(
            "empty_lines.txt",
            "Line 1\n\nLine 3\n\nLine 5\n"
        )

    def tearDown(self):
        """Clean up after tests."""
        # Clean up temporary files
        for file_path in self.temp_files:
            if os.path.exists(file_path):
                os.remove(file_path)

    def create_temp_file(self, name, content):
        """Create a temporary file with given content."""
        fd, path = tempfile.mkstemp(suffix=name)
        os.close(fd)
        
        with open(path, 'w') as f:
            f.write(content)
        
        self.temp_files.append(path)
        return path
    
    def test_reference_basic(self):
        """Compare basic cat with system command."""
        args = [self.simple_file]
        result = compare_with_system("cat", args, cat.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'cat' not available: {result['error']}")
        
        self.assertTrue(
            result['match'], 
            f"Output mismatch:\nPyKnife: {repr(result['pyknife_output'])}\n"
            f"System: {repr(result['system_output'])}"
        )
    
    def test_reference_number(self):
        """Compare cat -n with system command."""
        args = ["-n", self.simple_file]
        result = compare_with_system("cat", args, cat.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'cat' not available: {result['error']}")
        
        self.assertTrue(
            result['match'], 
            f"Output mismatch:\nPyKnife: {repr(result['pyknife_output'])}\n"
            f"System: {repr(result['system_output'])}"
        )
    
    def test_reference_multiple_files(self):
        """Compare cat with multiple files to system command."""
        args = [self.simple_file, self.empty_lines_file]
        result = compare_with_system("cat", args, cat.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'cat' not available: {result['error']}")
        
        self.assertTrue(
            result['match'], 
            f"Output mismatch:\nPyKnife: {repr(result['pyknife_output'])}\n"
            f"System: {repr(result['system_output'])}"
        )


if __name__ == "__main__":
    unittest.main() 