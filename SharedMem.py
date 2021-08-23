#-*- encoding: utf-8 -*-

# 공유 메모리를 관리하는 클래스
# 생성한 Stock 클래스 인스턴스를 딕셔너리 형태로 보유하고 관리한다. 
# 싱글턴으로 생성됨.

# 2021.08.01 created by taeyoung
# 2021.08.23 modified by taeyoung GetPutDB 모듈과 상호 import 하고 있어서 오류나던 문제 -> GetPutDb 초기화시 SharedMem인스턴스를 넣어 초기화하도록 변경

# m: 클래스 멤버 변수
# i : 인스턴스 변수

from typing import Dict, List
from datetime import datetime
from Stocks import Stock
from LoggerLT import Logger
from utilsLT import QueueLT
import constantsLT as const
from GetPutDB import GetPutDB


class SharedMem(object):
    __mdict_MstObject = {}   # 보유하고 있는 객체들을 dict형 변수에 저장한다.

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls.log = Logger()
        cls.log.INFO(cls._instance)
        return cls._instance

    def __init__(self, *args, **kwargs):
        cls = type(self)
        #최초 한 번만 초기화를 진행한다, 인자 없이 호출되는 경우 객체만 반환하고 초기화는 하지 않는다. 초기화는 RunThread.__init__에서
        if not hasattr(cls, "_init") and not hasattr(cls, "__il_Account_Info") and args:
            cls._init = True
            # if문 내부에서 초기화 진행
            self.__il_AccountInfo =args  # 최초 SharedMem 인스턴스를 호출할 때 어카운트 정보로 초기화한다.

            self.iq_RequestQueue = QueueLT(const.REQUEST_QUEUE_SIZE, "Queue4Request2Api")  #TradeLogic에서 의사결정을 하면 매도, 매수 주문을 큐에 등록함

            self.cls_DB = GetPutDB(self)

            self.log.INFO("SharedMem init:", self.__il_AccountInfo)

    @staticmethod
    def getInstance():
        return SharedMem()

    def print_shared_mem(self):
        print(self.__mdict_MstObject)

    #유저 정보(계좌 정보)를 넘겨준다
    def get_usr_info(self):
        return self.__il_AccountInfo

    #key 값 = 종목코드
    def add(self, nKey: int) -> None:
        self.__mdict_MstObject[nKey] = Stock(nKey)

        self.log.INFO("New Stock Instance:", nKey)

        self.cls_DB.add_property_column(nKey)
        self.cls_DB.update_stock_tracking_info(nKey)

    def delete(self, nKey: int) -> None:
        try:
            del(self.__mdict_MstObject[nKey])

            self.cls_DB.update_stock_tracking_info(nKey, False)

            self.log.INFO("Stock Deleted:", nKey)
        except KeyError as ke:
            self.log.WARNING("Cannot Delete Stock", nKey, "KeyError:", ke)

    #종목을 보유 중인지 확인한다
    def check_possess(self, nKey: int) -> bool:
        self.log.DEBUG(self.__mdict_MstObject)
        return nKey in self.__mdict_MstObject

    #인스턴스를 반환한다.
    def get_instance(self, nKey: int) -> object:
        self.log.DEBUG(self.__mdict_MstObject)
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

    def get_shared_mem(self):
        return self.__mdict_MstObject

    #보유중인 종목의 현재값들을 Dict로 반환한다
    def get_current_price_all(self) -> Dict:
        return {key: value.price for key, value in self.__mdict_MstObject.items()}

    #DB에 저장하기 위한 정보들을 리스트 in 튜플형태로 반환한다.
    def get_property_info4sql(self) -> List:
        list_Ret = []
        for key, value in self.__mdict_MstObject.items():
            tuple_Ret = (value.name, \
                        value.quantity, 
                        value.price, 
                        value.updated_time, 
                        key)
            list_Ret.append(tuple_Ret)
        
        return list_Ret

    #DB에 저장하기 위한 정보들을 리스트 in 튜플형태로 반환한다.
    def get_candle_info4sql(self) -> List:
        s_NowTime=str(datetime.now().strftime("%x"))  # 08/15/21
        list_Ret = []

        for key, value in self.__mdict_MstObject.items():
            tuple_Ret = (key, \
                        value.price_data_before["start"], 
                        value.price_data_before["end"], 
                        value.price_data_before["highest"], 
                        value.price_data_before["lowest"], 
                        value.stock_volume_n,
                        s_NowTime)
            list_Ret.append(tuple_Ret)
        
        return list_Ret

    #변수 업데이트: 18시
    #현재시간을 체크해 장이 마감되었는지 확인한다.
    def is_market_closed(self) -> bool:
        return datetime.now().hour > 18

    def init_after_market_closed(self) -> bool:
        for obj_Target in self.__mdict_MstObject.values():
            n_TotalTrade = 0    #WrapperClass.WrapperMethod()
            obj_Target.stock_volume_q = n_TotalTrade

            dict_PriceData = {
                "start":0,      #WrapperClass.WrapperMethod()
                "end":0,        #WrapperClass.WrapperMethod()
                "highest":0,    #WrapperClass.WrapperMethod()
                "lowest":0      #WrapperClass.WrapperMethod()
            }
            obj_Target.price_data_before = dict_PriceData # 업데이트
            obj_Target.price_data_queue = obj_Target.price_data_before #큐에 저장


    #타 스레드에서 최초에 값을 채워넣고 장마감이후 하루에 한 번 timer로 호출
    def update_trade_volume(self):
        for obj_Target in self.__mdict_MstObject.values():
            # updatedVolume = WrapperClass.WrapperMethod()
            # obj_Target.stock_volume_q = updatedVolume
            pass 
        self.log.INFO("Shared Memory Updated: Total Trade Volume(should be presented once a day)")


    #타 스레드에서 주기적으로 호출 1
    def update_current_stock_price(self):
        for obj_Target in self.__mdict_MstObject.values():
            # updatedPrice = WrapperClass.WrapperMethod()
            # obj_Target.price = updatedPrice
            pass
        self.log.INFO("Shared Memory Updated: Price")

    #평균 매수단가를 업데이트한다. 2
    def update_average_price_bought(self):
        for obj_Target in self.__mdict_MstObject.values():
            # updatedPrice = WrapperClass.WrapperMethod()
            # obj_Target.price_bought = updatedPrice
            pass
        self.log.INFO("Shared Memory Updated: Average Price Bought")
        
    #타 스레드에서 주기적으로 호출 3
    # 거래량의 경우 신뢰도를 위해 api쪽에서 받아온 데이터와 자체적으로 갖고있는 데이터를 비교 후 업데이트해야한다.
    def update_current_stock_quantity(self):
        for obj_Target in self.__mdict_MstObject.values():
            # updatedQuantity = WrapperClass.WrapperMethod()   #매수 : + / 매도 : -
            # obj_Target.quantity = updatedQuantity
            pass
        self.log.INFO("Shared Memory Updated: Quantity")

    #마지막 업데이트 시각 갱신 4
    def update_last_updated(self):
        s_NowTime=str(datetime.now())

        for obj_Target in self.__mdict_MstObject.values():
            obj_Target.updated_time = s_NowTime

        self.log.INFO("Shared Memory Updated: Updated Time")

    #다른 스레드에서 이거 하나만 호출해도 된다.
    def update_all(self):
        self.update_current_stock_price()
        self.update_average_price_bought()
        self.update_current_stock_quantity()
        self.update_last_updated()
        
            



if __name__ == "__main__":
    list_r = [101,1010,1010100]
    # _sm1 = SharedMem()
    # _sm2 = SharedMem()
    # _sm3 = SharedMem()
    sm = SharedMem(list_r)
    sm.add(100011)
    sm.add(100111)
    sm.add(101111)
    sm.add(111111)
    sm.print_shared_mem()

    sm.delete(111111)
    sm.print_shared_mem()

    sm.get_usr_info()

    samsung = sm.get_instance(100011)
    samsung.name = "Samsung"
    samsung.quantity = 5
    samsung.quantity = -3
    samsung.updated_time = str(datetime.now())
    samsung.logic_option ="LarryWilliams"
    samsung.stock_volume_q = 100_000_000_000
    
    lg = sm.get_instance(100111)
    lg.name = "LG"
    lg.quantity = 50
    lg.updated_time = str(datetime.now())
    lg.logic_option ="LarryWilliams"
    lg.stock_volume_q = 50_000_000_000

    hyundai = sm.get_instance(101111)
    hyundai.name = "Hyundai"
    hyundai.quantity = 100
    hyundai.updated_time = str(datetime.now())
    hyundai.logic_option ="LarryWilliams"
    hyundai.stock_volume_q = 23_000_000_000

    print("do i have Stock 111111? >>", sm.check_possess(111111))
    print("how many do i have? >>", sm.get_current_possess())
    print("what do i have? >>", sm.get_current_ticks())
    print("how are they valued? >>", sm.get_current_price_all())
    print("property data for sql ? >>", sm.get_property_info4sql())
    print("candle data for sql ? >>", sm.get_candle_info4sql())



