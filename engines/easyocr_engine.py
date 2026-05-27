# engines/easyocr_engine.py
import easyocr
import numpy as np
import cv2

# Initialize reader once at module level to avoid re-loading models on every run
reader = easyocr.Reader(['fa', 'en'], gpu=False, verbose=False)


def run_easyocr(img, paragraph=False, text_threshold=0.6, low_text=0.4, min_size=15, **kwargs):
    """
    Run EasyOCR on the input image and return the extracted text.
    """
    
    # Remove 'lang' argument since the reader is already configured
    kwargs.pop('lang', None)
    
    try:
        results = reader.readtext(
            np.array(img),
            detail=1,
            paragraph=True,        # Merge boxes into paragraphs for better flow
            text_threshold=text_threshold,
            low_text=low_text,
            min_size=min_size,
            width_ths=0.5,         # Threshold for grouping text boxes horizontally
            ycenter_ths=0.5,       # Threshold for grouping text boxes vertically
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
        
        # Split mixed Persian/English lines to preserve handles (e.g., @user)
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
            
    # Log detected handles for verification
    for item in final_results:
        if '@' in item[1]:
            print(f"[DEBUG] Handle preserved -> '{item[1]}' | Conf: {item[2]:.3f}")
    
    # Sort results based on Y-axis (top to bottom) to fix reading order
    final_results.sort(key=lambda x: sum([p[1] for p in x[0]]) / 4)
    
    texts = [item[1] for item in final_results]
    return "\n".join(texts) if texts else ""