import tkinter as tk
from tkinter import messagebox
from pybit.unified_trading import HTTP
import requests
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import timedelta
import mplfinance as mpf
import time
from matplotlib.animation import FuncAnimation


# 주문창과 관련된 함수 정의
response_label = None
session = None

def try_login(api_key, api_secret):
    try:
        session = HTTP(
            api_key=api_key,
            api_secret=api_secret,
            recv_window=45000,
            testnet=True
        )
        account_info = session.get_wallet_balance(accountType="UNIFIED",coin="USDT")
        print(account_info)
        if account_info['retCode'] == 0:
            return session, True
        else:
            return None, False
    except Exception as e:
        print(e)
        return None, False
    
    
# place_order 함수 수정
def place_order(session, symbol, position, order_type, qty, price, leverage, take_profit, stop_loss):
    try:
        if order_type.lower() == "limit":
            order_response = session.place_order(
                category="linear",
                symbol=symbol,
                side="Buy" if position.lower() == "long" else "Sell",
                order_type="Limit",
                qty=qty,
                price=price,
                time_in_force="PostOnly",
                reduce_only=False,
                close_on_trigger=False,
                leverage=leverage,
                take_profit=take_profit,  # TP 설정
                stop_loss=stop_loss  # SL 설정
            )
            if 'ret_code' in order_response and order_response['ret_code'] == 0:
                return order_response
            else:
                print(order_response.get('ret_msg', '알 수 없는 오류가 발생했습니다.'))  # 이 부분에서 오류 메시지 출력
        else:
            return f"주문 실패: {order_response.get('ret_msg', '알 수 없는 오류가 발생했습니다.')}"
    except Exception as e:
        return str(e)
    

def create_order(session, symbol_var, position_var, order_type_var, qty_entry, entry_price_entry, leverage_entry, tp_entry, sl_entry):
    symbol = symbol_var.get()
    position = position_var.get()
    order_type = order_type_var.get()

    # 주문 수량을 USDT 잔고를 기반으로 계산
    balance = get_wallet_balance()
    if balance is not None:
        qty_percentage = 100  # 원하는 백분율로 수정 가능
        qty = round(balance * qty_percentage / 100, 3)  # 백분율로 주문 수량 계산
        qty_entry.delete(0, tk.END)
        qty_entry.insert(0, str(qty))  # 주문 수량 필드에 설정
    else:
        response_label.config(text="USDT 잔고를 가져올 수 없습니다.")
        return

    qty = qty_entry.get()
    price = entry_price_entry.get()
    leverage = leverage_entry.get()
    tp_price = tp_entry.get()
    sl_price = sl_entry.get()  # sl_entry를 가져옴

    # API 요청을 전송하고 결과를 받습니다.
    order_response = place_order(
        session, symbol, position, order_type, qty, price, leverage, tp_price, sl_price
    )

    if isinstance(order_response, dict):
        # 딕셔너리로부터 필요한 정보를 추출하여 사용
        if 'ret_code' in order_response and order_response['ret_code'] == 0:
            response_label.config(text=f"주문 성공: {order_response['result']}")
        else:
            error_msg = order_response.get('ret_msg', '주문 실패: 알 수 없는 오류가 발생했습니다.')
            response_label.config(text=error_msg)
            print(f"주문 실패: {error_msg}")  # 오류 메시지를 터미널에 출력
            messagebox.showerror("주문 실패", error_msg)
    else:
        error_msg = f'주문 실패: {order_response}'
        response_label.config(text=error_msg)
        print(f"주문 실패: {error_msg}")  # 오류 메시지를 터미널에 출력
        messagebox.showerror("주문 실패", error_msg)

def set_order_quantity(percentage):
    balance = get_wallet_balance()
    if balance is not None:
        qty = round(balance * percentage / 100, 3)
        qty_entry.delete(0, tk.END)
        qty_entry.insert(0, str(qty))


def create_percentage_buttons(frame):
    percentages = [10, 25, 50, 75, 100]
    percentage_frame = tk.Frame(frame)  # 버튼을 위한 새로운 프레임 생성
    percentage_frame.pack()  # 프레임을 부모 프레임에 패킹

    for percentage in percentages:
        button = tk.Button(percentage_frame, text=f"{percentage}%", command=lambda p=percentage: set_order_quantity(p))
        button.grid(row=0, column=percentages.index(percentage))







def get_current_price():
    # 비트코인의 현재 시장가격을 가져오는 함수
    try:
        response = requests.get("https://api.bybit.com/v2/public/tickers?symbol=BTCUSD")
        data = response.json()
        if data['ret_code'] == 0:
            return data['result'][0]['last_price']
    except Exception as e:
        print(f"가격 정보 가져오기 실패: {str(e)}")
        return None

def update_price_label():
    # 가격 레이블을 업데이트하는 함수
    price = get_current_price()
    if price:
        price_label.config(text=f"BTCUSD: {price} USD")
    root.after(1000, update_price_label)  # 10초마다 가격 업데이트

def cancel_order(order_id):
    try:
        response = session.cancel_order(
            category="linear",
            symbol=symbol_var.get(),  # 현재 선택된 코인을 사용
            orderId=order_id
        )
        response_label.config(text=str(response))
    except Exception as e:
        response_label.config(text=f"오류 발생: {str(e)}")



def set_trading_stop(takeProfit, stopLoss, tpTriggerBy, slTriggerBy, tpslMode, tpOrderType, slOrderType, tpSize, slSize, tpLimitPrice, slLimitPrice, positionIdx):
    try:
        response = session.set_trading_stop(
            category="linear",
            symbol=symbol_var.get(), 
            takeProfit=takeProfit,
            stopLoss=stopLoss,
            tpTriggerBy=tpTriggerBy,
            slTriggerBy=slTriggerBy,
            tpslMode=tpslMode,
            tpOrderType=tpOrderType,
            slOrderType=slOrderType,
            tpSize=tpSize,
            slSize=slSize,
            tpLimitPrice=tpLimitPrice,
            slLimitPrice=slLimitPrice,
            positionIdx=positionIdx
        )
        response_label.config(text=str(response))
    except Exception as e:
        response_label.config(text=f"오류 발생: {str(e)}")

# 거래 종료 함수
def close_trade(close_trade_price_entry):
    close_price = close_trade_price_entry.get() #수정필요
    # Bybit API를 사용하여 현재 거래를 지정된 가격에 종료하는 요청을 보냅니다.
    print(f"거래 종료 설정 가격: {close_price}")


# 거래 종료 가격 입력 필드 생성
def create_close_trade_entry(frame):
    close_trade_label = tk.Label(frame, text="거래 종료 가격:")
    close_trade_label.pack()
    close_trade_entry = tk.Entry(frame)
    close_trade_entry.pack()
    return close_trade_entry



def set_tp_sl_mode(tpSlMode):
    try:
        response = session.set_tp_sl_mode(
            symbol=symbol_var.get(),
            category="linear",
            tpSlMode=tpSlMode
        )
        response_label.config(text=str(response))
    except Exception as e:
        response_label.config(text=f"오류 발생: {str(e)}")

# TP/SL 설정 입력 필드 생성
def create_tp_sl_entry(frame):
    tp_label = tk.Label(frame, text="TP 가격:")
    tp_label.pack()
    tp_entry = tk.Entry(frame)
    tp_entry.pack()

    sl_label = tk.Label(frame, text="SL 가격:")
    sl_label.pack()
    sl_entry = tk.Entry(frame)
    sl_entry.pack()

    return tp_entry, sl_entry



def get_wallet_balance():
    try:
        balance_info = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")
        
        # ret_code 또는 retCode 키를 확인합니다.
        ret_code_key = 'ret_code' if 'ret_code' in balance_info else 'retCode'

        if balance_info[ret_code_key] == 0:
            balance = balance_info['result']['list'][0]['coin'][0]['equity']
            # 문자열 대신 부동소수점 숫자를 반환합니다.
            return float(balance)
        else:
            return None  # 잔액 정보를 가져올 수 없을 때는 None을 반환합니다.
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return None
    



def update_balance_label():
    balance = get_wallet_balance()
    balance_label.config(text=f"잔고: {balance} ")


# 코인 선택을 위한 드롭다운 메뉴
def create_symbol_dropdown(frame):
    global symbol_var
    symbol_var = tk.StringVar(frame)
    symbol_var.set("BTCUSDT")  # 기본값을 BTCUSD로 설정
    available_symbols = ["BTCUSDT"]  # 추후에 다른 코인 추가 가능
    symbol_label = tk.Label(frame, text="Symbol:")
    symbol_label.pack()
    symbol_menu = tk.OptionMenu(frame, symbol_var, *available_symbols)
    symbol_menu.pack()


def login():
    # 로그인 창을 별도의 Toplevel 대신 메인 윈도우에 직접 배치
    tk.Label(root, text="API 키:").pack()
    api_key_entry = tk.Entry(root, width=50)
    api_key_entry.pack()

    tk.Label(root, text="시크릿 키:").pack()
    api_secret_entry = tk.Entry(root, show="*",width=50)
    api_secret_entry.pack()



    def on_login_click():
        global session, balance_label
        api_key = api_key_entry.get()
        api_secret = api_secret_entry.get()
        session, success = try_login(api_key, api_secret)
        if success:
            messagebox.showinfo("로그인 성공", "로그인에 성공했습니다.")
            # 로그인 관련 위젯 숨기기
            api_key_entry.pack_forget()
            api_secret_entry.pack_forget()
            login_button.pack_forget()
            balance_label = tk.Label(root, text="")
            balance_label.pack()
            update_balance_label()  # 잔고 정보 업데이트
            create_main_gui()  # 거래 및 차트 창 생성
        else:
            messagebox.showerror("로그인 실패", "로그인에 실패했습니다.")

    login_button = tk.Button(root, text="로그인", command=on_login_click)
    login_button.pack()


    

# 차트 그리기와 관련된 함수 정의
def get_candle_data(symbol):
    url = "https://api.bybit.com/v5/market/kline"
    current_time = int(time.time())
    start_time = current_time - 120  # 2분 전

    params = {
        "symbol": symbol,
        "interval": "1",
        "from": str(start_time)
    }

    response = requests.get(url, params=params)
    data = response.json()

    # 캔들 데이터 추출 및 DataFrame으로 변환
    candles = data['result']['list']
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'extra'])

    # Convert timestamp to datetime and adjust for Korean time (UTC+9)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms') + timedelta(hours=9)
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close']].astype(float)

    return df

def update(frame):#수정필요
    df = get_candle_data("BTCUSD")
    ax.clear()
    mpf.plot(df, type='candle', ax=ax, style='charles')
    # Reverse x-axis to make the graph progress from left to right
    ax.invert_xaxis()

def create_main_gui():
    global  ax, canvas , ani, trades_listbox, root, balance_label, price_label
    # 프레임 분할
    left_frame = tk.Frame(root)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    right_frame = tk.Frame(root)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # 왼쪽 프레임에 차트 그리기
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(1, 1, 1)
    canvas = FigureCanvasTkAgg(fig, master=left_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    ani = FuncAnimation(fig, update, interval=1000)  # 1초마다 업데이트
    
    
    # 잔고 정보를 표시할 레이블 생성
    #balance_label = tk.Label(right_frame, text="", font=("Helvetica", 12))
    #balance_label.pack(pady=10)
    # 초기 지갑 정보 업데이트
    #update_balance_label()


    create_symbol_dropdown(right_frame)  # 코인 선택 드롭다운 메뉴 생성

    # 비트코인 가격 레이블 추가
    price_label = tk.Label(right_frame, text="")
    price_label.pack()
    update_price_label()  # 가격 업데이트 시작

    #거래목록
    trades_frame = tk.Frame(right_frame)
    trades_frame.pack(side=tk.BOTTOM, fill=tk.X)
    trades_label = tk.Label(trades_frame, text="진행 중인 거래 목록")
    trades_label.pack()
    trades_listbox = tk.Listbox(trades_frame, height=5)
    trades_listbox.pack(fill=tk.BOTH, expand=True)

    update_trades_list()

    # 오른쪽 프레임에 주문창 배치
    # 주문창 관련 위젯 배치
    create_order_form(right_frame)


def update_trades_list():
    try:
        # Bybit의 선물 거래에 대한 활성 주문 목록 조회
        symbol = "BTCUSD"
        trades_response = session.get_open_orders(category="linear", symbol=symbol)
        
        if trades_response['retCode'] == 0:
            trades = trades_response['result']['list']
            trades_listbox.delete(0, tk.END)
            for trade in trades:
                trade_info = f"ID: {trade['orderId']}, Price: {trade['price']}, Qty: {trade['qty']}, Status: {trade['orderStatus']}"
                trades_listbox.insert(tk.END, trade_info)
        else:
            error_message = f"Error code: {trades_response['retCode']}, Message: {trades_response['retMsg']}"
            trades_listbox.insert(tk.END, "No active trades. " + error_message)
    except Exception as e:
        print(f"Failed to retrieve trade data: {e}")
        trades_listbox.insert(tk.END, "Failed to load trade data.")

        # 추가로 오류 메시지를 더 자세히 출력할 수 있습니다.
        print(f"오류 상세: {e.__class__.__name__}, {e}")




def create_order_form(frame):
    global response_label, symbol_var, qty_entry, entry_price_entry, leverage_entry, tp_entry, sl_entry, order_id_entry, close_trade_price_entry

    # Position 선택 라디오 버튼
    position_frame = tk.Frame(frame)
    position_frame.pack()
    position_label = tk.Label(position_frame, text="포지션:")
    position_label.grid(row=0, column=0)
    position_var = tk.StringVar(value="none")
    long_radio = tk.Radiobutton(position_frame, text="롱", variable=position_var, value="long")
    short_radio = tk.Radiobutton(position_frame, text="숏", variable=position_var, value="short")
    long_radio.grid(row=0, column=1)
    short_radio.grid(row=0, column=2)

    # Order Type 선택 라디오 버튼
    order_type_frame = tk.Frame(frame)
    order_type_frame.pack()
    order_type_label = tk.Label(order_type_frame, text="주문 유형:")
    order_type_label.grid(row=0, column=0)
    order_type_var = tk.StringVar(value="none")
    limit_radio = tk.Radiobutton(order_type_frame, text="지정가", variable=order_type_var, value="limit")
    market_radio = tk.Radiobutton(order_type_frame, text="시장가", variable=order_type_var, value="market")
    limit_radio.grid(row=0, column=1)
    market_radio.grid(row=0, column=2)

    # Quantity 
    #  필드
    qty_label = tk.Label(frame, text="수량:")
    qty_label.pack()
    qty_entry = tk.Entry(frame)
    qty_entry.pack()

    # 수량 비율 버튼 추가
    create_percentage_buttons(frame)

    # 진입 가격 입력 필드
    entry_price_label = tk.Label(frame, text="진입 가격:")
    entry_price_label.pack()
    entry_price_entry = tk.Entry(frame)
    entry_price_entry.pack()

    # 레버리지 입력 필드
    leverage_label = tk.Label(frame, text="레버리지:")
    leverage_label.pack()
    leverage_entry = tk.Entry(frame)
    leverage_entry.pack()

    # TP 가격 입력 필드
    tp_label = tk.Label(frame, text="TP 가격:")
    tp_label.pack()
    tp_entry = tk.Entry(frame)
    tp_entry.pack()

    # SL 가격 입력 필드
    sl_label = tk.Label(frame, text="SL 가격:")
    sl_label.pack()
    sl_entry = tk.Entry(frame)
    sl_entry.pack()

    # 주문 실행 버튼
    submit_button = tk.Button(frame, text="주문 실행", command=lambda: create_order(session, symbol_var, position_var, order_type_var, qty_entry, entry_price_entry, leverage_entry, tp_entry, sl_entry))
    submit_button.pack()


    # 거래 종료 가격 입력 필드 생성
    close_trade_price_entry = create_close_trade_entry(frame)

    # 거래 종료 버튼
    close_trade_button = tk.Button(frame, text="거래 종료", command=lambda: close_trade(close_trade_price_entry))
    close_trade_button.pack()

    # 주문 ID 입력 필드
    order_id_label = tk.Label(frame, text="주문 ID:")
    order_id_label.pack()
    order_id_entry = tk.Entry(frame)
    order_id_entry.pack()

    # 주문 취소 버튼
    cancel_order_button = tk.Button(frame, text="주문 취소", command=lambda: cancel_order(order_id_entry.get()))
    cancel_order_button.pack()

    # 주문 응답 레이블
    response_label = tk.Label(frame, text="")
    response_label.pack()



root = tk.Tk()
root.title("Bybit 거래 및 차트")
root.geometry("1200x600")
login()
root.mainloop()

