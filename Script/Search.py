# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QWidget, QHBoxLayout
from PyQt5.QtGui import QColor, QFont, QFontDatabase, QIcon, QPixmap
from PyQt5.QtCore import Qt
import os

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

        font_db = QFontDatabase()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(current_dir, '강원교육모두B.ttf')
        font_id = font_db.addApplicationFont(font_path)
        font_family = font_db.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"
        font = QFont(font_family, 10)

        for stock in filtered_stocks:
            row_position = self.gui_instance.tableWidget.rowCount()
            self.gui_instance.tableWidget.insertRow(row_position)

            # 종목 데이터
            name_item = QTableWidgetItem(stock['종목'])
            name_item.setForeground(QColor("#c3c3c6"))
            name_item.setFont(font)

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
            self.gui_instance.tableWidget.setItem(row_position, 0, icon)  # 첫 번째 열에 이미지 설정

            self.gui_instance.tableWidget.setItem(row_position, 1, name_item)  # 종목
            self.gui_instance.tableWidget.setItem(row_position, 2, Today_Price_item)  # 오늘 가격
            self.gui_instance.tableWidget.setItem(row_position, 3, RiseAndFalls_Price_item)  # 등락(￦)
            self.gui_instance.tableWidget.setItem(row_position, 4, RiseAndFalls_Percent_item)  # 등락(%)
            self.gui_instance.tableWidget.setItem(row_position, 5, Start_price_item)  # 시작가

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
