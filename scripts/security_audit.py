#!/usr/bin/env python3
"""Security audit and assessment tools.

EPIC-027 Story 1: Automated security scanning and reporting.

Usage:
    # Run full security audit
    python scripts/security_audit.py --full

    # Run specific scans
    python scripts/security_audit.py --dependencies --secrets

    # Generate report
    python scripts/security_audit.py --report security-report.json
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Vulnerability:
    """Security vulnerability finding."""

    id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    title: str
    description: str
    location: str
    remediation: str
    references: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "remediation": self.remediation,
            "references": self.references,
        }


@dataclass
class SecurityReport:
    """Complete security audit report."""

    timestamp: str
    summary: dict[str, int] = field(default_factory=dict)
    vulnerabilities: list[Vulnerability] = field(default_factory=list)
    findings: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "summary": self.summary,
            "vulnerabilities": [v.to_dict() for v in self.vulnerabilities],
            "findings": self.findings,
        }


class DependencyScanner:
    """Scan Python dependencies for vulnerabilities."""

    def scan(self) -> list[Vulnerability]:
        """Run pip-audit scan.

        Returns:
            List of vulnerabilities found.
        """
        vulnerabilities = []

        try:
            result = subprocess.run(
                ["pip-audit", "--format=json"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
            )

            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                for vuln in data.get("dependencies", []):
                    if "vulns" in vuln:
                        for v in vuln["vulns"]:
                            vulnerabilities.append(
                                Vulnerability(
                                    id=v.get("id", "UNKNOWN"),
                                    severity=v.get("fix_versions", ["MEDIUM"])[0].upper(),
                                    title=f"Vulnerability in {vuln['name']}",
                                    description=v.get("description", "No description"),
                                    location=f"{vuln['name']}=={vuln['version']}",
                                    remediation=f"Upgrade to: {', '.join(v.get('fix_versions', []))}",
                                    references=v.get("aliases", []),
                                )
                            )
        except FileNotFoundError:
            print("Warning: pip-audit not installed. Run: pip install pip-audit")
        except Exception as e:
            print(f"Dependency scan error: {e}")

        return vulnerabilities


class StaticAnalyzer:
    """Static code analysis with Bandit."""

    SEVERITY_MAP = {
        "HIGH": "HIGH",
        "MEDIUM": "MEDIUM",
        "LOW": "LOW",
    }

    def scan(self, src_dir: str = "src") -> list[Vulnerability]:
        """Run Bandit security scan.

        Args:
            src_dir: Source directory to scan.

        Returns:
            List of security issues.
        """
        vulnerabilities = []

        try:
            result = subprocess.run(
                ["bandit", "-r", src_dir, "-f", "json"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
            )

            if result.stdout:
                data = json.loads(result.stdout)
                for result_item in data.get("results", []):
                    vulnerabilities.append(
                        Vulnerability(
                            id=result_item.get("test_id", "B000"),
                            severity=self.SEVERITY_MAP.get(result_item.get("issue_severity", "LOW"), "LOW"),
                            title=result_item.get("test_name", "Unknown Issue"),
                            description=result_item.get("issue_text", ""),
                            location=f"{result_item.get('filename')}:{result_item.get('line_number')}",
                            remediation=result_item.get("issue_text", ""),
                        )
                    )
        except FileNotFoundError:
            print("Warning: bandit not installed. Run: pip install bandit")
        except Exception as e:
            print(f"Static analysis error: {e}")

        return vulnerabilities


class SecretScanner:
    """Scan for hardcoded secrets."""

    PATTERNS = {
        "aws_access_key": r"AKIA[0-9A-Z]{16}",
        "api_key_generic": r"api[_-]?key\s*[:=]\s*['\"][a-zA-Z0-9]{32,}['\"]",
        "secret_key": r"secret[_-]?key\s*[:=]\s*['\"][a-zA-Z0-9]{32,}['\"]",
        "password": r"password\s*[:=]\s*['\"][^'\"]{8,}['\"]",
        "private_key": r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
        "jwt_token": r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*",
        "slack_token": r"xox[baprs]-[0-9a-zA-Z]{10,48}",
        "github_token": r"gh[pousr]_[A-Za-z0-9_]{36}",
    }

    def scan(self) -> list[Vulnerability]:
        """Scan for secrets in codebase.

        Returns:
            List of potential secrets found.
        """
        import re

        vulnerabilities = []
        root = Path(__file__).parent.parent

        # Files to check
        extensions = {".py", ".json", ".yaml", ".yml", ".env", ".md"}
        exclude_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules"}

        for pattern_name, pattern in self.PATTERNS.items():
            regex = re.compile(pattern, re.IGNORECASE)

            for file_path in root.rglob("*"):
                if file_path.is_dir() or file_path.suffix not in extensions:
                    continue
                if any(excluded in str(file_path) for excluded in exclude_dirs):
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    matches = regex.findall(content)

                    for match in matches:
                        # Skip example/test values
                        if any(fake in match.lower() for fake in ["example", "test", "dummy", "placeholder"]):
                            continue

                        vulnerabilities.append(
                            Vulnerability(
                                id=f"SECRET_{pattern_name.upper()}",
                                severity="CRITICAL",
                                title=f"Potential {pattern_name.replace('_', ' ').title()} Exposed",
                                description=f"Found potential {pattern_name} in source code",
                                location=str(file_path.relative_to(root)),
                                remediation="Remove secret and use environment variables or secret manager",
                                references=[
                                    "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html"
                                ],
                            )
                        )
                except Exception:
                    continue

        return vulnerabilities


class SecurityAuditor:
    """Main security audit orchestrator."""

    def __init__(self):
        """Initialize security auditor."""
        self.dependency_scanner = DependencyScanner()
        self.static_analyzer = StaticAnalyzer()
        self.secret_scanner = SecretScanner()

    def run_full_audit(self) -> SecurityReport:
        """Run complete security audit.

        Returns:
            Security report with all findings.
        """
        print("🔍 Running security audit...")

        report = SecurityReport(
            timestamp=datetime.utcnow().isoformat(),
            vulnerabilities=[],
            findings=[],
        )

        # Dependency scan
        print("  📦 Scanning dependencies...")
        dep_vulns = self.dependency_scanner.scan()
        report.vulnerabilities.extend(dep_vulns)

        # Static analysis
        print("  📝 Running static analysis...")
        static_vulns = self.static_analyzer.scan()
        report.vulnerabilities.extend(static_vulns)

        # Secret scan
        print("  🔐 Scanning for secrets...")
        secret_vulns = self.secret_scanner.scan()
        report.vulnerabilities.extend(secret_vulns)

        # Calculate summary
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for v in report.vulnerabilities:
            severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1

        report.summary = {
            "total": len(report.vulnerabilities),
            **severity_counts,
        }

        return report

    def print_report(self, report: SecurityReport):
        """Print report to console.

        Args:
            report: Security report.
        """
        print("\n" + "=" * 60)
        print("SECURITY AUDIT REPORT")
        print("=" * 60)
        print(f"Timestamp: {report.timestamp}")
        print(f"\nSummary:")
        print(f"  Total: {report.summary.get('total', 0)}")
        print(f"  Critical: {report.summary.get('CRITICAL', 0)} 🔴")
        print(f"  High: {report.summary.get('HIGH', 0)} 🟠")
        print(f"  Medium: {report.summary.get('MEDIUM', 0)} 🟡")
        print(f"  Low: {report.summary.get('LOW', 0)} 🟢")

        if report.vulnerabilities:
            print(f"\nDetailed Findings:")
            for v in report.vulnerabilities[:10]:  # Show first 10
                emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(v.severity, "⚪")
                print(f"\n  {emoji} [{v.severity}] {v.id}")
                print(f"     Title: {v.title}")
                print(f"     Location: {v.location}")
                print(f"     Remediation: {v.remediation[:100]}...")

            if len(report.vulnerabilities) > 10:
                print(f"\n  ... and {len(report.vulnerabilities) - 10} more")

        print("\n" + "=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Security Audit Tool")
    parser.add_argument("--full", action="store_true", help="Run full audit")
    parser.add_argument("--dependencies", action="store_true", help="Scan dependencies only")
    parser.add_argument("--static", action="store_true", help="Run static analysis only")
    parser.add_argument("--secrets", action="store_true", help="Scan for secrets only")
    parser.add_argument("--report", type=str, help="Output report to file")
    parser.add_argument(
        "--fail-on", choices=["critical", "high", "medium"], help="Exit with error if findings at level"
    )

    args = parser.parse_args()

    auditor = SecurityAuditor()

    # Default to full audit if no specific scan selected
    if not any([args.dependencies, args.static, args.secrets]):
        args.full = True

    if args.full:
        report = auditor.run_full_audit()
    else:
        report = SecurityReport(
            timestamp=datetime.utcnow().isoformat(),
            vulnerabilities=[],
        )

        if args.dependencies:
            report.vulnerabilities.extend(auditor.dependency_scanner.scan())
        if args.static:
            report.vulnerabilities.extend(auditor.static_analyzer.scan())
        if args.secrets:
            report.vulnerabilities.extend(auditor.secret_scanner.scan())

    # Print report
    auditor.print_report(report)

    # Save report
    if args.report:
        with open(args.report, "w") as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"\n📄 Report saved to: {args.report}")

    # Exit with error if configured
    if args.fail_on:
        levels = {"critical": ["CRITICAL"], "high": ["CRITICAL", "HIGH"], "medium": ["CRITICAL", "HIGH", "MEDIUM"]}
        threshold = levels.get(args.fail_on, [])
        count = sum(1 for v in report.vulnerabilities if v.severity in threshold)
        if count > 0:
            print(f"\n❌ Failing due to {count} {args.fail_on}+ severity issues")
            sys.exit(1)

    # Exit with error if critical found
    critical_count = report.summary.get("CRITICAL", 0)
    if critical_count > 0:
        print(f"\n❌ {critical_count} critical vulnerabilities found")
        sys.exit(1)

    print("\n✅ Security audit passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
