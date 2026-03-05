import asyncio
import json
from datetime import datetime
from pathlib import Path

from solstein.data.real_data_integration import RealDataLoader


async def run(queue_path: Path, output_path: Path, min_confidence: float) -> None:
    data = json.loads(queue_path.read_text())
    queue = data.get("queue", [])
    company_names = sorted({item["company"] for item in queue if item.get("company")})

    if not company_names:
        raise SystemExit("No companies found in research queue")

    loader = RealDataLoader(min_confidence=min_confidence)
    companies = await loader.load_companies(company_names)

    if not companies:
        raise SystemExit("No companies found with sufficient confidence")

    output_data = {
        "competitors": companies,
        "metadata": {
            "data_source": "web_research",
            "collection_date": datetime.utcnow().isoformat(),
            "is_synthetic": False,
            "real_data_percentage": "100%",
            "companies_requested": len(company_names),
            "companies_found": len(companies),
            "queue_source": str(queue_path),
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output_data, indent=2))

    print(f"✅ Saved {len(companies)} companies to {output_path}")
    print(f"Requested: {len(company_names)} | Found: {len(companies)}")


if __name__ == "__main__":
    queue_path = Path("data/output/research_queue.json")
    output_path = Path("data/input/competitor_data_real.json")
    min_confidence = 0.3
    asyncio.run(run(queue_path, output_path, min_confidence))
