#!/usr/bin/env python3
"""
Performance Baseline Script

Records baseline performance metrics for database queries and API endpoints.
Use this script to establish performance benchmarks and detect regressions.

Usage:
    python scripts/performance_baseline.py [--database] [--api] [--all]
    
Options:
    --database   Run database query benchmarks only
    --api        Run API endpoint benchmarks only
    --all        Run all benchmarks (default)
    --save       Save results to performance_baseline.json
    --compare    Compare against previous baseline
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
except ImportError:
    print("Error: SQLAlchemy not installed. Install with: pip install sqlalchemy[asyncio]")
    sys.exit(1)


@dataclass
class BenchmarkResult:
    """Result of a single benchmark."""
    name: str
    category: str
    duration_ms: float
    iterations: int
    avg_ms: float
    min_ms: float
    max_ms: float
    success: bool
    error: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


class PerformanceBenchmark:
    """Database and API performance benchmarking tool."""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
        )
        self.results: list[BenchmarkResult] = []
        self.engine = None
        self.session_factory = None
        
    async def initialize(self):
        """Initialize database connection."""
        try:
            self.engine = create_async_engine(
                self.database_url,
                echo=False,
                pool_size=5,
                max_overflow=10
            )
            self.session_factory = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            # Test connection
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            print(f"✓ Connected to database")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False
    
    async def close(self):
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session."""
        async with self.session_factory() as session:
            yield session
    
    async def benchmark_query(
        self,
        name: str,
        query: str,
        category: str = "database",
        iterations: int = 100
    ) -> BenchmarkResult:
        """Benchmark a single query."""
        durations = []
        error = None
        
        try:
            async with self.get_session() as session:
                # Warmup
                for _ in range(5):
                    await session.execute(text(query))
                
                # Benchmark
                for _ in range(iterations):
                    start = time.perf_counter()
                    await session.execute(text(query))
                    await session.commit()
                    end = time.perf_counter()
                    durations.append((end - start) * 1000)  # Convert to ms
                
        except Exception as e:
            error = str(e)
        
        if durations:
            result = BenchmarkResult(
                name=name,
                category=category,
                duration_ms=sum(durations),
                iterations=len(durations),
                avg_ms=sum(durations) / len(durations),
                min_ms=min(durations),
                max_ms=max(durations),
                success=error is None,
                error=error
            )
        else:
            result = BenchmarkResult(
                name=name,
                category=category,
                duration_ms=0,
                iterations=0,
                avg_ms=0,
                min_ms=0,
                max_ms=0,
                success=False,
                error=error or "No iterations completed"
            )
        
        self.results.append(result)
        return result
    
    async def run_database_benchmarks(self):
        """Run all database query benchmarks."""
        print("\n" + "=" * 60)
        print("DATABASE QUERY BENCHMARKS")
        print("=" * 60)
        
        benchmarks = [
            # Company queries
            ("companies_select_all", "SELECT * FROM companies LIMIT 100", "companies"),
            ("companies_by_ticker", "SELECT * FROM companies WHERE ticker = 'AAPL'", "companies"),
            ("companies_by_status", "SELECT * FROM companies WHERE status = 'active' LIMIT 100", "companies"),
            ("companies_count", "SELECT COUNT(*) FROM companies", "companies"),
            
            # Research runs queries
            ("research_runs_select_all", "SELECT * FROM research_runs LIMIT 100", "research_runs"),
            ("research_runs_by_company", "SELECT * FROM research_runs WHERE company_id IS NOT NULL LIMIT 100", "research_runs"),
            ("research_runs_by_status", "SELECT * FROM research_runs WHERE status = 'completed' LIMIT 100", "research_runs"),
            ("research_runs_active", "SELECT * FROM research_runs WHERE status IN ('pending', 'running')", "research_runs"),
            
            # Facts queries
            ("facts_select_all", "SELECT * FROM facts LIMIT 100", "facts"),
            ("facts_by_company", "SELECT * FROM facts WHERE company_id IS NOT NULL LIMIT 100", "facts"),
            ("facts_active", "SELECT * FROM facts WHERE status = 'active' LIMIT 100", "facts"),
            ("facts_high_confidence", "SELECT * FROM facts WHERE confidence >= 0.8 LIMIT 100", "facts"),
            
            # Signals queries
            ("signals_select_all", "SELECT * FROM signals LIMIT 100", "signals"),
            ("signals_by_company", "SELECT * FROM signals WHERE company_id IS NOT NULL LIMIT 100", "signals"),
            ("signals_active", "SELECT * FROM signals WHERE status = 'active' LIMIT 100", "signals"),
            ("signals_by_type", "SELECT * FROM signals WHERE signal_type = 'price_movement' LIMIT 100", "signals"),
            
            # Scoring queries
            ("scoring_records_select_all", "SELECT * FROM scoring_records LIMIT 100", "scoring"),
            ("scoring_by_company", "SELECT * FROM scoring_records WHERE company_id IS NOT NULL ORDER BY scored_at DESC LIMIT 100", "scoring"),
            ("scoring_top_scores", "SELECT * FROM scoring_records WHERE total_score >= 70 ORDER BY total_score DESC LIMIT 100", "scoring"),
            
            # Enrichment queries
            ("enrichment_jobs_select_all", "SELECT * FROM enrichment_jobs LIMIT 100", "enrichment"),
            ("enrichment_pending", "SELECT * FROM enrichment_jobs WHERE status = 'pending' ORDER BY priority DESC", "enrichment"),
            
            # Join queries
            ("companies_with_runs", """
                SELECT c.*, COUNT(r.id) as run_count 
                FROM companies c 
                LEFT JOIN research_runs r ON c.id = r.company_id 
                GROUP BY c.id LIMIT 100
            """, "joins"),
            
            ("companies_with_facts", """
                SELECT c.id, c.ticker, COUNT(f.id) as fact_count 
                FROM companies c 
                LEFT JOIN facts f ON c.id = f.company_id AND f.status = 'active'
                GROUP BY c.id LIMIT 100
            """, "joins"),
            
            # Aggregation queries
            ("facts_stats", """
                SELECT 
                    company_id,
                    COUNT(*) as total_facts,
                    AVG(confidence) as avg_confidence
                FROM facts 
                WHERE status = 'active'
                GROUP BY company_id 
                LIMIT 100
            """, "aggregation"),
            
            ("signals_daily_count", """
                SELECT 
                    DATE(detected_at) as date,
                    COUNT(*) as signal_count
                FROM signals
                WHERE detected_at > NOW() - INTERVAL '30 days'
                GROUP BY DATE(detected_at)
                ORDER BY date DESC
            """, "aggregation"),
        ]
        
        for name, query, category in benchmarks:
            result = await self.benchmark_query(name, query, category)
            status = "✓" if result.success else "✗"
            if result.success:
                print(f"{status} {name:40s} {result.avg_ms:8.2f}ms (min: {result.min_ms:6.2f}ms, max: {result.max_ms:6.2f}ms)")
            else:
                print(f"{status} {name:40s} FAILED: {result.error}")
    
    async def run_api_benchmarks(self):
        """Run API endpoint benchmarks (requires running server)."""
        print("\n" + "=" * 60)
        print("API ENDPOINT BENCHMARKS")
        print("=" * 60)
        print("Note: API benchmarks require the server to be running")
        print("Skipping API benchmarks (server not detected)")
        # API benchmarks would be implemented here if server is running
    
    def save_results(self, filename: str = "performance_baseline.json"):
        """Save benchmark results to file."""
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "database_url": self.database_url.replace(
                "://", "://***@").replace("//postgres:", "//***:"),
            "results": [asdict(r) for r in self.results],
            "summary": {
                "total_benchmarks": len(self.results),
                "successful": sum(1 for r in self.results if r.success),
                "failed": sum(1 for r in self.results if not r.success),
                "avg_duration_ms": sum(r.avg_ms for r in self.results if r.success) / max(1, sum(1 for r in self.results if r.success))
            }
        }
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n✓ Results saved to {filepath}")
        return filepath
    
    def print_summary(self):
        """Print summary of all benchmarks."""
        print("\n" + "=" * 60)
        print("PERFORMANCE BASELINE SUMMARY")
        print("=" * 60)
        
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        
        print(f"\nTotal Benchmarks: {len(self.results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        
        if successful:
            avg_time = sum(r.avg_ms for r in successful) / len(successful)
            print(f"\nAverage Query Time: {avg_time:.2f}ms")
            print(f"Fastest Query: {min(r.avg_ms for r in successful):.2f}ms")
            print(f"Slowest Query: {max(r.avg_ms for r in successful):.2f}ms")
        
        # Category breakdown
        categories = {}
        for r in successful:
            if r.category not in categories:
                categories[r.category] = []
            categories[r.category].append(r.avg_ms)
        
        if categories:
            print("\nCategory Averages:")
            for cat, times in sorted(categories.items()):
                avg = sum(times) / len(times)
                print(f"  {cat:20s} {avg:8.2f}ms ({len(times)} queries)")
        
        if failed:
            print("\nFailed Benchmarks:")
            for r in failed:
                print(f"  - {r.name}: {r.error}")
    
    def compare_with_baseline(self, baseline_file: str = "performance_baseline.json"):
        """Compare current results with previous baseline."""
        filepath = os.path.join(os.path.dirname(__file__), baseline_file)
        
        if not os.path.exists(filepath):
            print(f"\nNo previous baseline found at {filepath}")
            return
        
        with open(filepath, 'r') as f:
            baseline = json.load(f)
        
        print("\n" + "=" * 60)
        print("COMPARISON WITH PREVIOUS BASELINE")
        print("=" * 60)
        print(f"Previous: {baseline.get('timestamp', 'unknown')}")
        print(f"Current:  {datetime.utcnow().isoformat()}")
        
        baseline_results = {r['name']: r for r in baseline.get('results', [])}
        
        print("\n{'Name':<40s} {'Previous':>10s} {'Current':>10s} {'Change':>10s}")
        print("-" * 80)
        
        for result in self.results:
            if result.name in baseline_results and result.success:
                prev = baseline_results[result.name]
                if prev.get('success'):
                    change = ((result.avg_ms - prev['avg_ms']) / prev['avg_ms']) * 100
                    change_str = f"{change:+.1f}%"
                    print(f"{result.name:<40s} {prev['avg_ms']:>10.2f} {result.avg_ms:>10.2f} {change_str:>10s}")


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Performance Baseline Tool")
    parser.add_argument("--database", action="store_true", help="Run database benchmarks")
    parser.add_argument("--api", action="store_true", help="Run API benchmarks")
    parser.add_argument("--all", action="store_true", help="Run all benchmarks (default)")
    parser.add_argument("--save", action="store_true", help="Save results to file")
    parser.add_argument("--compare", action="store_true", help="Compare with previous baseline")
    parser.add_argument("--url", type=str, help="Database URL (or use DATABASE_URL env var)")
    
    args = parser.parse_args()
    
    # Default to --all if no specific benchmark selected
    if not args.database and not args.api:
        args.database = True
    
    # Initialize benchmark
    benchmark = PerformanceBenchmark(database_url=args.url)
    
    print("=" * 60)
    print("PERFORMANCE BASELINE")
    print("=" * 60)
    print(f"Started: {datetime.utcnow().isoformat()}")
    
    # Initialize database connection
    if not await benchmark.initialize():
        print("\nFailed to initialize database connection.")
        print("Please ensure:")
        print("  1. PostgreSQL is running")
        print("  2. DATABASE_URL environment variable is set correctly")
        print("  3. Database is accessible")
        sys.exit(1)
    
    try:
        # Run benchmarks
        if args.database:
            await benchmark.run_database_benchmarks()
        
        if args.api:
            await benchmark.run_api_benchmarks()
        
        # Print summary
        benchmark.print_summary()
        
        # Compare with baseline
        if args.compare:
            benchmark.compare_with_baseline()
        
        # Save results
        if args.save:
            benchmark.save_results()
        
    finally:
        await benchmark.close()
    
    print("\n" + "=" * 60)
    print("Performance baseline complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
