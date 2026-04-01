"""Solstein CLI application — Click command group.

STORY-118: All commands call the Solstein API via HTTP. Zero direct
domain-layer imports. The CLI is a first-class API client, not a
domain bypass tool.
"""

from __future__ import annotations

import json
import sys
import time

import click

from solstein.cli.api_client import APIError, SolsteinAPIClient
from solstein.cli.auth import (
    clear_credentials,
    get_access_token,
    get_api_url,
    store_credentials,
)

# -- Shared output helpers ----------------------------------------------------

_JSON_OUTPUT = False


def _echo_json(data: object) -> None:
    """Print data as formatted JSON to stdout."""
    click.echo(json.dumps(data, indent=2, default=str))


def _echo(msg: str) -> None:
    """Print human-readable message (suppressed when --output json)."""
    if not _JSON_OUTPUT:
        click.echo(msg)


def _client() -> SolsteinAPIClient:
    """Create an API client using stored credentials."""
    return SolsteinAPIClient()


# -- Top-level group ----------------------------------------------------------


@click.group()
@click.option("--output", type=click.Choice(["text", "json"]), default="text",
              help="Output format (text or json)")
@click.version_option(package_name="solstein")
def cli(output: str) -> None:
    """SolStein -- AI-Powered Competitive Intelligence Platform.

    All commands communicate with the Solstein API. Run 'solstein login'
    first to authenticate.
    """
    global _JSON_OUTPUT  # noqa: PLW0603
    _JSON_OUTPUT = output == "json"


# -- Auth commands ------------------------------------------------------------


@cli.command()
@click.option("--email", prompt=True, help="Account email")
@click.option("--password", prompt=True, hide_input=True, help="Account password")
@click.option("--api-url", default=None, help="API base URL (default: http://localhost:8000)")
def login(email: str, password: str, api_url: str | None) -> None:
    """Authenticate with the Solstein API and store credentials."""
    url = api_url or get_api_url()
    client = SolsteinAPIClient(base_url=url)
    try:
        result = client.login(email, password)
        store_credentials(
            access_token=result["access_token"],
            refresh_token=result.get("refresh_token", ""),
            api_url=url,
        )
        if _JSON_OUTPUT:
            _echo_json({"status": "ok", "email": email})
        else:
            click.echo(f"Logged in as {email}")
            click.echo(f"Credentials stored in ~/.solstein/credentials.json")
    except APIError as exc:
        if _JSON_OUTPUT:
            _echo_json({"status": "error", "detail": exc.detail})
        else:
            click.echo(f"Login failed: {exc.detail}", err=True)
        sys.exit(1)


@cli.command()
def logout() -> None:
    """Remove stored credentials."""
    clear_credentials()
    if _JSON_OUTPUT:
        _echo_json({"status": "ok"})
    else:
        click.echo("Logged out. Credentials removed.")


@cli.command()
def whoami() -> None:
    """Show current authentication status."""
    token = get_access_token()
    url = get_api_url()
    if token:
        if _JSON_OUTPUT:
            _echo_json({"authenticated": True, "api_url": url})
        else:
            click.echo(f"Authenticated (API: {url})")
    else:
        if _JSON_OUTPUT:
            _echo_json({"authenticated": False})
        else:
            click.echo("Not logged in. Run 'solstein login' first.")


# -- Company commands ---------------------------------------------------------


@cli.group()
def companies() -> None:
    """Manage companies."""


@companies.command(name="list")
@click.option("--limit", default=20, help="Number of results")
@click.option("--offset", default=0, help="Pagination offset")
def companies_list(limit: int, offset: int) -> None:
    """List companies from the API."""
    client = _client()
    try:
        data = client.list_companies(limit=limit, offset=offset)
        if _JSON_OUTPUT:
            _echo_json(data)
        else:
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = data.get("items", data.get("data", []))
            else:
                items = []
            click.echo(f"{'Name':<30} {'ID':<36} {'Industry':<20}")
            click.echo("-" * 86)
            for item in items:
                name = item.get("name", "N/A")
                cid = item.get("id", "N/A")
                industry = item.get("industry", "N/A")
                click.echo(f"{name:<30} {cid:<36} {industry:<20}")
            click.echo(f"\n{len(items)} companies shown")
    except APIError as exc:
        click.echo(f"Error: {exc.detail}", err=True)
        sys.exit(1)


@companies.command(name="get")
@click.argument("company_id")
def companies_get(company_id: str) -> None:
    """Get details for a specific company."""
    client = _client()
    try:
        data = client.get_company(company_id)
        if _JSON_OUTPUT:
            _echo_json(data)
        else:
            click.echo(f"Company: {data.get('name', 'N/A')}")
            click.echo(f"ID:      {data.get('id', 'N/A')}")
            click.echo(f"Industry: {data.get('industry', 'N/A')}")
            financials = data.get("financials", {})
            if financials:
                click.echo(f"Revenue:  {financials.get('revenue', 'N/A')}")
                click.echo(f"Growth:   {financials.get('growth_rate', 'N/A')}%")
    except APIError as exc:
        click.echo(f"Error: {exc.detail}", err=True)
        sys.exit(1)


# -- Research commands --------------------------------------------------------


@cli.command()
@click.argument("company_name")
@click.option("--wait/--no-wait", default=True, help="Wait for job to complete")
@click.option("--poll-interval", default=5, help="Seconds between status polls")
def research(company_name: str, wait: bool, poll_interval: int) -> None:
    """Start a research job for a company.

    Calls POST /jobs/research and optionally polls until completion.
    """
    client = _client()
    try:
        result = client.start_research(company_name)
        job_id = result.get("job_id", result.get("id"))
        if _JSON_OUTPUT and not wait:
            _echo_json(result)
            return

        _echo(f"Research job started: {job_id}")

        if not wait:
            return

        _echo("Polling for completion...")
        while True:
            status_data = client.get_job_status(job_id)
            state = status_data.get("status", "unknown")
            _echo(f"  Status: {state}")
            if state in ("completed", "failed", "cancelled"):
                break
            time.sleep(poll_interval)

        if _JSON_OUTPUT:
            _echo_json(status_data)
        elif state == "completed":
            click.echo(f"Research complete for '{company_name}'")
        else:
            click.echo(f"Research {state}: {status_data.get('error', 'unknown')}", err=True)
            sys.exit(1)
    except APIError as exc:
        if _JSON_OUTPUT:
            _echo_json({"status": "error", "detail": exc.detail})
        else:
            click.echo(f"Error: {exc.detail}", err=True)
        sys.exit(1)


# -- Export commands ----------------------------------------------------------


@cli.command(name="export")
@click.argument("company_id")
@click.option("--format", "fmt", default="excel",
              type=click.Choice(["excel", "json", "markdown"]),
              help="Export format")
def export_cmd(company_id: str, fmt: str) -> None:
    """Export company data in the specified format."""
    client = _client()
    try:
        result = client.start_export(company_id, fmt)
        if _JSON_OUTPUT:
            _echo_json(result)
        else:
            click.echo(f"Export started: {result.get('job_id', result.get('id', 'N/A'))}")
            click.echo(f"Format: {fmt}")
    except APIError as exc:
        click.echo(f"Error: {exc.detail}", err=True)
        sys.exit(1)


# -- Job status ---------------------------------------------------------------


@cli.command()
@click.argument("job_id")
def status(job_id: str) -> None:
    """Check the status of a job."""
    client = _client()
    try:
        data = client.get_job_status(job_id)
        if _JSON_OUTPUT:
            _echo_json(data)
        else:
            click.echo(f"Job:    {job_id}")
            click.echo(f"Status: {data.get('status', 'unknown')}")
            if data.get("progress"):
                click.echo(f"Progress: {data['progress']}%")
            if data.get("error"):
                click.echo(f"Error: {data['error']}")
    except APIError as exc:
        click.echo(f"Error: {exc.detail}", err=True)
        sys.exit(1)


# -- Health -------------------------------------------------------------------


@cli.command()
def health() -> None:
    """Check API health."""
    client = _client()
    try:
        data = client.health()
        if _JSON_OUTPUT:
            _echo_json(data)
        else:
            click.echo(f"API: {get_api_url()}")
            click.echo(f"Status: {data.get('status', 'ok')}")
    except APIError as exc:
        click.echo(f"API unreachable: {exc.detail}", err=True)
        sys.exit(1)
    except Exception as exc:
        click.echo(f"API unreachable: {exc}", err=True)
        sys.exit(1)


# -- Entrypoint ---------------------------------------------------------------


def main() -> None:
    """Package entrypoint registered in pyproject.toml."""
    cli()
