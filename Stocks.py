#-*- encoding: utf-8 -*-

# 필요로 하는 항목들 클래스 호출 시 인스턴스 생성
# 종목 코드가 같으면 기존에 있던 인스턴스 리턴

# 2021.07.27 created by taeyoung

# m: 클래스 멤버 변수
# i : 인스턴스 변수

class Stock:
    __mn_TotalStock = 0
    __mset_Stocks = set()
    __mdict_Obj = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            Stock.__mdict_Obj[args[0]] = cls._instance
        elif {args[0]}.issubset(Stock.__mset_Stocks) == False:
            cls._instance = super().__new__(cls)
            Stock.__mdict_Obj[args[0]] = cls._instance
        else:
            cls._instance = Stock.__mdict_Obj[args[0]]
        return cls._instance


    def __init__(self, *args):
        if {args[0]}.issubset(Stock.__mset_Stocks) == False:
            self.__in_Ticker = args[0]
            self.__is_StockName = ""
            self.__in_StockValue = 0
            self.__in_StockTradeVolume = 0
            self.__if_StockFluncDay = 0.0
            self.__if_StockFluncHour = 0.0
            self.__if_StockFlunc30Min = 0.0
            self.__if_StockFlunc5Min = 0.0

            Stock.__mn_TotalStock += 1
            Stock.__mset_Stocks.add(args[0])

    def __del__(self):
        Stock.__mn_TotalStock -= 1

    def getNumberActiveStock(self):
        return self.__mn_TotalStock

    def getSetActiveStocks(self):
        return self.__mset_Stocks

    def getNumberTicker(self):
        return self.__in_Ticker




cls_stock1 = Stock(2199)
print(cls_stock1.getNumberTicker())
cls_stock2 = Stock(1002)
print(cls_stock2.getNumberTicker())
cls_stock3 = Stock(2100)
print(cls_stock3.getNumberTicker())
cls_stock4 = Stock(2199)
print(cls_stock4.getNumberTicker())
cls_stock5 = Stock(2199)
print(cls_stock5.getNumberTicker())

print(cls_stock1.getSetActiveStocks())
print(cls_stock2.getNumberActiveStock())

del(cls_stock1)
del(cls_stock5)

print(cls_stock2.getNumberActiveStock())



