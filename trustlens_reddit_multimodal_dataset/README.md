# TrustLens Reddit Multimodal Evidence Dataset

## Dataset Summary
- **Total Reddit Posts:** 178
- **Posts With Media:** 73
- **Posts Without Media:** 105
- **Successfully Downloaded Media Assets:** 330
- **Failed Media Downloads:** 0

---

## Directory Organization & Hierarchy

Every Reddit post in this archive maintains its own dedicated case folder inside `posts/`:

```text
trustlens_reddit_multimodal_dataset/
├── README.md                 # This document
├── manifest.json             # Dataset high-level metadata & summary
├── media_manifest.jsonl      # Machine-readable per-asset download log
├── post_media_map.json       # O(1) post_id -> media mapping
├── download_report.json      # Comprehensive download statistics & failure breakdown
└── posts/
    ├── <POST_ID>/
    │   ├── post_metadata.json # Post context (title, body, subreddit, author, media_ids)
    │   └── media/
    │       ├── MEDIA-<POST_ID>-001.jpg
    │       └── MEDIA-<POST_ID>-002.png
    └── ...
```

---

## Post-to-Media Mapping
The invariant relationship is strictly deterministic:
```text
post_id
    ↓
posts/<post_id>/post_metadata.json
    ↓
0, 1, or N media assets in posts/<post_id>/media/
    ↓
media_id: MEDIA-<post_id>-<001>.<ext>
```

For posts with zero media assets, the directory `posts/<post_id>/media/` exists intentionally as empty, and `post_metadata.json` clearly indicates `"media_count": 0, "media_ids": []`.

---

## Important Research & Integrity Notes
1. **Original Raw Data Remains Unchanged**: The source Reddit posts JSON was treated as strictly immutable raw data.
2. **Untouched Original Binary Assets**: Downloaded media files are original binary bytes without compression, resizing, watermarking, redaction, or format conversion.
3. **Traceability**: No media file exists detached from its parent Reddit `post_id`.
4. **Failure Transparency**: Any URL that failed to download is logged in `media_manifest.jsonl` with its HTTP status / error reason.
5. **Privacy & PII Warning**: Screenshots collected from Reddit contain real-world scam communications (WhatsApp chats, UPI IDs, phone numbers, merchant QR codes). Handle with research care according to ethical data guidelines.
