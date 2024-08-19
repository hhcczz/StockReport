# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QMessageBox, QCheckBox, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QDialog, QTableWidget
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5 import uic
import sys
import StockData as SD  # 주식 데이터 처리 모듈
from Search import Search 
from Favorite import FavoriteOption
from datetime import datetime
import os
from PIL import Image
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from ImageSet import ImageLink  # ImageSet.py에서 ImageSet을 불러옴

Save = []

class StockDataLoader(QThread):
    dataLoaded = pyqtSignal(list)

    def __init__(self, dialog_instance):
        super().__init__()
        self.dialog_instance = dialog_instance  # MyDialog 인스턴스를 참조

    def run(self):
        stock_data = SD.fetch_stock_data(self.dialog_instance.ThisStockPage)  # MyDialog 인스턴스를 통해 ThisStockPage에 접근
        global Save
        Save = stock_data
        self.dataLoaded.emit(stock_data)

class MyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ThisStockPage = "KR"  # 기본 시장 설정을 한국으로
        self.KR_CheckBoxBoolean = [False] * 200
        self.US_CheckBoxBoolean = [False] * 200
        self.US_ETF_CheckBoxBoolean = [False] * 200
        
        self.search_instance = Search(self)
        
        self.setupUi()  # UI 설정 초기화
        
        self.Favorite_instance = FavoriteOption(self)
        
        self.Favorite_Add.clicked.connect(self.Favorite_instance.addSelectedStockToFavorites)
        self.Favorite_Remove.clicked.connect(self.Favorite_instance.removeSelectedStockFromFavorites)
        
        self.dataLoader = StockDataLoader(self)  # MyDialog 인스턴스를 전달
        self.dataLoader.dataLoaded.connect(self.updateTable)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadStockData)
        self.timer.start(10000)
        self.loadStockData()
        self.Save = []

        self.finished.connect(self.Favorite_instance.saveCheckBoxStates)  # 윈도우가 닫힐 때 체크박스 상태 저장

    def setupUi(self):
        uic.loadUi('C:/Users/qimin/OneDrive/바탕 화면/Python/StockReport/tablewidgetTest.ui', self)
        self.tableWidget.setRowCount(0)  # 기존 테이블 행 제거
        self.KR_Won.clicked.connect(self.Select_Kor_Market)  # 국내
        self.US_KRW.clicked.connect(self.Select_US_KRWMarket)  # 해외 원화
        self.US_Dollar.clicked.connect(self.Select_US_DollarMarket)  # 해외 달러
        self.US_ETF.clicked.connect(self.Select_US_ETFMarket)  # 해외 ETF 달러
        self.btn_insertItem.clicked.connect(self.search_instance.searchStock)  # 검색 버튼 클릭 시 기능 연결
        self.pushButton.clicked.connect(self.Select_US_KRWETFMarket) # 해외 ETF 원화
        self.popular_searchitem.clicked.connect(self.MakeGraph)

        self.tableWidget_2 = self.findChild(QTableWidget, "tableWidget_2")
        if not self.tableWidget_2:
            print("Error: tableWidget_2 could not be loaded")

        self.tableWidget.cellClicked.connect(self.checkBoxStateChanged)  # 체크박스 클릭 시 기능 연결
        self.tableWidget.setColumnWidth(5, 20)  # 첫 번째 열 크기 고정
        self.tableWidget.setColumnWidth(0, 200)  # 첫 번째 열 크기 고정

    def closeEvent(self, event):
        # 윈도우가 닫힐 때 체크박스 상태 저장
        self.Favorite_instance.saveCheckBoxStates()
        event.accept()
            
    # Update 주식
    def updateTable(self, stock_data):
        self.Save = stock_data  # Save에 로드된 데이터를 저장
        if not stock_data:
            QMessageBox.warning(self, "정보", "현재 주식 데이터가 없습니다.")
            return

        # 주식 데이터를 테이블에 그리기
        DrawStock(self, stock_data)

        # 관심 종목 업데이트
        for stock in self.Favorite_instance.getWatchlistForCurrentPage(self.ThisStockPage):
            updated_stock = next((item for item in stock_data if item['종목'] == stock['종목']), None)
            if updated_stock:
                stock.update(updated_stock)  # 관심 종목의 정보를 업데이트

        self.Favorite_instance.updateWatchlist(self.ThisStockPage)  # 관심 종목 목록 갱신
        self.addCheckBoxesToTable()  # 체크박스 상태 유지

    def addCheckBoxesToTable(self):
        for row in range(self.tableWidget.rowCount()):
            checkbox = QCheckBox()

            # 현재 페이지에 따라 체크박스 상태를 설정
            if self.ThisStockPage == "KR":
                checkbox.setChecked(self.KR_CheckBoxBoolean[row])
            elif self.ThisStockPage in ["US_Dollar", "US_KRW"]:
                checkbox.setChecked(self.US_CheckBoxBoolean[row])
            elif self.ThisStockPage in ["US_ETF_Dollar", "US_ETF_KRW"]:
                checkbox.setChecked(self.US_ETF_CheckBoxBoolean[row])

            checkbox.stateChanged.connect(self.checkBoxStateChanged)  # 체크박스 상태 변경 시 기능 연결

            # 레이아웃을 사용하여 체크박스를 중앙에 배치
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignCenter)  # 중앙 정렬
            layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
            widget.setLayout(layout)

            self.tableWidget.setCellWidget(row, 5, widget)  # 체크박스는 6번째 열에 추가

    def checkBoxStateChanged(self, state):
        sender_checkbox = self.sender()  # 신호를 보낸 체크박스를 확인
        for row in range(self.tableWidget.rowCount()):
            widget = self.tableWidget.cellWidget(row, 5)
            if widget is not None:
                checkbox = widget.findChild(QCheckBox)
                if checkbox == sender_checkbox:
                    stock_name = self.tableWidget.item(row, 0).text()  # 주식 이름 가져오기
                    if state == Qt.Checked:
                        # 종목이 이미 관심 목록에 있는지 확인
                        if not any(stock['종목'] == stock_name for stock in self.Favorite_instance.getWatchlistForCurrentPage(self.ThisStockPage)):
                            if self.ThisStockPage == "KR":
                                self.KR_CheckBoxBoolean[row] = True
                            elif self.ThisStockPage in ["US_Dollar", "US_KRW"]:
                                self.US_CheckBoxBoolean[row] = True
                            elif self.ThisStockPage in ["US_ETF_Dollar", "US_ETF_KRW"]:
                                self.US_ETF_CheckBoxBoolean[row] = True

                            self.Favorite_instance.addToWatchList(self.Save, stock_name)  # 관심 종목 추가
                    else:
                        if self.ThisStockPage == "KR":
                            self.KR_CheckBoxBoolean[row] = False
                        elif self.ThisStockPage in ["US_Dollar", "US_KRW"]:
                            self.US_CheckBoxBoolean[row] = False
                        elif self.ThisStockPage in ["US_ETF_Dollar", "US_ETF_KRW"]:
                            self.US_ETF_CheckBoxBoolean[row] = False

                        self.Favorite_instance.removeSelectedStockFromFavorites(stock_name)  # 관심 종목에서 제거

                    # 관심 종목 목록 및 체크박스 상태 저장
                    self.Favorite_instance.updateWatchlist(self.ThisStockPage)  # 관심 종목 목록 업데이트
                    self.Favorite_instance.saveCheckBoxStates()  # 체크박스 상태 저장
                    break

    def Select_Kor_Market(self):
        self.ThisStockPage = "KR"
        self.loadStockData()  # 데이터 로드

    def Select_US_KRWMarket(self):
        self.ThisStockPage = "US_KRW"
        self.loadStockData()  # 데이터 로드

    def Select_US_DollarMarket(self):
        self.ThisStockPage = "US_Dollar"
        self.loadStockData()  # 데이터 로드

    def Select_US_ETFMarket(self):
        self.ThisStockPage = "US_ETF_Dollar"
        self.loadStockData()  # 데이터 로드

    def Select_US_KRWETFMarket(self):
        self.ThisStockPage = "US_ETF_KRW"
        self.loadStockData()  # 데이터 로드
        
    def MakeGraph(self):
        # 오늘 날짜와 시간 가져오기
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H-%M-%S")
        weekday_kr = ["월", "화", "수", "목", "금", "토", "일"]
        weekday = weekday_kr[datetime.today().weekday()]
        header_text = f"{current_date} ({weekday}) - {now.strftime('%H:%M:%S')}"

        # 바탕화면에 StockReport 폴더 생성
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        stock_report_dir = os.path.join(desktop_path, "StockReport", current_date)
        os.makedirs(stock_report_dir, exist_ok=True)

        # "맑은 고딕" 폰트 설정
        font_path = "C:/Windows/Fonts/malgun.ttf"
        font = ImageFont.truetype(font_path, 18)
        header_font = ImageFont.truetype(font_path, 24, encoding="unic")

        # 각 관심 종목 그룹에 대해 별도로 이미지를 생성하고 저장
        for group_name, group_data in [
            ("KR", self.Favorite_instance.watchlist_kr),
            ("US", self.Favorite_instance.watchlist_us),
            ("ETF", self.Favorite_instance.watchlist_etf)
        ]:
            if group_data:
                # 이미지 크기 및 백그라운드 설정
                image_width = 700
                row_height = 42  # 원래 크기에서 30% 줄인 크기
                image_height = 100 + len(group_data) * row_height  # 데이터 양에 따라 이미지 높이 조절
                background_color = "white"
                img = Image.new('RGB', (image_width, image_height), color=background_color)
                draw = ImageDraw.Draw(img)

                # 헤더 텍스트 작성
                draw.text((10, 10), header_text, font=header_font, fill="black")

                # 표의 시작 위치
                table_start_y = 60
                # 각 열의 최대 너비 계산
                headers = ["    ", "종목", "현재가", "등락(￦)", "등락(%)"]
                col_widths = [
                    row_height,  # 사진 열의 너비는 이미지 크기와 동일
                    max(draw.textbbox((0, 0), headers[1], font=font)[2], max(draw.textbbox((0, 0), stock['종목'], font=font)[2] for stock in group_data)) + 200,
                    max(draw.textbbox((0, 0), headers[2], font=font)[2], max(draw.textbbox((0, 0), f"{stock['원(￦)']}원", font=font)[2] for stock in group_data)) + 20,
                    max(draw.textbbox((0, 0), headers[3], font=font)[2], max(draw.textbbox((0, 0), f"{float(stock['원(￦)'].replace(',', '').replace('원', '').strip()) - float(stock['시작가'].replace(',', '').replace('원', '').strip()):+,.0f}원", font=font)[2] for stock in group_data)) + 20,
                    max(draw.textbbox((0, 0), headers[4], font=font)[2], max(draw.textbbox((0, 0), f"{(float(stock['원(￦)'].replace(',', '').replace('원', '').strip()) - float(stock['시작가'].replace(',', '').replace('원', '').strip())) / float(stock['시작가'].replace(',', '').replace('원', '').strip()) * 100:.2f}%", font=font)[2] for stock in group_data)) + 20,
                ]
                col_start_x = [sum(col_widths[:i]) + 10 for i in range(len(col_widths))]  # 각 열의 시작 X 좌표

                # 표 헤더 작성
                for i, header in enumerate(headers):
                    draw.text((col_start_x[i], table_start_y), header, font=font, fill="black")

                # 표 데이터 작성
                for row_idx, stock in enumerate(group_data):
                    today_price = float(stock['원(￦)'].replace(',', '').replace('원', '').strip())
                    start_price = float(stock['시작가'].replace(',', '').replace('원', '').strip())
                    if start_price != 0:
                        change_percent = ((today_price - start_price) / start_price) * 100
                    else:
                        change_percent = 0

                    price_change = today_price - start_price
                    rise_and_falls_won = f"{price_change:+,.0f}원"  # 등락(￦) 계산
                    rise_and_falls_percent = f"{change_percent:.2f}%"

                    stock_name = stock['종목'][:15] + '...' if len(stock['종목']) > 15 else stock['종목']

                    # 이미지 삽입 (종목 이미지 로드)
                    img_url = ImageLink.get(stock['종목'])
                    if img_url:
                        modified_url = img_url.replace("256x0", f"{row_height}x{row_height}")
                        response = requests.get(modified_url)
                        logo = Image.open(BytesIO(response.content))
                        logo = logo.resize((row_height, row_height), Image.Resampling.LANCZOS)
                        img_x = col_start_x[0]
                        img_y = table_start_y + (row_idx + 1) * row_height
                        img.paste(logo, (img_x - 10, img_y - 10))

                    # 각 셀에 텍스트 작성
                    draw.text((col_start_x[1], table_start_y + (row_idx + 1) * row_height), stock_name, font=font, fill="black")
                    draw.text((col_start_x[2], table_start_y + (row_idx + 1) * row_height), f"{today_price:,.0f}원", font=font, fill="black")
                    draw.text((col_start_x[3], table_start_y + (row_idx + 1) * row_height), rise_and_falls_won, font=font,
                              fill="#f04452" if price_change > 0 else "#3182f6")
                    draw.text((col_start_x[4], table_start_y + (row_idx + 1) * row_height), rise_and_falls_percent, font=font,
                              fill="#f04452" if price_change > 0 else "#3182f6")

                # 테두리 그리기
                for row_idx in range(len(group_data) + 1):
                    for col_idx in range(len(headers)):
                        x0 = col_start_x[col_idx] - 10
                        y0 = table_start_y + row_idx * row_height - 10
                        x1 = col_start_x[col_idx] + col_widths[col_idx] - 10
                        y1 = table_start_y + (row_idx + 1) * row_height - 10
                        draw.rectangle([x0, y0, x1, y1], outline="black")

                # 파일 이름 설정 및 저장
                filename = f"{current_date} ({weekday}) - {current_time} - {group_name}주식.png"
                filepath = os.path.join(stock_report_dir, filename)
                img.save(filepath)

                QMessageBox.information(self, "정보", f"{group_name} 그룹의 종목 이미지가 저장되었습니다: {filepath}")

    def loadStockData(self):
        self.dataLoader.start()  # 백그라운드 스레드 시작

def DrawStock(self, Data):
    self.tableWidget.setRowCount(0)  
    sorted_data = sorted(Data, key=lambda stock: stock.get('number', 0))
    
    for row_position, stock in enumerate(sorted_data):
        self.tableWidget.insertRow(row_position)  # 새로운 행 추가

        name_item = QTableWidgetItem(stock['종목'])

        # stock['원(￦)']와 stock['시작가'] 값을 가져오고 None일 경우 기본값을 설정
        price_str = str(stock.get('원(￦)', '0'))
        start_price_str = str(stock.get('시작가', '0'))

        # 소수점 여부에 따라 처리 분기
        if '.' in price_str:  # 소수점이 있는 경우 (USD)
            today_price = float(price_str)
            start_price = float(start_price_str)
            Today_Price_item = QTableWidgetItem(format(today_price, ",.2f"))
            RiseAndFalls_Percent_item = QTableWidgetItem(format(today_price - start_price, ",.2f"))
            Start_price_item = QTableWidgetItem(format(start_price, ",.2f"))
        else:  # 소수점이 없는 경우 (KRW)
            today_price = int(price_str)
            start_price = int(start_price_str)
            Today_Price_item = QTableWidgetItem(format(today_price, ","))
            RiseAndFalls_Percent_item = QTableWidgetItem(format(today_price - start_price, ","))
            Start_price_item = QTableWidgetItem(format(start_price, ","))

        # 기존 체크박스 상태 가져오기
        if self.ThisStockPage == "KR":
            checkbox_checked = self.KR_CheckBoxBoolean[row_position]
        elif self.ThisStockPage in ["US_Dollar", "US_KRW"]:
            checkbox_checked = self.US_CheckBoxBoolean[row_position]
        elif self.ThisStockPage in ["US_ETF_Dollar", "US_ETF_KRW"]:
            checkbox_checked = self.US_ETF_CheckBoxBoolean[row_position]

        # 체크박스 생성 및 상태 설정
        checkbox = QCheckBox()
        checkbox.setChecked(checkbox_checked)
        checkbox.stateChanged.connect(self.checkBoxStateChanged)

        # 레이아웃을 사용하여 체크박스를 중앙에 배치
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignCenter)  # 중앙 정렬
        layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
        widget.setLayout(layout)
    
        self.tableWidget.setCellWidget(row_position, 5, widget)  # 체크박스는 6번째 열에 추가

        if start_price != 0:  # 전날 가격이 0이 아닌 경우
            change_percent = ((today_price - start_price) / start_price) * 100
        else:
            change_percent = 0  # 전날 가격이 0일 경우 변경률은 0으로 설정

        RiseAndFalls_Price_item = QTableWidgetItem(f"{change_percent:.2f}%")  # 소수점 두 자리로 포맷팅

        if stock['등락'].startswith('UP'):
            RiseAndFalls_Percent_item.setForeground(QColor("#f04452"))
            RiseAndFalls_Price_item.setForeground(QColor("#f04452"))
        elif stock['등락'].startswith('DOWN'):
            RiseAndFalls_Percent_item.setForeground(QColor("#3182f6"))
            RiseAndFalls_Price_item.setForeground(QColor("#3182f6"))
        else:
            RiseAndFalls_Percent_item.setForeground(QColor("#333d4b"))
            RiseAndFalls_Price_item.setForeground(QColor("#333d4b"))

        self.tableWidget.setItem(row_position, 0, name_item)
        self.tableWidget.setItem(row_position, 1, Today_Price_item)
        self.tableWidget.setItem(row_position, 2, RiseAndFalls_Percent_item)
        self.tableWidget.setItem(row_position, 3, RiseAndFalls_Price_item)
        self.tableWidget.setItem(row_position, 4, Start_price_item)

# 애플리케이션 실행
app = QApplication(sys.argv)
dialog = MyDialog()
dialog.show()
sys.exit(app.exec_())
