"""Tests for STORY-064: Supabase Row Level Security Policies.

Validates:
- RLS migration file exists and contains required policies
- All tenant-scoped tables are covered
- Policy pattern is correct (tenant_select/insert/update/delete)
- Helper function is defined
- Old permissive anon policies are dropped
- Service role bypass is documented
- Alembic migration exists
"""

import re
from pathlib import Path

import pytest

# Root paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SUPABASE_MIGRATION = PROJECT_ROOT / "supabase" / "migrations" / "014_epic019_tenant_rls_policies.sql"
ALEMBIC_MIGRATION = PROJECT_ROOT / "alembic" / "versions" / "014_epic019_rls_helper_function.py"
RLS_DOCS = PROJECT_ROOT / "docs" / "rls-policies.md"

# All tables that must have tenant-scoped RLS policies
TENANT_SCOPED_TABLES = [
    "companies",
    "scoring_records",
    "signal_records",
    "market_snapshots",
    "audit_trails",
    "research_runs",
    "research_stages",
    "research_artifacts",
    "source_documents",
    "metric_observations",
    "evidence_readiness",
    "research_contradictions",
    "enrichment_audit_trail",
    "enrichment_cache",
    "enrichment_jobs",
    "outbox_records",
]

# Tables that should NOT have tenant RLS (system-wide or inherited)
NON_TENANT_TABLES = [
    "tenants",
    "release_gate_audit",
    "research_contradiction_transitions",
]


@pytest.fixture(scope="module")
def migration_sql() -> str:
    """Load the Supabase RLS migration SQL."""
    assert SUPABASE_MIGRATION.exists(), f"Migration file not found: {SUPABASE_MIGRATION}"
    return SUPABASE_MIGRATION.read_text()


@pytest.fixture(scope="module")
def alembic_migration_text() -> str:
    """Load the Alembic migration Python source."""
    assert ALEMBIC_MIGRATION.exists(), f"Alembic migration not found: {ALEMBIC_MIGRATION}"
    return ALEMBIC_MIGRATION.read_text()


class TestMigrationFileExists:
    """Verify migration files exist."""

    def test_supabase_migration_exists(self) -> None:
        assert SUPABASE_MIGRATION.exists()

    def test_alembic_migration_exists(self) -> None:
        assert ALEMBIC_MIGRATION.exists()

    def test_rls_documentation_exists(self) -> None:
        assert RLS_DOCS.exists()


class TestHelperFunction:
    """Verify the get_user_tenant_id() helper function."""

    def test_helper_function_defined(self, migration_sql: str) -> None:
        assert "CREATE OR REPLACE FUNCTION public.get_user_tenant_id()" in migration_sql

    def test_helper_returns_text(self, migration_sql: str) -> None:
        assert "RETURNS TEXT" in migration_sql

    def test_helper_reads_app_metadata(self, migration_sql: str) -> None:
        assert "app_metadata" in migration_sql
        assert "tenant_id" in migration_sql

    def test_helper_reads_user_metadata_fallback(self, migration_sql: str) -> None:
        assert "user_metadata" in migration_sql

    def test_helper_uses_coalesce(self, migration_sql: str) -> None:
        assert "COALESCE" in migration_sql

    def test_helper_is_security_definer(self, migration_sql: str) -> None:
        assert "SECURITY DEFINER" in migration_sql

    def test_helper_is_stable(self, migration_sql: str) -> None:
        assert "STABLE" in migration_sql


class TestTenantIdColumns:
    """Verify tenant_id columns are added to all tables."""

    @pytest.mark.parametrize("table", TENANT_SCOPED_TABLES)
    def test_tenant_id_column_added(self, migration_sql: str, table: str) -> None:
        # Check for ALTER TABLE ... ADD COLUMN ... tenant_id
        pattern = rf"ALTER TABLE public\.{table}\s+ADD COLUMN IF NOT EXISTS tenant_id"
        assert re.search(pattern, migration_sql, re.IGNORECASE), f"Missing tenant_id column addition for table: {table}"

    @pytest.mark.parametrize("table", TENANT_SCOPED_TABLES)
    def test_tenant_id_backfill(self, migration_sql: str, table: str) -> None:
        # Check for UPDATE ... SET tenant_id = default
        pattern = rf"UPDATE public\.{table}\s+SET tenant_id = '00000000-0000-0000-0000-000000000000'"
        assert re.search(pattern, migration_sql, re.IGNORECASE), f"Missing tenant_id backfill for table: {table}"

    @pytest.mark.parametrize("table", TENANT_SCOPED_TABLES)
    def test_tenant_id_index_created(self, migration_sql: str, table: str) -> None:
        # Check for index on tenant_id
        pattern = rf"CREATE INDEX IF NOT EXISTS ix_{table}_tenant_id ON public\.{table}\(tenant_id\)"
        assert re.search(pattern, migration_sql, re.IGNORECASE), f"Missing tenant_id index for table: {table}"


class TestOldPoliciesDropped:
    """Verify old permissive anon policies are removed."""

    @pytest.mark.parametrize("table", TENANT_SCOPED_TABLES)
    def test_old_anon_read_policy_dropped(self, migration_sql: str, table: str) -> None:
        pattern = rf'DROP POLICY IF EXISTS "Allow basic anon read" ON public\.{table}'
        assert re.search(pattern, migration_sql), f"Old anon read policy not dropped for table: {table}"


class TestTenantPoliciesCreated:
    """Verify new tenant-scoped policies for all operations."""

    OPERATIONS = ["select", "insert", "update", "delete"]

    @pytest.mark.parametrize("table", TENANT_SCOPED_TABLES)
    @pytest.mark.parametrize("op", OPERATIONS)
    def test_tenant_policy_exists(self, migration_sql: str, table: str, op: str) -> None:
        pattern = rf'CREATE POLICY "tenant_{op}" ON public\.{table}'
        assert re.search(pattern, migration_sql), f"Missing tenant_{op} policy for table: {table}"

    @pytest.mark.parametrize("table", TENANT_SCOPED_TABLES)
    def test_select_uses_using_clause(self, migration_sql: str, table: str) -> None:
        # Find the SELECT policy for this table and check it has USING clause
        pattern = rf'CREATE POLICY "tenant_select" ON public\.{table}\s+FOR SELECT TO authenticated\s+USING \(tenant_id = public\.get_user_tenant_id\(\)\)'
        assert re.search(pattern, migration_sql), f"tenant_select policy for {table} missing correct USING clause"

    @pytest.mark.parametrize("table", TENANT_SCOPED_TABLES)
    def test_insert_uses_with_check(self, migration_sql: str, table: str) -> None:
        pattern = rf'CREATE POLICY "tenant_insert" ON public\.{table}\s+FOR INSERT TO authenticated\s+WITH CHECK \(tenant_id = public\.get_user_tenant_id\(\)\)'
        assert re.search(pattern, migration_sql), f"tenant_insert policy for {table} missing correct WITH CHECK clause"

    @pytest.mark.parametrize("table", TENANT_SCOPED_TABLES)
    def test_policies_target_authenticated_role(self, migration_sql: str, table: str) -> None:
        # All policies for each table should target 'authenticated' role
        patterns = [
            rf"ON public\.{table}\s+FOR SELECT TO authenticated",
            rf"ON public\.{table}\s+FOR INSERT TO authenticated",
            rf"ON public\.{table}\s+FOR UPDATE TO authenticated",
            rf"ON public\.{table}\s+FOR DELETE TO authenticated",
        ]
        for p in patterns:
            assert re.search(p, migration_sql), f"Policy for {table} not targeting authenticated role: {p}"


class TestRLSEnabled:
    """Verify RLS is enabled on all tenant-scoped tables."""

    @pytest.mark.parametrize("table", TENANT_SCOPED_TABLES)
    def test_rls_enabled(self, migration_sql: str, table: str) -> None:
        pattern = rf"ALTER TABLE public\.{table} ENABLE ROW LEVEL SECURITY"
        assert re.search(pattern, migration_sql), f"RLS not enabled for table: {table}"


class TestNonTenantTablesExcluded:
    """Verify system tables don't get tenant policies."""

    @pytest.mark.parametrize("table", NON_TENANT_TABLES)
    def test_no_tenant_policy(self, migration_sql: str, table: str) -> None:
        pattern = rf'CREATE POLICY "tenant_select" ON public\.{table}'
        assert not re.search(pattern, migration_sql), f"Non-tenant table {table} should NOT have tenant policies"


class TestServiceRoleBypass:
    """Verify service role bypass is documented."""

    def test_service_role_comment_in_migration(self, migration_sql: str) -> None:
        assert "service_role" in migration_sql.lower() or "service role" in migration_sql.lower()

    def test_no_explicit_service_role_policy(self, migration_sql: str) -> None:
        # Supabase service_role bypasses RLS by default, so no policy needed
        assert "TO service_role" not in migration_sql, (
            "No explicit service_role policy should be created (Supabase bypasses RLS for service_role)"
        )


class TestAlembicMigration:
    """Verify the Alembic-side migration."""

    def test_creates_helper_function(self, alembic_migration_text: str) -> None:
        assert "get_user_tenant_id" in alembic_migration_text

    def test_enables_rls_on_tables(self, alembic_migration_text: str) -> None:
        assert "ENABLE ROW LEVEL SECURITY" in alembic_migration_text

    def test_has_downgrade(self, alembic_migration_text: str) -> None:
        assert "def downgrade" in alembic_migration_text

    def test_downgrade_disables_rls(self, alembic_migration_text: str) -> None:
        assert "DISABLE ROW LEVEL SECURITY" in alembic_migration_text

    def test_downgrade_drops_function(self, alembic_migration_text: str) -> None:
        assert "DROP FUNCTION" in alembic_migration_text

    def test_all_tenant_tables_listed(self, alembic_migration_text: str) -> None:
        for table in TENANT_SCOPED_TABLES:
            assert table in alembic_migration_text, f"Alembic migration missing table: {table}"

    def test_revision_id(self, alembic_migration_text: str) -> None:
        assert 'revision: str = "014"' in alembic_migration_text


class TestDocumentation:
    """Verify RLS documentation."""

    def test_docs_exist(self) -> None:
        assert RLS_DOCS.exists()

    def test_docs_list_all_tenant_tables(self) -> None:
        docs_text = RLS_DOCS.read_text()
        for table in TENANT_SCOPED_TABLES:
            assert table in docs_text, f"RLS documentation missing table: {table}"

    def test_docs_mention_service_role(self) -> None:
        docs_text = RLS_DOCS.read_text()
        assert "service_role" in docs_text or "service role" in docs_text.lower()

    def test_docs_mention_helper_function(self) -> None:
        docs_text = RLS_DOCS.read_text()
        assert "get_user_tenant_id" in docs_text

    def test_docs_list_excluded_tables(self) -> None:
        docs_text = RLS_DOCS.read_text()
        for table in NON_TENANT_TABLES:
            assert table in docs_text, f"RLS documentation should list excluded table: {table}"
