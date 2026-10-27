import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)

from models.review import Review


def _get_category_from_url(url):
    """Phân loại sản phẩm dựa trên URL của Điện Máy Xanh."""
    if not url: return "Khác"
    
    url = url.lower()
    if "may-giat" in url: return "Máy giặt"
    elif "dieu-hoa" in url or "may-lanh" in url: return "Điều hòa"
    elif "tu-lanh" in url: return "Tủ lạnh"
    elif "may-say-quan-ao" in url or "may-say" in url: return "Máy sấy quần áo"
    elif "tivi" in url: return "Tivi"
    elif "may-loc-nuoc" in url: return "Máy lọc nước"
    elif "noi-com-dien" in url: return "Nồi cơm điện"
    elif "may-loc-khong-khi" in url: return "Máy lọc không khí"
    elif "bep-dien" in url: return "Bếp điện"
    elif "camera-giam-sat" in url: return "Camera giám sát"
    
    return "Khác"


def _get_review_id(item):
    """Lấy ID duy nhất của bình luận từ thuộc tính data-comment-id."""
    try:
        return item.get_attribute("data-comment-id")
    except (StaleElementReferenceException, WebDriverException):
        return None


def _get_review_text(item):
    try:
        nodes = item.find_elements(By.CSS_SELECTOR, ":scope > p:nth-child(3)")
        for node in nodes:
            value = node.text.strip()
            if value:
                return value
    except (StaleElementReferenceException, WebDriverException):
        pass
    return None


def _get_username(item):
    try:
        node = item.find_element(By.CSS_SELECTOR, ":scope > p.gap-10px.flex > span:nth-child(1)")
        username = node.text.strip()
        return username if username else None
    except (StaleElementReferenceException, WebDriverException):
        return None


def _get_rating(item):
    try:
        stars = item.find_elements(By.CSS_SELECTOR, "i[class*='icon__row-6-col-1']")
        count = len(stars)
        if 1 <= count <= 5:
            return count
    except (StaleElementReferenceException, WebDriverException):
        pass
    return None


def _get_review_items(driver):
    try:
        return driver.find_elements(By.CSS_SELECTOR, "div[id^='cmt-'][data-comment-id]")
    except (StaleElementReferenceException, WebDriverException):
        return []


def _load_more_reviews(driver, max_click=50):
    print("\nĐang load thêm review (Chế độ 1 trang)...")
    for click_index in range(max_click):
        xpaths = [
            "//button[contains(normalize-space(.), 'Xem thêm')]",
            "//a[contains(normalize-space(.), 'Xem thêm')]",
            "//*[self::button or self::a][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'xem thêm')]",
        ]
        candidates = []
        seen_ids = set()

        for xpath in xpaths:
            try:
                for element in driver.find_elements(By.XPATH, xpath):
                    try:
                        element_id = element.id
                        if element_id not in seen_ids:
                            seen_ids.add(element_id)
                            candidates.append(element)
                    except Exception:
                        continue
            except Exception:
                continue

        clicked = False
        for button in candidates:
            try:
                if not button.is_displayed() or not button.is_enabled():
                    continue

                label = button.text.strip().casefold()
                if "xem thêm" not in label:
                    continue

                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(0.4)

                try:
                    ActionChains(driver).move_to_element(button).click().perform()
                except Exception:
                    driver.execute_script("arguments[0].click();", button)

                print(f"Đã bấm Xem thêm lần {click_index + 1}: {label}")
                time.sleep(1.2)
                clicked = True
                break
            except (StaleElementReferenceException, WebDriverException):
                continue
            except Exception:
                continue

        if not clicked:
            print("Không tìm thấy nút Xem thêm phù hợp hoặc không còn nút.")
            break


def _click_next_page(driver):
    try:
        css_selector = r"body > div.bg-gray-0.\!bg-white > div:nth-child(4) > main > div > div.mt-16px.text-12.flex.items-center.justify-center.gap-1 > button:last-child"
        buttons = driver.find_elements(By.CSS_SELECTOR, css_selector)
        
        for btn in buttons:
            if btn.is_displayed() and btn.is_enabled():
                class_attr = btn.get_attribute("class") or ""
                if "disable" in class_attr.lower() or "text-gray" in class_attr.lower():
                    continue
                    
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(0.5)
                
                try:
                    ActionChains(driver).move_to_element(btn).click().perform()
                except Exception:
                    driver.execute_script("arguments[0].click();", btn)
                    
                return True
    except Exception as e:
        print("Không thể chuyển trang:", e)
        
    return False


def crawl_dmx_reviews(driver, scraped_review_ids=None): 
    """Crawl review từ trang sản phẩm Điện Máy Xanh đang mở trong Selenium."""
    all_reviews = []
    
    # Khởi tạo bộ nhớ lưu ID của các đánh giá (nếu chưa có)
    if scraped_review_ids is None:
        scraped_review_ids = set()

    print("\n========== DIEN MAY XANH - REVIEW CRAWLER ==========")
    print(
        """
Hãy thực hiện:
1. Mở trang sản phẩm cần crawl trên Điện Máy Xanh.
2. Vượt captcha nếu có (CHƯA CẦN tự kéo xuống bấm Xem thêm).
3. Quay lại terminal và nhấn Enter, Tool sẽ tự động xử lý tất cả!
"""
    )
    input(">>> Sẵn sàng crawl thì nhấn Enter...")
    time.sleep(2)

    try:
        product_url = driver.current_url
    except WebDriverException as error:
        print("Không thể lấy URL vì Selenium đã mất kết nối:", error)
        return all_reviews

    print("-> Bắt đầu phân tích trang...\n")

    # =========================================================
    # TỰ ĐỘNG BẤM TÌM TRANG "/DANH-GIA"
    # =========================================================
    print("[TỰ ĐỘNG] Đang kiểm tra xem có thể chuyển sang trang /danh-gia không...")
    for i in range(2):
        if "/danh-gia" in driver.current_url.lower():
            print("-> Phát hiện đã ở trang /danh-gia.")
            break
            
        print(f"Thử tìm và bấm nút 'Xem tất cả / Xem thêm' (lần {i+1}/2)...")
        elements = driver.find_elements(By.CSS_SELECTOR, "a, button") 
        clicked = False
        
        for el in elements:
            try:
                if not el.is_displayed() or not el.is_enabled():
                    continue
                
                text = el.text.strip().lower()
                is_valid = ("xem thêm" in text) or ("xem tất cả" in text) or ("xem" in text and "đánh giá" in text)
                
                if is_valid and len(text) < 35: 
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                    time.sleep(0.5)
                    
                    try:
                        ActionChains(driver).move_to_element(el).click().perform()
                    except:
                        driver.execute_script("arguments[0].click();", el)
                        
                    print(f"-> Đã click vào nút: '{text}'")
                    time.sleep(3) 
                    clicked = True
                    break
            except:
                continue
                
        if not clicked:
            print("-> Không tìm thấy thêm nút chuyển trang nào.")
            break

    # =========================================================
    # BẮT ĐẦU CÀO DỮ LIỆU
    # =========================================================
    product_url = driver.current_url
    product_category = _get_category_from_url(product_url)
    
    print("\nĐang lấy tên sản phẩm...")
    product_name = None
    name_selectors = [
        r"body > div.bg-gray-0.pb-\[98px\] > div:nth-child(4) > main > div.pt-2.pb-9.flex.flex-wrap.gap-2.items-center > h1",
        r"body > div.bg-gray-0.\!bg-white > div:nth-child(4) > main > div > div.gap-10.flex.flex-col > div.text-26.font-700.w-full.shrink-0",
        "h1" 
    ]
    for selector in name_selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            text = element.text.strip()
            if text:
                product_name = text
                break
        except Exception:
            continue

    if not product_name:
        print("Cảnh báo: Không lấy được tên sản phẩm.")

    print("\nSản phẩm:", product_name)
    print("Phân loại:", product_category)
    print("URL:", product_url)

    def _extract_current_page_reviews():
        review_elements = _get_review_items(driver)
        extracted_count = 0
        skipped_count = 0
        
        for item in review_elements:
            try:
                # Lấy ID của review
                review_id = _get_review_id(item)
                
                # CHẶN TRÙNG LẶP: Bỏ qua nếu đánh giá này đã được cào
                if not review_id or review_id in scraped_review_ids:
                    skipped_count += 1
                    continue

                username = _get_username(item)
                text = _get_review_text(item)

                if not text:
                    continue

                rating = _get_rating(item)

                review = Review(
                    review_id=review_id,
                    text=text,
                    rating=rating,
                    username=username,
                    product_name=product_name,
                    source_url=product_url,
                    category=product_category
                )

                all_reviews.append(review)
                scraped_review_ids.add(review_id)  # Lưu ID này vào sổ
                extracted_count += 1
                
                print(f"[{len(all_reviews)}] (ID: {review_id}) {username} - {rating} sao: {text[:40]}...")
            except (StaleElementReferenceException, WebDriverException):
                pass
            except Exception as e:
                print("Lỗi bóc tách review:", e)
                
        if skipped_count > 0:
            print(f"-> Đã bỏ qua {skipped_count} review bị trùng lặp.")
            
        return extracted_count

    is_danh_gia_page = "/danh-gia" in product_url.lower()

    if is_danh_gia_page:
        print("\n=== CHẾ ĐỘ: CÀO NHIỀU TRANG (/danh-gia) ===")
        page_num = 1
        while True:
            print(f"\n--- Đang cào trang {page_num} ---")
            time.sleep(1.5) 
            
            _extract_current_page_reviews()
            
            if not _click_next_page(driver):
                print(">>> Đã đến trang cuối cùng.")
                break
                
            page_num += 1
            time.sleep(2) 
    else:
        print("\n=== CHẾ ĐỘ: CÀO 1 TRANG (Sản phẩm ít review) ===")
        _load_more_reviews(driver)
        print("\nĐang bóc tách danh sách review...")
        _extract_current_page_reviews()

    print(f"\n========== HOÀN THÀNH ==========")
    print(f"Mới cào thêm được: {len(all_reviews)} review không trùng lặp.")
    return all_reviews