#
# 주식매매 db 처리를 위한 클래스 및 sql문을 처리하는 메소드 관리 파일
# 싱글턴으로 동작한다.
# 나중에 mariaDB나 mySQL로 scale up 해서 이 파일만 교체해도 될듯
#
# 2021.08.04 created by taeyoung
# 2021.08.23 modified by taeyoung sharedMem 모듈과 상호 import 하고 있어서 오류나던 문제 초기화시 SharedMem인스턴스를 넣어 초기화하도록 변경
# 

import sqlite3
from datetime import datetime
import constantsLT as const
from LoggerLT import Logger

class GetPutDB(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls.log = Logger()
        cls.log.INFO(cls._instance)
        return cls._instance

    def __init__(self, *args):
        cls = type(self)
        if not hasattr(cls, "_init"):
            cls._init = True
            # if문 내부에서 초기화 진행
            self.__db_path = const.DB_SHARED_PATH

            for arg in args:
                if "SharedMem" in str(type(arg)):
                    self.__shared_mem = arg

            self.log.INFO("GetPutDB init")

    #메인 메모리 요소들을 DB에 저장
    #만약 한 번에 한 주씩 업데이트 하지 않고 보유한 인스턴스들에 대한 DB업데이트를 한 번에 한다면?
    #deprecated
    def update_property(self, nStockID: int) -> bool:
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
            self.log.ERROR("Exception Occured,", e)
            return False
        return True

    #공유메모리에 존재하는 데이터들을 한 번에 업데이트한다.
    #2021.08.08 추가, 아직 테스트 못함
    def update_properties(self) -> bool:
        list_Info4Execute = self.__shared_mem.get_property_info4sql()

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
            
            self.log.INFO("Updated", len(list_Info4Execute), "Fields")
        except Exception as e:
            self.log.ERROR("Exception Occured,", e)
            return False
        return True



    # 사용자가 사용하는 주식인지 여부를 업데이트한다 ("T" 트래킹 중, "N" 트래킹 안함)
    def update_stock_tracking_info(self, nStockID: int, bUsed=True) -> bool:
        c_CurruentState = 'N' if bUsed == False else 'T'
        s_NowTime=str(datetime.now())

        try:
            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            query = """UPDATE tStockProperties SET \
                `stockUsed`=?, \
                `timeStateChange`=? \
                WHERE `stockID`=?;"""
            curs.execute(query, (c_CurruentState, s_NowTime, nStockID))
            
            con.commit()
            con.close()
        except Exception as e:
            self.log.ERROR("Exception Occured,", e)
            return False
        return True

    #최초 실행시 db 칼럼을 초기화한다.
    def add_property_column(self, nStockID: int) -> bool:
        try:
            obj_Instance = self.__shared_mem.get_instance(nStockID)
            s_Name = obj_Instance.name
            n_Quantity = obj_Instance.quantity
            n_Value = obj_Instance.price
            s_Time = obj_Instance.updated_time

            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            #stockName은 최적화시 빼도된다
            query = """INSERT OR REPLACE INTO \
                        tStockProperties(stockID, stockName, stockCurrentPossess, stockCurrentValue, timeLastUpdate ) 
                        Values(?,?,?,?,?);"""
            curs.execute(query, \
                        (nStockID, 
                        s_Name, 
                        n_Quantity, 
                        n_Value, 
                        s_Time))

            con.commit()
            con.close()
        except Exception as e:
            self.log.ERROR("Exception Occured,", e)
            return False
        return True

    #일봉 데이터(시가, 종가, 최고가, 최저가), 거래량 개별로 db에 저장한다. update 2021.08.15 by taeyoung
    def add_candle_hist(self, nStockID: int, nStockVolume: int, dictDataSet: dict) -> bool:
        s_NowTime=str(datetime.now().strftime("%x"))  # 08/15/21

        try:
            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            query = """INSERT INTO tHistoryCandle Values(?, ?, ?, ?, ?, ?, ?);"""
            curs.execute(query, 
                        (nStockID, 
                        dictDataSet["start"], 
                        dictDataSet["end"], 
                        dictDataSet["highest"],
                        dictDataSet["lowest"], 
                        nStockVolume,
                        s_NowTime))
            
            con.commit()
            con.close()
        except Exception as e:
            self.log.ERROR("Exception Occured,", e)
            return False
        return True

    #일봉 데이터(시가, 종가, 최고가, 최저가), 거래량 한 번에 공유메모리를 참조하여 db에 저장한다. update 2021.08.15 by taeyoung
    def add_candle_hist_all(self) -> bool:
        list_Info4Execute = self.__shared_mem.get_candle_info4sql()
        # s_NowTime=str(datetime.now().strftime("%x")) 위에서 넘어옴

        try:
            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            query = """INSERT INTO tHistoryCandle Values(?, ?, ?, ?, ?, ?, ?);"""
            curs.executemany(query, list_Info4Execute)
            
            con.commit()
            con.close()
        except Exception as e:
            self.log.ERROR("Exception Occured,", e)
            return False
        return True

    # 거래 정보 업데이트
    # tStockProperties가 업데이트 될 때 trigger로 기록되도록 하는 것도 나쁘지 않음
    # nQuantity: + 사자 - 팔자
    def add_transaction_hist(self, nStockID: int, nQuantity: int, nPrice: int) -> bool:
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
            self.log.ERROR("Exception Occured,", e)
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
            self.log.ERROR("Exception Occured,", e)
            return None
        return rows



if __name__ == "__main__":
    from SharedMem import SharedMem
    sm = SharedMem([123, 123, 123])
    db = GetPutDB()
    sm.add(111)
    sm.add(222)
    sm.add(333)
    sm.add(444)
    sm.add(555)

    sm.get_shared_mem()
    sm.get_usr_info()

    sm.get_instance(111).price = 100000
    sm.get_instance(222).price = 120000
    sm.get_instance(333).price = 133000
    sm.get_instance(444).price = 4000
    sm.get_instance(555).price = 50000

    db.update_properties()

    sm.get_instance(555).price = 1000000
    db.update_property(555)