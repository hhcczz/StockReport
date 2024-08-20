from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QMessageBox, QCheckBox, QWidget, QHBoxLayout
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class Search:
    def __init__(self, gui_instance):
        self.gui_instance = gui_instance

    def searchStock(self):
        search_query = self.gui_instance.line_insertItem.text().strip()
        if not search_query:
            # 현재 페이지에 맞게 데이터 로드
            QMessageBox.warning(self.gui_instance, "경고", "검색어를 입력해 주세요.")
            return

        stock_data = self.gui_instance.Save
        if not stock_data:
            QMessageBox.warning(self.gui_instance, "정보", "현재 주식 데이터가 없습니다.")
            return

        filtered_stocks = [stock for stock in stock_data if search_query.lower() in stock['종목'].lower()]
        self.gui_instance.tableWidget.setRowCount(0)

        for stock in filtered_stocks:
            row_position = self.gui_instance.tableWidget.rowCount()
            self.gui_instance.tableWidget.insertRow(row_position)

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

            ## 현재 페이지에 따라 체크박스 상태를 가져옴
            #if self.gui_instance.ThisStockPage == "KR":
            #    checkbox_checked = self.gui_instance.KR_CheckBoxBoolean.get(stock['종목'], False)
            #elif self.gui_instance.ThisStockPage in ["US_Dollar", "US_KRW"]:
            #    checkbox_checked = self.gui_instance.US_CheckBoxBoolean.get(stock['종목'], False)
            #elif self.gui_instance.ThisStockPage in ["US_ETF_Dollar", "US_ETF_KRW"]:
            #    checkbox_checked = self.gui_instance.US_ETF_CheckBoxBoolean.get(stock['종목'], False)

            ## 체크박스 생성 및 상태 설정
            #checkbox = QCheckBox()
            #checkbox.setChecked(checkbox_checked)
            #checkbox.stateChanged.connect(self.gui_instance.checkBoxStateChanged)
#
            #widget = QWidget()
            #layout = QHBoxLayout(widget)
            #layout.addWidget(checkbox)
            #layout.setAlignment(Qt.AlignCenter)
            #layout.setContentsMargins(0, 0, 0, 0)
            #widget.setLayout(layout)
#
            #self.gui_instance.tableWidget.setCellWidget(row_position, 5, widget)

            if start_price != 0:  # 전날 가격이 0이 아닌 경우
                change_percent = ((today_price - start_price) / start_price) * 100
            else:
                change_percent = 0  # 전날 가격이 0일 경우 변경률은 0으로 설정

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

            self.gui_instance.tableWidget.setItem(row_position, 0, name_item)
            self.gui_instance.tableWidget.setItem(row_position, 1, Today_Price_item)
            self.gui_instance.tableWidget.setItem(row_position, 2, RiseAndFalls_Percent_item)
            self.gui_instance.tableWidget.setItem(row_position, 3, RiseAndFalls_Price_item)
            self.gui_instance.tableWidget.setItem(row_position, 4, Start_price_item)

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
