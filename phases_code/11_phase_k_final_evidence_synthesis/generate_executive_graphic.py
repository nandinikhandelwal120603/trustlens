"""Generates a high-resolution, executive-ready infographic image combining
TrustLens Architecture and Empirical Research Results.

Output: showcase/outreach/trustlens_architecture_and_results.png (1920x1080)
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

def create_infographic():
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor("#090d16")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("#090d16")
    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)
    ax.axis("off")

    # Font colors
    c_white = "#ffffff"
    c_head = "#f8fafc"
    c_sub = "#94a3b8"
    c_cyan = "#38bdf8"
    c_green = "#34d399"
    c_purple = "#a855f7"
    c_amber = "#fbbf24"
    c_rose = "#f43f5e"
    c_card = "#111827"
    c_border = "#1f2937"
    c_inner = "#1e293b"

    # =========================================================================
    # HEADER SECTION
    # =========================================================================
    ax.text(80, 1010, "TRUSTLENS", fontsize=32, fontweight="bold", color=c_cyan, fontfamily="sans-serif")
    ax.text(320, 1012, "— Multimodal Marketplace Fraud Intelligence System", fontsize=22, fontweight="bold", color=c_head, fontfamily="sans-serif")
    ax.text(80, 975, "Independent research prototype analyzing 2,980 OLX listings across Computer Vision, Packaging OCR, Graph Analytics & Statistical Novelty", fontsize=13, color=c_sub, fontfamily="sans-serif")

    # Badge in top right
    badge_bg = patches.FancyBboxPatch((1560, 980), 280, 45, boxstyle="round,pad=5,rounding_size=8", facecolor="#1e293b", edgecolor=c_cyan, linewidth=1.5)
    ax.add_patch(badge_bg)
    ax.text(1700, 1002, "PHASES A–K COMPLETE • 124 TESTS", fontsize=11, fontweight="bold", color=c_cyan, ha="center", va="center")

    # Separator line
    ax.plot([80, 1840], [950, 950], color="#334155", linewidth=1.5)

    # =========================================================================
    # LEFT PANEL: SYSTEM ARCHITECTURE (X: 80 to 980)
    # =========================================================================
    left_bg = patches.FancyBboxPatch((80, 80), 900, 840, boxstyle="round,pad=10,rounding_size=12", facecolor=c_card, edgecolor=c_border, linewidth=1.5)
    ax.add_patch(left_bg)

    ax.text(110, 885, "SYSTEM ARCHITECTURE & MULTIMODAL PIPELINE", fontsize=16, fontweight="bold", color=c_cyan)
    ax.text(110, 862, "End-to-end evidence triangulation replacing black-box 'scam probability' scores", fontsize=11, color=c_sub)

    # Arch Step 1: Ingestion
    s1_bg = patches.FancyBboxPatch((110, 775), 840, 65, boxstyle="round,pad=5,rounding_size=8", facecolor=c_inner, edgecolor="#38bdf8", linewidth=1.5)
    ax.add_patch(s1_bg)
    ax.text(130, 815, "1. Ingestion & Normalization", fontsize=13, fontweight="bold", color=c_head)
    ax.text(130, 792, "2,980 Canonical Listings • Rule-based taxonomy normalizer • Comparable model median price deviation (< -35% outlier flags)", fontsize=10.5, color=c_sub)

    # Down arrow
    ax.annotate("", xy=(530, 740), xytext=(530, 775), arrowprops=dict(arrowstyle="->", color=c_cyan, lw=2))

    # Arch Step 2: 4 Parallel Modality Cards
    ax.text(110, 725, "2. Multimodal Forensic Extraction Subsystems", fontsize=13, fontweight="bold", color=c_head)

    # Sub-card 2A: Price & Text
    c2a = patches.FancyBboxPatch((110, 580), 405, 130, boxstyle="round,pad=5,rounding_size=8", facecolor="#0f172a", edgecolor="#334155", linewidth=1)
    ax.add_patch(c2a)
    ax.text(125, 680, "PRICE & TEXT INTELLIGENCE", fontsize=11, fontweight="bold", color=c_cyan)
    ax.text(125, 655, "• Comparable Price Benchmarking", fontsize=10, fontweight="bold", color=c_head)
    ax.text(125, 638, "  Medians by normalized model (iPhone 13, 14, 15...)", fontsize=9, color=c_sub)
    ax.text(125, 618, "• Lexical N-Grams & TF-IDF Extraction", fontsize=10, fontweight="bold", color=c_head)
    ax.text(125, 601, "  Contact-redirection regexes ('WhatsApp only')", fontsize=9, color=c_sub)

    # Sub-card 2B: Computer Vision (DINOv2 & Hashes)
    c2b = patches.FancyBboxPatch((545, 580), 405, 130, boxstyle="round,pad=5,rounding_size=8", facecolor="#0f172a", edgecolor="#334155", linewidth=1)
    ax.add_patch(c2b)
    ax.text(560, 680, "COMPUTER VISION FORENSICS", fontsize=11, fontweight="bold", color=c_purple)
    ax.text(560, 655, "• Cryptographic SHA-256 Hashing", fontsize=10, fontweight="bold", color=c_head)
    ax.text(560, 638, "  Byte-for-byte exact duplicate image detection", fontsize=9, color=c_sub)
    ax.text(560, 618, "• 384-d DINOv2 Dense Embeddings", fontsize=10, fontweight="bold", color=c_head)
    ax.text(560, 601, "  Vision transformer captures shifted angles/lighting", fontsize=9, color=c_sub)

    # Sub-card 2C: Packaging OCR (Tesseract)
    c2c = patches.FancyBboxPatch((110, 435), 405, 130, boxstyle="round,pad=5,rounding_size=8", facecolor="#0f172a", edgecolor="#334155", linewidth=1)
    ax.add_patch(c2c)
    ax.text(125, 535, "PACKAGING OCR VERIFICATION", fontsize=11, fontweight="bold", color=c_amber)
    ax.text(125, 510, "• Tesseract 5.5 OCR Pipeline", fontsize=10, fontweight="bold", color=c_head)
    ax.text(125, 493, "  Text extraction from box packaging & device screens", fontsize=9, color=c_sub)
    ax.text(125, 473, "• Multimodal Claim Verification", fontsize=10, fontweight="bold", color=c_head)
    ax.text(125, 456, "  Cross-references declared title text against box text", fontsize=9, color=c_sub)

    # Sub-card 2D: Dual-Detector AI Consensus
    c2d = patches.FancyBboxPatch((545, 435), 405, 130, boxstyle="round,pad=5,rounding_size=8", facecolor="#0f172a", edgecolor="#334155", linewidth=1)
    ax.add_patch(c2d)
    ax.text(560, 535, "DUAL-DETECTOR AI CONSENSUS", fontsize=11, fontweight="bold", color=c_green)
    ax.text(560, 510, "• ViT-Base & Swin-Base Sequential Ensemble", fontsize=10, fontweight="bold", color=c_head)
    ax.text(560, 493, "  Two independent vision models evaluate synthetic cues", fontsize=9, color=c_sub)
    ax.text(560, 473, "• Strict Consensus Threshold (0.70)", fontsize=10, fontweight="bold", color=c_head)
    ax.text(560, 456, "  Filters out 559 single-detector disagreements", fontsize=9, color=c_sub)

    # Down arrow
    ax.annotate("", xy=(530, 400), xytext=(530, 435), arrowprops=dict(arrowstyle="->", color=c_cyan, lw=2))

    # Arch Step 3: Graph & Feature Store
    s3_bg = patches.FancyBboxPatch((110, 315), 840, 75, boxstyle="round,pad=5,rounding_size=8", facecolor=c_inner, edgecolor="#a855f7", linewidth=1.5)
    ax.add_patch(s3_bg)
    ax.text(130, 365, "3. Relationship Network & Unified Feature Store", fontsize=13, fontweight="bold", color=c_head)
    ax.text(130, 345, "• 5,709-Node Heterogeneous Entity Graph (21,395 relationship edges linking listings, SHA images, OCR phrases, cities)", fontsize=10, color=c_sub)
    ax.text(130, 328, "• Unified Analytical Feature Store (2,980 rows × 137 validated features; zero data leakage)", fontsize=10, color=c_sub)

    # Down arrow
    ax.annotate("", xy=(530, 280), xytext=(530, 315), arrowprops=dict(arrowstyle="->", color=c_cyan, lw=2))

    # Arch Step 4: Isolation Forest & Synthesis
    s4_bg = patches.FancyBboxPatch((110, 195), 840, 75, boxstyle="round,pad=5,rounding_size=8", facecolor=c_inner, edgecolor="#10b981", linewidth=1.5)
    ax.add_patch(s4_bg)
    ax.text(130, 245, "4. Multivariate Novelty Modeling & Evidence Synthesis", fontsize=13, fontweight="bold", color=c_head)
    ax.text(130, 225, "• Isolation Forest fitted across 4 feature spaces (Price, Price+Text, Price+Image, Full Multimodal)", fontsize=10, color=c_sub)
    ax.text(130, 208, "• Persistence analysis isolating 3 stable multivariate outliers across the entire corpus", fontsize=10, color=c_sub)

    # Down arrow
    ax.annotate("", xy=(530, 160), xytext=(530, 195), arrowprops=dict(arrowstyle="->", color=c_rose, lw=2))

    # Arch Step 5: Output
    s5_bg = patches.FancyBboxPatch((110, 95), 840, 60, boxstyle="round,pad=5,rounding_size=8", facecolor="#1e1b4b", edgecolor=c_rose, linewidth=1.5)
    ax.add_patch(s5_bg)
    ax.text(530, 137, "OUTPUT: EXPLAINABLE RESEARCH REVIEW QUEUE (213 MULTI-SIGNAL PAIRS)", fontsize=12, fontweight="bold", color=c_white, ha="center")
    ax.text(530, 115, "Zero fake scam probabilities • Prioritizes listings by integer count of independent forensic layers", fontsize=10, color="#cbd5e1", ha="center")

    # =========================================================================
    # RIGHT PANEL: EMPIRICAL FINDINGS & RESULTS (X: 1020 to 1840)
    # =========================================================================
    right_bg = patches.FancyBboxPatch((1020, 80), 820, 840, boxstyle="round,pad=10,rounding_size=12", facecolor=c_card, edgecolor=c_border, linewidth=1.5)
    ax.add_patch(right_bg)

    ax.text(1050, 885, "EMPIRICAL RESEARCH FINDINGS ON OLX DATASET", fontsize=16, fontweight="bold", color=c_green)
    ax.text(1050, 862, "Hard verified metrics from 2,980 listings & 2,280 processed media assets", fontsize=11, color=c_sub)

    # Top KPI row (4 stat boxes)
    kpis = [
        ("2,980", "Canonical Listings", "100% Deduplicated", c_cyan),
        ("2,280", "Images Evaluated", "Vision & OCR Tested", c_purple),
        ("213", "Multi-Signal Pairs", "≥2 Evidence Layers", c_green),
        ("124", "Tests Passed", "Continuous CI Suite", c_amber),
    ]
    for i, (val, title, sub, col) in enumerate(kpis):
        kx = 1050 + i * 195
        k_box = patches.FancyBboxPatch((kx, 765), 180, 80, boxstyle="round,pad=5,rounding_size=8", facecolor="#0f172a", edgecolor="#334155", linewidth=1.2)
        ax.add_patch(k_box)
        ax.text(kx + 90, 822, val, fontsize=22, fontweight="bold", color=col, ha="center")
        ax.text(kx + 90, 797, title, fontsize=9.5, fontweight="bold", color=c_head, ha="center")
        ax.text(kx + 90, 780, sub, fontsize=8.5, color=c_sub, ha="center")

    # Key Finding 1: Image Duplication
    f1 = patches.FancyBboxPatch((1050, 625), 760, 120, boxstyle="round,pad=5,rounding_size=8", facecolor=c_inner, edgecolor=c_border, linewidth=1)
    ax.add_patch(f1)
    ax.text(1070, 715, "1. Cross-City Image Duplication (78.0% Cross-Market)", fontsize=12, fontweight="bold", color=c_cyan)
    ax.text(1070, 692, "• Discovered 164 pairwise instances of exact binary image reuse (SHA-256) across 242 listings.", fontsize=10, color=c_head)
    ax.text(1070, 674, "• 78.0% of identical image pairs spanned different cities (e.g. Thane & Mumbai; Delhi & Jaipur).", fontsize=10, color=c_sub)
    ax.text(1070, 656, "• Deep visual similarity (DINOv2 cosine ≥ 0.70) connected 9,492 pairs across angle/lighting shifts.", fontsize=10, color=c_sub)

    # Key Finding 2: OCR Contradiction
    f2 = patches.FancyBboxPatch((1050, 485), 760, 120, boxstyle="round,pad=5,rounding_size=8", facecolor=c_inner, edgecolor=c_border, linewidth=1)
    ax.add_patch(f2)
    ax.text(1070, 575, "2. Multimodal OCR Claim Inconsistencies (68 Candidates)", fontsize=12, fontweight="bold", color=c_amber)
    ax.text(1070, 552, "• Tesseract OCR achieved 82.7% text extraction rate (1,885 of 2,280 images contained legible text).", fontsize=10, color=c_head)
    ax.text(1070, 534, "• Model Mismatch: Listing title declared 'iPhone 13 128', but box OCR detected 'iPhone 13 Mini'.", fontsize=10, color=c_sub)
    ax.text(1070, 516, "• 66 Shared-Image Claim Drifts: Listings sharing identical photos but asserting conflicting storage/prices.", fontsize=10, color=c_sub)

    # Key Finding 3: AI Detector Disagreements
    f3 = patches.FancyBboxPatch((1050, 345), 760, 120, boxstyle="round,pad=5,rounding_size=8", facecolor=c_inner, edgecolor=c_border, linewidth=1)
    ax.add_patch(f3)
    ax.text(1070, 435, "3. Dual-AI Consensus & 559 Detector Disagreements", fontsize=12, fontweight="bold", color=c_rose)
    ax.text(1070, 412, "• Evaluated 2,280 images across ViT-Base & Swin-Base synthetic image classifiers.", fontsize=10, color=c_head)
    ax.text(1070, 394, "• 559 Detector Disagreements (24.5%): Swin-Base flagged AI while ViT-Base scored Real.", fontsize=10, color=c_sub)
    ax.text(1070, 376, "• Only 6 images had mutual AI consensus (manual review showed commercial 3D renders, not deepfakes).", fontsize=10, color=c_sub)

    # Key Finding 4: Relationship Network Hubs
    f4 = patches.FancyBboxPatch((1050, 205), 760, 120, boxstyle="round,pad=5,rounding_size=8", facecolor=c_inner, edgecolor=c_border, linewidth=1)
    ax.add_patch(f4)
    ax.text(1070, 295, "4. Commercial Syndication Hubs & Macro-Clusters", fontsize=12, fontweight="bold", color=c_purple)
    ax.text(1070, 272, "• Entity graph identified 2,133 connected components; largest spans 122 listings across 14 cities.", fontsize=10, color=c_head)
    ax.text(1070, 254, "• 213 Multi-Signal Pairs: Corroborated by ≥2 independent layers (4 layers: 5 pairs; 3 layers: 63; 2: 145).", fontsize=10, color=c_sub)
    ax.text(1070, 236, "• Isolates merchant syndication & template automation without requiring persistent seller IDs.", fontsize=10, color=c_sub)

    # Key Finding 5: What We Refused to Automate
    f5 = patches.FancyBboxPatch((1050, 95), 760, 95, boxstyle="round,pad=5,rounding_size=8", facecolor="#064e3b", edgecolor=c_green, linewidth=1.2)
    ax.add_patch(f5)
    ax.text(1070, 160, "CORE PRINCIPLE: WHAT TRUSTLENS REFUSED TO AUTOMATE", fontsize=11, fontweight="bold", color=c_white)
    ax.text(1070, 138, "• NO black-box scam scores without transaction ground truth (avoids misleading 90%+ fake probabilities).", fontsize=9.5, color="#a7f3d0")
    ax.text(1070, 120, "• NO automated seller accusations (functions as an investigator copilot, organizing multi-modal proof).", fontsize=9.5, color="#a7f3d0")

    # Save
    out_dir = Path("showcase/outreach")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "trustlens_architecture_and_results.png"
    plt.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    print(f"Generated executive infographic: {out_path}")

if __name__ == "__main__":
    create_infographic()
