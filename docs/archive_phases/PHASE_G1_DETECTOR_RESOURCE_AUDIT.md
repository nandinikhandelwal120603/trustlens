# TrustLens Phase G.1 — AI-Generated Image Detector & Resource Audit

**Timestamp:** 2026-09-24T11:46:00+05:30  
**Machine:** Apple Mac (Apple M4, 10 cores, ARM64)  
**Total Unified RAM:** 16.00 GB  
**Available / Reclaimable Memory:** ~4.91 GB  
**Free Disk Space:** 107 GB  
**Python Runtime:** 3.11.13  
**PyTorch Version:** 2.14.0 (MPS available)  
**Transformers Version:** 5.17.0  

---

## 1. Objective & Architectural Requirements

Phase G.1 introduces **two independent, dedicated AI-generated-image detection models** to evaluate TrustLens marketplace assets.

### Strict Non-Negotiables:
1. **Dedicated AI-vs-Real Architecture:** Generic vision-language models, ImageNet classifiers, DINOv2 alone, raw FFT, or colorfulness heuristics are **prohibited** as AI detectors.
2. **Methodological Diversity:** Detector A and Detector B must belong to distinct architectural families (not two checkpoints of the same architecture).
3. **Sequential Execution (Hard Rule):** Because available RAM is ~4.91 GB, models MUST NOT be loaded concurrently.
   ```text
   Detector A loaded → Run inference batch → Unload / gc.collect() / empty_cache()
           ↓
   Detector B loaded → Run inference batch → Unload / gc.collect() / empty_cache()
   ```
4. **Offline Local Primary Detection:** No cloud APIs (OpenAI, Gemini, Puter) as primary inference engines. Puter is exclusively an escalation mechanism for borderline / disagreement samples.
5. **No Synthetic Confidence / Averaging:** Raw logits/scores must be preserved. Never do `(score_a + score_b) / 2`.
6. **Controlled Validation Gate:** If no labeled ground truth exists locally, record `controlled_validation_available = false`.

---

## 2. Model Investigation & Selection

We surveyed candidate open-source AI image detection models hosted on Hugging Face:

| Candidate Model | Architecture | Checkpoint Size | Parameter Count | Classes | License | Evaluation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `dima806/ai_vs_human_generated_image_detection` | **Vision Transformer (ViT-Base)** | 327.32 MB (`model.safetensors`) | ~86M | `0: human`, `1: AI-generated` | Apache-2.0 | **SELECTED as Detector A** |
| `umm-maybe/AI-image-detector` | **Hierarchical Swin Transformer (Swin-Base)** | 331.49 MB (`pytorch_model.bin`) | ~87M | `0: artificial`, `1: human` | MIT | **SELECTED as Detector B** |
| `prithivMLmods/Deep-Fake-Detector-Model` | SigLIP | 354.35 MB (`model.safetensors`) | ~86M | `0: Fake`, `1: Real` | Apache-2.0 | Viable alternate |

### Why Detector A & Detector B are Architecturally Distinct
- **Detector A (`dima806/...`)**: Standard non-hierarchical Vision Transformer (ViT) operating on fixed 16x16 non-overlapping patches with global self-attention across the whole sequence.
- **Detector B (`umm-maybe/...`)**: Hierarchical Swin Transformer utilizing shifted windows with localized cross-window self-attention, capturing multi-scale structural representations and local patch textures differently from standard ViTs.

---

## 3. Resource & Memory Footprint Budget

| Metric | Detector A (`dima806/...`) | Detector B (`umm-maybe/...`) | Combined (Sequential) |
| :--- | :--- | :--- | :--- |
| **Download / Storage Size** | 327.32 MB | 331.49 MB | 658.81 MB |
| **Model In-Memory Footprint** | ~350 MB | ~355 MB | Max ~360 MB (one at a time) |
| **Inference Working Memory (Batch=8)** | ~180 MB | ~195 MB | Max ~200 MB |
| **Total Process Footprint** | ~650 MB | ~680 MB | **Peak < 800 MB** |
| **System Headroom (Available RAM)** | 4.91 GB | 4.91 GB | **> 4.1 GB safety buffer** |

Both detectors operate well within safety thresholds. PyTorch MPS or CPU fallback can be utilized. To ensure deterministic stability on Apple Silicon without OpenMP thread contention, batch sizes will be kept at 8 with explicit memory reclamation (`gc.collect()`).

---

## 4. Controlled Validation Status

A search of the local workspace was conducted:
- Local labeled real vs. AI ground truth dataset: **NOT FOUND**.
- `controlled_validation_available = false`.
- **Finding:** Detector performance cannot be independently ground-truth validated against a verified benchmark on this machine. TrustLens marketplace images MUST NOT be treated as ground truth.

---

## 5. Execution Plan

1. **Implement `ai_image_detector.py`**:
   - Sequential model runner with explicit unload & memory purge.
   - Raw score preservation & semantic mapping.
   - Transparent agreement categorizer: `AGREEMENT_AI`, `AGREEMENT_REAL`, `DETECTOR_DISAGREEMENT`, `BORDERLINE`.
   - Robust checkpointing (`checkpoint_ai_detector.json`).
2. **Single-Image Smoke Test**:
   - Verify Detector A and B on a single asset without crashes or leaks.
3. **Pilot Evaluation (35 diverse images)**:
   - Sample diverse categories: `PHOTO`, `TEXT_HEAVY`, `SCREENSHOT`, `DOCUMENT_LIKE`, `PRODUCT_RENDER_LIKE`.
   - Score stability test against JPEG recompression / resizing.
4. **Full Run Gate Review**:
   - Inspect pilot score distributions, disagreement rate, runtime, and memory.
   - Run full 2,280 dataset sequentially if gated safe.
5. **Puter Escalation**:
   - Standardized multimodal escalation for borderline / disagreement assets.
6. **Reporting & Gallery**:
   - `AI_IMAGE_DETECTION_ANALYSIS.md`, `PHASE_G1_EXECUTION_REPORT.md`, `ai_detector_gallery.html`.
