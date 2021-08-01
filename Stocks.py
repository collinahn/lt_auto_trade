#-*- encoding: utf-8 -*-

# 종목 코드를 인자로 클래스 호출하고 그에 따른 인스턴스 생성
# 이미 생성되어있는 종목코드를 실수로 다시 생성했을 때, 기존에 있던 인스턴스 리턴

# 2021.07.27 created by taeyoung
# 2021.07.31 modifed by taeyoung : 현재 값 업데이트 로직 및 값 저장할 자료구조 클래스 추가, dict형 대응(hash)

# m: 클래스 멤버 변수
# i : 인스턴스 변수

import constantsLT as const

class Stock(object):

    __mn_TotalStock = 0         #인스턴스 생성 카운트하기 위한 클래스 변수
    __mset_Stocks = set()       #매개변수로 들어온 값들 저장하기 위한 set 클래스 변수
    __mdict_Obj = {}            #생성된 인스턴스들 저장하기 위한 dict 클래스 변수 { nTick:_instance }
    __mdict_ObjCalled = {}      #각 인스턴스들 호출 내역 저장하기 위한 dict 클래스 변수 { nTick:True }

    #생성자가 이미 생성된 종목의 인스턴스인지 판단하고 그에 따라 중복 없이 인스턴스 할당
    def __new__(cls, *args):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            Stock.__mdict_Obj[args[0]] = cls._instance
            Stock.__mdict_ObjCalled[args[0]] = True
        elif {args[0]}.issubset(Stock.__mset_Stocks) == False:
            cls._instance = super().__new__(cls)
            Stock.__mdict_Obj[args[0]] = cls._instance
            Stock.__mdict_ObjCalled[args[0]] = True
        else:
            cls._instance = Stock.__mdict_Obj[args[0]]
        return cls._instance

    #인스턴스 변수 초기화
    def __init__(self, *args):
        if {args[0]}.issubset(Stock.__mset_Stocks) == False:
            self.__in_Ticker = args[0]
            #나중에 완성된 키움 api wrapper 클래스로 여기서 초기화
            self.__is_StockName = ""
            self.__in_StockCurrentValue = 0
            self.__iq_StockValues = StockValuesQueue(const.STOCK_VALUE_QUEUE_SIZE) #주가 저장
            self.__in_StockTradeVolume = 0
            self.__if_StockFluncDay = 0.0
            self.__if_StockFluncHour = 0.0
            self.__if_StockFlunc30Min = 0.0
            self.__if_StockFlunc5Min = 0.0

            Stock.__mn_TotalStock += 1
            Stock.__mset_Stocks.add(args[0])
    
    def __hash__(self, *args):
        return hash((self.args[0]))

    #파이썬 gc 주기에 의해 즉시 반영이 안 될수도 있음
    def __del__(self):
        Stock.__mn_TotalStock -= 1
        Stock.__mdict_ObjCalled[self.__in_Ticker] = False

    def getTicker(self) -> int:
        return self.__in_Ticker

    def updateCurrentValue(self, nCurrentValue: int) -> None:
        try:
            if str(type(nCurrentValue)) != "<class 'int'>":
                raise(TypeError)

            if nCurrentValue <= 100:
                raise(ValueError)
            
            self.__in_StockCurrentValue = nCurrentValue
            self.__iq_StockValues.pushQueue(nCurrentValue)  # 큐에 저장

        except ValueError as ve:
            print("class Stock func updateCurrentValue : ValueError", ve)
        except TypeError as te:
            print("class Stock func updateCurrentValue : TypeError", te)

    def updateCurrentVolume(self, nUpdatedVolume: int) -> None:
        try:
            self.__in_StockTradeVolume += nUpdatedVolume
            if self.__in_StockTradeVolume < 0:
                raise(ValueError)
        except ValueError as ve:
            print("class Stock func updateCurrentVolume : ValueError", ve)

    def getCurrentValue(self) -> int:
        return self.__in_StockCurrentValue

    def getActiveStock(self) -> int:
        return self.__mn_TotalStock

    def getActiveStocks(self) -> set:
        return self.__mset_Stocks




class StockValuesQueue:

    def __init__(self, nSize: int):
        self.__iq_Queue = [None] * nSize
        self.__in_QueueSize = nSize
        self.__in_HeadPointIdx = 0
        self.__in_TailPointIdx = 0
        
    #큐에 데이터를 집어넣고 테일포인트를 옮긴다.
    def pushQueue(self, nStockValue: int) -> bool:
        n_NextTailPointIdx = (self.__in_TailPointIdx +1) % self.__in_QueueSize
        
        if n_NextTailPointIdx is self.__in_HeadPointIdx:            # 테일+1 == 헤드(버퍼 full) 
            return False
        else:
            self.__iq_Queue[self.__in_TailPointIdx] = nStockValue   # 테일포인터가 가르키는 자리에 value삽입
            self.__in_TailPointIdx = n_NextTailPointIdx             # 다음 자리로 테일포인터 이동.
            return True
        
    #큐에서 데이터를 빼고(함수 앞에서 getHead로) 헤드포인트를 옮긴다.
    def pullQueue(self) -> bool:
        n_NextHeadPointIdx = (self.__in_HeadPointIdx+1) % self.__in_QueueSize

        if self.__in_HeadPointIdx is self.__in_TailPointIdx:        # 테일 == 헤드 (buffer empty)
            return False
        else:
            self.__in_HeadPointIdx = n_NextHeadPointIdx
            return True

    # pull oldest push
    def getHead(self) -> int:
        return self.__iq_Queue[self.__in_HeadPointIdx]
        
    # pull latest push
    def getTail(self) -> int:
        #  테일포인트는 미리 데이터가 삽입될 곳을 가리키고 있음
        if self.__in_TailPointIdx == 0:
            return self.__iq_Queue[self.__in_QueueSize - 1]
        return self.__iq_Queue[self.__in_TailPointIdx -1] 
        

    def isEmpty(self) -> bool:
        return self.__in_HeadPointIdx == self.__in_TailPointIdx
        

    def isFull(self) -> bool:
        n_NextTailPointIdx = (self.__in_TailPointIdx +1) % self.__in_QueueSize

        return n_NextTailPointIdx == self.__in_HeadPointIdx             # 테일+1 == 헤드 => 버퍼 full






# __self__ 
