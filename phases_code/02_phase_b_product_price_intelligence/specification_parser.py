"""
TrustLens Marketplace Intelligence — Specification Parser (Phase B).
Extracts explicit hardware specifications (storage, RAM, battery health, chip, year, color)
strictly from visible text without guessing or hallucinating missing fields.
"""

import re
from typing import Any, Dict, Optional


class SpecificationParser:
    """Deterministic extractor of technical hardware specifications."""

    # RAM patterns with explicit 'RAM' keyword (e.g. 8GB RAM, 16 GB ram, 32gb ram)
    RAM_EXPLICIT_REGEX = re.compile(
        r"\b(4|6|8|12|16|18|24|32|36|48|64|128)\s*(?:gb)?\s*ram\b",
        re.IGNORECASE,
    )

    # Storage patterns with explicit 'SSD' or 'ROM' or 'Storage'
    STORAGE_EXPLICIT_REGEX = re.compile(
        r"\b(64|128|256|512)\s*(?:gb)?\s*(?:ssd|rom|storage)\b|\b(1|2)\s*(?:tb)?\s*(?:ssd|rom|storage)\b",
        re.IGNORECASE,
    )

    # Dual capacity pattern (e.g. 8GB 256GB, 8/256, 16GB 512GB, 8gb 128gb)
    DUAL_CAPACITY_REGEX = re.compile(
        r"\b(4|6|8|12|16|24|32)\s*(?:gb)?\s*[/ +,-]\s*(64|128|256|512)\s*(?:gb)?\b|\b(4|6|8|12|16|24|32)\s*(?:gb)?\s+(64|128|256|512)\s*gb\b",
        re.IGNORECASE,
    )

    # Terabyte storage (e.g. 1TB, 2 TB, 1 terabyte)
    TB_STORAGE_REGEX = re.compile(r"\b(1|2)\s*(?:tb|terabytes?)\b", re.IGNORECASE)

    # General Gigabyte pattern
    GENERAL_GB_REGEX = re.compile(r"\b(16|32|64|128|256|512)\s*(?:gb|gigabytes?)\b", re.IGNORECASE)

    # Battery Health (e.g. 100% battery health, 95% bh, 88 % battery)
    BATTERY_HEALTH_REGEX = re.compile(
        r"\b(\d{2,3})\s*%\s*(?:battery\s*health|battery|bh)\b|\b(?:battery\s*health|battery|bh)\s*[:=]?\s*(\d{2,3})\s*%\b",
        re.IGNORECASE,
    )

    # Year (e.g. 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026)
    YEAR_REGEX = re.compile(r"\b(201[5-9]|202[0-6])\b")

    # Chip / Generation (e.g. M1, M1 Pro, M1 Max, M2, M2 Pro, M2 Max, M3, M3 Pro, M3 Max, M4, i5, i7, i9)
    CHIP_REGEX = re.compile(
        r"\b(M1\s*(?:Pro|Max|Ultra)?|M2\s*(?:Pro|Max|Ultra)?|M3\s*(?:Pro|Max)?|M4\s*(?:Pro|Max)?|Intel\s*Core\s*i[3579]|Core\s*i[3579]|i[3579]\s*(?:th\s*gen)?)\b",
        re.IGNORECASE,
    )

    # Screen Size (e.g. 13", 13.3", 14", 15", 16", 13 inch, 14-inch)
    SCREEN_SIZE_REGEX = re.compile(
        r"\b(11|12|13|13\.3|13\.6|14|14\.2|15|15\.3|15\.6|16|16\.2|17)\s*(?:\"|''|inch(?:es)?|-inch)\b",
        re.IGNORECASE,
    )

    # Standard Colors
    COLOR_MAP = {
        "space gray": "Space Gray",
        "space grey": "Space Gray",
        "space black": "Space Black",
        "silver": "Silver",
        "midnight": "Midnight",
        "starlight": "Starlight",
        "natural titanium": "Natural Titanium",
        "desert titanium": "Desert Titanium",
        "black titanium": "Black Titanium",
        "white titanium": "White Titanium",
        "blue titanium": "Blue Titanium",
        "deep purple": "Deep Purple",
        "pacific blue": "Pacific Blue",
        "sierra blue": "Sierra Blue",
        "alpine green": "Alpine Green",
        "graphite": "Graphite",
        "gold": "Gold",
        "rose gold": "Rose Gold",
        "black": "Black",
        "white": "White",
        "red": "Red",
        "product red": "Product Red",
        "blue": "Blue",
        "green": "Green",
        "yellow": "Yellow",
        "pink": "Pink",
        "purple": "Purple",
        "cosmic red": "Cosmic Red",
        "midnight black": "Midnight Black",
        "starlight blue": "Starlight Blue",
        "galactic purple": "Galactic Purple",
        "nova pink": "Nova Pink",
        "volcanic red": "Volcanic Red",
    }

    @classmethod
    def parse_specs(cls, text: Optional[str]) -> Dict[str, Any]:
        """
        Parses text and extracts structured hardware specifications.
        """
        if not text or not text.strip():
            return {
                "storage_gb": None,
                "ram_gb": None,
                "screen_size_inches": None,
                "battery_health_percent": None,
                "year": None,
                "chip": None,
                "color": None,
            }

        clean = text.strip()
        storage_gb: Optional[int] = None
        ram_gb: Optional[int] = None
        screen_size_inches: Optional[float] = None
        battery_health_percent: Optional[int] = None
        year: Optional[int] = None
        chip: Optional[str] = None
        color: Optional[str] = None

        # 1. RAM & Storage Extraction
        # A. Check for explicit RAM (e.g. 32GB RAM)
        ram_explicit = cls.RAM_EXPLICIT_REGEX.search(clean)
        if ram_explicit:
            ram_gb = int(ram_explicit.group(1))

        # B. Check for explicit Storage (e.g. 1TB SSD or 512GB SSD)
        storage_explicit = cls.STORAGE_EXPLICIT_REGEX.search(clean)
        if storage_explicit:
            if storage_explicit.group(1):
                storage_gb = int(storage_explicit.group(1))
            elif storage_explicit.group(2):
                storage_gb = int(storage_explicit.group(2)) * 1024

        # C. Check for Dual Capacity Pattern (e.g. 8GB 256GB or 8/256)
        dual_match = cls.DUAL_CAPACITY_REGEX.search(clean)
        if dual_match:
            r_val = dual_match.group(1) or dual_match.group(3)
            s_val = dual_match.group(2) or dual_match.group(4)
            if r_val and not ram_gb:
                ram_gb = int(r_val)
            if s_val and not storage_gb:
                storage_gb = int(s_val)

        # D. Check for TB Storage (e.g. 1TB or 2TB)
        tb_match = cls.TB_STORAGE_REGEX.search(clean)
        if tb_match and not storage_gb:
            storage_gb = int(tb_match.group(1)) * 1024

        # E. General GB fallback if storage not yet identified
        if not storage_gb:
            gb_matches = cls.GENERAL_GB_REGEX.findall(clean)
            if gb_matches:
                # Find valid storage values (>= 64 or distinct from detected RAM)
                for gb_str in gb_matches:
                    val = int(gb_str)
                    if ram_gb and val == ram_gb:
                        continue
                    if val >= 64:
                        storage_gb = val
                        break
                    elif val in [16, 32] and not storage_gb and not ram_gb:
                        storage_gb = val

        # 2. Battery Health
        bh_match = cls.BATTERY_HEALTH_REGEX.search(clean)
        if bh_match:
            val = bh_match.group(1) or bh_match.group(2)
            if val:
                bh_int = int(val)
                if 50 <= bh_int <= 100:
                    battery_health_percent = bh_int

        # 3. Year
        yr_match = cls.YEAR_REGEX.search(clean)
        if yr_match:
            year = int(yr_match.group(1))

        # 4. Chip
        chip_match = cls.CHIP_REGEX.search(clean)
        if chip_match:
            chip_raw = chip_match.group(1).strip()
            chip_upper = chip_raw.upper()
            if "M1" in chip_upper:
                chip = "M1 Pro" if "PRO" in chip_upper else ("M1 Max" if "MAX" in chip_upper else "M1")
            elif "M2" in chip_upper:
                chip = "M2 Pro" if "PRO" in chip_upper else ("M2 Max" if "MAX" in chip_upper else "M2")
            elif "M3" in chip_upper:
                chip = "M3 Pro" if "PRO" in chip_upper else ("M3 Max" if "MAX" in chip_upper else "M3")
            elif "M4" in chip_upper:
                chip = "M4 Pro" if "PRO" in chip_upper else "M4"
            else:
                chip = chip_raw.title()

        # 5. Screen Size
        sz_match = cls.SCREEN_SIZE_REGEX.search(clean)
        if sz_match:
            try:
                screen_size_inches = float(sz_match.group(1))
            except ValueError:
                pass

        # 6. Color
        clean_lower = clean.lower()
        for color_key, standard_color in sorted(cls.COLOR_MAP.items(), key=lambda x: len(x[0]), reverse=True):
            if re.search(r"\b" + re.escape(color_key) + r"\b", clean_lower):
                color = standard_color
                break

        return {
            "storage_gb": storage_gb,
            "ram_gb": ram_gb,
            "screen_size_inches": screen_size_inches,
            "battery_health_percent": battery_health_percent,
            "year": year,
            "chip": chip,
            "color": color,
        }
