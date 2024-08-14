from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor

class Search:
    def __init__(self, gui_instance):
        self.gui_instance = gui_instance

    def searchStock(self):
        search_query = self.gui_instance.line_insertItem.text().strip()
        if not search_query:
            QMessageBox.warning(self.gui_instance, "경고", "검색어를 입력해 주세요.")
            return

        stock_data = self.gui_instance.Save
        if not stock_data:
            QMessageBox.warning(self.gui_instance, "정보", "현재 주식 데이터가 없습니다.")
            return

        filtered_stocks = [stock for stock in stock_data if search_query.lower() in stock['종목'].lower()]
        self.gui_instance.tableWidget.setRowCount(0)

        for stock in filtered_stocks:
            row_position = self.gui_instance.tableWidget.rowCount()  # 현재 테이블의 행 수 가져오기
            self.gui_instance.tableWidget.insertRow(row_position)  # 새로운 행 추가

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

            self.gui_instance.tableWidget.setItem(row_position, 0, name_item)
            self.gui_instance.tableWidget.setItem(row_position, 1, Today_Price_item)
            self.gui_instance.tableWidget.setItem(row_position, 2, RiseAndFalls_Percent_item)
            self.gui_instance.tableWidget.setItem(row_position, 3, RiseAndFalls_Price_item)
            self.gui_instance.tableWidget.setItem(row_position, 4, Start_price_item)

        # 검색 결과가 있을 경우 첫 번째 주식 정보를 관심 목록에 추가하는 버튼 활성화
        self.gui_instance.pushButton_2.setEnabled(bool(filtered_stocks))  # 관심 종목 추가 버튼 활성화/비활성화

    def viewWatchlist(self):
        if not self.gui_instance.watchlist:
            QMessageBox.information(self.gui_instance, "정보", "관심 종목 목록이 비어 있습니다.")
            return

        self.gui_instance.tableWidget_2.setRowCount(0)  # Assume tableWidget_2 is where you show the watchlist
        for stock in self.gui_instance.watchlist:
            row_position = self.gui_instance.tableWidget_2.rowCount()  # 현재 테이블의 행 수 가져오기
            self.gui_instance.tableWidget_2.insertRow(row_position)  # 새로운 행 추가

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

            self.gui_instance.tableWidget_2.setItem(row_position, 0, name_item)
            self.gui_instance.tableWidget_2.setItem(row_position, 1, Today_Price_item)
            self.gui_instance.tableWidget_2.setItem(row_position, 2, RiseAndFalls_Percent_item)
            self.gui_instance.tableWidget_2.setItem(row_position, 3, RiseAndFalls_Price_item)
            self.gui_instance.tableWidget_2.setItem(row_position, 4, Start_price_item)
