#-*- encoding: utf-8 -*-

# 종목 코드를 인자로 클래스 호출하고 그에 따른 인스턴스 생성
# 이미 생성되어있는 종목코드를 실수로 다시 생성했을 때, 기존에 있던 인스턴스 리턴

# 2021.07.27 created by taeyoung
# 2021.07.31 modified by taeyoung : 현재 값 업데이트 로직 및 값 저장할 자료구조 클래스 추가, dict형 대응(hash)
# 2021.08.08 modified by taeyoung : property 데코레이터를 통해 setter와 getter 간소화, 옵저버 패턴 적용

# m: 클래스 멤버 변수
# i : 인스턴스 변수

from typing import List
import constantsLT as const
from LoggerLT import Logger
from utilsLT import QueueLT
import time

class Stock(object):
    __mn_TotalStock = 0         #인스턴스 생성 카운트하기 위한 클래스 변수
    __mset_Stocks = set()       #매개변수로 들어온 값들 저장하기 위한 set 클래스 변수
    __mdict_Obj = {}            #생성된 인스턴스들 저장하기 위한 dict 클래스 변수 { nTick:_instance }
    __mdict_ObjCalled = {}      #각 인스턴스들 호출 내역 저장하기 위한 dict 클래스 변수 { nTick:True }
                                #value가 true : 현재 보유중 false : 현재보유중 아님. key가 없을 땐 보유했던 적 없음

    #생성자가 이미 생성된 종목의 인스턴스인지 판단하고 그에 따라 중복 없이 인스턴스 할당
    def __new__(cls, *args):
        if isinstance(args[0], int) == False:
            raise(ValueError)

        if hasattr(cls, "_instance") and args[0] in Stock.__mset_Stocks:
            cls._instance = Stock.__mdict_Obj[args[0]]
        else:
            cls._instance = super().__new__(cls)
            Stock.__mdict_Obj[args[0]] = cls._instance
            Stock.__mdict_ObjCalled[args[0]] = True
            cls.log = Logger()
        
        cls.log.INFO(cls._instance)
        return cls._instance

    #인스턴스 변수 초기화
    def __init__(self, *args):
        # if {args[0]}.issubset(Stock.__mset_Stocks) == False:
        if args[0] not in Stock.__mset_Stocks:
            self.__in_Ticker = args[0]
            #나중에 완성된 키움 api wrapper 클래스로 여기서 초기화
            self.__is_StockName = ""
            self.__in_StockCurrentPrice = 0
            self.__iq_StockValues = QueueLT(const.STOCK_VALUE_QUEUE_SIZE, "StockValue") #주가 저장
            self.__in_StockQuantity = 0
            self.__iq_TotalTradeVolume = QueueLT(const.STOCK_TRADING_VOLUME_QUEUE_SIZE, "TradeVolumePerDay")
            self.__is_LastUpdated = ""
            self.__id_DayBought = time.strftime("%d", time.localtime(time.time())) #래리 윌리엄스 모듈에서만 사용
            # self.__if_StockFluncDay = 0.0
            # self.__if_StockFluncHour = 0.0
            # self.__if_StockFlunc30Min = 0.0
            # self.__if_StockFlunc5Min = 0.0
            self.__is_LogicOption = ""
            self.__ib_JohnBer = False
            self.__is_TradeOption = ""
            self.__il_PriceDataBefore = {
                "start":0,
                "end":0,
                "highest":0,
                "lowest":0
            } #필히 장마감 후 initialize할 때 초기화 해야함!

            Stock.__mn_TotalStock += 1
            Stock.__mset_Stocks.add(args[0])

            self.log.INFO("Stock init:", args[0], self._instance)
    
    def __hash__(self, *args):
        return hash((self.args[0]))

    #파이썬 gc 주기에 의해 즉시 반영이 안 될수도 있음
    def __del__(self):
        print("Delete Stock", self.__in_Ticker)
        Stock.__mn_TotalStock -= 1
        Stock.__mdict_ObjCalled[self.__in_Ticker] = False
        del(Stock.__mdict_Obj[self.__in_Ticker]) #제거되고 나면 새로운 인스턴스 생성

    @property
    def ticker(self) -> int:
        return self.__in_Ticker

    @property
    def name(self) -> str:
        return self.__is_StockName

    @property
    def quantity(self) -> int:
        return self.__in_StockQuantity

    @property
    def price(self) -> int:
        return self.__in_StockCurrentPrice

    #하루 단위 거래량 큐의 시작 인덱스와 큐에 해당하는 리스트를 튜플로 반환
    @property
    def stock_volume_q(self) -> tuple: 
        if self.__iq_TotalTradeVolume.getTailPoint() == 0:
            return const.STOCK_TRADING_VOLUME_QUEUE_SIZE - 1, self.__iq_TotalTradeVolume.getQueue()
        return self.__iq_TotalTradeVolume.getTailPoint() - 1, self.__iq_TotalTradeVolume.getQueue()
    
    #당일의 거래량 반환
    @property
    def stock_volume_n(self) -> int:
        return self.stock_volume_q[1][self.stock_volume_q[0]]

    @property
    def updated_time(self) -> str:
        return self.__is_LastUpdated

    @property
    def active_stock(self) -> int:
        return self.__mn_TotalStock

    @property
    def active_stocks(self) -> set:
        return self.__mset_Stocks

    @property
    def logic_option(self) -> set:
        return self.__is_LogicOption

    @property
    def johnber(self) -> bool:
        return self.__ib_JohnBer

    @property
    def trade_option(self) -> str:
        return self.__is_TradeOption

    #래리 윌리엄스 전략
    @property
    def day_bought(self) -> int: 
        return self.__id_DayBought

    @property
    def price_data_before(self) -> dict:
        return self.__il_PriceDataBefore

    
    @name.setter
    def name(self, sName: str) -> None:
        self.__is_StockName = sName

    #매수/매도시 현재 보유수량을 업데이트한다.
    @quantity.setter
    def quantity(self, nUpdatedQuantity: int) -> None:
        try:
            if self.__in_StockQuantity + nUpdatedQuantity < 0:
                raise(ValueError)

            self.__in_StockQuantity += nUpdatedQuantity
            self.log.INFO("Stock ID:", self.__in_Ticker, ",", \
                          "Updated Quanity:", self.__in_StockQuantity)
        except ValueError as ve:
            self.log.ERROR("ValueError:", ve)

    #현재 가격을 업데이트한다.
    @price.setter
    def price(self, nCurrentPrice: int) -> None:
        try:
            if str(type(nCurrentPrice)) != "<class 'int'>":
                raise(TypeError)

            if nCurrentPrice <= 100:
                raise(ValueError)
            
            self.__in_StockCurrentPrice = nCurrentPrice
            self.__iq_StockValues.pushQueue(nCurrentPrice)  # 큐에 저장
            
            self.log.INFO("Stock ID:", self.__in_Ticker, "Price Updated and Enqueued: ", nCurrentPrice)

        except ValueError as ve:
            self.log.ERROR("ValueError:", ve)
        except TypeError as te:
            self.log.ERROR("TypeError:", te)

    #하루 단위 거래량을 큐에 저장한다.
    @stock_volume_q.setter
    def stock_volume_q(self, nTradeVolume: int) -> None:
        self.__iq_TotalTradeVolume.pushQueue(nTradeVolume)
        self.__iq_TotalTradeVolume.pullQueue()  #10일간의 데이터를 저장해두기 위해서 테일포인트를 옮기는 순간 헤드포인트도 옮긴다
        
        self.log.INFO("Stock ID:", self.__in_Ticker, "Total Stock Volume Updated and Enqueued:", nTradeVolume)

    #api가 주는 데이터로 업데이트를 마치고 꼭 호출 필요
    #SharedMem.py에서 구현한다.
    @updated_time.setter
    def updated_time(self, sNowTime):
        self.__is_LastUpdated = sNowTime

    @logic_option.setter
    def logic_option(self, sOption: str):
        if sOption in const.LOGIC_OPTION:
            self.__is_LogicOption = sOption
            self.log.INFO("Logic option", sOption, "is Set")
        else:
            self.log.CRITICAL("Non-Existing Logic Option!!")

    @johnber.setter
    def johnber(self, bJohnber: bool):
        self.__ib_JohnBer = bJohnber
        self.log.INFO("Johnber option", bJohnber, "is Set")

    @trade_option.setter
    def trade_option(self, sOption: str):
        if sOption in const.TRADE_OPTION:
            self.__is_TradeOption = sOption
            self.log.INFO("Trade option", sOption, "is Set")
        else:
            self.log.CRITICAL("Non-Existing Trade Option!!")

    #래리 윌리엄스 전략
    @day_bought.setter
    def day_bought(self, dayBought: int):
        self.__id_DayBought = dayBought

    #[전일시가, 전일종가] 로 매일 초기화 반드시 해야함
    @price_data_before.setter
    def price_data_before(self, dict_price: dict):
        self.__il_PriceDataBefore = dict_price





if __name__ == "__main__":
    a = Stock(111100)
    print("active stock is", a.active_stock)
    b = Stock(111110)
    print("active stock is", b.active_stock)
    c = Stock(111111)
    print("active stock is", c.active_stock)
    d = Stock(111111)
    print("active stock is", d.active_stock)
    # error = Stock('1')
    # e = Stock(1)

    a.price = 10_000
    b.price = 20_000
    for stocks in a.active_stocks:
        print("stock:", stocks, "stock price", Stock(stocks).price)
    
    c.logic_option = "LarryWilliams"
    print(c.logic_option)