"""TrustLens CLI application powered by Typer and Rich."""

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from trustlens.cli.marketplace_cli import marketplace_app
from trustlens.cli.olx_cli import olx_app
from trustlens.config.settings import settings
from trustlens.connectors.crawl4ai_adapter import Crawl4AIWebExtractor
from trustlens.connectors.user_submission import UserSubmissionConnector
from trustlens.ingestion.pipeline import IngestionPipeline
from trustlens.ingestion.validators import ListingValidator
from trustlens.storage.database import SessionLocal, init_db
from trustlens.storage.repository import Repository

app = typer.Typer(
    name="trustlens",
    help="TrustLens — Marketplace Fraud Intelligence Data Ingestion Foundation",
    add_completion=False,
)
app.add_typer(olx_app, name="olx")
app.add_typer(marketplace_app, name="marketplace")
console = Console()


@app.callback()
def main_callback():
    """Ensure database and directories are initialized on CLI execution."""
    settings.ensure_directories()
    init_db()


@app.command("ingest")
def ingest_cmd(
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Path to JSON listing(s) file"),
    csv_file: Optional[Path] = typer.Option(None, "--csv", "-c", help="Path to CSV listings file"),
    url: Optional[str] = typer.Option(None, "--url", "-u", help="Permitted web URL to ingest"),
    download_media: bool = typer.Option(
        False, "--download-media", help="Download and hash remote media assets"
    ),
):
    """Ingest marketplace listings from a JSON file, CSV file, or permitted URL."""
    if not file and not csv_file and not url:
        console.print("[red]Error: You must specify --file, --csv, or --url to ingest.[/red]")
        raise typer.Exit(code=1)

    target_path = file or csv_file
    connector = UserSubmissionConnector()
    listings = []
    raw_records = []

    if target_path:
        if not target_path.exists():
            console.print(f"[red]Error: File not found: {target_path}[/red]")
            raise typer.Exit(code=1)

        console.print(f"[cyan]Reading records from {target_path}...[/cyan]")

        if target_path.suffix.lower() == ".csv":
            # Collect from CSV
            async def load_csv():
                async for item in connector.from_csv(target_path):
                    listings.append(item)

            asyncio.run(load_csv())
        else:
            with open(target_path, "r", encoding="utf-8") as f:
                content = json.load(f)
            records = content if isinstance(content, list) else [content]
            raw_records = records
            for r in records:
                listings.append(connector.dict_to_canonical(r))

    elif url:
        console.print(f"[cyan]Extracting permitted web page from {url}...[/cyan]")
        extractor = Crawl4AIWebExtractor()
        raw_page = asyncio.run(extractor.extract(url))

        # Build listing from page
        rec = {
            "source": "web_url",
            "source_url": url,
            "title": raw_page.title or "Web Listing",
            "description": raw_page.text[:2000],
            "category": "Electronics",
            "price": None,
        }
        raw_records = [rec]
        listings.append(connector.dict_to_canonical(rec, default_source="web_url"))

    if not listings:
        console.print("[yellow]No listings were loaded to ingest.[/yellow]")
        return

    # Ingest through pipeline
    with SessionLocal() as session:
        pipeline = IngestionPipeline(session=session)
        result = pipeline.ingest_batch(listings, raw_records=raw_records)

    # Display summary panel
    table = Table(title="Ingestion Run Summary", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold green")

    table.add_row("Total Received", str(result.total_received))
    table.add_row("Successfully Persisted", str(result.persisted_count))
    table.add_row("Duplicates Detected", str(result.duplicates_detected))
    table.add_row("Invalid Records", str(result.invalid_count))

    console.print(table)
    console.print(
        f"[green]✓ Successfully ingested {result.persisted_count} of {result.total_received} records.[/green]"
    )


@app.command("validate")
def validate_cmd(
    file: Path = typer.Option(..., "--file", "-f", help="Path to JSON or CSV file to validate"),
):
    """Validate listings without committing them to the database."""
    if not file.exists():
        console.print(f"[red]Error: File not found: {file}[/red]")
        raise typer.Exit(code=1)

    connector = UserSubmissionConnector()
    items = []

    if file.suffix.lower() == ".csv":

        async def load_csv():
            async for item in connector.from_csv(file):
                items.append(item)

        asyncio.run(load_csv())
    else:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        records = data if isinstance(data, list) else [data]
        for r in records:
            items.append(connector.dict_to_canonical(r))

    table = Table(title=f"Validation Results for {file.name}", show_header=True)
    table.add_column("Index", style="dim")
    table.add_column("Title", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Errors", style="red")

    all_valid = True
    for idx, item in enumerate(items, 1):
        valid, errors = ListingValidator.validate_canonical(item)
        if not valid:
            all_valid = False
            table.add_row(str(idx), item.raw_title[:35], "[red]INVALID[/red]", ", ".join(errors))
        else:
            table.add_row(str(idx), item.raw_title[:35], "[green]VALID[/green]", "-")

    console.print(table)
    if all_valid:
        console.print(f"[green]✓ All {len(items)} records passed validation![/green]")
    else:
        console.print("[yellow]Some records have validation issues shown above.[/yellow]")


@app.command("normalize")
def normalize_cmd(
    file: Path = typer.Option(
        ..., "--file", "-f", help="Path to JSON file to inspect normalization"
    ),
    limit: int = typer.Option(5, "--limit", "-n", help="Number of records to preview"),
):
    """Preview normalization transformations on input data."""
    if not file.exists():
        console.print(f"[red]Error: File not found: {file}[/red]")
        raise typer.Exit(code=1)

    connector = UserSubmissionConnector()
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = data if isinstance(data, list) else [data]

    table = Table(
        title=f"Normalization Preview (Showing first {min(limit, len(records))})", show_header=True
    )
    table.add_column("Raw Title / Price / Cond", style="yellow")
    table.add_column("Normalized Title / Price / Cond", style="green")
    table.add_column("Category & Subcategory", style="cyan")

    for r in records[:limit]:
        item = connector.dict_to_canonical(r)
        raw_info = (
            f"Title: {item.raw_title[:30]}...\nPrice: {r.get('price')}\nCond: {r.get('condition')}"
        )
        norm_info = (
            f"Title: {(item.normalized_title or '')[:30]}...\n"
            f"Price: {item.normalized_price} {item.normalized_currency}\n"
            f"Cond: {item.condition.value}"
        )
        cat_info = f"Category: {item.category}\nSubcategory: {item.subcategory}"
        table.add_row(raw_info, norm_info, cat_info)

    console.print(table)


@app.command("stats")
def stats_cmd():
    """Display comprehensive TrustLens marketplace data ingestion statistics."""
    with SessionLocal() as session:
        repo = Repository(session)
        db_stats = repo.get_stats()

    # Read validation error count from data/raw/validation_errors.jsonl
    val_error_count = 0
    val_err_file = settings.raw_data_dir / "validation_errors.jsonl"
    if val_err_file.exists():
        with open(val_err_file, "r", encoding="utf-8") as f:
            val_error_count = sum(1 for line in f if line.strip())

    table = Table(
        title="TrustLens Marketplace Intelligence — Database Statistics",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Metric", style="cyan", width=35)
    table.add_column("Count / Breakdown", style="bold green")

    table.add_row("Total Listings Ingested", str(db_stats["total_listings"]))
    table.add_row("Synthetic Listings", str(db_stats["synthetic_listings"]))

    # Categories breakdown
    cat_str = (
        "\n".join([f"• {k}: {v}" for k, v in db_stats["by_category"].items()])
        if db_stats["by_category"]
        else "[dim]None[/dim]"
    )
    table.add_row("Listings by Category", cat_str)

    # Sources breakdown
    src_str = (
        "\n".join([f"• {k}: {v}" for k, v in db_stats["by_source"].items()])
        if db_stats["by_source"]
        else "[dim]None[/dim]"
    )
    table.add_row("Listings by Source", src_str)

    table.add_row("Listings with Images", str(db_stats["listings_with_images"]))
    table.add_row("Listings with Videos", str(db_stats["listings_with_videos"]))
    table.add_row("Missing Descriptions", str(db_stats["missing_descriptions"]))
    table.add_row("Missing Prices", str(db_stats["missing_prices"]))
    table.add_row("Duplicate Listings Detected", str(db_stats["duplicate_count"]))
    table.add_row("Logged Validation Errors", str(val_error_count))

    console.print(table)


@app.command("collect-media")
def collect_media_cmd(
    input_file: Path = typer.Option(
        ...,
        "--input",
        "-i",
        help="Path to raw Reddit posts JSON export",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output_dir: Path = typer.Option(
        Path("./trustlens_reddit_multimodal_dataset"),
        "--output",
        "-o",
        help="Destination directory for case-mapped media dataset",
    ),
    concurrency: int = typer.Option(
        5,
        "--concurrency",
        "-c",
        help="Maximum concurrent downloads",
    ),
    timeout: int = typer.Option(
        20,
        "--timeout",
        "-t",
        help="HTTP timeout in seconds",
    ),
    zip_output: bool = typer.Option(
        True,
        "--zip/--no-zip",
        help="Create a final ZIP archive of the dataset package",
    ),
):
    """Download Reddit post media assets, build case mappings, validate, and package into a ZIP."""
    from trustlens.media.media_packager import run_media_collection

    res = run_media_collection(
        input_file=input_file,
        output_dir=output_dir,
        concurrency=concurrency,
        timeout=timeout,
        create_zip=zip_output,
    )
    if not res.is_valid:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
