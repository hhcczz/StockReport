from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# URL 리스트
Kor_Normal_url = "https://tossinvest.com/screener/kr"
Eng_Normal_url = "https://tossinvest.com/screener/us"

# Selenium을 사용하여 브라우저를 열고 페이지를 로드
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # 브라우저 창을 열지 않고 실행

# Chrome 옵션 설정
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # 브라우저 시작 시 최대화
# 다른 옵션 추가 가능
# options.add_argument("--headless")  # 브라우저를 숨기고 실행
options.add_argument("--disable-gpu")  # GPU 비활성화
options.add_argument("--no-sandbox")  # 샌드박스 비활성화
options.add_argument("--log-level=3")  # 로그 레벨 설정

# Chrome 드라이버 설치 및 초기화
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 이후 스크롤을 맨 위로 올리기 위해 JavaScript 코드 실행
driver.execute_script("window.scrollTo(0, 0);")

def getUrls(stock_type):
    return Kor_Normal_url if stock_type == "한국주식" else Eng_Normal_url

def get_stock_data():
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    StockArr = []
    for row in rows:
        try:
            # 각 셀의 데이터를 가져옵니다
            elementName = row.find_element(By.CSS_SELECTOR, "td.tw-z7dod50.hq5o4c3.hq5o4c5 > div > div > div > span").text
            elementCurrentWon = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) > div > span").text
            elementPercent = row.find_element(By.CSS_SELECTOR, "td:nth-child(3) > div > div > span:nth-child(1)").text
            elementRiseWon = row.find_element(By.CSS_SELECTOR, "td:nth-child(3) > div > div > span:nth-child(2)").text

            StockArr.append(
                {
                    "종목": elementName,
                    "원(￦)": elementCurrentWon,
                    "등락": elementRiseWon,
                    "전날대비": elementPercent
                }
            )
        except Exception as e:
            print(f"Error retrieving data for stock: {e}")
    return StockArr

def print_stock_data(new_data, old_data):
    for stock in new_data:
        if stock not in old_data:
            print(stock)

def scroll_and_get_stocks(stock_type):
    driver.get(getUrls(stock_type))  # URL로 이동

    time.sleep(1.5)  # 페이지 로드 대기

    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.5)  # 잠시 대기

    scroll_count = 0
    max_scrolls = 2
    all_stock_data = []  # 모든 데이터를 저장할 리스트

    while scroll_count < max_scrolls:
        print(f"Scroll {scroll_count + 1}")

        # 이전 데이터 길이 기록
        previous_row_count = len(all_stock_data)

        # 새로운 데이터 가져오기
        new_stock_data = get_stock_data()

        # 새로운 데이터만 추가 (중복 제거)
        for stock in new_stock_data:
            if stock not in all_stock_data:
                all_stock_data.append(stock)

        print_stock_data(new_stock_data, all_stock_data)  # 새로운 데이터만 출력

        # 스크롤을 수행합니다
        driver.execute_script("window.scrollBy(0, 1500);")
        time.sleep(1)  # 스크롤 후 잠시 대기

        try:
            # 새로 로드된 데이터가 있는지 확인
            WebDriverWait(driver, 10).until(
                lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "table tbody tr")) > previous_row_count
            )
        except Exception as e:
            print(f"Error waiting for new elements to load: {e}")
            break  # 예외 발생 시 루프 종료

        scroll_count += 1

    print(f"Final Stock Data: {all_stock_data}")  # 최종 데이터 확인
    return all_stock_data  # 모든 데이터를 반환
