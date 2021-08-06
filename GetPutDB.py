#
# 주식매매 db 처리를 위한 클래스 및 sql문을 처리하는 메소드 관리 파일
# 싱글턴으로 동작한다.
# 나중에 mariaDB나 mySQL로 scale up 해서 이 파일만 교체해도 될듯
#
# 2021.08.04 created by taeyoung
# 

# 스레드 세이프?
# --> sqlite3는 스레드세이프 하지만 멀티스레드에 적합하지는 않음(병렬 처리 불가)

import sqlite3
from datetime import datetime
import constantsLT as const
from SharedMem import SharedMem

class GetPutDB(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, "_init"):
            cls._init = True
            # if문 내부에서 초기화 진행
            self.__db_path = const.DB_PATH
            self.__shared_mem = SharedMem()
            print("Construct of GetPutDb")

    #메인 메모리 요소들을 DB에 저장
    #아직 테이블 및 칼럼 구조를 구상하는 중
    #만약 한 번에 한 주씩 업데이트 하지 않고 보유한 인스턴스들에 대한 DB업데이트를 한 번에 한다면?(우선순위 상)
    def update_stock_properties(self, nStockID) -> bool:
        obj_Instance = self.__shared_mem.get_instance(nStockID)
        s_Name = obj_Instance.get_name()
        n_Quantity = obj_Instance.get_quantity()
        n_Value = obj_Instance.get_current_value()
        s_Time = obj_Instance.get_updated_time()

        try:
            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            #stockName은 최적화시 빼도된다
            query = """UPDATE tStockProperties SET 
                `stockName`=?,
                `stockCurrentPossess`=?, 
                `stockCurrentValue`=?, 
                `timeLastUpdate`=?
                WHERE `stockID`=?;"""
            curs.execute(query, (s_Name, n_Quantity, n_Value, s_Time, nStockID))

            con.commit()
            con.close()
        except Exception as e:
            print('GetPutDb::UpdateStockProperties >> exception occured:', e)
            return False
        return True

    # 사용자가 사용하는 주식인지 여부를 업데이트한다 ("T" 트래킹 중, "N" 트래킹 안함)
    def update_stock_tracking_info(self, nStockID: int, bUsed=False) -> bool:
        c_CurruentState = 'N' if bUsed == False else 'T'

        try:
            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            query = """UPDATE tStockProperties SET 
                `stockUsed`=? 
                `timeStateChange`=?,
                WHERE `stockID`=?;"""
            curs.execute(query, (c_CurruentState, nStockID))
            
            con.commit()
            con.close()
        except Exception as e:
            print('GetPutDb::UpdateStockTrackingInfo >> exception occured:', e)
            return False
        return True

    # 거래 정보 업데이트
    # 이 역시 거래가 한번에 여러번 되었다면 한번에 바인딩할 수 있도록 최적화(사실 그럴 경우는 드무니까 우선순위 하)
    # tStockProperties가 업데이트 될 때 trigger로 기록되도록 하는 것도 나쁘지 않음
    # nQuantity: + 사자 - 팔자
    def insert_transaction_hist(self, nStockID: int, nQuantity: int, nPrice: int) -> bool:
        s_NowTime=str(datetime.now())

        try:
            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            query = """INSERT INTO tHistoryTransaction Values(?, ?, ?, ?);"""
            curs.execute(query, (nStockID, nQuantity, nPrice, s_NowTime))
            
            con.commit()
            con.close()
        except Exception as e:
            print('GetPutDb::UpdateTradeInfo >> exception occured:', e)
            return False
        return True