from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QCheckBox
from PyQt5.QtGui import QColor
import os
import csv
import json  # JSON 형식으로 저장하기 위해 필요

class FavoriteOption:
    def __init__(self, favorite_instance):
        self.favorite_instance = favorite_instance
        self.watchlist = []

        # 파일 경로 설정 (사용자 홈 디렉토리 내에 StockReport 폴더가 없으면 생성)
        stock_report_dir = os.path.join(os.path.expanduser(r"C:\Users\qimin\OneDrive\바탕 화면\Python\StockReport\DB"))
        os.makedirs(stock_report_dir, exist_ok=True)  # 경로가 없으면 생성

        # 관심 종목을 저장할 파일 경로 설정
        self.file_path = os.path.join(stock_report_dir, "favorite_stocks.csv")
        print(f"Saving to: {self.file_path}")  # 파일 경로 출력해서 확인

        # 체크박스 상태 파일 경로 설정
        self.checkbox_state_file_path = os.path.join(stock_report_dir, "checkbox_states.json")
        
        # 초기화 시 파일에서 관심 종목과 체크박스 상태를 로드
        self.loadWatchlistFromFile()
        self.loadCheckBoxStates()

    def saveWatchlistToFile(self):
        with open(self.file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for stock in self.watchlist:
                writer.writerow([stock['종목'], stock['원(￦)'], stock['등락'], stock['시작가']])

        # 미국 주식 (US_KRW 및 US_Dollar)도 동일하게 저장
        with open(self.file_path.replace("favorite_stocks.csv", "us_favorite_stocks.csv"), 'w', newline='', encoding='utf-8') as us_file:
            us_writer = csv.writer(us_file)
            for stock in self.watchlist:
                us_writer.writerow([stock['종목'], stock['원(￦)'], stock['등락'], stock['시작가']])

    def loadWatchlistFromFile(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 4:
                        self.watchlist.append({
                            "종목": row[0],
                            "원(￦)": row[1],
                            "등락": row[2],
                            "시작가": row[3]
                        })
            self.updateWatchlist()  # 파일에서 로드한 후 UI 업데이트
            
    def saveCheckBoxStates(self):
    # 체크박스 상태를 저장하는 함수
        checkbox_states = {
            'KR_CheckBoxBoolean': self.favorite_instance.KR_CheckBoxBoolean,
            'US_CheckBoxBoolean': self.favorite_instance.US_CheckBoxBoolean,
            'US_ETF_CheckBoxBoolean': self.favorite_instance.US_ETF_CheckBoxBoolean
        }
        with open(self.checkbox_state_file_path, 'w') as file:
            json.dump(checkbox_states, file)

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

    def saveWatchlistToFile(self):
        with open(self.file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for stock in self.watchlist:
                writer.writerow([stock['종목'], stock['원(￦)'], stock['등락'], stock['시작가']])

    def loadWatchlistFromFile(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 4:
                        self.watchlist.append({
                            "종목": row[0],
                            "원(￦)": row[1],
                            "등락": row[2],
                            "시작가": row[3]
                        })

        # 미국 주식 (US_KRW 및 US_Dollar)도 동일하게 로드
        us_file_path = self.file_path.replace("favorite_stocks.csv", "us_favorite_stocks.csv")
        if os.path.exists(us_file_path):
            with open(us_file_path, 'r', newline='', encoding='utf-8') as us_file:
                us_reader = csv.reader(us_file)
                for row in us_reader:
                    if len(row) == 4:
                        self.watchlist.append({
                            "종목": row[0],
                            "원(￦)": row[1],
                            "등락": row[2],
                            "시작가": row[3]
                        })

        self.updateWatchlist()  # 파일에서 로드한 후 UI 업데이트
            
    # 관심 종목 목록 업데이트
    def updateWatchlist(self):
        self.favorite_instance.tableWidget_2.setRowCount(0)  # 기존 행 제거
        for stock in self.watchlist:
            row_position = self.favorite_instance.tableWidget_2.rowCount()
            self.favorite_instance.tableWidget_2.insertRow(row_position)

            name_item = QTableWidgetItem(stock['종목'])
            price_str = str(stock.get('원(￦)', '0'))
            start_price_str = str(stock.get('시작가', '0'))

            if '.' in price_str:
                today_price = float(price_str)
                start_price = float(start_price_str)
                Today_Price_item = QTableWidgetItem(format(today_price, ",.2f"))
                RiseAndFalls_Percent_item = QTableWidgetItem(format(today_price - start_price, ",.2f"))
                Start_price_item = QTableWidgetItem(format(start_price, ",.2f"))
            else:
                today_price = int(price_str)
                start_price = int(start_price_str)
                Today_Price_item = QTableWidgetItem(format(today_price, ","))
                RiseAndFalls_Percent_item = QTableWidgetItem(format(today_price - start_price, ","))
                Start_price_item = QTableWidgetItem(format(start_price, ","))

            if start_price != 0:
                change_percent = ((today_price - start_price) / start_price) * 100
            else:
                change_percent = 0

            RiseAndFalls_Price_item = QTableWidgetItem(f"{change_percent:.2f}%")

            if stock['등락'].startswith('UP'):
                RiseAndFalls_Percent_item.setForeground(QColor("#f04452"))
                RiseAndFalls_Price_item.setForeground(QColor("#f04452"))
            elif stock['등락'].startswith('DOWN'):
                RiseAndFalls_Percent_item.setForeground(QColor("#3182f6"))
                RiseAndFalls_Price_item.setForeground(QColor("#3182f6"))
            else:
                RiseAndFalls_Percent_item.setForeground(QColor("#333d4b"))
                RiseAndFalls_Price_item.setForeground(QColor("#333d4b"))

            self.favorite_instance.tableWidget_2.setItem(row_position, 0, name_item)
            self.favorite_instance.tableWidget_2.setItem(row_position, 1, Today_Price_item)
            self.favorite_instance.tableWidget_2.setItem(row_position, 2, RiseAndFalls_Percent_item)
            self.favorite_instance.tableWidget_2.setItem(row_position, 3, RiseAndFalls_Price_item)
            self.favorite_instance.tableWidget_2.setItem(row_position, 4, Start_price_item)

    def addSelectedStockToFavorites(self):
        selected_row = self.favorite_instance.tableWidget.currentRow()  # 현재 선택된 행 가져오기
        if selected_row < 0:
            QMessageBox.warning(self.favorite_instance, "경고", "관심 종목을 선택해 주세요.")
            return  
    
        stock_name = self.favorite_instance.tableWidget.item(selected_row, 0).text()  # 선택된 주식의 이름 가져오기
        stock_data = self.favorite_instance.Save  # 현재 저장된 주식 데이터
    
        print(f"선택된 종목: {stock_name}")  # 디버깅 로그 추가
    
        if not any(stock['종목'] == stock_name for stock in self.watchlist):
            print("관심 종목에 추가합니다.")  # 디버깅 로그 추가
            self.addToWatchList(stock_data, stock_name)  # 주식 목록에 추가
            self.saveWatchlistToFile()  # 파일로 저장
            self.updateWatchlist()  # 관심 종목 목록 업데이트
        else:
            print("이미 관심 종목에 있습니다.")  # 디버깅 로그 추가

    def removeSelectedStockFromFavorites(self):
        selected_row = self.favorite_instance.tableWidget_2.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self.favorite_instance, "경고", "제거할 관심 종목을 선택해 주세요.")
            return  

        stock_name = self.favorite_instance.tableWidget_2.item(selected_row, 0).text()
        self.watchlist = [stock for stock in self.watchlist if stock['종목'] != stock_name]

        self.saveWatchlistToFile()  # 파일로 저장
        self.updateWatchlist()  # UI 업데이트

    def removeSelectedStockFromFavorites(self):
        selected_row = self.favorite_instance.tableWidget_2.currentRow()  # 관심 종목 목록에서 선택된 행 가져오기
        if selected_row < 0:
            QMessageBox.warning(self.favorite_instance, "경고", "제거할 관심 종목을 선택해 주세요.")
            return  

        stock_name = self.favorite_instance.tableWidget_2.item(selected_row, 0).text()  # 선택된 주식의 이름 가져오기
        # watchlist에서 해당 주식 제거
        self.watchlist = [stock for stock in self.watchlist if stock['종목'] != stock_name] 

        # 관심 종목 목록 갱신
        self.saveWatchlistToFile()  # 파일로 저장
        self.updateWatchlist()  # UI 업데이트   

        # 체크박스 상태 해제
        for row in range(self.favorite_instance.tableWidget.rowCount()):
            if self.favorite_instance.tableWidget.item(row, 0).text() == stock_name:
                widget = self.favorite_instance.tableWidget.cellWidget(row, 5)
                if widget is not None:
                    checkbox = widget.findChild(QCheckBox)
                    if checkbox:
                        checkbox.setChecked(False)  # 체크박스 해제
                break  # 해당 주식이 제거되었으므로 반복 종료

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
        if any(stock['종목'] == stock_name for stock in self.watchlist):
            QMessageBox.warning(self.favorite_instance, "경고", f"{stock_name}은 이미 관심 종목 목록에 있습니다.")
            return

        # 관심 종목 목록에 추가
        self.watchlist.append(stock_info)
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
        self.updateWatchlist()  # UI 업데이트
