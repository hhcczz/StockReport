from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor
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
        uic.loadUi('tablewidgetTest.ui', self)  # UI 파일 로드
        self.tableWidget.setRowCount(0)  # 기존 테이블 행 제거
        self.pushButton.clicked.connect(self.Select_KorMarket)  # 국내
        self.btn_clearItem.clicked.connect(self.Select_USMarket)  # 해외
        self.btn_insertItem.clicked.connect(self.search_instance.searchStock)  # 검색 버튼 클릭 시 기능 연결
        self.pushButton_2.clicked.connect(self.Favorite_instance.addSelectedStockToFavorites)  # 관심 종목 추가 버튼 클릭
        self.pushButton_3.clicked.connect(self.Favorite_instance.removeSelectedStockFromFavorites)  # 관심 종목 제거 버튼 클릭


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
        
    def Select_KorMarket(self):
        global ThisStockPage
        ThisStockPage = "KR"
        self.loadStockData()  # 데이터 로드

    def Select_USMarket(self):
        global ThisStockPage
        ThisStockPage = "US"
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
        Today_Price_item = QTableWidgetItem(format(int(stock['원(￦)']), ","))
        RiseAndFalls_Percent_item = QTableWidgetItem(format(int(stock['원(￦)'] - stock['시작가']), ","))
        Start_price_item = QTableWidgetItem(format(int(stock['시작가']), ","))

        if stock['시작가'] != 0:  # 전날 가격이 0이 아닌 경우
            change_percent = ((stock['원(￦)'] - stock['시작가']) / stock['시작가']) * 100
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
