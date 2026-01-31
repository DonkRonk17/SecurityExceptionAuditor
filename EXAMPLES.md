# SecurityExceptionAuditor - Usage Examples

**Quick Navigation:**
- [Example 1: Basic Audit](#example-1-basic-audit)
- [Example 2: Full Audit with Recommendations](#example-2-full-audit-with-recommendations)
- [Example 3: Audit Specific Product](#example-3-audit-specific-product)
- [Example 4: Generate Team Brain Whitelist](#example-4-generate-team-brain-whitelist)
- [Example 5: Check Process Status](#example-5-check-process-status)
- [Example 6: Check Port Status](#example-6-check-port-status)
- [Example 7: Combined Process and Port Check](#example-7-combined-process-and-port-check)
- [Example 8: Find Stale Exceptions](#example-8-find-stale-exceptions)
- [Example 9: JSON Output for Automation](#example-9-json-output-for-automation)
- [Example 10: Python API Usage](#example-10-python-api-usage)
- [Example 11: Integration with SynapseLink](#example-11-integration-with-synapselink)
- [Example 12: CI/CD Validation Script](#example-12-cicd-validation-script)

---

## Example 1: Basic Audit

**Scenario:** You want to see all your current security exceptions.

**Command:**
```bash
python securityaudit.py audit
```

**Expected Output:**
```
[*] Auditing: defender, windows_firewall

# Security Exception Audit Report

**Generated:** 2026-01-31 14:30:15
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

## Windows Defender

### Exceptions

| Status | Type | Path |
|--------|------|------|
| [OK] | folder | `C:\Python312Official\` |
| [OK] | process | `python.exe` |
| [OK] | folder | `C:\Program Files\nodejs\` |
| [STALE] | path | `C:\OldProject\app.exe` |
| [OK] | extension | `.log` |
...

[!] Found 4 stale exception(s) - run 'securityaudit cleanup' to review
```

**What You Learned:**
- How many total exceptions you have
- Which ones point to paths that no longer exist
- Which security products were audited

---

## Example 2: Full Audit with Recommendations

**Scenario:** You want a complete audit PLUS recommendations for Team Brain tools.

**Command:**
```bash
python securityaudit.py audit --recommend --output full_report.md
```

**Expected Output:**
```
[*] Auditing: defender, windows_firewall

[OK] Report saved to: full_report.md

[!] Found 4 stale exception(s) - run 'securityaudit cleanup' to review
```

**Generated File (full_report.md):**
```markdown
# Security Exception Audit Report

**Generated:** 2026-01-31 14:35:22
...

---

## Recommendations

### Missing Exceptions (Should Add)

| Name | Path | Reason |
|------|------|--------|
| Uvicorn ASGI Server | `C:\Python312Official\Scripts\uvicorn.exe` | BCH backend ASGI server |
| BCH Backend | `D:\BEACON_HQ\PROJECTS\00_ACTIVE\BCH_APPS\backend\` | Beacon Comms Hub backend |

### Already Covered

- [OK] Python Runtime: `C:\Python312Official\python.exe`
- [OK] Node.js: `C:\Program Files\nodejs\node.exe`

---

## Cleanup Recommendations

The following exceptions point to paths that no longer exist:

- `C:\OldProject\app.exe` (defender)
- `D:\Deprecated\Tools\` (defender)
...
```

**What You Learned:**
- Which Team Brain tools are missing from exceptions
- Which ones are already covered
- What stale exceptions should be removed

---

## Example 3: Audit Specific Product

**Scenario:** You only want to audit Windows Defender, not firewall rules.

**Command:**
```bash
python securityaudit.py audit --product defender
```

**Expected Output:**
```
[*] Auditing: defender

# Security Exception Audit Report
...

## Windows Defender

### Exceptions

| Status | Type | Path |
|--------|------|------|
| [OK] | folder | `C:\Python312Official\` |
| [OK] | process | `python.exe` |
...
```

**What You Learned:**
- How to focus on a specific security product
- Faster results when you only need one product

---

## Example 4: Generate Team Brain Whitelist

**Scenario:** You want a list of all paths that Team Brain tools need whitelisted.

**Command:**
```bash
python securityaudit.py recommend
```

**Expected Output:**
```
[*] Generating Team Brain whitelist recommendations...

# Team Brain Security Whitelist Recommendations

**Generated:** 2026-01-31T14:45:00
**Platform:** Windows

## Missing Exceptions (Action Required)

These Team Brain tools/paths should be added to your security exceptions:

### Uvicorn ASGI Server
- **Path:** `C:\Python312Official\Scripts\uvicorn.exe`
- **Reason:** BCH backend ASGI server
- **Category:** server
- **Ports:** 8000, 8001, 8080

### BCH Backend
- **Path:** `D:\BEACON_HQ\PROJECTS\00_ACTIVE\BCH_APPS\backend\`
- **Reason:** Beacon Comms Hub backend API
- **Category:** project

## Already Covered

- [OK] Python Runtime: `C:\Python312Official\python.exe`
- [OK] Node.js: `C:\Program Files\nodejs\node.exe`
- [OK] Git Version Control: `C:\Program Files\Git\`

[!] 2 path(s) need to be added to security exceptions
```

**What You Learned:**
- Exactly which paths need to be added
- Why each path is important
- What's already covered

---

## Example 5: Check Process Status

**Scenario:** Your server isn't working and you want to verify the process is running.

**Command:**
```bash
python securityaudit.py check --process python.exe
```

**Expected Output (if running):**
```
Check Results (2026-01-31T15:00:23)
==================================================
Process 'python.exe': [OK] Running
```

**Expected Output (if not running):**
```
Check Results (2026-01-31T15:00:45)
==================================================
Process 'python.exe': [X] Not Running
```

**What You Learned:**
- Quick way to verify if a process is active
- Helps distinguish "not running" from "blocked"

---

## Example 6: Check Port Status

**Scenario:** You want to know if port 8000 is being used (maybe blocked or already bound).

**Command:**
```bash
python securityaudit.py check --port 8000
```

**Expected Output (if in use):**
```
Check Results (2026-01-31T15:05:12)
==================================================
Port 8000: [OK] In Use
```

**Expected Output (if free):**
```
Check Results (2026-01-31T15:05:30)
==================================================
Port 8000: [X] Not In Use
```

**What You Learned:**
- Quick port availability check
- "Not In Use" could mean blocked OR just not started

---

## Example 7: Combined Process and Port Check

**Scenario:** Debugging BCH backend - is Uvicorn running AND is port 8000 bound?

**Command:**
```bash
python securityaudit.py check --process uvicorn --port 8000
```

**Expected Output:**
```
Check Results (2026-01-31T15:10:00)
==================================================
Process 'uvicorn': [OK] Running
Port 8000: [OK] In Use
```

**Interpretation:**
- If process running but port not in use → Process is running but not bound (config issue)
- If port in use but process not running → Something else is using the port
- If neither → Process not started or killed by security software

**What You Learned:**
- Combined checks help diagnose issues faster
- Correlation between process and port status

---

## Example 8: Find Stale Exceptions

**Scenario:** You want to clean up old exceptions that point to deleted programs.

**Command:**
```bash
python securityaudit.py cleanup --dry-run
```

**Expected Output:**
```
[*] Scanning for stale exceptions...

Found 4 stale exception(s):

  - [defender] path: C:\OldProject\app.exe
  - [defender] folder: D:\Deprecated\Tools\
  - [defender] process: oldtool.exe
  - [bitdefender] path: C:\Uninstalled\program.exe

[DRY-RUN] No changes made. Use --apply to remove stale exceptions.

Note: Automatic removal is only supported for Windows Defender.
For other products, please remove manually via their GUI.
```

**To actually remove (Windows Defender only):**
```bash
python securityaudit.py cleanup --apply
```

**Expected Output:**
```
[*] Scanning for stale exceptions...

Found 4 stale exception(s):
...

[!] Removing stale exceptions...
  [OK] Removed exclusion: C:\OldProject\app.exe
  [OK] Removed exclusion: D:\Deprecated\Tools\
  [OK] Removed exclusion: oldtool.exe
  [SKIP] bitdefender - manual removal required
```

**What You Learned:**
- Always use `--dry-run` first to preview changes
- Only Windows Defender supports automated removal
- Clean up regularly for better security posture

---

## Example 9: JSON Output for Automation

**Scenario:** You want to integrate with other tools or scripts.

**Audit as JSON:**
```bash
python securityaudit.py audit --format json --output audit.json
```

**Recommendations as JSON:**
```bash
python securityaudit.py recommend --format json --output whitelist.json
```

**Check as JSON:**
```bash
python securityaudit.py check --process python.exe --port 8000 --format json
```

**Sample JSON Output:**
```json
{
  "timestamp": "2026-01-31T15:20:00",
  "process": {
    "name": "python.exe",
    "is_running": true
  },
  "port": {
    "number": 8000,
    "is_in_use": true
  }
}
```

**Usage in Script:**
```bash
# Check if any exceptions are missing
missing=$(python securityaudit.py recommend --format json | jq '.missing | length')
if [ "$missing" -gt 0 ]; then
    echo "WARNING: $missing exceptions need to be added!"
fi
```

**What You Learned:**
- JSON output enables scripting and automation
- Can be piped to `jq` or other JSON tools
- Perfect for CI/CD integration

---

## Example 10: Python API Usage

**Scenario:** You want to use SecurityExceptionAuditor in your Python code.

**Code:**
```python
#!/usr/bin/env python3
"""Example: Using SecurityExceptionAuditor as a library."""

from securityaudit import SecurityExceptionAuditor, generate_markdown_report

def main():
    # Initialize the auditor
    auditor = SecurityExceptionAuditor()
    
    # Check what products are available
    products = auditor.get_available_products()
    print(f"Available security products: {products}")
    
    # Run full audit
    print("\n--- Running Audit ---")
    results = auditor.audit()
    
    for product, result in results.items():
        print(f"\n{product}:")
        print(f"  Total: {result.total_count}")
        print(f"  Active: {result.active_count}")
        print(f"  Stale: {result.stale_count}")
        
        if result.errors:
            print(f"  Errors: {result.errors}")
    
    # Generate recommendations
    print("\n--- Recommendations ---")
    recommendations = auditor.generate_recommendations()
    
    if recommendations["missing"]:
        print("Missing exceptions:")
        for item in recommendations["missing"]:
            print(f"  - {item['name']}: {item['path']}")
    else:
        print("All Team Brain paths are covered!")
    
    # Check specific process/port
    print("\n--- Quick Check ---")
    check = auditor.check_process_and_port(process="python", port=8000)
    print(f"Python running: {check['process']['is_running']}")
    print(f"Port 8000 in use: {check['port']['is_in_use']}")
    
    # Generate report
    report = generate_markdown_report(results, recommendations)
    with open("api_report.md", "w") as f:
        f.write(report)
    print("\n[OK] Report saved to api_report.md")

if __name__ == "__main__":
    main()
```

**Expected Output:**
```
Available security products: ['defender', 'windows_firewall']

--- Running Audit ---

defender:
  Total: 42
  Active: 38
  Stale: 4

windows_firewall:
  Total: 15
  Active: 15
  Stale: 0

--- Recommendations ---
Missing exceptions:
  - Uvicorn ASGI Server: C:\Python312Official\Scripts\uvicorn.exe
  - BCH Backend: D:\BEACON_HQ\PROJECTS\00_ACTIVE\BCH_APPS\backend\

--- Quick Check ---
Python running: True
Port 8000 in use: True

[OK] Report saved to api_report.md
```

**What You Learned:**
- Full programmatic access to all features
- Can integrate into larger automation systems
- Results are Python objects for easy processing

---

## Example 11: Integration with SynapseLink

**Scenario:** Alert Team Brain when security exceptions need attention.

**Code:**
```python
#!/usr/bin/env python3
"""Alert Team Brain about missing security exceptions."""

from securityaudit import SecurityExceptionAuditor
from synapselink import quick_send

def check_and_alert():
    auditor = SecurityExceptionAuditor()
    
    # Check recommendations
    recommendations = auditor.generate_recommendations()
    missing_count = len(recommendations["missing"])
    
    # Find stale exceptions
    stale = auditor.find_stale_exceptions()
    stale_count = len(stale)
    
    # Alert if issues found
    if missing_count > 0 or stale_count > 0:
        message = f"""Security Exception Audit Results:

Missing Exceptions: {missing_count}
Stale Exceptions: {stale_count}

"""
        if missing_count > 0:
            message += "MISSING:\n"
            for item in recommendations["missing"]:
                message += f"  - {item['name']}: {item['path']}\n"
        
        if stale_count > 0:
            message += "\nSTALE:\n"
            for exc in stale[:5]:  # First 5
                message += f"  - {exc.path}\n"
        
        message += "\nRun 'securityaudit recommend' for full details."
        
        quick_send(
            "FORGE,LOGAN",
            "Security Exceptions Need Attention",
            message,
            priority="NORMAL"
        )
        print("[OK] Alert sent to Team Brain")
    else:
        print("[OK] All security exceptions are in order!")

if __name__ == "__main__":
    check_and_alert()
```

**What You Learned:**
- Proactive monitoring of security configuration
- Team stays informed without manual checks
- Part of environment health monitoring

---

## Example 12: CI/CD Validation Script

**Scenario:** Validate security exceptions as part of CI/CD pipeline.

**Script (validate_security.py):**
```python
#!/usr/bin/env python3
"""CI/CD: Validate security exceptions before deployment."""

import sys
import json
from securityaudit import SecurityExceptionAuditor

def validate():
    auditor = SecurityExceptionAuditor()
    
    # Check recommendations
    recommendations = auditor.generate_recommendations()
    
    # Count critical missing exceptions
    critical_missing = [
        item for item in recommendations["missing"]
        if item.get("category") in ["runtime", "server"]
    ]
    
    # Output results
    results = {
        "status": "PASS" if not critical_missing else "FAIL",
        "total_missing": len(recommendations["missing"]),
        "critical_missing": len(critical_missing),
        "details": critical_missing
    }
    
    print(json.dumps(results, indent=2))
    
    # Exit code: 0 = pass, 1 = fail
    return 0 if not critical_missing else 1

if __name__ == "__main__":
    sys.exit(validate())
```

**Usage in CI/CD:**
```yaml
# .github/workflows/deploy.yml
jobs:
  validate:
    steps:
      - name: Validate Security Exceptions
        run: python validate_security.py
```

**What You Learned:**
- Security validation as part of deployment
- Fail fast if critical exceptions missing
- JSON output for CI/CD integration

---

## Summary

| Example | Command | Use Case |
|---------|---------|----------|
| 1 | `audit` | Basic overview |
| 2 | `audit --recommend` | Full report with suggestions |
| 3 | `audit --product defender` | Specific product audit |
| 4 | `recommend` | Team Brain whitelist |
| 5 | `check --process X` | Verify process running |
| 6 | `check --port N` | Verify port status |
| 7 | `check --process X --port N` | Combined debugging |
| 8 | `cleanup --dry-run` | Find stale exceptions |
| 9 | `--format json` | Automation-friendly output |
| 10 | Python API | Programmatic access |
| 11 | + SynapseLink | Team notifications |
| 12 | CI/CD script | Deployment validation |

---

*For more information, see [README.md](README.md) and [CHEAT_SHEET.txt](CHEAT_SHEET.txt)*
