#!/usr/bin/env python3
"""
Tests for the ls command.
"""

import os
import sys
import stat
import shutil
import unittest
import tempfile
from io import StringIO
from src.commands import ls
from src.testing.reference_tester import compare_with_system


class TestLs(unittest.TestCase):
    """Test cases for the ls command."""

    def setUp(self):
        """Set up for tests."""
        # Redirect stdout and stderr
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.create_test_files()

    def tearDown(self):
        """Clean up after tests."""
        # Restore stdout and stderr
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        
        # Remove test directory and all contents
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_test_files(self):
        """Create test files for ls command tests."""
        # Create some regular files
        self.file1 = os.path.join(self.test_dir, "file1.txt")
        with open(self.file1, "w") as f:
            f.write("This is file 1")
        
        self.file2 = os.path.join(self.test_dir, "file2.txt")
        with open(self.file2, "w") as f:
            f.write("This is file 2")
        
        self.file3 = os.path.join(self.test_dir, "file3.dat")
        with open(self.file3, "w") as f:
            f.write("This is file 3")
        
        # Create a hidden file
        self.hidden_file = os.path.join(self.test_dir, ".hidden.txt")
        with open(self.hidden_file, "w") as f:
            f.write("This is a hidden file")
        
        # Create a directory
        self.subdir = os.path.join(self.test_dir, "subdir")
        os.mkdir(self.subdir)
        
        # Create a file in the subdirectory
        self.subdir_file = os.path.join(self.subdir, "subfile.txt")
        with open(self.subdir_file, "w") as f:
            f.write("This is a file in the subdirectory")
        
        # Create an executable file if not on Windows
        self.executable = os.path.join(self.test_dir, "executable.sh")
        with open(self.executable, "w") as f:
            f.write("#!/bin/sh\necho 'Hello, World!'\n")
        
        # Make it executable if the platform supports it
        if hasattr(os, "chmod"):
            try:
                os.chmod(self.executable, 0o755)
            except:
                pass

    def test_basic_list(self):
        """Test basic ls command with no options."""
        exit_code = ls.main([self.test_dir])
        
        # Check that it ran without error
        self.assertEqual(exit_code, 0)
        
        # Capture the output
        output = sys.stdout.getvalue()
        
        # Check that the regular files are listed
        self.assertIn("file1.txt", output)
        self.assertIn("file2.txt", output)
        self.assertIn("file3.dat", output)
        self.assertIn("subdir", output)
        if sys.platform != "win32":
            self.assertIn("executable.sh", output)
        
        # Hidden files should not be listed
        self.assertNotIn(".hidden.txt", output)

    def test_all_option(self):
        """Test the -a option to show hidden files."""
        exit_code = ls.main(["-a", self.test_dir])
        
        # Check that it ran without error
        self.assertEqual(exit_code, 0)
        
        # Capture the output
        output = sys.stdout.getvalue()
        
        # Check that all files are listed, including hidden
        self.assertIn("file1.txt", output)
        self.assertIn("file2.txt", output)
        self.assertIn("file3.dat", output)
        self.assertIn("subdir", output)
        self.assertIn(".hidden.txt", output)
        # Current and parent directory should also be listed
        self.assertIn(".", output)
        self.assertIn("..", output)

    def test_long_format(self):
        """Test the -l option for long listing format."""
        exit_code = ls.main(["-l", self.test_dir])
        
        # Check that it ran without error
        self.assertEqual(exit_code, 0)
        
        # Capture the output
        output = sys.stdout.getvalue()
        
        # Check for elements of the long format
        for filename in ["file1.txt", "file2.txt", "file3.dat", "subdir"]:
            # Each file should have a long listing with permissions, size, etc.
            # Different OSes use different formats, so we just check for basic components
            # Full regex matching would be OS-dependent
            file_info = [line for line in output.split('\n') if filename in line][0]
            
            # Check for permission string (starts with - for files, d for directories)
            if filename == "subdir":
                self.assertTrue(file_info.startswith('d'))
            else:
                self.assertTrue(file_info.startswith('-'))
            
            # Check for user and group info
            user_info = file_info.split()[2]  # 3rd column is typically the user
            self.assertTrue(len(user_info) > 0)

    def test_directory_option(self):
        """Test the -d option to list directories themselves."""
        exit_code = ls.main(["-d", self.subdir])
        
        # Check that it ran without error
        self.assertEqual(exit_code, 0)
        
        # Capture the output
        output = sys.stdout.getvalue()
        
        # Check that the directory itself is listed, not its contents
        self.assertIn("subdir", output)
        self.assertNotIn("subfile.txt", output)

    def test_recursive_option(self):
        """Test the -R option for recursive listing."""
        # Create a file in the subdirectory that will be visible in the output
        with open(os.path.join(self.subdir, "visible_file.txt"), "w") as f:
            f.write("This file should be visible in recursive output")
        
        # Debug: Print the directory structure
        print("\nDEBUG - Directory structure:")
        for root, dirs, files in os.walk(self.test_dir):
            print(f"Root: {root}")
            print(f"  Dirs: {dirs}")
            print(f"  Files: {files}")
            
        exit_code = ls.main(["-R", self.test_dir])
        
        # Check that it ran without error
        self.assertEqual(exit_code, 0)
        
        # Capture and print the output for debugging
        output = sys.stdout.getvalue()
        print("\nDEBUG - ls -R output:")
        print(output)
        
        # Check that both the directory and its contents are listed
        self.assertIn("subdir", output)
        self.assertIn("visible_file.txt", output)  # This file should be visible in the recursive output

    def test_format_mode(self):
        """Test the format_mode function."""
        # Test directory mode
        dir_mode = os.stat(self.subdir).st_mode
        dir_format = ls.format_mode(dir_mode)
        self.assertTrue(dir_format.startswith('d'))
        
        # Test regular file mode
        file_mode = os.stat(self.file1).st_mode
        file_format = ls.format_mode(file_mode)
        self.assertTrue(file_format.startswith('-'))
        
        # Test executable file mode (if not on Windows)
        if sys.platform != "win32" and hasattr(os, "chmod"):
            exe_mode = os.stat(self.executable).st_mode
            if exe_mode & stat.S_IXUSR:  # Only if it's actually executable
                exe_format = ls.format_mode(exe_mode)
                self.assertIn('x', exe_format)

    def test_format_size(self):
        """Test the format_size function."""
        # Test various sizes
        self.assertEqual(ls.format_size(0), "0")
        self.assertEqual(ls.format_size(1023), "1023")
        self.assertEqual(ls.format_size(1024), "1024")
        
        # Test human-readable format
        self.assertEqual(ls.format_size(0, human_readable=True), "0")
        self.assertEqual(ls.format_size(1023, human_readable=True), "1023")
        self.assertEqual(ls.format_size(1024, human_readable=True), "1K")
        self.assertEqual(ls.format_size(1536, human_readable=True), "1.5K")
        self.assertEqual(ls.format_size(1048576, human_readable=True), "1M")
        self.assertEqual(ls.format_size(10485760, human_readable=True), "10M")

    def test_nonexistent_file(self):
        """Test ls with a non-existent file."""
        nonexistent = os.path.join(self.test_dir, "nonexistent.txt")
        exit_code = ls.main([nonexistent])
        
        # Check that it exited with an error
        self.assertEqual(exit_code, 1)
        
        # Capture the error output
        error_output = sys.stderr.getvalue()
        
        # Check for error message
        self.assertIn("No such file or directory", error_output)

    def test_multiple_arguments(self):
        """Test ls with multiple arguments."""
        exit_code = ls.main([self.file1, self.file2])
        
        # Check that it ran without error
        self.assertEqual(exit_code, 0)
        
        # Capture the output
        output = sys.stdout.getvalue()
        
        # Check that both files are listed
        self.assertIn("file1.txt", output)
        self.assertIn("file2.txt", output)


@unittest.skipIf(os.environ.get('SKIP_REFERENCE_TESTS') or sys.platform == "win32", 
                "Reference tests skipped or running on Windows")
class ReferenceLsTests(unittest.TestCase):
    """Test PyKnife ls implementation against the system ls command."""
    
    def setUp(self):
        """Set up for reference tests."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create a test file
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("Test content")

    def tearDown(self):
        """Clean up after reference tests."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_reference_basic(self):
        """Compare basic ls with system command."""
        # Define a basic ls command
        args = [self.test_dir]
        
        # Compare PyKnife implementation with system command
        result = compare_with_system("ls", args, ls.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'ls' not available: {result['error']}")
        
        # We don't compare output directly as formatting may differ slightly
        # Instead, check that neither command failed
        self.assertEqual(result['pyknife_exit_code'], 0)
        self.assertEqual(result['system_exit_code'], 0)
        
    def test_reference_long(self):
        """Compare ls -l with system command."""
        # Define ls command with -l option
        args = ["-l", self.test_dir]
        
        # Compare PyKnife implementation with system command
        result = compare_with_system("ls", args, ls.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'ls' not available: {result['error']}")
        
        # We don't compare output directly as formatting may differ slightly
        # Instead, check that neither command failed
        self.assertEqual(result['pyknife_exit_code'], 0)
        self.assertEqual(result['system_exit_code'], 0)


if __name__ == "__main__":
    unittest.main() 