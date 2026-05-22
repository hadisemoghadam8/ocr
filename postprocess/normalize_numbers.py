# postprocess/normalize_numbers.py

def normalize_numbers(text):

    arabic_to_persian = str.maketrans(
        "٠١٢٣٤٥٦٧٨٩",
        "۰۱۲۳۴۵۶۷۸۹"
    )

    english_to_persian = str.maketrans(
        "0123456789",
        "۰۱۲۳۴۵۶۷۸۹"
    )

    text = text.translate(arabic_to_persian)
    text = text.translate(english_to_persian)

    return text