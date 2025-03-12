#!/usr/bin/env python3
"""
Tests for the mkdir command.
"""

import os
import sys
import stat
import shutil
import unittest
import tempfile
from io import StringIO
from src.commands import mkdir
from src.testing.reference_tester import compare_with_system


class TestMkdir(unittest.TestCase):
    """Test cases for the mkdir command."""

    def setUp(self):
        """Set up for tests."""
        # Redirect stdout and stderr
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        
        # Create a temporary directory for test directories
        self.test_dir = tempfile.mkdtemp()
        self.test_dirs = []

    def tearDown(self):
        """Clean up after tests."""
        # Restore stdout and stderr
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        
        # Remove any test directories
        for dir_path in self.test_dirs:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                except OSError:
                    pass
        
        # Remove test directory
        try:
            shutil.rmtree(self.test_dir)
        except OSError:
            pass

    def get_test_dir_path(self, dirname):
        """Get path for a test directory."""
        path = os.path.join(self.test_dir, dirname)
        self.test_dirs.append(path)
        return path

    def test_create_directory(self):
        """Test creating a simple directory."""
        test_dir = self.get_test_dir_path("simple_dir")
        
        # Make sure the directory doesn't exist
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        # Run mkdir
        exit_code = mkdir.main([test_dir])
        
        # Check results
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(test_dir))
        self.assertTrue(os.path.isdir(test_dir))

    def test_create_existing_directory(self):
        """Test attempting to create a directory that already exists."""
        test_dir = self.get_test_dir_path("existing_dir")
        
        # Create the directory
        os.makedirs(test_dir, exist_ok=True)
        
        # Run mkdir
        exit_code = mkdir.main([test_dir])
        
        # Check results
        self.assertEqual(exit_code, 1)
        stderr_output = sys.stderr.getvalue()
        self.assertIn("File exists", stderr_output)

    def test_create_multiple_directories(self):
        """Test creating multiple directories at once."""
        test_dir1 = self.get_test_dir_path("multi_dir1")
        test_dir2 = self.get_test_dir_path("multi_dir2")
        test_dir3 = self.get_test_dir_path("multi_dir3")
        
        # Make sure the directories don't exist
        for dir_path in [test_dir1, test_dir2, test_dir3]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
        
        # Run mkdir with multiple directories
        exit_code = mkdir.main([test_dir1, test_dir2, test_dir3])
        
        # Check results
        self.assertEqual(exit_code, 0)
        for dir_path in [test_dir1, test_dir2, test_dir3]:
            self.assertTrue(os.path.exists(dir_path))
            self.assertTrue(os.path.isdir(dir_path))

    def test_parents_option(self):
        """Test the -p option to create parent directories."""
        nested_dir = self.get_test_dir_path("parent/child/grandchild")
        
        # Make sure the directory doesn't exist
        parent_dir = os.path.dirname(os.path.dirname(nested_dir))
        if os.path.exists(parent_dir):
            shutil.rmtree(parent_dir)
        
        # Run mkdir with -p
        exit_code = mkdir.main(["-p", nested_dir])
        
        # Check results
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(nested_dir))
        self.assertTrue(os.path.isdir(nested_dir))

    def test_mode_option(self):
        """Test the -m option to set directory permissions."""
        test_dir = self.get_test_dir_path("mode_dir")
        
        # Make sure the directory doesn't exist
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        # We'll specify a mode that is unlikely to match the umask
        test_mode = "0755"  # rwxr-xr-x
        
        # Run mkdir with -m
        exit_code = mkdir.main(["-m", test_mode, test_dir])
        
        # Check results
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(test_dir))
        self.assertTrue(os.path.isdir(test_dir))
        
        # Permission testing is platform dependent, so we'll just check that
        # the directory was created successfully and is accessible
        mode = os.stat(test_dir).st_mode & 0o777
        
        # On Windows, the mode may not match exactly, so we'll just verify it's accessible
        if sys.platform == "win32":
            self.assertTrue(os.access(test_dir, os.R_OK | os.W_OK))
        else:
            # On Unix-like systems, we can check the mode more specifically
            # but still need to account for umask
            umask = os.umask(0)
            os.umask(umask)  # Reset the umask
            expected_mode = 0o755 & ~umask
            self.assertEqual(mode, expected_mode)

    def test_verbose_option(self):
        """Test the -v option to print messages about created directories."""
        test_dir = self.get_test_dir_path("verbose_dir")
        
        # Make sure the directory doesn't exist
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        # Run mkdir with -v
        exit_code = mkdir.main(["-v", test_dir])
        
        # Check results
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(test_dir))
        stdout_output = sys.stdout.getvalue()
        self.assertIn(f"created directory '{test_dir}'", stdout_output)

    def test_missing_parent(self):
        """Test attempting to create a directory without an existing parent."""
        nested_dir = self.get_test_dir_path("nonexistent_parent/child")
        
        # Make sure the parent directory doesn't exist
        parent_dir = os.path.dirname(nested_dir)
        if os.path.exists(parent_dir):
            shutil.rmtree(parent_dir)
        
        # Run mkdir without -p
        exit_code = mkdir.main([nested_dir])
        
        # Check results
        self.assertEqual(exit_code, 1)
        self.assertFalse(os.path.exists(nested_dir))
        stderr_output = sys.stderr.getvalue()
        self.assertIn("No such file or directory", stderr_output)

    def test_invalid_mode(self):
        """Test error handling when an invalid mode is specified."""
        test_dir = self.get_test_dir_path("invalid_mode_dir")
        
        # Run mkdir with an invalid mode
        exit_code = mkdir.main(["-m", "invalid", test_dir])
        
        # Check results
        self.assertEqual(exit_code, 1)
        self.assertFalse(os.path.exists(test_dir))
        stderr_output = sys.stderr.getvalue()
        self.assertIn("invalid mode", stderr_output.lower())

    def test_parse_mode(self):
        """Test the parse_mode function with various inputs."""
        # Test octal modes
        self.assertEqual(mkdir.parse_mode("0755"), 0o755)
        self.assertEqual(mkdir.parse_mode("0644"), 0o644)
        
        # Test decimal modes
        self.assertEqual(mkdir.parse_mode("755"), 755)
        self.assertEqual(mkdir.parse_mode("644"), 644)
        
        # Test invalid modes
        with self.assertRaises(ValueError):
            mkdir.parse_mode("invalid")


@unittest.skipIf(os.environ.get('SKIP_REFERENCE_TESTS'), "Reference tests skipped")
class ReferenceMkdirTests(unittest.TestCase):
    """Test PyKnife mkdir implementation against the system mkdir command."""
    
    def setUp(self):
        """Set up for reference tests."""
        self.test_dir = tempfile.mkdtemp()
        self.test_dirs = []

    def tearDown(self):
        """Clean up after reference tests."""
        for dir_path in self.test_dirs:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                except OSError:
                    pass
        
        try:
            shutil.rmtree(self.test_dir)
        except OSError:
            pass

    def get_test_dir_path(self, dirname):
        """Get path for a test directory."""
        path = os.path.join(self.test_dir, dirname)
        self.test_dirs.append(path)
        return path

    def test_reference_basic(self):
        """Compare basic mkdir with system command."""
        test_dir = self.get_test_dir_path("ref_basic_dir")
        
        # Define a basic mkdir command
        args = [test_dir]
        
        # Compare PyKnife implementation with system command
        result = compare_with_system("mkdir", args, mkdir.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'mkdir' not available: {result['error']}")
        
        # Check if the directory was created
        self.assertTrue(os.path.exists(test_dir))
        self.assertTrue(os.path.isdir(test_dir))
        
    def test_reference_parents(self):
        """Compare mkdir -p with system command."""
        test_dir = self.get_test_dir_path("ref_parent/child/grandchild")
        
        # Define mkdir command with -p option
        args = ["-p", test_dir]
        
        # Compare PyKnife implementation with system command
        result = compare_with_system("mkdir", args, mkdir.main)
        
        if not result['system_available']:
            self.skipTest(f"System command 'mkdir' not available: {result['error']}")
        
        # Check if the directory was created
        self.assertTrue(os.path.exists(test_dir))
        self.assertTrue(os.path.isdir(test_dir))


if __name__ == "__main__":
    unittest.main() 