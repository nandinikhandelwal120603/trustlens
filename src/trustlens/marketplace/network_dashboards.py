"""TrustLens Phase H — Interactive Network & Relationship Dashboards.

Generates 4 self-contained HTML dashboards:
1. `image_reuse_network.html`: Media reuse, pHash candidates, and DINO visual similarity.
2. `text_similarity_network.html`: Exact title reuse, lexical overlap, and shared OCR phrases.
3. `geographic_relationship_map.html`: Descriptive cross-city and cross-state corridor analysis.
4. `relationship_graph.html`: Master interactive graph with component selector, listing search, and inspector.
"""

from collections import Counter, defaultdict
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger("trustlens.network_dashboards")


class NetworkDashboardGenerator:
    """Generates production-grade, interactive HTML forensic dashboards."""

    def __init__(
        self,
        output_dir: Path = Path("data/olx_analysis/reports"),
        root_dir: Path = Path("."),
    ):
        self.output_dir = Path(output_dir)
        self.root_dir = Path(root_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Dict[str, Any]],
        components: List[Dict[str, Any]],
        features_df: pd.DataFrame,
        multi_signal: List[Dict[str, Any]],
    ) -> Dict[str, Path]:
        """Generates all 4 HTML dashboards and copies them to root."""
        logger.info("Generating Phase H interactive dashboards...")
        results = {}

        # 1. Image Reuse Network
        p1 = self.generate_image_reuse_dashboard(nodes, edges, components)
        results["image_reuse_network"] = p1

        # 2. Text Similarity Network
        p2 = self.generate_text_similarity_dashboard(nodes, edges, components)
        results["text_similarity_network"] = p2

        # 3. Geographic Relationship Map
        p3 = self.generate_geographic_map_dashboard(nodes, edges)
        results["geographic_relationship_map"] = p3

        # 4. Master Relationship Graph
        p4 = self.generate_master_graph_dashboard(nodes, edges, components, multi_signal)
        results["relationship_graph"] = p4

        logger.info("All 4 Phase H interactive dashboards generated successfully.")
        return results

    def _write_and_sync(self, filename: str, html_content: str) -> Path:
        """Writes to reports dir and syncs to repo root."""
        out_path = self.output_dir / filename
        out_path.write_text(html_content, encoding="utf-8")
        
        # Also sync to root for top-level accessibility
        root_path = self.root_dir / filename
        root_path.write_text(html_content, encoding="utf-8")
        logger.info("Wrote %s (and synced to %s)", out_path, root_path)
        return out_path

    # =========================================================================
    # 1. IMAGE REUSE NETWORK
    # =========================================================================
    def generate_image_reuse_dashboard(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Dict[str, Any]],
        components: List[Dict[str, Any]],
    ) -> Path:
        """Generates image_reuse_network.html answering the 8 media reuse forensic questions."""
        img_edges = [
            e for e in edges
            if e["relationship_type"] in (
                "MEDIA_EXACT_REUSE",
                "MEDIA_PERCEPTUAL_REUSE_CANDIDATE",
                "MEDIA_VISUAL_SIMILARITY_CANDIDATE",
            )
        ]

        exact_edges = [e for e in img_edges if e["relationship_type"] == "MEDIA_EXACT_REUSE"]
        percept_edges = [e for e in img_edges if e["relationship_type"] == "MEDIA_PERCEPTUAL_REUSE_CANDIDATE"]
        visual_edges = [e for e in img_edges if e["relationship_type"] == "MEDIA_VISUAL_SIMILARITY_CANDIDATE"]

        # Questions to answer
        total_multi_listing_images = len(set(e["source_node_id"] for e in exact_edges + percept_edges))
        listings_sharing_exact = len(set(e["listing_a_id"] for e in exact_edges).union(set(e["listing_b_id"] for e in exact_edges)))
        listings_sharing_phash = len(set(e["listing_a_id"] for e in percept_edges).union(set(e["listing_b_id"] for e in percept_edges)))
        listings_sharing_visual = len(set(e["listing_a_id"] for e in visual_edges).union(set(e["listing_b_id"] for e in visual_edges)))
        
        cross_city_img = sum(1 for e in img_edges if e.get("cross_city"))
        cross_state_img = sum(1 for e in img_edges if e.get("cross_state"))
        cross_prod_img = sum(1 for e in img_edges if e.get("cross_product"))

        # Representative media reuse pairs for table (all exact + all perceptual + sample of visual)
        display_pairs = []
        for e in exact_edges + percept_edges + visual_edges[:150]:
            display_pairs.append({
                "edge_id": e["edge_id"],
                "type": e["relationship_type"],
                "score": e["score"],
                "score_type": e["score_type"],
                "listing_a": e.get("listing_a_id"),
                "listing_b": e.get("listing_b_id"),
                "city_a": e.get("city_a") or "Unknown",
                "city_b": e.get("city_b") or "Unknown",
                "state_a": e.get("state_a") or "Unknown",
                "state_b": e.get("state_b") or "Unknown",
                "product_a": e.get("product_a") or "Unknown",
                "product_b": e.get("product_b") or "Unknown",
                "cross_city": bool(e.get("cross_city")),
                "cross_state": bool(e.get("cross_state")),
                "cross_product": bool(e.get("cross_product")),
                "evidence_source": e.get("evidence_source"),
            })

        pairs_json = json.dumps(display_pairs)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrustLens — Image Reuse & Visual Similarity Forensic Network</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0B0F19;
            --surface-color: #111827;
            --surface-card: #1E293B;
            --border-color: #334155;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --primary: #3B82F6;
            --exact-color: #7C3AED;
            --percept-color: #10B981;
            --visual-color: #3B82F6;
            --accent-amber: #F59E0B;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', sans-serif;
            padding: 30px 40px;
            line-height: 1.5;
        }}
        header {{
            margin-bottom: 24px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
        }}
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}
        h1 {{
            font-size: 26px;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .badge-brand {{
            background: linear-gradient(135deg, #7C3AED, #3B82F6);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .guardrail-alert {{
            background: rgba(59, 130, 246, 0.08);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 8px;
            padding: 12px 16px;
            margin: 16px 0;
            font-size: 13px;
            color: #93C5FD;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: var(--surface-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-main);
        }}
        .stat-label {{
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 600;
            margin-top: 4px;
        }}
        .filters-bar {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin: 20px 0;
            background: var(--surface-color);
            padding: 14px;
            border-radius: 10px;
            border: 1px solid var(--border-color);
        }}
        .filter-btn {{
            background: var(--surface-card);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 8px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .filter-btn:hover, .filter-btn.active {{
            background: var(--primary);
            color: #FFFFFF;
            border-color: var(--primary);
        }}
        .search-box {{
            flex: 1;
            min-width: 250px;
            background: var(--surface-card);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 8px 14px;
            color: var(--text-main);
            font-size: 13px;
            font-family: inherit;
        }}
        .search-box:focus {{
            outline: none;
            border-color: var(--primary);
        }}
        .table-container {{
            background: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow-x: auto;
            margin-top: 16px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
        }}
        th {{
            background: var(--surface-card);
            padding: 12px 16px;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--border-color);
        }}
        td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
        }}
        tr:hover td {{
            background: rgba(255, 255, 255, 0.02);
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
        }}
        .badge-exact {{ background: rgba(124, 58, 237, 0.2); color: #C4B5FD; border: 1px solid rgba(124, 58, 237, 0.4); }}
        .badge-percept {{ background: rgba(16, 185, 129, 0.2); color: #6EE7B7; border: 1px solid rgba(16, 185, 129, 0.4); }}
        .badge-visual {{ background: rgba(59, 130, 246, 0.2); color: #93C5FD; border: 1px solid rgba(59, 130, 246, 0.4); }}
        .tag-cross {{
            background: rgba(245, 158, 11, 0.15);
            color: #FCD34D;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-top">
            <h1>
                <span>TrustLens</span>
                <span class="badge-brand">Phase H Media Network</span>
            </h1>
            <span style="font-size: 12px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;">
                Generated: 2026-09-24 | Canonical Pipeline
            </span>
        </div>
        <p style="color: var(--text-muted); font-size: 14px; margin-top: 6px;">
            Specialized Forensic Network Analysis for Media Reuse, Perceptual Hashes & Visual Similarity
        </p>
        <div class="guardrail-alert">
            <strong>Forensic Guardrail:</strong> Media reuse establishes identical or visually similar binary assets across listings. It does NOT assert common seller ownership, fraudulent intent, or stolen media. Legitimate syndication, stock product photos, and retailer cross-posting also generate media reuse.
        </div>
    </header>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" style="color: #C4B5FD;">{len(exact_edges):,}</div>
            <div class="stat-label">Exact Image Reuse Edges (SHA-256)</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #6EE7B7;">{len(percept_edges):,}</div>
            <div class="stat-label">Perceptual Reuse Edges (pHash &le; 8)</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #93C5FD;">{len(visual_edges):,}</div>
            <div class="stat-label">Visual Similarity Edges (DINO &ge; 0.70)</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #FCD34D;">{cross_city_img:,}</div>
            <div class="stat-label">Cross-City Media Edges</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #F472B6;">{cross_state_img:,}</div>
            <div class="stat-label">Cross-State Media Edges</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #38BDF8;">{cross_prod_img:,}</div>
            <div class="stat-label">Cross-Product Family Edges</div>
        </div>
    </div>

    <div class="filters-bar">
        <button class="filter-btn active" onclick="setFilter('ALL')">All Media Relationships</button>
        <button class="filter-btn" onclick="setFilter('EXACT')">Exact Binary Reuse ({len(exact_edges)})</button>
        <button class="filter-btn" onclick="setFilter('PERCEPT')">Perceptual Reuse ({len(percept_edges)})</button>
        <button class="filter-btn" onclick="setFilter('VISUAL')">Visual Similarity ({len(visual_edges):,})</button>
        <button class="filter-btn" onclick="setFilter('CROSS_CITY')">Cross-City Corridors</button>
        <input type="text" id="searchInput" class="search-box" placeholder="Search listing ID, city, or product..." onkeyup="renderTable()">
    </div>

    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Relationship ID / Type</th>
                    <th>Metric / Score</th>
                    <th>Listing A (City | Product)</th>
                    <th>Listing B (City | Product)</th>
                    <th>Jurisdiction Spans</th>
                    <th>Evidence Source</th>
                </tr>
            </thead>
            <tbody id="pairsTableBody">
            </tbody>
        </table>
    </div>

    <script>
        const pairsData = {pairs_json};
        let currentFilter = 'ALL';

        function setFilter(f) {{
            currentFilter = f;
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            renderTable();
        }}

        function renderTable() {{
            const search = document.getElementById('searchInput').value.toLowerCase();
            const tbody = document.getElementById('pairsTableBody');
            tbody.innerHTML = '';

            const filtered = pairsData.filter(p => {{
                if (currentFilter === 'EXACT' && p.type !== 'MEDIA_EXACT_REUSE') return false;
                if (currentFilter === 'PERCEPT' && p.type !== 'MEDIA_PERCEPTUAL_REUSE_CANDIDATE') return false;
                if (currentFilter === 'VISUAL' && p.type !== 'MEDIA_VISUAL_SIMILARITY_CANDIDATE') return false;
                if (currentFilter === 'CROSS_CITY' && !p.cross_city) return false;

                if (search) {{
                    const s = (p.listing_a + ' ' + p.listing_b + ' ' + p.city_a + ' ' + p.city_b + ' ' + p.product_a + ' ' + p.product_b).toLowerCase();
                    if (!s.includes(search)) return false;
                }}
                return true;
            }});

            filtered.slice(0, 150).forEach(p => {{
                const tr = document.createElement('tr');
                let badgeClass = 'badge-visual';
                if (p.type === 'MEDIA_EXACT_REUSE') badgeClass = 'badge-exact';
                else if (p.type === 'MEDIA_PERCEPTUAL_REUSE_CANDIDATE') badgeClass = 'badge-percept';

                let crossTags = '';
                if (p.cross_city) crossTags += '<span class="tag-cross">Cross-City</span> ';
                if (p.cross_state) crossTags += '<span class="tag-cross">Cross-State</span> ';
                if (p.cross_product) crossTags += '<span class="tag-cross">Cross-Product</span>';

                tr.innerHTML = `
                    <td>
                        <span class="badge ${{badgeClass}}">${{p.type}}</span>
                        <div style="font-size: 11px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; margin-top: 4px;">${{p.edge_id}}</div>
                    </td>
                    <td style="font-family: 'JetBrains Mono', monospace;">
                        <strong>${{p.score}}</strong>
                        <div style="font-size: 10px; color: var(--text-muted);">${{p.score_type}}</div>
                    </td>
                    <td>
                        <strong>${{p.listing_a}}</strong>
                        <div style="font-size: 11px; color: var(--text-muted);">${{p.city_a}}, ${{p.state_a}}</div>
                        <div style="font-size: 11px; color: #93C5FD;">${{p.product_a}}</div>
                    </td>
                    <td>
                        <strong>${{p.listing_b}}</strong>
                        <div style="font-size: 11px; color: var(--text-muted);">${{p.city_b}}, ${{p.state_b}}</div>
                        <div style="font-size: 11px; color: #93C5FD;">${{p.product_b}}</div>
                    </td>
                    <td>${{crossTags || '<span style="color: var(--text-muted); font-size: 11px;">Intra-Market</span>'}}</td>
                    <td style="font-size: 11px; font-family: 'JetBrains Mono', monospace; color: var(--text-muted);">${{p.evidence_source}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // Initial Render
        renderTable();
    </script>
</body>
</html>
"""
        return self._write_and_sync("image_reuse_network.html", html)

    # =========================================================================
    # 2. TEXT SIMILARITY NETWORK
    # =========================================================================
    def generate_text_similarity_dashboard(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Dict[str, Any]],
        components: List[Dict[str, Any]],
    ) -> Path:
        """Generates text_similarity_network.html displaying exact title reuse, lexical overlap, and OCR phrases."""
        text_edges = [
            e for e in edges
            if e["relationship_type"] in (
                "LISTING_TEXT_EXACT_REUSE",
                "LISTING_TEXT_SIMILARITY_CANDIDATE",
                "LISTING_SHARED_OCR_PHRASE",
            )
        ]

        exact_titles = [e for e in text_edges if e["relationship_type"] == "LISTING_TEXT_EXACT_REUSE"]
        lexical_sim = [e for e in text_edges if e["relationship_type"] == "LISTING_TEXT_SIMILARITY_CANDIDATE"]
        ocr_phrases = [e for e in text_edges if e["relationship_type"] == "LISTING_SHARED_OCR_PHRASE"]

        cross_city_text = sum(1 for e in text_edges if e.get("cross_city"))
        cross_state_text = sum(1 for e in text_edges if e.get("cross_state"))

        display_text = []
        for e in exact_titles[:150] + lexical_sim[:100] + ocr_phrases:
            l1, l2 = e.get("listing_a_id"), e.get("listing_b_id")
            node1 = nodes.get(f"listing:{l1}", {})
            node2 = nodes.get(f"listing:{l2}", {})
            display_text.append({
                "edge_id": e["edge_id"],
                "type": e["relationship_type"],
                "score": e["score"],
                "listing_a": l1,
                "listing_b": l2,
                "title_a": node1.get("title", ""),
                "title_b": node2.get("title", ""),
                "city_a": e.get("city_a") or "Unknown",
                "city_b": e.get("city_b") or "Unknown",
                "product_a": e.get("product_a") or "Unknown",
                "product_b": e.get("product_b") or "Unknown",
                "cross_city": bool(e.get("cross_city")),
                "cross_state": bool(e.get("cross_state")),
                "evidence_id": e.get("evidence_id"),
            })

        text_json = json.dumps(display_text)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrustLens — Text Similarity & Language Reuse Forensic Network</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0B0F19;
            --surface-color: #111827;
            --surface-card: #1E293B;
            --border-color: #334155;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --primary: #EC4899;
            --exact-color: #EC4899;
            --lexical-color: #F59E0B;
            --ocr-color: #10B981;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', sans-serif;
            padding: 30px 40px;
            line-height: 1.5;
        }}
        header {{
            margin-bottom: 24px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
        }}
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}
        h1 {{
            font-size: 26px;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .badge-brand {{
            background: linear-gradient(135deg, #EC4899, #8B5CF6);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: var(--surface-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
        }}
        .stat-label {{
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 600;
            margin-top: 4px;
        }}
        .filters-bar {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin: 20px 0;
            background: var(--surface-color);
            padding: 14px;
            border-radius: 10px;
            border: 1px solid var(--border-color);
        }}
        .filter-btn {{
            background: var(--surface-card);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 8px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .filter-btn:hover, .filter-btn.active {{
            background: var(--primary);
            color: #FFFFFF;
            border-color: var(--primary);
        }}
        .search-box {{
            flex: 1;
            min-width: 250px;
            background: var(--surface-card);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 8px 14px;
            color: var(--text-main);
            font-size: 13px;
            font-family: inherit;
        }}
        .cards-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-top: 16px;
        }}
        .text-card {{
            background: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 16px;
            transition: border-color 0.2s;
        }}
        .text-card:hover {{
            border-color: #64748B;
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        .titles-comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            background: var(--surface-card);
            padding: 12px;
            border-radius: 8px;
            font-size: 13px;
        }}
        .title-block h4 {{
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            margin-bottom: 4px;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
        }}
        .badge-exact {{ background: rgba(236, 72, 153, 0.2); color: #F472B6; border: 1px solid rgba(236, 72, 153, 0.4); }}
        .badge-lexical {{ background: rgba(245, 158, 11, 0.2); color: #FCD34D; border: 1px solid rgba(245, 158, 11, 0.4); }}
        .badge-ocr {{ background: rgba(16, 185, 129, 0.2); color: #6EE7B7; border: 1px solid rgba(16, 185, 129, 0.4); }}
    </style>
</head>
<body>
    <header>
        <div class="header-top">
            <h1>
                <span>TrustLens</span>
                <span class="badge-brand">Phase H Text Network</span>
            </h1>
            <span style="font-size: 12px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;">
                Generated: 2026-09-24 | Canonical Pipeline
            </span>
        </div>
        <p style="color: var(--text-muted); font-size: 14px; margin-top: 6px;">
            Lexical Linguistics, Exact Normalized Title Reuse & Distinctive Shared OCR Phrase Network
        </p>
    </header>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" style="color: #F472B6;">{len(exact_titles):,}</div>
            <div class="stat-label">Exact Title Reuse Edges</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #FCD34D;">{len(lexical_sim):,}</div>
            <div class="stat-label">High Lexical Overlap Edges (Jaccard &ge; 0.75)</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #6EE7B7;">{len(ocr_phrases):,}</div>
            <div class="stat-label">Shared Distinctive OCR Phrase Edges</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #38BDF8;">{cross_city_text:,}</div>
            <div class="stat-label">Cross-City Text Edges</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #C084FC;">{cross_state_text:,}</div>
            <div class="stat-label">Cross-State Text Edges</div>
        </div>
    </div>

    <div class="filters-bar">
        <button class="filter-btn active" onclick="setFilter('ALL')">All Text Candidates</button>
        <button class="filter-btn" onclick="setFilter('EXACT')">Exact Title Reuse ({len(exact_titles):,})</button>
        <button class="filter-btn" onclick="setFilter('LEXICAL')">Lexical Overlap ({len(lexical_sim):,})</button>
        <button class="filter-btn" onclick="setFilter('OCR')">Shared OCR Phrases ({len(ocr_phrases)})</button>
        <button class="filter-btn" onclick="setFilter('CROSS_CITY')">Cross-City Only</button>
        <input type="text" id="searchInput" class="search-box" placeholder="Search title text, listing ID, or city..." onkeyup="renderCards()">
    </div>

    <div class="cards-list" id="cardsContainer">
    </div>

    <script>
        const textData = {text_json};
        let currentFilter = 'ALL';

        function setFilter(f) {{
            currentFilter = f;
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            renderCards();
        }}

        function renderCards() {{
            const search = document.getElementById('searchInput').value.toLowerCase();
            const container = document.getElementById('cardsContainer');
            container.innerHTML = '';

            const filtered = textData.filter(d => {{
                if (currentFilter === 'EXACT' && d.type !== 'LISTING_TEXT_EXACT_REUSE') return false;
                if (currentFilter === 'LEXICAL' && d.type !== 'LISTING_TEXT_SIMILARITY_CANDIDATE') return false;
                if (currentFilter === 'OCR' && d.type !== 'LISTING_SHARED_OCR_PHRASE') return false;
                if (currentFilter === 'CROSS_CITY' && !d.cross_city) return false;

                if (search) {{
                    const s = (d.listing_a + ' ' + d.listing_b + ' ' + d.title_a + ' ' + d.title_b + ' ' + d.city_a + ' ' + d.city_b).toLowerCase();
                    if (!s.includes(search)) return false;
                }}
                return true;
            }});

            filtered.slice(0, 100).forEach(d => {{
                let bClass = 'badge-lexical';
                if (d.type === 'LISTING_TEXT_EXACT_REUSE') bClass = 'badge-exact';
                else if (d.type === 'LISTING_SHARED_OCR_PHRASE') bClass = 'badge-ocr';

                const card = document.createElement('div');
                card.className = 'text-card';
                card.innerHTML = `
                    <div class="card-header">
                        <div>
                            <span class="badge ${{bClass}}">${{d.type}}</span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; margin-left: 10px; color: var(--text-muted);">${{d.edge_id}}</span>
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 13px;">
                            Score: <strong>${{d.score}}</strong>
                            ${{d.cross_city ? '<span style="color: #FCD34D; font-size: 11px; margin-left: 8px;">[Cross-City: ' + d.city_a + ' &harr; ' + d.city_b + ']</span>' : ''}}
                        </div>
                    </div>
                    <div class="titles-comparison">
                        <div class="title-block">
                            <h4>Listing ${{d.listing_a}} &bull; ${{d.city_a}} &bull; ${{d.product_a}}</h4>
                            <div style="font-weight: 600; color: #F8FAFC;">${{d.title_a || '—'}}</div>
                        </div>
                        <div class="title-block">
                            <h4>Listing ${{d.listing_b}} &bull; ${{d.city_b}} &bull; ${{d.product_b}}</h4>
                            <div style="font-weight: 600; color: #F8FAFC;">${{d.title_b || '—'}}</div>
                        </div>
                    </div>
                `;
                container.appendChild(card);
            }});
        }}

        // Initial render
        renderCards();
    </script>
</body>
</html>
"""
        return self._write_and_sync("text_similarity_network.html", html)

    # =========================================================================
    # 3. GEOGRAPHIC RELATIONSHIP MAP
    # =========================================================================
    def generate_geographic_map_dashboard(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Dict[str, Any]],
    ) -> Path:
        """Generates geographic_relationship_map.html showing cross-jurisdictional corridors."""
        obs_edges = [
            e for e in edges
            if e["relationship_type"] not in ("LISTING_IN_CITY", "LISTING_HAS_PRODUCT", "LISTING_HAS_MEDIA", "CITY_IN_STATE")
        ]

        cross_city_edges = [e for e in obs_edges if e.get("cross_city")]
        cross_state_edges = [e for e in obs_edges if e.get("cross_state")]

        # Group by City-City pairs
        city_corridors: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "city_a": "", "city_b": "", "state_a": "", "state_b": "",
            "total": 0, "exact_img": 0, "percept_img": 0, "visual_sim": 0, "text_exact": 0, "text_sim": 0, "ocr": 0
        })

        for e in cross_city_edges:
            c1, c2 = e.get("city_a"), e.get("city_b")
            if not c1 or not c2 or c1 == "Unknown" or c2 == "Unknown":
                continue
            pair_key = " <-> ".join(sorted([str(c1), str(c2)]))
            c_dict = city_corridors[pair_key]
            cities_sorted = sorted([(c1, e.get("state_a")), (c2, e.get("state_b"))], key=lambda x: x[0])
            c_dict["city_a"], c_dict["state_a"] = cities_sorted[0]
            c_dict["city_b"], c_dict["state_b"] = cities_sorted[1]
            c_dict["total"] += 1

            rtype = e["relationship_type"]
            if rtype == "MEDIA_EXACT_REUSE":
                c_dict["exact_img"] += 1
            elif rtype == "MEDIA_PERCEPTUAL_REUSE_CANDIDATE":
                c_dict["percept_img"] += 1
            elif rtype == "MEDIA_VISUAL_SIMILARITY_CANDIDATE":
                c_dict["visual_sim"] += 1
            elif rtype == "LISTING_TEXT_EXACT_REUSE":
                c_dict["text_exact"] += 1
            elif rtype == "LISTING_TEXT_SIMILARITY_CANDIDATE":
                c_dict["text_sim"] += 1
            elif rtype == "LISTING_SHARED_OCR_PHRASE":
                c_dict["ocr"] += 1

        corridors_list = list(city_corridors.values())
        corridors_list.sort(key=lambda x: x["total"], reverse=True)
        corridors_json = json.dumps(corridors_list)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrustLens — Geographic Relationship Corridor Analysis</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0B0F19;
            --surface-color: #111827;
            --surface-card: #1E293B;
            --border-color: #334155;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --primary: #F59E0B;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', sans-serif;
            padding: 30px 40px;
            line-height: 1.5;
        }}
        header {{
            margin-bottom: 24px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
        }}
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}
        h1 {{
            font-size: 26px;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .badge-brand {{
            background: linear-gradient(135deg, #F59E0B, #10B981);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .guardrail-alert {{
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 8px;
            padding: 12px 16px;
            margin: 16px 0;
            font-size: 13px;
            color: #FCD34D;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: var(--surface-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
        }}
        .stat-label {{
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 600;
            margin-top: 4px;
        }}
        .search-box {{
            width: 100%;
            background: var(--surface-card);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 10px 16px;
            color: var(--text-main);
            font-size: 14px;
            margin: 16px 0;
            font-family: inherit;
        }}
        .search-box:focus {{ outline: none; border-color: var(--primary); }}
        .table-container {{
            background: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
        }}
        th {{
            background: var(--surface-card);
            padding: 12px 16px;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            font-size: 11px;
            border-bottom: 1px solid var(--border-color);
        }}
        td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
        }}
        tr:hover td {{
            background: rgba(255, 255, 255, 0.02);
        }}
        .bar-pill {{
            display: inline-block;
            height: 6px;
            border-radius: 3px;
            background: #F59E0B;
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-top">
            <h1>
                <span>TrustLens</span>
                <span class="badge-brand">Phase H Geographic Map</span>
            </h1>
            <span style="font-size: 12px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace;">
                Generated: 2026-09-24 | Canonical Pipeline
            </span>
        </div>
        <p style="color: var(--text-muted); font-size: 14px; margin-top: 6px;">
            Descriptive Analysis of Observed Cross-City and Cross-State Relationship Corridors
        </p>
        <div class="guardrail-alert">
            <strong>Geographic Guardrail:</strong> This analysis visualizes observed relationship volumes between metropolitan centers. It is NOT a "scam map", high-risk state rating, or accusation index. Inter-city relationships frequently reflect nationwide electronics retailers, inter-city mobility, and e-commerce distribution networks.
        </div>
    </header>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" style="color: #FCD34D;">{len(cross_city_edges):,}</div>
            <div class="stat-label">Total Cross-City Relationship Edges</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #38BDF8;">{len(cross_state_edges):,}</div>
            <div class="stat-label">Total Cross-State Relationship Edges</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #10B981;">{len(city_corridors):,}</div>
            <div class="stat-label">Distinct Inter-City Corridors</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #C084FC;">{sum(c['exact_img'] + c['percept_img'] for c in corridors_list)}</div>
            <div class="stat-label">Cross-City Binary/Perceptual Image Reuses</div>
        </div>
    </div>

    <input type="text" id="searchInput" class="search-box" placeholder="Filter by city name or state (e.g., Delhi, Bengaluru, Mumbai)..." onkeyup="renderTable()">

    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Inter-City Corridor</th>
                    <th>State Jurisdictions</th>
                    <th>Total Observed Edges</th>
                    <th>Exact Media Reuse</th>
                    <th>Perceptual Candidates</th>
                    <th>Visual Sim Candidates</th>
                    <th>Exact Text Reuse</th>
                    <th>Lexical Similarity</th>
                    <th>Shared OCR</th>
                </tr>
            </thead>
            <tbody id="corridorsTableBody">
            </tbody>
        </table>
    </div>

    <script>
        const corridorsData = {corridors_json};

        function renderTable() {{
            const search = document.getElementById('searchInput').value.toLowerCase();
            const tbody = document.getElementById('corridorsTableBody');
            tbody.innerHTML = '';

            const filtered = corridorsData.filter(c => {{
                if (search) {{
                    const s = (c.city_a + ' ' + c.city_b + ' ' + c.state_a + ' ' + c.state_b).toLowerCase();
                    if (!s.includes(search)) return false;
                }}
                return true;
            }});

            const maxTotal = corridorsData.length > 0 ? corridorsData[0].total : 1;

            filtered.slice(0, 100).forEach(c => {{
                const tr = document.createElement('tr');
                const isCrossState = c.state_a !== c.state_b && c.state_a !== 'Unknown' && c.state_b !== 'Unknown';
                const barWidth = Math.max(4, Math.round((c.total / maxTotal) * 100));

                tr.innerHTML = `
                    <td>
                        <strong style="color: #F8FAFC;">${{c.city_a}} &harr; ${{c.city_b}}</strong>
                    </td>
                    <td>
                        <span style="color: var(--text-muted); font-size: 12px;">${{c.state_a}} &harr; ${{c.state_b}}</span>
                        ${{isCrossState ? '<span style="background: rgba(59, 130, 246, 0.2); color: #93C5FD; padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-left: 6px;">Inter-State</span>' : ''}}
                    </td>
                    <td style="font-family: 'JetBrains Mono', monospace; font-weight: bold; color: #FCD34D;">
                        ${{c.total.toLocaleString()}}
                        <div class="bar-pill" style="width: ${{barWidth}}px;"></div>
                    </td>
                    <td style="font-family: 'JetBrains Mono', monospace; color: #C4B5FD;">${{c.exact_img}}</td>
                    <td style="font-family: 'JetBrains Mono', monospace; color: #6EE7B7;">${{c.percept_img}}</td>
                    <td style="font-family: 'JetBrains Mono', monospace; color: #93C5FD;">${{c.visual_sim.toLocaleString()}}</td>
                    <td style="font-family: 'JetBrains Mono', monospace; color: #F472B6;">${{c.text_exact}}</td>
                    <td style="font-family: 'JetBrains Mono', monospace; color: #FCD34D;">${{c.text_sim}}</td>
                    <td style="font-family: 'JetBrains Mono', monospace; color: #34D399;">${{c.ocr}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // Initial render
        renderTable();
    </script>
</body>
</html>
"""
        return self._write_and_sync("geographic_relationship_map.html", html)

    # =========================================================================
    # 4. MASTER RELATIONSHIP GRAPH
    # =========================================================================
    def generate_master_graph_dashboard(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Dict[str, Any]],
        components: List[Dict[str, Any]],
        multi_signal: List[Dict[str, Any]],
    ) -> Path:
        """Generates relationship_graph.html master interactive Vis.js graph dashboard."""
        # Top 30 non-singleton components
        top_comps = [c for c in components if c["node_count"] > 1][:30]

        # Prepare component lookup
        comp_lookup: Dict[str, List[str]] = {}
        for c in top_comps:
            cid = c["component_id"]
            # Find listings in this component
            c_listings = [
                nid.split(":", 1)[1] for nid, nd in nodes.items()
                if nd["node_type"] == "LISTING" and nd.get("component_id") == cid
            ]
            comp_lookup[cid] = c_listings

        # Extract subgraphs for top 30 components
        comp_graphs_data: Dict[str, Dict[str, Any]] = {}
        for c in top_comps:
            cid = c["component_id"]
            member_listings = set(comp_lookup.get(cid, []))
            if not member_listings:
                continue

            # Gather nodes
            c_nodes = []
            for lid in member_listings:
                nd = nodes.get(f"listing:{lid}", {})
                c_nodes.append({
                    "id": f"listing:{lid}",
                    "label": f"{lid}\n{nd.get('model', '')[:14]}",
                    "group": "LISTING",
                    "title": f"<b>Listing {lid}</b><br>Title: {nd.get('title')}<br>Price: {nd.get('price')}<br>City: {nd.get('city')}, {nd.get('state')}<br>Model: {nd.get('model')}",
                    "city": nd.get("city"),
                    "state": nd.get("state"),
                    "product": nd.get("model"),
                    "product_family": nd.get("product_family"),
                })

            # Gather edges between these listings
            c_edges = []
            for e in edges:
                l1, l2 = e.get("listing_a_id"), e.get("listing_b_id")
                if l1 in member_listings and l2 in member_listings and l1 != l2:
                    rtype = e["relationship_type"]
                    color = "#3B82F6"
                    if "EXACT_REUSE" in rtype:
                        color = "#7C3AED"
                    elif "PERCEPTUAL" in rtype:
                        color = "#10B981"
                    elif "TEXT" in rtype:
                        color = "#EC4899"
                    elif "OCR" in rtype:
                        color = "#06B6D4"

                    c_edges.append({
                        "from": f"listing:{l1}",
                        "to": f"listing:{l2}",
                        "label": rtype.replace("MEDIA_", "").replace("LISTING_", ""),
                        "relationship_type": rtype,
                        "color": {"color": color},
                        "title": f"<b>{rtype}</b><br>Score: {e.get('score')}<br>Source: {e.get('evidence_source')}",
                        "evidence_id": e.get("evidence_id"),
                    })

            comp_graphs_data[cid] = {
                "nodes": c_nodes,
                "edges": c_edges,
                "meta": c,
            }

        graph_payload = json.dumps(comp_graphs_data)
        comps_meta_json = json.dumps(top_comps)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrustLens — Master Relationship Intelligence Graph</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        :root {{
            --bg-color: #0B0F19;
            --surface-color: #111827;
            --surface-card: #1E293B;
            --border-color: #334155;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --primary: #3B82F6;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', sans-serif;
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }}
        header {{
            background: var(--surface-color);
            border-bottom: 1px solid var(--border-color);
            padding: 16px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
        }}
        h1 {{
            font-size: 20px;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .badge-brand {{
            background: linear-gradient(135deg, #3B82F6, #7C3AED);
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .main-layout {{
            display: flex;
            flex: 1;
            overflow: hidden;
        }}
        .sidebar {{
            width: 340px;
            background: var(--surface-color);
            border-right: 1px solid var(--border-color);
            padding: 16px;
            overflow-y: auto;
            flex-shrink: 0;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .graph-area {{
            flex: 1;
            position: relative;
            background: #070A10;
        }}
        #networkContainer {{
            width: 100%;
            height: 100%;
        }}
        .inspector-panel {{
            width: 320px;
            background: var(--surface-color);
            border-left: 1px solid var(--border-color);
            padding: 16px;
            overflow-y: auto;
            flex-shrink: 0;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}
        .select-input, .text-input {{
            width: 100%;
            background: var(--surface-card);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 8px 12px;
            color: var(--text-main);
            font-size: 13px;
            font-family: inherit;
        }}
        .select-input:focus, .text-input:focus {{ outline: none; border-color: var(--primary); }}
        .section-label {{
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }}
        .stat-box {{
            background: var(--surface-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px;
        }}
        .stat-val {{
            font-size: 20px;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            color: #38BDF8;
        }}
        .stat-lbl {{
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            margin-top: 2px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            margin-bottom: 6px;
        }}
        .legend-color {{
            width: 12px;
            height: 12px;
            border-radius: 3px;
        }}
        .btn {{
            background: var(--primary);
            color: white;
            border: none;
            padding: 8px 14px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
        }}
        .btn:hover {{ opacity: 0.9; }}
    </style>
</head>
<body>
    <header>
        <h1>
            <span>TrustLens</span>
            <span class="badge-brand">Phase H Master Graph</span>
            <span style="font-size: 13px; font-weight: 500; color: var(--text-muted); margin-left: 10px;">
                Cross-Modal Relationship Intelligence
            </span>
        </h1>
        <div style="font-size: 12px; font-family: 'JetBrains Mono', monospace; color: var(--text-muted);">
            Nodes: {len(nodes):,} | Edges: {len(edges):,} | Non-Singleton Comps: {len([c for c in components if c['node_count'] > 1])}
        </div>
    </header>

    <div class="main-layout">
        <!-- Left Sidebar: Controls & Components -->
        <div class="sidebar">
            <div>
                <div class="section-label">Select Connected Component</div>
                <select id="componentSelect" class="select-input" onchange="loadComponent(this.value)">
                </select>
            </div>

            <div>
                <div class="section-label">Search Listing ID</div>
                <input type="text" id="listingSearchInput" class="text-input" placeholder="e.g. 1001..." onkeyup="searchListing(this.value)">
            </div>

            <div>
                <div class="section-label">Component Overview</div>
                <div class="stat-box" id="compStatBox">
                    <div class="stat-val" id="compSizeVal">—</div>
                    <div class="stat-lbl">Listings in Component</div>
                    <div style="margin-top: 8px; font-size: 12px; color: var(--text-muted);" id="compDetails">
                        Select a component to inspect its observational topology.
                    </div>
                </div>
            </div>

            <div>
                <div class="section-label">Relationship Edge Taxonomy</div>
                <div class="legend-item"><span class="legend-color" style="background: #7C3AED;"></span> Exact Image Reuse (SHA-256)</div>
                <div class="legend-item"><span class="legend-color" style="background: #10B981;"></span> Perceptual Image (pHash &le; 8)</div>
                <div class="legend-item"><span class="legend-color" style="background: #EC4899;"></span> Text Similarity (Jaccard &ge; 0.75)</div>
                <div class="legend-item"><span class="legend-color" style="background: #06B6D4;"></span> Distinctive Shared OCR Phrase</div>
                <div class="legend-item"><span class="legend-color" style="background: #3B82F6;"></span> DINO Visual Similarity</div>
            </div>

            <div>
                <div class="section-label">Graph Physics</div>
                <button class="btn" style="width: 100%;" onclick="togglePhysics()" id="physicsBtn">Freeze Physics</button>
            </div>
        </div>

        <!-- Center: Interactive Vis.js Canvas -->
        <div class="graph-area">
            <div id="networkContainer"></div>
        </div>

        <!-- Right Sidebar: Inspector Panel -->
        <div class="inspector-panel" id="inspectorPanel">
            <div class="section-label">Entity Inspector</div>
            <div id="inspectorContent" style="font-size: 13px; color: var(--text-muted);">
                Click on any node or edge in the graph canvas to inspect its underlying forensic evidence and source provenance.
            </div>
        </div>
    </div>

    <script>
        const graphsData = {graph_payload};
        const compsMeta = {comps_meta_json};

        let network = null;
        let physicsEnabled = true;
        let currentComponentId = null;

        // Initialize Component Dropdown
        const select = document.getElementById('componentSelect');
        compsMeta.forEach(c => {{
            const opt = document.createElement('option');
            opt.value = c.component_id;
            opt.textContent = `${{c.component_id}} (${{c.node_count}} listings | ${{c.city_count}} cities)`;
            select.appendChild(opt);
        }});

        function loadComponent(cid) {{
            currentComponentId = cid;
            const data = graphsData[cid];
            if (!data) return;

            // Update stats
            document.getElementById('compSizeVal').textContent = data.meta.node_count;
            document.getElementById('compDetails').innerHTML = `
                Cities: <strong>${{data.meta.city_count}}</strong> &bull; States: <strong>${{data.meta.state_count}}</strong><br>
                Products: <strong>${{data.meta.product_family_count}}</strong> families<br>
                Edges: <strong>${{data.meta.edge_count}}</strong> relationships
            `;

            // Setup Vis.js
            const container = document.getElementById('networkContainer');
            const visNodes = new vis.DataSet(data.nodes.map(n => ({{
                id: n.id,
                label: n.label,
                title: n.title,
                shape: 'box',
                color: {{
                    background: '#1E293B',
                    border: '#3B82F6',
                    highlight: {{ background: '#2563EB', border: '#60A5FA' }}
                }},
                font: {{ color: '#F8FAFC', face: 'Plus Jakarta Sans', size: 12 }},
                margin: 10,
                raw: n
            }})));

            const visEdges = new vis.DataSet(data.edges.map(e => ({{
                from: e.from,
                to: e.to,
                label: e.label,
                title: e.title,
                color: e.color,
                font: {{ color: '#94A3B8', size: 10, align: 'middle' }},
                arrows: 'to, from',
                smooth: {{ type: 'continuous' }},
                raw: e
            }})));

            const options = {{
                nodes: {{ borderWidth: 2 }},
                edges: {{ width: 1.5 }},
                physics: {{
                    enabled: physicsEnabled,
                    barnesHut: {{
                        gravitationalConstant: -2500,
                        springConstant: 0.04,
                        springLength: 120
                    }}
                }},
                interaction: {{ hover: true, tooltipDelay: 200 }}
            }};

            if (network) network.destroy();
            network = new vis.Network(container, {{ nodes: visNodes, edges: visEdges }}, options);

            network.on('click', function(params) {{
                if (params.nodes.length > 0) {{
                    const nid = params.nodes[0];
                    const nodeObj = visNodes.get(nid);
                    inspectNode(nodeObj.raw);
                }} else if (params.edges.length > 0) {{
                    const eid = params.edges[0];
                    const edgeObj = visEdges.get(eid);
                    inspectEdge(edgeObj.raw);
                }}
            }});
        }}

        function inspectNode(n) {{
            const panel = document.getElementById('inspectorContent');
            panel.innerHTML = `
                <div style="font-weight: 800; font-size: 15px; color: #38BDF8; margin-bottom: 8px;">${{n.id}}</div>
                <div style="background: var(--surface-card); padding: 12px; border-radius: 8px; border: 1px solid var(--border-color); display: flex; flex-direction: column; gap: 8px;">
                    <div><span style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">Product:</span><br><strong>${{n.product || 'Unknown'}}</strong></div>
                    <div><span style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">Family:</span><br>${{n.product_family || 'Unknown'}}</div>
                    <div><span style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">Geography:</span><br>${{n.city || 'Unknown'}}, ${{n.state || 'Unknown'}}</div>
                </div>
            `;
        }}

        function inspectEdge(e) {{
            const panel = document.getElementById('inspectorContent');
            panel.innerHTML = `
                <div style="font-weight: 800; font-size: 15px; color: #F472B6; margin-bottom: 8px;">Relationship Evidence</div>
                <div style="background: var(--surface-card); padding: 12px; border-radius: 8px; border: 1px solid var(--border-color); display: flex; flex-direction: column; gap: 8px;">
                    <div><span style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">Type:</span><br><strong>${{e.relationship_type}}</strong></div>
                    <div><span style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">Source:</span><br>${{e.from}} &harr; ${{e.to}}</div>
                    <div><span style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">Evidence ID:</span><br><code>${{e.evidence_id || '—'}}</code></div>
                </div>
            `;
        }}

        function togglePhysics() {{
            physicsEnabled = !physicsEnabled;
            if (network) network.setOptions({{ physics: {{ enabled: physicsEnabled }} }});
            document.getElementById('physicsBtn').textContent = physicsEnabled ? 'Freeze Physics' : 'Resume Physics';
        }}

        function searchListing(q) {{
            if (!q) return;
            const target = 'listing:' + q.trim();
            for (const [cid, data] of Object.entries(graphsData)) {{
                if (data.nodes.some(n => n.id === target || n.id.includes(q.trim()))) {{
                    select.value = cid;
                    loadComponent(cid);
                    break;
                }}
            }}
        }}

        // Initial Load
        if (compsMeta.length > 0) {{
            loadComponent(compsMeta[0].component_id);
        }}
    </script>
</body>
</html>
"""
        return self._write_and_sync("relationship_graph.html", html)
