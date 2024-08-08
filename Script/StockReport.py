import threading
from tkinter import *
import CSS_Selector as cs
import tkinter.ttk
import time

# Tkinter 창 생성
tk = Tk()
tk.wm_attributes("-topmost", 1)
tk.title("Stock Report Program")

# 화면 크기 받아오기
windows_width = tk.winfo_screenwidth()
windows_height = tk.winfo_screenheight()

# 생성할 윈도우의 가로와 세로 크기
app_width = 1280
app_height = 768

# 윈도우 화면 중앙 정렬 코드
center_width = (windows_width / 2) - (app_width / 2)
center_height = (windows_height / 2) - (app_height / 2)
tk.geometry(f"{app_width}x{app_height}+{int(center_width)}+{int(center_height)}")

# 표 생성하기
columns = ["one", "two", "three", "four"]
treeview = tkinter.ttk.Treeview(tk, columns=columns, show='headings')

# 각 컬럼 설정
treeview.heading("one", text="종목", anchor="center")
treeview.heading("two", text="원(￦)", anchor="center")
treeview.heading("three", text="등락", anchor="center")
treeview.heading("four", text="전날대비", anchor="center")

treeview.column("one", width=100, anchor="center")
treeview.column("two", width=100, anchor="center")
treeview.column("three", width=70, anchor="center")
treeview.column("four", width=70, anchor="center")

# 표를 화면에 배치
treeview.pack(expand=True, fill='both')

def fetch_data(stock_type):
    # 최초 데이터 가져오기
    stock_data = cs.scroll_and_get_stocks(stock_type)

    # 데이터가 None인 경우 빈 리스트로 초기화
    if stock_data is None:
        stock_data = []

    # UI 업데이트
    update_treeview(stock_data)

    # 이후 스크롤과 데이터 업데이트 시작
    start_scrolling(stock_type)

def update_treeview(stock_data):
    treeview.delete(*treeview.get_children())
    for stock in stock_data:
        treeview.insert('', 'end', values=(stock["종목"], stock["원(￦)"], stock["등락"], stock["전날대비"]))

def start_scrolling(stock_type):
    # 주기적으로 데이터를 가져오는 스레드 시작
    threading.Thread(target=scroll_and_fetch_data, args=(stock_type,)).start()

def scroll_and_fetch_data(stock_type):
    while True:  # 스크롤과 데이터 업데이트를 계속 반복
        stock_data = cs.scroll_and_get_stocks(stock_type)  # 데이터를 가져오는 함수 호출

        if stock_data is None:  # 데이터가 None인 경우
            stock_data = []
        update_treeview(stock_data)  # UI 업데이트

def StartStock(stock_type):
    threading.Thread(target=fetch_data, args=(stock_type,)).start()

# 메뉴바
topMenu = Menu(tk)  # topMenu 생성
tk.configure(menu=topMenu)  # tk에 메뉴 객체 연결

cbMenu = Menu(topMenu, tearoff=0)  # 묶음 메뉴 객체 생성
topMenu.add_cascade(label="시장", menu=cbMenu)  # 상위 모음 메뉴 연결

cbMenu.add_radiobutton(label="한국 일반 주식", command=lambda: StartStock("한국주식"))
cbMenu.add_radiobutton(label="한국 ETF 주식", command=lambda: StartStock("한국주식"))
cbMenu.add_radiobutton(label="미국 일반 주식", command=lambda: StartStock("미국주식"))
cbMenu.add_radiobutton(label="미국 ETF 주식", command=lambda: StartStock("미국주식"))
cbMenu.invoke(cbMenu.index("한국 일반 주식"))

# Tkinter 이벤트 루프 시작
tk.mainloop()
