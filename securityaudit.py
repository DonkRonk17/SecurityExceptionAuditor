#!/usr/bin/env python3
"""
SecurityExceptionAuditor - Security Software Exception Manager

A comprehensive tool for auditing, managing, and recommending security software
exceptions for development environments. Supports Windows Defender, Bitdefender,
and Linux firewall rules.

Features:
- Audit current security exceptions across multiple products
- Generate recommended whitelist for Team Brain development tools
- Identify stale/unused exceptions (programs no longer installed)
- Identify missing exceptions (tools not whitelisted)
- Cross-reference with running processes
- Support for Windows Defender, Bitdefender, and Linux iptables

Author: FORGE (Team Brain)
For: Logan Smith / Metaphy LLC
Version: 1.0
Date: January 31, 2026
License: MIT
"""

import argparse
import json
import os
import platform
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


# =============================================================================
# CONSTANTS
# =============================================================================

VERSION = "1.0.0"
TOOL_NAME = "SecurityExceptionAuditor"

# Default Team Brain whitelist
TEAM_BRAIN_WHITELIST = {
    "python": {
        "name": "Python Runtime",
        "paths": [
            "C:\\Python312Official\\python.exe",
            "C:\\Python312Official\\pythonw.exe",
            "C:\\Python312Official\\Scripts\\",
        ],
        "reason": "Core runtime for all Team Brain tools",
        "category": "runtime"
    },
    "uvicorn": {
        "name": "Uvicorn ASGI Server",
        "paths": [
            "C:\\Python312Official\\Scripts\\uvicorn.exe",
        ],
        "ports": [8000, 8001, 8080],
        "reason": "BCH backend ASGI server",
        "category": "server"
    },
    "nodejs": {
        "name": "Node.js",
        "paths": [
            "C:\\Program Files\\nodejs\\node.exe",
            "C:\\Program Files\\nodejs\\npm.cmd",
        ],
        "reason": "Frontend development and tooling",
        "category": "runtime"
    },
    "bch_backend": {
        "name": "BCH Backend",
        "paths": [
            "D:\\BEACON_HQ\\PROJECTS\\00_ACTIVE\\BCH_APPS\\backend\\",
        ],
        "ports": [8000, 8001],
        "reason": "Beacon Comms Hub backend API",
        "category": "project"
    },
    "autoprojects": {
        "name": "AutoProjects Tools",
        "paths": [
            "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\",
        ],
        "reason": "All Team Brain CLI tools and utilities",
        "category": "tools"
    },
    "git": {
        "name": "Git Version Control",
        "paths": [
            "C:\\Program Files\\Git\\",
        ],
        "reason": "Version control for all projects",
        "category": "tools"
    },
    "cursor": {
        "name": "Cursor IDE",
        "paths": [
            "C:\\Users\\logan\\AppData\\Local\\Programs\\cursor\\",
        ],
        "reason": "Primary development IDE",
        "category": "ide"
    },
    "tailscale": {
        "name": "Tailscale VPN",
        "paths": [
            "C:\\Program Files\\Tailscale\\",
        ],
        "ports": [41641],
        "reason": "VPN for remote network access",
        "category": "network"
    }
}


# =============================================================================
# DATA CLASSES
# =============================================================================

class SecurityException:
    """Represents a security exception/exclusion entry."""
    
    def __init__(
        self,
        path: str,
        exception_type: str,
        product: str,
        created: Optional[datetime] = None,
        exists: bool = True,
        ports: Optional[List[int]] = None,
        direction: str = "both",
        raw_data: Optional[Dict] = None
    ):
        self.path = path
        self.exception_type = exception_type  # 'path', 'process', 'folder', 'extension', 'firewall'
        self.product = product  # 'defender', 'bitdefender', 'iptables'
        self.created = created
        self.exists = exists  # Does the path/process still exist?
        self.ports = ports or []
        self.direction = direction  # 'inbound', 'outbound', 'both'
        self.raw_data = raw_data or {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": self.path,
            "exception_type": self.exception_type,
            "product": self.product,
            "created": self.created.isoformat() if self.created else None,
            "exists": self.exists,
            "ports": self.ports,
            "direction": self.direction,
            "raw_data": self.raw_data
        }
    
    def __repr__(self) -> str:
        status = "[OK]" if self.exists else "[STALE]"
        return f"{status} {self.product}:{self.exception_type} -> {self.path}"


class AuditResult:
    """Results from a security audit."""
    
    def __init__(self, product: str):
        self.product = product
        self.exceptions: List[SecurityException] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.audit_time = datetime.now()
        self.requires_elevation = False
    
    @property
    def total_count(self) -> int:
        return len(self.exceptions)
    
    @property
    def stale_count(self) -> int:
        return sum(1 for e in self.exceptions if not e.exists)
    
    @property
    def active_count(self) -> int:
        return sum(1 for e in self.exceptions if e.exists)
    
    def to_dict(self) -> Dict:
        return {
            "product": self.product,
            "audit_time": self.audit_time.isoformat(),
            "total_exceptions": self.total_count,
            "active_exceptions": self.active_count,
            "stale_exceptions": self.stale_count,
            "requires_elevation": self.requires_elevation,
            "exceptions": [e.to_dict() for e in self.exceptions],
            "errors": self.errors,
            "warnings": self.warnings
        }


# =============================================================================
# WINDOWS DEFENDER AUDITOR
# =============================================================================

class WindowsDefenderAuditor:
    """Audits Windows Defender exclusions."""
    
    def __init__(self):
        self.product = "defender"
    
    def is_available(self) -> bool:
        """Check if Windows Defender is available."""
        return platform.system() == "Windows"
    
    def audit(self) -> AuditResult:
        """Audit Windows Defender exclusions."""
        result = AuditResult(self.product)
        
        if not self.is_available():
            result.errors.append("Windows Defender not available on this platform")
            return result
        
        try:
            # Use PowerShell to get exclusions
            ps_cmd = "Get-MpPreference | ConvertTo-Json -Depth 5"
            output = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if output.returncode != 0:
                if "requires elevation" in output.stderr.lower() or "access is denied" in output.stderr.lower():
                    result.requires_elevation = True
                    result.warnings.append("Admin privileges required for full audit")
                else:
                    result.errors.append(f"PowerShell error: {output.stderr}")
                return result
            
            prefs = json.loads(output.stdout)
            
            # Process path exclusions
            path_exclusions = prefs.get("ExclusionPath", []) or []
            if isinstance(path_exclusions, str):
                path_exclusions = [path_exclusions]
            
            for path in path_exclusions:
                exists = os.path.exists(path)
                exc = SecurityException(
                    path=path,
                    exception_type="path" if os.path.isfile(path) else "folder",
                    product=self.product,
                    exists=exists
                )
                result.exceptions.append(exc)
            
            # Process process exclusions
            process_exclusions = prefs.get("ExclusionProcess", []) or []
            if isinstance(process_exclusions, str):
                process_exclusions = [process_exclusions]
            
            for proc in process_exclusions:
                exists = os.path.exists(proc) if os.path.isabs(proc) else True
                exc = SecurityException(
                    path=proc,
                    exception_type="process",
                    product=self.product,
                    exists=exists
                )
                result.exceptions.append(exc)
            
            # Process extension exclusions
            ext_exclusions = prefs.get("ExclusionExtension", []) or []
            if isinstance(ext_exclusions, str):
                ext_exclusions = [ext_exclusions]
            
            for ext in ext_exclusions:
                exc = SecurityException(
                    path=ext,
                    exception_type="extension",
                    product=self.product,
                    exists=True  # Extensions are always "valid"
                )
                result.exceptions.append(exc)
            
        except subprocess.TimeoutExpired:
            result.errors.append("PowerShell command timed out")
        except json.JSONDecodeError as e:
            result.errors.append(f"Failed to parse Defender preferences: {e}")
        except Exception as e:
            result.errors.append(f"Unexpected error: {e}")
        
        return result
    
    def add_exclusion(self, path: str, dry_run: bool = True) -> Tuple[bool, str]:
        """Add a path exclusion to Windows Defender."""
        if dry_run:
            return True, f"[DRY-RUN] Would add exclusion: {path}"
        
        try:
            ps_cmd = f'Add-MpPreference -ExclusionPath "{path}"'
            output = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if output.returncode == 0:
                return True, f"Added exclusion: {path}"
            else:
                return False, f"Failed: {output.stderr}"
        except Exception as e:
            return False, f"Error: {e}"
    
    def remove_exclusion(self, path: str, dry_run: bool = True) -> Tuple[bool, str]:
        """Remove a path exclusion from Windows Defender."""
        if dry_run:
            return True, f"[DRY-RUN] Would remove exclusion: {path}"
        
        try:
            ps_cmd = f'Remove-MpPreference -ExclusionPath "{path}"'
            output = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if output.returncode == 0:
                return True, f"Removed exclusion: {path}"
            else:
                return False, f"Failed: {output.stderr}"
        except Exception as e:
            return False, f"Error: {e}"


# =============================================================================
# BITDEFENDER AUDITOR
# =============================================================================

class BitdefenderAuditor:
    """Audits Bitdefender exclusions (limited - config file parsing)."""
    
    def __init__(self):
        self.product = "bitdefender"
        self.config_locations = [
            Path(os.environ.get("ProgramData", "C:\\ProgramData")) / "Bitdefender",
            Path.home() / "AppData" / "Roaming" / "Bitdefender",
        ]
    
    def is_available(self) -> bool:
        """Check if Bitdefender appears to be installed."""
        if platform.system() != "Windows":
            return False
        
        # Check for Bitdefender program files
        program_paths = [
            Path("C:\\Program Files\\Bitdefender"),
            Path("C:\\Program Files (x86)\\Bitdefender"),
        ]
        
        for path in program_paths:
            if path.exists():
                return True
        
        for loc in self.config_locations:
            if loc.exists():
                return True
        
        return False
    
    def audit(self) -> AuditResult:
        """Audit Bitdefender exclusions (best effort)."""
        result = AuditResult(self.product)
        
        if not self.is_available():
            result.errors.append("Bitdefender not detected on this system")
            return result
        
        result.warnings.append(
            "Bitdefender has limited API access. "
            "Results may be incomplete. Check Bitdefender GUI for full exclusion list."
        )
        
        # Try to find and parse config files
        exclusions_found = []
        
        for config_dir in self.config_locations:
            if not config_dir.exists():
                continue
            
            # Look for common config file patterns
            for pattern in ["*.xml", "*.json", "*.ini", "settings*", "exclusions*"]:
                try:
                    for config_file in config_dir.rglob(pattern):
                        try:
                            content = config_file.read_text(encoding='utf-8', errors='ignore')
                            
                            # Look for path-like patterns in config
                            path_patterns = re.findall(
                                r'[A-Za-z]:\\[^"\'<>\|\?\*\n\r]+',
                                content
                            )
                            
                            for path in path_patterns:
                                # Filter out system paths and Bitdefender's own paths
                                if "Bitdefender" in path:
                                    continue
                                if path not in exclusions_found:
                                    exclusions_found.append(path)
                                    exists = os.path.exists(path)
                                    exc = SecurityException(
                                        path=path,
                                        exception_type="path",
                                        product=self.product,
                                        exists=exists,
                                        raw_data={"source_file": str(config_file)}
                                    )
                                    result.exceptions.append(exc)
                        except PermissionError:
                            result.requires_elevation = True
                        except Exception:
                            pass
                except PermissionError:
                    result.requires_elevation = True
        
        if not result.exceptions:
            result.warnings.append(
                "Could not find parseable exclusion data. "
                "Manual export from Bitdefender GUI recommended."
            )
        
        return result
    
    def get_bduitool_path(self) -> Optional[Path]:
        """Find Bitdefender command line tool if available."""
        search_paths = [
            Path("C:\\Program Files\\Bitdefender\\Bitdefender Security"),
            Path("C:\\Program Files (x86)\\Bitdefender\\Bitdefender Security"),
        ]
        
        for base in search_paths:
            if base.exists():
                for tool in base.rglob("bduitool.exe"):
                    return tool
        
        return None


# =============================================================================
# WINDOWS FIREWALL AUDITOR
# =============================================================================

class WindowsFirewallAuditor:
    """Audits Windows Firewall rules."""
    
    def __init__(self):
        self.product = "windows_firewall"
    
    def is_available(self) -> bool:
        """Check if Windows Firewall is available."""
        return platform.system() == "Windows"
    
    def audit(self) -> AuditResult:
        """Audit Windows Firewall rules."""
        result = AuditResult(self.product)
        
        if not self.is_available():
            result.errors.append("Windows Firewall not available on this platform")
            return result
        
        try:
            # Get all firewall rules
            ps_cmd = (
                "Get-NetFirewallRule | Where-Object {$_.Enabled -eq 'True'} | "
                "Select-Object DisplayName, Direction, Action, Profile | "
                "ConvertTo-Json -Depth 3"
            )
            
            output = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if output.returncode != 0:
                if "requires elevation" in output.stderr.lower():
                    result.requires_elevation = True
                    result.warnings.append("Admin privileges may be needed for full details")
                else:
                    result.errors.append(f"PowerShell error: {output.stderr}")
                return result
            
            if not output.stdout.strip():
                result.warnings.append("No firewall rules found or access denied")
                return result
            
            rules = json.loads(output.stdout)
            if isinstance(rules, dict):
                rules = [rules]
            
            # Filter for relevant rules (custom/application rules)
            for rule in rules:
                display_name = rule.get("DisplayName", "Unknown")
                direction = rule.get("Direction", 0)
                
                # Skip system rules (basic heuristic)
                if any(skip in display_name.lower() for skip in [
                    "core networking", "windows", "microsoft", "netlogon"
                ]):
                    continue
                
                exc = SecurityException(
                    path=display_name,
                    exception_type="firewall",
                    product=self.product,
                    exists=True,
                    direction="inbound" if direction == 1 else "outbound",
                    raw_data=rule
                )
                result.exceptions.append(exc)
            
        except subprocess.TimeoutExpired:
            result.errors.append("PowerShell command timed out")
        except json.JSONDecodeError as e:
            result.errors.append(f"Failed to parse firewall rules: {e}")
        except Exception as e:
            result.errors.append(f"Unexpected error: {e}")
        
        return result


# =============================================================================
# LINUX FIREWALL AUDITOR
# =============================================================================

class LinuxFirewallAuditor:
    """Audits Linux firewall rules (iptables/ufw)."""
    
    def __init__(self):
        self.product = "linux_firewall"
    
    def is_available(self) -> bool:
        """Check if running on Linux."""
        return platform.system() == "Linux"
    
    def audit(self) -> AuditResult:
        """Audit Linux firewall rules."""
        result = AuditResult(self.product)
        
        if not self.is_available():
            result.errors.append("Linux firewall not available on this platform")
            return result
        
        # Try ufw first
        try:
            output = subprocess.run(
                ["ufw", "status", "verbose"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if output.returncode == 0:
                lines = output.stdout.split('\n')
                for line in lines:
                    if 'ALLOW' in line or 'DENY' in line:
                        exc = SecurityException(
                            path=line.strip(),
                            exception_type="firewall",
                            product="ufw",
                            exists=True,
                            raw_data={"rule": line}
                        )
                        result.exceptions.append(exc)
        except FileNotFoundError:
            # ufw not installed, try iptables
            pass
        except PermissionError:
            result.requires_elevation = True
            result.warnings.append("Root privileges required for ufw")
        
        # Try iptables
        try:
            output = subprocess.run(
                ["iptables", "-L", "-n", "--line-numbers"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if output.returncode == 0:
                lines = output.stdout.split('\n')
                for line in lines:
                    if line.strip() and not line.startswith("Chain") and not line.startswith("num"):
                        exc = SecurityException(
                            path=line.strip(),
                            exception_type="firewall",
                            product="iptables",
                            exists=True,
                            raw_data={"rule": line}
                        )
                        result.exceptions.append(exc)
        except FileNotFoundError:
            result.warnings.append("iptables not found")
        except PermissionError:
            result.requires_elevation = True
            result.warnings.append("Root privileges required for iptables")
        
        return result


# =============================================================================
# PROCESS CHECKER
# =============================================================================

class ProcessChecker:
    """Check if processes/ports are currently running."""
    
    @staticmethod
    def get_running_processes() -> List[Dict]:
        """Get list of running processes with paths."""
        processes = []
        
        if platform.system() == "Windows":
            try:
                ps_cmd = (
                    "Get-Process | Where-Object {$_.Path -ne $null} | "
                    "Select-Object Name, Path, Id | ConvertTo-Json"
                )
                output = subprocess.run(
                    ["powershell", "-Command", ps_cmd],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if output.returncode == 0 and output.stdout.strip():
                    procs = json.loads(output.stdout)
                    if isinstance(procs, dict):
                        procs = [procs]
                    processes = procs
            except Exception:
                pass
        else:
            # Linux/macOS
            try:
                output = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if output.returncode == 0:
                    for line in output.stdout.split('\n')[1:]:
                        parts = line.split(None, 10)
                        if len(parts) >= 11:
                            processes.append({
                                "Name": parts[10].split()[0],
                                "Path": parts[10],
                                "Id": parts[1]
                            })
            except Exception:
                pass
        
        return processes
    
    @staticmethod
    def get_listening_ports() -> List[Dict]:
        """Get list of ports currently listening."""
        ports = []
        
        if platform.system() == "Windows":
            try:
                output = subprocess.run(
                    ["netstat", "-an"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if output.returncode == 0:
                    for line in output.stdout.split('\n'):
                        if 'LISTENING' in line or 'ESTABLISHED' in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                local = parts[1]
                                if ':' in local:
                                    port = local.split(':')[-1]
                                    try:
                                        ports.append({
                                            "port": int(port),
                                            "state": parts[-1] if len(parts) > 3 else "UNKNOWN"
                                        })
                                    except ValueError:
                                        pass
            except Exception:
                pass
        else:
            try:
                output = subprocess.run(
                    ["ss", "-tuln"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if output.returncode == 0:
                    for line in output.stdout.split('\n')[1:]:
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 5:
                                local = parts[4]
                                if ':' in local:
                                    port = local.split(':')[-1]
                                    try:
                                        ports.append({
                                            "port": int(port),
                                            "state": parts[1]
                                        })
                                    except ValueError:
                                        pass
            except FileNotFoundError:
                pass
        
        return ports
    
    @staticmethod
    def check_process(name: str) -> bool:
        """Check if a process with given name is running."""
        processes = ProcessChecker.get_running_processes()
        name_lower = name.lower()
        
        for proc in processes:
            proc_name = proc.get("Name", "").lower()
            proc_path = proc.get("Path", "").lower()
            
            if name_lower in proc_name or name_lower in proc_path:
                return True
        
        return False
    
    @staticmethod
    def check_port(port: int) -> bool:
        """Check if a port is in use."""
        ports = ProcessChecker.get_listening_ports()
        return any(p["port"] == port for p in ports)


# =============================================================================
# SECURITY EXCEPTION AUDITOR (Main Class)
# =============================================================================

class SecurityExceptionAuditor:
    """Main class for auditing security exceptions."""
    
    def __init__(self):
        self.auditors = {
            "defender": WindowsDefenderAuditor(),
            "bitdefender": BitdefenderAuditor(),
            "windows_firewall": WindowsFirewallAuditor(),
            "linux_firewall": LinuxFirewallAuditor(),
        }
        self.process_checker = ProcessChecker()
        self.team_brain_whitelist = TEAM_BRAIN_WHITELIST
    
    def get_available_products(self) -> List[str]:
        """Get list of available security products on this system."""
        available = []
        for name, auditor in self.auditors.items():
            if auditor.is_available():
                available.append(name)
        return available
    
    def audit(self, products: Optional[List[str]] = None) -> Dict[str, AuditResult]:
        """Audit security exceptions for specified products."""
        if products is None:
            products = self.get_available_products()
        
        results = {}
        for product in products:
            if product in self.auditors:
                results[product] = self.auditors[product].audit()
            else:
                result = AuditResult(product)
                result.errors.append(f"Unknown product: {product}")
                results[product] = result
        
        return results
    
    def generate_recommendations(self) -> Dict[str, Any]:
        """Generate recommended exceptions for Team Brain tools."""
        recommendations = {
            "generated_at": datetime.now().isoformat(),
            "platform": platform.system(),
            "recommendations": [],
            "missing": [],
            "already_covered": [],
        }
        
        # Get current audit
        audit_results = self.audit()
        
        # Collect all current exception paths
        current_paths = set()
        for result in audit_results.values():
            for exc in result.exceptions:
                current_paths.add(exc.path.lower())
                # Also add parent directories
                path = Path(exc.path)
                for parent in path.parents:
                    current_paths.add(str(parent).lower())
        
        # Check each Team Brain whitelist item
        for key, item in self.team_brain_whitelist.items():
            for path in item.get("paths", []):
                path_lower = path.lower()
                exists = os.path.exists(path.rstrip('\\'))
                
                # Check if already covered
                is_covered = False
                for current in current_paths:
                    if path_lower.startswith(current) or current.startswith(path_lower):
                        is_covered = True
                        break
                
                rec = {
                    "name": item["name"],
                    "path": path,
                    "exists": exists,
                    "reason": item["reason"],
                    "category": item.get("category", "general"),
                    "is_covered": is_covered,
                }
                
                if item.get("ports"):
                    rec["ports"] = item["ports"]
                
                recommendations["recommendations"].append(rec)
                
                if not is_covered and exists:
                    recommendations["missing"].append(rec)
                elif is_covered:
                    recommendations["already_covered"].append(rec)
        
        return recommendations
    
    def find_stale_exceptions(self) -> List[SecurityException]:
        """Find exceptions for paths that no longer exist."""
        stale = []
        audit_results = self.audit()
        
        for result in audit_results.values():
            for exc in result.exceptions:
                if not exc.exists:
                    stale.append(exc)
        
        return stale
    
    def check_process_and_port(self, process: Optional[str] = None, port: Optional[int] = None) -> Dict:
        """Check if a process is running and/or port is in use."""
        result = {
            "timestamp": datetime.now().isoformat(),
        }
        
        if process:
            result["process"] = {
                "name": process,
                "is_running": ProcessChecker.check_process(process)
            }
        
        if port:
            result["port"] = {
                "number": port,
                "is_in_use": ProcessChecker.check_port(port)
            }
        
        return result


# =============================================================================
# REPORT GENERATORS
# =============================================================================

def generate_markdown_report(audit_results: Dict[str, AuditResult], recommendations: Dict = None) -> str:
    """Generate a markdown audit report."""
    lines = [
        "# Security Exception Audit Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Platform:** {platform.system()} {platform.release()}",
        f"**Tool:** SecurityExceptionAuditor v{VERSION}",
        "",
        "---",
        "",
    ]
    
    # Summary
    total_exceptions = sum(r.total_count for r in audit_results.values())
    total_stale = sum(r.stale_count for r in audit_results.values())
    total_active = sum(r.active_count for r in audit_results.values())
    
    lines.extend([
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total Exceptions | {total_exceptions} |",
        f"| Active (Path Exists) | {total_active} |",
        f"| Stale (Path Missing) | {total_stale} |",
        f"| Products Audited | {len(audit_results)} |",
        "",
    ])
    
    # Per-product details
    for product, result in audit_results.items():
        lines.extend([
            f"## {product.replace('_', ' ').title()}",
            "",
        ])
        
        if result.errors:
            lines.append("### Errors")
            for err in result.errors:
                lines.append(f"- [X] {err}")
            lines.append("")
        
        if result.warnings:
            lines.append("### Warnings")
            for warn in result.warnings:
                lines.append(f"- [!] {warn}")
            lines.append("")
        
        if result.requires_elevation:
            lines.append("> **Note:** Admin privileges required for full audit")
            lines.append("")
        
        if result.exceptions:
            lines.extend([
                "### Exceptions",
                "",
                "| Status | Type | Path |",
                "|--------|------|------|",
            ])
            
            for exc in result.exceptions:
                status = "[OK]" if exc.exists else "[STALE]"
                lines.append(f"| {status} | {exc.exception_type} | `{exc.path}` |")
            
            lines.append("")
        else:
            lines.append("*No exceptions found*")
            lines.append("")
    
    # Recommendations
    if recommendations:
        lines.extend([
            "---",
            "",
            "## Recommendations",
            "",
        ])
        
        if recommendations.get("missing"):
            lines.extend([
                "### Missing Exceptions (Should Add)",
                "",
                "| Name | Path | Reason |",
                "|------|------|--------|",
            ])
            
            for rec in recommendations["missing"]:
                lines.append(f"| {rec['name']} | `{rec['path']}` | {rec['reason']} |")
            
            lines.append("")
        
        if recommendations.get("already_covered"):
            lines.extend([
                "### Already Covered",
                "",
            ])
            
            for rec in recommendations["already_covered"]:
                lines.append(f"- [OK] {rec['name']}: `{rec['path']}`")
            
            lines.append("")
    
    # Cleanup recommendations
    stale_list = [e for r in audit_results.values() for e in r.exceptions if not e.exists]
    if stale_list:
        lines.extend([
            "---",
            "",
            "## Cleanup Recommendations",
            "",
            "The following exceptions point to paths that no longer exist:",
            "",
        ])
        
        for exc in stale_list:
            lines.append(f"- `{exc.path}` ({exc.product})")
        
        lines.append("")
        lines.append("Run `securityaudit cleanup --dry-run` to preview removal.")
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "*Report generated by SecurityExceptionAuditor (Team Brain)*",
    ])
    
    return "\n".join(lines)


def generate_json_report(audit_results: Dict[str, AuditResult], recommendations: Dict = None) -> str:
    """Generate a JSON audit report."""
    report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "platform": platform.system(),
            "platform_release": platform.release(),
            "tool_version": VERSION,
        },
        "summary": {
            "total_exceptions": sum(r.total_count for r in audit_results.values()),
            "active_exceptions": sum(r.active_count for r in audit_results.values()),
            "stale_exceptions": sum(r.stale_count for r in audit_results.values()),
            "products_audited": list(audit_results.keys()),
        },
        "products": {k: v.to_dict() for k, v in audit_results.items()},
    }
    
    if recommendations:
        report["recommendations"] = recommendations
    
    return json.dumps(report, indent=2)


# =============================================================================
# CLI
# =============================================================================

def cmd_audit(args):
    """Execute audit command."""
    auditor = SecurityExceptionAuditor()
    
    # Determine products to audit
    if args.product:
        products = [args.product]
    else:
        products = auditor.get_available_products()
    
    if not products:
        print("[X] No security products available to audit on this system")
        return 1
    
    print(f"[*] Auditing: {', '.join(products)}")
    print()
    
    # Run audit
    results = auditor.audit(products)
    
    # Generate recommendations if requested
    recommendations = None
    if args.recommend:
        recommendations = auditor.generate_recommendations()
    
    # Generate report
    if args.format == "json":
        report = generate_json_report(results, recommendations)
    else:
        report = generate_markdown_report(results, recommendations)
    
    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report, encoding='utf-8')
        print(f"[OK] Report saved to: {output_path}")
    else:
        print(report)
    
    # Summary
    total_stale = sum(r.stale_count for r in results.values())
    if total_stale > 0:
        print()
        print(f"[!] Found {total_stale} stale exception(s) - run 'securityaudit cleanup' to review")
    
    return 0


def cmd_recommend(args):
    """Execute recommend command."""
    auditor = SecurityExceptionAuditor()
    
    print("[*] Generating Team Brain whitelist recommendations...")
    print()
    
    recommendations = auditor.generate_recommendations()
    
    if args.format == "json":
        output = json.dumps(recommendations, indent=2)
    else:
        # Markdown format
        lines = [
            "# Team Brain Security Whitelist Recommendations",
            "",
            f"**Generated:** {recommendations['generated_at']}",
            f"**Platform:** {recommendations['platform']}",
            "",
        ]
        
        if recommendations["missing"]:
            lines.extend([
                "## Missing Exceptions (Action Required)",
                "",
                "These Team Brain tools/paths should be added to your security exceptions:",
                "",
            ])
            
            for rec in recommendations["missing"]:
                lines.append(f"### {rec['name']}")
                lines.append(f"- **Path:** `{rec['path']}`")
                lines.append(f"- **Reason:** {rec['reason']}")
                lines.append(f"- **Category:** {rec['category']}")
                if rec.get("ports"):
                    lines.append(f"- **Ports:** {', '.join(map(str, rec['ports']))}")
                lines.append("")
        else:
            lines.append("## [OK] All Team Brain paths are already covered!")
            lines.append("")
        
        if recommendations["already_covered"]:
            lines.extend([
                "## Already Covered",
                "",
            ])
            
            for rec in recommendations["already_covered"]:
                lines.append(f"- [OK] {rec['name']}: `{rec['path']}`")
            lines.append("")
        
        output = "\n".join(lines)
    
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output, encoding='utf-8')
        print(f"[OK] Recommendations saved to: {output_path}")
    else:
        print(output)
    
    # Summary
    missing_count = len(recommendations["missing"])
    if missing_count > 0:
        print()
        print(f"[!] {missing_count} path(s) need to be added to security exceptions")
    else:
        print()
        print("[OK] All Team Brain paths are covered!")
    
    return 0


def cmd_check(args):
    """Execute check command."""
    auditor = SecurityExceptionAuditor()
    
    result = auditor.check_process_and_port(args.process, args.port)
    
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Check Results ({result['timestamp']})")
        print("=" * 50)
        
        if "process" in result:
            status = "[OK] Running" if result["process"]["is_running"] else "[X] Not Running"
            print(f"Process '{result['process']['name']}': {status}")
        
        if "port" in result:
            status = "[OK] In Use" if result["port"]["is_in_use"] else "[X] Not In Use"
            print(f"Port {result['port']['number']}: {status}")
    
    return 0


def cmd_cleanup(args):
    """Execute cleanup command."""
    auditor = SecurityExceptionAuditor()
    
    print("[*] Scanning for stale exceptions...")
    print()
    
    stale = auditor.find_stale_exceptions()
    
    if not stale:
        print("[OK] No stale exceptions found!")
        return 0
    
    print(f"Found {len(stale)} stale exception(s):")
    print()
    
    for exc in stale:
        print(f"  - [{exc.product}] {exc.exception_type}: {exc.path}")
    
    print()
    
    if args.dry_run or not args.apply:
        print("[DRY-RUN] No changes made. Use --apply to remove stale exceptions.")
        print()
        print("Note: Automatic removal is only supported for Windows Defender.")
        print("For other products, please remove manually via their GUI.")
    else:
        print("[!] Removing stale exceptions...")
        
        defender_auditor = WindowsDefenderAuditor()
        
        for exc in stale:
            if exc.product == "defender":
                success, msg = defender_auditor.remove_exclusion(exc.path, dry_run=False)
                status = "[OK]" if success else "[X]"
                print(f"  {status} {msg}")
            else:
                print(f"  [SKIP] {exc.product} - manual removal required")
    
    return 0


def cmd_products(args):
    """List available security products."""
    auditor = SecurityExceptionAuditor()
    
    available = auditor.get_available_products()
    
    print("Available Security Products:")
    print("=" * 40)
    
    for product in available:
        print(f"  [OK] {product}")
    
    # List unavailable
    all_products = list(auditor.auditors.keys())
    unavailable = [p for p in all_products if p not in available]
    
    if unavailable:
        print()
        print("Not Available:")
        for product in unavailable:
            print(f"  [--] {product}")
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="securityaudit",
        description="SecurityExceptionAuditor - Manage security software exceptions for development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  securityaudit audit                           # Audit all available products
  securityaudit audit --product defender        # Audit Windows Defender only
  securityaudit audit --recommend -o report.md  # Full audit with recommendations
  
  securityaudit recommend                       # Team Brain whitelist recommendations
  securityaudit recommend -o whitelist.json -f json
  
  securityaudit check --process python.exe      # Check if process is running
  securityaudit check --port 8000               # Check if port is in use
  
  securityaudit cleanup --dry-run               # Preview stale exception cleanup
  securityaudit cleanup --apply                 # Remove stale exceptions
  
  securityaudit products                        # List available security products

For more information: https://github.com/DonkRonk17/SecurityExceptionAuditor
        """
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"%(prog)s {VERSION}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # audit command
    audit_parser = subparsers.add_parser("audit", help="Audit security exceptions")
    audit_parser.add_argument("--product", "-p", help="Specific product to audit")
    audit_parser.add_argument("--output", "-o", help="Output file path")
    audit_parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    audit_parser.add_argument("--recommend", "-r", action="store_true", help="Include recommendations")
    
    # recommend command
    recommend_parser = subparsers.add_parser("recommend", help="Generate whitelist recommendations")
    recommend_parser.add_argument("--output", "-o", help="Output file path")
    recommend_parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    
    # check command
    check_parser = subparsers.add_parser("check", help="Check process/port status")
    check_parser.add_argument("--process", help="Process name to check")
    check_parser.add_argument("--port", type=int, help="Port number to check")
    check_parser.add_argument("--format", "-f", choices=["text", "json"], default="text")
    
    # cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up stale exceptions")
    cleanup_parser.add_argument("--dry-run", action="store_true", help="Preview only, no changes")
    cleanup_parser.add_argument("--apply", action="store_true", help="Actually remove exceptions")
    
    # products command
    subparsers.add_parser("products", help="List available security products")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    commands = {
        "audit": cmd_audit,
        "recommend": cmd_recommend,
        "check": cmd_check,
        "cleanup": cmd_cleanup,
        "products": cmd_products,
    }
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
