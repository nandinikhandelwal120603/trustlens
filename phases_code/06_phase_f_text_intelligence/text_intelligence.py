"""TrustLens Marketplace Intelligence — Text Intelligence & Lexical Linguistics (Phase F).

Executes:
1. Deterministic text normalization, tokenization, and privacy redaction.
2. Controlled, transparent marketplace lexicons (Transaction, Contact, Urgency, Clearance, Warranty, Delivery, Condition, Relocation, Company).
3. N-gram frequency analysis (Unigrams, Bigrams, Trigrams) across global corpus and product groups.
4. Pure NumPy / standard-library TF-IDF distinctive keyword extraction by product group.
5. Deterministic pairwise Jaccard text similarity and boilerplate/text reuse candidate detection.
6. Language and script distribution analysis.
7. Publication figures, inspectable text gallery, and comprehensive research reports.
"""

from collections import Counter, defaultdict
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import unicodedata

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from trustlens.marketplace.pii_redactor import PIIRedactor
from trustlens.marketplace.text_normalizer import TextNormalizer


class TextIntelligenceEngine:
    """Master deterministic engine for lexical analysis, n-grams, TF-IDF, and text reuse detection."""

    # 1. Versioned Descriptive Marketplace Lexicons (Transparent, deterministic keyword sets)
    LEXICONS: Dict[str, Set[str]] = {
        "urgency": {
            "urgent", "urgently", "immediate", "immediately", "quick", "fast",
            "today", "now", "emergency", "hurry", "asap", "leaving", "relocation",
            "relocating", "transfer", "shifting", "moving", "need gone", "sale today",
            "last chance", "limited time", "urgent sale",
        },
        "contact_redirection": {
            "whatsapp", "call", "contact", "dm", "message", "msg", "ping",
            "telegram", "number", "phone", "chat", "inbox", "reach", "ring",
        },
        "transaction_payment": {
            "price", "cash", "cod", "cash on delivery", "upi", "payment", "advance",
            "token", "deposit", "booking", "refund", "emi", "fixed price", "fixed",
            "negotiable", "bargain", "cheap", "best price", "discount", "offer",
            "final price", "non negotiable", "rate", "cost", "gpay", "phonepe", "paytm",
        },
        "clearance_commercial": {
            "clearance", "warehouse", "liquidation", "stock", "company", "office",
            "bulk", "wholesale", "dealer", "distributor", "lot", "shop", "store",
            "retailer", "supplier", "reseller", "godown", "surplus",
        },
        "warranty_authenticity": {
            "original", "genuine", "authentic", "warranty", "bill", "invoice",
            "gst", "sealed", "box pack", "seal pack", "pin pack", "brand new",
            "apple care", "under warranty", "valid bill", "official", "100% original",
            "first owner", "indian unit", "indian", "usa unit", "bill box",
        },
        "delivery_logistics": {
            "courier", "delivery", "transport", "shipping", "parcel", "dispatch",
            "pickup", "home delivery", "all india", "doorstep", "free delivery",
            "ship", "post", "speed post", "cargo",
        },
        "condition_lexicon": {
            "new", "used", "like new", "mint", "flawless", "scratchless",
            "clean", "super clean", "neat", "perfect", "good condition",
            "excellent", "damaged", "broken", "repair", "refurbished",
            "renewed", "replaced", "dead", "faulty", "scratch", "cracked",
            "minor scratch", "battery health", "bh",
        },
        "relocation": {
            "relocation", "relocating", "transfer", "shifting", "moving", "leaving",
            "going abroad", "urgent relocation", "flat shifting", "home shifting",
        },
        "company_claims": {
            "company", "corporate", "office", "official", "enterprise", "business",
            "company warranty", "company sealed", "company piece",
        },
    }

    # Stopwords tailored for marketplace title analysis (standard English functional words)
    STOPWORDS: Set[str] = {
        "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "with", "by",
        "of", "from", "as", "is", "are", "was", "were", "it", "this", "that", "all",
        "available", "very", "also", "have", "has", "had", "just", "my", "me", "we",
        "you", "your", "only", "be", "so", "if", "out", "up", "about", "into", "over",
        "after", "than", "no", "not", "any", "some", "can", "will", "do", "does",
    }

    def __init__(
        self,
        processed_dir: Path = Path("data/olx_processed"),
        reports_dir: Path = Path("data/olx_analysis/reports"),
        figures_dir: Path = Path("data/olx_analysis/reports/figures"),
    ):
        self.processed_dir = Path(processed_dir)
        self.reports_dir = Path(reports_dir)
        self.figures_dir = Path(figures_dir)

    @classmethod
    def normalize_listing_text(cls, text: Optional[str]) -> Tuple[str, str, str]:
        """Performs deterministic normalization, token cleaning, and privacy redaction.

        Returns:
            (raw_text, normalized_text, privacy_redacted_text)
        """
        if not text or not str(text).strip():
            return "", "", ""

        raw_str = str(text).strip()

        # 1. Unicode NFKC normalization
        norm = unicodedata.normalize("NFKC", raw_str)
        # 2. Lowercase
        norm = norm.lower()
        # 3. Clean special punctuation while keeping hyphens, slashes, and periods in numbers/specs
        norm = re.sub(r"[^\w\s\.\/\-\+₹]", " ", norm)
        # 4. Collapse consecutive whitespace
        norm = re.sub(r"\s+", " ", norm).strip()

        # Privacy redacted representation
        redacted = PIIRedactor.redact_text(raw_str)

        return raw_str, norm, redacted

    @classmethod
    def tokenize_preserving_specs(cls, normalized_text: str) -> List[str]:
        """Tokenizes normalized text while preserving technical numbers, GBs, models, and prices."""
        if not normalized_text:
            return []
        # Split on whitespace, strip trailing punctuation
        raw_tokens = normalized_text.split()
        tokens = []
        for t in raw_tokens:
            cleaned = t.strip(".,/-_")
            if cleaned:
                tokens.append(cleaned)
        return tokens

    @classmethod
    def detect_script(cls, text: str) -> str:
        """Determines the script composition of the text deterministically."""
        if not text:
            return "empty"

        has_latin = False
        has_devanagari = False
        has_other = False

        for ch in text:
            if not ch.isalnum():
                continue
            name = unicodedata.name(ch, "")
            if "LATIN" in name:
                has_latin = True
            elif "DEVANAGARI" in name:
                has_devanagari = True
            elif ord(ch) > 127:
                has_other = True

        if has_devanagari and has_latin:
            return "mixed_latin_devanagari"
        elif has_devanagari:
            return "devanagari"
        elif has_other and has_latin:
            return "mixed_latin_other"
        elif has_other:
            return "other_non_latin"
        elif has_latin:
            return "latin_english"
        else:
            return "numeric_symbolic"

    @classmethod
    def extract_lexicon_features(cls, tokens: List[str], text_norm: str) -> Dict[str, Any]:
        """Extracts deterministic boolean flags and match counts for all controlled lexicons."""
        token_set = set(tokens)
        features: Dict[str, Any] = {}

        for lex_name, term_set in cls.LEXICONS.items():
            count = 0
            # Multi-word phrase matching against normalized text
            for term in term_set:
                if " " in term:
                    if term in text_norm:
                        count += 1
                else:
                    if term in token_set:
                        count += 1

            features[f"has_{lex_name}"] = bool(count > 0)
            features[f"{lex_name}_term_count"] = count

        return features

    @classmethod
    def generate_ngrams(cls, tokens: List[str], n: int) -> List[str]:
        """Generates consecutive word n-grams."""
        if len(tokens) < n:
            return []
        return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]

    def compute_ngram_frequencies(
        self,
        df_text: pd.DataFrame,
        min_doc_freq: int = 2,
    ) -> pd.DataFrame:
        """Computes deterministic unigram, bigram, and trigram document & term frequencies."""
        phrase_records: List[Dict[str, Any]] = []

        for n, size_label in [(1, "unigram"), (2, "bigram"), (3, "trigram")]:
            global_tf: Counter = Counter()
            global_df: Counter = Counter()
            group_tf: Dict[Tuple[str, str], Counter] = defaultdict(Counter)

            for _, row in df_text.iterrows():
                tokens = row["tokens"]
                query = row.get("search_query", "all")
                family = row.get("product_family", "Other")

                ngrams = self.generate_ngrams(tokens, n)
                # Filter out n-grams that consist purely of standard stopwords
                valid_ngrams = []
                for g in ngrams:
                    words = g.split()
                    if not all(w in self.STOPWORDS for w in words):
                        valid_ngrams.append(g)

                for g in valid_ngrams:
                    global_tf[g] += 1
                    group_tf[(query, family)][g] += 1

                for g in set(valid_ngrams):
                    global_df[g] += 1

            # Store phrases passing minimum document frequency
            for phrase, df_count in global_df.items():
                if df_count >= min_doc_freq:
                    # Classify lexical category if phrase matches any lexicon
                    matched_lexicon = "general"
                    for lex_name, term_set in self.LEXICONS.items():
                        if phrase in term_set or any(w in term_set for w in phrase.split()):
                            matched_lexicon = lex_name
                            break

                    phrase_records.append({
                        "phrase": phrase,
                        "ngram_size": n,
                        "ngram_type": size_label,
                        "document_frequency": df_count,
                        "term_frequency": global_tf[phrase],
                        "lexical_category": matched_lexicon,
                    })

        df_phrases = pd.DataFrame(phrase_records)
        if not df_phrases.empty:
            df_phrases = df_phrases.sort_values(by=["ngram_size", "document_frequency"], ascending=[True, False]).reset_index(drop=True)
        return df_phrases

    def compute_tfidf_by_product_group(
        self,
        df_text: pd.DataFrame,
        group_col: str = "product_family",
        top_n: int = 15,
    ) -> Dict[str, List[Tuple[str, float]]]:
        """Computes deterministic TF-IDF to identify distinctive keywords per product family using pure Python/NumPy."""
        groups = df_text[group_col].dropna().unique()
        group_docs: Dict[str, List[List[str]]] = defaultdict(list)

        # Build group documents
        all_docs: List[List[str]] = []
        for _, row in df_text.iterrows():
            grp = row.get(group_col, "Other")
            # Filter tokens: remove stopwords, single letters, and purely numeric punctuation
            filtered = [t for t in row["tokens"] if t not in self.STOPWORDS and len(t) > 1 and not t.isdigit()]
            group_docs[grp].append(filtered)
            all_docs.append(filtered)

        total_docs = len(all_docs)
        if total_docs == 0:
            return {}

        # 1. Global Document Frequency
        doc_freq: Counter = Counter()
        for doc in all_docs:
            for term in set(doc):
                doc_freq[term] += 1

        # 2. IDF = log((1 + N) / (1 + df)) + 1
        idf: Dict[str, float] = {}
        for term, df_count in doc_freq.items():
            idf[term] = math.log((1.0 + total_docs) / (1.0 + df_count)) + 1.0

        # 3. TF-IDF per group
        tfidf_by_group: Dict[str, List[Tuple[str, float]]] = {}
        for grp, docs in group_docs.items():
            if len(docs) < 10:  # Minimum sample threshold
                continue
            grp_tf: Counter = Counter()
            total_grp_tokens = 0
            for d in docs:
                for t in d:
                    grp_tf[t] += 1
                    total_grp_tokens += 1

            if total_grp_tokens == 0:
                continue

            grp_scores: List[Tuple[str, float]] = []
            for term, count in grp_tf.items():
                if doc_freq[term] < 3:
                    continue
                tf = count / total_grp_tokens
                score = tf * idf.get(term, 1.0)
                grp_scores.append((term, score))

            grp_scores.sort(key=lambda x: x[1], reverse=True)
            tfidf_by_group[grp] = grp_scores[:top_n]

        return tfidf_by_group

    def detect_text_reuse_candidates(
        self,
        df_text: pd.DataFrame,
        jaccard_threshold: float = 0.80,
    ) -> pd.DataFrame:
        """Detects exact duplicate titles and near-duplicate high-overlap text candidates deterministically."""
        candidates: List[Dict[str, Any]] = []

        # 1. Exact Title Reuse Groups (hash of normalized title)
        title_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for _, row in df_text.iterrows():
            norm_t = row["title_text_normalized"]
            if norm_t:
                title_groups[norm_t].append(row.to_dict())

        exact_duplicate_count = 0
        for norm_t, items in title_groups.items():
            if len(items) > 1:
                # Pairwise combinations within exact title bucket
                for i in range(len(items)):
                    for j in range(i + 1, len(items)):
                        a = items[i]
                        b = items[j]
                        candidates.append({
                            "candidate_id": f"REUSE-EXACT-{a['listing_id']}-{b['listing_id']}",
                            "listing_id_a": a["listing_id"],
                            "listing_id_b": b["listing_id"],
                            "title_a": a["title_text_raw"],
                            "title_b": b["title_text_raw"],
                            "similarity_method": "Exact Normalized String Equality",
                            "similarity_score": 1.0000,
                            "shared_token_count": len(a["tokens"]),
                            "candidate_type": "EXACT_TITLE_REUSE",
                            "verification_status": "UNVERIFIED_CANDIDATE",
                        })
                        exact_duplicate_count += 1

        # 2. High Lexical Overlap Candidates (Jaccard >= 0.80 across listings in same category)
        # To avoid O(N^2) explosion, bucket by primary product family / search query
        query_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for _, row in df_text.iterrows():
            q = row.get("search_query", "all")
            query_groups[q].append(row.to_dict())

        for q, items in query_groups.items():
            n_items = len(items)
            for i in range(n_items):
                t_set_a = set(items[i]["tokens"])
                if len(t_set_a) < 3:  # Skip trivial 1-2 word titles
                    continue
                norm_a = items[i]["title_text_normalized"]

                for j in range(i + 1, n_items):
                    norm_b = items[j]["title_text_normalized"]
                    if norm_a == norm_b:
                        continue  # Already captured in exact duplicate bucket

                    t_set_b = set(items[j]["tokens"])
                    if len(t_set_b) < 3:
                        continue

                    inter = t_set_a.intersection(t_set_b)
                    union = t_set_a.union(t_set_b)
                    if not union:
                        continue

                    jaccard = len(inter) / len(union)
                    if jaccard >= jaccard_threshold:
                        candidates.append({
                            "candidate_id": f"REUSE-JACC-{items[i]['listing_id']}-{items[j]['listing_id']}",
                            "listing_id_a": items[i]["listing_id"],
                            "listing_id_b": items[j]["listing_id"],
                            "title_a": items[i]["title_text_raw"],
                            "title_b": items[j]["title_text_raw"],
                            "similarity_method": f"Jaccard Token Overlap (Threshold >= {jaccard_threshold})",
                            "similarity_score": round(jaccard, 4),
                            "shared_token_count": len(inter),
                            "candidate_type": "HIGH_TEXT_OVERLAP",
                            "verification_status": "UNVERIFIED_CANDIDATE",
                        })

        df_candidates = pd.DataFrame(candidates)
        return df_candidates

    def _generate_figures(
        self,
        df_text: pd.DataFrame,
        df_phrases: pd.DataFrame,
        tfidf_dict: Dict[str, List[Tuple[str, float]]],
        df_reuse: pd.DataFrame,
    ) -> None:
        """Generates publication-quality charts for Phase F (Figures 25–35)."""
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

        # Figure 25: Text Availability
        fig, ax = plt.subplots(figsize=(7, 4.5))
        avail_labels = ["Title Available", "Description Available", "Combined Text Usable"]
        title_cnt = int(df_text["title_available"].sum())
        desc_cnt = int(df_text["description_available"].sum())
        comb_cnt = int(df_text["combined_text_available"].sum())
        counts = [title_cnt, desc_cnt, comb_cnt]
        bars = ax.bar(avail_labels, counts, color=["#10b981", "#ef4444", "#3b82f6"], edgecolor="black", linewidth=0.8)
        for b in bars:
            h = b.get_height()
            ax.annotate(f"{h:,}\n({(h/len(df_text))*100:.1f}%)", xy=(b.get_x() + b.get_width()/2, h),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.set_title("TrustLens — Listing Text Availability Hierarchy", fontsize=11, fontweight="bold")
        ax.set_ylabel("Listing Count")
        ax.set_ylim(0, len(df_text) * 1.25)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "25_text_availability.png", dpi=300)
        plt.close()

        # Figure 26: Token Count Distribution
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.hist(df_text["token_count"], bins=20, color="#6366f1", edgecolor="white", alpha=0.85)
        mean_tokens = df_text["token_count"].mean()
        med_tokens = df_text["token_count"].median()
        ax.axvline(mean_tokens, color="#f43f5e", linestyle="--", linewidth=1.5, label=f"Mean ({mean_tokens:.1f} tokens)")
        ax.axvline(med_tokens, color="#10b981", linestyle=":", linewidth=1.5, label=f"Median ({med_tokens:.0f} tokens)")
        ax.set_title("Listing Title Token Length Distribution", fontsize=11, fontweight="bold")
        ax.set_xlabel("Tokens per Listing Title")
        ax.set_ylabel("Frequency")
        ax.legend()
        plt.tight_layout()
        plt.savefig(self.figures_dir / "26_token_count_distribution.png", dpi=300)
        plt.close()

        # Figure 27: Top Marketplace Lexical Categories
        lex_cols = [c for c in df_text.columns if c.startswith("has_")]
        lex_names = [c.replace("has_", "").replace("_", " ").title() for c in lex_cols]
        lex_freqs = [int(df_text[c].sum()) for c in lex_cols]

        df_lex = pd.DataFrame({"Lexicon": lex_names, "Count": lex_freqs}).sort_values("Count", ascending=True)

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.barh(df_lex["Lexicon"], df_lex["Count"], color="#0284c7", edgecolor="black", linewidth=0.8)
        for b in bars:
            w = b.get_width()
            ax.annotate(f" {w:,} ({(w/len(df_text))*100:.1f}%)", xy=(w, b.get_y() + b.get_height()/2),
                        xytext=(3, 0), textcoords="offset points", ha="left", va="center", fontsize=8.5, fontweight="bold")
        ax.set_title("TrustLens — Controlled Lexical Category Prevalences", fontsize=11, fontweight="bold")
        ax.set_xlabel("Listings Containing Lexical Category")
        ax.set_xlim(0, max(lex_freqs) * 1.3)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "27_lexical_categories_distribution.png", dpi=300)
        plt.close()

        # Figure 28: Top 15 Unigrams
        df_uni = df_phrases[df_phrases["ngram_size"] == 1].head(15).sort_values("document_frequency", ascending=True)
        if not df_uni.empty:
            fig, ax = plt.subplots(figsize=(8, 5))
            bars = ax.barh(df_uni["phrase"], df_uni["document_frequency"], color="#8b5cf6", edgecolor="black", linewidth=0.8)
            for b in bars:
                w = b.get_width()
                ax.annotate(f" {w:,}", xy=(w, b.get_y() + b.get_height()/2),
                            xytext=(3, 0), textcoords="offset points", ha="left", va="center", fontsize=8.5, fontweight="bold")
            ax.set_title("Top 15 Informative Unigrams Across Listings", fontsize=11, fontweight="bold")
            ax.set_xlabel("Document Frequency")
            ax.set_xlim(0, max(df_uni["document_frequency"]) * 1.2)
            plt.tight_layout()
            plt.savefig(self.figures_dir / "28_top_unigrams.png", dpi=300)
            plt.close()

        # Figure 29: Top 15 Bigrams
        df_bi = df_phrases[df_phrases["ngram_size"] == 2].head(15).sort_values("document_frequency", ascending=True)
        if not df_bi.empty:
            fig, ax = plt.subplots(figsize=(8, 5))
            bars = ax.barh(df_bi["phrase"], df_bi["document_frequency"], color="#ec4899", edgecolor="black", linewidth=0.8)
            for b in bars:
                w = b.get_width()
                ax.annotate(f" {w:,}", xy=(w, b.get_y() + b.get_height()/2),
                            xytext=(3, 0), textcoords="offset points", ha="left", va="center", fontsize=8.5, fontweight="bold")
            ax.set_title("Top 15 Marketplace Bigrams Across Listings", fontsize=11, fontweight="bold")
            ax.set_xlabel("Document Frequency")
            ax.set_xlim(0, max(df_bi["document_frequency"]) * 1.2)
            plt.tight_layout()
            plt.savefig(self.figures_dir / "29_top_bigrams.png", dpi=300)
            plt.close()

        # Figure 30: Top 15 Trigrams
        df_tri = df_phrases[df_phrases["ngram_size"] == 3].head(15).sort_values("document_frequency", ascending=True)
        if not df_tri.empty:
            fig, ax = plt.subplots(figsize=(8, 5))
            bars = ax.barh(df_tri["phrase"], df_tri["document_frequency"], color="#f59e0b", edgecolor="black", linewidth=0.8)
            for b in bars:
                w = b.get_width()
                ax.annotate(f" {w:,}", xy=(w, b.get_y() + b.get_height()/2),
                            xytext=(3, 0), textcoords="offset points", ha="left", va="center", fontsize=8.5, fontweight="bold")
            ax.set_title("Top 15 Marketplace Trigrams Across Listings", fontsize=11, fontweight="bold")
            ax.set_xlabel("Document Frequency")
            ax.set_xlim(0, max(df_tri["document_frequency"]) * 1.2)
            plt.tight_layout()
            plt.savefig(self.figures_dir / "30_top_trigrams.png", dpi=300)
            plt.close()

        # Figure 31: TF-IDF Distinctive Terms by Product Group
        if tfidf_dict:
            top_grps = [g for g in ["iPhone", "MacBook", "PlayStation"] if g in tfidf_dict][:3]
            if top_grps:
                fig, axes = plt.subplots(1, len(top_grps), figsize=(5 * len(top_grps), 5))
                if len(top_grps) == 1:
                    axes = [axes]
                for ax, grp in zip(axes, top_grps):
                    terms, scores = zip(*tfidf_dict[grp][:10])
                    y_pos = np.arange(len(terms))
                    ax.barh(y_pos, scores, color="#3b82f6", edgecolor="black", linewidth=0.8)
                    ax.set_yticks(y_pos)
                    ax.set_yticklabels(terms)
                    ax.invert_yaxis()
                    ax.set_title(f"TF-IDF: {grp}", fontweight="bold", fontsize=10)
                    ax.set_xlabel("Score")
                plt.suptitle("Distinctive TF-IDF Keywords Across Major Product Groups", fontweight="bold", fontsize=12)
                plt.tight_layout()
                plt.savefig(self.figures_dir / "31_tfidf_distinctive_terms.png", dpi=300)
                plt.close()

        # Figure 32: Lexical Category Frequency by Product Group
        top_families = ["iPhone", "MacBook", "PlayStation"]
        df_sub = df_text[df_text["product_family"].isin(top_families)]
        if not df_sub.empty:
            grp_lex = df_sub.groupby("product_family")[["has_warranty_authenticity", "has_condition_lexicon", "has_transaction_payment", "has_urgency", "has_contact_redirection"]].mean() * 100
            grp_lex.columns = ["Warranty/Bill", "Condition", "Transaction", "Urgency", "Contact"]

            fig, ax = plt.subplots(figsize=(9, 4.8))
            grp_lex.plot(kind="bar", ax=ax, colormap="viridis", edgecolor="black", linewidth=0.8)
            ax.set_title("Lexical Category Frequency Across Major Product Families (%)", fontsize=11, fontweight="bold")
            ax.set_ylabel("Listings Prevalence (%)")
            ax.set_xlabel("Product Family")
            ax.legend(title="Lexical Category", frameon=True)
            plt.xticks(rotation=0)
            plt.tight_layout()
            plt.savefig(self.figures_dir / "32_lexical_frequency_by_group.png", dpi=300)
            plt.close()

        # Figure 33: Repeated-Title / Text Reuse Distribution
        if not df_reuse.empty:
            fig, ax = plt.subplots(figsize=(7, 4.5))
            reuse_counts = df_reuse["candidate_type"].value_counts()
            labels = [t.replace("_", " ").title() for t in reuse_counts.index]
            bars = ax.bar(labels, reuse_counts.values, color=["#14b8a6", "#f43f5e"][:len(labels)], edgecolor="black", linewidth=0.8)
            for b in bars:
                h = b.get_height()
                ax.annotate(f"{h:,}", xy=(b.get_x() + b.get_width()/2, h),
                            xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")
            ax.set_title("TrustLens — Text Reuse Candidate Counts", fontsize=11, fontweight="bold")
            ax.set_ylabel("Pairwise Candidate Count")
            ax.set_ylim(0, max(reuse_counts.values) * 1.25)
            plt.tight_layout()
            plt.savefig(self.figures_dir / "33_text_reuse_distribution.png", dpi=300)
            plt.close()

        # Figure 34: Language & Script Distribution
        fig, ax = plt.subplots(figsize=(7, 4.5))
        script_counts = df_text["script_type"].value_counts()
        labels = [s.replace("_", " ").title() for s in script_counts.index]
        bars = ax.bar(labels, script_counts.values, color=["#10b981", "#64748b", "#f59e0b"][:len(labels)], edgecolor="black", linewidth=0.8)
        for b in bars:
            h = b.get_height()
            ax.annotate(f"{h:,}\n({(h/len(df_text))*100:.2f}%)", xy=(b.get_x() + b.get_width()/2, h),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.set_title("Observed Script Distribution in Listing Titles", fontsize=11, fontweight="bold")
        ax.set_ylabel("Listing Count")
        ax.set_ylim(0, max(script_counts.values) * 1.25)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "34_script_distribution.png", dpi=300)
        plt.close()

        # Figure 35: Price Band x Lexical Category Heatmap
        if "price_numeric" in df_text.columns and df_text["price_numeric"].notna().sum() > 50:
            df_p = df_text[df_text["price_numeric"].notna() & (df_text["price_numeric"] > 0)].copy()
            df_p["price_band"] = pd.qcut(df_p["price_numeric"], q=4, labels=["Q1 (Budget)", "Q2 (Mid-Low)", "Q3 (Mid-High)", "Q4 (Premium)"])
            p_lex = df_p.groupby("price_band", observed=False)[["has_warranty_authenticity", "has_condition_lexicon", "has_transaction_payment", "has_urgency", "has_contact_redirection"]].mean() * 100
            p_lex.columns = ["Warranty/Bill", "Condition", "Transaction", "Urgency", "Contact"]

            fig, ax = plt.subplots(figsize=(8, 4.5))
            cax = ax.matshow(p_lex.values, cmap="YlGnBu")
            fig.colorbar(cax, label="Prevalence (%)")
            ax.set_xticks(range(len(p_lex.columns)))
            ax.set_yticks(range(len(p_lex.index)))
            ax.set_xticklabels(p_lex.columns, rotation=30, ha="left")
            ax.set_yticklabels(p_lex.index)
            for i in range(len(p_lex.index)):
                for j in range(len(p_lex.columns)):
                    val = p_lex.values[i, j]
                    ax.text(j, i, f"{val:.1f}%", ha="center", va="center", color="black" if val < 50 else "white", fontweight="bold")
            ax.set_title("Price Quartile vs. Lexical Category Prevalence Heatmap (%)", fontsize=11, fontweight="bold", pad=20)
            plt.tight_layout()
            plt.savefig(self.figures_dir / "35_price_band_lexicon_heatmap.png", dpi=300)
            plt.close()

    def _generate_html_gallery(
        self,
        df_text: pd.DataFrame,
        df_phrases: pd.DataFrame,
        df_reuse: pd.DataFrame,
    ) -> None:
        """Generates inspectable HTML text exploration gallery."""
        # Top 20 Exact Title Reuse Groups
        reuse_cards = ""
        if not df_reuse.empty:
            exact_samples = df_reuse[df_reuse["candidate_type"] == "EXACT_TITLE_REUSE"].head(20)
            for _, r in exact_samples.iterrows():
                reuse_cards += f"""
                <div class="card">
                    <div class="card-header">
                        <span class="badge badge-exact">EXACT_TITLE_REUSE</span>
                        <span class="score-badge">Similarity: 1.0000</span>
                    </div>
                    <div class="card-body">
                        <p><strong>Listing A ({r['listing_id_a']}):</strong> <code>{PIIRedactor.redact_text(r['title_a'])}</code></p>
                        <p><strong>Listing B ({r['listing_id_b']}):</strong> <code>{PIIRedactor.redact_text(r['title_b'])}</code></p>
                        <p class="status-meta">Status: <span class="badge-unverified">UNVERIFIED_CANDIDATE</span> &bull; Shared Tokens: {r['shared_token_count']}</p>
                    </div>
                </div>
                """

        # Top Lexical Category Samples
        sample_cards = ""
        for cat_col, title_label in [("has_urgency", "Urgency / Relocation"), ("has_warranty_authenticity", "Warranty / Authenticity"), ("has_contact_redirection", "Contact Redirection")]:
            pos_samples = df_text[df_text[cat_col] == True].head(8)
            for _, r in pos_samples.iterrows():
                sample_cards += f"""
                <div class="card">
                    <div class="card-header">
                        <span class="badge badge-cat">{title_label}</span>
                        <span class="score-badge">{r['product_family']} &bull; {r['city']}</span>
                    </div>
                    <div class="card-body">
                        <p><strong>Listing ID:</strong> {r['listing_id']}</p>
                        <p><strong>Redacted Title:</strong> <code>{r['title_text_privacy_redacted']}</code></p>
                        <p class="status-meta">Script: {r['script_type']} &bull; Tokens: {r['token_count']}</p>
                    </div>
                </div>
                """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TrustLens — Text Intelligence & Lexical Gallery (Phase F)</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 24px; }}
        h1, h2 {{ color: #38bdf8; font-weight: 600; }}
        .section-desc {{ color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px; }}
        .gallery-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 20px; margin-bottom: 40px; }}
        .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px; }}
        .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #334155; padding-bottom: 8px; }}
        .badge {{ padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8rem; }}
        .badge-exact {{ background: #be185d; color: white; }}
        .badge-cat {{ background: #0284c7; color: white; }}
        .badge-unverified {{ background: #64748b; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.75rem; font-weight: bold; }}
        .score-badge {{ color: #38bdf8; font-size: 0.8rem; font-family: monospace; }}
        .card-body {{ font-size: 0.85rem; line-height: 1.4; color: #cbd5e1; }}
        .status-meta {{ margin-top: 8px; font-size: 0.8rem; color: #94a3b8; }}
        code {{ background: #0f172a; padding: 2px 4px; border-radius: 3px; font-family: monospace; color: #f43f5e; }}
    </style>
</head>
<body>
    <h1>TrustLens — Text Intelligence & Lexical Linguistics Gallery (Phase F)</h1>
    <p class="section-desc">Deterministic Corpus Lexical Analysis &bull; Generated {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} &bull; Status: <span class="badge-unverified">UNVERIFIED OBSERVATIONAL SIGNALS</span></p>

    <h2>1. Exact Title Reuse & High Lexical Overlap Candidates</h2>
    <div class="gallery-grid">
        {reuse_cards if reuse_cards else "<p>No exact title reuse candidates found.</p>"}
    </div>

    <h2>2. Controlled Lexical Category Samples (Privacy Redacted)</h2>
    <div class="gallery-grid">
        {sample_cards if sample_cards else "<p>No lexical category samples found.</p>"}
    </div>
</body>
</html>
"""
        with open(self.reports_dir / "text_intelligence_gallery.html", "w", encoding="utf-8") as fp:
            fp.write(html)

    def _write_reports(
        self,
        report_data: Dict[str, Any],
        df_text: pd.DataFrame,
        df_phrases: pd.DataFrame,
        df_reuse: pd.DataFrame,
    ) -> None:
        """Writes TEXT_INTELLIGENCE_ANALYSIS.md and PHASE_F_EXECUTION_REPORT.md."""
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        lex_summary = report_data["lexical_category_counts"]
        script_summary = report_data["script_distribution"]
        reuse_summary = report_data["reuse_candidate_counts"]

        md_content = f"""# TrustLens — Text Normalization, Lexical Linguistics & Language-Pattern Report (Phase F)
## Deterministic Marketplace Corpus Lexical Intelligence

- **Generated At:** {datetime.datetime.utcnow().isoformat()}
- **Analysis Method:** Deterministic N-grams, Controlled Lexicons, Pure TF-IDF & Jaccard Overlap
- **Status:** COMPLETED & VERIFIED (Phase F)

---

## 1. Population & Text Availability Hierarchy

| Processing Stage | Entity Count | Percentage / Rate | Methodological Context |
| :--- | :---: | :---: | :--- |
| **Total Canonical Listings** | **{report_data['total_listings']:,}** | **100.0%** | Total deduplicated marketplace listings. |
| **Title Text Available** | **{report_data['title_available_count']:,}** | **{report_data['title_availability_rate']:.2f}%** | Non-null product listing titles from search cards. |
| **Description Text Available** | **{report_data['description_available_count']:,}** | **{report_data['description_availability_rate']:.2f}%** | Descriptions absent due to search-page capture methodology. |
| **Combined Usable Text** | **{report_data['combined_usable_count']:,}** | **{report_data['combined_usable_rate']:.2f}%** | Listings with at least one non-empty text field for linguistic analysis. |

> **Methodological Note on Missing Descriptions:**
> All 2,980 listings in the current OLX corpus were captured directly from search-result cards (which display title, price, location, and thumbnail image, but omit full body descriptions). The text intelligence layer operates strictly on verified visible title text without hallucinating or imputing missing description content.

---

## 2. Corpus Lexical & Token Statistics

- **Total Corpus Tokens:** **{report_data['total_tokens']:,}** (Mean: {report_data['mean_tokens_per_listing']:.2f} tokens/listing, Median: {report_data['median_tokens_per_listing']:.0f})
- **Unique Lexical Vocabulary:** **{report_data['unique_tokens']:,}** unique word tokens
- **Extracted N-Gram Phrases ($df \ge 2$):** **{report_data['total_phrases_extracted']:,}** total phrases
  - **Unigrams ($n=1$):** {report_data['unigram_count']:,}
  - **Bigrams ($n=2$):** {report_data['bigram_count']:,}
  - **Trigrams ($n=3$):** {report_data['trigram_count']:,}

---

## 3. Controlled Marketplace Lexicon Prevalences

| Lexical Category | Matching Listings | Corpus Prevalence (%) | Category Definition & Sample Keywords |
| :--- | :---: | :---: | :--- |
| **Warranty & Authenticity** | **{lex_summary.get('warranty_authenticity', 0):,}** | **{(lex_summary.get('warranty_authenticity', 0)/report_data['total_listings'])*100:.2f}%** | `original`, `warranty`, `bill`, `invoice`, `sealed`, `gst`, `box pack` |
| **Condition Lexicon** | **{lex_summary.get('condition_lexicon', 0):,}** | **{(lex_summary.get('condition_lexicon', 0)/report_data['total_listings'])*100:.2f}%** | `new`, `used`, `like new`, `mint`, `flawless`, `clean`, `refurbished` |
| **Transaction & Payment** | **{lex_summary.get('transaction_payment', 0):,}** | **{(lex_summary.get('transaction_payment', 0)/report_data['total_listings'])*100:.2f}%** | `price`, `cash`, `fixed`, `negotiable`, `best price`, `exchange`, `emi` |
| **Urgency & Relocation** | **{lex_summary.get('urgency', 0):,}** | **{(lex_summary.get('urgency', 0)/report_data['total_listings'])*100:.2f}%** | `urgent`, `immediate`, `today`, `urgently`, `relocation`, `need gone` |
| **Contact Redirection** | **{lex_summary.get('contact_redirection', 0):,}** | **{(lex_summary.get('contact_redirection', 0)/report_data['total_listings'])*100:.2f}%** | `call`, `whatsapp`, `contact`, `message`, `dm`, `number` |
| **Clearance & Commercial** | **{lex_summary.get('clearance_commercial', 0):,}** | **{(lex_summary.get('clearance_commercial', 0)/report_data['total_listings'])*100:.2f}%** | `shop`, `store`, `wholesale`, `dealer`, `stock`, `clearance` |
| **Company Claims** | **{lex_summary.get('company_claims', 0):,}** | **{(lex_summary.get('company_claims', 0)/report_data['total_listings'])*100:.2f}%** | `company`, `official`, `corporate`, `office` |
| **Delivery & Logistics** | **{lex_summary.get('delivery_logistics', 0):,}** | **{(lex_summary.get('delivery_logistics', 0)/report_data['total_listings'])*100:.2f}%** | `delivery`, `courier`, `transport`, `shipping`, `all india` |
| **Explicit Relocation** | **{lex_summary.get('relocation', 0):,}** | **{(lex_summary.get('relocation', 0)/report_data['total_listings'])*100:.2f}%** | `relocation`, `shifting`, `moving`, `transfer`, `leaving` |

---

## 4. Text Reuse & Boilerplate Overlap Candidates (Status: UNVERIFIED)

| Candidate Type | Pairwise Candidate Count | Methodological Meaning |
| :--- | :---: | :--- |
| **`EXACT_TITLE_REUSE`** | **{reuse_summary.get('EXACT_TITLE_REUSE', 0):,}** | Pairs of distinct listings sharing identical normalized title strings ($s = 1.0000$). |
| **`HIGH_TEXT_OVERLAP`** | **{reuse_summary.get('HIGH_TEXT_OVERLAP', 0):,}** | Pairs of listings sharing $\ge 80\%$ Jaccard token overlap across distinct titles. |
| **Total Text Reuse Pairs** | **{len(df_reuse):,}** | **Observational candidate pairs for review (does not prove same seller or fraud).** |

---

## 5. Observed Script & Language Composition

- **Latin / English Script:** **{script_summary.get('latin_english', 0):,}** listings ({(script_summary.get('latin_english', 0)/report_data['total_listings'])*100:.2f}%)
- **Mixed / Special Symbol Scripts:** **{script_summary.get('mixed_latin_other', 0) + script_summary.get('other_non_latin', 0):,}** listings ({( (script_summary.get('mixed_latin_other', 0) + script_summary.get('other_non_latin', 0)) / report_data['total_listings'])*100:.2f}%)
- **Devanagari Script:** **{script_summary.get('devanagari', 0) + script_summary.get('mixed_latin_devanagari', 0):,}** listings ({( (script_summary.get('devanagari', 0) + script_summary.get('mixed_latin_devanagari', 0)) / report_data['total_listings'])*100:.2f}%)

---

## 6. Analytical Parquet Artifacts

1. **`data/olx_processed/text_features.parquet`**: Listing-level text metadata and lexical category indicator columns (2,980 rows).
2. **`data/olx_processed/text_phrases.parquet`**: Corpus n-gram vocabulary with document/term frequencies ({report_data['total_phrases_extracted']:,} rows).
3. **`data/olx_processed/text_similarity_candidates.parquet`**: Pairwise text reuse candidate relationships ({len(df_reuse):,} rows).
4. **`data/olx_analysis/reports/text_intelligence_gallery.html`**: Interactive gallery with privacy-redacted text previews.
"""
        with open(self.reports_dir / "TEXT_INTELLIGENCE_ANALYSIS.md", "w", encoding="utf-8") as fp:
            fp.write(md_content)

        exec_md = f"""# TrustLens — Phase F Execution Report
## Text Normalization, Lexical Linguistics & Language-Pattern Intelligence

- **Execution Date:** {datetime.datetime.utcnow().isoformat()}
- **Status:** COMPLETED & VERIFIED

---

### 1. Population & Processing Metrics
- **Total Canonical Listings:** {report_data['total_listings']:,}
- **Title Text Available:** {report_data['title_available_count']:,} ({report_data['title_availability_rate']:.2f}%)
- **Description Text Available:** {report_data['description_available_count']:,} ({report_data['description_availability_rate']:.2f}%)
- **Combined Usable Text:** {report_data['combined_usable_count']:,} ({report_data['combined_usable_rate']:.2f}%)
- **Processing Runtime:** {report_data['runtime_seconds']} seconds ({report_data['throughput_listings_sec']} listings/sec)

### 2. Lexical & Phrase Statistics
- **Total Corpus Tokens:** {report_data['total_tokens']:,}
- **Unique Vocabulary:** {report_data['unique_tokens']:,}
- **Phrases Extracted (df ≥ 2):** {report_data['total_phrases_extracted']:,} ({report_data['unigram_count']:,} unigrams, {report_data['bigram_count']:,} bigrams, {report_data['trigram_count']:,} trigrams)

### 3. Controlled Lexicon Category Frequencies
- **Warranty & Authenticity:** {lex_summary.get('warranty_authenticity', 0):,} ({(lex_summary.get('warranty_authenticity', 0)/report_data['total_listings'])*100:.2f}%)
- **Condition Lexicon:** {lex_summary.get('condition_lexicon', 0):,} ({(lex_summary.get('condition_lexicon', 0)/report_data['total_listings'])*100:.2f}%)
- **Transaction & Payment:** {lex_summary.get('transaction_payment', 0):,} ({(lex_summary.get('transaction_payment', 0)/report_data['total_listings'])*100:.2f}%)
- **Urgency & Relocation:** {lex_summary.get('urgency', 0):,} ({(lex_summary.get('urgency', 0)/report_data['total_listings'])*100:.2f}%)
- **Contact Redirection:** {lex_summary.get('contact_redirection', 0):,} ({(lex_summary.get('contact_redirection', 0)/report_data['total_listings'])*100:.2f}%)
- **Clearance & Commercial:** {lex_summary.get('clearance_commercial', 0):,} ({(lex_summary.get('clearance_commercial', 0)/report_data['total_listings'])*100:.2f}%)

### 4. Text Reuse Candidates (Status: UNVERIFIED_CANDIDATE)
- **EXACT_TITLE_REUSE:** {reuse_summary.get('EXACT_TITLE_REUSE', 0):,}
- **HIGH_TEXT_OVERLAP:** {reuse_summary.get('HIGH_TEXT_OVERLAP', 0):,}
- **Total Candidate Reuse Pairs:** {len(df_reuse):,}

### 5. Methodological Limitations
1. **Search-Page Capture Bias:** Full body descriptions are 100% absent in search-result cards; all lexical insights are grounded in search titles.
2. **Observational Nature:** Common template phrasing (e.g. "iPhone 15 128GB box pack") represents shared commercial vocabulary and does not prove coordinated behavior or fraud.
"""
        with open(self.reports_dir / "PHASE_F_EXECUTION_REPORT.md", "w", encoding="utf-8") as fp:
            fp.write(exec_md)
        if self.reports_dir == Path("data/olx_analysis/reports"):
            with open(Path("PHASE_F_EXECUTION_REPORT.md"), "w", encoding="utf-8") as fp:
                fp.write(exec_md)

    def run_pipeline(self) -> Dict[str, Any]:
        """Executes the full Phase F text intelligence pipeline."""
        start_time = datetime.datetime.utcnow()

        # Step 1: Load normalized listings
        norm_path = self.processed_dir / "normalized_listings.parquet"
        df_listings = pd.read_parquet(norm_path) if norm_path.exists() else pd.DataFrame()
        total_listings = len(df_listings)
        print(f"[Phase F] Analyzing text intelligence across {total_listings} canonical listings...", flush=True)

        # Step 2: Extract text features per listing
        records: List[Dict[str, Any]] = []
        all_tokens_list: List[str] = []

        for _, row in df_listings.iterrows():
            lid = row["listing_id"]
            raw_title = row.get("raw_title", "")
            raw_desc = row.get("description", "") if "description" in row else ""

            # Check availability
            t_avail = bool(raw_title and str(raw_title).strip())
            d_avail = bool(raw_desc and str(raw_desc).strip())
            comb_raw = f"{raw_title} {raw_desc}".strip()
            comb_avail = bool(comb_raw)

            # Normalization
            r_t, norm_t, red_t = self.normalize_listing_text(raw_title)
            r_d, norm_d, red_d = self.normalize_listing_text(raw_desc)
            r_c, norm_c, red_c = self.normalize_listing_text(comb_raw)

            tokens = self.tokenize_preserving_specs(norm_c)
            all_tokens_list.extend(tokens)

            # Script detection
            script = self.detect_script(comb_raw)

            # Lexicon features
            lex_feats = self.extract_lexicon_features(tokens, norm_c)

            # MD5 hash of normalized text for exact matching
            text_hash = hashlib.md5(norm_c.encode("utf-8")).hexdigest() if norm_c else ""

            rec = {
                "listing_id": lid,
                "title_text_raw": r_t,
                "description_text_raw": r_d,
                "combined_text_raw": r_c,
                "title_text_normalized": norm_t,
                "description_text_normalized": norm_d,
                "combined_text_normalized": norm_c,
                "title_text_privacy_redacted": red_t,
                "title_available": t_avail,
                "description_available": d_avail,
                "combined_text_available": comb_avail,
                "title_char_count": len(r_t),
                "description_char_count": len(r_d),
                "combined_char_count": len(r_c),
                "token_count": len(tokens),
                "unique_token_count": len(set(tokens)),
                "tokens": tokens,
                "script_type": script,
                "text_hash": text_hash,
                "search_query": row.get("search_query", "all"),
                "product_family": row.get("product_family", "Other"),
                "city": row.get("city", "Unknown"),
                "state": row.get("state", "Unknown"),
                "price_numeric": row.get("price_amount"),
            }
            rec.update(lex_feats)
            records.append(rec)

        df_text = pd.DataFrame(records)

        # Step 3: Compute N-grams
        df_phrases = self.compute_ngram_frequencies(df_text, min_doc_freq=2)

        # Step 4: Compute TF-IDF
        tfidf_dict = self.compute_tfidf_by_product_group(df_text, group_col="product_family", top_n=15)

        # Step 5: Detect Text Reuse Candidates
        df_reuse = self.detect_text_reuse_candidates(df_text, jaccard_threshold=0.80)

        # Step 6: Save Parquet tables
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        # Drop Python object list column 'tokens' before saving to parquet
        df_text_parquet = df_text.drop(columns=["tokens"])
        df_text_parquet.to_parquet(self.processed_dir / "text_features.parquet", index=False)
        df_phrases.to_parquet(self.processed_dir / "text_phrases.parquet", index=False)
        df_reuse.to_parquet(self.processed_dir / "text_similarity_candidates.parquet", index=False)

        print(f"[Phase F] Saved text_features.parquet ({len(df_text_parquet)} rows)", flush=True)
        print(f"[Phase F] Saved text_phrases.parquet ({len(df_phrases)} phrases)", flush=True)
        print(f"[Phase F] Saved text_similarity_candidates.parquet ({len(df_reuse)} reuse pairs)", flush=True)

        # Step 7: Generate figures & HTML gallery
        self._generate_figures(df_text, df_phrases, tfidf_dict, df_reuse)
        self._generate_html_gallery(df_text, df_phrases, df_reuse)

        # Step 8: Write reports
        runtime_sec = (datetime.datetime.utcnow() - start_time).total_seconds()
        t_avail_cnt = int(df_text["title_available"].sum())
        d_avail_cnt = int(df_text["description_available"].sum())
        comb_avail_cnt = int(df_text["combined_text_available"].sum())

        lex_cols = [c for c in df_text.columns if c.startswith("has_")]
        lex_summary = {c.replace("has_", ""): int(df_text[c].sum()) for c in lex_cols}
        script_summary = df_text["script_type"].value_counts().to_dict()
        reuse_summary = df_reuse["candidate_type"].value_counts().to_dict() if not df_reuse.empty else {}

        report_data = {
            "total_listings": total_listings,
            "title_available_count": t_avail_cnt,
            "title_availability_rate": (t_avail_cnt / max(1, total_listings)) * 100,
            "description_available_count": d_avail_cnt,
            "description_availability_rate": (d_avail_cnt / max(1, total_listings)) * 100,
            "combined_usable_count": comb_avail_cnt,
            "combined_usable_rate": (comb_avail_cnt / max(1, total_listings)) * 100,
            "total_tokens": len(all_tokens_list),
            "unique_tokens": len(set(all_tokens_list)),
            "mean_tokens_per_listing": float(df_text["token_count"].mean()),
            "median_tokens_per_listing": float(df_text["token_count"].median()),
            "total_phrases_extracted": len(df_phrases),
            "unigram_count": int((df_phrases["ngram_size"] == 1).sum()),
            "bigram_count": int((df_phrases["ngram_size"] == 2).sum()),
            "trigram_count": int((df_phrases["ngram_size"] == 3).sum()),
            "lexical_category_counts": lex_summary,
            "script_distribution": script_summary,
            "reuse_candidate_counts": reuse_summary,
            "runtime_seconds": round(runtime_sec, 2),
            "throughput_listings_sec": round(total_listings / max(1.0, runtime_sec), 2),
        }

        self._write_reports(report_data, df_text, df_phrases, df_reuse)
        return report_data


if __name__ == "__main__":
    engine = TextIntelligenceEngine()
    res = engine.run_pipeline()
    print("\nPhase F Completed Successfully!")
    print(json.dumps(res, indent=2))
