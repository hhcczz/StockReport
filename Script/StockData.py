import requests
import StockDB as DB

def fetch_stock_data(stock_type):
    if stock_type == "KR":
        stock_names = {stock["code"]: {"name": stock["name"], "number": stock["number"]} for stock in DB.korean_stocks}
    elif stock_type == "US_KRW":
        stock_names = {stock["code"]: {"name": stock["name"], "number": stock["number"]} for stock in DB.US_stocks}
    elif stock_type == "US_Dollar":
        stock_names = {stock["code"]: {"name": stock["name"], "number": stock["number"]} for stock in DB.US_stocks}
    elif stock_type == "US_ETF_Dollar":
        stock_names = {stock["code"]: {"name": stock["name"], "number": stock["number"]} for stock in DB.US_ETF_stocks}
    elif stock_type == "US_ETF_KRW":
        stock_names = {stock["code"]: {"name": stock["name"], "number": stock["number"]} for stock in DB.US_ETF_stocks}
    
    stock_codes = list(stock_names.keys())
    stock_data = fetch_stock_prices(stock_codes)  # 주식 가격 데이터 요청
    return process_stock_price_data(stock_data, stock_names, stock_type)

def fetch_stock_prices(stock_codes):
    chunk_size = 10
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
            prices_chunk = data.get("result", {}).get("prices", [])
            prices.extend(prices_chunk)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching stock prices: {e}")

    return prices

def process_stock_price_data(stock_data, stock_names, stock_type):
    StockArr = []
    for price_info in stock_data:
        code = price_info.get("code")
        
        if stock_type in ["KR", "US_Dollar", "US_ETF_Dollar"]:
            close = price_info.get("close")
            base = price_info.get("base")
            if stock_type == "KR":
                close = str(int(float(close)))  # float를 int로 변환 후 문자열로 포맷
                base = str(int(float(base)))    # float를 int로 변환 후 문자열로 포맷
            # 달러로 표시되는 경우 소수점 2자리로 포맷팅
            elif stock_type in ["US_Dollar", "US_ETF_Dollar"]:
                close = f"{close:.2f}"
                base = f"{base:.2f}"
        elif stock_type in ["US_KRW", "US_ETF_KRW"]:
            close = price_info.get("closeKrw")
            base = price_info.get("baseKrw")
            # KRW 값은 소수점 없이 표시
            close = str(int(float(close)))  # float를 int로 변환 후 문자열로 포맷
            base = str(int(float(base)))    # float를 int로 변환 후 문자열로 포맷
        else:
            print("알 수 없는 통화 종류")
            close = "N/A"
            base = "N/A"

        change_type = price_info.get("changeType")
        stock_info = stock_names.get(code, {})
        name = stock_info.get("name", "알 수 없는 종목")
        number = stock_info.get("number", "N/A")

        StockArr.append({
            "number": number,
            "종목": name,
            "원(￦)": close,
            "등락": change_type,
            "시작가": base
        })

    return StockArr
