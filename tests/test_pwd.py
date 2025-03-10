#!/usr/bin/env python3
"""
Tests for the pwd command.
"""

import sys
import os
import unittest
from io import StringIO
from src.commands import pwd
from src.testing.reference_tester import compare_with_system


class TestPwd(unittest.TestCase):
    """Test cases for the pwd command."""

    def setUp(self):
        """Set up for tests."""
        self.original_stdout = sys.stdout
        sys.stdout = StringIO()

    def tearDown(self):
        """Clean up after tests."""
        sys.stdout = self.original_stdout

    def test_basic_pwd(self):
        """Test basic pwd functionality."""
        pwd.main([])
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, os.getcwd())
    
    def test_physical_pwd(self):
        """Test pwd with -P option (physical path)."""
        pwd.main(["-P"])
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, os.path.realpath(os.getcwd()))
    
    def test_logical_pwd(self):
        """Test pwd with -L option (logical path)."""
        pwd.main(["-L"])
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, os.getcwd())


@unittest.skipIf(os.environ.get('SKIP_REFERENCE_TESTS'), "Reference tests skipped")
class ReferencePwdTests(unittest.TestCase):
    """Test PyKnife pwd implementation against the system pwd command."""
    
    def test_reference_basic(self):
        """Compare basic pwd with system command."""
        args = []
        result = compare_with_system("pwd", args, pwd.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'pwd' not available: {result['error']}")
        
        self.assertTrue(
            result['match'], 
            f"Output mismatch:\nPyKnife: {repr(result['pyknife_output'])}\n"
            f"System: {repr(result['system_output'])}"
        )
    
    def test_reference_physical(self):
        """Compare pwd -P with system command."""
        args = ["-P"]
        result = compare_with_system("pwd", args, pwd.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'pwd' not available: {result['error']}")
        
        self.assertTrue(
            result['match'], 
            f"Output mismatch:\nPyKnife: {repr(result['pyknife_output'])}\n"
            f"System: {repr(result['system_output'])}"
        )


if __name__ == "__main__":
    unittest.main() 