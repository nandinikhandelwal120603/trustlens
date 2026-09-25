# TrustLens — Unified Feature Store Data Dictionary & Lineage

## Feature Store Schema Specification (Phase I)

- **Dataset Target:** `data/olx_processed/unified_features.parquet`
- **Canonical Population:** 2,980 listings (1 row = 1 canonical OLX listing)
- **Total Feature Count:** 137 features
- **Feature Breakdown:** 63 numeric | 34 binary | 40 categorical/metadata
- **Status:** FROZEN & DETERMINISTICALLY GENERATED

---

## Strict Interpretation Guardrails

1. **No Target Variables / Fraud Scores:** The feature store contains purely observational and structural attributes. Features such as `price_below_35_pct_median_flag`, `visual_similarity_candidate_count`, and `total_multimodal_inconsistency_count` are empirical observations, NOT fraud labels.
2. **Zero Seller Imputation:** Seller identity tokens remain unobserved in this capture. `seller_available` is false for all listings.
3. **Explicit Missingness:**
   - `0` indicates observed absence (e.g. 0 repeated images observed, 0 urgency keywords detected).
   - `NULL` indicates unobserved / unevaluated / unbenchmarked status (e.g. listings without media have NULL for image quality and AI detector scores; accessories have NULL for benchmarked device model price deltas).

---

## Feature Families Overview

| Feature Family | Columns | Source Phases | Description |
| :--- | :---: | :--- | :--- |
| **Family A: Listing & Coverage** | 23 | Phase A, F | Canonical identifiers, capture metadata, location, and explicit availability flags |
| **Family B: Product Normalization** | 16 | Phase B | Normalized taxonomy (category, brand, family, model, storage, condition) |
| **Family C: Price & Benchmarking** | 16 | Phase B | Raw price, validity, comparable group statistics, deltas, and discount flags |
| **Family D: Media & Visual Embeddings** | 12 | Phase C, D | Media counts, pixel dimensions, file size, exact reuse, and DINO similarity |
| **Family E: Multimodal OCR & Inconsistencies** | 17 | Phase E | OCR confidence, token counts, model mentions, and claim drift candidates |
| **Family F: Text Intelligence & Lexicon** | 24 | Phase F | Character/token counts, 8 behavioral keyword groups, title reuse counts |
| **Family G: Image Authenticity & Provenance** | 9 | Phase G | C2PA/EXIF status, image type (Photo/Screenshot), spectral HF, colorfulness |
| **Family H: AI Detector Observations** | 11 | Phase G.1 | ViT & Swin raw scores, agreement/disagreement, borderline flags |
| **Family I: Network & Graph Topology** | 9 | Phase H | Relationship degree, component ID, component size, cross-jurisdiction counts |
| **Total Features** | **137** | **Phases A–H** | **Unified Canonical Analytical Table** |

---

## Detailed Feature Dictionary

### Family A: Listing & Coverage

| Feature Name | Data Type | Null Count | Source Phase | Source File | Definition & Guardrails |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `listing_id` | `str` | 0 | Phase A | `listings.parquet` | Unique canonical listing identifier. Stable primary key. |
| `source_url` | `str` | 0 | Phase A | `listings.parquet` | Original OLX item page URL. |
| `first_seen_at` | `str` | 0 | Phase A | `listings.parquet` | First observed capture timestamp in UTC. |
| `last_seen_at` | `str` | 0 | Phase A | `listings.parquet` | Last observed capture timestamp in UTC. |
| `observation_count` | `int64` | 0 | Phase A | `listings.parquet` | Number of independent raw captures consolidating into this canonical listing. |
| `search_query` | `str` | 0 | Phase A | `listings.parquet` | Search keyword used when capturing this listing (e.g. 'iphone', 'macbook'). |
| `category_id` | `str` | 0 | Phase A | `listings.parquet` | OLX marketplace category identifier. |
| `raw_title` | `str` | 0 | Phase A | `listings.parquet` | Raw listing title as published on OLX. |
| `normalized_title` | `str` | 0 | Phase A | `listings.parquet` | Cleaned, whitespace-collapsed listing title. |
| `location_raw` | `str` | 579 | Phase A | `listings.parquet` | Raw location text scraped from listing card. |
| `city` | `str` | 0 | Phase A | `listings.parquet` | Normalized metropolitan city (e.g. 'Delhi', 'Bengaluru'). |
| `state` | `str` | 0 | Phase A | `listings.parquet` | Normalized state jurisdiction (e.g. 'Delhi', 'Karnataka'). |
| `country` | `str` | 0 | Phase A | `listings.parquet` | Country jurisdiction ('India'). |
| `geography_confidence` | `str` | 0 | Phase A | `listings.parquet` | Confidence tier of geographic resolution ('high', 'medium', 'unknown'). |
| `price_available` | `bool` | 0 | Phase A | `listings.parquet` | Boolean flag: true if price is non-null and valid (> 0). |
| `location_available` | `bool` | 0 | Phase A | `listings.parquet` | Boolean flag: true if city is resolved and non-unknown. |
| `description_available` | `bool` | 0 | Phase F | `text_features.parquet` | Boolean flag: true if full description text was captured. |
| `seller_available` | `bool` | 0 | Phase A | `listings.parquet` | Boolean flag: true if seller identity tokens were captured (false for all). |
| `media_available` | `bool` | 0 | Phase A | `listings.parquet` | Boolean flag: true if listing card contained at least 1 image reference. |
| `ocr_available` | `bool` | 0 | Phase E | `image_ocr.parquet` | Boolean flag: true if listing image was OCR-processed by Tesseract. |
| `text_available` | `bool` | 0 | Phase F | `text_features.parquet` | Boolean flag: true if title or description text was available. |
| `visual_embedding_available` | `bool` | 0 | Phase D | `deep_visual_relationships.parquet` | Boolean flag: true if listing participated in DINO visual similarity. |
| `ai_detector_available` | `bool` | 0 | Phase G.1 | `ai_detector_results.parquet` | Boolean flag: true if listing image was evaluated by ViT/Swin AI detectors. |
### Family B: Product Normalization

| Feature Name | Data Type | Null Count | Source Phase | Source File | Definition & Guardrails |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `product_domain` | `str` | 0 | Phase B | `normalized_listings.parquet` | High-level domain category ('Electronics'). |
| `product_category` | `str` | 0 | Phase B | `normalized_listings.parquet` | Resolved hardware category (e.g. 'Smartphone', 'Laptop'). |
| `brand` | `str` | 0 | Phase B | `normalized_listings.parquet` | Normalized manufacturer brand (e.g. 'Apple', 'Sony'). |
| `product_family` | `str` | 0 | Phase B | `normalized_listings.parquet` | Product product line (e.g. 'iPhone', 'MacBook', 'PlayStation'). |
| `model` | `str` | 0 | Phase B | `normalized_listings.parquet` | Normalized device model (e.g. 'iPhone 13', 'iPhone 15 Pro Max'). |
| `variant` | `str` | 1,397 | Phase B | `normalized_listings.parquet` | Device sub-variant (e.g. 'Pro', 'Pro Max', 'Plus'). |
| `generation` | `str` | 756 | Phase B | `normalized_listings.parquet` | Hardware generation identifier (e.g. '13', '14', '15'). |
| `storage_gb` | `float64` | 1,634 | Phase B | `normalized_listings.parquet` | Parsed onboard flash storage capacity in gigabytes. |
| `ram_gb` | `float64` | 2,729 | Phase B | `normalized_listings.parquet` | Parsed system RAM in gigabytes (primarily laptops). |
| `screen_size_inches` | `float64` | 2,867 | Phase B | `normalized_listings.parquet` | Parsed display diagonal size in inches. |
| `battery_health_percent` | `float64` | 2,859 | Phase B | `normalized_listings.parquet` | Parsed Apple battery maximum capacity health percentage. |
| `condition` | `str` | 0 | Phase B | `normalized_listings.parquet` | Normalized condition state ('used', 'new', 'refurbished', 'unknown'). |
| `condition_cues_str` | `str` | 0 | Phase B | `normalized_listings.parquet` | Exact textual condition cues extracted from title (e.g. 'sealed box'). |
| `accessory_or_device` | `str` | 0 | Phase B | `normalized_listings.parquet` | Classification: 'device' (complete hardware unit) vs 'accessory'. |
| `query_match_status` | `str` | 0 | Phase B | `normalized_listings.parquet` | Audit status comparing parsed model to search query intent. |
| `normalization_confidence` | `str` | 0 | Phase B | `normalized_listings.parquet` | Rule engine confidence tier ('high', 'medium', 'low', 'unknown'). |
### Family C: Price & Benchmarking

| Feature Name | Data Type | Null Count | Source Phase | Source File | Definition & Guardrails |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `price_amount` | `float64` | 1 | Phase B | `normalized_listings.parquet` | Numeric price amount in Indian Rupees (INR). |
| `price_currency` | `str` | 0 | Phase B | `normalized_listings.parquet` | Currency code ('INR'). |
| `price_status` | `str` | 0 | Phase B | `normalized_listings.parquet` | Price audit status ('valid', 'missing', 'zero', 'negative'). |
| `price_valid` | `bool` | 0 | Phase B | `normalized_listings.parquet` | Boolean flag: price is positive and non-null. |
| `comparable_product_group` | `str` | 626 | Phase B | `normalized_listings.parquet` | Benchmarked comparable model group name (requires N >= 5 devices). |
| `group_median_price` | `float64` | 626 | Phase B | `normalized_listings.parquet` | Median price of all valid device listings in comparable product group. |
| `group_mean_price` | `float64` | 626 | Phase B | `normalized_listings.parquet` | Arithmetic mean price in comparable product group. |
| `group_min_price` | `float64` | 626 | Phase B | `normalized_listings.parquet` | Minimum observed price in comparable product group. |
| `group_max_price` | `float64` | 626 | Phase B | `normalized_listings.parquet` | Maximum observed price in comparable product group. |
| `group_std_price` | `float64` | 626 | Phase B | `normalized_listings.parquet` | Standard deviation of prices in comparable product group. |
| `group_iqr_price` | `float64` | 626 | Phase B | `normalized_listings.parquet` | Interquartile range (Q3 - Q1) of prices in comparable product group. |
| `price_delta_from_group_median` | `float64` | 626 | Phase B | `normalized_listings.parquet` | Relative price deviation: (price - median) / median. |
| `price_ratio_to_group_median` | `float64` | 626 | Phase B | `normalized_listings.parquet` | Price ratio: price / group median price. |
| `price_percentile_in_group` | `float64` | 626 | Phase B | `normalized_listings.parquet` | Percentile rank of price within comparable product group [0, 100]. |
| `price_below_35_pct_median_flag` | `boolean` | 626 | Phase B | `normalized_listings.parquet` | Observational flag: price falls <= -35% below model group median. |
| `price_below_50_pct_median_flag` | `boolean` | 626 | Phase B | `normalized_listings.parquet` | Observational flag: price falls <= -50% below model group median. |
### Family D: Media & Visual Features

| Feature Name | Data Type | Null Count | Source Phase | Source File | Definition & Guardrails |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `media_count` | `int64` | 0 | Phase A | `listings.parquet` | Total number of images referenced in the listing media gallery. |
| `media_downloaded` | `bool` | 0 | Phase C | `fingerprints.parquet` | Boolean flag: primary image asset was successfully downloaded. |
| `media_fingerprinted` | `bool` | 0 | Phase C | `fingerprints.parquet` | Boolean flag: perceptual and cryptographic hashes were computed. |
| `media_width` | `float64` | 700 | Phase C | `fingerprints.parquet` | Image width in pixels. |
| `media_height` | `float64` | 700 | Phase C | `fingerprints.parquet` | Image height in pixels. |
| `media_file_size_bytes` | `float64` | 700 | Phase C | `fingerprints.parquet` | Image file size on disk in bytes. |
| `media_mime_type` | `str` | 700 | Phase C | `fingerprints.parquet` | Image MIME container type (e.g. 'image/webp', 'image/jpeg'). |
| `exact_image_reuse_count` | `int64` | 0 | Phase C / H | `relationship_features.parquet` | Number of listings sharing exact binary identical image (SHA-256). |
| `perceptual_reuse_candidate_count` | `int64` | 0 | Phase C / H | `relationship_features.parquet` | Number of listings sharing near-duplicate image (pHash distance <= 10). |
| `visual_similarity_candidate_count` | `int64` | 0 | Phase D / H | `relationship_features.parquet` | Number of listings with DINOv2 cosine similarity >= 0.70. |
| `max_visual_similarity_score` | `float64` | 1,342 | Phase D | `deep_visual_relationships.parquet` | Maximum DINOv2 cosine similarity observed to any other listing. |
| `mean_visual_similarity_score` | `float64` | 1,342 | Phase D | `deep_visual_relationships.parquet` | Mean DINOv2 cosine similarity across candidate visual neighbors. |
### Family E: Multimodal OCR & Inconsistencies

| Feature Name | Data Type | Null Count | Source Phase | Source File | Definition & Guardrails |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `ocr_evaluated` | `bool` | 0 | Phase E | `image_ocr.parquet` | Boolean flag: image was evaluated by local Tesseract OCR engine. |
| `ocr_status` | `str` | 700 | Phase E | `image_ocr.parquet` | OCR execution status ('SUCCESS', 'NO_TEXT', NULL). |
| `ocr_text_positive` | `bool` | 0 | Phase E | `image_ocr.parquet` | Boolean flag: OCR extracted at least 1 character of text. |
| `ocr_mean_confidence` | `float64` | 700 | Phase E | `image_ocr.parquet` | Mean word-level OCR confidence score [0, 100]. |
| `ocr_character_count` | `float64` | 700 | Phase E | `image_ocr.parquet` | Total alphanumeric character count extracted by OCR. |
| `ocr_token_count` | `float64` | 700 | Phase E | `image_ocr.parquet` | Total whitespace-delimited word token count extracted by OCR. |
| `ocr_model_mention_count` | `int64` | 0 | Phase E | `image_ocr.parquet` | Count of explicit device model strings detected in image text. |
| `ocr_storage_mention_count` | `int64` | 0 | Phase E | `image_ocr.parquet` | Count of explicit storage capacity strings detected in image text. |
| `ocr_condition_mention_count` | `int64` | 0 | Phase E | `image_ocr.parquet` | Count of condition cues detected in image text. |
| `ocr_demo_cue_count` | `int64` | 0 | Phase E | `image_ocr.parquet` | Count of demo/retail/activation lock clues detected in image text. |
| `model_mismatch_candidate_count` | `int64` | 0 | Phase E | `multimodal_inconsistencies.parquet` | Count of conflicting model assertions between text and image OCR. |
| `storage_mismatch_candidate_count` | `int64` | 0 | Phase E | `multimodal_inconsistencies.parquet` | Count of conflicting storage assertions between text and image OCR. |
| `condition_mismatch_candidate_count` | `int64` | 0 | Phase E | `multimodal_inconsistencies.parquet` | Count of conflicting condition assertions between text and image OCR. |
| `demo_clue_count` | `int64` | 0 | Phase E | `multimodal_inconsistencies.parquet` | Count of demo unit / retail kiosk visual indicators. |
| `shared_image_claim_drift_count` | `int64` | 0 | Phase E | `multimodal_inconsistencies.parquet` | Count of divergent product claims across listings sharing the same image. |
| `total_multimodal_inconsistency_count` | `int64` | 0 | Phase E | `multimodal_inconsistencies.parquet` | Sum of all unverified multimodal inconsistency candidates for listing. |
| `has_inconsistency_candidate` | `bool` | 0 | Phase E | `multimodal_inconsistencies.parquet` | Boolean flag: listing has >= 1 unverified inconsistency candidate. |
### Family F: Text Intelligence & Lexicon

| Feature Name | Data Type | Null Count | Source Phase | Source File | Definition & Guardrails |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `title_char_count` | `int64` | 0 | Phase F | `text_features.parquet` | Character length of normalized title string. |
| `token_count` | `int64` | 0 | Phase F | `text_features.parquet` | Word token count of normalized title string. |
| `unique_token_count` | `int64` | 0 | Phase F | `text_features.parquet` | Number of distinct vocabulary tokens in title. |
| `description_char_count` | `int64` | 0 | Phase F | `text_features.parquet` | Character length of listing description (0 if unavailable). |
| `has_urgency` | `bool` | 0 | Phase F | `text_features.parquet` | Boolean flag: title contains urgency terms ('urgent', 'today only', 'fast'). |
| `urgency_term_count` | `int64` | 0 | Phase F | `text_features.parquet` | Frequency of matched urgency vocabulary terms. |
| `has_contact_redirection` | `bool` | 0 | Phase F | `text_features.parquet` | Boolean flag: title requests off-platform contact ('call', 'whatsapp'). |
| `contact_redirection_term_count` | `int64` | 0 | Phase F | `text_features.parquet` | Frequency of contact redirection vocabulary terms. |
| `has_transaction_payment` | `bool` | 0 | Phase F | `text_features.parquet` | Boolean flag: title mentions payment methods ('cash', 'emi', 'gpay'). |
| `transaction_payment_term_count` | `int64` | 0 | Phase F | `text_features.parquet` | Frequency of payment vocabulary terms. |
| `has_clearance_commercial` | `bool` | 0 | Phase F | `text_features.parquet` | Boolean flag: title asserts commercial sale ('wholesale', 'lot', 'dealer'). |
| `clearance_commercial_term_count` | `int64` | 0 | Phase F | `text_features.parquet` | Frequency of commercial clearance terms. |
| `has_warranty_authenticity` | `bool` | 0 | Phase F | `text_features.parquet` | Boolean flag: title claims warranty / bill ('apple care', 'gst bill'). |
| `warranty_authenticity_term_count` | `int64` | 0 | Phase F | `text_features.parquet` | Frequency of warranty/authenticity terms. |
| `has_delivery_logistics` | `bool` | 0 | Phase F | `text_features.parquet` | Boolean flag: title mentions shipping / courier ('courier', 'cod', 'delivery'). |
| `delivery_logistics_term_count` | `int64` | 0 | Phase F | `text_features.parquet` | Frequency of shipping/delivery terms. |
| `has_condition_lexicon` | `bool` | 0 | Phase F | `text_features.parquet` | Boolean flag: title mentions condition descriptors ('mint', 'scratchless'). |
| `condition_lexicon_term_count` | `int64` | 0 | Phase F | `text_features.parquet` | Frequency of condition descriptors. |
| `has_relocation` | `bool` | 0 | Phase F | `text_features.parquet` | Boolean flag: title claims relocation / moving distress ('moving abroad'). |
| `relocation_term_count` | `int64` | 0 | Phase F | `text_features.parquet` | Frequency of relocation distress terms. |
| `has_company_claims` | `bool` | 0 | Phase F | `text_features.parquet` | Boolean flag: title claims company gift / corporate asset. |
| `company_claims_term_count` | `int64` | 0 | Phase F | `text_features.parquet` | Frequency of corporate claim terms. |
| `exact_title_reuse_count` | `int64` | 0 | Phase F / H | `relationship_features.parquet` | Number of other listings sharing the exact character-identical title. |
| `text_similarity_candidate_count` | `int64` | 0 | Phase F / H | `relationship_features.parquet` | Number of listings sharing high token Jaccard similarity (>= 0.75). |
### Family G: Image Authenticity & Provenance

| Feature Name | Data Type | Null Count | Source Phase | Source File | Definition & Guardrails |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `c2pa_present` | `boolean` | 700 | Phase G | `image_authenticity.parquet` | Boolean flag: C2PA provenance manifest container present (0 across dataset). |
| `exif_present` | `boolean` | 700 | Phase G | `image_authenticity.parquet` | Boolean flag: EXIF metadata present (0 across dataset due to WebP conversion). |
| `camera_make` | `str` | 700 | Phase G | `image_authenticity.parquet` | Hardware camera manufacturer extracted from EXIF (NULL). |
| `camera_model` | `str` | 700 | Phase G | `image_authenticity.parquet` | Hardware camera model extracted from EXIF (NULL). |
| `gps_present` | `boolean` | 700 | Phase G | `image_authenticity.parquet` | Boolean flag: GPS geolocation tags exposed in EXIF (0 across dataset). |
| `image_type` | `str` | 700 | Phase G | `image_authenticity.parquet` | Observational image classification ('PHOTO', 'SCREENSHOT', 'TEXT_HEAVY', 'DOCUMENT_LIKE'). |
| `spectral_hf_ratio` | `float64` | 700 | Phase G | `image_authenticity.parquet` | FFT high-frequency spectral energy ratio measuring camera sensor noise vs smoothness. |
| `colorfulness_index` | `float64` | 700 | Phase G | `image_authenticity.parquet` | Hasler-Süsstrunk perceptual color saturation index. |
| `forensic_assessment_status` | `str` | 700 | Phase G | `image_authenticity.parquet` | Statistical optical heuristic status ('REAL_IMAGE_CANDIDATE', 'BORDERLINE', 'NO_CONCLUSIVE_SIGNAL'). |
### Family H: AI Detector Observations

| Feature Name | Data Type | Null Count | Source Phase | Source File | Definition & Guardrails |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `ai_detector_evaluated` | `bool` | 0 | Phase G.1 | `ai_detector_results.parquet` | Boolean flag: listing image evaluated by dual ViT/Swin AI classifiers. |
| `detector_a_name` | `str` | 700 | Phase G.1 | `ai_detector_results.parquet` | Detector A model identifier ('ViT-Base'). |
| `detector_a_score` | `float64` | 700 | Phase G.1 | `ai_detector_results.parquet` | Raw Detector A probability score in [0.0, 1.0]. |
| `detector_a_result` | `str` | 700 | Phase G.1 | `ai_detector_results.parquet` | Detector A category ('AI_GENERATED_CANDIDATE', 'BORDERLINE', 'REAL_IMAGE'). |
| `detector_b_name` | `str` | 700 | Phase G.1 | `ai_detector_results.parquet` | Detector B model identifier ('Swin-Base'). |
| `detector_b_score` | `float64` | 700 | Phase G.1 | `ai_detector_results.parquet` | Raw Detector B probability score in [0.0, 1.0]. |
| `detector_b_result` | `str` | 700 | Phase G.1 | `ai_detector_results.parquet` | Detector B category ('AI_GENERATED_CANDIDATE', 'BORDERLINE', 'REAL_IMAGE'). |
| `detector_agreement` | `str` | 700 | Phase G.1 | `ai_detector_results.parquet` | Agreement status between Detector A and Detector B. |
| `ai_generation_candidate_flag` | `bool` | 0 | Phase G.1 | `ai_detector_results.parquet` | Boolean flag: both detectors independently crossed the 0.70 threshold. |
| `borderline_detector_flag` | `bool` | 0 | Phase G.1 | `ai_detector_results.parquet` | Boolean flag: either detector score falls in [0.30, 0.70]. |
| `detector_disagreement_flag` | `bool` | 0 | Phase G.1 | `ai_detector_results.parquet` | Boolean flag: one detector indicates AI (>=0.70) while the other indicates real (<=0.30). |
### Family I: Network & Graph Topology

| Feature Name | Data Type | Null Count | Source Phase | Source File | Definition & Guardrails |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `relationship_degree` | `int64` | 0 | Phase H | `relationship_features.parquet` | Total count of direct edges connected to listing in relationship graph. |
| `unique_connected_listings` | `int64` | 0 | Phase H | `relationship_features.parquet` | Count of distinct other listings directly connected through any evidence layer. |
| `distinct_cities_connected` | `int64` | 0 | Phase H | `relationship_features.parquet` | Number of distinct metropolitan cities represented among connected neighbors. |
| `distinct_states_connected` | `int64` | 0 | Phase H | `relationship_features.parquet` | Number of distinct states represented among connected neighbors. |
| `distinct_product_families_connected` | `int64` | 0 | Phase H | `relationship_features.parquet` | Number of distinct product lines represented among connected neighbors. |
| `component_id` | `str` | 0 | Phase H | `relationship_features.parquet` | Identifier of the connected component to which listing belongs (e.g. 'COMP-0001'). |
| `component_size` | `int64` | 0 | Phase H | `relationship_features.parquet` | Total number of listings in listing's connected component. |
| `is_singleton_listing` | `bool` | 0 | Phase H | `relationship_features.parquet` | Boolean flag: true if listing has 0 relationships to other listings. |
| `shared_ocr_candidate_count` | `int64` | 0 | Phase H | `relationship_features.parquet` | Number of other listings connected via distinctive shared OCR phrases. |