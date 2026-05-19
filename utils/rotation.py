#C:\Users\ASUS\ocr_project\utils\rotation.py


def try_rotations_ocr(img):
    rotations = [0, 90, 180, 270]

    best_score = -1
    best_img = img
    best_angle = 0

    for angle in rotations:
        rotated = img.rotate(angle, expand=True)

        psm = detect_psm(rotated)

        text = pytesseract.image_to_string(
            rotated,
            lang="fas+eng",
            config=f"--oem 3 --psm {psm}"
        )
        persian = len(re.findall(r'[\u0600-\u06FF]', text))

        digits = len(re.findall(r'\d', text))

        garbage = len(re.findall(r'[@#$%^&*_=+<>\\/|]', text))

        score = (
            persian * 5 +
            digits * 2 -
            garbage * 3
        )

        if score > best_score:
            best_score = score
            best_angle = angle
            best_img = rotated

    print(f"[INFO] Best rotation: {best_angle}")
    return best_img
