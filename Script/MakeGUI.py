# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QMessageBox, QCheckBox, QWidget, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5 import uic
import sys
import StockData as SD  # 주식 데이터 처리 모듈
from Search import Search 
from Favorite import FavoriteOption

Save = []
ThisStockPage = "KR"  # 기본 시장 설정을 한국으로

class StockDataLoader(QThread):
    dataLoaded = pyqtSignal(list)

    def run(self):
        global Save
        stock_data = SD.fetch_stock_data(ThisStockPage)  # 데이터 가져오기
        Save = stock_data
        self.dataLoaded.emit(stock_data)

class MyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.KR_CheckBoxBoolean = [False] * 200  # 체크박스 상태를 저장하는 리스트
        self.US_CheckBoxBoolean = [False] * 200
        self.watchlist = []  # 관심 종목 리스트 초기화
        self.search_instance = Search(self)  # Search 클래스의 인스턴스 생성
        self.Favorite_instance = FavoriteOption(self)
        self.dataLoader = StockDataLoader()  # StockDataLoader 인스턴스 생성
        self.dataLoader.dataLoaded.connect(self.updateTable)  # dataLoaded 시그널을 updateTable 슬롯에 연결
        self.timer = QTimer(self)  # QTimer 인스턴스 생성
        self.timer.timeout.connect(self.loadStockData)  # 타이머의 timeout 시그널을 loadStockData 메서드에 연결
        self.timer.start(3000)  # 10초마다 타이머 실행
        self.loadStockData()  # UI 초기화 후 데이터 로드
        self.Save = []  # Save 속성 초기화, 데이터를 저장할 리스트로 사용
        self.setupUi()  # UI 설정 초기화

     # UI 세팅
    def setupUi(self):
        uic.loadUi('C:/Users/qimin/OneDrive/바탕 화면/Python/StockReport/tablewidgetTest.ui', self)
        self.tableWidget.setRowCount(0)  # 기존 테이블 행 제거
        self.KR_Won.clicked.connect(self.Select_Kor_Market)  # 국내
        self.US_KRW.clicked.connect(self.Select_US_KRWMarket)  # 해외 원화
        self.US_Dollar.clicked.connect(self.Select_US_DollarMarket)  # 해외 달러
        self.US_ETF.clicked.connect(self.Select_US_ETFMarket)  # 해외
        #self.US_ETF_KRW.clicked.connect(self.Select_US_ETFMarket)  # 해외
        self.btn_insertItem.clicked.connect(self.search_instance.searchStock)  # 검색 버튼 클릭 시 기능 연결
        self.Favorite_Add.clicked.connect(self.Favorite_instance.addSelectedStockToFavorites)  # 관심 종목 추가 버튼 클릭
        self.Favorite_Remove.clicked.connect(self.Favorite_instance.removeSelectedStockFromFavorites)  # 관심 종목 제거 버튼 클릭
        self.tableWidget.cellClicked.connect(self.checkBoxStateChanged)  # 체크박스 클릭 시 기능 연결
        self.tableWidget.setColumnWidth(5,20) #첫번째 열 크기 고정
        self.tableWidget.setColumnWidth(0,200) #첫번째 열 크기 고정

        # ETF - US_ETF
        # Dollar - US_Dollar
        # US_KRW - US_KRW
        # KR - KR_Won
        # ETF - US_ETF_KRW

        # 관심종목추가 - Favorite_Add
        # 관심종목제거 - Favorite_Remove

    # Update 주식
    def updateTable(self, stock_data):
        self.Save = stock_data  # Save에 로드된 데이터를 저장
        if not stock_data:
            QMessageBox.warning(self, "정보", "현재 주식 데이터가 없습니다.")
            return
    
        # 주식 데이터를 테이블에 그리기
        DrawStock(self, stock_data)
    
        # 관심 종목 업데이트
        for stock in self.Favorite_instance.watchlist:
            updated_stock = next((item for item in stock_data if item['종목'] == stock['종목']), None)
            if updated_stock:
                stock.update(updated_stock)  # 관심 종목의 정보를 업데이트
    
        self.Favorite_instance.updateWatchlist()  # 관심 종목 목록 갱신
        MyDialog.addCheckBoxesToTable(self)

    
    def addCheckBoxesToTable(self):
        for row in range(self.tableWidget.rowCount()):
            checkbox = QCheckBox()
            checkbox.setChecked(self.KR_CheckBoxBoolean[row])  # 체크박스를 기본적으로 현재 상태로 설정
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
                        if not any(stock['종목'] == stock_name for stock in self.Favorite_instance.watchlist):
                            self.KR_CheckBoxBoolean[row] = True
                            print(f"{row} : {self.KR_CheckBoxBoolean[row]}")
                            self.Favorite_instance.addToWatchList(self.Save, stock_name)  # 관심 종목 추가
                    else:
                        self.KR_CheckBoxBoolean[row] = False
                        print(f"{row} : {self.KR_CheckBoxBoolean[row]}")
                        # 관심 종목에서 제거하는 로직 추가
                        self.Favorite_instance.watchlist = [stock for stock in self.Favorite_instance.watchlist if stock['종목'] != stock_name]

                    # 관심 종목 목록 업데이트
                    self.Favorite_instance.updateWatchlist()  # 관심 종목 목록 업데이트
                    break


    def Select_Kor_Market(self):
        global ThisStockPage
        ThisStockPage = "KR"
        self.loadStockData()  # 데이터 로드

    def Select_US_KRWMarket(self):
        global ThisStockPage
        ThisStockPage = "US_KRW"
        self.loadStockData()  # 데이터 로드

    def Select_US_DollarMarket(self):
        global ThisStockPage
        ThisStockPage = "US_Dollar"
        self.loadStockData()  # 데이터 로드

    def Select_US_ETFMarket(self):
        global ThisStockPage
        ThisStockPage = "US_ETF_Dollar"
        self.loadStockData()  # 데이터 로드

    def Select_US_ETFKRWMarket(self):
        global ThisStockPage
        ThisStockPage = "US_ETF_KRW"
        self.loadStockData()  # 데이터 로드

    def loadStockData(self):
        self.dataLoader.start()  # 백그라운드 스레드 시작

def DrawStock(self, Data):
    self.tableWidget.setRowCount(0)  
    sorted_data = sorted(Data, key=lambda stock: stock.get('number', 0))
    
    for stock in sorted_data:
        row_position = self.tableWidget.rowCount()  # 현재 테이블의 행 수 가져오기
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
