#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGES_DIR="${1:-$(dirname "$SCRIPT_DIR")}"
OUTPUT_CSV="${2:-$IMAGES_DIR/expo_cards_data.csv}"
TEMP_JSON="$SCRIPT_DIR/temp_ocr_results.json"

echo "=========================================================="
echo "    Visiting / Business Card OCR & CSV Extraction Pipeline"
echo "=========================================================="
echo "Input Folder:  $IMAGES_DIR"
echo "Output CSV:    $OUTPUT_CSV"
echo ""

# 1. Compile native macOS Apple Vision OCR binary if not compiled or changed
if [ ! -f "$SCRIPT_DIR/batch_ocr" ] || [ "$SCRIPT_DIR/batch_ocr.m" -nt "$SCRIPT_DIR/batch_ocr" ]; then
    echo "[1/3] Compiling native Apple Vision OCR tool..."
    clang -O3 -framework Foundation -framework Vision -framework AppKit "$SCRIPT_DIR/batch_ocr.m" -o "$SCRIPT_DIR/batch_ocr"
else
    echo "[1/3] Native OCR tool is ready."
fi

# 2. Run multi-threaded OCR
echo "[2/3] Extracting text across all card images..."
"$SCRIPT_DIR/batch_ocr" "$IMAGES_DIR" "$TEMP_JSON"

# 3. Parse and generate structured CSV
echo "[3/3] Parsing details and generating CSV..."
python3 "$SCRIPT_DIR/parse_cards.py" "$TEMP_JSON" "$OUTPUT_CSV"

# Cleanup temporary JSON
rm -f "$TEMP_JSON"

echo ""
echo "SUCCESS! Extracted CSV saved to:"
echo "$OUTPUT_CSV"
echo "=========================================================="
