#-*- encoding: utf-8 -*-

# 종목 코드를 인자로 클래스 호출하고 그에 따른 인스턴스 생성
# 이미 생성되어있는 종목코드를 실수로 다시 생성했을 때, 기존에 있던 인스턴스 리턴

# 2021.07.27 created by taeyoung

# m: 클래스 멤버 변수
# i : 인스턴스 변수

class Stock:
    __mn_TotalStock = 0         #인스턴스 생성 카운트하기 위한 클래스 변수
    __mset_Stocks = set()       #매개변수로 들어온 값들 저장하기 위한 set 클래스 변수
    __mdict_Obj = {}            #생성된 인스턴스들 저장하기 위한 dict 클래스 변수 { nTick:_instance }
    __mdict_ObjCalled = {}      #각 인스턴스들 호출 내역 저장하기 위한 dict 클래스 변수 { nTick:True }

    #생성자가 이미 생성된 종목의 인스턴스인지 판단하고 그에 따라 중복 없이 인스턴스 할당
    def __new__(cls, *args, **kwargs):
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
    def __init__(self, *args, **kwargs):
        if {args[0]}.issubset(Stock.__mset_Stocks) == False:
            self.__in_Ticker = args[0]
            #나중에 완성된 api 클래스로 여기서 초기화
            self.__is_StockName = ""
            self.__in_StockValue = 0
            self.__in_StockTradeVolume = 0
            self.__if_StockFluncDay = 0.0
            self.__if_StockFluncHour = 0.0
            self.__if_StockFlunc30Min = 0.0
            self.__if_StockFlunc5Min = 0.0

            Stock.__mn_TotalStock += 1
            Stock.__mset_Stocks.add(args[0])

    #파이썬 gc 주기에 의해 바로 반영이 안 될수도 있음
    def __del__(self):
        Stock.__mn_TotalStock -= 1
        Stock.__mdict_ObjCalled[self.__in_Ticker] = False
        # Stock.__mdict_ObjCalled[self.__in_Ticker] -= 1
        # if Stock.__mdict_ObjCalled[self.__in_Ticker] == 1:
            # Stock.__mn_TotalStock -= 1

    def getNumberTicker(self):
        return self.__in_Ticker

    def getNumberActiveStock(self):
        return self.__mn_TotalStock

    def getSetActiveStocks(self):
        return self.__mset_Stocks








# __self__ 
#2199번 종목 인스턴스 생성
cls_stock1 = Stock(2199)
# print(cls_stock1.getNumberTicker())
cls_stock2 = Stock(1002)
# print(cls_stock2.getNumberTicker())
cls_stock3 = Stock(2100)
# print(cls_stock3.getNumberTicker())
cls_stock4 = Stock(2199)
cls_stock41 = Stock(2199)
cls_stock42 = Stock(2199)
cls_stock43 = Stock(2199)
cls_stock44 = Stock(2199)
cls_stock45 = Stock(2199)
cls_stock46 = Stock(2199)
# print(cls_stock4.getNumberTicker())
# cls_stock5 = Stock(2199)
# print(cls_stock5.getNumberTicker())

print(cls_stock1.getSetActiveStocks())
print(cls_stock2.getNumberActiveStock())

del(cls_stock1)
# del(cls_stock4)
# del(cls_stock5)
 
print(cls_stock3.getNumberActiveStock())


del(cls_stock4)


del(cls_stock41)
print(cls_stock46.getNumberActiveStock())
del(cls_stock42)
print(cls_stock46.getNumberActiveStock())
del(cls_stock43)
print(cls_stock46.getNumberActiveStock())
del(cls_stock44)
print(cls_stock46.getNumberActiveStock()) 
del(cls_stock45)
del(cls_stock46)




