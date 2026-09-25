# TrustLens — AI/ML Interview & Project Story Guide

Factual, precise, and technically grounded answers for interview rounds, technical deep-dives, and system design discussions.

---

### 1. The 30-Second Elevator Pitch
> *"TrustLens is an evidence-first multimodal fraud intelligence system for online marketplaces. Instead of generating ungrounded 'scam probability' scores, it ingests marketplace listings and extracts independent forensic signals across price normalization, text cues, cryptographic image hashes, DINOv2 vision embeddings, and Tesseract packaging OCR. Across 2,980 OLX listings, it constructed a 5,709-node relationship graph and isolated 213 multi-signal listing pairs corroborated across multiple forensic layers, giving trust & safety teams an explainable evidence board rather than a black box."*

---

### 2. The 60-Second Interview Answer
> *"Most marketplace fraud detection projects try to build a supervised binary classifier that outputs a scam score. But in real-world classifieds, you don't have ground-truth fraud labels at ingestion time, and single heuristics fail—for instance, in my research, two leading vision transformers disagreed on 24.5% of marketplace images.  
> I built TrustLens to solve this using multimodal evidence triangulation. I collected 2,980 listings and 2,280 images across India, normalized the product taxonomy, computed exact SHA-256 and dense DINOv2 visual similarity, and used OCR to catch contradictions between listing titles and packaging boxes—like a title claiming an iPhone 13 while the box showed an iPhone 13 Mini. I consolidated 137 features into a feature store, modeled statistical novelty with Isolation Forest, and built an evidence graph with 21,395 edges. The outcome is 213 cross-corroborated listing pairs prioritized for human review without arbitrary risk scoring."*

---

### 3. The 2-Minute Technical Explanation
> *"The engineering behind TrustLens spans four core pillars: ingestion, multimodal extraction, graph modeling, and unsupervised novelty detection.  
> First, ingestion: I built a deduplicated capture pipeline enforcing strict data boundaries across 2,980 listings and 2,280 validated images. I engineered a taxonomy parser that extracts model, variant, and storage to benchmark prices against comparable medians, isolating listings priced below 35% of median while filtering out accessory noise.  
> Second, multimodal forensics: On the visual side, I implemented a dual-track architecture—exact SHA-256 hashes to find binary re-use (164 pairs, 78% cross-city), and 384-dimensional DINOv2 embeddings to capture visual similarity across varying angles. I integrated Tesseract OCR across all images, discovering 68 multimodal discrepancy candidates—including an explicit packaging model mismatch and a demo unit lock screen. To evaluate synthetic imagery, I deployed two independent vision models (ViT-Base and Swin-Base) in a consensus setup, identifying 6 mutual candidates and 559 disagreements.  
> Third, the relationship graph: I projected these signals into a 5,709-node heterogeneous network, clustering listings into 2,133 components. The largest component linked 122 listings across 14 cities via shared templates.  
> Finally, I consolidated 137 validated features into a canonical feature store and trained Isolation Forest models across four distinct feature spaces. Persistence analysis revealed that only 3 listings were anomalous across all four spaces. The entire pipeline is fully reproducible, deterministic, and backed by 124 passing automated tests."*

---

### 4. "Tell me about your most technically difficult project."
> *"TrustLens was technically challenging because it required orchestrating multiple heterogeneous machine learning and computer vision models on a local 16GB unified memory machine without GPU clusters or cloud dependencies, while maintaining absolute data integrity.  
> The first major challenge was memory and resource management. Loading PyTorch with DINOv2, ViT-Base, and Swin-Base simultaneously would cause out-of-memory crashes. I designed a sequential execution pipeline with aggressive cache reclamation, batching, and PyArrow memory mapping.  
> The second challenge was multimodal alignment under noisy e-commerce conditions. Marketplace photos have glare, compression artifacts, and varied angles. Perceptual hashing alone was too rigid, while deep embeddings were too broad. I solved this by building a multi-tier visual pipeline: exact cryptographic hashes for identical image re-use, perceptual hashes for compression, and DINOv2 for semantic pose matching.  
> The third challenge was avoiding target leakage and fake precision. Without post-transaction dispute logs, creating a supervised 'scam score' would have been fraudulent science. I designed a principled evidence hierarchy—Observed, Derived, Candidate, Unverified, and Unknown—and ranked candidates by integer counts of independent forensic layers rather than arbitrary weights."*

---

### 5. "Why did you build this?"
> *"I built TrustLens because I experienced the real-world impact of marketplace fraud firsthand when I lost ₹23,000 to an online deposit scam. When I looked into existing anti-fraud tools, I realized they were either simplistic keyword blacklists or black-box classifiers that nobody trusted.  
> I wanted to investigate whether modern multimodal AI—combining vision transformers, OCR, and graph intelligence—could act as a structured evidence copilot for marketplace investigators. I wanted to build a system that respected scientific boundaries: one that organizes facts and reveals cross-listing relationships rather than making reckless automated accusations."*

---

### 6. "What did you personally engineer?"
> *"I engineered the entire system from scratch:  
> 1. Built the ingestion pipeline and data quality auditing system enforcing 0 duplicate IDs and 0 unmatched joins.  
> 2. Designed the deterministic regex product normalizer that extracts clean product taxonomy and computes median price baselines.  
> 3. Implemented the cryptographic hashing (SHA-256) and perceptual hashing (pHash, dHash, aHash) algorithms.  
> 4. Integrated DINOv2 dense visual embeddings and nearest-neighbor search.  
> 5. Built the Tesseract OCR packaging verification engine that detected 68 cross-modal discrepancies.  
> 6. Implemented the dual-detector AI consensus architecture (ViT-Base and Swin-Base).  
> 7. Constructed the 5,709-node NetworkX-based relationship graph and component clustering.  
> 8. Built the canonical 137-column Unified Feature Store.  
> 9. Designed the multi-space Isolation Forest statistical novelty engine and persistence evaluation.  
> 10. Authored 124 automated unit and integration tests and built the interactive showcase web application."*

---

### 7. "What would you improve or do differently?"
> *"If starting over, I would introduce asynchronous parallel workers for OCR and embedding extraction to cut processing time from minutes to seconds. I would also capture complete listing pages rather than search cards, which would give us seller account registration dates and full item descriptions. Algorithmically, I would explore Graph Neural Networks (GNNs) on the relationship graph to learn multi-hop entity embeddings directly from the heterogeneous network."*

---

### 8. "What were the biggest limitations?"
> *"The biggest limitations were:  
> 1. Lack of persistent seller IDs in public search cards, which prevented us from linking listings to verified legal entities.  
> 2. Lack of post-transaction ground truth labels, which is why we strictly bounded our modeling to unsupervised statistical novelty and evidence corroboration.  
> 3. Domain scope: our dataset focused on high-value electronics (`iphone`, `macbook`, `ps5 controller`), so the findings describe this specific vertical rather than the entire classifieds ecosystem."*

---

### 9. "How would this become a production system at scale?"
> *"In a production environment at a company like OLX or eBay, TrustLens would transition from a batch analytical pipeline to an event-driven streaming architecture:  
> 1. **Ingestion:** Kafka topic streaming new listings and image uploads.  
> 2. **Near-Real-Time Feature Workers:** Lightweight microservices computing SHA-256 hashes and perceptual hashes in milliseconds; asynchronous workers generating DINO embeddings and OCR extractions.  
> 3. **Graph Database:** Storing entity edges in Neo4j or Amazon Neptune, querying 2-hop neighborhoods at publish time.  
> 4. **Investigator Dashboard:** Exposing multi-signal evidence cards to human trust & safety agents in their existing review queue.  
> 5. **Human Feedback Loop:** Reviewer actions (confirming mismatches or clearing false positives) feeding into active-learning pipelines to calibrate risk models with verified internal ground truth."*
