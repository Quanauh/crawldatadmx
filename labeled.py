import pandas as pd
import re
import os

# 1. Đọc dữ liệu gốc
df = pd.read_csv(r"C:\Users\Admin\OneDrive\Documents\crawldatadmxdemo\data\commentdienmayxanh.csv")

# 2. Xây dựng bộ lọc tiêu chí (Xử lý dòng đơn lẻ)
def check_spam(text):
    if pd.isna(text): return 1
    text = str(text).lower().strip()
    
    # Quảng cáo, link, SĐT, MXH
    if re.search(r'(0\d{9,10})|(\+84\d{9})', re.sub(r'[\s\.\-]', '', text)): return 1
    if re.search(r'(http|www\.|\.com|\.vn|\.net)', text): return 1
    if re.search(r'\b(zalo|facebook|fb|youtube|ytb|ig|instagram|tiktok)\b', text): return 1
        
    # Ký tự vô nghĩa, lặp lại (chỉ xét chữ cái)
    if re.search(r'([a-zđăâêôơư])\1{4,}', text): return 1
    words = text.split()
    if len(words) >= 3 and len(set(words)) == 1: return 1
        
    text_clean = re.sub(r'[^\w\s]', '', text).strip()
    
    # Quá ngắn
    if len(text_clean) < 3 and text_clean not in ['êm', 'ổn', 'ồn', 'tệ', 'dở']: 
        return 1
    if len(set(text_clean.replace(' ', ''))) == 2: return 1
    return 0

# 3. Tạo DataFrame chuẩn
df_labeled = pd.DataFrame()
df_labeled['category'] = df['phan_loai']
df_labeled['product'] = df['san_pham']
df_labeled['review'] = df['noi_dung']
df_labeled['rating'] = df['so_sao']

# Chạy bộ lọc mức độ câu
df_labeled['label'] = df['noi_dung'].apply(check_spam)

# Đếm số lần xuất hiện của cùng một nội dung review cho CÙNG 1 sản phẩm
df_labeled['review_lower_clean'] = df_labeled['review'].astype(str).str.lower().str.strip()
duplicates_count = df_labeled.groupby(['product', 'review_lower_clean'])['review_lower_clean'].transform('size')

# Tính tỷ lệ review trùng lặp trong tổng review của mỗi sản phẩm
product_total = df_labeled.groupby('product').size()
ratio = duplicates_count / df_labeled['product'].map(product_total)

# Cập nhật nhãn: Những review xuất hiện ở tỷ lệ >= 25% VÀ > 3 lần trong cùng 1 sản phẩm sẽ bị đánh spam
df_labeled.loc[(ratio >= 0.25) & (duplicates_count > 3), 'label'] = 1

# Xóa cột phụ
df_labeled = df_labeled.drop(columns=['review_lower_clean'])

# 4. Lưu ra file CSV mới
os.makedirs("data/labeled", exist_ok=True)
df_labeled.to_csv("data/labeled/reviews_labeled.csv", index=False, encoding='utf-8-sig')

print("Đã gán nhãn xong và lưu tại: data/labeled/reviews_labeled.csv")