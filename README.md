<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/22076ddb-892a-443e-9e3e-13cbb04a72ed" />

# 🛡️ SecurityExceptionAuditor

**Intelligent Security Exception Manager for Development Environments**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 36 passing](https://img.shields.io/badge/tests-36%20passing-brightgreen.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-green.svg)]()

> **Audit, manage, and optimize security software exceptions for your development environment. Stop debugging blocked connections!**

---

## 📋 Table of Contents

- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
  - [Audit Command](#audit-command)
  - [Recommend Command](#recommend-command)
  - [Check Command](#check-command)
  - [Cleanup Command](#cleanup-command)
  - [Products Command](#products-command)
- [Real-World Results](#-real-world-results)
- [Supported Security Products](#-supported-security-products)
- [Team Brain Whitelist](#-team-brain-whitelist)
- [Python API](#-python-api)
- [How It Works](#-how-it-works)
- [Use Cases](#-use-cases)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Integration](#-integration)
- [Contributing](#-contributing)
- [License](#-license)
- [Credits](#-credits)

---

## 🚨 The Problem

**Security software blocking your development tools is a recurring nightmare:**

- BCH backend gets blocked by Bitdefender Advanced Threat Defense
- Python scripts fail silently due to firewall rules
- Uvicorn servers can't bind to ports
- Node.js network requests timeout mysteriously
- Hours spent debugging "connection refused" errors that are actually security blocks

**The pain points:**

1. **Manual Exception Management** - Adding exceptions one-by-one through clunky GUIs
2. **No Visibility** - Can't easily see what's already excepted
3. **Stale Exceptions** - Old programs remain whitelisted, potential security risk
4. **Missing Exceptions** - New tools constantly need to be added
5. **Repeated Work** - Every new security software update can reset exceptions
6. **Cross-Reference Nightmare** - Is that port blocked? Is that process whitelisted?

**Real Impact:**
- 30+ minutes debugging a "network error" that was Bitdefender blocking Uvicorn
- 2+ hours on BCH mobile connectivity issues caused by firewall rules
- Constant interruptions when security software blocks legitimate dev tools

---

## ✅ The Solution

**SecurityExceptionAuditor provides:**

1. **Complete Audit** - See ALL your security exceptions in one report
2. **Smart Recommendations** - Get tailored whitelist suggestions for your dev tools
3. **Stale Detection** - Find exceptions for programs that no longer exist
4. **Missing Detection** - Know exactly what's NOT covered
5. **Process/Port Checking** - Instantly verify if something is blocked
6. **Cross-Platform** - Windows Defender, Bitdefender, Linux firewalls

**One command to audit:**
```bash
securityaudit audit --recommend -o security_report.md
```

**Result:** Complete visibility into your security configuration in seconds.

---

## ✨ Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| 🔍 **Multi-Product Audit** | Scans Windows Defender, Bitdefender, Windows Firewall, Linux iptables/ufw |
| 📋 **Exception Inventory** | Lists all paths, processes, extensions, and firewall rules |
| 🎯 **Team Brain Whitelist** | Pre-built recommendations for common development tools |
| 🗑️ **Stale Detection** | Identifies exceptions pointing to non-existent paths |
| ➕ **Missing Detection** | Shows which dev tools aren't whitelisted |
| 🔎 **Process Checker** | Verify if a process is running or port is in use |
| 📊 **Multiple Formats** | Output as Markdown, JSON, or text |
| 🔐 **Safe by Default** | Dry-run mode for cleanup operations |

### Key Benefits

- **Zero Dependencies** - Uses only Python standard library
- **Cross-Platform** - Works on Windows and Linux
- **Non-Destructive** - Read-only by default, explicit `--apply` for changes
- **Comprehensive** - Covers paths, processes, extensions, firewall rules
- **Actionable** - Clear recommendations with reasons
- **Fast** - Full audit completes in seconds

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/DonkRonk17/SecurityExceptionAuditor.git
cd SecurityExceptionAuditor
```

### 2. Run Your First Audit

```bash
python securityaudit.py audit
```

**Sample Output:**
```
[*] Auditing: defender, windows_firewall

# Security Exception Audit Report

**Generated:** 2026-01-31 10:30:15
**Platform:** Windows 10.0.26200
**Tool:** SecurityExceptionAuditor v1.0.0

---

## Summary

| Metric | Count |
|--------|-------|
| Total Exceptions | 42 |
| Active (Path Exists) | 38 |
| Stale (Path Missing) | 4 |
| Products Audited | 2 |

...
```

### 3. Get Recommendations

```bash
python securityaudit.py recommend
```

**That's it!** You now know exactly what's covered and what needs attention.

---

## 📦 Installation

### Option 1: Direct Download (Recommended)

```bash
# Clone the repository
git clone https://github.com/DonkRonk17/SecurityExceptionAuditor.git

# Navigate to directory
cd SecurityExceptionAuditor

# Verify it works
python securityaudit.py --version
```

### Option 2: Copy to AutoProjects

```bash
# For Team Brain integration
cp -r SecurityExceptionAuditor "C:\Users\logan\OneDrive\Documents\AutoProjects\"
```

### Option 3: Add to PATH

```bash
# Add to your PATH for global access
# Windows (PowerShell - run as admin):
$env:Path += ";C:\Users\logan\OneDrive\Documents\AutoProjects\SecurityExceptionAuditor"

# Or create an alias
Set-Alias securityaudit "C:\Users\logan\OneDrive\Documents\AutoProjects\SecurityExceptionAuditor\securityaudit.py"
```

### Requirements

- Python 3.8 or higher
- Windows (for Defender/Bitdefender auditing) or Linux (for iptables/ufw)
- No external dependencies!

---

## 📖 Usage

### Audit Command

**Audit all available security products:**
```bash
python securityaudit.py audit
```

**Audit specific product:**
```bash
python securityaudit.py audit --product defender
python securityaudit.py audit --product bitdefender
python securityaudit.py audit --product windows_firewall
```

**Include recommendations:**
```bash
python securityaudit.py audit --recommend
```

**Save to file:**
```bash
python securityaudit.py audit --output report.md
python securityaudit.py audit --output report.json --format json
```

**Full audit with all options:**
```bash
python securityaudit.py audit --recommend --output full_audit.md --format markdown
```

---

### Recommend Command

**Get Team Brain whitelist recommendations:**
```bash
python securityaudit.py recommend
```

**Output:**
```
[*] Generating Team Brain whitelist recommendations...

# Team Brain Security Whitelist Recommendations

## Missing Exceptions (Action Required)

These Team Brain tools/paths should be added to your security exceptions:

### Python Runtime
- **Path:** `C:\Python312Official\python.exe`
- **Reason:** Core runtime for all Team Brain tools
- **Category:** runtime

### Uvicorn ASGI Server
- **Path:** `C:\Python312Official\Scripts\uvicorn.exe`
- **Reason:** BCH backend ASGI server
- **Category:** server
- **Ports:** 8000, 8001, 8080

...

[!] 3 path(s) need to be added to security exceptions
```

**Save recommendations as JSON (for programmatic use):**
```bash
python securityaudit.py recommend --format json --output whitelist.json
```

---

### Check Command

**Check if a process is running:**
```bash
python securityaudit.py check --process python.exe
```

**Output:**
```
Check Results (2026-01-31T10:45:23)
==================================================
Process 'python.exe': [OK] Running
```

**Check if a port is in use:**
```bash
python securityaudit.py check --port 8000
```

**Output:**
```
Check Results (2026-01-31T10:45:30)
==================================================
Port 8000: [OK] In Use
```

**Check both:**
```bash
python securityaudit.py check --process uvicorn --port 8000
```

**JSON output for scripting:**
```bash
python securityaudit.py check --process python.exe --port 8000 --format json
```

---

### Cleanup Command

**Preview stale exceptions (dry-run):**
```bash
python securityaudit.py cleanup --dry-run
```

**Output:**
```
[*] Scanning for stale exceptions...

Found 4 stale exception(s):

  - [defender] path: C:\OldProject\app.exe
  - [defender] folder: D:\Deprecated\Tools\
  - [defender] process: oldtool.exe
  - [bitdefender] path: C:\Uninstalled\program.exe

[DRY-RUN] No changes made. Use --apply to remove stale exceptions.
```

**Actually remove stale exceptions (Windows Defender only):**
```bash
python securityaudit.py cleanup --apply
```

> **Note:** Automatic removal is only supported for Windows Defender. For other products, use their GUI.

---

### Products Command

**List available security products:**
```bash
python securityaudit.py products
```

**Output:**
```
Available Security Products:
========================================
  [OK] defender
  [OK] windows_firewall

Not Available:
  [--] bitdefender
  [--] linux_firewall
```

---

## 📊 Real-World Results

### Before SecurityExceptionAuditor

| Problem | Time Wasted |
|---------|-------------|
| BCH backend blocked by Bitdefender | 30+ minutes |
| Uvicorn port binding failures | 15 minutes |
| "Connection refused" debugging | 45 minutes |
| Manual exception management | 20+ minutes/week |

### After SecurityExceptionAuditor

| Action | Time Required |
|--------|---------------|
| Full security audit | < 30 seconds |
| Generate recommendations | < 10 seconds |
| Identify stale exceptions | < 10 seconds |
| Check process/port status | < 5 seconds |

**Time Savings:** 2+ hours per month for active development

---

## 🔒 Supported Security Products

| Product | Platform | Audit | Add Exception | Remove Exception |
|---------|----------|-------|---------------|------------------|
| Windows Defender | Windows | ✅ Full | ✅ Yes | ✅ Yes |
| Windows Firewall | Windows | ✅ Rules | ❌ Manual | ❌ Manual |
| Bitdefender | Windows | ⚠️ Limited* | ❌ Manual | ❌ Manual |
| iptables | Linux | ✅ Rules | ❌ Manual | ❌ Manual |
| ufw | Linux | ✅ Rules | ❌ Manual | ❌ Manual |

*Bitdefender has limited API access. Results parsed from config files.

---

## 🧠 Team Brain Whitelist

The tool includes a pre-built whitelist of common development tools used by Team Brain:

| Category | Tools |
|----------|-------|
| **Runtime** | Python, Node.js |
| **Server** | Uvicorn, npm |
| **Project** | BCH Backend, AutoProjects |
| **Tools** | Git |
| **IDE** | Cursor |
| **Network** | Tailscale |

**Customize the whitelist** by editing the `TEAM_BRAIN_WHITELIST` dictionary in `securityaudit.py`:

```python
TEAM_BRAIN_WHITELIST = {
    "my_tool": {
        "name": "My Custom Tool",
        "paths": ["C:\\MyTool\\tool.exe"],
        "reason": "Required for my workflow",
        "category": "custom"
    },
    # ... existing entries ...
}
```

---

## 🐍 Python API

Use SecurityExceptionAuditor programmatically:

```python
from securityaudit import SecurityExceptionAuditor

# Initialize
auditor = SecurityExceptionAuditor()

# Check available products
products = auditor.get_available_products()
print(f"Available: {products}")

# Run audit
results = auditor.audit()
for product, result in results.items():
    print(f"{product}: {result.total_count} exceptions ({result.stale_count} stale)")

# Generate recommendations
recommendations = auditor.generate_recommendations()
for missing in recommendations["missing"]:
    print(f"MISSING: {missing['name']} - {missing['path']}")

# Find stale exceptions
stale = auditor.find_stale_exceptions()
for exc in stale:
    print(f"STALE: {exc.path}")

# Check process/port
check = auditor.check_process_and_port(process="python", port=8000)
print(f"Python running: {check['process']['is_running']}")
print(f"Port 8000 in use: {check['port']['is_in_use']}")
```

---

## ⚙️ How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  SecurityExceptionAuditor                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Windows    │  │ Bitdefender │  │   Windows   │         │
│  │  Defender   │  │   Auditor   │  │  Firewall   │         │
│  │   Auditor   │  │ (config     │  │   Auditor   │         │
│  │ (PowerShell)│  │  parsing)   │  │ (netsh)     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Linux     │  │   Process   │  │   Report    │         │
│  │  Firewall   │  │   Checker   │  │  Generator  │         │
│  │(iptables/ufw)  │ (netstat)   │  │ (MD/JSON)   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Detection** - Identify available security products on the system
2. **Collection** - Query each product for exception/rule data
3. **Validation** - Check if each excepted path still exists
4. **Analysis** - Compare against Team Brain whitelist
5. **Reporting** - Generate comprehensive report with recommendations

### Technical Details

- **Windows Defender:** Uses PowerShell `Get-MpPreference` cmdlet
- **Windows Firewall:** Uses PowerShell `Get-NetFirewallRule` cmdlet
- **Bitdefender:** Parses config files in `%ProgramData%\Bitdefender\`
- **Linux:** Queries `ufw status` and `iptables -L`
- **Process Checker:** Uses `netstat` (Windows) or `ss` (Linux)

---

## 🎯 Use Cases

### Use Case 1: New Developer Onboarding

```bash
# Generate complete whitelist for new team member
python securityaudit.py recommend --format json --output team_whitelist.json

# New developer applies these exceptions to their security software
```

### Use Case 2: Debugging "Connection Refused"

```bash
# Quick check if port is blocked
python securityaudit.py check --port 8000 --process uvicorn

# Result: Port 8000: [X] Not In Use
# Action: Add Uvicorn to security exceptions!
```

### Use Case 3: Security Audit After Software Update

```bash
# After security software update, verify exceptions survived
python securityaudit.py audit --recommend

# Compare with previous audit to find removed exceptions
```

### Use Case 4: Quarterly Security Cleanup

```bash
# Find and remove stale exceptions
python securityaudit.py cleanup --dry-run

# Review the list, then:
python securityaudit.py cleanup --apply
```

### Use Case 5: CI/CD Environment Validation

```bash
# Verify build server has correct exceptions
python securityaudit.py recommend --format json | jq '.missing | length'

# If > 0, alert that exceptions need to be added
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECURITYAUDIT_OUTPUT_DIR` | Default output directory | Current directory |
| `SECURITYAUDIT_FORMAT` | Default output format | `markdown` |

### Customizing the Whitelist

Edit `TEAM_BRAIN_WHITELIST` in `securityaudit.py`:

```python
TEAM_BRAIN_WHITELIST = {
    "my_app": {
        "name": "My Application",
        "paths": [
            "C:\\MyApp\\bin\\app.exe",
            "C:\\MyApp\\scripts\\",
        ],
        "ports": [3000, 3001],  # Optional
        "reason": "Required for my workflow",
        "category": "custom"  # runtime, server, project, tools, ide, network
    },
}
```

---

## 🔍 Troubleshooting

### "Access Denied" or "Requires Elevation"

**Problem:** PowerShell commands fail due to permissions.

**Solution:** Run as Administrator:
```bash
# PowerShell (Run as Administrator)
python securityaudit.py audit
```

Or accept partial results:
```bash
# Will show what can be read without elevation
python securityaudit.py audit
# Note: Report will indicate what requires elevation
```

### "Bitdefender not detected"

**Problem:** Bitdefender audit returns no results.

**Solution:** 
1. Bitdefender may be installed in a non-standard location
2. Config files may have different structure in your version
3. Export exceptions manually from Bitdefender GUI and use as reference

### "No firewall rules found"

**Problem:** Windows Firewall audit is empty.

**Solution:**
1. Ensure Windows Firewall service is running
2. Run as Administrator for full access
3. Check if Group Policy restricts access

### PowerShell Execution Policy

**Problem:** Scripts won't run due to execution policy.

**Solution:**
```powershell
# Temporarily allow scripts (current session only)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Then run the audit
python securityaudit.py audit
```

---

## 🔗 Integration

### With Team Brain Tools

```python
from securityaudit import SecurityExceptionAuditor
from synapselink import quick_send

# Run audit
auditor = SecurityExceptionAuditor()
recommendations = auditor.generate_recommendations()

# Alert team if exceptions are missing
if recommendations["missing"]:
    quick_send(
        "TEAM",
        "Security Exceptions Needed",
        f"{len(recommendations['missing'])} paths need whitelisting",
        priority="HIGH"
    )
```

### With EnvGuard

SecurityExceptionAuditor complements EnvGuard:
- **EnvGuard:** Validates `.env` configuration
- **SecurityExceptionAuditor:** Validates security exceptions

```bash
# Full environment health check
python -m envguard scan .
python securityaudit.py audit --recommend
```

### With APIProbe

```bash
# Validate API config AND security exceptions
python -m apiprobe validate-all
python securityaudit.py check --port 8000
```

**See:** [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) for detailed integration guides.

---

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/ecd6fccf-9dbe-44a3-b6eb-14364cfe119f" />


## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Code Style

- Follow PEP 8
- Add type hints
- Include docstrings
- No Unicode emojis in Python code (ASCII only: `[OK]`, `[X]`, `[!]`)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 📝 Credits

**Built by:** FORGE (Team Brain)  
**For:** Logan Smith / Metaphy LLC  
**Requested by:** FORGE (Tool Request #29)  
**Why:** Logan has accumulated many security exceptions with no easy way to audit or manage them. Every new tool triggers the same pain point.  
**Part of:** Beacon HQ / Team Brain Ecosystem  
**Date:** January 31, 2026

**Special Thanks:**
- Logan Smith for identifying this recurring pain point
- Team Brain collective for the Q-Mode tool ecosystem
- EnvGuard and APIProbe as inspiration for environment health tools

---

## 📚 Additional Resources

- [EXAMPLES.md](EXAMPLES.md) - 10+ working examples
- [CHEAT_SHEET.txt](CHEAT_SHEET.txt) - Quick reference guide
- [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) - Team Brain integration
- [QUICK_START_GUIDES.md](QUICK_START_GUIDES.md) - Agent-specific guides

---

## 🏆 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-31 | Initial release |

---

*Built with precision. Deployed with pride.*  
*Team Brain Standard: 99%+ Quality, Every Time.*

---

```
   _____ _______ _____  _____  _____  ___  ___  ___________ _____ _____ _______ 
  / ____|__   __|  __ \|  __ \|  __ \|__ \|__ \|__   __/ _ \ ____|_   _|__   __|
 | (___    | |  | |__) | |__) | |  | |  ) |  ) |  | | | | | |  |_  | |    | |   
  \___ \   | |  |  _  /|  _  /| |  | | / /  / /   | | | | | |   _| | |    | |   
  ____) |  | |  | | \ \| | \ \| |__| |/ /_ / /_   | | | |_| |  |_  | |    | |   
 |_____/   |_|  |_|  \_\_|  \_\_____/|____|____|  |_|  \___/|_____||_|    |_|   

 For the Maximum Benefit of Life.
 One World. One Family. One Love.
```
