# TrustLens — Phase J Feature Audit & Experimental Suitability Report

- **Audit Date:** 2026-09-25
- **Analyzed Features:** 137 features from Phase I feature store
- **Constant Features Excluded:** 16
- **Status:** AUDITED & VALIDATED

---

## Summary of Experimental Inclusion

- **J_PRICE Candidates:** 6 features
- **J_PRICE_TEXT Candidates:** 27 features
- **J_PRICE_IMAGE Candidates:** 36 features
- **J_FULL_MULTIMODAL Candidates:** 69 features

---

## Feature Classification Table

| Feature Name | Data Type | Missing Rate | Unique Values | Price Exp | Price+Text Exp | Price+Img Exp | Multimodal Exp | Classification / Exclusion Reason |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `listing_id` | `str` | 0.0% | 2980 | No | No | No | No | Identifier / URL / Freeform text string |
| `source_url` | `str` | 0.0% | 2980 | No | No | No | No | Identifier / URL / Freeform text string |
| `first_seen_at` | `str` | 0.0% | 5 | No | No | No | No | Identifier / URL / Freeform text string |
| `last_seen_at` | `str` | 0.0% | 5 | No | No | No | No | Identifier / URL / Freeform text string |
| `observation_count` | `int64` | 0.0% | 1 | No | No | No | No | Constant feature (zero variance) |
| `search_query` | `str` | 0.0% | 3 | No | No | No | No | Low-variance metadata or administrative container |
| `category_id` | `str` | 0.0% | 3 | No | No | No | No | Low-variance metadata or administrative container |
| `raw_title` | `str` | 0.0% | 2636 | No | No | No | No | High-cardinality non-numeric attribute |
| `normalized_title` | `str` | 0.0% | 2632 | No | No | No | No | High-cardinality non-numeric attribute |
| `location_raw` | `str` | 19.4% | 1235 | No | No | No | No | Identifier / URL / Freeform text string |
| `city` | `str` | 0.0% | 153 | No | No | No | No | Included in candidate experimental sets |
| `state` | `str` | 0.0% | 18 | No | No | No | No | Included in candidate experimental sets |
| `country` | `str` | 0.0% | 1 | No | No | No | No | Constant feature (zero variance) |
| `geography_confidence` | `str` | 0.0% | 3 | No | No | No | Yes | Included in candidate experimental sets |
| `price_available` | `bool` | 0.0% | 2 | No | No | No | No | Included in candidate experimental sets |
| `location_available` | `bool` | 0.0% | 2 | No | No | No | No | Included in candidate experimental sets |
| `description_available` | `bool` | 0.0% | 1 | No | No | No | No | Constant feature (zero variance) |
| `seller_available` | `bool` | 0.0% | 1 | No | No | No | No | Constant feature (zero variance) |
| `media_available` | `bool` | 0.0% | 2 | No | No | Yes | Yes | Included in candidate experimental sets |
| `ocr_available` | `bool` | 0.0% | 2 | No | No | Yes | Yes | Included in candidate experimental sets |
| `text_available` | `bool` | 0.0% | 1 | No | No | No | No | Constant feature (zero variance) |
| `visual_embedding_available` | `bool` | 0.0% | 2 | No | No | No | No | Included in candidate experimental sets |
| `ai_detector_available` | `bool` | 0.0% | 2 | No | No | Yes | Yes | Included in candidate experimental sets |
| `product_domain` | `str` | 0.0% | 3 | No | No | No | No | Included in candidate experimental sets |
| `product_category` | `str` | 0.0% | 6 | No | No | No | Yes | Included in candidate experimental sets |
| `brand` | `str` | 0.0% | 5 | No | No | No | Yes | Included in candidate experimental sets |
| `product_family` | `str` | 0.0% | 7 | No | No | No | Yes | Included in candidate experimental sets |
| `model` | `str` | 0.0% | 60 | No | No | No | No | Included in candidate experimental sets |
| `variant` | `str` | 46.9% | 10 | No | No | No | No | Included in candidate experimental sets |
| `generation` | `str` | 25.4% | 47 | No | No | No | No | Included in candidate experimental sets |
| `storage_gb` | `float64` | 54.8% | 9 | No | No | No | No | Included in candidate experimental sets |
| `ram_gb` | `float64` | 91.6% | 13 | No | No | No | No | Included in candidate experimental sets |
| `screen_size_inches` | `float64` | 96.2% | 10 | No | No | No | No | Included in candidate experimental sets |
| `battery_health_percent` | `float64` | 95.9% | 25 | No | No | No | No | Included in candidate experimental sets |
| `condition` | `str` | 0.0% | 6 | No | No | No | Yes | Included in candidate experimental sets |
| `condition_cues_str` | `str` | 0.0% | 204 | No | No | No | No | Identifier / URL / Freeform text string |
| `accessory_or_device` | `str` | 0.0% | 7 | No | No | No | Yes | Included in candidate experimental sets |
| `query_match_status` | `str` | 0.0% | 5 | No | No | No | No | Included in candidate experimental sets |
| `normalization_confidence` | `str` | 0.0% | 3 | No | No | No | No | Included in candidate experimental sets |
| `price_amount` | `float64` | 0.0% | 591 | Yes | Yes | Yes | Yes | Included in candidate experimental sets |
| `price_currency` | `str` | 0.0% | 1 | No | No | No | No | Constant feature (zero variance) |
| `price_status` | `str` | 0.0% | 2 | No | No | No | No | Low-variance metadata or administrative container |
| `price_valid` | `bool` | 0.0% | 2 | No | No | No | No | Included in candidate experimental sets |
| `comparable_product_group` | `str` | 21.0% | 43 | No | No | No | No | Included in candidate experimental sets |
| `group_median_price` | `float64` | 21.0% | 39 | No | No | No | No | Included in candidate experimental sets |
| `group_mean_price` | `float64` | 21.0% | 43 | No | No | No | No | Included in candidate experimental sets |
| `group_min_price` | `float64` | 21.0% | 35 | No | No | No | No | Included in candidate experimental sets |
| `group_max_price` | `float64` | 21.0% | 39 | No | No | No | No | Included in candidate experimental sets |
| `group_std_price` | `float64` | 21.0% | 43 | No | No | No | No | Included in candidate experimental sets |
| `group_iqr_price` | `float64` | 21.0% | 40 | No | No | No | No | Included in candidate experimental sets |
| `price_delta_from_group_median` | `float64` | 21.0% | 970 | Yes | Yes | Yes | Yes | Included in candidate experimental sets |
| `price_ratio_to_group_median` | `float64` | 21.0% | 970 | Yes | Yes | Yes | Yes | Included in candidate experimental sets |
| `price_percentile_in_group` | `float64` | 21.0% | 1015 | Yes | Yes | Yes | Yes | Included in candidate experimental sets |
| `price_below_35_pct_median_flag` | `boolean` | 21.0% | 3 | Yes | Yes | Yes | Yes | Included in candidate experimental sets |
| `price_below_50_pct_median_flag` | `boolean` | 21.0% | 3 | Yes | Yes | Yes | Yes | Included in candidate experimental sets |
| `media_count` | `int64` | 0.0% | 2 | No | No | Yes | Yes | Included in candidate experimental sets |
| `media_downloaded` | `bool` | 0.0% | 1 | No | No | No | No | Constant feature (zero variance) |
| `media_fingerprinted` | `bool` | 0.0% | 1 | No | No | No | No | Constant feature (zero variance) |
| `media_width` | `float64` | 23.5% | 4 | No | No | Yes | Yes | Included in candidate experimental sets |
| `media_height` | `float64` | 23.5% | 203 | No | No | Yes | Yes | Included in candidate experimental sets |
| `media_file_size_bytes` | `float64` | 23.5% | 1489 | No | No | Yes | Yes | Included in candidate experimental sets |
| `media_mime_type` | `str` | 23.5% | 2 | No | No | No | No | Included in candidate experimental sets |
| `exact_image_reuse_count` | `int64` | 0.0% | 5 | No | No | Yes | Yes | Included in candidate experimental sets |
| `perceptual_reuse_candidate_count` | `int64` | 0.0% | 6 | No | No | Yes | Yes | Included in candidate experimental sets |
| `visual_similarity_candidate_count` | `int64` | 0.0% | 6 | No | No | Yes | Yes | Included in candidate experimental sets |
| `max_visual_similarity_score` | `float64` | 45.0% | 1294 | No | No | Yes | Yes | Included in candidate experimental sets |
| `mean_visual_similarity_score` | `float64` | 45.0% | 1551 | No | No | Yes | Yes | Included in candidate experimental sets |
| `ocr_evaluated` | `bool` | 0.0% | 2 | No | No | No | No | Included in candidate experimental sets |
| `ocr_status` | `str` | 23.5% | 3 | No | No | No | No | Included in candidate experimental sets |
| `ocr_text_positive` | `bool` | 0.0% | 2 | No | No | Yes | Yes | Included in candidate experimental sets |
| `ocr_mean_confidence` | `float64` | 23.5% | 526 | No | No | Yes | Yes | Included in candidate experimental sets |
| `ocr_character_count` | `float64` | 23.5% | 75 | No | No | Yes | Yes | Included in candidate experimental sets |
| `ocr_token_count` | `float64` | 23.5% | 30 | No | No | Yes | Yes | Included in candidate experimental sets |
| `ocr_model_mention_count` | `int64` | 0.0% | 2 | No | No | Yes | Yes | Included in candidate experimental sets |
| `ocr_storage_mention_count` | `int64` | 0.0% | 2 | No | No | Yes | Yes | Included in candidate experimental sets |
| `ocr_condition_mention_count` | `int64` | 0.0% | 1 | No | No | No | No | Constant feature (zero variance) |
| `ocr_demo_cue_count` | `int64` | 0.0% | 2 | No | No | Yes | Yes | Included in candidate experimental sets |
| `model_mismatch_candidate_count` | `int64` | 0.0% | 2 | No | No | Yes | Yes | Included in candidate experimental sets |
| `storage_mismatch_candidate_count` | `int64` | 0.0% | 1 | No | No | No | No | Constant feature (zero variance) |
| `condition_mismatch_candidate_count` | `int64` | 0.0% | 1 | No | No | No | No | Constant feature (zero variance) |
| `demo_clue_count` | `int64` | 0.0% | 2 | No | No | Yes | Yes | Included in candidate experimental sets |
| `shared_image_claim_drift_count` | `int64` | 0.0% | 1 | No | No | No | No | Constant feature (zero variance) |
| `total_multimodal_inconsistency_count` | `int64` | 0.0% | 2 | No | No | Yes | Yes | Included in candidate experimental sets |
| `has_inconsistency_candidate` | `bool` | 0.0% | 2 | No | No | Yes | Yes | Included in candidate experimental sets |
| `title_char_count` | `int64` | 0.0% | 63 | No | Yes | No | Yes | Included in candidate experimental sets |
| `token_count` | `int64` | 0.0% | 18 | No | Yes | No | Yes | Included in candidate experimental sets |
| `unique_token_count` | `int64` | 0.0% | 16 | No | Yes | No | Yes | Included in candidate experimental sets |
| `description_char_count` | `int64` | 0.0% | 1 | No | No | No | No | Constant feature (zero variance) |
| `has_urgency` | `bool` | 0.0% | 2 | No | Yes | No | Yes | Included in candidate experimental sets |
| `urgency_term_count` | `int64` | 0.0% | 3 | No | Yes | No | Yes | Included in candidate experimental sets |
| `has_contact_redirection` | `bool` | 0.0% | 2 | No | Yes | No | Yes | Included in candidate experimental sets |
| `contact_redirection_term_count` | `int64` | 0.0% | 3 | No | Yes | No | Yes | Included in candidate experimental sets |
| `has_transaction_payment` | `bool` | 0.0% | 2 | No | Yes | No | Yes | Included in candidate experimental sets |
| `transaction_payment_term_count` | `int64` | 0.0% | 4 | No | Yes | No | Yes | Included in candidate experimental sets |
| `has_clearance_commercial` | `bool` | 0.0% | 2 | No | Yes | No | Yes | Included in candidate experimental sets |
| `clearance_commercial_term_count` | `int64` | 0.0% | 2 | No | Yes | No | Yes | Included in candidate experimental sets |
| `has_warranty_authenticity` | `bool` | 0.0% | 2 | No | Yes | No | Yes | Included in candidate experimental sets |
| `warranty_authenticity_term_count` | `int64` | 0.0% | 5 | No | Yes | No | Yes | Included in candidate experimental sets |
| `has_delivery_logistics` | `bool` | 0.0% | 2 | No | Yes | No | Yes | Included in candidate experimental sets |
| `delivery_logistics_term_count` | `int64` | 0.0% | 3 | No | Yes | No | Yes | Included in candidate experimental sets |
| `has_condition_lexicon` | `bool` | 0.0% | 2 | No | Yes | No | Yes | Included in candidate experimental sets |
| `condition_lexicon_term_count` | `int64` | 0.0% | 4 | No | Yes | No | Yes | Included in candidate experimental sets |
| `has_relocation` | `bool` | 0.0% | 1 | No | No | No | No | Constant feature (zero variance) |
| `relocation_term_count` | `int64` | 0.0% | 1 | No | No | No | No | Constant feature (zero variance) |
| `has_company_claims` | `bool` | 0.0% | 2 | No | Yes | No | Yes | Included in candidate experimental sets |
| `company_claims_term_count` | `int64` | 0.0% | 2 | No | Yes | No | Yes | Included in candidate experimental sets |
| `exact_title_reuse_count` | `int64` | 0.0% | 23 | No | Yes | No | Yes | Included in candidate experimental sets |
| `text_similarity_candidate_count` | `int64` | 0.0% | 23 | No | Yes | No | Yes | Included in candidate experimental sets |
| `c2pa_present` | `boolean` | 23.5% | 2 | No | No | No | No | Included in candidate experimental sets |
| `exif_present` | `boolean` | 23.5% | 2 | No | No | No | No | Included in candidate experimental sets |
| `camera_make` | `str` | 23.5% | 2 | No | No | No | No | Included in candidate experimental sets |
| `camera_model` | `str` | 23.5% | 2 | No | No | No | No | Included in candidate experimental sets |
| `gps_present` | `boolean` | 23.5% | 2 | No | No | No | No | Included in candidate experimental sets |
| `image_type` | `str` | 23.5% | 5 | No | No | Yes | Yes | Included in candidate experimental sets |
| `spectral_hf_ratio` | `float64` | 23.5% | 1893 | No | No | Yes | Yes | Included in candidate experimental sets |
| `colorfulness_index` | `float64` | 23.5% | 1895 | No | No | Yes | Yes | Included in candidate experimental sets |
| `forensic_assessment_status` | `str` | 23.5% | 4 | No | No | No | No | Included in candidate experimental sets |
| `ai_detector_evaluated` | `bool` | 0.0% | 2 | No | No | No | No | Included in candidate experimental sets |
| `detector_a_name` | `str` | 23.5% | 2 | No | No | No | No | Included in candidate experimental sets |
| `detector_a_score` | `float64` | 23.5% | 2113 | No | No | Yes | Yes | Included in candidate experimental sets |
| `detector_a_result` | `str` | 23.5% | 4 | No | No | No | No | Included in candidate experimental sets |
| `detector_b_name` | `str` | 23.5% | 2 | No | No | No | No | Included in candidate experimental sets |
| `detector_b_score` | `float64` | 23.5% | 2219 | No | No | Yes | Yes | Included in candidate experimental sets |
| `detector_b_result` | `str` | 23.5% | 4 | No | No | No | No | Included in candidate experimental sets |
| `detector_agreement` | `str` | 23.5% | 5 | No | No | No | No | Included in candidate experimental sets |
| `ai_generation_candidate_flag` | `bool` | 0.0% | 2 | No | No | Yes | Yes | Included in candidate experimental sets |
| `borderline_detector_flag` | `bool` | 0.0% | 2 | No | No | Yes | Yes | Included in candidate experimental sets |
| `detector_disagreement_flag` | `bool` | 0.0% | 1 | No | No | No | No | Constant feature (zero variance) |
| `relationship_degree` | `int64` | 0.0% | 25 | No | No | No | Yes | Included in candidate experimental sets |
| `unique_connected_listings` | `int64` | 0.0% | 25 | No | No | No | Yes | Included in candidate experimental sets |
| `distinct_cities_connected` | `int64` | 0.0% | 9 | No | No | No | Yes | Included in candidate experimental sets |
| `distinct_states_connected` | `int64` | 0.0% | 7 | No | No | No | Yes | Included in candidate experimental sets |
| `distinct_product_families_connected` | `int64` | 0.0% | 3 | No | No | No | No | Included in candidate experimental sets |
| `component_id` | `str` | 0.0% | 2133 | No | No | No | No | High-cardinality non-numeric attribute |
| `component_size` | `int64` | 0.0% | 19 | No | No | No | Yes | Included in candidate experimental sets |
| `is_singleton_listing` | `bool` | 0.0% | 2 | No | No | No | Yes | Included in candidate experimental sets |
| `shared_ocr_candidate_count` | `int64` | 0.0% | 2 | No | No | No | No | Included in candidate experimental sets |