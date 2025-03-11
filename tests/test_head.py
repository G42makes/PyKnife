#!/usr/bin/env python3
"""
Tests for the head command.
"""

import sys
import os
import unittest
import tempfile
from io import StringIO
from src.commands import head
from src.testing.reference_tester import compare_with_system


class TestHead(unittest.TestCase):
    """Test cases for the head command."""

    def setUp(self):
        """Set up for tests."""
        # Redirect stdout
        self.original_stdout = sys.stdout
        sys.stdout = StringIO()
        
        # Create temporary test files
        self.temp_files = []
        self.create_test_files()

    def tearDown(self):
        """Clean up after tests."""
        # Restore stdout
        sys.stdout = self.original_stdout
        
        # Clean up temporary files
        for file_path in self.temp_files:
            if os.path.exists(file_path):
                os.remove(file_path)

    def create_test_files(self):
        """Create temporary test files for testing head."""
        # File with 20 lines
        content = "\n".join(f"Line {i}" for i in range(1, 21))
        self.twenty_lines_file = self.create_temp_file(
            "twenty_lines.txt",
            content + "\n"
        )
        
        # File with 5 lines
        content = "\n".join(f"Short line {i}" for i in range(1, 6))
        self.five_lines_file = self.create_temp_file(
            "five_lines.txt",
            content + "\n"
        )
        
        # Text file for byte testing
        self.text_for_bytes = self.create_temp_file(
            "bytes_test.txt",
            "This is exactly 30 bytes long.\n"
        )
        
        # Binary file with 100 bytes
        binary_content = bytes(range(100))
        self.binary_file = self.create_temp_file(
            "binary.bin",
            binary_content,
            binary=True
        )

    def create_temp_file(self, name, content, binary=False):
        """Create a temporary file with given content."""
        fd, path = tempfile.mkstemp(suffix=name)
        os.close(fd)
        
        mode = "wb" if binary else "w"
        with open(path, mode) as f:
            f.write(content)
        
        self.temp_files.append(path)
        return path

    def test_default_behavior(self):
        """Test head with default settings (first 10 lines)."""
        head.main([self.twenty_lines_file])
        expected = "\n".join(f"Line {i}" for i in range(1, 11)) + "\n"
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_lines_option(self):
        """Test head with -n option to specify number of lines."""
        head.main(["-n", "5", self.twenty_lines_file])
        expected = "\n".join(f"Line {i}" for i in range(1, 6)) + "\n"
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_bytes_option(self):
        """Test head with -c option to specify number of bytes."""
        head.main(["-c", "20", self.text_for_bytes])
        self.assertEqual(sys.stdout.getvalue(), "This is exactly 30 b")

    def test_multiple_files(self):
        """Test head with multiple files."""
        head.main([self.five_lines_file, self.twenty_lines_file])
        
        # Expected output should have headers and content from both files
        expected = f"==> {self.five_lines_file} <==\n"
        expected += "\n".join(f"Short line {i}" for i in range(1, 6)) + "\n"
        expected += f"\n==> {self.twenty_lines_file} <==\n"
        expected += "\n".join(f"Line {i}" for i in range(1, 11)) + "\n"
        
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_quiet_option(self):
        """Test head with -q option to suppress headers."""
        head.main(["-q", self.five_lines_file, self.twenty_lines_file])
        
        # Expected output should NOT have headers
        expected = "\n".join(f"Short line {i}" for i in range(1, 6)) + "\n"
        expected += "\n".join(f"Line {i}" for i in range(1, 11)) + "\n"
        
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_verbose_option(self):
        """Test head with -v option to always show headers."""
        head.main(["-v", self.five_lines_file])
        
        # Expected output should have headers even for a single file
        expected = f"==> {self.five_lines_file} <==\n"
        expected += "\n".join(f"Short line {i}" for i in range(1, 6)) + "\n"
        
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_nonexistent_file(self):
        """Test head with a non-existent file."""
        # Redirect stderr temporarily
        original_stderr = sys.stderr
        sys.stderr = StringIO()
        
        exit_code = head.main(["nonexistent_file.txt"])
        
        # Restore stderr
        stderr_output = sys.stderr.getvalue()
        sys.stderr = original_stderr
        
        self.assertEqual(exit_code, 1)
        self.assertTrue("nonexistent_file.txt" in stderr_output)


@unittest.skipIf(os.environ.get('SKIP_REFERENCE_TESTS'), "Reference tests skipped")
class ReferenceHeadTests(unittest.TestCase):
    """Test PyKnife head implementation against the system head command."""
    
    def setUp(self):
        """Set up for reference tests."""
        self.temp_files = []
        
        # Create a file with 20 lines
        content = "\n".join(f"Line {i}" for i in range(1, 21))
        self.test_file = self.create_temp_file(
            "test_file.txt",
            content + "\n"
        )

    def tearDown(self):
        """Clean up after tests."""
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
        """Compare basic head with system command."""
        args = [self.test_file]
        result = compare_with_system("head", args, head.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'head' not available: {result['error']}")
        
        self.assertTrue(
            result['match'], 
            f"Output mismatch:\nPyKnife: {repr(result['pyknife_output'])}\n"
            f"System: {repr(result['system_output'])}"
        )
    
    def test_reference_lines(self):
        """Compare head -n with system command."""
        args = ["-n", "5", self.test_file]
        result = compare_with_system("head", args, head.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'head' not available: {result['error']}")
        
        self.assertTrue(
            result['match'], 
            f"Output mismatch:\nPyKnife: {repr(result['pyknife_output'])}\n"
            f"System: {repr(result['system_output'])}"
        )


if __name__ == "__main__":
    unittest.main() 