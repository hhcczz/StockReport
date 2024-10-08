# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QCheckBox
from PyQt5.QtGui import QColor, QFont, QFontDatabase, QIcon, QPixmap
from PyQt5.QtCore import Qt
import os
import csv
import json  # JSON 형식으로 저장하기 위해 필요

class FavoriteOption:
    def __init__(self, favorite_instance):
        self.favorite_instance = favorite_instance
        self.watchlist_kr = []  # 국내 주식 관심 종목
        self.watchlist_us = []  # 미국 주식 관심 종목
        self.watchlist_etf = []  # 미국 ETF 관심 종목

        # 실행 파일이 위치한 디렉토리에 StockReport 폴더 생성
        current_dir = os.path.dirname(os.path.abspath(__file__))
        stock_report_dir = os.path.join(current_dir, "DB")
        os.makedirs(stock_report_dir, exist_ok=True)  # 경로가 없으면 생성

        # 관심 종목을 저장할 파일 경로 설정
        self.file_path = os.path.join(stock_report_dir, "favorite_stocks.csv")
        self.checkbox_state_file_path = os.path.join(stock_report_dir, "checkbox_states.json")

        # 체크박스 상태 파일 경로 설정
        self.checkbox_state_file_path = os.path.join(stock_report_dir, "checkbox_states.json")# 열 헤더 숨기기

        # 초기화 시 파일에서 관심 종목과 체크박스 상태를 로드
        self.loadWatchlistFromFile()
        self.loadCheckBoxStates()

    def saveWatchlistToFile(self):
        # 국내 주식 관심 종목을 저장
        with open(self.file_path.replace("favorite_stocks.csv", "favorite_stocks_kr.csv"), 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for stock in self.watchlist_kr:
                writer.writerow([stock['종목'], stock['원(￦)'], stock['등락'], stock['시작가']])
    
        # 미국 주식 관심 종목을 저장
        with open(self.file_path.replace("favorite_stocks.csv", "favorite_stocks_us.csv"), 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for stock in self.watchlist_us:
                writer.writerow([stock['종목'], stock['원(￦)'], stock['등락'], stock['시작가']])
    
        # 미국 ETF 관심 종목을 저장
        with open(self.file_path.replace("favorite_stocks.csv", "favorite_stocks_etf.csv"), 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for stock in self.watchlist_etf:
                writer.writerow([stock['종목'], stock['원(￦)'], stock['등락'], stock['시작가']])
    
        print("관심 종목이 그룹별로 저장되었습니다.")

    def loadWatchlistFromFile(self):
        if os.path.exists(self.file_path.replace("favorite_stocks.csv", "favorite_stocks_kr.csv")):
            with open(self.file_path.replace("favorite_stocks.csv", "favorite_stocks_kr.csv"), 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 4:
                        stock = {
                            "종목": row[0],
                            "원(￦)": row[1],
                            "등락": row[2],
                            "시작가": row[3]
                        }
                        self.watchlist_kr.append(stock)
        
        if os.path.exists(self.file_path.replace("favorite_stocks.csv", "favorite_stocks_us.csv")):
            with open(self.file_path.replace("favorite_stocks.csv", "favorite_stocks_us.csv"), 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 4:
                        stock = {
                            "종목": row[0],
                            "원(￦)": row[1],
                            "등락": row[2],
                            "시작가": row[3]
                        }
                        self.watchlist_us.append(stock)
        
        if os.path.exists(self.file_path.replace("favorite_stocks.csv", "favorite_stocks_etf.csv")):
            with open(self.file_path.replace("favorite_stocks.csv", "favorite_stocks_etf.csv"), 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 4:
                        stock = {
                            "종목": row[0],
                            "원(￦)": row[1],
                            "등락": row[2],
                            "시작가": row[3]
                        }
                        self.watchlist_etf.append(stock)

        self.updateWatchlist(self.favorite_instance.ThisStockPage)  # 파일에서 로드한 후 UI 업데이트

    def saveCheckBoxStates(self):
        # 체크박스 상태를 저장하는 함수
        checkbox_states = {
            'KR_CheckBoxBoolean': self.favorite_instance.KR_CheckBoxBoolean,
            'US_CheckBoxBoolean': self.favorite_instance.US_CheckBoxBoolean,
            'US_ETF_CheckBoxBoolean': self.favorite_instance.US_ETF_CheckBoxBoolean
        }
        with open(self.checkbox_state_file_path, 'w') as file:
            json.dump(checkbox_states, file, indent=4)  # 들여쓰기를 위해 indent=4 추가

        # 관심 종목 목록도 저장
        self.saveWatchlistToFile()
        
    def loadCheckBoxStates(self):
        # 체크박스 상태를 로드하는 함수
        if os.path.exists(self.checkbox_state_file_path):
            with open(self.checkbox_state_file_path, 'r') as file:
                checkbox_states = json.load(file)
                self.favorite_instance.KR_CheckBoxBoolean = checkbox_states.get('KR_CheckBoxBoolean', [False] * 200)
                self.favorite_instance.US_CheckBoxBoolean = checkbox_states.get('US_CheckBoxBoolean', [False] * 200)
                self.favorite_instance.US_ETF_CheckBoxBoolean = checkbox_states.get('US_ETF_CheckBoxBoolean', [False] * 200)

    def getWatchlistForCurrentPage(self, page):
        if page == "KR":
            return self.watchlist_kr
        elif page in ["US_KRW", "US_Dollar"]:
            return self.watchlist_us
        elif page in ["US_ETF_Dollar", "US_ETF_KRW"]:
            return self.watchlist_etf
        else:
            return []

    def updateWatchlist(self, page):
        # 외부 폰트 파일 등록
        font_db = QFontDatabase()

        # 현재 파일의 디렉토리 경로를 가져옵니다.
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 폰트 파일의 전체 경로를 만듭니다.
        font_path = os.path.join(current_dir, '강원교육모두B.ttf')

        font_id = font_db.addApplicationFont(font_path)
        font_family = font_db.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"

        # 등록된 폰트 설정
        font = QFont(font_family, 10)  # 폰트 크기 10
        self.favorite_instance.tableWidget_2.setRowCount(0)  # 기존 행 제거
        watchlist = self.getWatchlistForCurrentPage(page)
        for stock in watchlist:
            row_position = self.favorite_instance.tableWidget_2.rowCount()
            self.favorite_instance.tableWidget_2.insertRow(row_position)

            # 이미지 추가
            image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'your_image_file.png')
            icon = QTableWidgetItem()
            icon.setIcon(QIcon(image_path))  # 이미지 아이콘 설정
            self.favorite_instance.tableWidget_2.setItem(row_position, 0, icon)  # 첫 번째 열에 이미지 설정

            # 종목 데이터
            name_item = QTableWidgetItem(stock['종목'])
            name_item.setForeground(QColor("#c3c3c6"))  # 색상 변경
            name_item.setFont(font)  # 폰트 설정

            price_str = str(stock.get('원(￦)', '0'))
            start_price_str = str(stock.get('시작가', '0'))

            if '.' in price_str:  # 소수점이 있는 경우 (USD)
                today_price = float(price_str)
                start_price = float(start_price_str)
                Today_Price_item = QTableWidgetItem(f" {today_price:,.2f}")
                Start_price_item = QTableWidgetItem(f" {start_price:,.2f}")
            else:  # 소수점이 없는 경우 (KRW)
                today_price = int(price_str)
                start_price = int(start_price_str)
                Today_Price_item = QTableWidgetItem(f" {today_price:,}")
                Start_price_item = QTableWidgetItem(f" {start_price:,}")

            # 등락(￦) 계산
            price_change = today_price - start_price
            if price_change > 0:
                price_change_str = f"+{price_change:,.2f}" if '.' in price_str else f"+{price_change:,}"
            else:
                price_change_str = f"{price_change:,.2f}" if '.' in price_str else f"{price_change:,}"

            # 등락(%) 계산
            if start_price != 0:
                change_percent = ((today_price - start_price) / start_price) * 100
            else:
                change_percent = 0

            # 등락(%) 포맷팅
            percent_change_str = f"{change_percent:+.2f}%"

            # 새로운 QTableWidgetItem 객체 생성
            RiseAndFalls_Price_item = QTableWidgetItem(f" {price_change_str}")
            RiseAndFalls_Percent_item = QTableWidgetItem(f" {percent_change_str}")

            # 색상 설정
            if change_percent > 6.0:
                color = QColor("#ff0015")
            elif change_percent > 3.0:
                color = QColor("#f32b3b")
            elif change_percent > 0:
                color = QColor("#f04452")
            elif change_percent < -6.0:
                color = QColor("#0068ff")
            elif change_percent < -3.0:
                color = QColor("#1b75f7")
            elif change_percent < 0:
                color = QColor("#3182f6")
            else:
                color = QColor("#c3c3c6")

            # 색상 및 폰트 적용
            RiseAndFalls_Price_item.setForeground(color)
            RiseAndFalls_Price_item.setFont(font)
            RiseAndFalls_Percent_item.setForeground(color)
            RiseAndFalls_Percent_item.setFont(font)
            

            # 이미지 추가
            pixmap = load_image(stock['종목'])
            icon = QTableWidgetItem()
            icon.setIcon(QIcon(pixmap))
            self.favorite_instance.tableWidget_2.setItem(row_position, 0, icon)  # 첫 번째 열에 이미지 설정

            # 나머지 데이터 항목 설정
            self.favorite_instance.tableWidget_2.setItem(row_position, 1, name_item)
            self.favorite_instance.tableWidget_2.setItem(row_position, 2, Today_Price_item)
            self.favorite_instance.tableWidget_2.setItem(row_position, 3, RiseAndFalls_Price_item)
            self.favorite_instance.tableWidget_2.setItem(row_position, 4, RiseAndFalls_Percent_item)
            self.favorite_instance.tableWidget_2.setItem(row_position, 5, Start_price_item)

    def addSelectedStockToFavorites(self):
        selected_row = self.favorite_instance.tableWidget.currentRow()  # 현재 선택된 행 가져오기
        if selected_row < 0:
            QMessageBox.warning(self.favorite_instance, "경고", "관심 종목을 선택해 주세요.")
            return  

        stock_name = self.favorite_instance.tableWidget.item(selected_row, 0).text()  # 선택된 주식의 이름 가져오기
        stock_data = self.favorite_instance.Save  # 현재 저장된 주식 데이터

        if not any(stock['종목'] == stock_name for stock in self.getWatchlistForCurrentPage(self.favorite_instance.ThisStockPage)):
            self.addToWatchList(stock_data, stock_name)  # 주식 목록에 추가

            # 체크박스 상태 저장
            if self.favorite_instance.ThisStockPage == "KR":
                self.favorite_instance.KR_CheckBoxBoolean[selected_row] = True
            elif self.favorite_instance.ThisStockPage in ["US_Dollar", "US_KRW"]:
                self.favorite_instance.US_CheckBoxBoolean[selected_row] = True
            elif self.favorite_instance.ThisStockPage in ["US_ETF_Dollar", "US_ETF_KRW"]:
                self.favorite_instance.US_ETF_CheckBoxBoolean[selected_row] = True

            # 파일로 저장 및 체크박스 상태 저장
            self.saveWatchlistToFile()  # 파일로 저장
            self.saveCheckBoxStates()  # 체크박스 상태 저장
            self.updateWatchlist(self.favorite_instance.ThisStockPage)  # 관심 종목 목록 업데이트
        else:
            print("이미 관심 종목에 있습니다.")  # 디버깅 로그 추가

    def removeSelectedStockFromFavorites(self, stock_name=None):
        print("removeSelectedStockFromFavorites 호출됨")  # 디버깅 로그 추가

        if not stock_name:
            selected_row = self.favorite_instance.tableWidget_2.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self.favorite_instance, "경고", "제거할 관심 종목을 선택해 주세요.")
                return
            stock_name = self.favorite_instance.tableWidget_2.item(selected_row, 0).text()

        # watchlist에서 해당 주식 제거
        found = False
        watchlist = self.getWatchlistForCurrentPage(self.favorite_instance.ThisStockPage)
        for stock in watchlist:
            if stock['종목'].strip().lower() == stock_name.strip().lower():  # 대소문자와 공백을 무시한 비교
                watchlist.remove(stock)
                found = True
                print(f"{stock_name}이(가) watchlist에서 제거되었습니다.")
                break

        if not found:
            print(f"{stock_name}이(가) watchlist에서 제거되지 않았습니다.")
            return  # 주식이 리스트에서 제거되지 않았으면 더 이상 진행하지 않음

        # 모든 행을 탐색하여 일치하는 종목의 체크박스 상태를 업데이트
        for row in range(self.favorite_instance.tableWidget.rowCount()):
            item = self.favorite_instance.tableWidget.item(row, 0)
            if item is not None and item.text().strip().lower() == stock_name.strip().lower():
                if self.favorite_instance.ThisStockPage == "KR":
                    self.favorite_instance.KR_CheckBoxBoolean[row] = False
                elif self.favorite_instance.ThisStockPage in ["US_Dollar", "US_KRW"]:
                    self.favorite_instance.US_CheckBoxBoolean[row] = False
                elif self.favorite_instance.ThisStockPage in ["US_ETF_Dollar", "US_ETF_KRW"]:
                    self.favorite_instance.US_ETF_CheckBoxBoolean[row] = False

                # 테이블에서 체크박스 상태 해제 (UI 업데이트)
                widget = self.favorite_instance.tableWidget.cellWidget(row, 5)
                if widget is not None:
                    checkbox = widget.findChild(QCheckBox)
                    if checkbox is not None:
                        checkbox.setChecked(False)
                break  # 해당 종목을 찾았으면 루프 종료

        # 관심 종목 목록 갱신 및 상태 저장
        self.saveWatchlistToFile()  # 파일로 저장
        self.saveCheckBoxStates()  # 체크박스 상태 저장
        self.updateWatchlist(self.favorite_instance.ThisStockPage)  # UI 업데이트

        print(f"{stock_name}이(가) 관심 종목에서 제거되었습니다.")  # 디버깅 로그 추가

    def addToWatchList(self, stockData, stock_name=None):
        print("addToWatchList 호출")  # 디버깅 로그
        if stockData is None or not isinstance(stockData, list):
            QMessageBox.warning(self.favorite_instance, "경고", "주식 데이터가 유효하지 않습니다.")
            return

        if stock_name is None:
            stock_name = self.favorite_instance.line_insertItem.text().strip()  # line_insertItem 접근

        stock_info = next((item for item in stockData if item['종목'] == stock_name), None)

        # 주식 정보가 있는지 확인
        if stock_info is None:
            QMessageBox.warning(self.favorite_instance, "경고", f"{stock_name}의 정보를 찾을 수 없습니다.")
            return

        # 이미 관심 종목 목록에 있는지 확인
        if any(stock['종목'] == stock_name for stock in self.getWatchlistForCurrentPage(self.favorite_instance.ThisStockPage)):
            QMessageBox.warning(self.favorite_instance, "경고", f"{stock_name}은 이미 관심 종목 목록에 있습니다.")
            return

        # 관심 종목 목록에 추가
        if self.favorite_instance.ThisStockPage == "KR":
            self.watchlist_kr.append(stock_info)
        elif self.favorite_instance.ThisStockPage in ["US_KRW", "US_Dollar"]:
            self.watchlist_us.append(stock_info)
        elif self.favorite_instance.ThisStockPage in ["US_ETF_Dollar", "US_ETF_KRW"]:
            self.watchlist_etf.append(stock_info)
        
        QMessageBox.information(self.favorite_instance, "정보", f"{stock_name}이(가) 관심 종목 목록에 추가되었습니다.")

        # 체크박스 체크
        row_count = self.favorite_instance.tableWidget.rowCount()
        for row in range(row_count):
            if self.favorite_instance.tableWidget.item(row, 0).text() == stock_name:
                widget = self.favorite_instance.tableWidget.cellWidget(row, 5)
                if widget is not None:
                    checkbox = widget.findChild(QCheckBox)
                    if checkbox:
                        checkbox.setChecked(True)  # 체크박스 체크

        # 관심 종목 및 체크박스 상태 저장
        self.saveWatchlistToFile()  # 파일로 저장
        self.saveCheckBoxStates()  # 체크박스 상태 저장
        self.updateWatchlist(self.favorite_instance.ThisStockPage)  # UI 업데이트

# Helper function to load the image
def load_image(stock_name):
    # 절대 경로를 사용하여 경로를 설정합니다
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, 'cache_images', f"{stock_name}.png")
    pixmap = QPixmap(image_path)
    
    if pixmap.isNull():
        print(f"Warning: Unable to load image for stock: {stock_name}")
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.gray)
    
    return pixmap
