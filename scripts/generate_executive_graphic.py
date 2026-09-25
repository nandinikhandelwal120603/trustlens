"""Generates a high-resolution, executive-ready infographic image combining
TrustLens Architecture and Empirical Research Results.

Outputs:
- all_graphs_and_images/infographics_and_architecture/trustlens_architecture_and_results.png
- showcase/outreach/trustlens_architecture_and_results.png
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

    # Color palette
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
    c_olx = "#002f34"
    c_olx_accent = "#23e5db"

    # =========================================================================
    # HEADER SECTION
    # =========================================================================
    # Title
    ax.text(80, 1022, "TRUSTLENS", fontsize=28, fontweight="bold", color=c_cyan, fontfamily="sans-serif")
    ax.text(360, 1025, "—  Multimodal Marketplace Fraud Intelligence System", fontsize=20, fontweight="bold", color=c_head, fontfamily="sans-serif")
    
    # Subtitle with OLX context
    ax.text(80, 982, "Empirical research analyzing 2,980 OLX India listings across Computer Vision, Packaging OCR, Graph Analytics & Statistical Novelty", fontsize=12.5, color=c_sub, fontfamily="sans-serif")

    # OLX Target Badge in header
    olx_badge = patches.FancyBboxPatch((1330, 980), 180, 48, boxstyle="round,pad=4,rounding_size=8", facecolor=c_olx, edgecolor=c_olx_accent, linewidth=1.5)
    ax.add_patch(olx_badge)
    ax.text(1420, 1004, "OLX INDIA CORPUS", fontsize=11, fontweight="bold", color=c_olx_accent, ha="center", va="center")

    # Verification Badge in top right
    badge_bg = patches.FancyBboxPatch((1530, 980), 310, 48, boxstyle="round,pad=4,rounding_size=8", facecolor="#1e293b", edgecolor=c_cyan, linewidth=1.5)
    ax.add_patch(badge_bg)
    ax.text(1685, 1004, "PHASES A–K COMPLETE • 124 TESTS", fontsize=11, fontweight="bold", color=c_cyan, ha="center", va="center")

    # Separator line
    ax.plot([80, 1840], [950, 950], color="#334155", linewidth=1.5)

    # =========================================================================
    # LEFT PANEL: SYSTEM ARCHITECTURE (X: 80 to 980)
    # =========================================================================
    left_bg = patches.FancyBboxPatch((80, 75), 900, 845, boxstyle="round,pad=10,rounding_size=12", facecolor=c_card, edgecolor=c_border, linewidth=1.5)
    ax.add_patch(left_bg)

    ax.text(110, 888, "SYSTEM ARCHITECTURE & MULTIMODAL PIPELINE", fontsize=16, fontweight="bold", color=c_cyan)
    ax.text(110, 866, "Evidence-based multi-signal triangulation replacing black-box 'scam probability' scores", fontsize=11, color=c_sub)

    # Arch Step 1: Ingestion & Normalization
    s1_bg = patches.FancyBboxPatch((110, 765), 840, 75, boxstyle="round,pad=5,rounding_size=8", facecolor=c_inner, edgecolor="#38bdf8", linewidth=1.5)
    ax.add_patch(s1_bg)
    ax.text(130, 814, "1. Ingestion & Deterministic Normalization", fontsize=13, fontweight="bold", color=c_head)
    ax.text(130, 792, "• 2,980 Canonical Listings normalized via rule-based product taxonomy (81 models)", fontsize=10.5, color=c_sub)
    ax.text(130, 774, "• Model price deviation metrics isolating extreme discount bands (≤ -35% and ≤ -50% outliers)", fontsize=10.5, color=c_sub)

    # Down arrow
    ax.annotate("", xy=(530, 730), xytext=(530, 765), arrowprops=dict(arrowstyle="->", color=c_cyan, lw=2))

    # Arch Step 2: 4 Parallel Modality Cards
    ax.text(110, 712, "2. Multimodal Forensic Extraction Subsystems", fontsize=13, fontweight="bold", color=c_head)

    # Sub-card 2A: Price & Text
    c2a = patches.FancyBboxPatch((110, 565), 405, 130, boxstyle="round,pad=5,rounding_size=8", facecolor="#0f172a", edgecolor="#334155", linewidth=1)
    ax.add_patch(c2a)
    ax.text(125, 668, "PRICE & TEXT INTELLIGENCE", fontsize=11, fontweight="bold", color=c_cyan)
    ax.text(125, 644, "• Comparable Price Benchmarking", fontsize=10, fontweight="bold", color=c_head)
    ax.text(125, 628, "  Medians by normalized model (iPhone 13, 14, 15...)", fontsize=9, color=c_sub)
    ax.text(125, 608, "• Lexical N-Grams & TF-IDF Extraction", fontsize=10, fontweight="bold", color=c_head)
    ax.text(125, 592, "  Contact-redirection regexes ('WhatsApp only')", fontsize=9, color=c_sub)

    # Sub-card 2B: Computer Vision (DINOv2 & Hashes)
    c2b = patches.FancyBboxPatch((545, 565), 405, 130, boxstyle="round,pad=5,rounding_size=8", facecolor="#0f172a", edgecolor="#334155", linewidth=1)
    ax.add_patch(c2b)
    ax.text(560, 668, "COMPUTER VISION FORENSICS", fontsize=11, fontweight="bold", color=c_purple)
    ax.text(560, 644, "• Cryptographic SHA-256 Hashing", fontsize=10, fontweight="bold", color=c_head)
    ax.text(560, 628, "  Byte-for-byte exact duplicate image detection", fontsize=9, color=c_sub)
    ax.text(560, 608, "• 384-d DINOv2 Dense Embeddings", fontsize=10, fontweight="bold", color=c_head)
    ax.text(560, 592, "  Foundation vision model captures shifted angles/lighting", fontsize=9, color=c_sub)

    # Sub-card 2C: Packaging OCR (Tesseract)
    c2c = patches.FancyBboxPatch((110, 420), 405, 130, boxstyle="round,pad=5,rounding_size=8", facecolor="#0f172a", edgecolor="#334155", linewidth=1)
    ax.add_patch(c2c)
    ax.text(125, 523, "PACKAGING OCR VERIFICATION", fontsize=11, fontweight="bold", color=c_amber)
    ax.text(125, 499, "• Tesseract 5.5 OCR Pipeline", fontsize=10, fontweight="bold", color=c_head)
    ax.text(125, 483, "  Text extraction from box packaging & device screens", fontsize=9, color=c_sub)
    ax.text(125, 463, "• Multimodal Claim Verification", fontsize=10, fontweight="bold", color=c_head)
    ax.text(125, 447, "  Cross-references declared title text against box text", fontsize=9, color=c_sub)

    # Sub-card 2D: Dual-Detector AI Consensus
    c2d = patches.FancyBboxPatch((545, 420), 405, 130, boxstyle="round,pad=5,rounding_size=8", facecolor="#0f172a", edgecolor="#334155", linewidth=1)
    ax.add_patch(c2d)
    ax.text(560, 523, "DUAL-DETECTOR AI CONSENSUS", fontsize=11, fontweight="bold", color=c_green)
    ax.text(560, 499, "• ViT-Base & Swin-Base Sequential Ensemble", fontsize=10, fontweight="bold", color=c_head)
    ax.text(560, 483, "  Two independent vision models evaluate synthetic cues", fontsize=9, color=c_sub)
    ax.text(560, 463, "• Strict Consensus Threshold (0.70)", fontsize=10, fontweight="bold", color=c_head)
    ax.text(560, 447, "  Filters out 559 single-detector disagreements", fontsize=9, color=c_sub)

    # Down arrow
    ax.annotate("", xy=(530, 385), xytext=(530, 420), arrowprops=dict(arrowstyle="->", color=c_cyan, lw=2))

    # Arch Step 3: Graph & Feature Store
    s3_bg = patches.FancyBboxPatch((110, 300), 840, 75, boxstyle="round,pad=5,rounding_size=8", facecolor=c_inner, edgecolor="#a855f7", linewidth=1.5)
    ax.add_patch(s3_bg)
    ax.text(130, 350, "3. Relationship Network & Unified Feature Store", fontsize=13, fontweight="bold", color=c_head)
    ax.text(130, 330, "• 5,709-Node Heterogeneous Entity Graph (21,395 edges linking listings, SHA images, OCR, cities)", fontsize=10, color=c_sub)
    ax.text(130, 312, "• 137-Column Canonical Feature Store (2,980 listings; 0 missing joins; zero target leakage)", fontsize=10, color=c_sub)

    # Down arrow
    ax.annotate("", xy=(530, 265), xytext=(530, 300), arrowprops=dict(arrowstyle="->", color=c_cyan, lw=2))

    # Arch Step 4: Isolation Forest & Synthesis
    s4_bg = patches.FancyBboxPatch((110, 180), 840, 75, boxstyle="round,pad=5,rounding_size=8", facecolor=c_inner, edgecolor="#10b981", linewidth=1.5)
    ax.add_patch(s4_bg)
    ax.text(130, 230, "4. Multivariate Novelty Modeling & Evidence Synthesis", fontsize=13, fontweight="bold", color=c_head)
    ax.text(130, 210, "• Isolation Forest fitted across 4 feature spaces (Price, Price+Text, Price+Image, Full Multimodal)", fontsize=10, color=c_sub)
    ax.text(130, 192, "• Persistence analysis isolating 3 stable multivariate outliers across the entire corpus", fontsize=10, color=c_sub)

    # Down arrow
    ax.annotate("", xy=(530, 145), xytext=(530, 180), arrowprops=dict(arrowstyle="->", color=c_rose, lw=2))

    # Arch Step 5: Output
    s5_bg = patches.FancyBboxPatch((110, 85), 840, 56, boxstyle="round,pad=5,rounding_size=8", facecolor="#1e1b4b", edgecolor=c_rose, linewidth=1.5)
    ax.add_patch(s5_bg)
    ax.text(530, 120, "OUTPUT: EXPLAINABLE RESEARCH REVIEW QUEUE (213 MULTI-SIGNAL PAIRS)", fontsize=12, fontweight="bold", color=c_white, ha="center")
    ax.text(530, 98, "Zero fake scam probabilities • Prioritizes listings by integer count of independent forensic layers", fontsize=10, color="#cbd5e1", ha="center")

    # =========================================================================
    # RIGHT PANEL: EMPIRICAL FINDINGS & RESULTS (X: 1020 to 1840)
    # =========================================================================
    right_bg = patches.FancyBboxPatch((1020, 75), 820, 845, boxstyle="round,pad=10,rounding_size=12", facecolor=c_card, edgecolor=c_border, linewidth=1.5)
    ax.add_patch(right_bg)

    ax.text(1050, 888, "EMPIRICAL RESEARCH FINDINGS ON OLX DATASET", fontsize=16, fontweight="bold", color=c_green)
    ax.text(1050, 866, "Verified quantitative findings from 2,980 listings & 2,280 processed media assets", fontsize=11, color=c_sub)

    # Top KPI row (4 stat boxes)
    kpis = [
        ("2,980", "Canonical Listings", "100% Deduplicated", c_cyan),
        ("2,280", "Images Evaluated", "Vision & OCR Tested", c_purple),
        ("213", "Multi-Signal Pairs", "≥2 Evidence Layers", c_green),
        ("124", "Tests Passed", "Continuous CI Suite", c_amber),
    ]
    for i, (val, title, sub, col) in enumerate(kpis):
        kx = 1050 + i * 195
        k_box = patches.FancyBboxPatch((kx, 765), 180, 82, boxstyle="round,pad=5,rounding_size=8", facecolor="#0f172a", edgecolor="#334155", linewidth=1.2)
        ax.add_patch(k_box)
        ax.text(kx + 90, 824, val, fontsize=22, fontweight="bold", color=col, ha="center")
        ax.text(kx + 90, 798, title, fontsize=9.5, fontweight="bold", color=c_head, ha="center")
        ax.text(kx + 90, 781, sub, fontsize=8.5, color=c_sub, ha="center")

    # Key Finding 1: Image Duplication
    f1 = patches.FancyBboxPatch((1050, 625), 760, 118, boxstyle="round,pad=5,rounding_size=8", facecolor=c_inner, edgecolor=c_border, linewidth=1)
    ax.add_patch(f1)
    ax.text(1070, 714, "1. Cross-City Image Duplication (78.0% Cross-Market)", fontsize=12, fontweight="bold", color=c_cyan)
    ax.text(1070, 691, "• Discovered 164 pairwise instances of exact binary image reuse (SHA-256) across 242 listings.", fontsize=10, color=c_head)
    ax.text(1070, 673, "• 78.0% of identical image pairs spanned different cities (e.g. Thane & Mumbai; Delhi & Jaipur).", fontsize=10, color=c_sub)
    ax.text(1070, 655, "• Deep visual similarity (DINOv2 cosine ≥ 0.70) connected 9,492 pairs across angle/lighting shifts.", fontsize=10, color=c_sub)

    # Key Finding 2: OCR Contradiction
    f2 = patches.FancyBboxPatch((1050, 485), 760, 118, boxstyle="round,pad=5,rounding_size=8", facecolor=c_inner, edgecolor=c_border, linewidth=1)
    ax.add_patch(f2)
    ax.text(1070, 574, "2. Multimodal OCR Claim Inconsistencies (68 Candidates)", fontsize=12, fontweight="bold", color=c_amber)
    ax.text(1070, 551, "• Tesseract OCR achieved 82.7% text extraction rate (1,885 of 2,280 images contained legible text).", fontsize=10, color=c_head)
    ax.text(1070, 533, "• Model Mismatch: Listing title declared 'iPhone 13 128', but box OCR detected 'iPhone 13 Mini'.", fontsize=10, color=c_sub)
    ax.text(1070, 515, "• 66 Shared-Image Claim Drifts: Listings sharing identical photos but asserting conflicting storage/prices.", fontsize=10, color=c_sub)

    # Key Finding 3: AI Detector Disagreements
    f3 = patches.FancyBboxPatch((1050, 345), 760, 118, boxstyle="round,pad=5,rounding_size=8", facecolor=c_inner, edgecolor=c_border, linewidth=1)
    ax.add_patch(f3)
    ax.text(1070, 434, "3. Dual-AI Consensus & 559 Detector Disagreements", fontsize=12, fontweight="bold", color=c_rose)
    ax.text(1070, 411, "• Evaluated 2,280 images across ViT-Base & Swin-Base synthetic image classifiers.", fontsize=10, color=c_head)
    ax.text(1070, 393, "• 559 Detector Disagreements (24.5%): Swin-Base flagged AI while ViT-Base scored Real.", fontsize=10, color=c_sub)
    ax.text(1070, 375, "• Only 6 images had mutual AI consensus (manual review showed commercial 3D renders, not deepfakes).", fontsize=10, color=c_sub)

    # Key Finding 4: Relationship Network Hubs
    f4 = patches.FancyBboxPatch((1050, 205), 760, 118, boxstyle="round,pad=5,rounding_size=8", facecolor=c_inner, edgecolor=c_border, linewidth=1)
    ax.add_patch(f4)
    ax.text(1070, 294, "4. Commercial Syndication Hubs & Macro-Clusters", fontsize=12, fontweight="bold", color=c_purple)
    ax.text(1070, 271, "• Entity graph identified 2,133 connected components; largest spans 122 listings across 14 cities.", fontsize=10, color=c_head)
    ax.text(1070, 253, "• 213 Multi-Signal Pairs: Corroborated by ≥2 independent layers (4 layers: 5 pairs; 3 layers: 63; 2: 145).", fontsize=10, color=c_sub)
    ax.text(1070, 235, "• Isolates merchant syndication & template automation without requiring persistent seller IDs.", fontsize=10, color=c_sub)

    # Key Finding 5: What We Refused to Automate
    f5 = patches.FancyBboxPatch((1050, 85), 760, 96, boxstyle="round,pad=5,rounding_size=8", facecolor="#064e3b", edgecolor=c_green, linewidth=1.2)
    ax.add_patch(f5)
    ax.text(1070, 152, "CORE PRINCIPLE: WHAT TRUSTLENS REFUSED TO AUTOMATE", fontsize=11, fontweight="bold", color=c_white)
    ax.text(1070, 131, "• NO black-box scam scores without transaction ground truth (avoids misleading 90%+ fake probabilities).", fontsize=9.5, color="#a7f3d0")
    ax.text(1070, 113, "• NO automated seller accusations (functions as an investigator copilot, organizing multi-modal proof).", fontsize=9.5, color="#a7f3d0")

    # Save to both target locations
    targets = [
        Path("all_graphs_and_images/infographics_and_architecture/trustlens_architecture_and_results.png"),
        Path("showcase/outreach/trustlens_architecture_and_results.png"),
    ]
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(target, facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
        print(f"Generated clean executive infographic: {target}")

    plt.close(fig)


if __name__ == "__main__":
    create_infographic()
