import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import re

def scrape_millionaire_final():
    url = "https://millionaire.fandom.com/wiki/Ai_L%C3%A0_Tri%E1%BB%87u_Ph%C3%BA"
    scraper = cloudscraper.create_scraper()
    
    print("🌐 Đang kết nối và tải dữ liệu từ Wiki...")
    
    try:
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', class_='wikitable')
        
        results = []

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                # Lấy tất cả văn bản trong các ô của hàng đó
                cells = [c.get_text(" ", strip=True) for c in row.find_all(['td', 'th'])]
                row_text = " ".join(cells)
                
                # 1. Tìm năm (từ 2005 đến 2026)
                year_match = re.search(r'(200[5-9]|201[0-9]|202[0-6])', row_text)
                
                if year_match:
                    year_val = int(year_match.group(1))
                    q_found = None
                    
                    # 2. Tìm số câu hỏi trong hàng đó
                    # Ưu tiên các định dạng như "Câu 14", "15/15", "Mốc 10"
                    special_match = re.search(r'(?:Câu|Mốc|vượt qua|đạt)\s*(\d+)|(\d+)\s*/\s*15', row_text, re.IGNORECASE)
                    
                    if special_match:
                        # Lấy group nào có số (1 hoặc 2)
                        q_found = special_match.group(1) if special_match.group(1) else special_match.group(2)
                    else:
                        # Nếu không thấy chữ "Câu", tìm số lẻ loi từ 1-15 (nhưng né các số quá nhỏ hoặc tiền thưởng)
                        # Thường số câu hỏi nằm ở các ô ngắn
                        for cell in cells:
                            # Nếu ô chỉ chứa số hoặc "số (chữ)", ví dụ "14 (Thắng)"
                            clean_cell = re.search(r'^(\d{1,2})(\s||\(|$)', cell)
                            if clean_cell:
                                num = int(clean_cell.group(1))
                                if 1 <= num <= 15:
                                    q_found = num
                                    break
                    
                    if q_found:
                        results.append(int(q_found))

        if not results:
            print("❌ Vẫn không tìm thấy dữ liệu. Có thể do trang web chặn truy cập nội dung bảng.")
            return

        # Xử lý và vẽ biểu đồ
        print(f"✅ Đã tìm thấy {len(results)} bản ghi người chơi tiêu biểu.")
        df = pd.DataFrame(results, columns=['Question'])
        counts = df['Question'].value_counts().sort_index()
        final_counts = pd.Series(0, index=range(1, 16)).add(counts, fill_value=0)

        plt.figure(figsize=(12, 6), facecolor='#f0f0f0')
        colors = plt.cm.Blues(final_counts.values / (max(final_counts.values) + 5))
        bars = plt.bar(final_counts.index, final_counts.values, color=colors, edgecolor='#003366', linewidth=1.2)
        
        plt.title('THỐNG KÊ MỐC CÂU HỎI CỦA NGƯỜI CHƠI TIÊU BIỂU (2005 - 2026)', fontsize=14, fontweight='bold', color='#003366')
        plt.xlabel('Mốc câu hỏi đạt được', fontsize=12)
        plt.ylabel('Số lượng người chơi', fontsize=12)
        plt.xticks(range(1, 16))
        plt.grid(axis='y', linestyle='--', alpha=0.5)

        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1, int(height), ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"🔥 Lỗi: {e}")

if __name__ == "__main__":
    scrape_millionaire_final()
