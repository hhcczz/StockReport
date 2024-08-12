from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QTimer, QDateTime, Qt, QThread, pyqtSignal
import sys
import request as RQ

Save = []
stock_name = ""

class StockDataLoader(QThread):
    dataLoaded = pyqtSignal(list)

    def run(self):
        global Save
        stock_data = RQ.process_stock_price_data(RQ.stock_data, RQ.stock_names)
        Save = stock_data
        self.dataLoaded.emit(stock_data)


class MyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi()  # UI 설정 초기화
        self.watchlist = []  # 관심 종목 리스트 초기화

        self.dataLoader = StockDataLoader()  # StockDataLoader 인스턴스 생성
        self.dataLoader.dataLoaded.connect(self.updateTable)  # dataLoaded 시그널을 updateTable 슬롯에 연결
        self.dataLoader.start()  # 백그라운드 스레드 시작

    def setupUi(self):
        from PyQt5 import uic
        uic.loadUi('tablewidgetTest.ui', self)  # UI 파일 로드
        
        self.tableWidget.setRowCount(0)  # 기존 테이블 행 제거
        self.dateTimeEdit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")  # 날짜 및 시간 형식 설정

        # 버튼 클릭 시 연결될 기능 설정
        self.pushButton_2.clicked.connect(self.addToWatchlist)  # '관심 종목 추가' 버튼 클릭 시, 관심 종목에 추가하는 기능 연결
        self.pushButton_3.clicked.connect(self.removeFromWatchlist)  # '관심 종목 제거' 버튼 클릭 시, 관심 종목에서 제거하는 기능 연결
        self.btn_removeItem.clicked.connect(self.viewWatchlist)  # '관심 종목 보기' 버튼 클릭 시, 관심 종목 리스트 보기 기능 연결
        self.btn_insertItem.clicked.connect(self.searchStock)  # '검색' 버튼 클릭 시, 주식 검색 기능 연결
        self.pushButton.clicked.connect(self.refreshDomesticMarket)  # '국내증시 새로고침' 버튼 클릭 시, 국내 주식 시장 정보 갱신 기능 연결

    def updateTable(self, stock_data):
        if not stock_data:
            QMessageBox.warning(self, "정보", "현재 주식 데이터가 없습니다.")  # 데이터가 없을 경우 경고 메시지 표시
            return
        # 데이터 형식 확인
        if not all(isinstance(stock, dict) for stock in stock_data):
            QMessageBox.warning(self, "정보", "잘못된 주식 데이터 형식입니다.")
            return
        DrawStock(self, stock_data)

    def updateDateTime(self):
        current_time = QDateTime.currentDateTime()  # 현재 시간 가져오기
        self.dateTimeEdit.setDateTime(current_time)  # UI에 시간 업데이트

    def addToWatchlist(self):
        stock_name = self.line_insertItem.text().strip()  # 사용자가 입력한 주식 이름 가져오기
        stock_data = Save  # 현재 주식 데이터 가져오기

        # 관심 종목 목록에 추가할 주식 정보 찾기
        stock_info = next((item for item in stock_data if item['종목'] == stock_name), None)

        if stock_name and stock_info:
            if not any(stock['종목'] == stock_name for stock in self.watchlist):
                self.watchlist.append(stock_info)  # 관심 종목 리스트에 추가
                MessageBox(self, "정보", "관심종목추가", stock_name)
            else:
                MessageBox(self, "경고", "관심종목중복", stock_name)
        elif not stock_name:
            MessageBox(self, "경고", "관심종목이름입력", stock_name)
        else:
            MessageBox(self, "경고", "관심종목정보X", stock_name)

    def removeFromWatchlist(self):
        stock_name = self.line_insertItem.text().strip()  # 사용자가 입력한 주식 이름 가져오기
        if stock_name:
            # 관심 종목 리스트에서 해당 주식 제거
            self.watchlist = [stock for stock in self.watchlist if stock['종목'] != stock_name]
            MessageBox(self, "정보", "관심종목제거", stock_name)
        else:
            MessageBox(self, "경고", "관심종목이름입력", stock_name)

    def viewWatchlist(self):
        if not self.watchlist:
            MessageBox(self, "정보", "관심종목비어있음", stock_name)
            return
        
        # watchlist에 있는 종목들을 최신 데이터로 업데이트
        for i, watch_item in enumerate(self.watchlist):
            updated_stock = next((stock for stock in Save if stock['종목'] == watch_item['종목']), None)
            if updated_stock:
                self.watchlist[i] = updated_stock
        
        DrawStock(self, self.watchlist)

    def searchStock(self):
        search_query = self.line_insertItem.text().strip()  # 사용자가 입력한 검색어 가져오기
        if not search_query:
            MessageBox(self, "경고", "검색어입력", stock_name)
            return
        
        stock_data = Save  # 현재 주식 데이터 가져오기

        if not stock_data:
            MessageBox(self, "경고", "데이터없음", stock_name)
            return

        # 검색어로 주식 필터링 (대소문자 구분하지 않음)
        filtered_stocks = [stock for stock in stock_data if search_query.lower() in stock['종목'].lower()]
        
        if not filtered_stocks:
            MessageBox(self, "정보", "검색결과없음", search_query)  # 검색 결과가 없을 경우 경고 메시지 표시
            return
        
        DrawStock(self, filtered_stocks)

    def refreshDomesticMarket(self):
        DrawStock(self, Save)

def DrawStock(self, Data):
    self.tableWidget.setRowCount(0)  # 테이블의 기존 행 초기화
    for stock in Data:
        # 주식 정보를 테이블에 추가
        row_position = self.tableWidget.rowCount()  # 현재 테이블의 행 수 가져오기
        self.tableWidget.insertRow(row_position)  # 새로운 행 추가
        
        name_item = QTableWidgetItem(stock['종목'])
        price_item = QTableWidgetItem(str(stock['원(￦)']))  # float를 문자열로 변환
        change_item = QTableWidgetItem(stock['등락'])
        change_percent_item = QTableWidgetItem(str(stock['전날대비']))  # float를 문자열로 변환

        # 색상 설정
        if stock['등락'].startswith('+'):
            change_item.setForeground(Qt.red)
            change_percent_item.setForeground(Qt.red)
        elif stock['등락'].startswith('-'):
            change_item.setForeground(Qt.blue)
            change_percent_item.setForeground(Qt.blue)
        else:
            change_item.setForeground(Qt.black)
            change_percent_item.setForeground(Qt.black)

        self.tableWidget.setItem(row_position, 0, name_item)
        self.tableWidget.setItem(row_position, 1, price_item)
        self.tableWidget.setItem(row_position, 2, change_item)
        self.tableWidget.setItem(row_position, 3, change_percent_item)

def MessageBox(self, thistype, type, stock_name):
    if(type == "관심종목추가"):
        return QMessageBox.information(self, f"{thistype}", f"{stock_name}이(가) 관심 종목 목록에 추가되었습니다.")
    elif(type == "관심종목중복"):
        return QMessageBox.warning(self, f"{thistype}", f"{stock_name}은 이미 관심 종목 목록에 있습니다.")
    elif(type == "관심종목이름입력"):
        QMessageBox.warning(self, f"{thistype}", "관심 종목 이름을 입력해 주세요.")
    elif(type == "관심종목정보X"):
        QMessageBox.warning(self, f"{thistype}", f"{stock_name}의 정보를 찾을 수 없습니다.")
    elif(type == "관심종목제거"):
        QMessageBox.information(self, f"{thistype}", f"{stock_name}이(가) 관심 종목 목록에서 제거되었습니다.")
    elif(type == "관심종목비어있음"):
        QMessageBox.information(self, f"{thistype}", "관심 종목 목록이 비어 있습니다.")  # 관심 종목 목록이 비어 있을 경우 경고 메시지 표시
    elif(type == "검색어입력"):
        QMessageBox.warning(self, f"{thistype}", "검색어를 입력해 주세요.")  # 검색어가 없을 경우 경고 메시지 표시
    elif(type == "데이터없음"):
        QMessageBox.warning(self, "정보", "현재 주식 데이터가 없습니다.")  # 주식 데이터가 없을 경우 경고 메시지 표시
    elif(type == "검색결과없음"):
        QMessageBox.warning(self, "정보", f"'{stock_name}'에 대한 검색 결과가 없습니다.")  # 검색 결과가 없을 경우 경고 메시지 표시

# 애플리케이션 실행
app = QApplication(sys.argv)
dialog = MyDialog()
dialog.show()
sys.exit(app.exec_())
