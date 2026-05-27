#C:\Users\ASUS\ocr_project\postprocess\persian_fix.py
import re


def improve_persian_text(text: str) -> str:
    """
    Comprehensive post-processing for Persian OCR output.
    Handles character normalization, spacing, punctuation, and text structure.
    """
    if not text:
        return ""

    # Normalize line endings and remove invisible Unicode controls
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r'[\u200d\u200e\u200f\u2066-\u2069]', '', text)

    # Fix common Arabic character misreads in Persian text
    arabic_to_persian = {
        "ك": "ک", "ي": "ی", "ى": "ی", "ئ": "ی", "ؤ": "و", "ة": "ه", "ۀ": "ه", "ھ": "ه",
        "كی": "کی", "مى": "می", "نمى": "نمی", "كافى": "کافی", "دنيا": "دنیا"
    }
    for old, new in arabic_to_persian.items():
        text = text.replace(old, new)

    # Split commonly glued words and fix frequent typos
    glued_fixes = [
        (r"\bوبه\b", "و به"), (r"\bواز\b", "و از"), (r"\bودر\b", "و در"), (r"\bوگفت\b", "و گفت"),
        (r"\bردشد\b", "رد شد"), (r"\bاماکه\b", "اما که"), (r"\bازآن\b", "از آن"), (r"\bهرروز\b", "هر روز"),
        (r"\bهیچکس\b", "هیچ‌کس"), (r"\bهیچکدام\b", "هیچ‌کدام"), (r"\bهمدیگر\b", "هم‌دیگر"), (r"\bهمیشهگی\b", "همیشگی"),
        (r"\bوست\s*به\s*[-–]\s*", "وستِ به‌روز، "),
        (r"\bخوشکلا\b", "خوشگلا"),
        (r"\bپنجر\s*5\b", "پنجره"), (r"\bپنجر\b", "پنجره"), (r"\bپنجر\s*د‌ای\b", "پنجره‌ای"), (r"\bلحظههاست\b", "لحظه‌هاست")
    ]
    for pattern, repl in glued_fixes:
        text = re.sub(pattern, repl, text)

    # Fix spacing for mi/nemi prefixes and compound verbs
    text = re.sub(r"\bمی\s*([اآ-ی]+)", r"می‌\1", text)
    text = re.sub(r"\bنمی\s*([اآ-ی]+)", r"نمی‌\1", text)
    text = re.sub(r"\bمى\s*([اآ-ی]+)", r"می‌\1", text)
    text = re.sub(r"\bنمى\s*([اآ-ی]+)", r"نمی‌\1", text)

    # Fix pronouns attached to verbs (e.g., رفته ام -> رفته‌ام)
    text = re.sub(
        r"\b([اآ-ی]+ه)\s+(ام|ای|است|ایم|اید|اند)\b",
        r"\1‌\2",
        text
    )

    # Fix broken verb forms from OCR spacing errors
    text = re.sub(r"\bخوا\s+هد\b", "خواهد", text)

    # Fix plural suffixes and Persian half-space usage
    text = re.sub(r"\b([اآ-ی]+)\s+ها\b", r"\1‌ها", text)
    text = re.sub(r"\b([اآ-ی]+ه)ها\b", r"\1‌ها", text)
    text = re.sub(r"\b([اآ-ی]+[^ه‌\s])ها\b", r"\1‌ها", text)
    text = re.sub(r"‌{2,}", "‌", text)
    text = re.sub(r"([اآ-ی]+)هه\b", r"\1ه", text)
    text = re.sub(r"هه‌های\b", r"ه‌های", text)
    text = re.sub(r"\bوبه([اآ-ی]+)", r"و به \1", text)
    text = re.sub(r"\bودر([اآ-ی]+)", r"و در \1", text)
    text = re.sub(r"\bواز([اآ-ی]+)", r"و از \1", text)

    # Fix comparative and superlative suffix spacing
    text = re.sub(r"\b([اآ-ی]{2,})\s+ترین\b", r"\1ترین", text)
    text = re.sub(r"\b([اآ-ی]{2,})\s+تر\b", r"\1تر", text)
    text = re.sub(r"\b([اآ-ی]{2,})\s+ای\b", r"\1‌ای", text)
    text = re.sub(r"\b([اآ-ی]+)\s+ها\b", r"\1‌ها", text)
    text = re.sub(r"\b([اآ-ی]+)\s+های\b", r"\1‌های", text)
    text = re.sub(r"\b([اآ-ی]+)\s+(ام|ات|اش)\b", r"\1‌\2", text)

    text = re.sub(
        r"\b([اآ-ی]+[هی])\s+(اند|ایم|اید)\b",
        r"\1‌\2",
        text
    )
    text = re.sub(r"‌{2,}", "‌", text)

    # Separate glued compound verbs
    text = re.sub(r"\b([اآ-ی]{2,})کرد\b", r"\1 کرد", text)
    text = re.sub(r"\b([اآ-ی]{2,})شد\b", r"\1 شد", text)
    text = re.sub(r"\b([اآ-ی]{2,})گفت\b", r"\1 گفت", text)

    # Remove isolated single-character noise (common in OCR)
    def _keep_if_vav(match):
        char = match.group(1)
        return '' if char != 'و' else char

    text = re.sub(r'(?<!\S)([\u0600-\u06FF])(?!\S)', _keep_if_vav, text)
    text = re.sub(r'\s{2,}', ' ', text)

    # Fix frequent Persian OCR misreads
    common_ocr_fixes = {
        "مي": "می", "نمي": "نمی", "ك": "ک", "ي": "ی", "كرد": "کرد",
        "ميشود": "می‌شود", "نمیشود": "نمی‌شود", "ميكند": "می‌کند",
        "نميكند": "نمی‌کند", "ميخواست": "می‌خواست", "نميدانست": "نمی‌دانست",
        "می باشد": "می‌باشد", "نمی باشد": "نمی‌باشد", "می شود": "می‌شود",
        "نمی شود": "نمی‌شود", "می توان": "می‌توان", "نمی توان": "نمی‌توان",
        "خوا هد": "خواهد", "تن‌هاست": "تنهاست",
    }
    for old, new in common_ocr_fixes.items():
        text = text.replace(old, new)

    # Fix punctuation spacing and placement
    text = re.sub(r"[ \t]+([.!؟،,:؛])", r"\1", text)
    text = re.sub(r"([.!؟،,:؛])([^\s\n])", r"\1 \2", text)
    text = re.sub(r'(?<=[\u0600-\u06FF])\s*[-–]\s*(?=[\u0600-\u06FF])', '، ', text)
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)

    # Format dialogue markers consistently
    text = re.sub(r"(گفت|پرسید|جواب داد|لبخند زد)\s+", r"\1: ", text)

    # Fix specific sentence-ending patterns from OCR errors
    sentence_patterns = [
        (r"تنهاست\s+یک روز", "تنهاست.\n\nیک روز"),
        (r"نگاه می‌کردند\s+پیام", "نگاه می‌کردند.\n\nپیام"),
        (r"می‌سازند\s+می‌", "می‌سازند.\nمی‌"),
        (r"می‌شوی\s+می‌", "می‌شوی.\nمی‌"),
        (r"کافی نیست\?", "کافی نیست؟"),
    ]
    for pattern, repl in sentence_patterns:
        text = re.sub(pattern, repl, text)

    # Clean up headings and excessive whitespace
    text = re.sub(r"(?m)^\s*#([^\s])", r"# \1", text)
    text = re.sub(r"\bپیام\s+", "\n\nپیام:\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove noisy lines with high symbol density
    cleaned_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        stripped = re.sub(r"[|\\/`~]+$", "", stripped)
        if not stripped:
            cleaned_lines.append("")
            continue
        symbols = len(re.findall(r'[@#$%^&*_=+<>\\/|~`]', stripped))
        if len(stripped) > 0 and (symbols / len(stripped) > 0.4):
            continue
        cleaned_lines.append(stripped)

    text = "\n".join(cleaned_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove underscores between Persian words (OCR artifact)
    text = re.sub(r'(?<=[\u0600-\u06FF])\s*_+\s*(?=[\u0600-\u06FF])', ' ', text)

    # Final punctuation spacing pass
    text = re.sub(r"\s+([.!؟،,:؛])", r"\1", text)
    text = re.sub(r"([.!؟،,:؛])([^\s\n])", r"\1 \2", text)

    # Wrap overly long lines while preserving structure
    import textwrap
    temp_lines = text.split('\n')
    wrapped_lines = []

    for line in temp_lines:
        line = line.strip()
        if (len(line) > 160 and
            not any(x in line for x in ['http', 'www.', '@', '#']) and
            not line[-1] in '.!?؟'):
            wrapped_lines.extend(textwrap.wrap(line, width=160, break_long_words=False))
        else:
            wrapped_lines.append(line)

    text = '\n'.join(wrapped_lines)

    # Apply explicit RTL direction for pure Persian lines
    lines = text.split('\n')
    fixed_lines = []
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            fixed_lines.append('')
            continue
        if re.search(r'[\u0600-\u06FF]', line_stripped) and not re.search(r'[A-Za-z]', line_stripped):
            fixed_lines.append('\u202B' + line_stripped + '\u202C')
        else:
            fixed_lines.append(line_stripped)
    text = '\n'.join(fixed_lines)

    # Prevent repeated character artifacts from OCR
    text = re.sub(r"\b([اآ-ی])\1{3,}\b", r"\1\1", text)
    return text.strip()


def fix_safe_ocr_artifacts(text: str) -> str:
    """
    Apply safe, targeted fixes for common OCR artifacts.
    """
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line:
            cleaned.append('')
            continue

        # Fix spacing before "که" in common verb patterns
        line = re.sub(r'(می‌خواهد|می‌کند|می‌شود|می‌گوید|خواهد|باید)[\s\u200c]*که', r'\1 که', line)

        # Fix specific misreads
        if 'انصادالله' in line:
            line = line.replace('انصادالله', 'انصارالله')
        if 'دوز معلم' in line:
            line = line.replace('دوز معلم', 'روز معلم')
        line = line.replace('د -', '- ')

        # Remove EasyOCR artifacts like I1 or I۱ at line ends
        line = re.sub(r'[.!؟،,:؛]?\s*I[1lI۱]\s*$', '', line)

        # Strip trailing punctuation artifacts
        line = re.sub(r"['\"\\|`{}\[\]]+$", '', line)

        cleaned.append(line)
    return '\n'.join(cleaned)


def fix_instagram_handles(text: str) -> str:
    """
    Safely convert misread Instagram handles (C/S -> @).
    Only applies to clear cases to avoid false positives.
    """
    lines = text.split('\n')
    fixed_lines = []

    for line in lines:
        stripped_line = line.strip()

        # Case 1: entire line is a handle-like word starting with C or S
        if re.fullmatch(r'[CS][a-zA-Z0-9_]{5,}', stripped_line):
            line = '@' + stripped_line[1:]
            print(f"[DEBUG] Fixed handle (full line): '{stripped_line}' -> '{line}'")
            fixed_lines.append(line)
            continue

        # Case 2: handle appears mid-line; only fix very long words to avoid false positives
        pattern = r'\b(C|S)([a-zA-Z0-9_]{5,})\b'

        def replacer(match):
            word = match.group(0)
            if len(word) > 12:
                return '@' + word[1:]
            return word

        line = re.sub(pattern, replacer, line)
        fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def advanced_score(text):
    """
    Score OCR output quality based on character composition.
    Higher weight for Persian characters, penalty for garbage symbols.
    """
    persian = len(re.findall(r'[\u0600-\u06FF]', text))
    english = len(re.findall(r'[A-Za-z]', text))
    digits = len(re.findall(r'\d', text))
    garbage = len(re.findall(r'[@#$%^&*_=+<>\\/|]', text))
    words = len(text.split())

    if english > persian:
        english_weight, persian_weight = 4, 1
    else:
        persian_weight, english_weight = 4, 2

    return persian * persian_weight + english * english_weight + digits - garbage * 6 + words * 1.5