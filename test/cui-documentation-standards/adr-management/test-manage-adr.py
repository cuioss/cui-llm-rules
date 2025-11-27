#!/usr/bin/env python3
"""Tests for manage-adr.py script."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestManageAdr(unittest.TestCase):
    """Test cases for ADR management script."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.script_path = (
            Path(__file__).parent.parent.parent.parent
            / "marketplace/bundles/cui-documentation-standards/skills/adr-management/scripts/manage-adr.py"
        )
        cls.temp_dir = tempfile.mkdtemp()
        cls.adr_dir = Path(cls.temp_dir) / "doc" / "adr"
        cls.adr_dir.mkdir(parents=True)
        cls.original_cwd = os.getcwd()
        os.chdir(cls.temp_dir)

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures."""
        os.chdir(cls.original_cwd)
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        """Clean ADR directory before each test."""
        # Remove all ADR files
        for f in self.adr_dir.glob("*.adoc"):
            f.unlink()

    def run_script(self, *args):
        """Run the script with given arguments."""
        result = subprocess.run(
            [sys.executable, str(self.script_path)] + list(args),
            capture_output=True,
            text=True,
            cwd=self.temp_dir,
        )
        return result

    def test_next_number_empty_dir(self):
        """Test next-number returns 1 for empty directory."""
        result = self.run_script("next-number")
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertTrue(output["success"])
        self.assertEqual(output["next_number"], 1)

    def test_create_adr(self):
        """Test creating a new ADR."""
        result = self.run_script("create", "--title", "Use PostgreSQL")
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertTrue(output["success"])
        self.assertEqual(output["number"], 1)
        self.assertIn("001-Use_PostgreSQL.adoc", output["path"])

        # Verify file exists
        created_file = self.adr_dir / "001-Use_PostgreSQL.adoc"
        self.assertTrue(created_file.exists())

        # Verify content
        content = created_file.read_text()
        self.assertIn("ADR-001", content)
        self.assertIn("Use PostgreSQL", content)
        self.assertIn("Proposed", content)

    def test_create_adr_with_status(self):
        """Test creating ADR with custom status."""
        result = self.run_script(
            "create", "--title", "Another Decision", "--status", "Accepted"
        )
        output = json.loads(result.stdout)
        self.assertTrue(output["success"])

        # Verify status in file
        created_file = self.adr_dir / f"{output['number']:03d}-Another_Decision.adoc"
        content = created_file.read_text()
        self.assertIn("Accepted", content)

    def test_create_multiple_adrs(self):
        """Test creating multiple ADRs increments numbers."""
        self.run_script("create", "--title", "First ADR")
        self.run_script("create", "--title", "Second ADR")
        result = self.run_script("create", "--title", "Third ADR")

        output = json.loads(result.stdout)
        self.assertEqual(output["number"], 3)

    def test_list_adrs(self):
        """Test listing ADRs."""
        # Create some ADRs first
        self.run_script("create", "--title", "ADR One")
        self.run_script("create", "--title", "ADR Two")

        result = self.run_script("list")
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertTrue(output["success"])
        self.assertEqual(output["count"], 2)

    def test_list_adrs_filter_status(self):
        """Test listing ADRs filtered by status."""
        self.run_script("create", "--title", "Proposed One")
        self.run_script("create", "--title", "Accepted One", "--status", "Accepted")

        result = self.run_script("list", "--status", "Proposed")
        output = json.loads(result.stdout)
        self.assertTrue(output["success"])
        self.assertEqual(output["count"], 1)
        for adr in output["adrs"]:
            self.assertEqual(adr["status"], "Proposed")

    def test_read_adr(self):
        """Test reading ADR by number."""
        self.run_script("create", "--title", "Test Read")

        result = self.run_script("read", "--number", "1")
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertTrue(output["success"])
        self.assertIn("content", output)
        self.assertIn("Test Read", output["content"])

    def test_read_adr_not_found(self):
        """Test reading non-existent ADR."""
        result = self.run_script("read", "--number", "999")
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stderr)
        self.assertFalse(output["success"])
        self.assertIn("not found", output["error"].lower())

    def test_update_adr_status(self):
        """Test updating ADR status."""
        self.run_script("create", "--title", "Update Test")

        result = self.run_script("update", "--number", "1", "--status", "Deprecated")
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertTrue(output["success"])

        # Verify status updated
        result = self.run_script("read", "--number", "1")
        output = json.loads(result.stdout)
        self.assertIn("Deprecated", output["content"])

    def test_delete_requires_force(self):
        """Test delete requires --force flag."""
        self.run_script("create", "--title", "Delete Test")

        result = self.run_script("delete", "--number", "1")
        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stderr)
        self.assertIn("--force", output["error"])

    def test_delete_with_force(self):
        """Test delete with --force flag."""
        self.run_script("create", "--title", "Delete Me")

        result = self.run_script("delete", "--number", "1", "--force")
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertTrue(output["deleted"])

        # Verify file is deleted
        files = list(self.adr_dir.glob("001-*.adoc"))
        self.assertEqual(len(files), 0)

    def test_filename_sanitization(self):
        """Test filename sanitization for special characters."""
        result = self.run_script(
            "create", "--title", "Use API/REST for User Service!"
        )
        output = json.loads(result.stdout)
        self.assertTrue(output["success"])
        # Get just the filename part
        filename = Path(output["path"]).name
        # Special chars should be removed/replaced
        self.assertNotIn("/", filename)
        self.assertNotIn("!", filename)

    def test_invalid_status(self):
        """Test creating ADR with invalid status."""
        result = self.run_script(
            "create", "--title", "Invalid Status", "--status", "InvalidStatus"
        )
        # argparse will reject invalid choices with exit code 2
        self.assertNotEqual(result.returncode, 0)
        # Error message is in stderr from argparse
        self.assertIn("invalid choice", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
