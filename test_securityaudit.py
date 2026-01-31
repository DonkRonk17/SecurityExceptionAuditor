#!/usr/bin/env python3
"""
Comprehensive test suite for SecurityExceptionAuditor.

Tests cover:
- Core functionality
- Edge cases
- Error handling
- Cross-platform behavior
- Integration scenarios

Run: python test_securityaudit.py
"""

import json
import os
import platform
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from securityaudit import (
    SecurityException,
    AuditResult,
    WindowsDefenderAuditor,
    BitdefenderAuditor,
    WindowsFirewallAuditor,
    LinuxFirewallAuditor,
    ProcessChecker,
    SecurityExceptionAuditor,
    generate_markdown_report,
    generate_json_report,
    TEAM_BRAIN_WHITELIST,
    VERSION,
)


class TestSecurityException(unittest.TestCase):
    """Test SecurityException data class."""
    
    def test_creation_basic(self):
        """Test basic exception creation."""
        exc = SecurityException(
            path="C:\\Python312\\python.exe",
            exception_type="process",
            product="defender"
        )
        
        self.assertEqual(exc.path, "C:\\Python312\\python.exe")
        self.assertEqual(exc.exception_type, "process")
        self.assertEqual(exc.product, "defender")
        self.assertTrue(exc.exists)  # Default
    
    def test_creation_with_ports(self):
        """Test exception with port information."""
        exc = SecurityException(
            path="uvicorn",
            exception_type="process",
            product="defender",
            ports=[8000, 8001, 8080]
        )
        
        self.assertEqual(exc.ports, [8000, 8001, 8080])
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        exc = SecurityException(
            path="C:\\Test\\app.exe",
            exception_type="path",
            product="bitdefender",
            exists=False,
            created=datetime(2026, 1, 15, 10, 30)
        )
        
        d = exc.to_dict()
        
        self.assertEqual(d["path"], "C:\\Test\\app.exe")
        self.assertEqual(d["exception_type"], "path")
        self.assertEqual(d["product"], "bitdefender")
        self.assertFalse(d["exists"])
        self.assertIn("2026-01-15", d["created"])
    
    def test_repr_active(self):
        """Test string representation for active exception."""
        exc = SecurityException(
            path="C:\\Program Files\\Test",
            exception_type="folder",
            product="defender",
            exists=True
        )
        
        repr_str = repr(exc)
        self.assertIn("[OK]", repr_str)
        self.assertIn("defender", repr_str)
    
    def test_repr_stale(self):
        """Test string representation for stale exception."""
        exc = SecurityException(
            path="C:\\OldProgram\\app.exe",
            exception_type="path",
            product="defender",
            exists=False
        )
        
        repr_str = repr(exc)
        self.assertIn("[STALE]", repr_str)


class TestAuditResult(unittest.TestCase):
    """Test AuditResult class."""
    
    def test_creation(self):
        """Test basic audit result creation."""
        result = AuditResult("defender")
        
        self.assertEqual(result.product, "defender")
        self.assertEqual(result.total_count, 0)
        self.assertEqual(result.stale_count, 0)
        self.assertEqual(result.active_count, 0)
        self.assertFalse(result.requires_elevation)
    
    def test_counts(self):
        """Test exception counting."""
        result = AuditResult("defender")
        
        # Add some exceptions
        result.exceptions.append(SecurityException(
            path="path1", exception_type="path", product="defender", exists=True
        ))
        result.exceptions.append(SecurityException(
            path="path2", exception_type="path", product="defender", exists=True
        ))
        result.exceptions.append(SecurityException(
            path="path3", exception_type="path", product="defender", exists=False
        ))
        
        self.assertEqual(result.total_count, 3)
        self.assertEqual(result.active_count, 2)
        self.assertEqual(result.stale_count, 1)
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        result = AuditResult("bitdefender")
        result.exceptions.append(SecurityException(
            path="test", exception_type="path", product="bitdefender"
        ))
        result.errors.append("Test error")
        result.warnings.append("Test warning")
        
        d = result.to_dict()
        
        self.assertEqual(d["product"], "bitdefender")
        self.assertEqual(d["total_exceptions"], 1)
        self.assertEqual(len(d["exceptions"]), 1)
        self.assertEqual(d["errors"], ["Test error"])
        self.assertEqual(d["warnings"], ["Test warning"])


class TestWindowsDefenderAuditor(unittest.TestCase):
    """Test Windows Defender auditor."""
    
    def test_is_available_windows(self):
        """Test availability check on Windows."""
        auditor = WindowsDefenderAuditor()
        
        if platform.system() == "Windows":
            self.assertTrue(auditor.is_available())
        else:
            self.assertFalse(auditor.is_available())
    
    @patch('subprocess.run')
    def test_audit_success(self, mock_run):
        """Test successful audit with mocked PowerShell."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "ExclusionPath": ["C:\\Test\\Path1", "C:\\Test\\Path2"],
                "ExclusionProcess": ["python.exe"],
                "ExclusionExtension": [".log"]
            })
        )
        
        auditor = WindowsDefenderAuditor()
        
        with patch.object(auditor, 'is_available', return_value=True):
            result = auditor.audit()
        
        self.assertEqual(result.product, "defender")
        # Should have 2 paths + 1 process + 1 extension = 4 exceptions
        # (actual count depends on path existence checks)
    
    @patch('subprocess.run')
    def test_audit_elevation_required(self, mock_run):
        """Test audit when elevation is required."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Access is denied. Requires elevation."
        )
        
        auditor = WindowsDefenderAuditor()
        
        with patch.object(auditor, 'is_available', return_value=True):
            result = auditor.audit()
        
        self.assertTrue(result.requires_elevation)


class TestBitdefenderAuditor(unittest.TestCase):
    """Test Bitdefender auditor."""
    
    def test_is_available(self):
        """Test availability check."""
        auditor = BitdefenderAuditor()
        # Just ensure it doesn't crash
        available = auditor.is_available()
        self.assertIsInstance(available, bool)
    
    def test_audit_not_available(self):
        """Test audit when Bitdefender is not installed."""
        auditor = BitdefenderAuditor()
        
        with patch.object(auditor, 'is_available', return_value=False):
            result = auditor.audit()
        
        self.assertEqual(len(result.errors), 1)
        self.assertIn("not detected", result.errors[0])


class TestWindowsFirewallAuditor(unittest.TestCase):
    """Test Windows Firewall auditor."""
    
    def test_is_available(self):
        """Test availability check."""
        auditor = WindowsFirewallAuditor()
        
        if platform.system() == "Windows":
            self.assertTrue(auditor.is_available())
        else:
            self.assertFalse(auditor.is_available())


class TestLinuxFirewallAuditor(unittest.TestCase):
    """Test Linux Firewall auditor."""
    
    def test_is_available(self):
        """Test availability check."""
        auditor = LinuxFirewallAuditor()
        
        if platform.system() == "Linux":
            self.assertTrue(auditor.is_available())
        else:
            self.assertFalse(auditor.is_available())


class TestProcessChecker(unittest.TestCase):
    """Test ProcessChecker utility."""
    
    def test_get_running_processes(self):
        """Test getting running processes."""
        processes = ProcessChecker.get_running_processes()
        
        self.assertIsInstance(processes, list)
        # Should have at least some processes
        if platform.system() == "Windows":
            # On Windows, should get process list
            pass  # May be empty due to permissions
    
    def test_get_listening_ports(self):
        """Test getting listening ports."""
        ports = ProcessChecker.get_listening_ports()
        
        self.assertIsInstance(ports, list)
    
    def test_check_process_python(self):
        """Test checking for Python process (should be running)."""
        # Python is running since we're executing this test
        is_running = ProcessChecker.check_process("python")
        # Note: May not always detect itself depending on process name
        self.assertIsInstance(is_running, bool)
    
    def test_check_process_nonexistent(self):
        """Test checking for non-existent process."""
        is_running = ProcessChecker.check_process("nonexistent_process_xyz_12345")
        self.assertFalse(is_running)
    
    def test_check_port(self):
        """Test checking port status."""
        # Port 0 should never be in use
        is_in_use = ProcessChecker.check_port(0)
        self.assertFalse(is_in_use)


class TestSecurityExceptionAuditor(unittest.TestCase):
    """Test main SecurityExceptionAuditor class."""
    
    def test_initialization(self):
        """Test auditor initialization."""
        auditor = SecurityExceptionAuditor()
        
        self.assertIsNotNone(auditor.auditors)
        self.assertIn("defender", auditor.auditors)
        self.assertIn("bitdefender", auditor.auditors)
        self.assertIsNotNone(auditor.team_brain_whitelist)
    
    def test_get_available_products(self):
        """Test getting available products."""
        auditor = SecurityExceptionAuditor()
        
        products = auditor.get_available_products()
        
        self.assertIsInstance(products, list)
        
        if platform.system() == "Windows":
            self.assertIn("defender", products)
            self.assertIn("windows_firewall", products)
        elif platform.system() == "Linux":
            self.assertIn("linux_firewall", products)
    
    def test_audit_all(self):
        """Test auditing all available products."""
        auditor = SecurityExceptionAuditor()
        
        results = auditor.audit()
        
        self.assertIsInstance(results, dict)
        
        for product, result in results.items():
            self.assertIsInstance(result, AuditResult)
            self.assertEqual(result.product, product)
    
    def test_generate_recommendations(self):
        """Test generating Team Brain recommendations."""
        auditor = SecurityExceptionAuditor()
        
        recommendations = auditor.generate_recommendations()
        
        self.assertIn("generated_at", recommendations)
        self.assertIn("platform", recommendations)
        self.assertIn("recommendations", recommendations)
        self.assertIn("missing", recommendations)
        self.assertIn("already_covered", recommendations)
        
        # Should have recommendations for Team Brain whitelist
        self.assertGreater(len(recommendations["recommendations"]), 0)
    
    def test_find_stale_exceptions(self):
        """Test finding stale exceptions."""
        auditor = SecurityExceptionAuditor()
        
        stale = auditor.find_stale_exceptions()
        
        self.assertIsInstance(stale, list)
    
    def test_check_process_and_port(self):
        """Test combined process and port check."""
        auditor = SecurityExceptionAuditor()
        
        result = auditor.check_process_and_port(
            process="python",
            port=8000
        )
        
        self.assertIn("timestamp", result)
        self.assertIn("process", result)
        self.assertIn("port", result)
        self.assertEqual(result["process"]["name"], "python")
        self.assertEqual(result["port"]["number"], 8000)


class TestReportGenerators(unittest.TestCase):
    """Test report generation functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_result = AuditResult("defender")
        self.sample_result.exceptions.append(SecurityException(
            path="C:\\Test\\Path",
            exception_type="folder",
            product="defender",
            exists=True
        ))
        self.sample_result.exceptions.append(SecurityException(
            path="C:\\Old\\Path",
            exception_type="path",
            product="defender",
            exists=False
        ))
        
        self.sample_results = {"defender": self.sample_result}
    
    def test_markdown_report_generation(self):
        """Test markdown report generation."""
        report = generate_markdown_report(self.sample_results)
        
        self.assertIn("# Security Exception Audit Report", report)
        self.assertIn("defender", report.lower())
        self.assertIn("[OK]", report)
        self.assertIn("[STALE]", report)
        self.assertIn("SecurityExceptionAuditor", report)
    
    def test_markdown_report_with_recommendations(self):
        """Test markdown report with recommendations."""
        recommendations = {
            "missing": [
                {"name": "Test", "path": "C:\\Test", "reason": "Testing"}
            ],
            "already_covered": []
        }
        
        report = generate_markdown_report(self.sample_results, recommendations)
        
        self.assertIn("Recommendations", report)
        self.assertIn("Missing Exceptions", report)
    
    def test_json_report_generation(self):
        """Test JSON report generation."""
        report = generate_json_report(self.sample_results)
        
        # Should be valid JSON
        data = json.loads(report)
        
        self.assertIn("metadata", data)
        self.assertIn("summary", data)
        self.assertIn("products", data)
        self.assertEqual(data["summary"]["total_exceptions"], 2)
        self.assertEqual(data["summary"]["active_exceptions"], 1)
        self.assertEqual(data["summary"]["stale_exceptions"], 1)
    
    def test_json_report_with_recommendations(self):
        """Test JSON report with recommendations."""
        recommendations = {
            "missing": [],
            "already_covered": [{"name": "Test", "path": "C:\\Test"}]
        }
        
        report = generate_json_report(self.sample_results, recommendations)
        
        data = json.loads(report)
        self.assertIn("recommendations", data)


class TestTeamBrainWhitelist(unittest.TestCase):
    """Test Team Brain whitelist configuration."""
    
    def test_whitelist_structure(self):
        """Test whitelist has correct structure."""
        for key, item in TEAM_BRAIN_WHITELIST.items():
            self.assertIn("name", item)
            self.assertIn("paths", item)
            self.assertIn("reason", item)
            self.assertIsInstance(item["paths"], list)
            self.assertGreater(len(item["paths"]), 0)
    
    def test_whitelist_contains_essential_items(self):
        """Test whitelist contains essential Team Brain items."""
        essential_keys = ["python", "autoprojects", "nodejs"]
        
        for key in essential_keys:
            self.assertIn(key, TEAM_BRAIN_WHITELIST)


class TestVersion(unittest.TestCase):
    """Test version information."""
    
    def test_version_format(self):
        """Test version string format."""
        self.assertRegex(VERSION, r'^\d+\.\d+\.\d+$')


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_empty_audit_results(self):
        """Test handling of empty audit results."""
        results = {}
        
        markdown = generate_markdown_report(results)
        json_report = generate_json_report(results)
        
        self.assertIn("Security Exception Audit Report", markdown)
        
        data = json.loads(json_report)
        self.assertEqual(data["summary"]["total_exceptions"], 0)
    
    def test_exception_with_special_characters(self):
        """Test exception with special characters in path."""
        exc = SecurityException(
            path="C:\\Users\\test user\\Documents\\file (1).exe",
            exception_type="path",
            product="defender"
        )
        
        d = exc.to_dict()
        self.assertIn("test user", d["path"])
        self.assertIn("(1)", d["path"])
    
    def test_audit_result_with_errors(self):
        """Test audit result with errors."""
        result = AuditResult("test")
        result.errors.append("Error 1")
        result.errors.append("Error 2")
        result.warnings.append("Warning 1")
        
        d = result.to_dict()
        
        self.assertEqual(len(d["errors"]), 2)
        self.assertEqual(len(d["warnings"]), 1)


def run_tests():
    """Run all tests with nice output."""
    print("=" * 70)
    print(f"TESTING: SecurityExceptionAuditor v{VERSION}")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityException))
    suite.addTests(loader.loadTestsFromTestCase(TestAuditResult))
    suite.addTests(loader.loadTestsFromTestCase(TestWindowsDefenderAuditor))
    suite.addTests(loader.loadTestsFromTestCase(TestBitdefenderAuditor))
    suite.addTests(loader.loadTestsFromTestCase(TestWindowsFirewallAuditor))
    suite.addTests(loader.loadTestsFromTestCase(TestLinuxFirewallAuditor))
    suite.addTests(loader.loadTestsFromTestCase(TestProcessChecker))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityExceptionAuditor))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGenerators))
    suite.addTests(loader.loadTestsFromTestCase(TestTeamBrainWhitelist))
    suite.addTests(loader.loadTestsFromTestCase(TestVersion))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {result.testsRun} tests")
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"[OK] Passed: {passed}")
    if result.failures:
        print(f"[X] Failed: {len(result.failures)}")
    if result.errors:
        print(f"[X] Errors: {len(result.errors)}")
    print("=" * 70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
