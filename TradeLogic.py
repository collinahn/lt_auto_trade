# 주식매매 의사결정을 하는 클래스.
# 싱글턴으로 동작하며 스레드로 동작하고 공유메모리 큐에 매수/매도 수량을 저장한다.

# 2021.08.12 created by taeyoung
# 2021.08.18 modified by chanhyeok (종가베팅방법 추가)

import time

# from PyQt5.sip import wrapinstance
from LoggerLT import Logger
from SharedMem import SharedMem
from utilsLT import QueueLT
from datetime import datetime
import constantsLT as const


class TradeLogic:
    
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls.log = Logger()

        cls.log.INFO(cls._instance)
        return cls._instance

    def __init__(self, *args, **kwargs):
        cls = type(self)
        if not hasattr(cls, "_init"):
            cls._init = True

            self.iq_SharedMem = SharedMem()

            self.log.INFO("TradeLogic init")

    def print_queue(self):
        print(self.iq_SharedMem.iq_RequestQueue)
        print(self.iq_SharedMem.iq_RequestQueue.getHead())

    # 요청 형식을 푸시한다
    def push_queue(self, dictRequestFormat: dict):
        #파이썬스럽지 않은 코드인데 누가 파이썬스럽게 고쳐줄사람 2021.08.12 by aty
        while self.iq_SharedMem.iq_RequestQueue.pushQueue(dictRequestFormat) == False:
            #큐가 꽉 차서 와일 내부 문장이 실행된다면, 처리될 때까지 잠시 기다린다.
            time.sleep(0.1)
            

    #의사결정 로직1, tested 2021.08.12
    #반드시 파는 로직과 사는 로직을 한 함수에 전부 기록해야한다.
    def Logic1(self, nStockID: int) -> bool:
        #self.iq_SharedMem에서 필요한 데이터를 종합해 살지 말지 결정하고 몇 주 살건지 결정, dict형으로 매수/매도할 때 필요한 정보 전달

        #보유 수량이 0보다 크면 팔 궁리부터
        if self.iq_SharedMem.get_instance(nStockID).quantity > 0:
            #파는 로직 구현부
            dict_SellRequest = { 
            "StockID":nStockID,
            "TradeOption":0,
            "JohnBer":self.iq_SharedMem.get_instance(nStockID).johnber,
            "Buy":0,
            "Sell":10 #보유수량보다 작거나 같게
            }
            self.push_queue(dict_SellRequest)

        #사는건 항상 노려라
        #사는 로직 구현부
        #dict 형식: key고정, value만 변환해서 쓰기
        # 예시(종목코드 11011, 시장가로 10주 매수, 매수 옵션:(미정), 존버안함)
        # { "StockID":11011, "Buy":10, "Sell":0, "TradeOption":0 "JohnBer":False }
        dict_BuyRequest = { 
            "StockID":nStockID,
            "TradeOption":0,
            "JohnBer":self.iq_SharedMem.get_instance(nStockID).johnber,
            "Buy":10,
            "Sell":0
        }
        self.push_queue(dict_BuyRequest)

        return True


    def Larry_Williams(self, nStockID: int) -> bool:
        cls_TargetStock = self.iq_SharedMem.get_instance(nStockID)
        n_PriceNow = cls_TargetStock.price
        n_PriceBought = cls_TargetStock.price_bought
        n_TodayDate = time.strftime("%x", time.localtime(time.time())) # 08/15/21
        dict_DayBefore = cls_TargetStock.price_data_before
        

        #------------------파는 로직------------------
        #존버조건에 해당하지 않는다면 거래 다음날 시가에 전부 던진다
        if cls_TargetStock.quantity > 0 and cls_TargetStock.day_bought != n_TodayDate:
            if cls_TargetStock.johnber == True and n_PriceBought > n_PriceNow:
                self.log.INFO("Johnber Executed", "price bought:", cls_TargetStock.price_bought, "price now:", cls_TargetStock.price)
            else:
                dict_SellRequest = { 
                "StockID":nStockID,
                "TradeOption":cls_TargetStock.trade_option,
                "JohnBer":cls_TargetStock.johnber,
                "Buy":0,
                "Sell":cls_TargetStock.quantity
                }
                self.push_queue(dict_SellRequest)
                self.log.INFO("Sell Request Pushed", dict_SellRequest)

        #------------------파는 로직 끝------------------


        #------------------사는 로직------------------
        #전날 양봉이고 전날 최고가와 최저가 평균을 넘을 때 산다
        if dict_DayBefore["start"] < dict_DayBefore["end"] \
            and dict_DayBefore["highest"] + dict_DayBefore["lowest"] < n_PriceNow \
            and cls_TargetStock.day_bought != n_TodayDate:
            # 거래일이 오늘이면 더 사지 않는다.

            dict_BuyRequest = { 
                "StockID":nStockID,
                "TradeOption":cls_TargetStock.trade_option,
                "JohnBer":cls_TargetStock.johnber,
                "Buy":10, #보유금액 10%정도? 못정했다.
                "Sell":0
            }
            self.push_queue(dict_BuyRequest)
            self.log.INFO("Buy Request Pushed", dict_BuyRequest)
            #거래 일자 갱신 2021년 7월20일 -> 07/20/21
            #큐는 들어갔어도 거래가 실패할 수도 있는데 미리 초기화를 해 주는 이유는 거래가 안되었으면 어짜피 파는 조건문은 실행 안될 것이기 때문
            cls_TargetStock.day_bought = n_TodayDate
        #------------------사는 로직 끝------------------

        return True



#------------------종가베팅 거래 로직 구현------------------

    def Closing_Price(self, nStockID: int) -> bool:
        cls_TargetStock = self.iq_SharedMem.get_instance(nStockID)
        n_PriceNow = cls_TargetStock.price
        n_PriceBought = cls_TargetStock.price_bought
        n_TodayDate = time.strftime("%x", time.localtime(time.time())) # 08/20/21
        dict_DayBefore = cls_TargetStock.price_data_before

        #-------------파는 로직------------------
        #   1%이상 수익나면 다음날 바로 매도(일부만 파는 방법)
        if cls_TargetStock.quantity > 0 and float(n_PriceNow/n_PriceBought) - 1 >= 0.01:
            if cls_TargetStock.johnber == True:
                dict_SellRequest = { 
                "StockID":nStockID,
                "TradeOption":cls_TargetStock.trade_option,
                "JohnBer":cls_TargetStock.johnber,
                "Buy":0,
                "Sell":cls_TargetStock.quantity//2
                }
                self.log.INFO("Johnber Executed", "Remain_Quantity:", cls_TargetStock.quantity//2)
            else:
                dict_SellRequest = { 
                "StockID":nStockID,
                "TradeOption":cls_TargetStock.trade_option,
                "JohnBer":cls_TargetStock.johnber,
                "Buy":0,
                "Sell":cls_TargetStock.quantity
                }

            self.push_queue(dict_SellRequest)
            self.log.INFO("Sell Request Pushed", dict_SellRequest)

        #------------------파는 로직 끝------------------

        #-------------사는 로직------------------
        #종가베팅 유의점 (1) 미국장 악재 고려해 금요일, 공휴일 전날 피하기 (2)주식 증거금 100%피하기
        #사는 로직
        #1. 주식시장이 끝나면 당일거래상위 증100제외 거래량 상위1~40위에서 장대양봉 뽑음 (조건식을 이용해야할 것 같음.)
        #2. 현재가가 전날 종가보다 낮은 가격O 
        if dict_DayBefore["start"] < dict_DayBefore["end"] \
        and dict_DayBefore["end"] > n_PriceNow:
        #전날 거래량 대비 거래량이 60%이상 감소
        #당일 3분봉 차트에서 20이동평균선을 관찰 (어떻게 구현할지 막힘...)
           
            dict_BuyRequest = { 
                "StockID":nStockID,
                "TradeOption":cls_TargetStock.trade_option,
                "JohnBer":cls_TargetStock.johnber,
                "Buy":10, #10%(미정)
                "Sell":0
            }
            self.push_queue(dict_BuyRequest)
            self.log.INFO("Buy Request Pushed", dict_BuyRequest)
            
        #------------------사는 로직 끝------------------

# 14일간의 당일 고가, 저가, 종가의 평균을 n_tp에 저장 후, 그 당일 거래량과 곱한다
# MFR = 14 일간 양의 RMF/14일간 음의 RMF​
# MFI = 100 − (100 / 1+ MFR​)

# 14일간의 당일 고가, 저가, 종가, 거래량을 받아와야 하는데, 그걸 한번에 리스트로 받으면 정말 좋을 듯
# 아니면 아예 rmf, mfr를 구하는 식이 stocks.py에 저장되면 더 좋을 수도.. 굳이 여기서 연산하는거보다
# 거기서 연산된 값을 가져오는게 더 좋을거같다..

    def Money_Flow_Index(self, nStockID):
        cls_TargetStock = self.iq_SharedMem.get_instance(nStockID)
        cls_AccountInfo = self.iq_SharedMem.get_usr_info()
        n_TodayDate = time.strftime("%x", time.localtime(time.time()))
        n_mfi = cls_TargetStock.mfi
        now = datetime.now()
        n_investmoney = 0 # 초기 자본 (초기 투자 금액) <- 이 정보가 저장이 되어있나? 안되어있는거같긴한데.. 다른방법을 고안해봐야할듯..

        if cls_AccountInfo['current_cash'] >= n_investmoney*0.2: # 최소 초기 자본 20% 이상이 있어야 거래 진행, cls_AccountInfo['current_cash'] = 계좌정보에서의 예수금 (현재 보유 현금)
            #------------------사는 로직 ------------------------------
            if 0 <= n_mfi <= 30: #과매도 상태
                if 9 <= now.hour <= 15 and now.minute == 0 and now.second%60 == 0: # 매 시각 정각에만 매수 (계속 과매수상태여도 한시간에 한번만 매수한다) <- 의도는 그렇긴한데.. 쉽지않네
                    dict_BuyRequest = { 
                        "StockID":nStockID,
                        "TradeOption":cls_TargetStock.trade_option,
                        "Buy":10, #보유금액 10%정도? 못정했다.
                        "Sell":0
                    }
                    self.push_queue(dict_BuyRequest)
                    self.log.INFO("Buy Request Pushed", dict_BuyRequest)

            #------------------파는 로직 ------------------------------
            if n_mfi >= 70 and cls_TargetStock.quantity > 0: #과매수 상태
                dict_SellRequest = { 
                "StockID":nStockID,
                "TradeOption":cls_TargetStock.trade_option,
                "Buy":0,
                "Sell":cls_TargetStock.quantity
                }
                self.push_queue(dict_SellRequest)
                self.log.INFO("Sell Request Pushed", dict_SellRequest)

            else: # mfi < 0 일 경우
                self.log.INFO("error occured", n_mfi)
        else:
            self.log.INFO("최소 현금 보유금액을 유지하기 위해 거래 중지")
            
#--------- 아래는 무시 바람------------------#

        # n_exp_moving_average_12 = 0 #3일 지수이동평균(EMA) = (((금일 종가 x 2/(1+n)) + (전 EMA x (1 - 2/(1+n)))) n은 몇일 기준인지
        # n_exp_moving_average_26 = 0 #7일 지수이동평균
        # n_macd_line = n_exp_moving_average_12 - n_exp_moving_average_26
        # n_signal_line = 

        # MFI 공식 이용 
        # 기본 로직 - MACD 오실레이터 (3일 지수이동평균, 7일 지수이동평균)사용함

#------------------여기에 각자 거래 로직 구현하세요------------------


    #스레드에서 호출되는 함수(전체 로직이 호출되어야 함)
    def show_me_the_money(self):
        cls_SM = SharedMem()
        while True:

            for key, value in cls_SM.get_shared_mem():
                #사용하는 이름은 무조건 constantsLT 파일에 등록이 되어있고 Stock인스턴스에 속성으로 초기화를 시켜줘야한다.
                if value.trade_option not in const.LOGIC_OPTION:
                    time.sleep(1)
                    continue

                if value.trade_option == 'LarryWilliams':
                    self.Larry_Williams(key)

                #sharedMem 가져와서 어떤 옵션인지 확인하고 해당 종목 인스턴스로 해당 함수 실행
                elif value.trade_option == 'CandleTrade':
                    pass

                elif value.trade_option == 'CoolTradeOption':
                    pass


            time.sleep(1)
            