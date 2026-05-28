import re


def clean_ocr_text(text: str) -> str:
    """
    Remove noise, empty lines, and invalid characters from OCR output.
    Preserves valid Persian, English, and numeric content.
    """
    lines = text.splitlines()
    cleaned = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Count character types for quality assessment
        symbols = sum(not ch.isalnum() and not ch.isspace() for ch in line)
        english_chars = sum(ch.isascii() and ch.isalpha() for ch in line)
        persian_chars = sum('\u0600' <= ch <= '\u06FF' for ch in line)
        digit_chars = sum(ch.isdigit() for ch in line)

        valid_chars = persian_chars + english_chars + digit_chars

        # Skip lines with high symbol density unless they contain Persian text
        if len(line) > 0 and symbols / len(line) > 0.35 and persian_chars < 2:
            continue

        # Filter out common short OCR artifacts
        if line.lower() in ["ae", "alll", "lll"]:
            continue
        if line.strip() in ["ممت", "مشا"]:
            continue

        # Skip lines with insufficient valid content
        if valid_chars < 2 or len(line) < 3:
            continue

        # Remove trailing artifacts like '@D &' or isolated symbols
        line = re.sub(r'\s+@[\w\s&]+$', '', line)
        line = re.sub(r'[&@]+$', '', line).strip()

        cleaned.append(line)

    return "\n".join(cleaned)