#!/usr/bin/env python3
"""Extract structured financial data from competitor markdown files.

Parses all `financial-growth.md` files under `tickets/COMPETITION/*/`,
extracting Growth Scorecards, Revenue Timelines, Funding History,
Employee data, and SaaS metrics into a single JSON structure.

Usage:
    python extract_competitor_data.py --input tickets/COMPETITION/ --output competitor_data.json
    python extract_competitor_data.py --input tickets/COMPETITION/  (prints JSON to stdout)
    python extract_competitor_data.py --input tickets/COMPETITION/ --output out.json --no-cache
    python extract_competitor_data.py --input tickets/COMPETITION/ --output out.json --profile

Requirements:
    Python 3.10+
    rich >= 13.0 (optional, for progress bars)

Performance (29 competitors, no cache):
    Total pipeline: ~0.10s
    Per-file extraction: ~0.09s (89% of total, linear with competitor count)
    JSON serialization: ~0.007s
    With cache (unchanged files): extraction drops to near-zero for cached entries
"""

import argparse
import hashlib
import json
import logging
import re
import sys
from pathlib import Path
from typing import Optional

from competitor_utils import timed_phase

try:
    from rich.console import Console
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# Growth Scorecard dimension names in canonical order
SCORECARD_DIMENSIONS = [
    "Revenue Growth",
    "Funding Momentum",
    "Employee Growth",
    "Geographic Expansion",
    "M&A Activity",
    "SaaS Maturity",
]

CLASSIFICATION_THRESHOLDS = {
    "Rocket": (7.0, 10.0),
    "Riser": (5.0, 6.9),
    "Steady": (3.0, 4.9),
    "Dinosaur": (1.0, 2.9),
}

# Pre-compiled regex patterns avoid re-compilation on every call
_RE_TABLE_SEP = re.compile(r"^\|?\s*[-:]+")
_RE_TABLE_BLOCK = re.compile(r"(\|[^\n]+\|\n\|[\s:|-]+\|\n(?:\|[^\n]+\|\n?)+)")
_RE_CURRENCY = re.compile(r"[€$£]|EUR|USD|NOK|GBP|SEK|DKK|PLN", re.IGNORECASE)
_RE_NUM_RANGE = re.compile(r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*[M]?")
_RE_NUM_MAIN = re.compile(
    r"[~≈]?\s*(?:[€$£]|EUR|USD|NOK|GBP|SEK|DKK|PLN)?\s*(\d+(?:\.\d+)?)\s*([BMK%])?",
    re.IGNORECASE,
)
_RE_NUM_SIMPLE = re.compile(r"(\d+(?:\.\d+)?)")
_RE_PERCENTAGE = re.compile(r"[+~≈]?\s*(\d+(?:\.\d+)?)\s*%")
_RE_EUR_K_SUFFIX = re.compile(r"\d\s*K\b", re.IGNORECASE)
_RE_EUR_K_RANGE = re.compile(r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)")
_RE_EUR_K_NUM = re.compile(
    r"[~≈]?\s*(?:[€$£]|EUR|USD|NOK|GBP|SEK|DKK|PLN)?\s*(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
_RE_H1_DEEP_DIVE = re.compile(
    r"^#\s+Financial & Growth Deep-Dive\s*[-–—]\s*(.+)$", re.MULTILINE
)
_RE_H1_GENERIC = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_RE_DATA_AVAIL = re.compile(r"\*\*Data Availability\*\*:\s*(.+)")
_RE_YEAR = re.compile(r"\b(20\d{2})\b")


def iter_with_progress(items, description="Processing"):
    """Iterate with a progress bar (Rich) or simple stderr counter (fallback)."""
    if _HAS_RICH:
        with Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            console=Console(stderr=True),
        ) as progress:
            task = progress.add_task(description, total=len(items))
            for item in items:
                yield item
                progress.advance(task)
    else:
        for i, item in enumerate(items, 1):
            print(f"\r{description}: {i}/{len(items)}", end="", file=sys.stderr)
            yield item
        print(file=sys.stderr)


def compute_file_hash(path: Path) -> str:
    """Return the MD5 hex digest of a file's contents."""
    return hashlib.md5(path.read_bytes()).hexdigest()


def load_cache(cache_path: Path) -> dict:
    """Load cached hashes and data, returning empty dict on missing/corrupt file."""
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            log.warning("Corrupted cache file %s, starting fresh", cache_path)
            return {}
    return {}


def save_cache(cache_path: Path, cache: dict) -> None:
    """Persist the cache dict to disk."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_markdown_table(text: str) -> list[dict[str, str]]:
    """Parse a markdown table into a list of row dicts keyed by header names."""
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if len(lines) < 3:
        return []

    def split_row(line: str) -> list[str]:
        parts = line.strip().strip("|").split("|")
        return [p.strip() for p in parts]

    headers = split_row(lines[0])
    rows: list[dict[str, str]] = []
    for line in lines[2:]:  # skip header + separator
        if _RE_TABLE_SEP.match(line):
            continue
        cells = split_row(line)
        row = {}
        for i, hdr in enumerate(headers):
            row[hdr] = cells[i] if i < len(cells) else ""
        rows.append(row)
    return rows


def find_section(content: str, heading: str) -> Optional[str]:
    """Return text under a markdown heading (### or ##), up to the next heading of same or higher level."""
    pattern = rf"^(#{{2,3}})\s+{re.escape(heading)}\s*$"
    match = re.search(pattern, content, re.MULTILINE)
    if not match:
        return None
    level = len(match.group(1))
    start = match.end()
    end_pattern = rf"^#{{1,{level}}}\s+"
    end_match = re.search(end_pattern, content[start:], re.MULTILINE)
    if end_match:
        return content[start : start + end_match.start()]
    return content[start:]


def extract_first_table(section_text: str) -> list[dict[str, str]]:
    """Find and parse the first markdown table in a section."""
    match = _RE_TABLE_BLOCK.search(section_text)
    if match:
        return parse_markdown_table(match.group(1))
    return []


def parse_number(text: str, assume_millions: bool = False) -> Optional[float]:
    """Best-effort extraction of a numeric value from free-form text.

    Handles patterns like '~EUR 143M', 'EUR 10M', '22%', '7.3', '~44%',
    monetary ranges like 'EUR 25-30M', exact amounts like '€36,322,612',
    and plain integers.

    When assume_millions is True and a currency symbol is present, large
    numbers without M/B suffix are converted to millions (e.g. €36,322,612 -> 36.3).
    """
    if not text:
        return None
    cleaned = text.replace(",", "").replace("**", "").strip()
    has_currency = bool(_RE_CURRENCY.search(cleaned))

    range_match = _RE_NUM_RANGE.search(cleaned)
    if range_match:
        low = float(range_match.group(1))
        high = float(range_match.group(2))
        midpoint = (low + high) / 2.0
        if "M" in cleaned[range_match.end() - 2 : range_match.end() + 2]:
            return midpoint
        if "B" in cleaned[range_match.end() - 2 : range_match.end() + 2]:
            return midpoint * 1000.0
        if assume_millions and has_currency and midpoint > 10000:
            return round(midpoint / 1_000_000, 1)
        return midpoint

    num_match = _RE_NUM_MAIN.search(cleaned)
    if num_match:
        val = float(num_match.group(1))
        suffix = (num_match.group(2) or "").upper()
        if suffix == "B":
            val *= 1000.0
        elif suffix == "K":
            val /= 1000.0
        elif assume_millions and has_currency and val > 10000 and not suffix:
            val = round(val / 1_000_000, 1)
        return val

    simple = _RE_NUM_SIMPLE.search(cleaned)
    if simple:
        return float(simple.group(1))
    return None


def parse_percentage(text: str) -> Optional[float]:
    """Extract a percentage value from text like '+12%', '~15.4%', '22%'."""
    if not text:
        return None
    match = _RE_PERCENTAGE.search(text)
    if match:
        return float(match.group(1))
    return None


def extract_growth_scorecard(content: str) -> dict:
    """Extract Growth Scorecard dimensions, composite score, and classification."""
    section = find_section(content, "Growth Scorecard")
    if not section:
        return {}

    rows = extract_first_table(section)
    if not rows:
        return {}

    dimensions: dict[str, dict] = {}
    composite_score: Optional[float] = None
    classification: Optional[str] = None

    for row in rows:
        dim_name = row.get("Dimension", "").replace("**", "").strip()
        score_raw = row.get("Score (1-10)", "").replace("**", "").strip()
        evidence = row.get("Evidence Summary", "").replace("**", "").strip()

        if "COMPOSITE" in dim_name.upper():
            composite_score = parse_number(score_raw)
            # Prefer score-based classification (avoids ambiguity in text like "Dinosaur (boundary with Steady)")
            if composite_score is not None:
                for cls, (lo, hi) in CLASSIFICATION_THRESHOLDS.items():
                    if lo <= composite_score <= hi:
                        classification = cls
                        break
            # Fallback: extract from evidence text
            if not classification:
                for cls in CLASSIFICATION_THRESHOLDS:
                    if cls.lower() in evidence.lower():
                        classification = cls
                        break
            continue

        score = parse_number(score_raw)
        dimensions[dim_name] = {
            "score": score,
            "evidence": evidence,
        }

    return {
        "dimensions": dimensions,
        "composite_score": composite_score,
        "classification": classification,
    }


def extract_revenue_timeline(content: str) -> dict:
    """Extract revenue timeline table and CAGR values."""
    section = find_section(content, "Revenue Timeline")
    if not section:
        return {}

    rows = extract_first_table(section)
    timeline = []
    for row in rows:
        year_raw = row.get("Year", "")
        eur_equiv = row.get("EUR Equivalent", "")
        yoy = row.get("YoY Growth", "")
        confidence = row.get("Confidence", "")

        eur_value = parse_number(eur_equiv, assume_millions=True)
        yoy_pct = parse_percentage(yoy)

        timeline.append({
            "year": year_raw.strip(),
            "eur_millions": eur_value,
            "yoy_growth_pct": yoy_pct,
            "confidence": confidence.strip(),
        })

    cagr_3yr = None
    cagr_5yr = None
    for line in section.splitlines():
        # Only take the first match for each CAGR type to avoid overwriting
        # (e.g., "Revenue CAGR" followed by "Organic CAGR" on separate lines)
        if cagr_3yr is None and "CAGR" in line and "3yr" in line.lower():
            cagr_3yr = parse_percentage(line)
        elif cagr_5yr is None and "CAGR" in line and ("4yr" in line.lower() or "5yr" in line.lower()):
            cagr_5yr = parse_percentage(line)

    latest_revenue = None
    for entry in timeline:
        if entry["eur_millions"] is not None:
            latest_revenue = entry["eur_millions"]
            break

    return {
        "timeline": timeline,
        "cagr_3yr_pct": cagr_3yr,
        "cagr_5yr_pct": cagr_5yr,
        "latest_revenue_eur_m": latest_revenue,
    }


def _parse_eur_k(text: str) -> Optional[float]:
    """Parse a revenue-per-employee value and normalise to EUR thousands.

    Handles both "~EUR 118K" (already in K) and "EUR 79,500" (plain EUR).
    Returns the value in EUR thousands (e.g. 118.0, 79.5).
    """
    if not text:
        return None
    cleaned = text.replace(",", "").replace("**", "").strip()
    has_k = bool(_RE_EUR_K_SUFFIX.search(cleaned))

    range_match = _RE_EUR_K_RANGE.search(cleaned)
    if range_match:
        mid = (float(range_match.group(1)) + float(range_match.group(2))) / 2.0
        # With K suffix the numbers are already in thousands
        return round(mid, 1) if has_k else round(mid / 1000.0, 1)

    num_match = _RE_EUR_K_NUM.search(cleaned)
    if num_match:
        val = float(num_match.group(1))
        if has_k:
            return round(val, 1)
        # Plain EUR (no K suffix) with value > 1000 -> convert to thousands
        if val > 1000:
            return round(val / 1000.0, 1)
        return round(val, 1)

    return None


def _extract_year(text: str) -> int:
    """Extract a 4-digit year from text, returning 0 if none found."""
    match = _RE_YEAR.search(text)
    return int(match.group(1)) if match else 0


def _latest_metric(
    metrics: dict[str, Optional[str]],
    keyword: str,
    parser=None,
) -> Optional[float]:
    """Return the parsed value of the metric whose key contains *keyword* and has the latest year."""
    best_year = -1
    best_val: Optional[float] = None
    for key, raw in metrics.items():
        if keyword in key.lower():
            parsed = parser(raw) if parser else parse_number(raw)
            if parsed is not None:
                year = _extract_year(key)
                if year > best_year:
                    best_year = year
                    best_val = parsed
    return best_val


def extract_profitability(content: str) -> dict:
    """Extract key profitability metrics including EBITDA margin and revenue per employee."""
    section = find_section(content, "Profitability")
    if not section:
        return {}

    rows = extract_first_table(section)
    metrics: dict[str, Optional[str]] = {}
    for row in rows:
        dp = row.get("Data Point", row.get("Metric", "")).strip()
        val = row.get("Value", "").strip()
        if dp:
            metrics[dp] = val

    recurring_pct = None
    for key, val in metrics.items():
        if "recurring revenue" in key.lower() and "%" in val:
            recurring_pct = parse_percentage(val)
            break

    ebitda_margin_pct = _latest_metric(metrics, "ebitda margin", parser=parse_percentage)
    revenue_per_employee_eur_k = _latest_metric(metrics, "revenue per employee", parser=_parse_eur_k)

    return {
        "recurring_revenue_pct": recurring_pct,
        "raw_metrics": metrics,
        "ebitda_margin_pct": ebitda_margin_pct,
        "revenue_per_employee_eur_k": revenue_per_employee_eur_k,
    }


def extract_funding(content: str) -> dict:
    """Extract funding history, lead investors, and war chest signals."""
    section = find_section(content, "Funding & Investment History")
    if not section:
        return {}

    rows = extract_first_table(section)
    rounds = []
    lead_investors: set[str] = set()
    for row in rows:
        investors_text = row.get("Lead Investor(s)", "").strip()
        rounds.append({
            "date": row.get("Date", "").strip(),
            "round": row.get("Round", "").strip(),
            "amount": row.get("Amount", "").strip(),
            "valuation": row.get("Valuation", "").strip(),
            "lead_investors": investors_text,
        })
        if investors_text and investors_text not in ("N/A", "--", "—", "-", "", "Market"):
            for inv in re.split(r"[,;]", investors_text):
                name = inv.strip()
                if name:
                    lead_investors.add(name)

    total_raised = None
    latest_valuation = None
    war_chest_signals = None
    for line in section.splitlines():
        lower = line.lower()
        if "total raised" in lower or "total capital" in lower:
            total_raised = line.split(":", 1)[-1].strip() if ":" in line else line.strip()
        if "latest valuation" in lower:
            latest_valuation = line.split(":", 1)[-1].strip() if ":" in line else line.strip()

    wc_match = re.search(
        r"\*\*War Chest Signals?\*\*:\s*(.+?)(?=\n\*\*|\n##|\n---|\Z)",
        section,
        re.DOTALL | re.IGNORECASE,
    )
    if wc_match:
        war_chest_signals = wc_match.group(1).strip() or None

    return {
        "rounds": rounds,
        "total_raised_text": total_raised,
        "latest_valuation_text": latest_valuation,
        "lead_investors": sorted(lead_investors),
        "war_chest_signals": war_chest_signals,
    }


def extract_employees(content: str) -> dict:
    """Extract employee timeline and CAGR."""
    section = find_section(content, "Employee Timeline")
    if not section:
        return {}

    rows = extract_first_table(section)
    timeline = []
    for row in rows:
        year = row.get("Year", "").strip()
        headcount_raw = row.get("Headcount", "").strip()
        headcount = parse_number(headcount_raw)
        timeline.append({
            "year": year,
            "headcount": headcount,
        })

    cagr = None
    open_positions = None
    for line in section.splitlines():
        if "Employee CAGR" in line or "employee CAGR" in line:
            cagr = parse_percentage(line)
        if "Open Positions" in line:
            raw = line.split(":", 1)[-1] if ":" in line else None
            parsed = parse_number(raw) if raw else None
            # Values >= 2000 are almost certainly year references (e.g. "as of Feb 2026")
            # embedded in prose, not actual position counts
            open_positions = parsed if parsed is not None and parsed < 2000 else None

    latest_headcount = None
    for entry in timeline:
        if entry["headcount"] is not None:
            latest_headcount = entry["headcount"]
            break

    return {
        "timeline": timeline,
        "employee_cagr_pct": cagr,
        "latest_headcount": latest_headcount,
        "open_positions": open_positions,
    }


def extract_geographic(content: str) -> dict:
    """Extract geographic expansion data: international revenue % and countries count."""
    result: dict = {
        "international_revenue_pct": None,
        "countries_count": None,
    }
    section = find_section(content, "Geographic & Market Expansion")
    if not section:
        return result

    intl_match = re.search(
        r"\*\*International Revenue %?\*\*:\s*(.+)",
        section,
        re.IGNORECASE,
    )
    if intl_match:
        result["international_revenue_pct"] = parse_percentage(intl_match.group(1))

    countries_match = re.search(r"(\d+)\+?\s*countries", section, re.IGNORECASE)
    if countries_match:
        result["countries_count"] = int(countries_match.group(1))
    else:
        # Fallback: count unique country names from expansion events table
        rows = extract_first_table(section)
        countries: set[str] = set()
        for row in rows:
            details = row.get("Details", row.get("Expansion Event", ""))
            for m in re.finditer(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", details):
                candidate = m.group(1)
                if candidate in _KNOWN_COUNTRIES:
                    countries.add(candidate)
        if countries:
            result["countries_count"] = len(countries)

    return result


# Minimal set of European / key countries that appear in competitor data
_KNOWN_COUNTRIES = frozenset([
    "Germany", "France", "Netherlands", "Belgium", "Austria", "Switzerland",
    "Denmark", "Sweden", "Norway", "Finland", "Poland", "Italy", "Spain",
    "Portugal", "Ireland", "Luxembourg", "Bulgaria", "Romania", "Hungary",
    "Czech", "Slovakia", "Slovenia", "Croatia", "Greece", "Turkey",
    "United Kingdom", "UK", "USA", "Japan", "China", "India", "Australia",
    "Canada", "Brazil", "Singapore", "Mexico", "Chile", "Colombia",
])


def extract_saas_metrics(content: str) -> dict:
    """Extract SaaS transition metrics: deployment model and cloud revenue %."""
    result: dict = {
        "deployment_model": None,
        "cloud_revenue_pct": None,
    }
    section = find_section(content, "SaaS Transition Metrics")
    if not section:
        return result

    rows = extract_first_table(section)
    for row in rows:
        dp = row.get("Data Point", row.get("Metric", "")).strip().lower()
        val = row.get("Value", "").strip()
        if "deployment model" in dp:
            # Classify: pure "SaaS", "Hybrid", or "On-Premise"
            val_lower = val.lower()
            if "hybrid" in val_lower:
                result["deployment_model"] = "Hybrid"
            elif "saas" in val_lower or "cloud-native" in val_lower:
                result["deployment_model"] = "SaaS"
            elif "on-prem" in val_lower:
                result["deployment_model"] = "On-Premise"
            else:
                result["deployment_model"] = val.split("(")[0].strip() if val else None
        elif "cloud revenue" in dp and "current" in dp:
            result["cloud_revenue_pct"] = parse_percentage(val)

    # Fallback: if no "(current)" row, take the first cloud revenue row
    if result["cloud_revenue_pct"] is None:
        for row in rows:
            dp = row.get("Data Point", row.get("Metric", "")).strip().lower()
            val = row.get("Value", "").strip()
            if "cloud revenue" in dp:
                pct = parse_percentage(val)
                if pct is not None:
                    result["cloud_revenue_pct"] = pct
                    break

    return result


def extract_company_name(content: str) -> str:
    """Extract company name from the H1 heading."""
    match = _RE_H1_DEEP_DIVE.search(content)
    if match:
        return match.group(1).strip()
    match = _RE_H1_GENERIC.search(content)
    if match:
        return match.group(1).strip()
    return "Unknown"


def extract_data_availability(content: str) -> Optional[str]:
    """Extract Data Availability line."""
    match = _RE_DATA_AVAIL.search(content)
    if match:
        return match.group(1).strip()
    return None


def get_tier_from_readme(readme_content: str, folder_name: str) -> Optional[str]:
    """Look up the tier for a competitor by scanning the README tables."""
    tier_map: dict[str, str] = {}

    current_tier = None
    for line in readme_content.splitlines():
        if "### Tier 1 -" in line and "1b" not in line:
            current_tier = "Tier 1"
        elif "### Tier 1b" in line:
            current_tier = "Tier 1b"
        elif "### Tier 2" in line:
            current_tier = "Tier 2"
        elif "### Tier 3" in line:
            current_tier = "Tier 3"
        elif line.startswith("###") and "Tier" not in line:
            current_tier = None
        elif "eneve" in line.lower() and "self-assessment" in line.lower():
            current_tier = "Self"
        elif current_tier and "|" in line and ".md" in line:
            link_match = re.search(r"\[.*?\]\(([^)]+)/", line)
            if link_match:
                linked_folder = link_match.group(1).strip()
                tier_map[linked_folder] = current_tier

    return tier_map.get(folder_name)


def extract_ai_talent(content: str) -> dict:
    """Extract AI talent intelligence from an ai-talent.md file.

    Parses leadership table, team composition, talent scorecard,
    key hires, talent origin map, and talent flow summary.
    """
    result: dict = {
        "leadership": [],
        "team_size": None,
        "ai_team_pct_engineering": None,
        "ai_team_pct_total": None,
        "open_ai_positions": None,
        "concentration_risk": None,
        "acquihire_score": None,
        "key_hires": [],
        "talent_origins": {},
        "publications_count": None,
        "patents_count": None,
        "opensource_count": None,
        "net_talent_flow": None,
        "leadership_assessment": None,
        "team_assessment": None,
        "data_available": True,
    }

    # --- Leadership ---
    leadership_section = find_section(content, "AI/ML Leadership")
    if leadership_section:
        rows = extract_first_table(leadership_section)
        for row in rows:
            result["leadership"].append({
                "name": row.get("Name", "").strip(),
                "title": row.get("Title", "").strip(),
                "tenure": row.get("Tenure", "").strip(),
                "previous_role": row.get("Previous Role", "").strip(),
                "academic_background": row.get("Academic Background", "").strip(),
                "visibility": row.get("Public Visibility", "").strip(),
            })
        assessment_match = re.search(
            r"\*\*Leadership Assessment\*\*:\s*(.+?)(?=\n##|\n\*\*|\Z)",
            leadership_section, re.DOTALL,
        )
        if assessment_match:
            result["leadership_assessment"] = assessment_match.group(1).strip()

    # --- Team Composition ---
    team_section = find_section(content, "Team Composition")
    if team_section:
        rows = extract_first_table(team_section)
        metrics: dict[str, str] = {}
        for row in rows:
            metric = row.get("Metric", "").strip().lower()
            value = row.get("Value", "").strip()
            metrics[metric] = value

        for key, val in metrics.items():
            if "total ai" in key and "headcount" in key:
                result["team_size"] = parse_number(val)
            elif "ai team % of engineering" in key:
                result["ai_team_pct_engineering"] = parse_percentage(val)
            elif "ai team % of total" in key:
                result["ai_team_pct_total"] = parse_percentage(val)
            elif "open ai" in key and "position" in key:
                result["open_ai_positions"] = parse_number(val)

        assessment_match = re.search(
            r"\*\*Team Assessment\*\*:\s*(.+?)(?=\n##|\n\*\*|\Z)",
            team_section, re.DOTALL,
        )
        if assessment_match:
            result["team_assessment"] = assessment_match.group(1).strip()

    # --- Key Hires ---
    hires_section = find_section(content, "Key Hires")
    if hires_section:
        rows = extract_first_table(hires_section)
        for row in rows:
            result["key_hires"].append({
                "date": row.get("Date", "").strip(),
                "name": row.get("Name", "").strip(),
                "role": row.get("Role", "").strip(),
                "origin": row.get("Origin", "").strip(),
                "expertise": row.get("Expertise Brought", "").strip(),
            })

    # --- Talent Origin Map ---
    origin_section = find_section(content, "Talent Origin Map")
    if origin_section:
        rows = extract_first_table(origin_section)
        for row in rows:
            category = row.get("Origin Category", "").strip()
            count = parse_number(row.get("Count", ""))
            if category:
                result["talent_origins"][category] = count

    # --- Publications, Patents & Open Source ---
    pubs_section = find_section(content, "Publications, Patents & Open Source")
    if pubs_section:
        rows = extract_first_table(pubs_section)
        for row in rows:
            item_type = row.get("Type", "").strip().lower()
            count = parse_number(row.get("Count", ""))
            if "paper" in item_type or "conference" in item_type:
                result["publications_count"] = count
            elif "patent" in item_type:
                result["patents_count"] = count
            elif "open" in item_type and "source" in item_type:
                result["opensource_count"] = count

    # --- Talent Scorecard ---
    scorecard_section = find_section(content, "Talent Scorecard")
    if scorecard_section:
        rows = extract_first_table(scorecard_section)
        for row in rows:
            dim = row.get("Dimension", "").strip().lower()
            score = parse_number(row.get("Score (1-10)", ""))
            if "concentration" in dim:
                result["concentration_risk"] = score
            elif "acqui" in dim:
                result["acquihire_score"] = score

    # --- Talent Flow Summary ---
    flow_section = find_section(content, "Talent Flow Summary")
    if flow_section:
        direction_match = re.search(
            r"\*\*Net Direction\*\*:\s*(.+)",
            flow_section,
        )
        if direction_match:
            result["net_talent_flow"] = direction_match.group(1).strip()

    return result


def extract_competitor(file_path: Path) -> dict:
    """Extract all financial data from a single competitor's financial-growth.md."""
    content = file_path.read_text(encoding="utf-8")
    folder_name = file_path.parent.name

    company_name = extract_company_name(content)
    data_availability = extract_data_availability(content)
    scorecard = extract_growth_scorecard(content)
    revenue = extract_revenue_timeline(content)
    profitability = extract_profitability(content)
    funding = extract_funding(content)
    employees = extract_employees(content)
    geographic = extract_geographic(content)
    saas = extract_saas_metrics(content)

    # AI talent data from separate ai-talent.md (if present)
    ai_talent_file = file_path.parent / "ai-talent.md"
    ai_talent: dict = {}
    if ai_talent_file.exists():
        ai_talent_content = ai_talent_file.read_text(encoding="utf-8")
        ai_talent = extract_ai_talent(ai_talent_content)

    return {
        "company_name": company_name,
        "folder": folder_name,
        "data_availability": data_availability,
        "scorecard": scorecard,
        "revenue": revenue,
        "profitability": profitability,
        "funding": funding,
        "employees": employees,
        "geographic": geographic,
        "saas": saas,
        "ai_talent": ai_talent,
    }


def extract_all_competitors(
    competition_dir: Path,
    *,
    use_cache: bool = True,
    cache_path: Optional[Path] = None,
    profile: bool = False,
) -> dict:
    """Extract data from all competitor financial-growth.md files.

    Returns a dict with 'competitors' list and 'metadata'.
    Supports smart caching: unchanged files are skipped on subsequent runs.
    """
    if not competition_dir.is_dir():
        log.error("Directory not found: %s", competition_dir)
        return {"competitors": [], "metadata": {"error": f"Directory not found: {competition_dir}"}}

    with timed_phase("File discovery", profile=profile):
        readme_path = competition_dir / "README.md"
        readme_content = ""
        if readme_path.exists():
            readme_content = readme_path.read_text(encoding="utf-8")

        competitors: list[dict] = []
        missing: list[dict] = []

        cache: dict = {}
        if use_cache and cache_path:
            cache = load_cache(cache_path)

        subdirs = sorted(
            [d for d in competition_dir.iterdir() if d.is_dir() and d.name != "protocols"],
            key=lambda d: d.name,
        )

    cache_hits = 0
    cache_misses = 0

    with timed_phase("Per-file extraction", profile=profile):
        for subdir in iter_with_progress(subdirs, "Extracting competitors"):
            fg_file = subdir / "financial-growth.md"
            if fg_file.exists():
                file_hash = compute_file_hash(fg_file)
                cached_entry = cache.get(subdir.name, {})

                if use_cache and cached_entry.get("hash") == file_hash and "data" in cached_entry:
                    log.debug("Cache hit: %s (hash %s)", subdir.name, file_hash[:8])
                    data = cached_entry["data"]
                    cache_hits += 1
                else:
                    log.debug("Cache miss: %s (hash %s)", subdir.name, file_hash[:8])
                    log.info("Extracting: %s", subdir.name)
                    data = extract_competitor(fg_file)
                    cache[subdir.name] = {"hash": file_hash, "data": data}
                    cache_misses += 1

                data["tier"] = get_tier_from_readme(readme_content, subdir.name)
                competitors.append(data)
            else:
                log.warning("No financial-growth.md: %s", subdir.name)
                missing.append({
                    "folder": subdir.name,
                    "tier": get_tier_from_readme(readme_content, subdir.name),
                })

    with timed_phase("Cache save", profile=profile):
        if use_cache and cache_path:
            save_cache(cache_path, cache)
            log.debug("Cache summary: %d hits, %d misses", cache_hits, cache_misses)

    with timed_phase("Sorting results", profile=profile):
        competitors.sort(
            key=lambda c: c.get("scorecard", {}).get("composite_score") or 0,
            reverse=True,
        )

    return {
        "competitors": competitors,
        "missing_data": missing,
        "metadata": {
            "total_folders": len(subdirs),
            "with_financial_data": len(competitors),
            "without_financial_data": len(missing),
            "source_directory": str(competition_dir),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract structured financial data from competitor markdown files.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to tickets/COMPETITION/ directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSON file path (prints to stdout if omitted)",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Force full re-extraction, ignoring cached file hashes",
    )
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Log wall-clock timing for each major pipeline phase",
    )
    args = parser.parse_args()

    use_cache = not args.no_cache
    cache_path = args.input / ".cache" / "market_hashes.json" if use_cache else None

    try:
        with timed_phase("Total extraction pipeline", profile=args.profile):
            result = extract_all_competitors(
                args.input, use_cache=use_cache, cache_path=cache_path,
                profile=args.profile,
            )

            with timed_phase("JSON serialization", profile=args.profile):
                json_output = json.dumps(result, indent=2, ensure_ascii=False)

            with timed_phase("File write", profile=args.profile):
                if args.output:
                    args.output.write_text(json_output, encoding="utf-8")
                    log.info(
                        "Wrote %d competitors to %s (%d missing data)",
                        result["metadata"]["with_financial_data"],
                        args.output,
                        result["metadata"]["without_financial_data"],
                    )
                else:
                    print(json_output)

        return 0
    except FileNotFoundError as exc:
        log.error("File not found: %s", exc)
        return 1
    except json.JSONDecodeError as exc:
        log.error("Invalid JSON: %s", exc)
        return 1
    except Exception as exc:
        log.error("Unexpected error: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
