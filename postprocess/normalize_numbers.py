# postprocess/normalize_numbers.py
import re
def normalize_numbers(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    
    # اگر متن کوتاه است (مثل "4K", "2h") یا انگلیسی غالب دارد، اعداد را تغییر نده
    if len(text.strip()) < 15:
        return text
        
    persian = len(re.findall(r'[\u0600-\u06FF]', text))
    english = len(re.findall(r'[A-Za-z]', text))
    
    if english > persian:
        return text
    
    arabic_to_persian = str.maketrans("٠١٢٣٤٥٦٧٨٩", "۰۱۲۳۴۵۶۷۸۹")
    english_to_persian = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    
    text = text.translate(arabic_to_persian)
    text = text.translate(english_to_persian)
    return text