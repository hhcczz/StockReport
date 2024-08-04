import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import re

# 한자 요일 변환 함수
def weekday_to_kanji(weekday):
    kanji_days = {
        "Sun": "日",
        "Mon": "月",
        "Tue": "火",
        "Wed": "水",
        "Thu": "木",
        "Fri": "金",
        "Sat": "土"
    }
    return kanji_days.get(weekday, "")

# 데이터 가져오는 함수
def get_stock_data(urls):
    stocks = []
    for url in urls:
        driver.get(url)
        # 버크셔 A만 오류남 아래는 버크셔 A Url
        if url == "https://tossinvest.com/stocks/US19800317002/order":
            css_selector_Won = "#__next > div > div.ho2myi1 > main > div > div > div > div.njzdl30 > div.njzdl31 > div._1sivumi0 > div:nth-child(2) > span:nth-child(1)"
            css_selector_Percent = "#__next > div > div.ho2myi1 > main > div > div > div > div.njzdl30 > div.njzdl31 > div._1sivumi0 > div:nth-child(2) > span:nth-child(3)"
            css_selector_NameKo = "#__next > div > div.ho2myi1 > main > div > div > div > div.njzdl30 > div.njzdl31 > div._1sivumi0 > div:nth-child(1) > span:nth-child(1)"
            css_selector_NameEng = "#__next > div > div.ho2myi1 > main > div > div > div > div.njzdl30 > div.njzdl31 > div._1sivumi0 > div:nth-child(1) > span:nth-child(2)"
        else:
            css_selector_Won = "#__next > div > div.ho2myi1 > main > div > div > div > div.njzdl30 > div > div._1sivumi0 > div:nth-child(2) > span:nth-child(1)"
            css_selector_Percent = "#__next > div > div.ho2myi1 > main > div > div > div > div.njzdl30 > div > div._1sivumi0 > div:nth-child(2) > span:nth-child(3)"
            css_selector_NameKo = "#__next > div > div.ho2myi1 > main > div > div > div > div.njzdl30 > div > div._1sivumi0 > div:nth-child(1) > span:nth-child(1)"
            css_selector_NameEng = "#__next > div > div.ho2myi1 > main > div > div > div > div.njzdl30 > div > div._1sivumi0 > div:nth-child(1) > span:nth-child(2)"

        try:
            # 특정 요소가 로드될 때까지 기다림 (최대 10초)
            elementWon = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector_Won))
            )

            elementPercent = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector_Percent))
            )

            elementNameKo = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector_NameKo))
            )

            elementNameEng = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector_NameEng))
            )

            # 요소의 텍스트를 가져옴
            elementWon_text = elementWon.text
            elementPercent_text = elementPercent.text
            
            # 등락률과 전날대비를 분리
            change, percent = re.findall(r'([-+]?\d+,?\d*원)\s*\(([-+]?\d+\.?\d*%)\)', elementPercent_text)[0]
            
            # stocks 리스트에 데이터 추가
            stocks.append({
                "종목": elementNameKo.text,
                "영문": elementNameEng.text,
                "원(￦)": elementWon.text,
                "등락": change,
                "전날대비": percent
            })

        except Exception as e:
            stocks.append({
                "종목": "Error",
                "영문": "Error",
                "원(￦)": f"Error - {str(e)}",
                "등락": "Error",
                "전날대비": "Error"
            })

    return stocks

# 이미지 생성 함수
def create_image(stocks, file_name):
    # 현재 날짜 및 시간 가져오기
    now = datetime.now()
    date_time_str = now.strftime("%Y-%m-%d (%a) - %H:%M:%S")

    # 표 데이터
    table_data = [
        ["종목", "영문", "원(￦)", "등락", "전날대비"]
    ] + [[stock["종목"], stock["영문"], stock["원(￦)"], stock["등락"], stock["전날대비"]] for stock in stocks]

    # 폰트 설정
    font_size = 20
    font = ImageFont.truetype("malgun.ttf", font_size)

    # 텍스트의 너비를 계산하는 함수
    def get_text_width(text, font):
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0]

    # 이미지 크기 계산
    cell_padding = 10
    date_time_height = font.getbbox(date_time_str)[3] - font.getbbox(date_time_str)[1] + cell_padding * 2
    column_widths = [max(get_text_width(cell, font) for cell in column) + cell_padding * 2 for column in zip(*table_data)]
    row_height = max(font.getbbox(cell)[3] - font.getbbox(cell)[1] for row in table_data for cell in row) + cell_padding * 2
    image_width = sum(column_widths) + 2 * cell_padding
    image_height = row_height * len(table_data) + date_time_height + 2 * cell_padding

    # 이미지 생성
    image = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(image)

    # 색상 설정
    red = (255, 0, 0)
    blue = (0, 0, 255)
    black = (0, 0, 0)

    # 날짜 및 시간 추가
    draw.text((cell_padding, cell_padding), date_time_str, fill=black, font=font)

    # 표 그리기
    y = date_time_height  # 날짜 및 시간의 높이만큼 아래에서 시작
    for row in table_data:
        x = 0
        색상 = None

        for i, cell in enumerate(row):
            cell_width = column_widths[i]
            cell_height = row_height
            draw.rectangle([x, y, x + cell_width, y + cell_height], outline="black")

            # 텍스트 색상 적용
            if i == 3:  # 등락 컬럼
                color = red if cell.startswith('+') else blue if cell.startswith('-') else black
                색상 = color
            elif i == 4:  # 전날대비 컬럼
                color = 색상 if 색상 is not None else black
            else:
                color = black

            draw.text((x + cell_padding, y + cell_padding), cell, fill=color, font=font)
            x += cell_width
        y += row_height

    # 바탕화면에 StockReport 폴더 생성
        
        # OneDrive 바탕화면 경로 가져오기
    one_drive_path = os.path.join(os.environ['USERPROFILE'], 'OneDrive')
    desktop_path = os.path.join(one_drive_path, '바탕 화면')  # 한글 경로 사용 시
    report_folder = os.path.join(desktop_path, "StockReport")

    # 폴더 생성
    os.makedirs(report_folder, exist_ok=True)

    # 이미지 저장
    image.save(os.path.join(report_folder, file_name))

# URL 목록
urls = [
    "https://tossinvest.com/stocks/US19990122001/order",
    "https://tossinvest.com/stocks/US19801212001/order",
    "https://tossinvest.com/stocks/US20100629001/order",
    "https://tossinvest.com/stocks/US19860313001/order",
    "https://tossinvest.com/stocks/US20040819001/order",
    "https://tossinvest.com/stocks/US20040819002/order",
    "https://tossinvest.com/stocks/US19970515001/order",
    "https://tossinvest.com/stocks/US20120518001/order",
    "https://tossinvest.com/stocks/US20100121001/order",
    "https://tossinvest.com/stocks/US19971008002/order",
    "https://tossinvest.com/stocks/US19700709001/order",
    "https://tossinvest.com/stocks/US20090806002/order",
    "https://tossinvest.com/stocks/US19690401002/order",
    "https://tossinvest.com/stocks/US19701001001/order",
    "https://tossinvest.com/stocks/US19911010002/order",
    "https://tossinvest.com/stocks/US20080319001/order",
    "https://tossinvest.com/stocks/US19200325001/order",
    "https://tossinvest.com/stocks/US19810709001/order",
    "https://tossinvest.com/stocks/US20060525001/order",
    "https://tossinvest.com/stocks/US19500322001/order",
    "https://tossinvest.com/stocks/US19440925001/order",
    "https://tossinvest.com/stocks/US19860312001/order",
    "https://tossinvest.com/stocks/US19851127001/order",
    "https://tossinvest.com/stocks/US19810922001/order",
    "https://tossinvest.com/stocks/US19950315001/order"
]

# ETF URL 목록
etf_urls = [
    "https://tossinvest.com/stocks/US19990310001/order?symbol-or-stock-code=A428560",
    "https://tossinvest.com/stocks/US20100211003/order",
    "https://tossinvest.com/stocks/US20100909007/order?symbol-or-stock-code=US20111006004",
    "https://tossinvest.com/stocks/NAS0221213008/order?symbol-or-stock-code=US19990310001",
    "https://tossinvest.com/stocks/NAS0230822004/order?symbol-or-stock-code=NAS0221213008",
    "https://tossinvest.com/stocks/US20100311002/order?symbol-or-stock-code=NAS0230822004",
    "https://tossinvest.com/stocks/US20100311003/order?symbol-or-stock-code=US20100311002",
    "https://tossinvest.com/stocks/US20220809007/order?symbol-or-stock-code=NAS0230822004",
    "https://tossinvest.com/stocks/US20081125005/order?symbol-or-stock-code=US20111006001",
    "https://tossinvest.com/stocks/US20111006001/order?symbol-or-stock-code=US20081125005",
    "https://tossinvest.com/stocks/US20111006004/order?symbol-or-stock-code=US20111006001",
    "https://tossinvest.com/stocks/US20220330008/order?",
    "https://tossinvest.com/stocks/AMX0240401004/order?",
    "https://tossinvest.com/stocks/US20201123016/order?",
    "https://tossinvest.com/stocks/NAS0231019003/order?",
    "https://tossinvest.com/stocks/US20220809012/order?symbol-or-stock-code=US20111020005",
    "https://tossinvest.com/stocks/NAS0231019002/order?symbol-or-stock-code=NAS0231019003",
    "https://tossinvest.com/stocks/NAS0231019003/order?symbol-or-stock-code=US20220809012",
    "https://tossinvest.com/stocks/US20220714009/order?symbol-or-stock-code=NAS0231019002",
    "https://tossinvest.com/stocks/US20111020005/order?",
]

# Selenium을 사용하여 브라우저를 열고 페이지를 로드
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 브라우저 창을 열지 않고 실행
options.add_argument("--log-level=3")  # 브라우저 로그 레벨을 설정하여 로그 출력 최소화

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 일반 주식 데이터 가져오기
stocks = get_stock_data(urls)

# ETF 데이터 가져오기
etf_stocks = get_stock_data(etf_urls)

# 현재 날짜 및 시간 가져오기
now = datetime.now()
weekday_kanji = weekday_to_kanji(now.strftime("%a"))

# 파일 이름 설정
file_name_stocks = now.strftime(f"%Y-%m-%d-({weekday_kanji}) - %H-%M-%S - 일반주식.png")
file_name_etf = now.strftime(f"%Y-%m-%d-({weekday_kanji}) - %H-%M-%S - ETF주식.png")

# 이미지 생성 및 저장
create_image(stocks, file_name_stocks)
create_image(etf_stocks, file_name_etf)
