from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QCheckBox
from PyQt5.QtGui import QColor

class FavoriteOption:
    def __init__(self, favorite_instance):
        self.favorite_instance = favorite_instance
        self.watchlist = favorite_instance.watchlist  # Favorite_instance에서 watchlist 가져오기
        self.my_dialog_instance = favorite_instance  # MyDialog 인스턴스 저장
        
    def updateWatchlist(self):
        # 관심 종목 목록 업데이트
        self.favorite_instance.tableWidget_2.setRowCount(0)  # 기존 행 제거
        for stock in self.watchlist:
            row_position = self.favorite_instance.tableWidget_2.rowCount()  # 현재 테이블의 행 수 가져오기
            self.favorite_instance.tableWidget_2.insertRow(row_position)  # 새로운 행 추가

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

            self.favorite_instance.tableWidget_2.setItem(row_position, 0, name_item)
            self.favorite_instance.tableWidget_2.setItem(row_position, 1, Today_Price_item)
            self.favorite_instance.tableWidget_2.setItem(row_position, 2, RiseAndFalls_Percent_item)
            self.favorite_instance.tableWidget_2.setItem(row_position, 3, RiseAndFalls_Price_item)
            self.favorite_instance.tableWidget_2.setItem(row_position, 4, Start_price_item)

    # FavoriteOption 클래스에서 addSelectedStockToFavorites 수정
    def addSelectedStockToFavorites(self):
        selected_row = self.favorite_instance.tableWidget.currentRow()  # 현재 선택된 행 가져오기
        if selected_row < 0:
            QMessageBox.warning(self.favorite_instance, "경고", "관심 종목을 선택해 주세요.")
            return  

        stock_name = self.favorite_instance.tableWidget.item(selected_row, 0).text()  # 선택된 주식의 이름 가져오기
        stock_data = self.favorite_instance.Save  # 현재 저장된 주식 데이터

        # 이미 관심 종목 목록에 있는지 확인
        if not any(stock['종목'] == stock_name for stock in self.watchlist):
            self.addToWatchList(stock_data, stock_name)  # 주식 목록에 추가
            self.updateWatchlist()  # 관심 종목 목록 업데이트   

            # 체크박스 상태 갱신
            row_count = self.favorite_instance.tableWidget.rowCount()
            for row in range(row_count):
                if self.favorite_instance.tableWidget.item(row, 0).text() == stock_name:
                    widget = self.favorite_instance.tableWidget.cellWidget(row, 5)
                    if widget is not None:
                        checkbox = widget.findChild(QCheckBox)
                        if checkbox:
                            checkbox.setChecked(True)  # 체크박스 체크
                    self.favorite_instance.KR_CheckBoxBoolean[row] = True  # 체크박스 상태 저장
                    break  # 주식이 추가되었으므로 반복 종료

    def removeSelectedStockFromFavorites(self):
        selected_row = self.favorite_instance.tableWidget_2.currentRow()  # 관심 종목 목록에서 선택된 행 가져오기
        if selected_row < 0:
            QMessageBox.warning(self.favorite_instance, "경고", "제거할 관심 종목을 선택해 주세요.")
            return  

        stock_name = self.favorite_instance.tableWidget_2.item(selected_row, 0).text()  # 선택된 주식의 이름 가져오기
        # watchlist에서 해당 주식 제거
        self.watchlist = [stock for stock in self.watchlist if stock['종목'] != stock_name] 

        # 관심 종목 목록 갱신
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
                break
