# Business Card OCR & CSV Extractor

Extracts structured information from visiting/business card images directly into CSV format.

## Features
- **Native Apple Vision OCR**: Multi-threaded OCR with GCD on macOS for high speed and accuracy.
- **Auto-Formatting**:
  - `Brand Name`: Prioritizes corporate entities (`Pvt Ltd`, `LLP`, `Inc`, `GmbH`) and cross-references email/website domain roots.
  - `Person Name`: Extracts contact names, recognizes initials (e.g. `K.Priyadharshini`, `E. GANESAN`), and aligns with email usernames.
  - `Mob number`: Indian 10-digit mobile numbers (+91), landlines, and toll-free numbers formatted cleanly. Multiple numbers are split into separate columns (`Mob number`, `Mob number 2`, etc.).
  - `Email`: Validated and formatted. Multiple emails are split into separate columns (`Email`, `Email 2`, etc.).
  - `Website`: Multiple websites are combined in the **same cell** (comma-separated).
  - `Address` & `pincode`: Addresses combined cleanly; 6-digit Indian PIN codes placed in dedicated column.
  - `Insta Handle`: Handles formatted with `@`.
  - `Services/ Category`: Captures designations and product/service offerings.

## How to Run Next Time

### Option 1: Run the all-in-one shell script (Recommended)
Open Terminal and navigate to this folder:
```bash
cd "/Users/ashiquehussain/Library/CloudStorage/GoogleDrive-marketing@pettorque.com/My Drive/Email Marketing/EXPO - DATA - IMAGE ONLY/card_extractor"
./run_extraction.sh
```

### Option 2: Custom input folder or custom output file
You can pass custom paths as arguments:
```bash
./run_extraction.sh "/path/to/card_images_folder" "/path/to/output.csv"
```

## Files in this Folder
- `run_extraction.sh`: 1-click execution script.
- `batch_ocr.m` & `batch_ocr`: Native Apple Vision multi-threaded OCR tool.
- `parse_cards.py`: Logic engine that categorizes OCR tokens into the target CSV structure.
