#!/usr/bin/env python3
"""
Tests for the tail command.
"""

import sys
import os
import unittest
import tempfile
import threading
import time
from io import StringIO
from src.commands import tail
from src.testing.reference_tester import compare_with_system


class TestTail(unittest.TestCase):
    """Test cases for the tail command."""

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
        """Create temporary test files for testing tail."""
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
        
        # Binary file with 100 bytes
        binary_content = bytes(range(100))
        self.binary_file = self.create_temp_file(
            "binary.bin",
            binary_content,
            binary=True
        )
        
        # File for follow testing
        self.follow_file = self.create_temp_file(
            "follow.txt",
            "Initial content\n"
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
        """Test tail with default settings (last 10 lines)."""
        tail.main([self.twenty_lines_file])
        expected = "\n".join(f"Line {i}" for i in range(11, 21)) + "\n"
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_lines_option(self):
        """Test tail with -n option to specify number of lines."""
        tail.main(["-n", "5", self.twenty_lines_file])
        expected = "\n".join(f"Line {i}" for i in range(16, 21)) + "\n"
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_bytes_option(self):
        """Test tail with -c option to specify number of bytes."""
        # Since binary content can be tricky to test with stdout,
        # we'll use a simple text file and count bytes
        tail.main(["-c", "10", self.five_lines_file])
        self.assertEqual(len(sys.stdout.getvalue()), 10)

    def test_multiple_files(self):
        """Test tail with multiple files."""
        tail.main([self.five_lines_file, self.twenty_lines_file])
        
        # Expected output should have headers and content from both files
        expected = f"==> {self.five_lines_file} <==\n"
        expected += "\n".join(f"Short line {i}" for i in range(1, 6)) + "\n"
        expected += f"\n==> {self.twenty_lines_file} <==\n"
        expected += "\n".join(f"Line {i}" for i in range(11, 21)) + "\n"
        
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_quiet_option(self):
        """Test tail with -q option to suppress headers."""
        tail.main(["-q", self.five_lines_file, self.twenty_lines_file])
        
        # Expected output should NOT have headers
        expected = "\n".join(f"Short line {i}" for i in range(1, 6)) + "\n"
        expected += "\n".join(f"Line {i}" for i in range(11, 21)) + "\n"
        
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_verbose_option(self):
        """Test tail with -v option to always show headers."""
        tail.main(["-v", self.five_lines_file])
        
        # Expected output should have headers even for a single file
        expected = f"==> {self.five_lines_file} <==\n"
        expected += "\n".join(f"Short line {i}" for i in range(1, 6)) + "\n"
        
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_positive_line_number(self):
        """Test tail with +N line number to start at line N."""
        tail.main(["-n", "+15", self.twenty_lines_file])
        expected = "\n".join(f"Line {i}" for i in range(15, 21)) + "\n"
        self.assertEqual(sys.stdout.getvalue(), expected)

    def test_positive_byte_number(self):
        """Test tail with +N byte number to start at byte N."""
        # Create a file with known content for this test
        content = "0123456789abcdefghij"
        test_file = self.create_temp_file("positive_byte.txt", content)
        
        tail.main(["-c", "+11", test_file])
        self.assertEqual(sys.stdout.getvalue(), "abcdefghij")

    def test_follow_option(self):
        """Test tail with -f option to follow file updates."""
        # This test simulates file updates in a separate thread
        follow_output = []
        
        # Create a thread to capture output
        def capture_output():
            # Store original stdout
            original_stdout = sys.stdout
            output_capture = StringIO()
            sys.stdout = output_capture
            
            # Create a thread to append to the file after a delay
            def append_to_file():
                time.sleep(0.2)  # Wait for tail to start following
                with open(self.follow_file, "a") as f:
                    f.write("New line 1\n")
                time.sleep(0.1)  # Wait between writes
                with open(self.follow_file, "a") as f:
                    f.write("New line 2\n")
                time.sleep(0.1)  # Wait to ensure tail sees the changes
            
            # Start the file appender thread
            append_thread = threading.Thread(target=append_to_file)
            append_thread.daemon = True
            append_thread.start()
            
            # Run tail with follow for a limited time
            def run_tail():
                # Patch the follow_file function to exit after a short time
                original_follow = tail.follow_file
                def mock_follow(file_path, callback):
                    stop_time = time.time() + 0.5  # Follow for 0.5 seconds
                    with open(file_path, "rb") as f:
                        f.seek(os.path.getsize(file_path))
                        while time.time() < stop_time:
                            line = f.readline()
                            if line:
                                callback(line)
                            time.sleep(0.05)
                
                # Replace the follow function temporarily
                tail.follow_file = mock_follow
                try:
                    tail.main(["-f", self.follow_file])
                finally:
                    # Restore the original follow function
                    tail.follow_file = original_follow
            
            # Run tail
            run_tail()
            
            # Restore stdout and return the captured output
            result = output_capture.getvalue()
            sys.stdout = original_stdout
            follow_output.append(result)
        
        # Run the capture in a thread
        capture_thread = threading.Thread(target=capture_output)
        capture_thread.daemon = True
        capture_thread.start()
        capture_thread.join(timeout=1.0)  # Wait up to 1 second for the thread to finish
        
        # Check the output
        if follow_output:
            output = follow_output[0]
            self.assertTrue("Initial content" in output)
            self.assertTrue("New line 1" in output)
            self.assertTrue("New line 2" in output)

    def test_nonexistent_file(self):
        """Test tail with a non-existent file."""
        # Redirect stderr temporarily
        original_stderr = sys.stderr
        sys.stderr = StringIO()
        
        exit_code = tail.main(["nonexistent_file.txt"])
        
        # Restore stderr
        stderr_output = sys.stderr.getvalue()
        sys.stderr = original_stderr
        
        self.assertEqual(exit_code, 1)
        self.assertTrue("nonexistent_file.txt" in stderr_output)


@unittest.skipIf(os.environ.get('SKIP_REFERENCE_TESTS'), "Reference tests skipped")
class ReferenceTailTests(unittest.TestCase):
    """Test PyKnife tail implementation against the system tail command."""
    
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
        """Compare basic tail with system command."""
        args = [self.test_file]
        result = compare_with_system("tail", args, tail.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'tail' not available: {result['error']}")
        
        self.assertTrue(
            result['match'], 
            f"Output mismatch:\nPyKnife: {repr(result['pyknife_output'])}\n"
            f"System: {repr(result['system_output'])}"
        )
    
    def test_reference_lines(self):
        """Compare tail -n with system command."""
        args = ["-n", "5", self.test_file]
        result = compare_with_system("tail", args, tail.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'tail' not available: {result['error']}")
        
        self.assertTrue(
            result['match'], 
            f"Output mismatch:\nPyKnife: {repr(result['pyknife_output'])}\n"
            f"System: {repr(result['system_output'])}"
        )


if __name__ == "__main__":
    unittest.main() 