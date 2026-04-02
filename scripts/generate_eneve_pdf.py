#!/usr/bin/env python3
"""Generate PDF report for Eneve competitive intelligence."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from fpdf import FPDF

    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


def clean_text(text, max_length=200):
    """Clean text for PDF output by removing non-latin-1 characters."""
    if not text:
        return ""
    text = str(text)
    replacements = {
        "\u2022": "-",
        "\u2019": "'",
        "\u2018": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
    }
    for uni, asc in replacements.items():
        text = text.replace(uni, asc)
    text = text.encode("latin-1", "ignore").decode("latin-1")
    return text[:max_length]


def generate_eneve_pdf(companies_data, output_path, title):
    """Generate a PDF report for Eneve competitive intelligence."""

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 20, title, ln=True, align="C")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 8, f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", ln=True, align="C")
    pdf.cell(0, 8, f"Companies Analyzed: {len(companies_data)}", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Executive Summary", ln=True)
    pdf.set_font("Helvetica", size=10)

    categories = {}
    for c in companies_data:
        cat = c.get("relevance_category", "Other")
        categories[cat] = categories.get(cat, 0) + 1

    summary_text = (
        f"Target Company: Eneve (Netherlands)\n"
        f"Focus: Smart software for the energy value chain\n\n"
        f"Total Competitors: {len(companies_data)}\n"
    )
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        summary_text += f"  - {cat}: {count} companies\n"

    pdf.multi_cell(0, 6, summary_text)
    pdf.ln(10)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Company Profiles", ln=True)
    pdf.ln(5)

    sorted_companies = sorted(companies_data, key=lambda x: x.get("confidence_score", 0) or 0, reverse=True)

    for rank, c in enumerate(sorted_companies, 1):
        if pdf.get_y() > 260:
            pdf.add_page()

        pdf.set_font("Helvetica", "B", 11)
        name = str(c.get("name", "Unknown"))[:45]
        pdf.cell(0, 7, f"{rank}. {name}", ln=True)

        pdf.set_font("Helvetica", size=9)
        cat = str(c.get("relevance_category", "N/A"))[:25]
        score = c.get("confidence_score", 0) or 0
        industry = str(c.get("industry", "N/A"))[:35]
        hq = str(c.get("headquarters", "N/A"))[:40] if c.get("headquarters") else "N/A"

        pdf.cell(0, 5, f"Category: {cat} | Score: {score:.2f} | Industry: {industry}", ln=True)
        pdf.cell(0, 5, f"Location: {hq}", ln=True)

        desc = c.get("description", "") or ""
        if desc:
            desc = clean_text(desc, 200)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 5, desc)
            pdf.set_text_color(0, 0, 0)

        pdf.ln(4)

    pdf.output(str(output_path))
    return output_path


def main():
    json_path = Path("data/research_results/eneve_report/eneve_relevant_companies.json")
    output_dir = Path("data/research_results/eneve_report")
    pdf_path = output_dir / "eneve_competitive_intelligence.pdf"

    if not json_path.exists():
        print(f"Error: {json_path} not found. Run generate_eneve_report.py first.")
        sys.exit(1)

    if not FPDF_AVAILABLE:
        print("Error: fpdf2 not installed. Install with: pip install fpdf2")
        sys.exit(1)

    with open(json_path) as f:
        data = json.load(f)

    companies_data = data.get("companies", [])

    print(f"📄 Generating PDF report for {len(companies_data)} companies...")

    title = "Eneve Competitive Intelligence Report"

    result_path = generate_eneve_pdf(companies_data, pdf_path, title)

    print(f"✅ PDF report saved: {result_path}")

    print("\n" + "=" * 60)
    print("📊 REPORT SUMMARY")
    print("=" * 60)
    print("Target Company: Eneve (Netherlands)")
    print("Focus: Smart software for the energy value chain")
    print(f"Total Competitors Analyzed: {len(companies_data)}")
    print("\nTop 5 by Confidence Score:")
    sorted_companies = sorted(companies_data, key=lambda x: x.get("confidence_score", 0) or 0, reverse=True)
    for i, c in enumerate(sorted_companies[:5], 1):
        print(f"  {i}. {c.get('name', 'Unknown')} (Score: {c.get('confidence_score', 0):.2f})")
    print("=" * 60)


if __name__ == "__main__":
    main()
