# engines/easyocr_engine.py
import easyocr
import numpy as np
import cv2

# ✅ Reader را یک‌بار در سطح ماژول بسازید (برای کارایی بهتر)
reader = easyocr.Reader(['fa', 'en'], gpu=False, verbose=False)


def run_easyocr(img, paragraph=False, text_threshold=0.6, low_text=0.4, min_size=15, **kwargs):
    """
    اجرای EasyOCR روی تصویر و بازگرداندن متن به صورت رشته.
    
    Returns:
        str: متن استخراج‌شده (همیشه رشته، حتی اگر خالی)
    """
    
    # حذف پارامتر lang اگر وجود دارد (چون reader از قبل ساخته شده)
    kwargs.pop('lang', None)
    
    try:
        # ✅ تغییر کلیدی: استفاده از paragraph=True برای حفظ ترتیب طبیعی متن
        results = reader.readtext(
            np.array(img),
            detail=1,
            paragraph=True,        # ✅ True: تشخیص پاراگراف برای حفظ ترتیب
            text_threshold=text_threshold,
            low_text=low_text,
            min_size=min_size,
            width_ths=0.5,         # ✅ اتصال باکس‌های نزدیک به هم
            ycenter_ths=0.5,       # ✅ آستانه مرکز Y برای گروه‌بندی
            **kwargs
        )
    except Exception as e:
        print(f"[WARNING] EasyOCR failed: {e}")
        return ""
    
    final_results = []
    for item in results:
        bbox = item[0]
        text = item[1]
        conf = item[2] if len(item) > 2 else 1.0
        
        # 🔍 جداکننده هوشمند (حفظ کامل هندل‌های انگلیسی در خطوط فارسی)
        if '@' in text and any('\u0600' <= c <= '\u06FF' for c in text):
            parts = text.split('@', 1)
            fa_part = parts[0].strip()
            en_part = '@' + parts[1].strip()
            if fa_part:
                final_results.append((bbox, fa_part, conf))
            if en_part:
                final_results.append((bbox, en_part, conf))
        else:
            final_results.append((bbox, text, conf))
            
    # لاگ دیباگ (فقط برای اطمینان از تشخیص هندل)
    for item in final_results:
        if '@' in item[1]:
            print(f"[DEBUG] 🔍 Handle preserved -> '{item[1]}' | Conf: {item[2]:.3f}")
    
    # ✅ مرتب‌سازی ساده بر اساس Y (از بالا به پایین)
    final_results.sort(key=lambda x: sum([p[1] for p in x[0]]) / 4)
    
    # ✅ تبدیل لیست به رشته با \n (برای حفظ ساختار خطوط)
    texts = [item[1] for item in final_results]
    return "\n".join(texts) if texts else ""