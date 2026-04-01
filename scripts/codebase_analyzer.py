#!/usr/bin/env python3
"""
Solstein Comprehensive Codebase Analyzer
Runs hourly to identify anti-patterns, gaps, and improvement opportunities
"""

import ast
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class AntiPattern:
    name: str
    severity: str  # critical, high, medium, low
    location: str
    line_number: int
    description: str
    recommendation: str
    category: str  # architecture, quality, performance, security

@dataclass
class Metric:
    name: str
    value: float
    target: float
    status: str  # pass, warn, fail

class CodebaseAnalyzer:
    def __init__(self, src_dir: str = "src/solstein"):
        self.src_dir = Path(src_dir)
        self.anti_patterns: list[AntiPattern] = []
        self.metrics: list[Metric] = []
        self.files_analyzed = 0
        self.total_lines = 0
        
    def analyze_all(self):
        """Run complete analysis"""
        print("🔍 Starting Solstein codebase analysis...")
        
        self._analyze_file_sizes()
        self._analyze_function_sizes()
        self._analyze_import_cycles()
        self._analyze_code_smells()
        self._analyze_async_patterns()
        self._analyze_test_coverage()
        self._analyze_documentation()
        self._calculate_metrics()
        
        print(f"✅ Analyzed {self.files_analyzed} files ({self.total_lines} lines)")
        print(f"🚨 Found {len(self.anti_patterns)} anti-patterns")
        
    def _analyze_file_sizes(self):
        """Find oversized files"""
        for py_file in self.src_dir.rglob("*.py"):
            self.files_analyzed += 1
            lines = len(py_file.read_text().splitlines())
            self.total_lines += lines
            
            if lines > 800:
                self.anti_patterns.append(AntiPattern(
                    name="God File",
                    severity="high",
                    location=str(py_file.relative_to(self.src_dir)),
                    line_number=1,
                    description=f"File has {lines} lines (limit: 500)",
                    recommendation="Split into multiple modules by responsibility",
                    category="architecture"
                ))
            elif lines > 600:
                self.anti_patterns.append(AntiPattern(
                    name="Large File",
                    severity="medium",
                    location=str(py_file.relative_to(self.src_dir)),
                    line_number=1,
                    description=f"File has {lines} lines (target: <500)",
                    recommendation="Consider splitting large files",
                    category="architecture"
                ))
                
    def _analyze_function_sizes(self):
        """Find oversized functions"""
        for py_file in self.src_dir.rglob("*.py"):
            try:
                tree = ast.parse(py_file.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_lines = node.end_lineno - node.lineno
                        if func_lines > 100:
                            self.anti_patterns.append(AntiPattern(
                                name="God Function",
                                severity="high",
                                location=f"{py_file.relative_to(self.src_dir)}:{node.lineno}",
                                line_number=node.lineno,
                                description=f"Function '{node.name}' has {func_lines} lines",
                                recommendation="Extract helper functions, apply Single Responsibility Principle",
                                category="quality"
                            ))
                        elif func_lines > 50:
                            self.anti_patterns.append(AntiPattern(
                                name="Long Function",
                                severity="medium",
                                location=f"{py_file.relative_to(self.src_dir)}:{node.lineno}",
                                line_number=node.lineno,
                                description=f"Function '{node.name}' has {func_lines} lines (target: <50)",
                                recommendation="Consider breaking into smaller functions",
                                category="quality"
                            ))
                            
                        # Check parameter count
                        param_count = len(node.args.args) + len(node.args.kwonlyargs)
                        if param_count > 7:
                            self.anti_patterns.append(AntiPattern(
                                name="Long Parameter List",
                                severity="medium",
                                location=f"{py_file.relative_to(self.src_dir)}:{node.lineno}",
                                line_number=node.lineno,
                                description=f"Function '{node.name}' has {param_count} parameters",
                                recommendation="Use data classes or kwargs for grouped parameters",
                                category="quality"
                            ))
            except SyntaxError:
                continue
                
    def _analyze_import_cycles(self):
        """Detect circular imports"""
        try:
            result = subprocess.run(
                ["python3", "scripts/ci/detect_import_cycles.py"],
                capture_output=True,
                text=True,
                cwd=self.src_dir.parent.parent
            )
            if result.returncode != 0 and "circular" in result.stdout.lower():
                self.anti_patterns.append(AntiPattern(
                    name="Circular Import",
                    severity="critical",
                    location="Multiple files",
                    line_number=0,
                    description="Circular dependencies detected",
                    recommendation="Refactor to break cycles using interfaces or dependency injection",
                    category="architecture"
                ))
        except Exception:
            pass
            
    def _analyze_code_smells(self):
        """Find common code smells"""
        for py_file in self.src_dir.rglob("*.py"):
            content = py_file.read_text()
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                # Bare except
                if re.match(r'^\s*except\s*:', line):
                    self.anti_patterns.append(AntiPattern(
                        name="Bare Except Clause",
                        severity="high",
                        location=f"{py_file.relative_to(self.src_dir)}:{i}",
                        line_number=i,
                        description="Bare 'except:' catches KeyboardInterrupt, SystemExit",
                        recommendation="Use 'except Exception:' or specific exception types",
                        category="quality"
                    ))
                
                # Lazy imports
                if re.match(r'^\s*from\s+.*\s+import\s+', line) and 'def ' in content[:content.find(line)]:
                    # Check if import is inside a function
                    func_start = content.rfind('def ', 0, content.find(line))
                    if func_start > 0:
                        self.anti_patterns.append(AntiPattern(
                            name="Lazy Import",
                            severity="medium",
                            location=f"{py_file.relative_to(self.src_dir)}:{i}",
                            line_number=i,
                            description="Import inside function (lazy import)",
                            recommendation="Move imports to top of file to avoid circular deps",
                            category="architecture"
                        ))
                        
    def _analyze_async_patterns(self):
        """Check for async/sync mixing issues"""
        for py_file in self.src_dir.rglob("*.py"):
            content = py_file.read_text()
            
            # Check for blocking calls in async functions
            blocking_patterns = [
                (r'async def.*:\s*\n.*time\.sleep\(', "Blocking time.sleep() in async function"),
                (r'async def.*:\s*\n.*requests\.(get|post)', "Blocking requests in async function"),
                (r'async def.*:\s*\n.*open\(.*[\"\']r', "Blocking file I/O in async function"),
            ]
            
            for pattern, description in blocking_patterns:
                if re.search(pattern, content, re.MULTILINE):
                    self.anti_patterns.append(AntiPattern(
                        name="Blocking Operation in Async",
                        severity="high",
                        location=str(py_file.relative_to(self.src_dir)),
                        line_number=0,
                        description=description,
                        recommendation="Use async equivalents (httpx, aiofiles, asyncio.sleep)",
                        category="performance"
                    ))
                    
    def _analyze_test_coverage(self):
        """Analyze test gaps"""
        tests_dir = self.src_dir.parent.parent / "tests"
        src_files = list(self.src_dir.rglob("*.py"))
        test_files = list(tests_dir.rglob("test_*.py")) if tests_dir.exists() else []
        
        src_count = len([f for f in src_files if not f.name.startswith('_')])
        test_count = len(test_files)
        
        ratio = test_count / src_count if src_count > 0 else 0
        
        if ratio < 0.5:
            self.anti_patterns.append(AntiPattern(
                name="Low Test Coverage",
                severity="high",
                location="tests/",
                line_number=0,
                description=f"Test-to-source ratio: {ratio:.2f} (target: 1.0+)",
                recommendation="Add unit tests for all public functions",
                category="quality"
            ))
            
    def _analyze_documentation(self):
        """Check documentation coverage"""
        for py_file in self.src_dir.rglob("*.py"):
            content = py_file.read_text()
            
            # Check for docstrings
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        if not node.name.startswith('_'):  # Skip private
                            self.anti_patterns.append(AntiPattern(
                                name="Missing Docstring",
                                severity="low",
                                location=f"{py_file.relative_to(self.src_dir)}:{node.lineno}",
                                line_number=node.lineno,
                                description=f"{node.__class__.__name__} '{node.name}' has no docstring",
                                recommendation="Add docstring explaining purpose and usage",
                                category="quality"
                            ))
                            
    def _calculate_metrics(self):
        """Calculate overall metrics"""
        avg_file_size = self.total_lines / self.files_analyzed if self.files_analyzed > 0 else 0
        
        self.metrics.append(Metric(
            name="Average File Size",
            value=avg_file_size,
            target=300,
            status="pass" if avg_file_size < 300 else "warn" if avg_file_size < 500 else "fail"
        ))
        
        critical_count = sum(1 for ap in self.anti_patterns if ap.severity == "critical")
        high_count = sum(1 for ap in self.anti_patterns if ap.severity == "high")
        
        self.metrics.append(Metric(
            name="Code Smell Density",
            value=len(self.anti_patterns) / self.total_lines * 1000 if self.total_lines > 0 else 0,
            target=0.3,
            status="pass" if critical_count == 0 and high_count < 10 else "fail"
        ))
        
    def generate_report(self, output_dir: str):
        """Generate comprehensive analysis report"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Generate comprehensive report
        report_file = output_path / f"ANALYSIS_REPORT_{timestamp}.md"
        with open(report_file, 'w') as f:
            f.write(self._generate_markdown_report())
            
        # Generate anti-patterns catalog
        catalog_file = output_path / f"ANTIPATTERNS_CATALOG_{timestamp}.md"
        with open(catalog_file, 'w') as f:
            f.write(self._generate_antipatterns_catalog())
            
        # Generate metrics JSON
        metrics_file = output_path / f"METRICS_{timestamp}.json"
        with open(metrics_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "files_analyzed": self.files_analyzed,
                "total_lines": self.total_lines,
                "anti_patterns_count": len(self.anti_patterns),
                "metrics": [asdict(m) for m in self.metrics],
                "anti_patterns": [asdict(ap) for ap in self.anti_patterns]
            }, f, indent=2)
            
        # Generate EPICs and Stories
        self._generate_epics_and_stories(output_path, timestamp)
        
        print(f"📄 Reports generated in: {output_path}")
        print(f"   - {report_file.name}")
        print(f"   - {catalog_file.name}")
        print(f"   - {metrics_file.name}")
        
    def _generate_markdown_report(self) -> str:
        """Generate markdown analysis report"""
        critical = [ap for ap in self.anti_patterns if ap.severity == "critical"]
        high = [ap for ap in self.anti_patterns if ap.severity == "high"]
        medium = [ap for ap in self.anti_patterns if ap.severity == "medium"]
        low = [ap for ap in self.anti_patterns if ap.severity == "low"]
        
        report = f"""# 🔍 Solstein Codebase Analysis Report

> **Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
> **Files Analyzed:** {self.files_analyzed}  
> **Total Lines:** {self.total_lines:,}  
> **Anti-Patterns Found:** {len(self.anti_patterns)}

---

## 📊 Executive Summary

### Key Findings
- {'🚨' if critical else '✅'} {len(critical)} Critical issues requiring immediate attention
- {'⚠️' if high else '✅'} {len(high)} High priority issues to fix this sprint
- {'💡' if medium else '✅'} {len(medium)} Medium priority improvements
- {'ℹ️' if low else '✅'} {len(low)} Low priority suggestions

### Metrics
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
"""
        for metric in self.metrics:
            status_emoji = "✅" if metric.status == "pass" else "⚠️" if metric.status == "warn" else "🚨"
            report += f"| {metric.name} | {metric.value:.2f} | {metric.target:.2f} | {status_emoji} {metric.status.upper()} |\n"
            
        report += """
---

## 🚨 Critical Issues (Fix Immediately)

"""
        for ap in critical[:10]:  # Top 10
            report += f"""### {ap.name}
- **Location:** `{ap.location}`
- **Description:** {ap.description}
- **Recommendation:** {ap.recommendation}

"""
            
        report += """---

## ⚠️ High Priority (Fix This Sprint)

"""
        for ap in high[:15]:  # Top 15
            report += f"""### {ap.name}
- **Location:** `{ap.location}`
- **Description:** {ap.description}
- **Recommendation:** {ap.recommendation}

"""
            
        report += """---

## 💡 Medium Priority (Fix This Month)

"""
        for ap in medium[:10]:
            report += f"- **{ap.name}** in `{ap.location}`: {ap.description[:80]}...\n"
            
        report += """
---

## 📁 Category Breakdown

### Architecture Issues
"""
        arch_issues = [ap for ap in self.anti_patterns if ap.category == "architecture"]
        for ap in arch_issues[:10]:
            report += f"- [{ap.severity.upper()}] {ap.name}: `{ap.location}`\n"
            
        report += """
### Code Quality Issues
"""
        quality_issues = [ap for ap in self.anti_patterns if ap.category == "quality"]
        for ap in quality_issues[:10]:
            report += f"- [{ap.severity.upper()}] {ap.name}: `{ap.location}`\n"
            
        report += """
### Performance Issues
"""
        perf_issues = [ap for ap in self.anti_patterns if ap.category == "performance"]
        for ap in perf_issues[:10]:
            report += f"- [{ap.severity.upper()}] {ap.name}: `{ap.location}`\n"
            
        report += """
---

## 🎯 Recommended Actions

### Immediate (Today)
"""
        for ap in critical[:3]:
            report += f"1. Fix {ap.name} in `{ap.location}`\n"
            
        report += """
### This Week
"""
        for ap in high[:5]:
            report += f"1. Address {ap.name} in `{ap.location}`\n"
            
        report += """
---

*Report generated by Solstein Codebase Analyzer*
"""
        return report
        
    def _generate_antipatterns_catalog(self) -> str:
        """Generate anti-patterns catalog"""
        catalog = """# 📚 Anti-Patterns Catalog

> **Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This catalog documents all anti-patterns found in the codebase for reference and training.

---

"""
        # Group by category
        by_category = {}
        for ap in self.anti_patterns:
            if ap.category not in by_category:
                by_category[ap.category] = []
            by_category[ap.category].append(ap)
            
        for category, patterns in by_category.items():
            catalog += f"## {category.upper()} Anti-Patterns\n\n"
            for ap in patterns:
                catalog += f"""### {ap.name}
**Severity:** {ap.severity.upper()}  
**Location:** `{ap.location}`  
**Description:** {ap.description}  
**Recommendation:** {ap.recommendation}  

---

"""
        return catalog
        
    def _generate_epics_and_stories(self, output_path: Path, timestamp: str):
        """Generate EPICs and Stories from anti-patterns"""
        
        # Group anti-patterns into logical EPICs
        epics = []
        
        # EPIC 1: God Objects & Functions
        god_patterns = [ap for ap in self.anti_patterns if "God" in ap.name or "Large" in ap.name]
        if god_patterns:
            epic_num = len(epics) + 51
            epic_file = output_path / f"EPIC_{epic_num}_GOD_OBJECT_REFACTORING.md"
            with open(epic_file, 'w') as f:
                f.write(f"""# EPIC-{epic_num}: God Object & Function Refactoring

## Problem Statement
The codebase contains {len(god_patterns)} god objects, large files, or oversized functions that violate Single Responsibility Principle and make testing, maintenance, and onboarding difficult.

## Business Impact
- Harder to onboard new developers
- Increased bug risk (more code = more bugs)
- Slower feature development
- Difficult to test thoroughly

## Success Criteria
- [ ] Zero files >600 lines
- [ ] Zero functions >80 lines
- [ ] All classes <300 lines
- [ ] Improved test coverage for refactored code

## Stories

| ID | Title | Points | Priority |
|----|-------|--------|----------|
""")
                for i, ap in enumerate(god_patterns[:10], 1):
                    f.write(f"| STORY-{epic_num}.{i} | Refactor {ap.name} in {ap.location} | 5 | P{0 if ap.severity == 'critical' else 1} |\n")
                    
                f.write("""
## Anti-Patterns Addressed

""")
                for ap in god_patterns[:10]:
                    f.write(f"- {ap.name}: `{ap.location}`\n")
                    
            epics.append(epic_num)
            
        # EPIC 2: Code Quality Improvements
        quality_patterns = [ap for ap in self.anti_patterns if ap.category == "quality" and ap.severity in ["high", "critical"]]
        if quality_patterns:
            epic_num = len(epics) + 51
            epic_file = output_path / f"EPIC_{epic_num}_CODE_QUALITY_IMPROVEMENTS.md"
            with open(epic_file, 'w') as f:
                f.write(f"""# EPIC-{epic_num}: Code Quality Improvements

## Problem Statement
{len(quality_patterns)} code quality issues identified including bare except clauses, missing docstrings, and long parameter lists.

## Success Criteria
- [ ] Zero bare except clauses
- [ ] All public functions have docstrings
- [ ] No function with >5 parameters
- [ ] Code smell density <0.3 per 100 lines

## Stories

| ID | Title | Points | Priority |
|----|-------|--------|----------|
""")
                seen = set()
                story_num = 1
                for ap in quality_patterns[:15]:
                    key = f"{ap.name}-{ap.location}"
                    if key not in seen:
                        seen.add(key)
                        f.write(f"| STORY-{epic_num}.{story_num} | Fix {ap.name} in {ap.location} | 3 | P1 |\n")
                        story_num += 1
                        
            epics.append(epic_num)
            
        # EPIC 3: Async Pattern Fixes
        async_patterns = [ap for ap in self.anti_patterns if "Async" in ap.name or "Blocking" in ap.name]
        if async_patterns:
            epic_num = len(epics) + 51
            epic_file = output_path / f"EPIC_{epic_num}_ASYNC_PATTERN_FIXES.md"
            with open(epic_file, 'w') as f:
                f.write(f"""# EPIC-{epic_num}: Async Pattern Fixes

## Problem Statement
{len(async_patterns)} instances of blocking operations in async functions detected, causing performance degradation and potential event loop blocking.

## Success Criteria
- [ ] Zero blocking I/O in async functions
- [ ] All external calls use async libraries
- [ ] Response time improved by 50%

## Stories

| ID | Title | Points | Priority |
|----|-------|--------|----------|
""")
                for i, ap in enumerate(async_patterns[:10], 1):
                    f.write(f"| STORY-{epic_num}.{i} | Fix {ap.name} in {ap.location} | 3 | P0 |\n")
                    
            epics.append(epic_num)
            
        # EPIC 4: Architecture Improvements
        arch_patterns = [ap for ap in self.anti_patterns if ap.category == "architecture"]
        if arch_patterns:
            epic_num = len(epics) + 51
            epic_file = output_path / f"EPIC_{epic_num}_ARCHITECTURE_IMPROVEMENTS.md"
            with open(epic_file, 'w') as f:
                f.write(f"""# EPIC-{epic_num}: Architecture Improvements

## Problem Statement
{len(arch_patterns)} architectural issues including circular imports, layer violations, and tight coupling.

## Success Criteria
- [ ] Zero circular imports
- [ ] Clear layer boundaries (domain/infrastructure/api)
- [ ] Dependency injection used consistently
- [ ] All modules have clear responsibilities

## Stories

| ID | Title | Points | Priority |
|----|-------|--------|----------|
""")
                seen = set()
                story_num = 1
                for ap in arch_patterns[:10]:
                    key = f"{ap.name}-{ap.location}"
                    if key not in seen:
                        seen.add(key)
                        f.write(f"| STORY-{epic_num}.{story_num} | Address {ap.name} in {ap.location} | 5 | P1 |\n")
                        story_num += 1
                        
            epics.append(epic_num)
            
        print(f"📝 Generated {len(epics)} new EPICs")


def main():
    """Main entry point"""
    analyzer = CodebaseAnalyzer()
    analyzer.analyze_all()
    
    output_dir = ".analysis-output/runs"
    analyzer.generate_report(output_dir)
    
    # Create/update latest symlink
    latest_link = Path(".analysis-output/latest")
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    latest_link.symlink_to(Path(output_dir).name, target_is_directory=True)
    
    print("\n✅ Analysis complete!")
    print(f"📊 Found {len(analyzer.anti_patterns)} anti-patterns")
    print(f"📁 Reports saved to: {output_dir}")


if __name__ == "__main__":
    main()
