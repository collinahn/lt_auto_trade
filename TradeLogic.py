# 주식매매 의사결정을 하는 클래스.
# 싱글턴으로 동작하며 스레드로 동작하고 공유메모리 큐에 매수/매도 수량을 저장한다.

# 2021.08.12 created by taeyoung

import time

from PyQt5.sip import wrapinstance
from LoggerLT import Logger
from SharedMem import SharedMem
from utilsLT import QueueLT
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


#------------------여기에 각자 거래 로직 구현하세요------------------

    def Money_Flow_Index(self, nStockID):
        cls_TargetStock = self.iq_SharedMem.get_instance(nStockID)
        n_TodayDate = time.strftime("%x", time.localtime(time.time()))
        list_pos_mfr = [] # mfr이 양수인 날들의 값 저장
        list_neg_mfr = [] # mfr이 음수인 날들의 값 저장
        n_day_highest = 0 # 원하는 날의 고가
        n_day_lowest = 0 # 원하는 날의 저가
        n_day_end = 0 # 원하는 날의 종가
        n_day_tradevolume = 0 # 원하는 날의 거래량

# 14일간의 당일 고가, 저가, 종가의 평균을 n_tp에 저장 후, 그 당일 거래량과 곱한다
# MFR = 14 일간 양의 RMF/14일간 음의 RMF​
# MFI = 100 − (100 / 1+ MFR​)

# 14일간의 당일 고가, 저가, 종가, 거래량을 받아와야 하는데, 그걸 한번에 리스트로 받으면 정말 좋을 듯
# 아니면 아예 rmf, mfr를 구하는 식이 stocks.py에 저장되면 더 좋을 수도.. 굳이 여기서 연산하는거보다
# 거기서 연산된 값을 가져오는게 더 좋을거같다..

        for _ in range(14):
            n_tp = (n_day_highest + n_day_lowest + n_day_end)/3
            n_rmf = n_tp * n_day_tradevolume

            if n_rmf >= 0:
                list_pos_mfr.append(n_rmf)
            else:
                list_neg_mfr.append(n_rmf)
            
        n_mfr = sum(list_pos_mfr)/sum(list_neg_mfr)
        n_mfi = 100 - 100/(1+n_mfr)

        #------------------사는 로직 ------------------------------
        if n_mfi <= 30 or cls_TargetStock.trade_option == 'Buy': #과매도 상태
            dict_BuyRequest = { 
                "StockID":nStockID,
                "TradeOption":cls_TargetStock.trade_option,
                "Buy":10, #보유금액 10%정도? 못정했다.
                "Sell":0
            }
            self.push_queue(dict_BuyRequest)
            self.log.INFO("Buy Request Pushed", dict_BuyRequest)
            time.sleep(3600)

        #------------------파는 로직 ------------------------------
        if n_mfi >= 70 or cls_TargetStock.trade_option == 'Sell': #과매수 상태
            dict_SellRequest = { 
            "StockID":nStockID,
            "TradeOption":cls_TargetStock.trade_option,
            "Buy":0,
            "Sell":cls_TargetStock.quantity
            }
            self.push_queue(dict_SellRequest)
            self.log.INFO("Sell Request Pushed", dict_SellRequest)
            time.sleep(3600)

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
            