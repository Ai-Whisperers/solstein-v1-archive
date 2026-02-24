import uuid
from datetime import datetime
from pathlib import Path

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from alembic import command
from alembic.config import Config


def _alembic_config(repo_root: Path) -> Config:
    cfg = Config(str(repo_root / "alembic.ini"))
    cfg.set_main_option("script_location", str(repo_root / "alembic"))
    return cfg


def test_facts_migration_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "facts_migration_smoke.sqlite"
    monkeypatch.setenv("DATABASE__URL", f"sqlite:///{db_path}")

    repo_root = Path(__file__).resolve().parents[2]
    command.upgrade(_alembic_config(repo_root), "head")

    engine = sa.create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        conn.execute(sa.text("PRAGMA foreign_keys=ON"))

        md = sa.MetaData()
        companies = sa.Table("companies", md, autoload_with=conn)
        gathering_batches = sa.Table("gathering_batches", md, autoload_with=conn)
        facts = sa.Table("facts", md, autoload_with=conn)
        fact_sources = sa.Table("fact_sources", md, autoload_with=conn)

        company_id = "test-company"
        now = datetime.utcnow()
        conn.execute(
            companies.insert().values(
                company_id=company_id,
                name="Test Company",
                last_updated=now,
                created_at=now,
            )
        )

        with pytest.raises(IntegrityError):
            conn.execute(
                gathering_batches.insert().values(
                    batch_id=str(uuid.uuid4()),
                    company_id="missing-company",
                )
            )

        batch_id = str(uuid.uuid4())
        conn.execute(
            gathering_batches.insert().values(batch_id=batch_id, company_id=company_id)
        )

        fact_id = str(uuid.uuid4())
        conn.execute(
            facts.insert().values(
                fact_id=fact_id,
                company_id=company_id,
                batch_id=batch_id,
                fact_type="annual_revenue",
                value=1_000_000,
                confidence=0.95,
            )
        )

        conn.execute(
            fact_sources.insert().values(
                source_id=str(uuid.uuid4()),
                fact_id=fact_id,
                source_type="sec_edgar",
                source_url="https://example.invalid/filing",
                raw_content="{}",
            )
        )

        row = conn.execute(
            sa.select(facts.c.fact_type, facts.c.company_id).where(facts.c.company_id == company_id)
        ).one()
        assert row.fact_type == "annual_revenue"
        assert row.company_id == company_id
