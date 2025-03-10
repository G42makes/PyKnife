#!/usr/bin/env python3
"""
Tests for the echo command.
"""

import sys
import os
import unittest
from io import StringIO
from src.commands import echo
from src.testing.reference_tester import compare_with_system


class TestEcho(unittest.TestCase):
    """Test cases for the echo command."""

    def setUp(self):
        """Set up for tests."""
        self.original_stdout = sys.stdout
        sys.stdout = StringIO()

    def tearDown(self):
        """Clean up after tests."""
        sys.stdout = self.original_stdout

    def test_basic_echo(self):
        """Test basic echo functionality."""
        echo.main(["Hello", "World"])
        self.assertEqual(sys.stdout.getvalue(), "Hello World\n")

    def test_no_newline(self):
        """Test echo with -n option."""
        echo.main(["-n", "No", "newline"])
        self.assertEqual(sys.stdout.getvalue(), "No newline")

    def test_escape_sequences(self):
        """Test echo with -e option."""
        echo.main(["-e", "Tab:\\t Newline:\\n"])
        self.assertEqual(sys.stdout.getvalue(), "Tab:\t Newline:\n\n")

    def test_disable_escapes(self):
        """Test echo with -E option."""
        # The -e comes before -E, so -E takes precedence
        echo.main(["-e", "-E", "No\\tescapes"])
        # The tab escape sequence should NOT be processed when -E comes after -e
        self.assertEqual(sys.stdout.getvalue(), "No\\tescapes\n")

    def test_e_overrides_E(self):
        """Test that -e overrides -E when it comes after."""
        echo.main(["-E", "-e", "Escapes\\twork"])
        # The tab escape sequence should be processed when -e comes after -E
        self.assertEqual(sys.stdout.getvalue(), "Escapes\twork\n")


@unittest.skipIf(os.environ.get('SKIP_REFERENCE_TESTS'), "Reference tests skipped")
class ReferenceEchoTests(unittest.TestCase):
    """Test PyKnife echo implementation against the system echo command."""
    
    def test_reference_basic(self):
        """Compare basic echo with system command."""
        args = ["Hello", "World"]
        result = compare_with_system("echo", args, echo.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'echo' not available: {result['error']}")
        
        self.assertTrue(
            result['match'], 
            f"Output mismatch:\nPyKnife: {repr(result['pyknife_output'])}\n"
            f"System: {repr(result['system_output'])}"
        )
    
    def test_reference_newline(self):
        """Compare echo -n with system command."""
        args = ["-n", "No", "newline"]
        result = compare_with_system("echo", args, echo.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'echo' not available: {result['error']}")
            
        # Note: Some systems may not support -n, so we check stderr
        if result['system_stderr'] and "illegal option" in result['system_stderr']:
            self.skipTest("System echo does not support -n option")
            
        self.assertTrue(
            result['match'], 
            f"Output mismatch:\nPyKnife: {repr(result['pyknife_output'])}\n"
            f"System: {repr(result['system_output'])}"
        )
    
    def test_reference_escape(self):
        """Compare echo -e with system command."""
        args = ["-e", "Tab:\\t Newline:\\n"]
        result = compare_with_system("echo", args, echo.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'echo' not available: {result['error']}")
            
        # Note: Some systems may not support -e, so we check stderr
        if result['system_stderr'] and "illegal option" in result['system_stderr']:
            self.skipTest("System echo does not support -e option")
            
        self.assertTrue(
            result['match'], 
            f"Output mismatch:\nPyKnife: {repr(result['pyknife_output'])}\n"
            f"System: {repr(result['system_output'])}"
        )


if __name__ == "__main__":
    unittest.main() 