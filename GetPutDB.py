#
# 주식매매 db 처리를 위한 클래스 및 sql문을 처리하는 메소드 관리 파일
# 싱글턴으로 동작한다.
# 나중에 mariaDB나 mySQL로 scale up 해서 이 파일만 교체해도 될듯
#
# 2021.08.04 created by taeyoung
# 

import sqlite3
from datetime import datetime
import constantsLT as const
from SharedMem import SharedMem
from LoggerLT import Logger

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
            self.log = Logger()
            self.log.INFO(str(self._instance))

    #메인 메모리 요소들을 DB에 저장
    #만약 한 번에 한 주씩 업데이트 하지 않고 보유한 인스턴스들에 대한 DB업데이트를 한 번에 한다면?
    #deprecated
    def update_property(self, nStockID) -> bool:
        obj_Instance = self.__shared_mem.get_instance(nStockID)
        s_Name = obj_Instance.name
        n_Quantity = obj_Instance.quantity
        n_Value = obj_Instance.price
        s_Time = obj_Instance.updated_time

        try:
            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            #stockName은 최적화시 빼도된다
            query = """UPDATE tStockProperties SET \
                `stockName`=?, \
                `stockCurrentPossess`=?, \
                `stockCurrentValue`=?, \
                `timeLastUpdate`=? \
                WHERE `stockID`=?;"""
            curs.execute(query, (s_Name, n_Quantity, n_Value, s_Time, nStockID))

            con.commit()
            con.close()
        except Exception as e:
            self.log.ERROR("Exception Occured, " + str(e))
            return False
        return True

    #공유메모리에 존재하는 데이터들을 한 번에 업데이트한다.
    #2021.08.08 추가, 아직 테스트 못함
    def update_properties(self) -> bool:
        list_Info4Execute = self.__shared_mem.get_info4sql()

        try:
            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            #stockName은 최적화시 빼도된다
            query = """UPDATE tStockProperties SET \
                `stockName`=?, \
                `stockCurrentPossess`=?, \
                `stockCurrentValue`=?, \
                `timeLastUpdate`=? \
                WHERE `stockID`=?;"""
            curs.executemany(query, list_Info4Execute)

            con.commit()
            con.close()
            
            self.log.INFO("Updated " + str(len(list_Info4Execute)) + " Fields")
        except Exception as e:
            self.log.ERROR("Exception Occured, " + str(e))
            return False
        return True



    # 사용자가 사용하는 주식인지 여부를 업데이트한다 ("T" 트래킹 중, "N" 트래킹 안함)
    def update_stock_tracking_info(self, nStockID: int, bUsed=False) -> bool:
        c_CurruentState = 'N' if bUsed == False else 'T'

        try:
            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            query = """UPDATE tStockProperties SET \
                `stockUsed`=? \
                `timeStateChange`=?, \
                WHERE `stockID`=?;"""
            curs.execute(query, (c_CurruentState, nStockID))
            
            con.commit()
            con.close()
        except Exception as e:
            self.log.ERROR("Exception Occured, " + str(e))
            return False
        return True

    # 거래 정보 업데이트
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
            self.log.ERROR("Exception Occured, " + str(e))
            return False
        return True

    # 거래내역 얻어오기
    def get_history_by_id(self, nStockID: int, nNumberFetch: int):
        try:
            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            query = """SELECT * \
                FROM `tHistoryTransaction` \
                WHERE `stockID`=? \
                LIMIT ?"""
            curs.execute(query, (nStockID, nNumberFetch))
            rows = curs.fetchall()
            
            con.commit()
            con.close()
        except Exception as e:
            self.log.ERROR("Exception Occured, " + str(e))
            return None
        return rows