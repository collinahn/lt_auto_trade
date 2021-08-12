# 주식매매 의사결정을 하는 클래스.
# 싱글턴으로 동작하며 스레드로 동작하고 공유메모리 큐에 매수/매도 수량을 저장한다.

# 2021.08.12 created by taeyoung

import time
from LoggerLT import Logger
from SharedMem import SharedMem
from utilsLT import QueueLT
import constantsLT as const

class TradeLogic:
    
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, *args, **kwargs):
        cls = type(self)
        if not hasattr(cls, "_init"):
            cls._init = True

            self.iq_SharedMem = SharedMem()

            self.log = Logger()
            self.log.INFO(cls._instance)

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
        n_TodayDate = time.strftime("%d", time.localtime(time.time()))
        dict_Data = cls_TargetStock.price_data_before
        

        #------------------파는 로직------------------
        #거래 다음날 시가에 전부 던진다
        #아직 존버는 구현 안함
        if cls_TargetStock.quantity > 0 and cls_TargetStock.day_bought != n_TodayDate:
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
        if dict_Data["start"] < dict_Data["end"] \
            and dict_Data["highest"] + dict_Data["lowest"] < n_PriceNow \
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
            #거래 일자 갱신 7월21일 -> 21
            #큐는 들어갔어도 거래가 실패할 수도 있는데 미리 초기화를 해 주는 이유는 거래가 안되었으면 어짜피 파는 조건문은 실행 안될 것이기 때문
            cls_TargetStock.day_bought = n_TodayDate
        #------------------사는 로직 끝------------------

        return True


#------------------여기에 각자 거래 로직 구현하세요------------------





#------------------여기에 각자 거래 로직 구현하세요------------------


    #스레드에서 호출되는 함수(전체 로직이 호출되어야 함)
    def show_me_the_money(self):
        while True:
            cls_SM = SharedMem()

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
            