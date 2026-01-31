# SecurityExceptionAuditor - Quick Start Guides

## 📖 ABOUT THESE GUIDES

Each Team Brain agent has a **5-minute quick-start guide** tailored to their role and workflows.

**Choose your guide:**
- [Forge (Orchestrator)](#-forge-quick-start)
- [Atlas (Executor)](#-atlas-quick-start)
- [Clio (Linux Agent)](#-clio-quick-start)
- [Nexus (Multi-Platform)](#-nexus-quick-start)
- [Bolt (Free Executor)](#-bolt-quick-start)
- [Iris (Desktop Development)](#-iris-quick-start)
- [Porter (Mobile Development)](#-porter-quick-start)

---

## 🔥 FORGE QUICK START

**Role:** Orchestrator / Reviewer  
**Time:** 5 minutes  
**Goal:** Learn to validate team environment and identify security blockers

### Step 1: Installation Check

```bash
# Navigate to tool
cd C:\Users\logan\OneDrive\Documents\AutoProjects\SecurityExceptionAuditor

# Verify installation
python securityaudit.py --version
# Expected: securityaudit 1.0.0
```

### Step 2: Run Your First Audit

```bash
python securityaudit.py audit --recommend
```

This shows:
- All current security exceptions
- Which Team Brain paths are missing
- Which exceptions are stale (old programs)

### Step 3: Quick Health Check (Use This Daily)

```python
# Add to your session startup
from securityaudit import SecurityExceptionAuditor

def quick_security_check():
    auditor = SecurityExceptionAuditor()
    recommendations = auditor.generate_recommendations()
    
    if recommendations["missing"]:
        print(f"[!] {len(recommendations['missing'])} security exceptions missing")
        return False
    else:
        print("[OK] Security configuration healthy")
        return True

# Run at session start
quick_security_check()
```

### Step 4: When to Use in Orchestration

**Before assigning network tasks:**
```python
# Check if BCH ports are accessible
from securityaudit import SecurityExceptionAuditor

auditor = SecurityExceptionAuditor()
check = auditor.check_process_and_port(port=8000)

if not check["port"]["is_in_use"]:
    print("[!] BCH backend not running - check security exceptions")
```

### Common Forge Commands

```bash
# Quick audit
python securityaudit.py audit

# Full report with recommendations
python securityaudit.py audit --recommend -o forge_audit.md

# Check if port is blocked
python securityaudit.py check --port 8000

# JSON for scripting
python securityaudit.py recommend --format json
```

### Next Steps for Forge
1. Add to session startup routine
2. Use before assigning BCH tasks
3. Review [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) for full integration

---

## ⚡ ATLAS QUICK START

**Role:** Executor / Builder  
**Time:** 5 minutes  
**Goal:** Validate build environment before tool creation

### Step 1: Installation Check

```bash
# Verify tool is available
python -c "from securityaudit import SecurityExceptionAuditor; print('[OK] SecurityExceptionAuditor available')"
```

### Step 2: Pre-Build Validation

**Before starting a new tool build:**

```bash
# Check if Python is whitelisted
python securityaudit.py recommend

# Check if build ports are available
python securityaudit.py check --port 8000 --process python.exe
```

### Step 3: Integration with Build Workflow

```python
# atlas_build_validation.py
from securityaudit import SecurityExceptionAuditor

def validate_before_build():
    """Run before starting a new tool build."""
    auditor = SecurityExceptionAuditor()
    
    # Check runtime whitelisting
    recommendations = auditor.generate_recommendations()
    
    critical_missing = [
        item for item in recommendations["missing"]
        if item.get("category") in ["runtime", "server"]
    ]
    
    if critical_missing:
        print("[!] Critical exceptions missing:")
        for item in critical_missing:
            print(f"    - {item['name']}: {item['path']}")
        print("Add these before building!")
        return False
    
    print("[OK] Build environment validated")
    return True

# Run before each build
validate_before_build()
```

### Step 4: Debug Build Failures

When tests fail with network errors:

```bash
# 1. Check if test server port is available
python securityaudit.py check --port 8080

# 2. Check if Python is blocked
python securityaudit.py check --process python.exe

# 3. Get full audit
python securityaudit.py audit --recommend
```

### Common Atlas Commands

```bash
# Pre-build validation
python securityaudit.py recommend

# Check test server port
python securityaudit.py check --port 8080

# Full environment audit
python securityaudit.py audit --product defender

# Debug network issues
python securityaudit.py check --process python.exe --port 8000
```

### Next Steps for Atlas
1. Add validation to Holy Grail Protocol
2. Run before each tool build
3. Include in test debugging workflow

---

## 🐧 CLIO QUICK START

**Role:** Linux / CLI Agent  
**Time:** 5 minutes  
**Goal:** Audit Linux firewall rules and server security

### Step 1: Linux Installation

```bash
# Clone repository
git clone https://github.com/DonkRonk17/SecurityExceptionAuditor.git
cd SecurityExceptionAuditor

# Verify
python3 securityaudit.py --version
```

### Step 2: Check Available Products

```bash
python3 securityaudit.py products
```

**Expected Output:**
```
Available Security Products:
========================================
  [OK] linux_firewall

Not Available:
  [--] defender
  [--] bitdefender
  [--] windows_firewall
```

### Step 3: Audit Linux Firewall

```bash
# Basic audit (may need sudo)
python3 securityaudit.py audit

# Full audit with sudo
sudo python3 securityaudit.py audit
```

### Step 4: Check Server Ports

```bash
# Check if service port is open
python3 securityaudit.py check --port 8000

# Check if service is running
python3 securityaudit.py check --process uvicorn

# Combined check
python3 securityaudit.py check --process python3 --port 8000
```

### Step 5: Integration with ABIOS

```bash
# Add to ABIOS startup script
#!/bin/bash

echo "=== Security Audit ==="
python3 /path/to/securityaudit.py audit --format json > /tmp/security.json

missing=$(cat /tmp/security.json | jq '.recommendations.missing | length')
if [ "$missing" -gt 0 ]; then
    echo "[!] $missing security exceptions need attention"
fi
```

### Common Clio Commands

```bash
# Linux firewall audit
python3 securityaudit.py audit --product linux_firewall

# Check port (common ports)
python3 securityaudit.py check --port 22    # SSH
python3 securityaudit.py check --port 80    # HTTP
python3 securityaudit.py check --port 443   # HTTPS
python3 securityaudit.py check --port 8000  # API

# Save audit report
python3 securityaudit.py audit -o /var/log/security_audit.md
```

### Next Steps for Clio
1. Add to server provisioning scripts
2. Integrate with monitoring
3. Schedule regular audits

---

## 🌐 NEXUS QUICK START

**Role:** Multi-Platform Agent  
**Time:** 5 minutes  
**Goal:** Cross-platform security validation

### Step 1: Platform Detection

```python
import platform
from securityaudit import SecurityExceptionAuditor

print(f"Platform: {platform.system()}")

auditor = SecurityExceptionAuditor()
print(f"Available: {auditor.get_available_products()}")
```

### Step 2: Cross-Platform Audit

```python
# Works on Windows, Linux, macOS
from securityaudit import SecurityExceptionAuditor

def cross_platform_check():
    auditor = SecurityExceptionAuditor()
    
    # Get available products for this platform
    products = auditor.get_available_products()
    print(f"Auditing: {products}")
    
    # Run audit
    results = auditor.audit()
    
    for product, result in results.items():
        print(f"\n{product}:")
        print(f"  Total: {result.total_count}")
        print(f"  Stale: {result.stale_count}")

cross_platform_check()
```

### Step 3: Platform-Specific Considerations

**Windows:**
```bash
# Uses Windows Defender, Windows Firewall
python securityaudit.py audit --product defender
python securityaudit.py audit --product windows_firewall
```

**Linux:**
```bash
# Uses iptables/ufw
python3 securityaudit.py audit --product linux_firewall
```

**macOS:**
```bash
# Limited support - check products
python3 securityaudit.py products
```

### Common Nexus Commands

```bash
# Platform-agnostic audit
python securityaudit.py audit

# Check what's available
python securityaudit.py products

# JSON output (works everywhere)
python securityaudit.py audit --format json
```

### Next Steps for Nexus
1. Test on all 3 platforms
2. Document platform-specific findings
3. Create cross-platform validation scripts

---

## 🆓 BOLT QUICK START

**Role:** Free Executor (Cline + Grok)  
**Time:** 5 minutes  
**Goal:** Quick pre-deployment validation

### Step 1: Verify Installation

```bash
# No API key required - fully local tool!
python securityaudit.py --version
```

### Step 2: Quick Pre-Deployment Check

```bash
# Before deploying any service
python securityaudit.py check --port 8000

# Check if server process is running
python securityaudit.py check --process uvicorn
```

### Step 3: Batch Validation

```bash
# Check multiple ports quickly
python securityaudit.py check --port 8000
python securityaudit.py check --port 8001
python securityaudit.py check --port 3000
```

### Step 4: Report for Handoff

```bash
# Generate JSON for other tools/agents
python securityaudit.py audit --format json -o audit.json

# Quick status check
python securityaudit.py recommend --format json | grep -c '"missing"'
```

### Common Bolt Commands

```bash
# Quick port check
python securityaudit.py check --port 8000

# Process verification
python securityaudit.py check --process python.exe

# JSON output for automation
python securityaudit.py recommend -f json

# Cleanup preview
python securityaudit.py cleanup --dry-run
```

### Next Steps for Bolt
1. Add to pre-deployment checklist
2. Use for environment validation
3. Report issues via Synapse

---

## 🖥️ IRIS QUICK START

**Role:** Desktop Development (Tauri/Electron)  
**Time:** 5 minutes  
**Goal:** Validate desktop app build environment

### Step 1: Verify Build Tools

```bash
# Check if build tools are whitelisted
python securityaudit.py recommend
```

### Step 2: Desktop Build Environment Check

```python
from securityaudit import SecurityExceptionAuditor

def check_desktop_build_env():
    """Check Tauri/Electron build environment."""
    auditor = SecurityExceptionAuditor()
    
    # Check critical build processes
    processes = ["python", "node", "cargo", "rustc"]
    
    print("Build Tool Status:")
    for proc in processes:
        check = auditor.check_process_and_port(process=proc)
        status = "[OK]" if check["process"]["is_running"] else "[--]"
        print(f"  {status} {proc}")
    
    # Check development ports
    ports = {"Tauri Dev": 1420, "React": 3000, "API": 8000}
    
    print("\nPort Status:")
    for name, port in ports.items():
        check = auditor.check_process_and_port(port=port)
        status = "In Use" if check["port"]["is_in_use"] else "Free"
        print(f"  {name} ({port}): {status}")

check_desktop_build_env()
```

### Step 3: Before Desktop Build

```bash
# Full audit with recommendations
python securityaudit.py audit --recommend -o desktop_audit.md

# Check if Tauri dev port is available
python securityaudit.py check --port 1420
```

### Common Iris Commands

```bash
# Desktop build validation
python securityaudit.py check --process cargo --port 1420

# Full audit
python securityaudit.py audit --recommend

# Check React dev server
python securityaudit.py check --port 3000
```

### Next Steps for Iris
1. Add to Tauri build scripts
2. Run before desktop builds
3. Document Windows/macOS differences

---

## 📱 PORTER QUICK START

**Role:** Mobile Development  
**Time:** 5 minutes  
**Goal:** Validate mobile dev environment

### Step 1: Mobile Dev Environment Check

```bash
# Check Metro bundler port
python securityaudit.py check --port 8081

# Check ADB port (wireless debugging)
python securityaudit.py check --port 5555
```

### Step 2: Pre-Build Validation

```python
from securityaudit import SecurityExceptionAuditor

def check_mobile_env():
    """Check React Native / mobile build environment."""
    auditor = SecurityExceptionAuditor()
    
    # Mobile dev ports
    ports = {
        "Metro Bundler": 8081,
        "ADB Wireless": 5555,
        "API Server": 8000,
    }
    
    print("Mobile Dev Ports:")
    for name, port in ports.items():
        check = auditor.check_process_and_port(port=port)
        status = "Active" if check["port"]["is_in_use"] else "Free"
        print(f"  {name} ({port}): {status}")
    
    # Check Node.js
    check = auditor.check_process_and_port(process="node")
    print(f"\nNode.js: {'Running' if check['process']['is_running'] else 'Not Running'}")

check_mobile_env()
```

### Common Porter Commands

```bash
# Metro bundler check
python securityaudit.py check --port 8081

# ADB port check
python securityaudit.py check --port 5555

# Node.js process
python securityaudit.py check --process node
```

### Next Steps for Porter
1. Add to mobile build scripts
2. Check before running emulator
3. Validate API connectivity

---

## 📚 ADDITIONAL RESOURCES

**For All Agents:**
- Full Documentation: [README.md](README.md)
- Examples: [EXAMPLES.md](EXAMPLES.md)
- Integration Plan: [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md)
- Cheat Sheet: [CHEAT_SHEET.txt](CHEAT_SHEET.txt)

**Support:**
- GitHub Issues: https://github.com/DonkRonk17/SecurityExceptionAuditor/issues
- Synapse: Post in THE_SYNAPSE/active/
- Direct: Contact FORGE

---

**Last Updated:** January 31, 2026  
**Maintained By:** FORGE (Team Brain)
