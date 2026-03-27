"""Profiling dashboard for viewing performance metrics.

EPIC-023 Story 1: Web-based dashboard for viewing profiling results.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from ..profiling import profiler

router = APIRouter(prefix="/profiling", tags=["profiling"])


@router.get("/stats")
async def get_profiling_stats() -> dict[str, Any]:
    """Get profiling statistics."""
    if not profiler.results:
        return {"message": "No profiling data available"}

    # Group by name
    by_name: dict[str, list] = {}
    for result in profiler.results:
        by_name.setdefault(result.name, []).append(result)

    stats = {}
    for name, results in by_name.items():
        durations = [r.duration_ms for r in results]
        stats[name] = {
            "count": len(results),
            "avg_duration_ms": sum(durations) / len(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "total_duration_ms": sum(durations),
        }

    return {
        "total_profiles": len(profiler.results),
        "unique_functions": len(by_name),
        "by_function": stats,
    }


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard() -> str:
    """Get profiling dashboard HTML."""
    stats = await get_profiling_stats()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Solstein Performance Dashboard</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            h1 {{
                color: #333;
                border-bottom: 2px solid #007bff;
                padding-bottom: 10px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            .stat-card {{
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .stat-card h3 {{
                margin-top: 0;
                color: #007bff;
            }}
            .metric {{
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }}
            .metric:last-child {{
                border-bottom: none;
            }}
            .metric-value {{
                font-weight: bold;
                color: #333;
            }}
            .status {{
                padding: 10px 20px;
                border-radius: 4px;
                margin-bottom: 20px;
            }}
            .status.enabled {{
                background: #d4edda;
                color: #155724;
            }}
            .status.disabled {{
                background: #f8d7da;
                color: #721c24;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Solstein Performance Dashboard</h1>

            <div class="status {"enabled" if profiler.is_enabled else "disabled"}">
                Profiling is {"ENABLED" if profiler.is_enabled else "DISABLED"}
                {" - Set SOLSTEIN_PROFILING=true to enable" if not profiler.is_enabled else ""}
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <h3>📊 Overview</h3>
                    <div class="metric">
                        <span>Total Profiles:</span>
                        <span class="metric-value">{stats.get("total_profiles", 0)}</span>
                    </div>
                    <div class="metric">
                        <span>Unique Functions:</span>
                        <span class="metric-value">{stats.get("unique_functions", 0)}</span>
                    </div>
                </div>
    """

    # Add function-specific cards
    by_function = stats.get("by_function", {})
    for func_name, func_stats in by_function.items():
        html += f"""
                <div class="stat-card">
                    <h3>⚡ {func_name}</h3>
                    <div class="metric">
                        <span>Calls:</span>
                        <span class="metric-value">{func_stats["count"]}</span>
                    </div>
                    <div class="metric">
                        <span>Avg Duration:</span>
                        <span class="metric-value">{func_stats["avg_duration_ms"]:.2f}ms</span>
                    </div>
                    <div class="metric">
                        <span>Min Duration:</span>
                        <span class="metric-value">{func_stats["min_duration_ms"]:.2f}ms</span>
                    </div>
                    <div class="metric">
                        <span>Max Duration:</span>
                        <span class="metric-value">{func_stats["max_duration_ms"]:.2f}ms</span>
                    </div>
                    <div class="metric">
                        <span>Total Time:</span>
                        <span class="metric-value">{func_stats["total_duration_ms"]:.2f}ms</span>
                    </div>
                </div>
        """

    html += """
            </div>

            <div style="margin-top: 40px; text-align: center; color: #666;">
                <p>Solstein Performance Monitoring | EPIC-023</p>
                <p>Auto-refreshes every 30 seconds</p>
            </div>
        </div>

        <script>
            // Auto-refresh every 30 seconds
            setInterval(() => {
                window.location.reload();
            }, 30000);
        </script>
    </body>
    </html>
    """

    return html


@router.post("/export")
async def export_results() -> dict[str, str]:
    """Export profiling results to JSON file."""
    from datetime import datetime

    output_path = Path(f"profiling_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    profiler.export_json(output_path)

    return {"message": f"Results exported to {output_path}", "path": str(output_path)}


@router.post("/clear")
async def clear_results() -> dict[str, str]:
    """Clear all profiling results."""
    count = len(profiler.results)
    profiler.clear()
    return {"message": f"Cleared {count} profiling results"}


@router.post("/enable")
async def enable_profiling() -> dict[str, str]:
    """Enable profiling."""
    profiler.enable()
    return {"message": "Profiling enabled"}


@router.post("/disable")
async def disable_profiling() -> dict[str, str]:
    """Disable profiling."""
    profiler.disable()
    return {"message": "Profiling disabled"}
