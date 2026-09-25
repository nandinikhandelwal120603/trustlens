"""Typer CLI commands for TrustLens Marketplace Media Intelligence."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from trustlens.marketplace.cluster import RelationalClusterManager
from trustlens.marketplace.evidence import EvidenceRelationshipManager
from trustlens.marketplace.ingestion import MarketplaceIngestionEngine
from trustlens.marketplace.models import SimilarityThresholds
from trustlens.storage.database import SessionLocal, init_db
from trustlens.storage.orm_models import ListingORM

marketplace_app = typer.Typer(
    name="marketplace",
    help="Marketplace Media Intelligence & Local Observation Index",
    add_completion=False,
)
console = Console()


@marketplace_app.command("ingest")
def ingest_capture(
    file: Path = typer.Option(..., "--file", "-f", help="Path to capture-olx exported JSON file"),
    download_media: bool = typer.Option(
        False, "--download-media", help="Download and compute fingerprints for remote image URLs"
    ),
    phash_max: int = typer.Option(8, "--phash-max", help="Maximum pHash Hamming distance for candidate matches"),
    dhash_max: int = typer.Option(10, "--dhash-max", help="Maximum dHash Hamming distance for candidate matches"),
    ahash_max: int = typer.Option(10, "--ahash-max", help="Maximum aHash Hamming distance for candidate matches"),
):
    """Ingest an OLX capture JSON file into the local marketplace observation index."""
    if not file.exists():
        console.print(f"[red]Error: File not found: {file}[/red]")
        raise typer.Exit(code=1)

    init_db()
    console.print(f"[cyan]Ingesting marketplace capture from {file}...[/cyan]")

    thresholds = SimilarityThresholds(
        phash_max_distance=phash_max,
        dhash_max_distance=dhash_max,
        ahash_max_distance=ahash_max,
    )

    engine = MarketplaceIngestionEngine(
        thresholds=thresholds,
        download_media=download_media,
    )

    try:
        report = engine.ingest_file(file)

        # Output Summary Table
        table = Table(title="TrustLens Marketplace Ingestion Summary", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="dim")
        table.add_column("Count / Value", style="bold green")

        table.add_row("Capture ID", report.capture_id)
        table.add_row("Search Query", report.search_query or "(None / Listing)")
        table.add_row("Listings Observed", str(report.listings_observed))
        table.add_row("New Listings", str(report.new_listings))
        table.add_row("Existing Listings Updated", str(report.existing_listings_updated))
        table.add_row("Images Observed", str(report.images_observed))
        table.add_row("Images Fingerprinted", str(report.images_fingerprinted))
        table.add_row("Exact Image Matches (SHA-256)", str(report.exact_image_matches))
        table.add_row("Perceptual Image Matches", str(report.perceptual_candidate_matches))
        table.add_row("Image Clusters Updated", str(report.clusters_updated))
        table.add_row("Exact Title Reuse", str(report.exact_title_reuse_count))
        table.add_row("Similar Title Candidates", str(report.similar_title_count))
        table.add_row("Evidence Relationships Recorded", str(report.relationships_recorded))

        console.print(table)

        # Output Detailed Match Reports if matches were found
        if report.detailed_matches:
            console.print("\n[bold yellow]Observable Media Matches Found:[/bold yellow]")
            for m in report.detailed_matches[:5]:
                match_text = (
                    f"[bold]Match ID:[/bold] {m['match_id']}\n"
                    f"[bold]New Listing:[/bold] {m['listing_a']}\n"
                    f"[bold]Previously Observed Listing:[/bold] {m['listing_b']}\n"
                    f"[bold]Match Type:[/bold] {m['match_type']}\n"
                    f"[bold]pHash Distance:[/bold] {m['phash_distance']} | [bold]dHash Distance:[/bold] {m['dhash_distance']}\n"
                    f"[bold]Assigned Cluster:[/bold] {m['cluster_id']}\n"
                    f"[bold]Status:[/bold] UNVERIFIED (Candidate Match)"
                )
                console.print(Panel(match_text, title="Media Match", border_style="yellow"))

        console.print("\n[dim]Note: No fraud classification performed. All relationships remain unverified candidate matches.[/dim]\n")

    finally:
        engine.close()


@marketplace_app.command("clusters")
def list_clusters():
    """List all relational media clusters in the marketplace index."""
    init_db()
    with SessionLocal() as session:
        mgr = RelationalClusterManager(session)
        clusters = mgr.get_all_clusters()

        if not clusters:
            console.print("[yellow]No media clusters found in index.[/yellow]")
            return

        table = Table(title="Marketplace Media Clusters", show_header=True, header_style="bold cyan")
        table.add_column("Cluster ID", style="bold")
        table.add_column("Members Count")
        table.add_column("Member Listings")
        table.add_column("First Seen")
        table.add_column("Last Seen")
        table.add_column("Status")

        for c in clusters:
            listings = ", ".join(sorted(set(m.listing_id for m in c.members)))
            table.add_row(
                c.cluster_id,
                str(len(c.members)),
                listings[:50] + ("..." if len(listings) > 50 else ""),
                c.created_at.strftime("%Y-%m-%d %H:%M"),
                c.updated_at.strftime("%Y-%m-%d %H:%M"),
                c.verification_status.value,
            )

        console.print(table)


@marketplace_app.command("report")
def listing_report(
    listing: str = typer.Option(..., "--listing", "-l", help="Canonical listing ID (e.g. OLX-1856328590)")
):
    """View observation history, media clusters, and evidence relationships for a listing."""
    init_db()
    with SessionLocal() as session:
        listing_orm = session.get(ListingORM, listing)
        if not listing_orm:
            console.print(f"[red]Listing not found in index: {listing}[/red]")
            raise typer.Exit(code=1)

        evidence_mgr = EvidenceRelationshipManager(session)
        relationships = evidence_mgr.get_relationships_for_listing(listing)

        console.print(f"\n[bold cyan]Marketplace Report for {listing}[/bold cyan]")
        console.print(f"[bold]Title:[/bold] {listing_orm.raw_title}")
        console.print(f"[bold]Price:[/bold] ₹{listing_orm.raw_price:,.0f}" if listing_orm.raw_price else "[bold]Price:[/bold] None")
        console.print(f"[bold]Location:[/bold] {listing_orm.location_raw or 'Unknown'}")
        console.print(f"[bold]First Collected:[/bold] {listing_orm.collected_at}")

        if not relationships:
            console.print("\n[dim]No asset or text relationships observed for this listing yet.[/dim]\n")
            return

        table = Table(title="Observed Relationships", show_header=True, header_style="bold yellow")
        table.add_column("Relationship ID")
        table.add_column("Related Listing")
        table.add_column("Relationship Type")
        table.add_column("Evidence Summary")
        table.add_column("Verification Status")

        for r in relationships:
            other_listing = r.listing_b if r.listing_a == listing else r.listing_a
            table.add_row(
                r.relationship_id,
                other_listing,
                r.relationship_type.value,
                str(r.evidence_data)[:60],
                r.verification_status.value,
            )

        console.print(table)
        console.print("\n[dim]All relationships are unverified observable links.[/dim]\n")
