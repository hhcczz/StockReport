import requests
import StockDB as DB  # StockDB 모듈에서 한국 주식 정보를 가져온다고 가정합니다.
from pprint import pprint  # 데이터 구조를 이쁘게 출력하기 위해 pprint 모듈을 임포트합니다.
import time

def fetch_stock_prices(stock_codes):
    chunk_size = 30
    prices = []

    for i in range(0, len(stock_codes), chunk_size):
        chunk = stock_codes[i:i + chunk_size]
        url = f"https://wts-info-api.tossinvest.com/api/v2/stock-prices/wts?codes={','.join(chunk)}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            prices.extend(data.get("result", {}).get("prices", []))  # 받은 데이터 추가
            
            # 요청한 종목 코드와 수신된 가격 데이터의 일치 여부 확인
            for code in chunk:
                if not any(price['code'] == code for price in prices):
                    print(f"Missing data for stock code: {code}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching stock prices: {e}")

    return prices

def process_stock_price_data(stock_data, stock_names):
    # 주어진 JSON 데이터에서 주식 가격 정보를 추출
    StockArr = []  # 주식 정보를 담을 리스트 초기화

    # stock_data는 prices 리스트 형태여야 함
    for price_info in stock_data:
        code = price_info.get("code")
        close = price_info.get("close")
        change_type = price_info.get("changeType")
        base = price_info.get("base")
        volume = price_info.get("volume")
        
        # 종목 이름 가져오기
        name = stock_names.get(code, "알 수 없는 종목")

        # 주식 정보를 StockArr에 추가
        StockArr.append(
            {
                "종목": name,
                "원(￦)": close,  # 현재 가격
                "등락": change_type,  # 변동 유형
                "전날대비": base  # 기준가 (전날 가격)
            }
        )

    return StockArr  # 최종적으로 StockArr 반환

# StockDB 모듈에서 종목 코드와 이름을 딕셔너리로 가져오기
stock_names = {stock["code"]: stock["name"] for stock in DB.korean_stocks}

# 종목 코드 리스트
stock_codes = list(stock_names.keys())

# 주식 가격 데이터 요청 및 처리
stock_data = fetch_stock_prices(stock_codes)

# 데이터가 올바르게 반환되었는지 확인
if stock_data:
    stock_info_array = process_stock_price_data(stock_data, stock_names)

    # 종목 정보를 시가총액 순으로 정렬 (여기서는 예시로 기준을 '원(￦)'로 하였으나, 실제 시가총액이 필요하면 추가 정보를 받아야 함)
    stock_info_array.sort(key=lambda x: x["원(￦)"], reverse=True)  # 가격 기준으로 내림차순 정렬

    # 번호와 함께 데이터 출력
    print("번호 | 종목      | 원(￦)    | 등락 | 전날대비")
    print("-" * 40)  # 구분선
    for index, stock in enumerate(stock_info_array, start=1):
        print(f"{index:>3} | {stock['종목']:>8} | {stock['원(￦)']:>8} | {stock['등락']:>4} | {stock['전날대비']:>8}")
else:
    print("주식 데이터를 불러오는 데 실패했습니다.")
