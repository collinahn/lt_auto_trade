#-*- encoding: utf-8 -*-

# 공유 메모리를 관리하는 클래스
# 생성한 Stock 클래스 인스턴스를 딕셔너리 형태로 보유하고 관리한다. 
# 싱글턴으로 생성됨.

# 2021.08.01 created by taeyoung

# m: 클래스 멤버 변수
# i : 인스턴스 변수

from typing import Dict, List
from datetime import datetime
from Stocks import Stock as st
from LoggerLT import Logger


class SharedMem(object):
    __mdict_MstObject = {}
    
    log = Logger()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, "_init"):
            cls._init = True
            # if문 내부에서 초기화 진행
            print("Construct of SharedMem", self._instance)
    
    def print_shared_mem(self):
        print(self.__mdict_MstObject)

    #key 값 = 종목코드
    def add(self, nKey: int) -> None:
        self.__mdict_MstObject[nKey] = st(nKey)

    #db에 반영하는 함수 또한 호출되어야 한다.
    def delete(self, nKey: int) -> None:
        del(self.__mdict_MstObject[nKey])

    #종목을 보유 중인지 확인한다
    def check_possess(self, nKey: int) -> bool:
        return nKey in self.__mdict_MstObject

    #인스턴스를 반환한다.
    def get_instance(self, nKey: int) -> object:
        if self.check_possess(nKey) == True:
            return self.__mdict_MstObject[nKey]
        else:
            return None

    #보유중인 종목의 수를 int로 반환한다.
    def get_current_possess(self) -> int:
        return len(self.__mdict_MstObject)

    #보유중인 종목의 코드들을 dict_keys 형태로 반환한다. 
    def get_current_ticks(self):
        return self.__mdict_MstObject.keys()

    #보유중인 종목의 현재값들을 Dict로 반환한다
    def get_current_price_all(self) -> Dict:
        dict_StockValues = {}
        for key, value in self.__mdict_MstObject.items():
            dict_StockValues[key] = value.price
        return dict_StockValues

    #타 스레드에서 주기적으로 호출 1
    def update_current_stock_price(self):
        for obj_Target in self.__mdict_MstObject.values():
            # updatedPrice = WrapperClass.WrapperMethod()
            # obj_Target.price(updatedPrice)
            pass
        
    #타 스레드에서 주기적으로 호출 2
    # 거래량의 경우 신뢰도를 위해 api쪽에서 받아온 데이터와 자체적으로 갖고있는 데이터를 비교 후 업데이트해야한다.
    def update_current_stock_quantity(self):
        for obj_Target in self.__mdict_MstObject.values():
            # updatedQuantity = WrapperClass.WrapperMethod()   #매수 : + / 매도 : -
            # obj_Target.quantity(updatedQuantity)
            pass

    #타 스레드에서 최초에 값을 채워넣고 장마감이후 하루에 한 번 호출 3
    def update_total_stock_trade_volume(self):
        for obj_Target in self.__mdict_MstObject.values():
            # updatedVolume = WrapperClass.WrapperMethod()
            # obj_Target.stock_volume_q(updatedVolume)
            pass 

    #마지막 업데이트 시각 갱신
    def update_last_updated(self):
        s_NowTime=str(datetime.now())

        for obj_Target in self.__mdict_MstObject.values():
            obj_Target.updated_time(s_NowTime)


    #다른 스레드에서 이거 하나만 호출해도 된다.
    def update_all(self):
        self.update_current_stock_price()
        self.update_current_stock_quantity()
        self.update_total_stock_trade_volume()
        self.update_last_updated()

