#!/usr/bin/env python3
"""
Backlog Metrics Updater

Scans the backlog directory and updates README.md with accurate counts.
Run this after adding/moving stories to keep the dashboard current.

Usage:
    python scripts/update-backlog-metrics.py
    python scripts/update-backlog-metrics.py --check  # Verify without writing
"""

import os
import re
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class BacklogStats:
    total_epics: int
    total_stories: int
    p0_stories: int
    p1_stories: int
    p2_stories: int
    p3_stories: int
    open_stories: int
    in_progress_stories: int
    done_stories: int
    superseded_stories: int


def count_stories_in_file(filepath: Path) -> Tuple[str, str, bool]:
    """Extract priority and status from a story file."""
    content = filepath.read_text()
    
    # Extract priority
    priority_match = re.search(r'\*\*Priority\*\*\s*\|\s*(P[0-3])', content)
    priority = priority_match.group(1) if priority_match else 'Unknown'
    
    # Extract status
    status_match = re.search(r'\*\*Status\*\*\s*\|\s*([🔴🟡🟠🟢⚫])', content)
    status = status_match.group(1) if status_match else '🔴'
    
    # Check if superseded
    is_superseded = '⚫ **SUPERSEDED**' in content or filepath.parent.name == 'superseded'
    
    return priority, status, is_superseded


def scan_backlog(backlog_dir: Path) -> BacklogStats:
    """Scan the backlog directory and collect statistics."""
    epics_dir = backlog_dir / 'EPICS'
    archive_dir = backlog_dir / 'archive'
    
    total_epics = 0
    total_stories = 0
    p0_stories = 0
    p1_stories = 0
    p2_stories = 0
    p3_stories = 0
    open_stories = 0
    in_progress_stories = 0
    done_stories = 0
    superseded_stories = 0
    
    # Count epics (directories in EPICS/)
    if epics_dir.exists():
        total_epics = len([d for d in epics_dir.iterdir() if d.is_dir()])
    
    # Count active stories
    if epics_dir.exists():
        for epic_dir in epics_dir.iterdir():
            if not epic_dir.is_dir():
                continue
            stories_dir = epic_dir / 'STORIES'
            if stories_dir.exists():
                for story_file in stories_dir.glob('STORY-*.md'):
                    total_stories += 1
                    priority, status, is_superseded = count_stories_in_file(story_file)
                    
                    if is_superseded:
                        superseded_stories += 1
                    elif priority == 'P0':
                        p0_stories += 1
                    elif priority == 'P1':
                        p1_stories += 1
                    elif priority == 'P2':
                        p2_stories += 1
                    elif priority == 'P3':
                        p3_stories += 1
                    
                    if status == '🔴':
                        open_stories += 1
                    elif status == '🟡':
                        in_progress_stories += 1
                    elif status == '🟢':
                        done_stories += 1
    
    # Count archived/superseded stories
    if archive_dir.exists():
        for story_file in archive_dir.rglob('STORY-*.md'):
            superseded_stories += 1
    
    return BacklogStats(
        total_epics=total_epics,
        total_stories=total_stories,
        p0_stories=p0_stories,
        p1_stories=p1_stories,
        p2_stories=p2_stories,
        p3_stories=p3_stories,
        open_stories=open_stories,
        in_progress_stories=in_progress_stories,
        done_stories=done_stories,
        superseded_stories=superseded_stories
    )


def update_readme(backlog_dir: Path, stats: BacklogStats, dry_run: bool = False) -> bool:
    """Update the README.md with new statistics."""
    readme_path = backlog_dir / 'README.md'
    
    if not readme_path.exists():
        print(f"Error: README.md not found at {readme_path}")
        return False
    
    content = readme_path.read_text()
    
    # Update dashboard table
    old_dashboard = re.search(
        r'## System Health Dashboard\n\n\| Metric \| Value \| Trend \|\n\|[^\n]+\|\n([^\n]+\n)+',
        content
    )
    
    if old_dashboard:
        new_dashboard = f"""## System Health Dashboard

| Metric | Value | Trend |
|--------|-------|-------|
| Total Epics | {stats.total_epics} | — |
| Total Stories | {stats.total_stories} | — |
| P0 Stories (Ship Blockers) | {stats.p0_stories} | 🔴 Unresolved |
| P1 Stories (Current Sprint) | {stats.p1_stories} | 🟠 Queued |
| P2 Stories (Next Quarter) | {stats.p2_stories} | 🟡 Backlogged |
| P3 Stories (Sustaining) | {stats.p3_stories} | 🟢 Deferred |
| Open Stories | {stats.open_stories} | — |
| In Progress | {stats.in_progress_stories} | — |
| Done | {stats.done_stories} | — |
| Superseded | {stats.superseded_stories} | — |
| Overall System Status | **CRITICAL** | 🔴 Do Not Ship |
"""
        content = content.replace(old_dashboard.group(0), new_dashboard)
        
        if dry_run:
            print("Would update README.md with:")
            print(new_dashboard)
        else:
            readme_path.write_text(content)
            print("Updated README.md")
        return True
    else:
        print("Warning: Could not find dashboard section in README.md")
        return False


def main():
    parser = argparse.ArgumentParser(description='Update backlog metrics')
    parser.add_argument('--check', action='store_true', help='Verify counts without writing')
    parser.add_argument('--backlog-dir', type=Path, default=Path(__file__).parent.parent,
                       help='Path to backlog directory')
    args = parser.parse_args()
    
    print("Scanning backlog...")
    stats = scan_backlog(args.backlog_dir)
    
    print(f"\nBacklog Statistics:")
    print(f"  Total Epics: {stats.total_epics}")
    print(f"  Total Stories: {stats.total_stories}")
    print(f"  P0 (Ship Blockers): {stats.p0_stories}")
    print(f"  P1 (Current Sprint): {stats.p1_stories}")
    print(f"  P2 (Next Quarter): {stats.p2_stories}")
    print(f"  P3 (Sustaining): {stats.p3_stories}")
    print(f"  Open: {stats.open_stories}")
    print(f"  In Progress: {stats.in_progress_stories}")
    print(f"  Done: {stats.done_stories}")
    print(f"  Superseded: {stats.superseded_stories}")
    
    if args.check:
        print("\n--check mode: not writing changes")
    else:
        print()
        update_readme(args.backlog_dir, stats, dry_run=args.check)


if __name__ == '__main__':
    main()
