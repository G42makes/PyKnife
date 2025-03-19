#!/usr/bin/env python3
"""
Tests for the wc command.
"""

import sys
import os
import unittest
import tempfile
from io import StringIO
from src.commands import wc
from src.testing.reference_tester import compare_with_system


class TestWc(unittest.TestCase):
    """Test cases for the wc command."""

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
        """Create temporary test files for testing wc."""
        # Create a file with known content for precise testing
        content = "This file has 3 lines,\n15 words,\nand a max line length of 39 characters.\n"
        self.known_file = self.create_temp_file("known.txt", content)
        
        # Store the expected counts for the known file
        # Note: Character count will vary by platform due to CRLF vs LF line endings
        self.expected_lines = 3
        self.expected_words = 15  # Actually 15 words: This(1) file(2) has(3) 3(4) lines,(5) 15(6) words,(7) and(8) a(9) max(10) line(11) length(12) of(13) 39(14) characters.(15)
        self.expected_chars = len(content)  # Will be platform-dependent
        self.expected_max_length = 39  # "and a max line length of 39 characters."
        
        # File with specific counts for regular testing
        self.test_file = self.create_temp_file(
            "test.txt",
            "This file has several lines.\nIt is used for testing the wc command.\nLet's see if it counts correctly.\n"
        )
        
        # Empty file
        self.empty_file = self.create_temp_file(
            "empty.txt",
            ""
        )
        
        # File with empty lines
        self.empty_lines_file = self.create_temp_file(
            "empty_lines.txt",
            "Line 1\n\nLine 3\n\nLine 5\n"
        )
        
        # Binary file 
        binary_content = bytes(range(50))
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
        """Test wc with default settings (count lines, words, bytes)."""
        wc.main([self.known_file])
        output = sys.stdout.getvalue().strip()
        
        # Extract the counts (ignore the filename part)
        counts = output.split()[:3]
        
        # Convert to integers for comparison
        line_count, word_count, byte_count = map(int, counts)
        
        self.assertEqual(line_count, self.expected_lines)
        self.assertEqual(word_count, self.expected_words)
        # Byte count might vary by platform due to line endings
        # so we'll just check it's reasonable
        self.assertTrue(byte_count > 0)

    def test_lines_option(self):
        """Test wc with -l option to count lines only."""
        wc.main(["-l", self.known_file])
        output = sys.stdout.getvalue().strip()
        
        line_count = int(output.split()[0])
        self.assertEqual(line_count, self.expected_lines)

    def test_words_option(self):
        """Test wc with -w option to count words only."""
        wc.main(["-w", self.known_file])
        output = sys.stdout.getvalue().strip()
        
        word_count = int(output.split()[0])
        self.assertEqual(word_count, self.expected_words)

    def test_bytes_option(self):
        """Test wc with -c option to count bytes only."""
        wc.main(["-c", self.known_file])
        output = sys.stdout.getvalue().strip()
        
        byte_count = int(output.split()[0])
        # Verify byte count is reasonable (but exact value may vary by platform)
        self.assertTrue(byte_count > 0)

    def test_chars_option(self):
        """Test wc with -m option to count characters only."""
        wc.main(["-m", self.known_file])
        output = sys.stdout.getvalue().strip()
        
        char_count = int(output.split()[0])
        self.assertEqual(char_count, self.expected_chars)

    def test_max_line_length_option(self):
        """Test wc with -L option to show max line length."""
        wc.main(["-L", self.known_file])
        output = sys.stdout.getvalue().strip()
        
        max_length = int(output.split()[0])
        self.assertEqual(max_length, self.expected_max_length)

    def test_multiple_options(self):
        """Test wc with multiple options."""
        wc.main(["-l", "-w", self.known_file])
        output = sys.stdout.getvalue().strip()
        
        line_count, word_count = map(int, output.split()[:2])
        self.assertEqual(line_count, self.expected_lines)
        self.assertEqual(word_count, self.expected_words)

    def test_empty_file(self):
        """Test wc with an empty file."""
        wc.main([self.empty_file])
        output = sys.stdout.getvalue().strip()
        
        # Extract the counts (ignore the filename part)
        counts = output.split()[:3]
        
        # Convert to integers for comparison
        line_count, word_count, byte_count = map(int, counts)
        
        self.assertEqual(line_count, 0)
        self.assertEqual(word_count, 0)
        self.assertEqual(byte_count, 0)

    def test_multiple_files(self):
        """Test wc with multiple files."""
        wc.main([self.test_file, self.empty_lines_file])
        
        # Output should have three lines: results for each file and a total
        lines = sys.stdout.getvalue().strip().split('\n')
        self.assertEqual(len(lines), 3)
        
        # Check that "total" appears in the last line
        self.assertTrue("total" in lines[2])

    def test_nonexistent_file(self):
        """Test wc with a non-existent file."""
        # Redirect stderr temporarily
        original_stderr = sys.stderr
        sys.stderr = StringIO()
        
        exit_code = wc.main(["nonexistent_file.txt"])
        
        # Restore stderr
        stderr_output = sys.stderr.getvalue()
        sys.stderr = original_stderr
        
        self.assertEqual(exit_code, 1)
        self.assertTrue("nonexistent_file.txt" in stderr_output)


@unittest.skipIf(os.environ.get('SKIP_REFERENCE_TESTS'), "Reference tests skipped")
class ReferenceWcTests(unittest.TestCase):
    """Test PyKnife wc implementation against the system wc command."""
    
    def setUp(self):
        """Set up for reference tests."""
        # Create temporary test files
        self.temp_files = []
        
        # Create a test file with content
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"
        self.test_file = self.create_temp_file("test_wc.txt", content)
    
    def tearDown(self):
        """Clean up after reference tests."""
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
        """Compare basic wc with system command."""
        args = [self.test_file]
        result = compare_with_system("wc", args, wc.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'wc' not available: {result['error']}")
        
        # Normalize whitespace for comparison - the actual counts are the important part
        def normalize(text):
            # Split by whitespace and filename, extract the numbers
            parts = text.strip().split()
            if len(parts) >= 4:  # Has line count, word count, byte count, filename
                numbers = parts[:3]
                return [int(n) for n in numbers]
            return text
        
        pyknife_nums = normalize(result['pyknife_output'])
        system_nums = normalize(result['system_output'])
        
        self.assertEqual(
            pyknife_nums, system_nums,
            f"Count mismatch:\nPyKnife: {repr(result['pyknife_output'])}\n"
            f"System: {repr(result['system_output'])}"
        )
    
    def test_reference_count_lines(self):
        """Compare wc -l with system command."""
        args = ["-l", self.test_file]
        result = compare_with_system("wc", args, wc.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'wc' not available: {result['error']}")
        
        # Normalize whitespace for comparison
        def normalize(text):
            parts = text.strip().split()
            if len(parts) >= 2:  # Has line count and filename
                return int(parts[0])
            return text
        
        pyknife_num = normalize(result['pyknife_output'])
        system_num = normalize(result['system_output'])
        
        self.assertEqual(
            pyknife_num, system_num,
            f"Count mismatch:\nPyKnife: {repr(result['pyknife_output'])}\n"
            f"System: {repr(result['system_output'])}"
        )
    
    def test_reference_count_words(self):
        """Compare wc -w with system command."""
        args = ["-w", self.test_file]
        result = compare_with_system("wc", args, wc.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'wc' not available: {result['error']}")
        
        # Normalize whitespace for comparison
        def normalize(text):
            parts = text.strip().split()
            if len(parts) >= 2:  # Has word count and filename
                return int(parts[0])
            return text
        
        pyknife_num = normalize(result['pyknife_output'])
        system_num = normalize(result['system_output'])
        
        self.assertEqual(
            pyknife_num, system_num,
            f"Count mismatch:\nPyKnife: {repr(result['pyknife_output'])}\n"
            f"System: {repr(result['system_output'])}"
        )
    
    def test_reference_count_chars(self):
        """Compare wc -c with system command."""
        args = ["-c", self.test_file]
        result = compare_with_system("wc", args, wc.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'wc' not available: {result['error']}")
        
        # Normalize whitespace for comparison
        def normalize(text):
            parts = text.strip().split()
            if len(parts) >= 2:  # Has char count and filename
                return int(parts[0])
            return text
        
        pyknife_num = normalize(result['pyknife_output'])
        system_num = normalize(result['system_output'])
        
        self.assertEqual(
            pyknife_num, system_num,
            f"Count mismatch:\nPyKnife: {repr(result['pyknife_output'])}\n"
            f"System: {repr(result['system_output'])}"
        )


if __name__ == "__main__":
    unittest.main() 