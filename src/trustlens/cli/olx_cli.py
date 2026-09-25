"""
TrustLens — OLX CLI Subcommand Suite (Phase 3).
"""

import asyncio
import json
import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from trustlens.olx.collector import OLXCollector
from trustlens.olx.config import INVESTIGATION_SUITES, get_investigation_config
from trustlens.olx.models import CollectionType
from trustlens.olx.server import start_server

olx_app = typer.Typer(
    name="olx",
    help="Targeted OLX Marketplace Acquisition & Investigation (Phase 3)",
    add_completion=False,
)
console = Console()


@olx_app.command("suites")
def list_suites():
    """List available targeted investigation suites."""
    table = Table(title="TrustLens — Investigation Suites (Phase 3)", show_header=True)
    table.add_column("Suite ID", style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Target Queries", style="yellow")
    table.add_column("Baseline Queries", style="dim")

    for s_id, suite in INVESTIGATION_SUITES.items():
        table.add_row(
            s_id,
            suite.name,
            f"{len(suite.target_queries)} queries",
            f"{len(suite.baseline_queries)} queries",
        )
    console.print(table)


@olx_app.command("discover")
def discover_cmd(
    investigation: str = typer.Option("INV-002", "--investigation", "-i", help="Investigation ID (INV-001, INV-002, BASELINE)"),
    query: str = typer.Option(..., "--query", "-q", help="Search query string"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum listings to discover"),
    location: str = typer.Option("india", "--location", "-loc", help="Geographic market location (e.g. india)"),
    download_media: bool = typer.Option(True, "--download-media/--no-download-media", help="Download listing photos"),
):
    """Execute search discovery and collection for a single targeted query."""
    console.print(f"[cyan]Searching OLX in [{location.upper()}] for targeted query '{query}' under suite {investigation}...[/cyan]")
    collector = OLXCollector()
    run = asyncio.run(
        collector.discover_and_collect_query(
            investigation_id=investigation,
            query=query,
            collection_type=CollectionType.TARGETED,
            limit=limit,
            location=location,
            download_media=download_media,
        )
    )

    table = Table(title=f"Discovery Run Summary: {run.run_id}", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold green")

    table.add_row("Run ID", run.run_id)
    table.add_row("Location", location.upper())
    table.add_row("Discovered Listings", str(run.discovered_count))
    table.add_row("Successfully Collected", str(run.collected_count))
    table.add_row("Failed", str(run.failed_count))
    console.print(table)


@olx_app.command("run")
def run_suite_cmd(
    investigation: str = typer.Option("INV-002", "--investigation", "-i", help="Investigation suite ID (INV-001, INV-002, BASELINE)"),
    max_results: int = typer.Option(5, "--max-results", "-m", help="Max listings per search query"),
    location: str = typer.Option("india", "--location", "-loc", help="Geographic market location (e.g. india)"),
    download_media: bool = typer.Option(True, "--download-media/--no-download-media", help="Download listing photos"),
):
    """Execute complete targeted investigation suite (Target + Baseline queries)."""
    config = get_investigation_config(investigation)
    console.print(f"[bold magenta]Launching Investigation Suite: {config.investigation_id} — {config.name} (Location: {location.upper()})[/bold magenta]")

    collector = OLXCollector()
    runs = asyncio.run(
        collector.run_investigation_suite(
            investigation_id=investigation,
            max_results_per_query=max_results,
            location=location,
            download_media=download_media,
        )
    )

    table = Table(title=f"Suite Execution Summary: {investigation}", show_header=True)
    table.add_column("Query", style="yellow")
    table.add_column("Type", style="cyan")
    table.add_column("Discovered", style="green")
    table.add_column("Collected", style="bold green")
    table.add_column("Failed", style="red")

    total_col = sum(r.collected_count for r in runs)
    for r in runs:
        table.add_row(
            r.query or "-",
            r.collection_type.value,
            str(r.discovered_count),
            str(r.collected_count),
            str(r.failed_count),
        )
    console.print(table)
    console.print(f"[green]✓ Completed suite execution. Total listings collected: {total_col}[/green]")


@olx_app.command("ingest")
def ingest_cmd(
    url: Optional[str] = typer.Option(None, "--url", "-u", help="OLX listing URL to fetch and analyze"),
    html_file: Optional[Path] = typer.Option(None, "--html", "-f", help="Saved researcher HTML file"),
    investigation: str = typer.Option("INV-002", "--investigation", "-i", help="Investigation ID"),
    collection_type: str = typer.Option("targeted", "--type", "-t", help="targeted or baseline"),
    download_media: bool = typer.Option(True, "--download-media/--no-download-media", help="Download listing photos"),
):
    """Ingest a single listing from URL or researcher-saved HTML file."""
    if not url and not html_file:
        console.print("[red]Error: You must provide either --url or --html[/red]")
        raise typer.Exit(code=1)

    collector = OLXCollector()
    c_type = CollectionType(collection_type.lower())

    if html_file:
        if not html_file.exists():
            console.print(f"[red]Error: File not found: {html_file}[/red]")
            raise typer.Exit(code=1)
        console.print(f"[cyan]Ingesting saved researcher HTML from {html_file}...[/cyan]")
        inv = asyncio.run(
            collector.ingest_html_file(
                file_path=html_file,
                investigation_id=investigation,
                collection_type=c_type,
                download_media=download_media,
            )
        )
    else:
        assert url is not None
        console.print(f"[cyan]Fetching and ingesting OLX URL: {url}...[/cyan]")
        inv = asyncio.run(
            collector.ingest_url(
                url=url,
                investigation_id=investigation,
                collection_type=c_type,
                download_media=download_media,
            )
        )

    console.print(f"[bold green]✓ Ingestion Complete![/bold green]")
    console.print(f"Investigation ID: [cyan]{inv.investigation_id}[/cyan]")
    console.print(f"Listing ID: [cyan]{inv.listing.listing_id}[/cyan]")
    console.print(f"Title: {inv.listing.title}")
    console.print(f"Observed Price: ₹{inv.listing.price or 0:,.0f}")
    console.print(f"Signals Detected: [yellow]{len(inv.signals)}[/yellow]")
    console.print(f"Media Assets: [yellow]{len(inv.media)}[/yellow]")


@olx_app.command("report")
def report_cmd(
    investigation_id: str = typer.Argument(..., help="Investigation ID (e.g. INV-OLX-000001)"),
):
    """View human-readable markdown investigation report."""
    inv_id = investigation_id.strip()
    if not inv_id.startswith("INV-"):
        inv_id = f"INV-{inv_id}"

    collector = OLXCollector()
    report_file = collector.reports_dir / f"{inv_id}.md"

    if not report_file.exists():
        console.print(f"[red]Error: Report not found for {inv_id}[/red]")
        raise typer.Exit(code=1)

    with open(report_file, "r", encoding="utf-8") as f:
        console.print(f.read())


@olx_app.command("status")
def status_cmd(
    run_id: Optional[str] = typer.Argument(None, help="Optional Run ID to inspect"),
):
    """Check status of collection runs and database metrics."""
    collector = OLXCollector()

    if run_id:
        if not collector.runs_file.exists():
            console.print("[yellow]No collection runs recorded yet.[/yellow]")
            return
        found = False
        with open(collector.runs_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    if r.get("run_id") == run_id:
                        found = True
                        console.print(json.dumps(r, indent=2))
                        break
        if not found:
            console.print(f"[red]Run ID {run_id} not found.[/red]")
        return

    # Overview table
    total_listings = 0
    if collector.listings_file.exists():
        with open(collector.listings_file, "r", encoding="utf-8") as f:
            total_listings = sum(1 for line in f if line.strip())

    total_media = 0
    manifest = collector.media_dir / "olx_media_manifest.jsonl"
    if manifest.exists():
        with open(manifest, "r", encoding="utf-8") as f:
            total_media = sum(1 for line in f if line.strip())

    table = Table(title="TrustLens OLX Pilot Acquisition Status", show_header=True)
    table.add_column("Repository Metric", style="cyan")
    table.add_column("Count", style="bold green")

    table.add_row("Total Normalized Listings", str(total_listings))
    table.add_row("Total Downloaded Media Assets", str(total_media))
    table.add_row("Data Directory", str(collector.base_dir))
    console.print(table)


@olx_app.command("serve")
def serve_cmd(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Bind host address"),
    port: int = typer.Option(8765, "--port", "-p", help="Port number"),
):
    """Start local ingestion daemon for browser extension."""
    console.print(f"[bold green]Starting TrustLens Ingestion Daemon on http://{host}:{port}...[/bold green]")
    start_server(host=host, port=port, block=True)
