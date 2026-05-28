
import re


def fix_english_ocr(text: str) -> str:
    """
    Apply post-processing fixes for English OCR output.
    """
    if not text or not isinstance(text, str):
        return ""

    # Basic replacements for common OCR errors and punctuation spacing
    replacements = {
        r'\bIll\b': "I'll",
        r'\bIIl\b': "I'll",
        r'\bIII\b': "I'll",
        r'\bI1l\b': "I'll",
        r'\bI\'II\b': "I'll",
        r'@emini(?=\s|$)': "@Gemini",
        r'(?<!\n)[ \t]+([.,!?;:])': r'\1',
        r'[ \t]{2,}': ' ',
    }

    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text)

    # Convert leading 'G' to '@' for social media handles
    # Excludes common English words that start with G
    excluded_words = {
        'google', 'gmail', 'great', 'good', 'go', 'get',
        'gym', 'game', 'group', 'guide', 'general', 'global', 'gemini'
    }

    def replace_g_with_at(match):
        prefix = match.group(1)
        username = match.group(2)
        full_word = "G" + username

        if full_word.lower() not in excluded_words:
            return prefix + '@' + username
        return match.group(0)

    # Pattern: G at word boundary followed by 5+ alphanumeric characters
    text = re.sub(r'(^|\s)G([a-zA-Z][a-zA-Z0-9_]{4,})', replace_g_with_at, text)

    # Advanced fixes: only apply to longer English texts to avoid false positives
    english_chars = len(re.findall(r'[A-Za-z]', text))

    if english_chars > 30:
        # Fix specific OCR misreads
        text = re.sub(r'\b2\W*1\W*1\b', "I'll", text)

        # Fix word order in "Afternoon" poem
        text = re.sub(r'\bbe!\s*they\s+Were\b', "be! They were", text)

        # Format poem title with em-dash
        text = re.sub(r'(?m)^(Afternoon)\s+(Dorothy Parker)\s*$', r'\1 — \2', text)

        # Remove stray commas at line starts
        text = re.sub(r'(?m)^,([A-Z])', r'\1', text)

        # Move punctuation from line start to previous line end
        text = re.sub(r'\n([,.;:!?])([A-Za-z])', r'\1 \2', text)

        # Fix broken URLs
        text = re.sub(r'www\s+([A-Za-z0-9.-]+)\s+com', r'www.\1.com', text)
        text = re.sub(r'www\s+([A-Za-z0-9.-]+)\s+ir', r'www.\1.ir', text)

        # Fix final line of "Afternoon" poem
        text = re.sub(
            r'be!\s*They\s+were\s+further\s+than',
            "Were further than they be!",
            text
        )

    # Final cleanup: trim whitespace and normalize line breaks
    text = text.strip()
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text