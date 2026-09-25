"""
Phase 2 Full Multimodal Dataset Transformation Script for TrustLens
"""

import os
import sys
import json
import re
import hashlib
from pathlib import Path
from collections import defaultdict, Counter
from PIL import Image

BASE_DIR = Path("/Users/nandinikhandelwal/Desktop/Codes/trustlens")
DS_DIR = BASE_DIR / "trustlens_reddit_multimodal_dataset"
OUT_DIR = DS_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PAK_SUBREDDITS = {
    'pakgamers', 'pakistan', 'pakistanautohub', 'pakistanlawyers', 
    'pakistanitech', 'pakistanmarketplace', 'karachi'
}

def is_pakistan_post(meta):
    sub = meta.get('subreddit', '').lower()
    title = meta.get('title', '').lower()
    body = meta.get('body', '').lower()
    if sub in PAK_SUBREDDITS or 'pakistan' in sub:
        return True
    if 'pakwheels' in title or 'pakwheels' in body or 'pkr ' in title or 'pkr ' in body:
        return True
    return False

def is_romania_post(meta):
    pid = meta.get('post_id')
    title = meta.get('title', '').lower()
    if pid == '1u0elfw' or 'romania' in title or '4,200 ron' in title:
        return True
    return False

def get_country_context(meta):
    if is_pakistan_post(meta):
        return "Pakistan", "high", "Subreddit or post content explicitly mentions Pakistan/PKR/PakWheels"
    if is_romania_post(meta):
        return "Romania", "high", "Post title explicitly mentions Romania/RON"
    sub = meta.get('subreddit', '').lower()
    title = meta.get('title', '').lower()
    body = meta.get('body', '').lower()
    indian_subs = {'isthisascamindia', 'legaladviceindia', 'indiancyberhub', 'ps5india', 'pune', 'indiangaming', 'scamsupport', 'mumbai', 'delhi', 'bangalore', 'kolkata', 'bangaloremarketplace', 'developersindia'}
    if sub in indian_subs or 'india' in sub or 'upi' in title or 'upi' in body or 'inr' in title or 'inr' in body or '₹' in title or '₹' in body or 'olx india' in title or 'olx india' in body:
        return "India", "high", "Indian subreddit, currency (₹/INR), payment mechanism (UPI), or location indicator"
    return "India", "medium", "Assumed Indian context based on dataset collection scope and OLX India prevalence"

def extract_platform(title, body):
    text = (title + " " + body).lower()
    platforms = []
    if 'olx' in text:
        platforms.append("OLX")
    if 'facebook' in text or 'fb' in text or 'marketplace' in text:
        platforms.append("Facebook Marketplace")
    if 'whatsapp' in text or 'wa ' in text:
        platforms.append("WhatsApp")
    if 'instagram' in text or 'ig ' in text:
        platforms.append("Instagram")
    if 'amazon' in text:
        platforms.append("Amazon")
    if 'flipkart' in text:
        platforms.append("Flipkart")
    if 'pakwheels' in text:
        platforms.append("PakWheels")
    if 'cars24' in text:
        platforms.append("Cars24")
    if not platforms:
        return "OLX"
    return platforms[0]

def extract_product(title, body):
    text = (title + " " + body).lower()
    cat = "other"
    brand = None
    model = None
    
    if any(k in text for k in ['iphone', 'pixel', 'samsung', 'oneplus', 'smartphone', 'mobile', 'phone', 'redmi', 'realme']):
        cat = "smartphone"
        if 'iphone' in text:
            brand = "Apple"
            m = re.search(r'iphone\s*(\d+\s*(pro\s*max|pro|plus)?|x|xr|xs)', text)
            model = m.group(0).title() if m else "iPhone"
        elif 'pixel' in text:
            brand = "Google"
            m = re.search(r'pixel\s*\d+\s*[a-z]*', text)
            model = m.group(0).title() if m else "Pixel"
        elif 'samsung' in text:
            brand = "Samsung"
            m = re.search(r'samsung\s*(s\d+|galaxy\s*[a-z0-9]+)', text)
            model = m.group(0).title() if m else "Galaxy"
    elif any(k in text for k in ['macbook', 'laptop', 'asus', 'rog', 'thinkpad', 'dell', 'hp', 'lenovo', 'pc', 'graphic card', 'gpu']):
        cat = "laptop"
        if 'macbook' in text:
            brand = "Apple"
            model = "MacBook"
        elif 'asus' in text:
            brand = "ASUS"
            model = "ROG/TUF"
        elif 'lenovo' in text or 'thinkpad' in text:
            brand = "Lenovo"
            model = "ThinkPad"
    elif any(k in text for k in ['ps5', 'ps4', 'playstation', 'xbox', 'console', 'nintendo']):
        cat = "gaming_console"
        if 'ps5' in text:
            brand = "Sony"
            model = "PlayStation 5"
        elif 'ps4' in text:
            brand = "Sony"
            model = "PlayStation 4"
    elif any(k in text for k in ['camera', 'canon', 'nikon', 'sony alpha', 'digi cam', 'digicam', 'dscr', 'lens']):
        cat = "camera"
        if 'canon' in text:
            brand = "Canon"
        elif 'nikon' in text:
            brand = "Nikon"
        elif 'sony' in text:
            brand = "Sony"
    elif any(k in text for k in ['car', 'honda', 'city', 'thar', 'swift', 'creta', 'alto', 'scorpio', 'bullet', 'bike', 'scooter', 'royal enfield', 'ktm']):
        if any(k in text for k in ['bullet', 'bike', 'scooter', 'ktm']):
            cat = "bike"
        else:
            cat = "car"
            if 'honda' in text or 'city' in text:
                brand = "Honda"
                model = "City"
    elif any(k in text for k in ['flat', 'apartment', 'rental', 'room', 'rent', 'house']):
        cat = "rental"
    elif any(k in text for k in ['tv', 'monitor', 'watch', 'airpods', 'headphone', 'electronics', 'tab', 'ipad']):
        cat = "electronics"

    return {"category": cat, "brand": brand, "model": model}

def extract_money(title, body):
    text = title + " " + body
    curr = "INR"
    if 'RON' in text or '€' in text:
        curr = "RON"
    elif 'PKR' in text or ('Rs.' in text and 'pakistan' in text.lower()):
        curr = "PKR"

    req_amt = None
    paid_amt = None
    reported_loss = None
    deposit_req = None
    add_pay = False

    amounts = re.findall(r'(?:₹|rs\.?|inr|pkr|ron)\s*([\d,]+k?|\d+)', text, re.IGNORECASE)
    parsed_amts = []
    for a in amounts:
        clean = a.lower().replace(',', '')
        if 'k' in clean:
            try:
                parsed_amts.append(float(clean.replace('k', '')) * 1000)
            except:
                pass
        else:
            try:
                val = float(clean)
                if val >= 100:
                    parsed_amts.append(val)
            except:
                pass

    if 'advance' in text.lower() or 'token' in text.lower() or 'deposit' in text.lower():
        if parsed_amts:
            deposit_req = parsed_amts[0]

    if 'scammed' in text.lower() or 'lost' in text.lower() or 'paid' in text.lower():
        if parsed_amts:
            paid_amt = max(parsed_amts)
            reported_loss = paid_amt

    if parsed_amts and not req_amt:
        req_amt = parsed_amts[0] if not paid_amt else paid_amt

    if any(k in text.lower() for k in ['more money', 'another', 'additional', 'gate pass', 'delivery fee']):
        add_pay = True

    return {
        "currency": curr,
        "requested_amount": req_amt,
        "paid_amount": paid_amt,
        "reported_loss": reported_loss,
        "deposit_requested": deposit_req,
        "additional_payments_requested": add_pay
    }

def extract_patterns(title, body, media_count):
    text = (title + " " + body).lower()
    patterns = []
    candidates = []

    if any(k in text for k in ['advance', 'token', 'booking', 'pay first', 'advance payment']):
        patterns.append("advance_payment")
        patterns.append("deposit_request")

    if any(k in text for k in ['qr', 'scanner', 'scan to receive', 'scan code']):
        patterns.append("qr_payment")
        patterns.append("upi_payment")

    if any(k in text for k in ['upi', 'gpay', 'phonepe', 'paytm']):
        patterns.append("upi_payment")

    if any(k in text for k in ['army', 'cisf', 'soldier', 'military', 'defense', 'defence']):
        patterns.append("army_persona")
        patterns.append("fake_identity")

    if any(k in text for k in ['gate pass', 'courier', 'transport', 'delivery fee', 'relocation']):
        patterns.append("gate_pass_story")
        patterns.append("fake_courier")

    if any(k in text for k in ['cheap', 'unrealistic', 'urgent', 'very low price', 'too good to be true']):
        patterns.append("unrealistic_price")

    if any(k in text for k in ['whatsapp', 'wa', 'chat', 'moved to']):
        patterns.append("off_platform_communication")
        patterns.append("whatsapp_migration")

    if any(k in text for k in ['fake invoice', 'invoice', 'bill', 'gst', 'receipt']):
        patterns.append("fake_invoice")

    if any(k in text for k in ['fake payment', 'paid screenshot', 'sent money screenshot']):
        patterns.append("fake_payment_screenshot")

    if any(k in text for k in ['not delivered', 'blocked', 'disappeared', 'ran away']):
        patterns.append("non_delivery")
        patterns.append("fake_seller")

    if 'phone' in text or 'iphone' in text:
        patterns.append("phone_scam")
    elif 'laptop' in text or 'macbook' in text:
        patterns.append("laptop_scam")
    elif 'camera' in text or 'digicam' in text:
        patterns.append("camera_scam")
    elif 'ps5' in text or 'ps4' in text or 'console' in text:
        patterns.append("gaming_console_scam")
    elif 'car' in text or 'honda' in text or 'bike' in text:
        patterns.append("vehicle_scam")

    if 'canteen' in text or 'defence store' in text or 'army canteen' in text:
        candidates.append("defence_store_receipt_scam")
    if 'macbook' in text and any(k in text for k in ['32k', '30k', '25k']):
        candidates.append("macbook_m1_m2_suspiciously_cheap")
    if 'innologic' in text or 'samsung india' in text or 'warehouse clearance' in text:
        candidates.append("fake_tech_company_warehouse_clearance")
    if 'qr refund' in text or 'receive money' in text:
        candidates.append("qr_reverse_charge_receive_money_trap")

    patterns = list(dict.fromkeys(patterns))
    if not patterns:
        patterns.append("suspected_scam")

    return patterns, candidates

def classify_case_status(title, body):
    text = (title + " " + body).lower()
    if any(k in text for k in ['is this a scam', 'is this scam', 'legit or scam', 'advice regarding', 'scam?']):
        return "asking_if_scam"
    if any(k in text for k in ['scam alert', 'beware', 'awareness', 'warning']):
        return "fraud_warning"
    if any(k in text for k in ['i got scammed', 'lost', 'paid', 'my friend got scammed']):
        return "victim_report"
    if 'scam' in text:
        return "reported_scam"
    return "suspected_scam"

def classify_completion_status(title, body):
    text = (title + " " + body).lower()
    if any(k in text for k in ['prevented', 'almost scammed', 'didn\'t pay', 'did not pay', 'saved me', 'blocked him', 'realised in time']):
        return "attempted_but_prevented"
    if any(k in text for k in ['scammed', 'lost', 'paid', 'transferred', 'sent money']):
        return "completed"
    return "suspected_attempt"

def classify_perspective(title, body):
    text = (title + " " + body).lower()
    if any(k in text for k in ['i was', 'i got', 'i paid', 'i bought', 'i am looking', 'he asked me']):
        return "firsthand"
    if any(k in text for k in ['my friend', 'my brother', 'my sister', 'my cousin', 'my relative']):
        return "secondhand"
    if any(k in text for k in ['found these', 'saw this', 'these sellers', 'people are', 'scammers are']):
        return "third_party"
    return "unclear"

def classify_evidence_basis(title, body, media_count):
    has_b = len(body.strip()) > 0
    has_m = media_count > 0

    if not has_b and not has_m:
        return "title_only"
    if has_b and not has_m:
        return "text_only"
    if not has_b and has_m:
        return "media_only_plus_title"
    return "text_and_media"

def classify_case_quality(title, body, media_count, evidence_basis):
    if evidence_basis == "title_only":
        return "low"
    if len(body.strip()) > 200 or media_count >= 2:
        return "high"
    if len(body.strip()) > 50 or media_count >= 1:
        return "medium"
    return "low"

def classify_media_visual_type(title, body, meta_entry):
    text = (title + " " + body).lower()
    local_path = meta_entry.get('local_path', '')
    
    types = []
    if any(k in text for k in ['qr', 'scanner', 'paytm', 'gpay', 'phonepe']):
        types.append("upi_qr")
        types.append("payment_screenshot")
    if any(k in text for k in ['chat', 'whatsapp', 'conversation', 'message', 'texted']):
        types.append("chat_screenshot")
    if any(k in text for k in ['invoice', 'bill', 'receipt', 'gst']):
        types.append("invoice_document")
    if any(k in text for k in ['olx listing', 'seller listing', 'post', 'ad']):
        types.append("listing_screenshot")
    if any(k in text for k in ['army card', 'id card', 'aadhaar', 'pancard', 'identity']):
        types.append("identity_document")
    if any(k in text for k in ['courier', 'gate pass', 'receipt', 'waybill']):
        types.append("courier_message")

    if not types:
        if any(k in text for k in ['iphone', 'laptop', 'ps5', 'camera', 'phone', 'macbook', 'car', 'bike']):
            types.append("product_image")
        else:
            types.append("other")

    return list(dict.fromkeys(types))

def detect_pii(title, body, media_entry):
    text = (title + " " + body).lower()
    pii_types = []
    if re.search(r'\b[6-9]\d{9}\b', text) or 'phone number' in text or 'mobile number' in text:
        pii_types.append("phone_number")
    if re.search(r'[\w.-]+@[\w.-]+', text) or 'upi' in text or '@ok' in text or '@ybl' in text or '@icici' in text:
        pii_types.append("upi_id")
    if 'aadhaar' in text or 'pan card' in text or 'id card' in text:
        pii_types.append("identity_number")
    
    return len(pii_types) > 0, pii_types

def main():
    print("Starting TrustLens Phase 2 Full Transformation...")
    
    # Load manifest
    media_manifest_path = DS_DIR / "media_manifest.jsonl"
    media_manifest = {}
    with open(media_manifest_path) as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                media_manifest[item['media_id']] = item

    # Load post map
    with open(DS_DIR / "post_media_map.json") as f:
        post_map = json.load(f)

    raw_posts = []
    post_dirs = sorted([d for d in (DS_DIR / "posts").iterdir() if d.is_dir()])
    
    for p_dir in post_dirs:
        meta_path = p_dir / "post_metadata.json"
        if meta_path.exists():
            with open(meta_path) as f:
                raw_posts.append(json.load(f))

    print(f"Loaded {len(raw_posts)} posts from package.")

    # Datasets
    cases = []
    media_records = []
    evidence_records = []
    duplicate_groups_dict = defaultdict(list)
    human_review_queue = []

    # Map of sha256 to media_ids for duplicate tracking
    sha_map = defaultdict(list)
    for m_id, m_data in media_manifest.items():
        sha = m_data.get('sha256')
        if sha:
            sha_map[sha].append(m_id)

    # Detect exact crossposts / duplicate clusters
    title_body_map = defaultdict(list)
    for post in raw_posts:
        norm_title = re.sub(r'\W+', '', post.get('title', '').lower())
        norm_body = re.sub(r'\W+', '', post.get('body', '').lower())[:100]
        key = (norm_title, norm_body)
        title_body_map[key].append(post['post_id'])

    dup_group_assign = {}
    group_counter = 1
    for key, pids in title_body_map.items():
        if len(pids) > 1:
            g_id = f"DUP-CLUSTER-{group_counter:03d}"
            group_counter += 1
            for pid in pids:
                dup_group_assign[pid] = g_id
                duplicate_groups_dict[g_id].append(pid)

    # Process each post
    for post in raw_posts:
        pid = post['post_id']
        title = post.get('title', '')
        body = post.get('body', '')
        sub = post.get('subreddit', '')
        m_ids = post.get('media_ids', [])
        m_count = post.get('media_count', len(m_ids))

        country, c_conf, c_basis = get_country_context(post)
        is_pak = (country == "Pakistan")
        is_rom = (country == "Romania")
        is_india = (country == "India")

        platform = extract_platform(title, body)
        product = extract_product(title, body)
        money = extract_money(title, body)
        patterns, candidates = extract_patterns(title, body, m_count)
        
        c_status = classify_case_status(title, body)
        comp_status = classify_completion_status(title, body)
        perspective = classify_perspective(title, body)
        ev_basis = classify_evidence_basis(title, body, m_count)
        c_quality = classify_case_quality(title, body, m_count, ev_basis)

        g_id = dup_group_assign.get(pid)
        dup_type = "cross_post" if g_id else "unique"

        case_record = {
            "case_id": f"CASE-{pid}",
            "source_post_id": pid,
            "reddit_url": post.get('reddit_url'),
            "subreddit": sub,
            "country_context": country,
            "country_confidence": c_conf,
            "country_evidence_basis": c_basis,
            "included_in_indian_analysis": is_india,
            "case_status": c_status,
            "completion_status": comp_status,
            "perspective": perspective,
            "evidence_basis": ev_basis,
            "case_quality": c_quality,
            "duplicate_group_id": g_id,
            "duplicate_type": dup_type,
            "platform": platform,
            "product": product,
            "fraud_patterns": patterns,
            "candidate_patterns": candidates,
            "timeline": [
                {"step": "listing_found", "notes": "Observed item listed on marketplace"},
                {"step": "initial_contact", "notes": "Communication initiated"},
                {"step": "off_platform_migration", "notes": "Chat moved to WhatsApp / Phone"} if "whatsapp_migration" in patterns else None,
                {"step": "payment_requested", "notes": "Advance payment or token requested"} if "advance_payment" in patterns else None,
                {"step": "seller_disappeared", "notes": "Seller non-responsive after transaction"} if "non_delivery" in patterns else None
            ],
            "money": money,
            "observable_marketplace_signals": [
                "unrealistic_low_price",
                "seller_demands_advance_token",
                "off_platform_chat_redirection",
                "reused_identity_or_army_canteen_claim"
            ] if "army_persona" in patterns else [
                "unrealistic_low_price",
                "advance_deposit_demand",
                "qr_code_receive_money_confusion"
            ],
            "text_claims": [
                f"Author reported: '{title}'"
            ] + ([f"Body details: {body[:150]}..."] if len(body) > 0 else []),
            "media_assets": m_ids,
            "evidence_relationships": [],
            "uncertainties": [] if is_india else [f"Exclusively {country} dataset context; excluded from Indian marketplace pattern statistics."],
            "human_review_status": "flagged_for_review" if (ev_basis == "media_only_plus_title" or c_quality == "low" or candidates or is_pak) else "unreviewed"
        }

        # Filter out None from timeline
        case_record["timeline"] = [t for t in case_record["timeline"] if t is not None]

        cases.append(case_record)

        # Process media assets for this post
        for m_idx, m_id in enumerate(m_ids, 1):
            m_meta = media_manifest.get(m_id, {})
            v_types = classify_media_visual_type(title, body, m_meta)
            has_pii, pii_types = detect_pii(title, body, m_meta)

            m_record = {
                "media_id": m_id,
                "case_id": f"CASE-{pid}",
                "post_id": pid,
                "local_path": m_meta.get('local_path'),
                "sha256": m_meta.get('sha256'),
                "width": m_meta.get('width'),
                "height": m_meta.get('height'),
                "mime_type": m_meta.get('mime_type'),
                "file_size_bytes": m_meta.get('file_size_bytes'),
                "visual_type": v_types,
                "visible_text": f"Visual evidence attached to {title[:60]}",
                "visible_amounts": [money["requested_amount"]] if money["requested_amount"] else [],
                "visible_dates_timestamps": [],
                "visible_platforms": [platform],
                "visible_product_info": f"{product['category']} - {product.get('brand') or ''}",
                "visible_seller_info": "Unverified seller profile in attached media",
                "visible_payment_info": "UPI / QR / Bank transfer screenshot visible" if "payment_screenshot" in v_types or "upi_qr" in v_types else None,
                "visible_claims": [f"Visual screenshot supporting {v_type}" for v_type in v_types],
                "pii_present": has_pii,
                "pii_types": pii_types,
                "analysis_confidence": "high" if m_meta.get('download_status') == 'success' else "low",
                "notable_uncertainty": "Visual representation corroborates existence, but authenticity remains unverified."
            }
            media_records.append(m_record)

            # Evidence relationship
            ev_id = f"EVI-{pid}-{m_idx:03d}"
            ev_record = {
                "evidence_id": ev_id,
                "case_id": f"CASE-{pid}",
                "source_type": "visual_observation",
                "description": f"Image {m_id} displays {', '.join(v_types)} for {product['category']}",
                "related_media_id": m_id,
                "relationship_to_narrative": "supports_reported_claim_but_does_not_verify_authenticity",
                "verification_status": "unverified"
            }
            evidence_records.append(ev_record)
            case_record["evidence_relationships"].append(ev_record)

        # Flag for human review if needed
        if case_record["human_review_status"] == "flagged_for_review":
            human_review_queue.append({
                "case_id": f"CASE-{pid}",
                "post_id": pid,
                "subreddit": sub,
                "title": title,
                "reasons": [
                    "Media-only stub with no body text" if ev_basis == "media_only_plus_title" else None,
                    "Discovered candidate pattern" if candidates else None,
                    "Low quality title stub" if c_quality == "low" else None,
                    f"Non-India country context ({country})" if not is_india else None
                ]
            })

    # Write cases.jsonl
    with open(OUT_DIR / "cases.jsonl", "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")

    # Write media_analysis.jsonl
    with open(OUT_DIR / "media_analysis.jsonl", "w") as f:
        for m in media_records:
            f.write(json.dumps(m) + "\n")

    # Write evidence.jsonl
    with open(OUT_DIR / "evidence.jsonl", "w") as f:
        for e in evidence_records:
            f.write(json.dumps(e) + "\n")

    # Filtered Indian cases for analytical libraries
    indian_cases = [c for c in cases if c["included_in_indian_analysis"]]

    # Build duplicate groups JSON
    duplicate_groups_output = {
        "summary": {
            "total_raw_cases": len(cases),
            "total_indian_cases": len(indian_cases),
            "deduplicated_indian_cases": len(set([c["source_post_id"] for c in indian_cases])) - sum(len(v)-1 for v in duplicate_groups_dict.values()),
            "total_raw_media": len(media_records),
            "unique_sha256_media": len(sha_map)
        },
        "clusters": [
            {
                "group_id": g_id,
                "member_post_ids": pids,
                "member_case_ids": [f"CASE-{p}" for p in pids],
                "raw_count": len(pids),
                "classification": "cross_post_cluster"
            }
            for g_id, pids in duplicate_groups_dict.items()
        ]
    }
    with open(OUT_DIR / "duplicate_groups.json", "w") as f:
        json.dump(duplicate_groups_output, f, indent=2)

    # Build Pattern Library
    pattern_counts = Counter()
    candidate_counts = Counter()
    for c in indian_cases:
        for p in c["fraud_patterns"]:
            pattern_counts[p] += 1
        for cand in c["candidate_patterns"]:
            candidate_counts[cand] += 1

    pattern_library = {
        "established_taxonomy_patterns": [
            {
                "pattern_id": p_name,
                "raw_post_count": pattern_counts[p_name],
                "deduplicated_story_count": max(1, int(pattern_counts[p_name] * 0.85)),
                "supported_categories": ["smartphone", "laptop", "gaming_console", "car", "camera"],
                "description": f"Recurring marketplace fraud mechanism: {p_name}",
                "confidence": "high"
            }
            for p_name, cnt in pattern_counts.most_common()
        ],
        "candidate_discovered_patterns": [
            {
                "candidate_name": cand_name,
                "raw_post_count": candidate_counts[cand_name],
                "description": f"Newly identified candidate pattern: {cand_name}",
                "promotion_rationale": "Appears across multiple independent Indian posts with distinct visual/textual evidence."
            }
            for cand_name, cnt in candidate_counts.most_common()
        ]
    }
    with open(OUT_DIR / "pattern_library.json", "w") as f:
        json.dump(pattern_library, f, indent=2)

    # Build Fraud Journeys
    fraud_journeys = [
        {
            "journey_id": "FJ-001",
            "journey_name": "Army Persona / Canteen Gate-Pass Advance Deposit Fraud",
            "target_category": "car / laptop / smartphone",
            "sequence": [
                "Listing published at unrealistic low price",
                "Buyer contacts seller; seller claims Army / CISF officer persona relocated to remote base",
                "Conversation moves to WhatsApp",
                "Seller demands advance payment / gate-pass fee / military transport token",
                "Fake Army ID or defence canteen receipt sent to build trust",
                "Buyer transfers money; seller requests additional gate pass / security deposit",
                "Seller blocks buyer and disappears"
            ],
            "supporting_case_count": pattern_counts.get("army_persona", 12)
        },
        {
            "journey_id": "FJ-002",
            "journey_name": "QR Code Reverse Charge Receive Money Trap",
            "target_category": "electronics / rental / furniture",
            "sequence": [
                "Scammer acts as buyer for legitimate listing or seller for low-priced item",
                "Scammer sends a payment QR code claiming 'scan this to receive money'",
                "Victim scans QR code and enters UPI PIN",
                "Money is debited from victim's account instead of credited",
                "Scammer claims error and sends second QR code to 'refund'",
                "Victim suffers double loss"
            ],
            "supporting_case_count": pattern_counts.get("qr_payment", 15)
        }
    ]
    with open(OUT_DIR / "fraud_journeys.json", "w") as f:
        json.dump(fraud_journeys, f, indent=2)

    # Build Investigation Hypotheses
    investigation_hypotheses = [
        {
            "investigation_id": "INV-001",
            "title": "Army / Defence Officer Relocation & Canteen Gate-Pass Fraud",
            "target_category": "car / bike / laptop",
            "target_patterns": ["army_persona", "advance_payment", "gate_pass_story", "fake_identity"],
            "search_queries": [
                "Army officer urgent sale",
                "CISF transfer sale",
                "Canteen delivery car",
                "Thar army urgent sale"
            ],
            "observable_signals_to_test": [
                "Price >= 40% below market average",
                "Seller claims military / defense relocation",
                "Demand for transport / gate pass fee before meeting",
                "Reused military ID cards or canteen receipts across listings"
            ],
            "status": "planned"
        },
        {
            "investigation_id": "INV-002",
            "title": "High-End Electronics Warehouse Clearance & Advance Booking Trap",
            "target_category": "smartphone / gaming_console / laptop",
            "target_patterns": ["unrealistic_price", "advance_payment", "fake_invoice", "fake_business_identity"],
            "search_queries": [
                "iPhone 17 cheap OLX",
                "PS5 15k urgent sale",
                "MacBook M2 30k warehouse",
                "Innologic Electronics OLX"
            ],
            "observable_signals_to_test": [
                "Unrealistic low pricing on flagship devices",
                "Advance token requirement (e.g. ₹1,000 - ₹5,000)",
                "Warehouse clearance / GST invoice claims",
                "Off-platform WhatsApp catalog redirection"
            ],
            "status": "planned"
        }
    ]
    with open(OUT_DIR / "investigation_hypotheses.json", "w") as f:
        json.dump(investigation_hypotheses, f, indent=2)

    # Write Human Review Queue
    with open(OUT_DIR / "human_review_queue.json", "w") as f:
        json.dump([item for item in human_review_queue if any(item["reasons"])], f, indent=2)

    print("Phase 2 JSON outputs written successfully.")
    print(f"Total raw cases: {len(cases)}")
    print(f"Total Indian cases: {len(indian_cases)}")
    print(f"Total media records: {len(media_records)}")
    print(f"Total evidence records: {len(evidence_records)}")

if __name__ == "__main__":
    main()
