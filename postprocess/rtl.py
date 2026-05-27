# postprocess/rtl.py
"""
RTL/BiDi utilities for Persian OCR post-processing.

Handles bidirectional text issues, punctuation spacing, and safe RTL application
while preserving URLs, handles, and mixed-language content.
"""

import re

# Patterns for detecting content that should not be modified
URL_PATTERN = re.compile(r'(https?://\S+|www\.\S+|[A-Za-z0-9_-]+\.(com|ir|org|net))')
USERNAME_PATTERN = re.compile(r'@\w+')
HASHTAG_PATTERN = re.compile(r'#\w+')


def is_mixed_line(line: str) -> bool:
    """
    Check if a line contains both Persian and English characters.
    
    Mixed lines are left unchanged to avoid breaking word order during RTL application.
    """
    persian_chars = len(re.findall(r'[\u0600-\u06FF]', line))
    english_chars = len(re.findall(r'[A-Za-z]', line))
    return persian_chars > 0 and english_chars > 0


def clean_bidi(text: str) -> str:
    """
    Remove invisible Unicode BiDi control characters.
    
    Handles None or non-string inputs safely.
    """
    if text is None or not isinstance(text, str):
        return ""
    
    return re.sub(r'[\u200e\u200f\u2066-\u2069]', '', text)


def fix_bidi_punctuation(text: str) -> str:
    """
    Normalize punctuation spacing for Persian and English text.
    
    Rules:
    - Remove space before punctuation: "سلام ، دنیا" → "سلام، دنیا"
    - Add space after punctuation: "سلام،دنیا" → "سلام، دنیا"
    - Remove space after #: "# سلام" → "#سلام"
    """
    # Remove space before punctuation marks
    text = re.sub(r'\s+([،,:؛.!؟])', r'\1', text)
    
    # Add space after punctuation if missing
    text = re.sub(r'([،,:؛.!؟])([^\s])', r'\1 \2', text)
    
    # Remove space after hash for proper hashtag formatting
    text = re.sub(r'#\s+', '#', text)
    
    return text


def smart_direction_fix(line: str) -> str:
    """
    Apply RTL direction only to lines that are purely Persian.
    
    Decision logic:
    - Pure Persian lines: apply RTL markers
    - English-only lines: leave unchanged
    - Mixed Persian/English: leave unchanged (prevents word order issues)
    - Lines with URLs, @handles, or #hashtags: leave unchanged
    
    This ensures stable text rendering across terminals, editors, and document formats.
    """
    line = line.strip()
    if not line:
        return line

    # Normalize punctuation first
    line = fix_bidi_punctuation(line)

    # Skip RTL for lines containing URLs, handles, or hashtags
    if URL_PATTERN.search(line):
        return line
    if USERNAME_PATTERN.search(line) or HASHTAG_PATTERN.search(line):
        return line

    # Skip RTL for mixed-language lines
    if is_mixed_line(line):
        return line

    # Count character types to determine language dominance
    persian_chars = len(re.findall(r'[\u0600-\u06FF]', line))
    english_chars = len(re.findall(r'[A-Za-z]', line))

    # Apply RTL only if Persian characters dominate (at least 2:1 ratio)
    if persian_chars > english_chars * 2:
        # Avoid double-wrapping if RTL markers already present
        if line.startswith('\u202B') and line.endswith('\u202C'):
            return line
        return '\u202B' + line + '\u202C'
    
    return line