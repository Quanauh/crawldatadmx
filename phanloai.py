import pandas as pd
import re

file_path = r"C:\Users\Admin\OneDrive\Desktop\commentdienmayxanh3.csv"
output_path = r"C:\Users\Admin\OneDrive\Desktop\commentdienmayxanh_daphanloai.csv"

# 1. Đọc file CSV: Thử lần lượt các bảng mã phổ biến, không dùng 'replace' để giữ nguyên vẹn ký tự
encodings_to_try = ['utf-8', 'cp1258', 'utf-16', 'latin1']
df = None

for enc in encodings_to_try:
    try:
        df = pd.read_csv(file_path, encoding=enc)
        print(f"Đã đọc file thành công với chuẩn: {enc}")
        break
    except UnicodeDecodeError:
        continue

# 2. Hàm trích xuất và phân loại từ link
def phan_loai_tu_link(link):
    if not isinstance(link, str):
        return "Khác"
    
    match = re.search(r'dienmayxanh\.com/([^/]+)/', link)
    if match:
        slug = match.group(1)
        category_mapping = {
            'may-giat': 'Máy giặt',
            'may-lanh': 'Điều hòa',
            'dieu-hoa': 'Điều hòa',
            'tu-lanh': 'Tủ lạnh',
            'may-say-quan-ao': 'Máy sấy quần áo',
            'tivi': 'Tivi',
            'may-loc-nuoc': 'Máy lọc nước'
        }
        return category_mapping.get(slug, slug.replace('-', ' ').capitalize())
    return "Khác"

# 3. Áp dụng phân loại
df['phan_loai'] = df['link'].apply(phan_loai_tu_link)

# 4. Xuất file với utf-8-sig (giúp Excel/WPS tự nhận diện Tiếng Việt)
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"Hoàn tất! Hãy mở file {output_path} để kiểm tra.")