"""Gán nhãn spam (1) / ham (0) cho review Điện Máy Xanh."""

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "commentdienmayxanh.csv"
TARGET = ROOT / "data" / "labeled" / "reviews_spam_ham.csv"

PHONE = re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s.\-]*\d){9,10}(?!\d)")
LINK = re.compile(r"(?:https?://|www\.|\b\w+\.(?:com|vn|net|org)\b)", re.I)
REPEATED_CHAR = re.compile(r"([^\W\d_])\1{4,}", re.I | re.UNICODE)
OK_ONLY = re.compile(r"(?:ok)+|oki|oke|okay", re.I)


def normalized(text):
    return re.sub(r"\s+", " ", text.casefold()).strip()


def is_spam(text):
    clean = normalized(text)
    letters = re.sub(r"[^\w]", "", clean, flags=re.UNICODE)
    if not letters or len(letters) < 2:
        return True
    # Các câu chỉ có "ok" và biến thể ngắn, kể cả dấu câu/emoji, đều là spam.
    words_only = re.sub(r"[^\w]+", " ", clean, flags=re.UNICODE).strip()
    if OK_ONLY.fullmatch(words_only):
        return True
    if PHONE.search(clean) or LINK.search(clean):
        return True
    if REPEATED_CHAR.search(clean):
        return True
    words = clean.split()
    if len(words) >= 3 and len(set(words)) == 1:
        return True
    return False


def main():
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))

    product_counts = Counter(row["san_pham"] for row in rows)
    review_counts = Counter(
        (row["san_pham"], normalized(row["noi_dung"])) for row in rows
    )

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    spam_count = 0
    with TARGET.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.DictWriter(
            target, fieldnames=["category", "product", "review", "rating", "label"]
        )
        writer.writeheader()
        for row in rows:
            product = row["san_pham"]
            review = row["noi_dung"]
            repeated = review_counts[(product, normalized(review))]
            # Chỉ dùng trùng lặp cho câu đủ dài; "Tốt" có thể là thật.
            suspicious_duplicate = (
                len(review.split()) >= 4
                and repeated >= 4
                and repeated / product_counts[product] >= 0.25
            )
            label = int(is_spam(review) or suspicious_duplicate)
            spam_count += label
            writer.writerow(
                {
                    "category": row["phan_loai"],
                    "product": product,
                    "review": review,
                    "rating": row["so_sao"],
                    "label": label,
                }
            )

    print(f"Saved {len(rows)} reviews to {TARGET}")
    print(f"Spam: {spam_count}; ham: {len(rows) - spam_count}")


if __name__ == "__main__":
    main()
