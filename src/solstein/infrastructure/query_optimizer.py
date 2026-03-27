"""Query optimization utilities for efficient database operations.

EPIC-025 Story 7: Implements advanced query optimization patterns including:
- Select only required columns
- Use EXISTS for semi-joins
- Batch operations
- Query plan analysis
"""

from typing import Any

from sqlalchemy import Column, exists, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query


class QueryOptimizer:
    """Utilities for optimizing database queries."""

    @staticmethod
    def build_column_select(table: Any, columns: list[str] | None = None) -> Query:
        """Build a query selecting only specific columns.

        Args:
            table: SQLAlchemy table/model class.
            columns: List of column names to select. If None, selects all.

        Returns:
            Select query with only required columns.

        Example:
            # Instead of: SELECT * FROM companies
            # Use: SELECT id, name, industry FROM companies
            query = QueryOptimizer.build_column_select(
                CompanyRecord, ['id', 'name', 'industry']
            )
        """
        if not columns:
            return select(table)

        column_objects = [getattr(table, col) for col in columns if hasattr(table, col)]
        return select(*column_objects)

    @staticmethod
    def exists_subquery(table: Any, where_conditions: list) -> exists:
        """Build an EXISTS subquery for efficient semi-joins.

        EXISTS stops at the first match, unlike IN which loads all matches.

        Args:
            table: Table to check existence in.
            where_conditions: List of WHERE conditions.

        Returns:
            EXISTS construct for use in queries.

        Example:
            # Efficient: Stop at first match
            has_scoring = QueryOptimizer.exists_subquery(
                ScoringRecord,
                [ScoringRecord.company_id == CompanyRecord.id]
            )
            query = select(CompanyRecord).where(has_scoring)
        """
        subquery = select(table).where(*where_conditions)
        return exists(subquery)

    @staticmethod
    async def batch_insert(
        session: AsyncSession,
        table: Any,
        records: list[dict[str, Any]],
        batch_size: int = 1000,
    ) -> int:
        """Insert records in batches for efficiency.

        Args:
            session: Database session.
            table: Target table.
            records: List of record dictionaries.
            batch_size: Number of records per batch.

        Returns:
            Total number of records inserted.

        Example:
            records = [{'name': 'A'}, {'name': 'B'}, ...]
            count = await QueryOptimizer.batch_insert(
                session, CompanyRecord, records, batch_size=500
            )
        """
        if not records:
            return 0

        total_inserted = 0

        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            # Use insert() from sqlalchemy for both Table and ORM model classes
            target_table = table.__table__ if hasattr(table, "__table__") else table
            await session.execute(target_table.insert(), batch)
            total_inserted += len(batch)

        return total_inserted

    @staticmethod
    def optimize_pagination(
        query: Query, cursor_column: Column, cursor_value: Any | None = None, limit: int = 100
    ) -> Query:
        """Apply cursor-based pagination for efficient large dataset paging.

        Keyset pagination is more efficient than OFFSET for large tables.

        Args:
            query: Base query.
            cursor_column: Column to use for cursor (should be indexed).
            cursor_value: Last seen value for cursor (None for first page).
            limit: Number of records per page.

        Returns:
            Query with pagination applied.

        Example:
            query = select(CompanyRecord).order_by(CompanyRecord.id)
            page1 = await session.execute(
                QueryOptimizer.optimize_pagination(query, CompanyRecord.id, limit=50)
            )
            # Get last ID from page1
            last_id = ...
            page2 = await session.execute(
                QueryOptimizer.optimize_pagination(query, CompanyRecord.id, last_id, 50)
            )
        """
        query = query.order_by(cursor_column)

        if cursor_value is not None:
            query = query.where(cursor_column > cursor_value)

        return query.limit(limit)

    @staticmethod
    def add_hint(query: Query, hint: str) -> Query:
        """Add a PostgreSQL query hint.

        Args:
            query: Base query.
            hint: Query hint (e.g., "PARALLEL 4", "INDEX (companies)").

        Returns:
            Query with hint prefix.

        Note:
            Use sparingly. PostgreSQL's planner is usually smarter than humans.
        """
        # Prefix the query with a comment hint
        # This is a placeholder - actual implementation depends on SQLAlchemy version
        return query.prefix_with(f"/*+ {hint} */")


class QueryPlanAnalyzer:
    """Analyze query execution plans for optimization opportunities."""

    @staticmethod
    async def explain_query(
        session: AsyncSession,
        query: Any,
        analyze: bool = True,
        buffers: bool = True,
    ) -> dict[str, Any]:
        """Get EXPLAIN output for a query.

        Args:
            session: Database session.
            query: SQLAlchemy query or raw SQL string.
            analyze: Execute query and show actual times.
            buffers: Show buffer usage statistics.

        Returns:
            Query plan as dictionary.

        Example:
            query = select(CompanyRecord).where(CompanyRecord.industry == 'Tech')
            plan = await QueryPlanAnalyzer.explain_query(session, query)
            print(f"Cost: {plan['Plan']['Total Cost']}")
        """
        # Convert query to SQL
        if hasattr(query, "compile"):
            sql = str(query.compile(compile_kwargs={"literal_binds": True}))
        else:
            sql = str(query)

        # Build EXPLAIN command
        options = []
        if analyze:
            options.append("ANALYZE")
        if buffers:
            options.append("BUFFERS")
        options.append("FORMAT JSON")

        explain_sql = f"EXPLAIN ({', '.join(options)}) {sql}"

        result = await session.execute(text(explain_sql))
        row = result.fetchone()

        if row:
            import json

            return json.loads(row[0])

        return {}

    @staticmethod
    def extract_plan_metrics(plan: dict[str, Any]) -> dict[str, Any]:
        """Extract key metrics from query plan.

        Args:
            plan: Query plan dictionary from explain_query.

        Returns:
            Dictionary of key metrics.
        """
        if not plan or "Plan" not in plan:
            return {}

        p = plan["Plan"]

        return {
            "total_cost": p.get("Total Cost"),
            "startup_cost": p.get("Startup Cost"),
            "actual_time": p.get("Actual Total Time"),
            "actual_rows": p.get("Actual Rows"),
            "estimated_rows": p.get("Plan Rows"),
            "node_type": p.get("Node Type"),
            "index_name": p.get("Index Name"),
            "relation": p.get("Relation Name"),
            "shared_hit_blocks": plan.get("Planning", {}).get("Shared Hit Blocks"),
            "shared_read_blocks": plan.get("Planning", {}).get("Shared Read Blocks"),
        }

    @staticmethod
    def identify_slow_operations(plan: dict[str, Any]) -> list[dict[str, Any]]:
        """Identify potentially slow operations in query plan.

        Args:
            plan: Query plan dictionary.

        Returns:
            List of operations that may need optimization.
        """
        slow_ops = []

        def traverse(node: dict[str, Any], path: str = ""):
            node_type = node.get("Node Type", "")
            actual_time = node.get("Actual Total Time", 0)

            # Flag slow operations
            concerns = []

            if node_type == "Seq Scan" and actual_time > 100:
                concerns.append(f"Sequential scan taking {actual_time:.2f}ms - consider adding index")

            if node_type == "Nested Loop" and actual_time > 50:
                concerns.append(f"Nested loop join slow ({actual_time:.2f}ms) - check join conditions")

            if node.get("Actual Rows", 0) > node.get("Plan Rows", 0) * 10:
                concerns.append("Large row estimate discrepancy - stale statistics?")

            if concerns:
                slow_ops.append(
                    {
                        "node_type": node_type,
                        "path": path,
                        "time_ms": actual_time,
                        "concerns": concerns,
                    }
                )

            # Traverse subplans
            for i, child in enumerate(node.get("Plans", [])):
                traverse(child, f"{path}/Plans[{i}]")

        if "Plan" in plan:
            traverse(plan["Plan"])

        return slow_ops


class BatchQueryBuilder:
    """Build efficient batch queries."""

    @staticmethod
    def build_upsert(
        table: Any,
        records: list[dict[str, Any]],
        conflict_columns: list[str],
        update_columns: list[str],
    ) -> str:
        """Build PostgreSQL upsert (INSERT ... ON CONFLICT DO UPDATE).

        Args:
            table: Target table.
            records: Records to upsert.
            conflict_columns: Columns for conflict detection.
            update_columns: Columns to update on conflict.

        Returns:
            SQL upsert statement.

        Note:
            Returns raw SQL - use with caution and parameterization.
        """
        if not records:
            return ""

        def _quote_ident(name: str) -> str:
            """Quote a SQL identifier to prevent injection."""
            # Double any existing quotes and wrap in quotes
            return '"' + name.replace('"', '""') + '"'

        # Build column list
        columns = list(records[0].keys())
        col_str = ", ".join(_quote_ident(c) for c in columns)

        # Build values placeholders
        placeholders = []
        for i, record in enumerate(records):
            row_placeholders = [f":{col}_{i}" for col in columns]
            placeholders.append(f"({', '.join(row_placeholders)})")

        values_str = ", ".join(placeholders)

        # Build conflict and update clauses
        conflict_str = ", ".join(_quote_ident(c) for c in conflict_columns)
        updates = [f"{_quote_ident(col)} = EXCLUDED.{_quote_ident(col)}" for col in update_columns]
        update_str = ", ".join(updates)

        table_name = _quote_ident(table.__tablename__)

        return f"""
            INSERT INTO {table_name} ({col_str})
            VALUES {values_str}
            ON CONFLICT ({conflict_str})
            DO UPDATE SET {update_str}
        """

    @staticmethod
    def build_in_batches(values: list[Any], batch_size: int = 1000) -> list[list[Any]]:
        """Split values into batches for IN clause efficiency.

        PostgreSQL has limits on IN clause size. Split large lists.

        Args:
            values: List of values.
            batch_size: Maximum batch size.

        Returns:
            List of batches.
        """
        return [values[i : i + batch_size] for i in range(0, len(values), batch_size)]


# Convenience function for explain
async def explain(session: AsyncSession, query: Any, analyze: bool = True) -> dict[str, Any]:
    """Quick explain function.

    Args:
        session: Database session.
        query: Query to explain.
        analyze: Whether to execute and analyze.

    Returns:
        Query plan dictionary.
    """
    return await QueryPlanAnalyzer.explain_query(session, query, analyze=analyze)
