# TrustLens — Interactive Demo Storyboard

A visual and structural guide for walking reviewers through the TrustLens interactive showcase application.

---

### Frame 1: Title & Population Funnel
* **Visual:** Header banner displaying "TRUSTLENS: Multimodal Marketplace Fraud Intelligence" with 4 primary stat cards (`2,980 listings`, `2,280 media assets`, `213 multi-signal pairs`, `124 tests passed`).
* **Speaker Action:** Introduce the core philosophy: shifting from black-box suspicion to evidence-first investigation.

---

### Frame 2: The Raw Marketplace Observation (Screen 1)
* **Visual:** Clean marketplace listing card displaying an iPhone 13 in Delhi listed at ₹18,500 with WhatsApp contact redirection.
* **Key Callout:** Prominent pill label stating `Research Observation Detected` (NOT "Scam Alert").
* **Speaker Action:** Highlight how an incoming listing looks prior to multi-modal feature extraction.

---

### Frame 3: Multi-Modal Evidence Ingestion (Screen 2)
* **Visual:** A 6-card grid categorizing incoming evidence into the strict hierarchy: Price (`Derived`), Text (`Derived`), Image (`Candidate`), OCR (`Candidate`), Network (`Observed`), Seller Identity (`Unknown`).
* **Speaker Action:** Emphasize the epistemological discipline of separating direct observations from unverified candidates.

---

### Frame 4: Dual-Track Media Forensics (Screen 3)
* **Visual:** Side-by-side comparison cards:
  * Left: Cryptographic SHA-256 byte-for-byte exact duplication (164 pairs; 78% cross-city).
  * Right: Dense 384-d DINOv2 visual similarity candidate (cosine $\ge 0.70$; 9,492 pairs).
* **Speaker Action:** Explain why hash-based deduplication and vision transformers solve complementary problems in marketplace imagery.

---

### Frame 5: Cross-Modal OCR Contradiction (Screen 4)
* **Visual:** Visual equation: Title Claim (`"iPhone 13 128"`) $\ne$ Image OCR Packaging String (`"iPhone 13 Mini"`).
* **Status Badge:** `MULTIMODAL INCONSISTENCY CANDIDATE` with explicit note: *"Requires verification. Does not prove malicious intent."*
* **Speaker Action:** Demonstrate deterministic text extraction catching packaging-to-title claim drift.

---

### Frame 6: Dual-Detector AI Consensus (Screen 5)
* **Visual:** Score meter comparing Detector A (ViT-Base: 0.975) and Detector B (Swin-Base: 0.871), alongside a summary table of 559 disagreements.
* **Speaker Action:** Explain why single AI detectors fail in e-commerce and why dual-model consensus is mandatory.

---

### Frame 7: The Marketplace Evidence Graph (Screen 6)
* **Visual:** Interactive vector network showing Listing nodes connected to shared image hashes, OCR phrases, and geographic nodes across Nashik and Mumbai.
* **Label:** Explicitly titled `Marketplace Evidence Network` (NOT "Fraud Ring").
* **Speaker Action:** Walk through how multi-signal relationships cross state and city borders.

---

### Frame 8: Multivariate Statistical Novelty (Screen 7)
* **Visual:** Bar chart showing anomaly persistence across 4 Isolation Forest spaces: 2,574 inliers, 270 single-space outliers, 88 two-space, 45 three-space, and 3 four-space outliers.
* **Speaker Action:** Explain that statistical outliers often reveal high-value bundles or placeholder data rather than fraud.

---

### Frame 9: Multi-Signal Synthesis (Screen 8)
* **Visual:** Tier breakdown of the 213 multi-signal pairs: 5 strongly cross-corroborated (4 layers), 63 three-layer, 145 two-layer.
* **Speaker Action:** Show how multiple independent forensic modalities reduce false positives without arbitrary scoring weights.

---

### Frame 10: Investigator Review Board (Screen 9)
* **Visual:** Case study layout structured into 5 questions: What We Saw, What The System Found, What Was Independently Observed, What Remains Unknown, Why It Deserves Human Review.
* **Speaker Action:** Demonstrate that TrustLens functions as a copilot for human trust & safety investigators.

---

### Frame 11: Scientific Boundaries & Conclusion (Screen 10)
* **Visual:** Limitations matrix explicitly stating unobserved seller metadata, uncaptured descriptions, and absence of ground-truth fraud labels.
* **Closing Banner:** *"FROM 'IS THIS A SCAM?' TO 'WHAT EVIDENCE SHOULD WE VERIFY?'"*
