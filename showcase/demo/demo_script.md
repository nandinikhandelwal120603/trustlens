# TrustLens — 2–3 Minute Interactive Demo Script

**Target Audience:** Recruiters, Machine Learning Engineers, Product Leaders, Trust & Safety Specialists  
**Tone:** Confident, technical, precise, human. Never sensationalist or accusatory.  
**Total Runtime:** ~2 minutes 45 seconds  

---

### [0:00 – 0:15] The Hook & The Problem
> *"Hi everyone. Most attempts at marketplace fraud detection start with a flawed question: 'Is this listing a scam?' They try to train a black-box binary classifier that outputs an arbitrary 95% scam score. But in real-world marketplaces, you don't have clean ground-truth fraud labels, and single heuristics fail.*  
> *TrustLens is an evidence-first fraud intelligence research system. We don't ask 'Is this a scam?' We ask: 'What observable evidence exists, and how can we verify it?'"*

---

### [0:15 – 0:35] Ingesting a Listing (Screen 1)
> *"Let's look at this live capture from OLX. It's an iPhone 13 listed in Delhi for ₹18,500. A standard classifier might immediately flag this because of the price. But TrustLens doesn't jump to conclusions. Instead, it ingests the listing into a deterministic forensic pipeline."*

---

### [0:35 – 1:00] Price & Text Evidence (Screen 2)
> *"First, price intelligence: by normalizing the product taxonomy, TrustLens benchmarks this specific device against 350 comparable iPhone 13 listings, measuring it at 51.9% below median.  
> Second, lexical intelligence: regex extractors identify contact-redirection language—'WhatsApp only'—and urgency cues.  
> Every signal is categorized in our strict evidence hierarchy: Observed, Derived, Candidate, Unverified, or Unknown."*

---

### [1:00 – 1:25] Media Forensics & OCR Verification (Screens 3 & 4)
> *"Now we look at the image. TrustLens calculates exact SHA-256 hashes, perceptual pHash, and 384-dimensional DINOv2 visual embeddings. Across our 2,280 analyzed images, we discovered 164 exact duplicate image pairs, with 78% spanning different cities.  
> Then, our OCR engine inspects the packaging box. The title claimed an iPhone 13, but Tesseract OCR detects 'iPhone 13 Mini' printed directly on the box. This creates an explainable Multimodal Inconsistency Candidate."*

---

### [1:25 – 1:50] The Evidence Network (Screens 5 & 6)
> *"Next, we evaluate AI synthetic indicators using a two-detector consensus architecture—ViT-Base and Swin-Base. We found 559 disagreements, proving single detectors are unreliable on marketplace photos.  
> Then, we project everything into our 5,709-node Marketplace Evidence Graph. Here you see Listing 185368 in Nashik and Listing 185419 in Mumbai. They share an identical image hash, lexical similarity, a shared OCR banner phrase, and high visual similarity—linking them across 4 independent forensic layers."*

---

### [1:50 – 2:10] Statistical Novelty (Screen 7)
> *"In Phase J, we ran unsupervised Isolation Forest novelty modeling across four feature spaces. Out of 2,980 canonical listings, only 3 listings were persistently anomalous across all four feature spaces—such as a ₹110,000 PS5 console bundle appearing within a controller query. These are statistical novelties, not automated fraud verdicts."*

---

### [2:10 – 2:30] Multi-Signal Synthesis (Screens 8 & 9)
> *"Across the entire platform, we identified 213 multi-signal listing pairs corroborated by at least two independent forensic layers. 5 pairs met the highest standard of 4 layers.  
> This feeds directly into a prioritized investigator queue, giving human trust and safety reviewers a complete evidence board: what was observed, what was derived, what is only a candidate, and what remains unknown."*

---

### [2:30 – 2:50] Limitations as an Engineering Strength (Screen 10)
> *"Finally, TrustLens is honest about its limitations. We don't have persistent seller profile IDs from search cards, so we don't infer seller identity. We don't have post-transaction fraud labels, so we refuse to generate fake probabilities. These limitations are clearly documented core constraints."*

---

### [2:50 – 3:00] Closing & The Takeaway
> *"TrustLens turns fragmented, noisy marketplace signals into structured, explainable evidence. The entire pipeline is open, frozen, and backed by 124 passing automated tests. Thank you."*
