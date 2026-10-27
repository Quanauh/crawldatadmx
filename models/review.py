class Review:
    def __init__(
        self,
        review_id,      # Vẫn giữ ở đây để crawler dùng check trùng
        text,
        rating,
        username,
        product_name,
        source_url,
        category="Khác"
    ):
        self.review_id = review_id
        self.text = text
        self.rating = rating
        self.username = username
        self.product_name = product_name
        self.source_url = source_url
        self.category = category

    def to_dict(self):
        # Trả về dict KHÔNG có review_id để lúc lưu CSV không bị dính vào
        return {
            "phan_loai": self.category,
            "noi_dung": self.text,
            "so_sao": self.rating,
            "nguoi_danh_gia": self.username,
            "san_pham": self.product_name,
            "link": self.source_url
        }