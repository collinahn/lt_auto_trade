#-*- encoding: utf-8 -*-

# 종목 코드를 인자로 클래스 호출하고 그에 따른 인스턴스 생성
# 이미 생성되어있는 종목코드를 실수로 다시 생성했을 때, 기존에 있던 인스턴스 리턴

# 2021.07.27 created by taeyoung
# 2021.07.31 modified by taeyoung : 현재 값 업데이트 로직 및 값 저장할 자료구조 클래스 추가, dict형 대응(hash)
# 2021.08.08 modified by taeyoung : property 데코레이터를 통해 setter와 getter 간소화, 옵저버 패턴 적용

# m: 클래스 멤버 변수
# i : 인스턴스 변수

from datetime import datetime
import time
from . import constantsLT as const
from .LoggerLT import Logger
from .utilsLT import QueueLT

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
    #첫 번째 인자는 종목코드, 두 번째 인자는 알고리즘옵션, 세 번째 인자는 매매옵션(구현안됨) 2021.09.08
    def __init__(self, nStockID: int, sLogicOption: str='', sTradeOption: str='', *args):
        # if {nStockID}.issubset(Stock.__mset_Stocks) == False:
        if nStockID not in Stock.__mset_Stocks:
            self.__in_Ticker = nStockID
            self.__is_LogicOption = sLogicOption
            self.__is_TradeOption = sTradeOption

            self.__is_StockName = ""
            self.__in_StockCurrentPrice = 0
            self.__iq_StockValues = QueueLT(const.STOCK_VALUE_QUEUE_SIZE, str(self.__in_Ticker)+"StockValue") #주가 저장
            self.__in_StockVolumeRealTime = 0
            self.__in_StockPriceBought = 0
            self.__in_StockPossessedQuantity = 0
            self.__in_DayTradeVolume = 0
            self.__iq_TotalTradeVolume = QueueLT(const.STOCK_COMMON_SIZE, str(self.__in_Ticker)+"TradeVolume")
            self.__is_LastUpdated = ""
            self.__is_LastAdded = str(datetime.now())
            self.__is_DayBought = time.strftime("%x", time.localtime(time.time())) #  08/15/21 거래된 날을 따저 추가적인 거래가 일어나지 않도록 한다.
            # self.__if_StockFluncDay = 0.0
            # self.__if_StockFluncHour = 0.0
            # self.__if_StockFlunc30Min = 0.0
            # self.__if_StockFlunc5Min = 0.0
            self.__ib_JohnBer = False
            self.__id_PriceDataBefore = {
                "start":0,
                "end":0,
                "highest":0,
                "lowest":0
            }
            self.__iq_PriceDataQueue = QueueLT(const.STOCK_COMMON_SIZE, str(self.__in_Ticker)+"PriceData") # n일간의 가격 정보를 저장한다.

            Stock.__mn_TotalStock += 1
            Stock.__mset_Stocks.add(nStockID)

            self.log.INFO("Stock init:", nStockID, self._instance)
    
    def __hash__(self, *args):
        return hash((self.args[0]))

    #파이썬 gc 주기에 의해 즉시 반영이 안 될수도 있음
    def __del__(self):
        print(datetime.now(), "Stock Deleted", self.__in_Ticker)
        Stock.__mn_TotalStock -= 1
        Stock.__mdict_ObjCalled[self.__in_Ticker] = False
        del(Stock.__mdict_Obj[self.__in_Ticker]) #제거되고 나면 추후 추가될 때 새로 인스턴스 생성

    @property
    def ticker(self) -> int:
        return self.__in_Ticker

    @property
    def name(self) -> str:
        return self.__is_StockName

    @property
    def price_bought(self) -> int:
        return self.__in_StockPriceBought

    @property
    def quantity(self) -> int:
        return self.__in_StockPossessedQuantity

    @property
    def price(self) -> int:
        return self.__in_StockCurrentPrice

    @property
    def price_q(self) -> QueueLT:
        return self.__iq_StockValues

    #실시간 거래량
    @property
    def volume_rt(self) -> int:
        return self.__in_StockVolumeRealTime
    
    #당일의 거래량 반환
    @property
    def stock_volume(self) -> int:
        return self.__in_DayTradeVolume

    @property
    def stock_volume_q(self) -> QueueLT: 
        return self.__iq_TotalTradeVolume

    @property
    def updated_time(self) -> str:
        return self.__is_LastUpdated

    @property
    def last_added_time(self) -> str:
        return self.__is_LastAdded

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
        return self.__is_DayBought

    @property
    def price_data_before(self) -> dict:
        return self.__id_PriceDataBefore

    @property
    def price_data_q(self) -> QueueLT:
        return self.__iq_PriceDataQueue

    #평균가격
    def _tp(self, dict_Price: dict) -> float:
        return (dict_Price["highest"] + dict_Price["lowest"] + dict_Price["end"]) / 3

    #tp * 거래량
    #역순정렬이라 전일 평균거래가는 nthDate+1을 본다.
    #tp가 양이면 true, 아니면 false를 덧붙여 반환한다.
    def _rmf(self, nthDate: int):
        # 최근 순으로 14개를 계산할 거임. 이때 두 리스트의 크기는 14보다 커야한다.
        # 사이즈 커지면 오래걸릴텐데,,, 미리 계산을 끝내놓을 수 없나?
        lst_priceData = self.__iq_PriceDataQueue.getList().reverse()
        lst_volume = self.__iq_TotalTradeVolume.getList().reverse()

        if len(lst_priceData) < const.MFI_STANDARD+1 and len(lst_volume) < const.MFI_STANDARD+1:
            self.log.CRITICAL("PriceData and TradeVolume Queue Size Error !")
            raise ValueError

        bRet = False
        if self._tp(lst_priceData[nthDate]) > self._tp(lst_priceData[nthDate+1]): #전일보다 큼: 양의 tp
            bRet = True

        return self._tp(lst_priceData[nthDate])*lst_volume[nthDate], bRet

    # MFR = 14 일간 양의 RMF/14일간 음의 RMF
    def mfr(self) -> float:
        pos_rmf = 0
        neg_rmf = 0

        for idx in range(const.MFI_STANDARD):
            rmf, bSign = self._rmf(idx)
            if bSign == True:
                pos_rmf += rmf
            else:
                neg_rmf += rmf

        return (pos_rmf / neg_rmf) if neg_rmf != 0 else -1

    # MFI = 100 − (100 / 1+ MFR​)
    @property
    def mfi(self) -> float:
        try:
            return 100 - (100 / (1+self.mfr()))
        except ZeroDivisionError as ze:
            self.log.ERROR("Negative RMF sum 0", ze)
            return -1

    @name.setter
    def name(self, sName: str) -> None:
        self.__is_StockName = sName

    @price_bought.setter
    def price_bought(self, nAveragePriceBought: int) -> None:
        self.__in_StockPriceBought = nAveragePriceBought

    #매수/매도시 현재 보유수량을 업데이트한다.
    @quantity.setter
    def quantity(self, nUpdatedQuantity: int) -> None:
        try:
            if self.__in_StockPossessedQuantity + nUpdatedQuantity < 0:
                raise(ValueError)

            self.__in_StockPossessedQuantity += nUpdatedQuantity
            self.log.INFO("Stock ID:", self.__in_Ticker, ",", \
                          "Updated Quanity:", self.__in_StockPossessedQuantity)
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

    @volume_rt.setter
    def volume_rt(self, nVolumeRT: int) -> None:
        self.__in_StockVolumeRealTime = nVolumeRT
        # self.log.DEBUG("Stock ID:", self.__in_Ticker, "VolumeRT updated:", nVolumeRT)

    #하루 단위 거래량을 큐에 저장한다.
    @stock_volume.setter
    def stock_volume(self, nTradeVolume: int) -> None:

        self.__in_DayTradeVolume = nTradeVolume

        self.__iq_TotalTradeVolume.pushQueue(nTradeVolume)
        self.__iq_TotalTradeVolume.pullQueue()  #10일간의 데이터를 저장해두기 위해서 테일포인트를 옮기는 순간 헤드포인트도 옮긴다
        
        # self.log.DEBUG("Stock ID:", self.__in_Ticker, "Total Stock Volume Updated and Enqueued:", nTradeVolume)

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
        self.__is_DayBought = dayBought

    #[전일시가, 전일종가] 로 매일 초기화 반드시 해야함, 자동으로 큐에 들어감
    @price_data_before.setter
    def price_data_before(self, dict_Price: dict):
        self.__id_PriceDataBefore = dict_Price
        self.__iq_PriceDataQueue.pushQueue(dict_Price)
        self.__iq_PriceDataQueue.pullQueue()  

    # @price_data_q.setter
    # def price_data_q(self, dict_Price: dict):
    #     self.__iq_PriceDataList.pushQueue(dict_Price)
    #     self.__iq_PriceDataList.pullQueue()        #데이터를 pull하는 곳이 없음





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