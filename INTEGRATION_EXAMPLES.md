# SecurityExceptionAuditor - Integration Examples

## 🎯 INTEGRATION PHILOSOPHY

SecurityExceptionAuditor is designed to work seamlessly with other Team Brain tools. This document provides **copy-paste-ready code examples** for common integration patterns.

---

## 📚 TABLE OF CONTENTS

1. [Pattern 1: SecurityExceptionAuditor + EnvGuard](#pattern-1-securityexceptionauditor--envguard)
2. [Pattern 2: SecurityExceptionAuditor + SynapseLink](#pattern-2-securityexceptionauditor--synapselink)
3. [Pattern 3: SecurityExceptionAuditor + APIProbe](#pattern-3-securityexceptionauditor--apiprobe)
4. [Pattern 4: SecurityExceptionAuditor + AgentHealth](#pattern-4-securityexceptionauditor--agenthealth)
5. [Pattern 5: SecurityExceptionAuditor + TaskQueuePro](#pattern-5-securityexceptionauditor--taskqueuepro)
6. [Pattern 6: SecurityExceptionAuditor + MemoryBridge](#pattern-6-securityexceptionauditor--memorybridge)
7. [Pattern 7: SecurityExceptionAuditor + SessionReplay](#pattern-7-securityexceptionauditor--sessionreplay)
8. [Pattern 8: SecurityExceptionAuditor + BuildEnvValidator](#pattern-8-securityexceptionauditor--buildenvvalidator)
9. [Pattern 9: Multi-Tool Environment Validation](#pattern-9-multi-tool-environment-validation)
10. [Pattern 10: Full Team Brain Stack](#pattern-10-full-team-brain-stack)

---

## Pattern 1: SecurityExceptionAuditor + EnvGuard

**Use Case:** Complete environment health check combining config validation with security validation.

**Why:** EnvGuard checks `.env` configuration, SecurityExceptionAuditor checks security exceptions. Together they provide comprehensive environment validation.

**Code:**

```python
#!/usr/bin/env python3
"""Combined environment validation with EnvGuard + SecurityExceptionAuditor."""

import sys
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\EnvGuard")
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\SecurityExceptionAuditor")

from envguard import EnvGuard
from securityaudit import SecurityExceptionAuditor

def full_environment_validation(project_path: str) -> dict:
    """
    Validate both configuration and security.
    
    Returns:
        dict: Validation results with issues list
    """
    results = {
        "config_valid": True,
        "security_valid": True,
        "issues": []
    }
    
    # EnvGuard: Check .env configuration
    env_guard = EnvGuard()
    env_result = env_guard.scan(project_path)
    
    if env_result.conflicts:
        results["config_valid"] = False
        results["issues"].append(f"EnvGuard: {len(env_result.conflicts)} config conflicts")
        for conflict in env_result.conflicts[:3]:
            results["issues"].append(f"  - {conflict}")
    
    if env_result.missing:
        results["config_valid"] = False
        results["issues"].append(f"EnvGuard: {len(env_result.missing)} missing values")
    
    # SecurityExceptionAuditor: Check security exceptions
    auditor = SecurityExceptionAuditor()
    recommendations = auditor.generate_recommendations()
    
    if recommendations["missing"]:
        results["security_valid"] = False
        results["issues"].append(
            f"Security: {len(recommendations['missing'])} missing exceptions"
        )
        for item in recommendations["missing"][:3]:
            results["issues"].append(f"  - {item['name']}: {item['path']}")
    
    # Check for stale exceptions
    stale = auditor.find_stale_exceptions()
    if stale:
        results["issues"].append(f"Security: {len(stale)} stale exceptions to clean up")
    
    return results


# Example usage
if __name__ == "__main__":
    results = full_environment_validation("D:\\BEACON_HQ\\PROJECTS\\00_ACTIVE\\BCH_APPS")
    
    if results["issues"]:
        print("[!] Environment issues found:")
        for issue in results["issues"]:
            print(f"    {issue}")
    else:
        print("[OK] Environment fully validated!")
```

**Result:** Single function to validate entire development environment.

---

## Pattern 2: SecurityExceptionAuditor + SynapseLink

**Use Case:** Automatically alert Team Brain when security issues are detected.

**Why:** Proactive monitoring keeps team informed without manual status checks.

**Code:**

```python
#!/usr/bin/env python3
"""Alert Team Brain about security exceptions via SynapseLink."""

import sys
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\SynapseLink")
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\SecurityExceptionAuditor")

from synapselink import quick_send
from securityaudit import SecurityExceptionAuditor

def security_health_check_with_alert():
    """
    Run security audit and alert team if issues found.
    """
    auditor = SecurityExceptionAuditor()
    
    # Get recommendations
    recommendations = auditor.generate_recommendations()
    missing_count = len(recommendations["missing"])
    
    # Find stale exceptions
    stale = auditor.find_stale_exceptions()
    stale_count = len(stale)
    
    # Build alert message if issues found
    if missing_count > 0 or stale_count > 0:
        message = f"""Security Exception Audit Alert

Missing Exceptions: {missing_count}
Stale Exceptions: {stale_count}

"""
        if missing_count > 0:
            message += "MISSING (should add):\n"
            for item in recommendations["missing"][:5]:
                message += f"  - {item['name']}: {item['path']}\n"
            if missing_count > 5:
                message += f"  ... and {missing_count - 5} more\n"
        
        if stale_count > 0:
            message += "\nSTALE (should remove):\n"
            for exc in stale[:5]:
                message += f"  - {exc.path}\n"
            if stale_count > 5:
                message += f"  ... and {stale_count - 5} more\n"
        
        message += "\nRun 'securityaudit audit --recommend' for details."
        
        # Send alert
        quick_send(
            "FORGE,LOGAN",
            "Security Exceptions Need Attention",
            message,
            priority="NORMAL"
        )
        print(f"[OK] Alert sent: {missing_count} missing, {stale_count} stale")
        return False
    else:
        print("[OK] Security configuration healthy - no alert needed")
        return True


# Example usage
if __name__ == "__main__":
    security_health_check_with_alert()
```

**Result:** Team automatically notified when security attention needed.

---

## Pattern 3: SecurityExceptionAuditor + APIProbe

**Use Case:** Validate API configuration AND security exceptions together.

**Why:** API failures can be caused by security blocks - check both!

**Code:**

```python
#!/usr/bin/env python3
"""Combined API + Security validation."""

import sys
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\APIProbe")
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\SecurityExceptionAuditor")

from apiprobe import APIProbe
from securityaudit import SecurityExceptionAuditor

def validate_api_environment(api_port: int = 8000):
    """
    Validate API is properly configured AND accessible.
    
    Args:
        api_port: Port the API should be running on
        
    Returns:
        dict: Validation results
    """
    results = {
        "api_config_valid": False,
        "port_accessible": False,
        "security_ok": False,
        "issues": []
    }
    
    # APIProbe: Validate API configuration
    try:
        probe = APIProbe()
        results["api_config_valid"] = probe.validate_all()
        if not results["api_config_valid"]:
            results["issues"].append("API configuration issues detected")
    except Exception as e:
        results["issues"].append(f"APIProbe error: {e}")
    
    # SecurityExceptionAuditor: Check port and process
    auditor = SecurityExceptionAuditor()
    
    check = auditor.check_process_and_port(process="uvicorn", port=api_port)
    
    results["port_accessible"] = check["port"]["is_in_use"]
    
    if not check["process"]["is_running"]:
        results["issues"].append("Uvicorn process not running")
    
    if not check["port"]["is_in_use"]:
        results["issues"].append(f"Port {api_port} not in use - server not started?")
    
    # Check if server is whitelisted
    recommendations = auditor.generate_recommendations()
    server_missing = [
        item for item in recommendations["missing"]
        if item.get("category") == "server"
    ]
    
    if server_missing:
        results["issues"].append("Server paths not whitelisted in security software")
        for item in server_missing:
            results["issues"].append(f"  - {item['name']}")
    else:
        results["security_ok"] = True
    
    return results


# Example usage
if __name__ == "__main__":
    results = validate_api_environment(8000)
    
    if results["issues"]:
        print("[!] API Environment Issues:")
        for issue in results["issues"]:
            print(f"    {issue}")
    else:
        print("[OK] API environment fully validated!")
        print(f"    API Config: OK")
        print(f"    Port 8000: Active")
        print(f"    Security: OK")
```

**Result:** Complete API environment validation in one call.

---

## Pattern 4: SecurityExceptionAuditor + AgentHealth

**Use Case:** Include security status in agent health monitoring.

**Why:** Security issues affect agent health - track them together.

**Code:**

```python
#!/usr/bin/env python3
"""Include security status in agent health tracking."""

import sys
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\AgentHealth")
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\SecurityExceptionAuditor")

from agenthealth import AgentHealth
from securityaudit import SecurityExceptionAuditor

def start_health_session_with_security(agent_name: str) -> str:
    """
    Start agent health session with security metadata.
    
    Args:
        agent_name: Name of the agent (e.g., "FORGE", "ATLAS")
        
    Returns:
        str: Session ID
    """
    health = AgentHealth()
    auditor = SecurityExceptionAuditor()
    
    # Start health session
    session_id = health.start_session(agent_name)
    
    # Get security status
    recommendations = auditor.generate_recommendations()
    stale = auditor.find_stale_exceptions()
    
    # Add security metadata
    security_status = "OK" if not recommendations["missing"] else "NEEDS_ATTENTION"
    
    health.log_metadata(session_id, {
        "security_status": security_status,
        "security_missing_count": len(recommendations["missing"]),
        "security_stale_count": len(stale),
        "security_products": auditor.get_available_products(),
    })
    
    # Log heartbeat with security info
    health.heartbeat(
        agent_name,
        status="active",
        context=f"Security: {security_status}"
    )
    
    return session_id


def end_health_session_with_security_report(agent_name: str, session_id: str):
    """
    End session with final security audit.
    """
    health = AgentHealth()
    auditor = SecurityExceptionAuditor()
    
    # Final security check
    audit_results = auditor.audit()
    total_exceptions = sum(r.total_count for r in audit_results.values())
    
    health.log_metadata(session_id, {
        "final_security_exceptions": total_exceptions,
    })
    
    health.end_session(agent_name, session_id=session_id)


# Example usage
if __name__ == "__main__":
    session_id = start_health_session_with_security("ATLAS")
    print(f"Started session with security: {session_id}")
    
    # ... do work ...
    
    end_health_session_with_security_report("ATLAS", session_id)
    print("Session ended with security report")
```

**Result:** Security metrics tracked as part of agent health.

---

## Pattern 5: SecurityExceptionAuditor + TaskQueuePro

**Use Case:** Automatically create tasks for security remediation.

**Why:** Convert audit findings into actionable tasks.

**Code:**

```python
#!/usr/bin/env python3
"""Create tasks for security issues."""

import sys
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\TaskQueuePro")
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\SecurityExceptionAuditor")

from taskqueuepro import TaskQueuePro
from securityaudit import SecurityExceptionAuditor

def create_security_remediation_tasks():
    """
    Audit security and create tasks for any issues found.
    """
    queue = TaskQueuePro()
    auditor = SecurityExceptionAuditor()
    
    tasks_created = []
    
    # Check for missing exceptions
    recommendations = auditor.generate_recommendations()
    
    if recommendations["missing"]:
        missing_paths = [item["path"] for item in recommendations["missing"]]
        
        task_id = queue.create_task(
            title=f"Add {len(recommendations['missing'])} missing security exceptions",
            description=(
                f"The following paths need to be whitelisted:\n" +
                "\n".join(f"- {path}" for path in missing_paths)
            ),
            agent="LOGAN",  # Human task
            priority=2,
            metadata={
                "type": "security_add_exceptions",
                "paths": missing_paths
            }
        )
        tasks_created.append(("add_exceptions", task_id))
        print(f"[OK] Created task: Add {len(missing_paths)} exceptions")
    
    # Check for stale exceptions
    stale = auditor.find_stale_exceptions()
    
    if stale:
        stale_paths = [exc.path for exc in stale]
        
        task_id = queue.create_task(
            title=f"Remove {len(stale)} stale security exceptions",
            description=(
                f"The following exceptions point to non-existent paths:\n" +
                "\n".join(f"- {path}" for path in stale_paths[:10]) +
                (f"\n... and {len(stale) - 10} more" if len(stale) > 10 else "")
            ),
            agent="LOGAN",
            priority=3,
            metadata={
                "type": "security_cleanup",
                "paths": stale_paths
            }
        )
        tasks_created.append(("cleanup", task_id))
        print(f"[OK] Created task: Remove {len(stale)} stale exceptions")
    
    if not tasks_created:
        print("[OK] No security tasks needed - environment healthy!")
    
    return tasks_created


# Example usage
if __name__ == "__main__":
    tasks = create_security_remediation_tasks()
    print(f"\nCreated {len(tasks)} task(s)")
```

**Result:** Security issues become trackable tasks.

---

## Pattern 6: SecurityExceptionAuditor + MemoryBridge

**Use Case:** Persist security audit history for trend analysis.

**Why:** Track security configuration changes over time.

**Code:**

```python
#!/usr/bin/env python3
"""Persist security audit history to memory core."""

import sys
from datetime import datetime

sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\MemoryBridge")
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\SecurityExceptionAuditor")

from memorybridge import MemoryBridge
from securityaudit import SecurityExceptionAuditor

def audit_with_history():
    """
    Run audit and store results in memory for historical tracking.
    """
    memory = MemoryBridge()
    auditor = SecurityExceptionAuditor()
    
    # Run audit
    results = auditor.audit()
    recommendations = auditor.generate_recommendations()
    
    # Load existing history
    audit_history = memory.get("security_audit_history", default=[])
    
    # Create audit entry
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "total_exceptions": sum(r.total_count for r in results.values()),
        "active_exceptions": sum(r.active_count for r in results.values()),
        "stale_exceptions": sum(r.stale_count for r in results.values()),
        "missing_count": len(recommendations["missing"]),
        "products_audited": list(results.keys()),
    }
    
    # Add to history
    audit_history.append(audit_entry)
    
    # Keep last 30 audits
    audit_history = audit_history[-30:]
    
    # Save
    memory.set("security_audit_history", audit_history)
    memory.sync()
    
    print(f"[OK] Audit saved to memory. Total history: {len(audit_history)} entries")
    
    # Trend analysis
    if len(audit_history) >= 2:
        prev = audit_history[-2]
        curr = audit_entry
        
        change = curr["stale_exceptions"] - prev["stale_exceptions"]
        if change > 0:
            print(f"[!] Stale exceptions increased by {change}")
        elif change < 0:
            print(f"[OK] Stale exceptions decreased by {abs(change)}")
    
    return audit_entry


# Example usage
if __name__ == "__main__":
    entry = audit_with_history()
    print(f"\nCurrent status:")
    print(f"  Total: {entry['total_exceptions']}")
    print(f"  Stale: {entry['stale_exceptions']}")
    print(f"  Missing: {entry['missing_count']}")
```

**Result:** Historical audit data for trend analysis.

---

## Pattern 7: SecurityExceptionAuditor + SessionReplay

**Use Case:** Record security checks as part of session replay.

**Why:** Debug session failures by seeing security state at each step.

**Code:**

```python
#!/usr/bin/env python3
"""Include security checks in session replay logging."""

import sys
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\SessionReplay")
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\SecurityExceptionAuditor")

from sessionreplay import SessionReplay
from securityaudit import SecurityExceptionAuditor

def session_with_security_logging(agent_name: str, task: str):
    """
    Start session with security state logged for replay.
    """
    replay = SessionReplay()
    auditor = SecurityExceptionAuditor()
    
    # Start session
    session_id = replay.start_session(agent_name, task=task)
    
    # Log initial security state
    recommendations = auditor.generate_recommendations()
    
    replay.log_event(session_id, "security_check", {
        "type": "initial_audit",
        "missing_count": len(recommendations["missing"]),
        "missing_paths": [item["path"] for item in recommendations["missing"][:5]],
    })
    
    # Check critical ports
    critical_ports = [8000, 8001, 3000]
    port_status = {}
    
    for port in critical_ports:
        check = auditor.check_process_and_port(port=port)
        port_status[port] = check["port"]["is_in_use"]
    
    replay.log_event(session_id, "port_check", {
        "ports": port_status
    })
    
    return session_id, replay


def end_session_with_security(replay: SessionReplay, session_id: str):
    """
    End session with final security check.
    """
    auditor = SecurityExceptionAuditor()
    
    # Final security state
    recommendations = auditor.generate_recommendations()
    
    replay.log_event(session_id, "security_check", {
        "type": "final_audit",
        "missing_count": len(recommendations["missing"]),
    })
    
    replay.end_session(session_id, status="COMPLETED")


# Example usage
if __name__ == "__main__":
    session_id, replay = session_with_security_logging("ATLAS", "Tool Build")
    print(f"Session started: {session_id}")
    
    # ... do work ...
    
    end_session_with_security(replay, session_id)
    print("Session ended with security logging")
```

**Result:** Security state preserved for session debugging.

---

## Pattern 8: SecurityExceptionAuditor + BuildEnvValidator

**Use Case:** Complete build environment validation.

**Why:** BuildEnvValidator checks tools, SecurityExceptionAuditor checks they're not blocked.

**Code:**

```python
#!/usr/bin/env python3
"""Combined build environment + security validation."""

import sys
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\BuildEnvValidator")
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects\\SecurityExceptionAuditor")

from buildenvvalidator import BuildEnvValidator
from securityaudit import SecurityExceptionAuditor

def complete_build_validation(project_type: str = "python"):
    """
    Validate build tools AND security configuration.
    
    Args:
        project_type: Type of project (python, nodejs, rust, etc.)
    """
    print(f"=== Build Environment Validation ({project_type}) ===\n")
    
    issues = []
    
    # BuildEnvValidator: Check tools are installed
    print("[1/2] Checking build tools...")
    validator = BuildEnvValidator()
    build_result = validator.validate(project_type)
    
    if not build_result.success:
        issues.extend(build_result.errors)
        print(f"    [X] Build tools: {len(build_result.errors)} issues")
    else:
        print("    [OK] Build tools validated")
    
    # SecurityExceptionAuditor: Check tools are whitelisted
    print("\n[2/2] Checking security exceptions...")
    auditor = SecurityExceptionAuditor()
    
    # Check if runtime is whitelisted
    recommendations = auditor.generate_recommendations()
    
    runtime_missing = [
        item for item in recommendations["missing"]
        if item.get("category") == "runtime"
    ]
    
    if runtime_missing:
        for item in runtime_missing:
            issues.append(f"Security: {item['name']} not whitelisted")
        print(f"    [X] Security: {len(runtime_missing)} runtime(s) not whitelisted")
    else:
        print("    [OK] Runtime tools whitelisted")
    
    # Summary
    print("\n" + "=" * 50)
    if issues:
        print(f"[!] Validation FAILED - {len(issues)} issue(s):")
        for issue in issues:
            print(f"    - {issue}")
        return False
    else:
        print("[OK] Build environment READY")
        return True


# Example usage
if __name__ == "__main__":
    complete_build_validation("python")
```

**Result:** Single command validates entire build environment.

---

## Pattern 9: Multi-Tool Environment Validation

**Use Case:** Comprehensive environment check using multiple tools.

**Why:** Real production validation needs multiple perspectives.

**Code:**

```python
#!/usr/bin/env python3
"""Multi-tool environment validation workflow."""

import sys
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects")

def full_environment_validation():
    """
    Run comprehensive environment validation.
    """
    print("=" * 60)
    print("FULL ENVIRONMENT VALIDATION")
    print("=" * 60)
    
    results = {}
    
    # 1. Security Exception Audit
    print("\n[1/4] Security Exceptions...")
    try:
        from SecurityExceptionAuditor.securityaudit import SecurityExceptionAuditor
        auditor = SecurityExceptionAuditor()
        recommendations = auditor.generate_recommendations()
        
        results["security"] = {
            "status": "OK" if not recommendations["missing"] else "ISSUES",
            "missing": len(recommendations["missing"]),
            "stale": len(auditor.find_stale_exceptions())
        }
        print(f"    Status: {results['security']['status']}")
        print(f"    Missing: {results['security']['missing']}")
    except ImportError:
        results["security"] = {"status": "UNAVAILABLE"}
        print("    [--] SecurityExceptionAuditor not available")
    
    # 2. Port Availability
    print("\n[2/4] Critical Ports...")
    try:
        ports = {8000: "BCH API", 8001: "BCH Alt", 3000: "Frontend"}
        for port, name in ports.items():
            check = auditor.check_process_and_port(port=port)
            status = "Active" if check["port"]["is_in_use"] else "Free"
            print(f"    Port {port} ({name}): {status}")
    except:
        print("    [--] Port check unavailable")
    
    # 3. EnvGuard (if available)
    print("\n[3/4] Environment Configuration...")
    try:
        from EnvGuard.envguard import EnvGuard
        env = EnvGuard()
        # Quick check
        results["envguard"] = {"status": "OK"}
        print("    [OK] EnvGuard available")
    except ImportError:
        results["envguard"] = {"status": "UNAVAILABLE"}
        print("    [--] EnvGuard not available")
    
    # 4. API Probe (if available)
    print("\n[4/4] API Configuration...")
    try:
        from APIProbe.apiprobe import APIProbe
        results["apiprobe"] = {"status": "OK"}
        print("    [OK] APIProbe available")
    except ImportError:
        results["apiprobe"] = {"status": "UNAVAILABLE"}
        print("    [--] APIProbe not available")
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    all_ok = all(
        r.get("status") in ["OK", "UNAVAILABLE"]
        for r in results.values()
    )
    
    if all_ok:
        print("[OK] Environment ready for development!")
    else:
        print("[!] Issues detected - review above results")
    
    return results


# Example usage
if __name__ == "__main__":
    full_environment_validation()
```

**Result:** One-command full environment validation.

---

## Pattern 10: Full Team Brain Stack

**Use Case:** Production-grade workflow using all tools.

**Why:** This is how a real session should start.

**Code:**

```python
#!/usr/bin/env python3
"""
Full Team Brain session startup with security.
This is the complete pattern for starting a new session.
"""

import sys
from datetime import datetime

# Add all tools to path
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects")

def team_brain_session_start(agent_name: str, task: str):
    """
    Complete session startup with full validation.
    
    Args:
        agent_name: Name of agent starting session
        task: Description of the task
    """
    print("=" * 60)
    print(f"TEAM BRAIN SESSION START: {agent_name}")
    print(f"Task: {task}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    session_data = {
        "agent": agent_name,
        "task": task,
        "started_at": datetime.now().isoformat(),
        "checks": {}
    }
    
    # 1. Security Check
    print("\n[SECURITY CHECK]")
    try:
        from SecurityExceptionAuditor.securityaudit import SecurityExceptionAuditor
        auditor = SecurityExceptionAuditor()
        recommendations = auditor.generate_recommendations()
        
        if recommendations["missing"]:
            print(f"  [!] {len(recommendations['missing'])} exceptions missing")
            for item in recommendations["missing"][:3]:
                print(f"      - {item['name']}")
            session_data["checks"]["security"] = "ISSUES"
        else:
            print("  [OK] Security configuration healthy")
            session_data["checks"]["security"] = "OK"
    except Exception as e:
        print(f"  [--] Security check failed: {e}")
        session_data["checks"]["security"] = "ERROR"
    
    # 2. Port Check (for network tasks)
    print("\n[PORT CHECK]")
    try:
        critical_ports = [8000, 8001]
        for port in critical_ports:
            check = auditor.check_process_and_port(port=port)
            status = "Active" if check["port"]["is_in_use"] else "Free"
            print(f"  Port {port}: {status}")
    except:
        print("  [--] Port check skipped")
    
    # 3. Synapse Check
    print("\n[SYNAPSE CHECK]")
    try:
        from SynapseLink.synapselink import check_unread
        unread = check_unread(agent_name)
        if unread:
            print(f"  [!] {len(unread)} unread Synapse messages")
        else:
            print("  [OK] No unread messages")
    except:
        print("  [--] Synapse check skipped")
    
    # Ready to work
    print("\n" + "=" * 60)
    print(f"SESSION READY - {agent_name} can begin work")
    print("=" * 60)
    
    return session_data


# Example usage
if __name__ == "__main__":
    team_brain_session_start("FORGE", "Tool Review")
```

**Result:** Complete session startup with all validations.

---

## 📊 RECOMMENDED INTEGRATION PRIORITY

**Week 1 (Essential):**
1. ✅ SynapseLink - Team notifications
2. ✅ EnvGuard - Combined validation
3. ✅ APIProbe - API + security check

**Week 2 (Productivity):**
4. ☐ TaskQueuePro - Task creation
5. ☐ AgentHealth - Health metrics
6. ☐ MemoryBridge - History tracking

**Week 3 (Advanced):**
7. ☐ SessionReplay - Debug logging
8. ☐ BuildEnvValidator - Build validation
9. ☐ Full stack integration

---

## 🔧 TROUBLESHOOTING INTEGRATIONS

**Import Errors:**
```python
# Ensure tools are in Python path
import sys
sys.path.insert(0, "C:\\Users\\logan\\OneDrive\\Documents\\AutoProjects")

# Then import
from SecurityExceptionAuditor.securityaudit import SecurityExceptionAuditor
```

**Version Conflicts:**
```bash
# Check tool versions
python -c "from securityaudit import VERSION; print(VERSION)"
```

**Configuration Issues:**
```python
# Reset and retry
auditor = SecurityExceptionAuditor()
products = auditor.get_available_products()
print(f"Available: {products}")
```

---

**Last Updated:** January 31, 2026  
**Maintained By:** FORGE (Team Brain)
