# OLX Outreach — Engineering Leadership Technical Brief

**Target Audience:** Principal Engineers, Staff ML Engineers, Director of Engineering, Trust & Safety Platform Leads  
**Focus:** Technical Architecture, Multimodal Retrieval, Graph Topology, Feature Store, Production Roadmap  

---

### Subject: Technical Brief: Multimodal Evidence Retrieval & Graph Topology for Marketplace Trust

> *Hi [Name],*  
>  
> *I am an AI/ML engineer based in Delhi specializing in computer vision, graph analytics, and multimodal systems. I recently developed an open research prototype called **TrustLens**, exploring how multimodal feature stores and relationship graphs can tackle cross-listing duplication and deceptive listings without relying on brittle, uncalibrated scam probabilities.*  
>  
> *I wanted to share a brief technical overview of the system architecture and how I believe this approach could translate into a scalable platform capability.*  

---

### Technical Architecture Highlights

```
Incoming Listing ──> Multimodal Ingestion Pipeline
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   Text Engine      Media Engine      OCR Engine
  (N-Grams, TF-IDF) (SHA / DINOv2)  (Tesseract 5.5)
        │                │                │
        └────────────────┼────────────────┘
                         ▼
             Cross-Modal Consistency Engine
                         │
                         ▼
             Heterogeneous Evidence Graph
             (5,709 Nodes • 21,395 Edges)
                         │
                         ▼
             Unified Analytical Feature Store
              (2,980 Rows × 137 Features)
                         │
                         ▼
             Isolation Forest Novelty Engine
                         │
                         ▼
             Investigator Evidence Queue
```

1. **Dual-Track Visual Representation:**  
   * **Exact Hash Deduplication:** High-throughput cryptographic SHA-256 hashes isolate byte-for-byte image recycling across listings (164 pairs; 78% cross-city).  
   * **Dense Semantic Visual Retrieval:** 384-dimensional dense vectors generated via `dinov2_vits14` capture semantic similarity invariant to minor angle shifts and camera perspective (9,492 pairs at cosine $\ge 0.70$).  

2. **Cross-Modal Claim Verification:**  
   * Integrates local Tesseract OCR over product images (82.7% text-positive yield).  
   * Implements a deterministic consistency validator cross-referencing extracted box/display text with listing title claims, identifying 68 discrepancy candidates (such as title declaring iPhone 13 while packaging box shows iPhone 13 Mini).  

3. **Dual-Transformer Synthetic Image Consensus:**  
   * Evaluated 2,280 images across ViT-Base and Swin-Base architectures.  
   * Discovered 559 single-detector disagreements (24.5%), confirming that single-model AI detection on compressed classified images produces unacceptable false positive rates.  

4. **Relationship Network Topology:**  
   * Built a 5,709-node heterogeneous entity graph linking listings, media hashes, OCR phrases, and geographic locations.  
   * Connected component clustering isolated 266 non-singleton clusters, with the largest spanning 122 listings across 14 cities—automatically exposing commercial marketing syndication.  

5. **Deterministic Feature Store & Novelty Modeling:**  
   * Consolidated 137 features (63 numeric, 40 categorical, 34 binary) into a PyArrow feature store with strict distinction between observed absence (`0`) and uncaptured data (`NULL`).  
   * Unsupervised Isolation Forest novelty modeling across 4 feature spaces isolated 3 persistent multivariate outliers.  

---

### What a Production Platform Deployment Would Require

*In my research, I deliberately restricted the system to public search-card data. Transitioning this architecture to an internal platform infrastructure would unlock significant compounding capabilities:*

1. **Authenticated Ingestion:** Ingesting internal seller account IDs, KYC status, and phone hashes into the graph to resolve clusters into verified merchant accounts versus coordinated abuse rings.  
2. **Event-Driven Streaming:** Replacing batch Parquet evaluation with a real-time Kafka/Flink pipeline that computes perceptual hashes and lightweight embeddings at the moment of listing creation.  
3. **Internal Ground Truth & Active Learning:** Connecting investigator verification decisions (clearing false positives or taking takedown action) back into a calibrated feedback loop to train high-precision supervised rerankers.  
4. **Hardware Serial Verification:** Deploying specialized OCR models to parse partially obscured IMEI / serial numbers against authorized platform databases.  

---

### Potential Discussion Points

*I would welcome the opportunity to walk through the technical implementation, share our benchmark results across our 124 passing automated tests, and discuss how your team approaches multimodal integrity challenges.*  

*Would you be open to a 20-minute technical exchange next week?*  

*Best regards,*  
*Nandini Khandelwal*  
*[GitHub: trustlens] • [LinkedIn Profile]*
