# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QMessageBox, QCheckBox, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QDialog, QTableWidget
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QFont, QFontDatabase
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
import textwrap  # 종목 이름을 줄이는 데 사용

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
        uic.loadUi('C:/Users/U308-13/OneDrive/바탕 화면/StockReport/tablewidgetTest.ui', self)
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
        # 현재 스크롤 위치 저장
        current_scroll_pos = self.tableWidget.verticalScrollBar().value()

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

        # 저장된 스크롤 위치로 복원
        self.tableWidget.verticalScrollBar().setValue(current_scroll_pos)

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

        # 폰트 설정
        font_path = "C:\\Users\\U308-13\\Desktop\\강원교육모두B.ttf"
        try:
            font = ImageFont.truetype(font_path, 18)
            header_font = ImageFont.truetype(font_path, 24, encoding="unic")
        except IOError:
            # 폰트 파일을 찾을 수 없을 경우 기본 폰트 사용
            font = ImageFont.load_default()
            header_font = ImageFont.load_default()

        # 각 관심 종목 그룹에 대해 별도로 이미지를 생성하고 저장
        for group_name, group_data in [
            ("KR", self.Favorite_instance.watchlist_kr),
            ("US", self.Favorite_instance.watchlist_us),
            ("ETF", self.Favorite_instance.watchlist_etf)
        ]:
            if group_data:
                # 이미지 크기 및 백그라운드 설정
                image_width = 650  # 이미지 너비 고정
                row_height = 42  # 원래 크기에서 30% 줄인 크기
                image_height = 100 + len(group_data) * row_height  # 데이터 양에 따라 이미지 높이 조절
                background_color = "#17171c"
                img = Image.new('RGBA', (image_width, image_height), color=background_color)
                draw = ImageDraw.Draw(img)

                # 헤더 텍스트 작성
                draw.text((10, 10), header_text, font=header_font, fill="#e4e4e5")

                # 표의 시작 위치
                table_start_y = 60
                # 각 열의 최대 너비 계산
                headers = ["    ", "종목", "현재가", "등락(￦)", "등락(%)"]

                # 종목 열의 너비를 크게 설정
                stock_col_width = max(draw.textbbox((0, 0), headers[1], font=font)[2], 
                                      max(draw.textbbox((0, 0), stock['종목'], font=font)[2] for stock in group_data)) + 100

                # 나머지 열의 너비를 고정
                fixed_col_widths = [
                    row_height,  # 사진 열의 너비는 이미지 크기와 동일
                    stock_col_width,  # 종목 열의 너비
                    max(draw.textbbox((0, 0), headers[2], font=font)[2], 100) + 20,  # 현재가 열 너비
                    max(draw.textbbox((0, 0), headers[3], font=font)[2], 100) + 20,  # 등락(￦) 열 너비
                    max(draw.textbbox((0, 0), headers[4], font=font)[2], 100) + 20,  # 등락(%) 열 너비
                ]

                # 전체 너비가 700이 되도록 열 너비 조정
                total_fixed_width = sum(fixed_col_widths)
                if total_fixed_width > image_width:
                    scale_factor = image_width / total_fixed_width
                    fixed_col_widths = [width * scale_factor for width in fixed_col_widths]

                # 각 열의 시작 X 좌표 계산
                col_start_x = [sum(fixed_col_widths[:i]) + 10 for i in range(len(fixed_col_widths))]

                # 표 헤더 작성
                for i, header in enumerate(headers):
                    draw.text((col_start_x[i], table_start_y), header, font=font, fill="#e4e4e5")

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
                    rise_and_falls_percent = f"{change_percent:.2f}%"  # 등락(%) 계산

                    # 종목 이름 줄이기 (예: 40자 이상이면 "..."로 축약)
                    stock_name = textwrap.shorten(stock['종목'], width=40, placeholder="...")

                    # 이미지 삽입 (종목 이미지 로드)
                    img_url = ImageLink.get(stock['종목'])
                    if img_url:
                        modified_url = img_url.replace("256x0", f"{row_height}x{row_height}")
                        response = requests.get(modified_url)
                        logo = Image.open(BytesIO(response.content)).convert('RGBA')
                        logo = logo.resize((row_height, row_height), Image.Resampling.LANCZOS)
                        img_x = col_start_x[0]
                        img_y = table_start_y + (row_idx + 1) * row_height
                        img.paste(logo, (img_x - 10, img_y - 10), logo)  # 투명도 유지

                    # 각 셀에 텍스트 작성
                    draw.text((col_start_x[1], table_start_y + (row_idx + 1) * row_height), stock_name, font=font, fill="#e4e4e5")
                    draw.text((col_start_x[2], table_start_y + (row_idx + 1) * row_height), f"{today_price:,.0f}원", font=font, fill="#e4e4e5")
                    draw.text((col_start_x[3], table_start_y + (row_idx + 1) * row_height), rise_and_falls_won, font=font,
                              fill="#f04452" if price_change > 0 else "#3182f6")
                    draw.text((col_start_x[4], table_start_y + (row_idx + 1) * row_height), rise_and_falls_percent, font=font,
                              fill="#f04452" if price_change > 0 else "#3182f6")

                # 테두리 그리기
                for row_idx in range(len(group_data) + 1):
                    for col_idx in range(len(headers)):
                        x0 = col_start_x[col_idx] - 10
                        y0 = table_start_y + row_idx * row_height - 10
                        x1 = col_start_x[col_idx] + fixed_col_widths[col_idx] - 10
                        y1 = table_start_y + (row_idx + 1) * row_height - 10

                        # 테두리 두께를 3으로 설정하여 진하게 그리기
                        draw.rectangle([x0, y0, x1, y1], outline="black", width=1)

                # 파일 이름 설정 및 저장
                filename = f"{current_date} ({weekday}) - {current_time} - {group_name}주식.png"
                filepath = os.path.join(stock_report_dir, filename)
                img.save(filepath)

                QMessageBox.information(self, "정보", f"{group_name} 그룹의 종목 이미지가 저장되었습니다: {filepath}")

    def loadStockData(self):
        self.dataLoader.start()  # 백그라운드 스레드 시작

def DrawStock(self, Data):
    # 외부 폰트 파일 등록
    font_db = QFontDatabase()
    font_id = font_db.addApplicationFont("C:\\Users\\U308-13\\Desktop\\강원교육모두B.ttf")
    font_family = font_db.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"
    
    # 등록된 폰트 설정
    font = QFont(font_family, 10)  # 폰트 크기 10
    header_font = QFont(font_family, 12, QFont.Bold)  # 폰트 크기 12, Bold
    
    self.tableWidget.setRowCount(0)  
    sorted_data = sorted(Data, key=lambda stock: stock.get('number', 0))
    
    for row_position, stock in enumerate(sorted_data):
        self.tableWidget.insertRow(row_position)  # 새로운 행 추가

        # 종목 데이터
        name_item = QTableWidgetItem(stock['종목'])
        name_item.setForeground(QColor("#e4e4e5"))  # 색상 변경
        name_item.setFont(font)  # 폰트 설정

        # stock['원(￦)']와 stock['시작가'] 값을 가져오고 None일 경우 기본값을 설정
        price_str = str(stock.get('원(￦)', '0'))
        start_price_str = str(stock.get('시작가', '0'))

        # 소수점 여부에 따라 처리 분기
        if '.' in price_str:  # 소수점이 있는 경우 (USD)
            today_price = float(price_str)
            start_price = float(start_price_str)
            Today_Price_item = QTableWidgetItem(f" {format(today_price, ',.2f')}")
            Start_price_item = QTableWidgetItem(f" {format(start_price, ',.2f')}")
        else:  # 소수점이 없는 경우 (KRW)
            today_price = int(price_str)
            start_price = int(start_price_str)
            Today_Price_item = QTableWidgetItem(f" {format(today_price, ',')}")
            Start_price_item = QTableWidgetItem(f" {format(start_price, ',')}")

        # 색상 설정
        Today_Price_item.setForeground(QColor("#e4e4e5"))  # 색상 변경
        Start_price_item.setForeground(QColor("#e4e4e5"))  # 색상 변경
        Today_Price_item.setFont(font)  # 폰트 설정
        Start_price_item.setFont(font)  # 폰트 설정

        # 등락(￦) 계산
        price_change = today_price - start_price
        if price_change > 0:
            price_change_str = f"+{price_change:,.0f}"
        else:
            price_change_str = f"{price_change:,.0f}"
        
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
        if price_change > 0:
            RiseAndFalls_Price_item.setForeground(QColor("#f04452"))
            RiseAndFalls_Percent_item.setForeground(QColor("#f04452"))
        else:
            RiseAndFalls_Price_item.setForeground(QColor("#3182f6"))
            RiseAndFalls_Percent_item.setForeground(QColor("#3182f6"))

        RiseAndFalls_Price_item.setFont(font)  # 폰트 설정
        RiseAndFalls_Percent_item.setFont(font)  # 폰트 설정

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

        # 데이터 항목 추가
        self.tableWidget.setItem(row_position, 0, name_item)
        self.tableWidget.setItem(row_position, 1, Today_Price_item)
        self.tableWidget.setItem(row_position, 2, RiseAndFalls_Price_item)
        self.tableWidget.setItem(row_position, 3, RiseAndFalls_Percent_item)
        self.tableWidget.setItem(row_position, 4, Start_price_item)

# 애플리케이션 실행
app = QApplication(sys.argv)
dialog = MyDialog()
dialog.show()
sys.exit(app.exec_())
