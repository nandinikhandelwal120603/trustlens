# TrustLens — LinkedIn Project Announcement Post

---

A few months ago, I lost ₹23,000 to an online marketplace scam. 

Like thousands of others, I was negotiating to buy a second-hand gadget. The listing looked clean, the price was reasonable, and the photos looked legitimate. But once the upfront deposit was sent, the listing vanished, the seller went dark, and the money was gone.

When I looked into how marketplaces tackle this, I found a surprising disconnect: most anti-fraud solutions try to train a black-box binary classifier that outputs a "scam score"—e.g. "94% Scam Probability". 

The problem? In real-world marketplaces, you don't have clean ground-truth fraud labels at the moment of listing creation. An opaque score doesn't tell a trust & safety investigator *what* is wrong, and single-signal rules (like flagging cheap items) cause massive false positives.

So I spent the last few months building **TrustLens**—an open-source, evidence-first fraud intelligence research system.

Instead of asking *"Is this a scam?"*, TrustLens asks:  
👉 **"What observable evidence exists, what independent relationships connect it to other listings, and what cannot be established from this data?"**

Here is what I built and what I discovered across 2,980 canonical marketplace listings and 2,280 validated images:

🔍 **1. Multimodal Evidence Triangulation**
* **Price Normalization:** Standardized raw titles into clean taxonomy models, calculating price deviations against model-specific medians (isolating listings priced >35% below median).
* **Dual-Track Vision:** SHA-256 binary hashing discovered 164 exact duplicate image pairs—and **78% spanned different metropolitan cities**. Meanwhile, 384-d DINOv2 vision embeddings captured 9,492 visual similarity relationships across varying camera angles.
* **Packaging OCR Verification:** Using Tesseract OCR across all 2,280 images, the engine uncovered 68 multimodal discrepancies—including an explicit mismatch where a title claimed an "iPhone 13", but OCR detected "iPhone 13 Mini" printed on the box!
* **Dual-Detector AI Consensus:** Benchmarked two vision transformers (ViT-Base and Swin-Base). They disagreed on **24.5% of images**, proving why single AI detectors cannot be trusted in e-commerce.

🕸️ **2. The Marketplace Evidence Graph**
I projected all entities into a 5,709-node relationship graph with 21,395 edges. The largest cluster linked 122 listings across 14 cities via shared templates and images—surfacing commercial syndication patterns automatically.

📊 **3. Multivariate Statistical Novelty**
Using Isolation Forest across 4 distinct feature spaces (Price, Text, Image, Multimodal), only **3 out of 2,980 listings** were persistently anomalous across all spaces—including an unreleased "iPhone 17 Pro" placeholder at ₹350.

🎯 **4. What I Refused to Automate**
TrustLens does not output a "scam score", does not infer seller identity (which is unobserved in public search cards), and does not automate bans. Instead, it surfaced **213 multi-signal listing pairs** corroborated across ≥2 independent forensic layers (including 5 pairs cross-verified across 4 layers), prioritizing them for human investigators with zero arbitrary risk weighting.

The entire research pipeline spans Phases A through K, backed by 124 passing automated tests and a complete interactive visual showcase.

Check out the full case study, system architecture, and interactive showcase here:
👉 GitHub Repository: [Link]
👉 Architecture Diagram: [Link]
👉 Interactive Demo: [Link]

I'd love to hear your thoughts—especially from anyone working in Marketplace Operations, Trust & Safety, or Multimodal Machine Learning!

#MachineLearning #ComputerVision #TrustAndSafety #ArtificialIntelligence #Python #DataScience #AppliedAI #ECommerce
