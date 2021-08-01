#-*- encoding: utf-8 -*-

# 공유 메모리를 관리하는 클래스
# 생성한 Stock 클래스 인스턴스를 딕셔너리 형태로 보유하고 관리한다. 
# 싱글턴으로 생성됨.

# 2021.08.01 created by taeyoung

# m: 클래스 멤버 변수
# i : 인스턴스 변수

from typing import Dict, List
from Stocks import Stock as st

class SharedMem(object):
    __mdict_MstObject = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, "_init"):
            cls._init = True
            # if문 내부에서 초기화 진행
            print("Construct of SharedMem")
    
    def __printSharedMem(self):
        print(self.__mdict_MstObject)

    #key 값 = 종목코드
    def addSharedMem(self, nKey: int) -> None:
        self.__mdict_MstObject[nKey] = st(nKey)

    #db에 반영하는 함수 또한 호출되어야 한다.
    def delSharedMem(self, nKey: int) -> None:
        del(self.__mdict_MstObject[nKey])
        del(st(nKey))

    #종목을 보유 중인지 확인한다
    def checkPossess(self, nKey: int) -> bool:
        return nKey in self.__mdict_MstObject

    #보유중인 종목의 수를 int로 반환한다.
    def getCurrentPossess(self) -> int:
        return len(self.__mdict_MstObject)

    #보유중인 종목의 코드들을 dict_keys 형태로 반환한다. 
    def getCurrentTicks(self):
        return self.__mdict_MstObject.keys()

    #보유중인 종목의 현재값들을 Dict로 반환한다
    def getCurrentValueAll(self) -> Dict:
        dict_StockValues = {}
        for key, value in self.__mdict_MstObject.items():
            dict_StockValues[key] = value.getCurrentValue()
        return dict_StockValues

    #타 스레드에서 주기적으로 호출 1
    def updateCurrentStockValue(self):
        for obj_Target in self.__mdict_MstObject.values():
            # updatedValue = WrapperClass.WrapperMethod()
            # obj_Target.updateCurrentValue(updatedValue)
            pass
        
    #타 스레드에서 주기적으로 호출 2
    def updateCurrentStockVolume(self):
        for obj_Target in self.__mdict_MstObject.values():
            # updatedValue = WrapperClass.WrapperMethod()   #매수 : + / 매도 : -
            # obj_Target.updateCurrentVolume(updatedValue)
            pass
    

# __selfExe__
a = SharedMem()
a.addSharedMem(1159, st(1159))
a.addSharedMem(1160, st(1160))
a.addSharedMem(1159, st(1159))

a.printSharedMem()

