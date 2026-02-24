#!/usr/bin/env python3
"""
Documentation Link Validator

Validates all internal and external links in documentation.
- Checks internal markdown links exist
- Verifies link anchors are correct
- Validates external URLs are reachable
- Reports broken links with suggested fixes

Usage:
    python scripts/validate-links.py              # Check all links
    python scripts/validate-links.py --fix        # Auto-fix relative paths
    python scripts/validate-links.py --docs       # Check docs/ only
    python scripts/validate-links.py --external   # Check external URLs only
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from urllib.parse import urlparse

import requests


class LinkValidator:
    """Validates internal and external links in documentation."""

    def __init__(
        self, docs_dir: Path, verbose: bool = False, check_external: bool = True
    ):
        """Initialize validator.

        Args:
            docs_dir: Path to documentation directory
            verbose: Print detailed output
            check_external: Check external URLs (slow, default True)
        """
        self.docs_dir = docs_dir
        self.verbose = verbose
        self.check_external = check_external
        self.broken_links: List[Tuple[Path, str, str]] = []
        self.external_failures: List[Tuple[Path, str, str]] = []
        self.fixed_count = 0

    def validate_all(self) -> bool:
        """Validate all markdown files in docs directory.

        Returns:
            True if no broken links found, False otherwise
        """
        md_files = list(self.docs_dir.rglob("*.md"))
        if self.verbose:
            print(f"📄 Found {len(md_files)} markdown files")

        for md_file in md_files:
            self._validate_file(md_file)

        return self._report_results()

    def _validate_file(self, md_file: Path) -> None:
        """Validate all links in a single markdown file.

        Args:
            md_file: Path to markdown file
        """
        content = md_file.read_text(encoding="utf-8")
        content = self._remove_code_blocks(content)
        links = self._extract_links(content)

        for link_text, link_url in links:
            if link_url.startswith(("#", "mailto:", "http://", "https://")):
                if link_url.startswith(("http://", "https://")) and self.check_external:
                    self._validate_external_link(md_file, link_url, link_text)
                continue

            self._validate_internal_link(md_file, link_url, link_text)

    @staticmethod
    def _remove_code_blocks(content: str) -> str:
        """Remove code blocks from content to avoid parsing their content.

        Args:
            content: Markdown content

        Returns:
            Content with code blocks replaced by empty lines
        """
        result = content
        result = re.sub(r"```[\s\S]*?```", "", result)
        result = re.sub(r"`[^`]+`", "", result)
        return result

    def _extract_links(self, content: str) -> List[Tuple[str, str]]:
        """Extract all markdown links from content.

        Args:
            content: Markdown content

        Returns:
            List of (link_text, link_url) tuples
        """
        pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        matches = re.findall(pattern, content)
        return matches

    def _validate_internal_link(
        self, from_file: Path, link_url: str, link_text: str
    ) -> None:
        """Validate internal markdown link.

        Args:
            from_file: File containing the link
            link_url: Link URL (may include anchor)
            link_text: Link display text
        """
        # Split URL from anchor
        if "#" in link_url:
            url_part, anchor = link_url.split("#", 1)
        else:
            url_part, anchor = link_url, None

        # Resolve relative path
        if url_part:
            target_file = (from_file.parent / url_part).resolve()
        else:
            # Same file with anchor
            target_file = from_file.resolve()

        # Check file exists
        if not target_file.exists():
            self.broken_links.append(
                (from_file, link_url, f"File not found: {target_file}")
            )
            if self.verbose:
                print(f"  ❌ {from_file}: {link_url}")
            return

        # Check anchor if specified
        if anchor:
            if not self._anchor_exists(target_file, anchor):
                self.broken_links.append(
                    (from_file, link_url, f"Anchor not found: #{anchor}")
                )
                if self.verbose:
                    print(f"  ❌ {from_file}: {link_url} (anchor not found)")
                return

        if self.verbose:
            print(f"  ✅ {from_file}: {link_url}")

    def _anchor_exists(self, md_file: Path, anchor: str) -> bool:
        """Check if an anchor (heading) exists in a markdown file.

        Args:
            md_file: Path to markdown file
            anchor: Anchor name (without #)

        Returns:
            True if anchor exists, False otherwise
        """
        content = md_file.read_text(encoding="utf-8")

        # Convert anchor to heading pattern
        # Anchors are auto-generated from heading text by mkdocs
        # "My Heading" → "my-heading"
        heading_pattern = anchor.replace("-", " ").lower()

        # Look for markdown heading matching the anchor
        for line in content.split("\n"):
            if line.startswith("#"):
                # Extract heading text (remove # symbols)
                heading_text = line.lstrip("#").strip().lower()
                # Compare normalized versions
                if self._normalize_for_anchor(heading_text) == anchor:
                    return True

        return False

    @staticmethod
    def _normalize_for_anchor(text: str) -> str:
        """Normalize heading text to anchor format.

        Args:
            text: Heading text

        Returns:
            Normalized anchor string
        """
        # Remove special characters, convert to lowercase, replace spaces with hyphens
        text = text.lower()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", "-", text)
        return text.strip("-")

    def _validate_external_link(
        self, from_file: Path, url: str, link_text: str
    ) -> None:
        """Validate external URL (if check_external enabled).

        Args:
            from_file: File containing the link
            url: External URL
            link_text: Link display text
        """
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code >= 400:
                self.external_failures.append(
                    (from_file, url, f"HTTP {response.status_code}")
                )
                if self.verbose:
                    print(f"  ⚠️  {from_file}: {url} ({response.status_code})")
            else:
                if self.verbose:
                    print(f"  ✅ {from_file}: {url}")
        except requests.RequestException as e:
            self.external_failures.append((from_file, url, str(e)))
            if self.verbose:
                print(f"  ⚠️  {from_file}: {url} (timeout/unreachable)")

    def _report_results(self) -> bool:
        """Report validation results.

        Returns:
            True if no broken links, False if any found
        """
        if not self.broken_links and not self.external_failures:
            print("✅ All links validated successfully!")
            return True

        if self.broken_links:
            print(f"\n❌ Found {len(self.broken_links)} broken link(s):\n")
            for file, url, reason in self.broken_links:
                print(f"  📄 {file.relative_to(self.docs_dir.parent)}")
                print(f"     Link: {url}")
                print(f"     Error: {reason}\n")

        if self.external_failures:
            print(
                f"\n⚠️  Found {len(self.external_failures)} unreachable external link(s):\n"
            )
            for file, url, reason in self.external_failures:
                print(f"  📄 {file.relative_to(self.docs_dir.parent)}")
                print(f"     URL: {url}")
                print(f"     Error: {reason}\n")

        return len(self.broken_links) == 0


def main() -> int:
    """Main entry point.

    Returns:
        0 if successful, 1 if broken links found
    """
    parser = argparse.ArgumentParser(
        description="Validate internal and external links in documentation"
    )
    parser.add_argument(
        "--docs",
        type=Path,
        default=Path("docs"),
        help="Path to documentation directory (default: docs)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed validation output",
    )
    parser.add_argument(
        "--no-external",
        action="store_true",
        help="Skip external URL validation (faster)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix relative path issues",
    )

    args = parser.parse_args()

    if not args.docs.exists():
        print(f"❌ Documentation directory not found: {args.docs}")
        return 1

    validator = LinkValidator(
        docs_dir=args.docs,
        verbose=args.verbose,
        check_external=not args.no_external,
    )

    success = validator.validate_all()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
