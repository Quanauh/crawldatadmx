import os
import pandas as pd

def save_to_csv(reviews, filename):
    if not reviews:
        print("\nKhông có review nào để lưu.")
        return

    data = []
    for review in reviews:
        data.append(review.to_dict())

    df_new = pd.DataFrame(data)
    
    # Bỏ "id_danh_gia" đi, trả về đúng 6 cột ban đầu
    cols_order = ["phan_loai", "san_pham", "nguoi_danh_gia", "so_sao", "noi_dung", "link"]
    cols_order = [col for col in cols_order if col in df_new.columns]
    df_new = df_new[cols_order]

    if "noi_dung" in df_new.columns:
        df_new["noi_dung"] = df_new["noi_dung"].fillna("").astype(str).str.strip()
        df_new = df_new[df_new["noi_dung"] != ""]

    if df_new.empty:
        return

    folder = os.path.dirname(filename)
    if folder:
        os.makedirs(folder, exist_ok=True)

    file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0

    df_new.to_csv(
        filename,
        mode='a' if file_exists else 'w',
        header=not file_exists,
        index=False,
        encoding="utf-8-sig"
    )
    print("\n========== DONE ==========")
    print(df_new.tail())