from utils.driver_setup import create_driver
from crawler.dmxcrawler import crawl_dmx_reviews
from storage.csv_storage import save_to_csv
from config.settings import OUTPUT_FILE

def main():
    driver = create_driver()
    all_reviews = []
    
    # ĐỔI TÊN BỘ NHỚ: Lưu các ID đánh giá đã cào trong phiên này thay vì URL
    scraped_review_ids = set()

    try:
        while True:
            print("\n========================================")
            print("Mở sản phẩm cần crawl trên trình duyệt.")
            print("- Nhấn Enter để crawl sản phẩm hiện tại")
            print("- Nhập 0 để dừng")
            print("========================================")

            choice = input(">>> Lựa chọn: ").strip()

            if choice == "0":
                break

            # CẬP NHẬT THAM SỐ: Truyền scraped_review_ids vào hàm crawler
            reviews = crawl_dmx_reviews(driver, scraped_review_ids=scraped_review_ids)
            all_reviews.extend(reviews)

            print(f"Tổng review đang giữ trong RAM (không trùng lặp): {len(all_reviews)}")

        save_to_csv(all_reviews, OUTPUT_FILE)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()