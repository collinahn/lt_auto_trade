#-*- encoding: utf-8 -*-

# 공유 메모리를 관리하는 클래스
# 생성한 Stock 클래스 인스턴스를 딕셔너리 형태로 보유하고 관리한다. 
# 싱글턴으로 생성됨.

# 2021.08.01 created by taeyoung

# m: 클래스 멤버 변수
# i : 인스턴스 변수

from Stocks import Stock as st

class SharedMem:
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

    #타 스레드에서 주기적으로 호출 1
    def updateCurrentStockValue(self):
        for obj_Target in self.__mdict_MstObject.values():
            # updatedValue = WrapperClass.WrapperMethod()
            # obj_Target.updateCurrentValue(updatedValue)
            pass
        
    #타 스레드에서 주기적으로 호출 2
    def updateCurrentStockQuantity(self):
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

