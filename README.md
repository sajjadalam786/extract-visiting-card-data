# Visiting Card OCR & B2B Lead Categorization Pipeline

An end-to-end computer vision and NLP pipeline for extracting structured contact and business intelligence from physical visiting/business cards. Built with Apple Vision Framework and Python.

---

## Overview

This repository contains:
1. **The Extracted & Categorized Dataset (`expo_cards_data.csv`)**: 210 exhibition visiting cards parsed, cleansed, and categorized with dedicated relevance tiers for **PetTorque** (hydraulic torque wrenches, bolt tensioners, flange facing tools).
2. **The Extraction Engine (`card_extractor/`)**: A reusable pipeline for processing new batches of business cards.

---

## Dataset Schema (`expo_cards_data.csv`)

The CSV is tailored for marketing automation (bulk emailers, WhatsApp broadcasting, CRM imports):

| Column | Description | Automation Feature |
| :--- | :--- | :--- |
| **Brand Name** | Company / Organization name | Verified against domain roots & legal suffixes (`Pvt Ltd`, `LLP`, `GmbH`) |
| **Person Name** | Contact person name | Normalized title-casing and initial handling |
| **Mob number, Mob number 2, ...** | Phone & WhatsApp numbers | Individual columns for direct bulk messaging & dialers |
| **Email, Email 2, ...** | Email addresses | Individual columns for email drip campaigns |
| **Website** | Corporate websites | Combined in a single cell for easy CRM linking |
| **Address** | Street, industrial estate, city | Multi-line addresses parsed cleanly |
| **pincode** | 6-digit postal code | Dedicated column for geo-targeting |
| **Insta Handle** | Instagram profile | Clean `@handle` format |
| **Services/ Category** | Core business domain | 12 industry classifications |
| **PetTorque Relevance Tier** | Lead priority rating | Tier 1 (Prime Direct Buyer) down to Tier 5 |
| **Relevance Reason / Bolting Use Case** | Sales qualification notes | Specific bolting, flange, or wind turbine applications |

### Lead Prioritization Breakdown
- **Tier 1 (Prime Direct Buyers)**: Wind turbine OEMs, wind farm operators, EPC contractors, power utilities, turbine maintenance (Suzlon, Vestas, Nordex, Siemens Gamesa, BHEL, Greenko, etc.).
- **Tier 2 (High Potential Industrial OEM / EPC)**: Heavy equipment manufacturers, solar EPC, pressure vessel / piping fabricators.
- **Tier 3 (Bolting & Fastener Ecosystem)**: Industrial fastener manufacturers, bolt suppliers, flange fabricators (potential supply chain / cross-selling partners).
- **Tier 4 (Industrial Services & Secondary)**: Non-destructive testing (NDT), calibration, automation, industrial automation.
- **Tier 5 (Other / Low Direct Relevance)**: Logistics, freight forwarding, media, event organizers.

---

## Repository Structure

```text
.
├── README.md                  # Project overview and documentation
├── .gitignore                 # Excludes raw images and build artifacts
├── expo_cards_data.csv        # Master structured dataset (210 categorized leads)
├── Pettorque/
│   └── expo_cards_data.csv    # Synchronized workspace copy
└── card_extractor/
    ├── README.md              # Extractor documentation
    ├── run_extraction.sh      # 1-click execution script
    ├── batch_ocr.m            # Multi-threaded Apple Vision OCR engine (Objective-C)
    └── parse_cards.py         # Entity extraction & classification script (Python)
```

---

## How to Run the Extractor on New Cards

### Prerequisites
- **Operating System**: macOS (requires Apple Vision framework)
- **Compilers**: Clang / Xcode Command Line Tools (`xcode-select --install`)
- **Python**: Python 3.8+ (standard library only, no heavy pip dependencies required)

### Quick Start
To extract visiting cards from a folder, run:

```bash
cd card_extractor
./run_extraction.sh "/path/to/card_images_folder" "/path/to/output.csv"
```

If run without arguments, it defaults to processing images in the parent directory and outputting to `expo_cards_data.csv`.

---

## Pipeline Architecture

1. **Native Apple Vision OCR (`batch_ocr.m`)**:
   - Uses `VNRecognizeTextRequest` with `VNRequestTextRecognitionLevelAccurate`.
   - Utilizes Grand Central Dispatch (`dispatch_apply`) for parallel processing across all CPU/GPU cores.
   - Outputs bounding box and text content directly to a structured JSON stream.

2. **Parsing & Intelligence Engine (`parse_cards.py`)**:
   - **Entity Resolution**: Distinguishes between company names, designations, personal names, and physical addresses.
   - **Pattern Matching**: Regex pipelines for phone numbers (+91, landlines, toll-free), emails, domains, social handles, and Indian postal codes.
   - **B2B Lead Categorization**: Classifies leads into PetTorque's 12 industry verticals and assigns relevance tiers based on keyword semantics and business models.
