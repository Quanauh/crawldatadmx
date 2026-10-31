# Crawl và phân loại đánh giá Điện Máy Xanh

Project thu thập đánh giá sản phẩm trên Điện Máy Xanh và gán nhãn spam/ham bằng các quy tắc đơn giản. `ham` là đánh giá được giữ lại; nhãn này không khẳng định đánh giá chắc chắn là thật.

## Quy trình hoạt động

1. Cài Python và các thư viện `selenium`, `webdriver-manager`, `pandas`; máy cần có Chrome. Chạy `python main.py` từ thư mục project.
2. Chương trình mở Chrome. Người dùng mở trang sản phẩm Điện Máy Xanh trong cửa sổ đó, xử lý captcha nếu có, rồi nhấn Enter trong terminal để bắt đầu crawl. Có thể lặp lại với sản phẩm khác; nhập `0` để dừng.
3. `crawler/dmxcrawler.py` thử mở trang `/danh-gia`, duyệt các trang đánh giá hoặc bấm “Xem thêm”, rồi lấy danh mục, tên sản phẩm, người đánh giá, số sao, nội dung và URL. Trong cùng một phiên chạy, review có `data-comment-id` đã lấy sẽ được bỏ qua.
4. `storage/csv_storage.py` ghi nối các review vào `data/commentdienmayxanh.csv` với các cột `phan_loai,san_pham,nguoi_danh_gia,so_sao,noi_dung,link`. ID chỉ dùng để chống trùng trong phiên, không được ghi vào CSV. Các lần chạy khác nhau vẫn có thể tạo dòng trùng.
5. Chạy `python classify_reviews.py` để đọc toàn bộ file CSV gốc và tạo `data/labeled/reviews_spam_ham.csv`. File kết quả có cấu trúc `category,product,review,rating,label`, tương tự `data/labeled/reviews_labeled.csv`. Mỗi dòng đầu vào tạo đúng một dòng đầu ra, giữ nguyên thứ tự.

`phanloai.py` là script phân loại danh mục từ URL riêng; `labeled.py` là bộ gán nhãn cũ với quy tắc khác. Hai script này không nằm trong luồng `classify_reviews.py` và đang chứa đường dẫn tuyệt đối cần chỉnh khi chạy trên máy khác. Chạy lại `classify_reviews.py` sẽ ghi đè **file `reviews_spam_ham.csv`**; không sửa file gốc hoặc `reviews_labeled.csv`.

## Quy tắc gán nhãn trong `classify_reviews.py`

`label=1` (spam) khi nội dung thỏa ít nhất một điều kiện dưới đây:

- Nội dung rỗng, chỉ có dấu/emoji, hoặc dưới 2 ký tự chữ và số sau khi bỏ dấu câu, khoảng trắng.
- Toàn bộ nội dung chỉ là `ok` không phân biệt hoa thường, hoặc biến thể ngắn `okok`, `oki`, `oke`, `okay`; dấu câu và emoji đi kèm cũng bị bỏ qua. Ví dụ: `OK`, `ok.`, `Ok 👍` đều là spam. Câu có thêm nhận xét như `OK tốt` không bị gắn spam chỉ vì chứa chữ `ok`.
- Có số điện thoại dạng `0...` hoặc `+84...` theo mẫu trong mã, hoặc chứa `http://`, `https://`, `www.` hay tên miền `.com`, `.vn`, `.net`, `.org`.
- Có cùng một chữ cái lặp từ 5 lần liên tiếp, ví dụ `okkkkk`; hoặc có ít nhất 3 từ và tất cả các từ giống nhau, ví dụ `tốt tốt tốt`.
- Cùng một nội dung dài ít nhất 4 từ xuất hiện từ 4 lần trở lên ở **cùng sản phẩm**, đồng thời chiếm ít nhất 25% tổng review của sản phẩm đó. So sánh không phân biệt hoa thường và gom các khoảng trắng liên tiếp.

Các dòng còn lại nhận `label=0` (ham). Những nhận xét ngắn có nghĩa như `Tốt` được giữ là ham nếu không vi phạm quy tắc khác. Số sao không tham gia quyết định spam; được giữ lại để phân tích sau.

Đây là nhãn tạo tự động theo quy tắc, có thể có cả nhầm spam và bỏ sót spam. Nên kiểm tra mẫu thủ công trước khi dùng file để huấn luyện hoặc đánh giá mô hình.
