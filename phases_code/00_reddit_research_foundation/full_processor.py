"""
TrustLens — Reddit Multimodal Dataset Full Analysis Pipeline
Performs Phase 2 transformation across all raw Reddit post records and media assets.
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
    # Check Indian indicators
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
        return "OLX"  # default dataset source
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

    # Find amounts
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
                if val >= 100:  # filter small numbers
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

    if 'more money' in text.lower() or 'another' in text.lower() or 'additional' in text.lower() or 'gate pass' in text.lower() or 'delivery fee' in text.lower():
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

    if 'advance' in text or 'token' in text or 'booking' in text or 'pay first' in text or 'advance payment' in text:
        patterns.append("advance_payment")
        patterns.append("deposit_request")

    if 'qr' in text or 'scanner' in text or 'scan to receive' in text or 'scan code' in text:
        patterns.append("qr_payment")
        patterns.append("upi_payment")

    if 'upi' in text or 'gpay' in text or 'phonepe' in text or 'paytm' in text:
        patterns.append("upi_payment")

    if 'army' in text or 'cisf' in text or 'soldier' in text or 'military' in text or 'defense' in text or 'defence' in text:
        patterns.append("army_persona")
        patterns.append("fake_identity")

    if 'gate pass' in text or 'courier' in text or 'transport' in text or 'delivery fee' in text or 'relocation' in text:
        patterns.append("gate_pass_story")
        patterns.append("fake_courier")

    if 'cheap' in text or 'unrealistic' in text or 'urgent' in text or 'very low price' in text or 'too good to be true' in text:
        patterns.append("unrealistic_price")

    if 'whatsapp' in text or 'wa' in text or 'chat' in text or 'moved to' in text:
        patterns.append("off_platform_communication")
        patterns.append("whatsapp_migration")

    if 'fake invoice' in text or 'invoice' in text or 'bill' in text or 'gst' in text or 'receipt' in text:
        patterns.append("fake_invoice")

    if 'fake payment' in text or 'screenshot' in text and ('paid' in text or 'sent' in text):
        patterns.append("fake_payment_screenshot")

    if 'not delivered' in text or 'blocked' in text or 'disappeared' in text or 'ran away' in text:
        patterns.append("non_delivery")
        patterns.append("fake_seller")

    # Product specific
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

    # Discovered Candidate Patterns
    if 'canteen' in text or 'defence store' in text or 'army canteen' in text:
        candidates.append("defence_store_receipt_scam")
    if 'macbook' in text and ('32k' in text or '30k' in text or '25k' in text):
        candidates.append("macbook_m1_m2_suspiciously_cheap")
    if 'innologic' in text or 'samsung india' in text or 'warehouse clearance' in text:
        candidates.append("fake_tech_company_warehouse_clearance")
    if 'qr refund' in text or 'receive money' in text:
        candidates.append("qr_reverse_charge_receive_money_trap")

    # Deduplicate
    patterns = list(dict.fromkeys(patterns))
    if not patterns:
        patterns.append("suspected_scam")

    return patterns, candidates

def classify_case_status(title, body):
    text = (title + " " + body).lower()
    if 'is this a scam' in text or 'is this scam' in text or 'legit or scam' in text or 'advice regarding' in text or 'scam?' in text:
        return "asking_if_scam"
    if 'scam alert' in text or 'beware' in text or 'awareness' in text or 'warning' in text:
        return "fraud_warning"
    if 'i got scammed' in text or 'lost' in text or 'paid' in text or 'my friend got scammed' in text:
        return "victim_report"
    if 'scam' in text:
        return "reported_scam"
    return "suspected_scam"

def classify_completion_status(title, body):
    text = (title + " " + body).lower()
    if any(k in text for k in ['prevented', 'almost scammed', 'didn\'t pay', 'did not pay', 'saved me', 'blocked him', 'realised in time', 'did not fall']):
        return "attempted_but_prevented"
    if any(k in text for k in ['scammed', 'lost', 'paid', 'transferred', 'sent money']):
        return "completed"
    return "suspected_attempt"

def classify_perspective(title, body):
    text = (title + " " + body).lower()
    if any(k in text for k in ['i was', 'i got', 'i paid', 'i bought', 'i am looking', 'he asked me', 'to me']):
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

print("Pipeline helper functions defined.")
