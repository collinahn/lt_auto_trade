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
from sqlite3.dbapi2 import Connection, Cursor
from . import constantsLT as const
from . import utilsLT as utils
from .LoggerLT import Logger

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
                    break

            self.log.INFO("GetPutDB init")

    #메인 메모리 요소들을 DB에 저장
    #만약 한 번에 한 주씩 업데이트 하지 않고 보유한 인스턴스들에 대한 DB업데이트를 한 번에 한다면?
    #deprecated
    def update_property(self, nStockID: int) -> bool:
        con: Connection = None
        obj_Instance    = self.__shared_mem.get_instance(nStockID)
        s_Name: str     = obj_Instance.name
        n_Quantity: int = obj_Instance.quantity
        n_Value: int    = obj_Instance.price
        s_Time: str     = obj_Instance.updated_time

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
            return self.exception_handling(e, con)
        return True

    #공유메모리에 존재하는 데이터들을 한 번에 업데이트한다.
    def update_properties(self) -> bool:
        con: Connection = None
        list_Info4Execute: list = self.__shared_mem.get_property_info4sql()
        if not list_Info4Execute:
            self.log.WARNING("DB Update Not Executed - Might be Temporary Problem")
            return False

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
            return self.exception_handling(e, con)
        return True



    # 사용자가 사용하는 주식인지 여부를 업데이트한다 ("T" 트래킹 중, "N" 트래킹 안함)
    def update_stock_tracking_info(self, nStockID: int, bUsed=True) -> bool:
        con: Connection = None
        c_CurruentState: str    = 'N' if bUsed == False else 'T'
        s_NowTime: str          =str(datetime.now())

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
            return self.exception_handling(e, con)
        return True

    #최초 실행시 db 칼럼을 초기화한다.
    def add_property_column(self, nStockID: int) -> bool:
        con: Connection = None
        try:
            obj_Instance    = self.__shared_mem.get_instance(nStockID)
            s_Name: str     = obj_Instance.name
            n_Quantity: int = obj_Instance.quantity
            n_Value: int    = obj_Instance.price
            s_Time: str     = obj_Instance.updated_time

            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            #stockName은 최적화시 빼도된다
            query = """INSERT OR IGNORE INTO \
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
            return self.exception_handling(e, con)
        return True

    #auto increment 설정되어있는 필드를 초기화
    def init_table_autoincrement(self, con: Connection, curs: Cursor, sTableName: str, nStockID: int):
        query_CheckExists = f"""SELECT EXISTS(SELECT * FROM {sTableName} WHERE rowNo=1)"""
        curs.execute(query_CheckExists)
        ret, = curs.fetchone()
        self.log.INFO(ret)

        if ret == 0:
            query_InitTable = f"""INSERT INTO {sTableName} Values(1, ?, 0, 0, 0, 0, 0, 0)"""
            curs.execute(query_InitTable, (nStockID ,))
            self.log.INFO("Table initiated")

        con.commit()


    #종목 추가될 때 테이블을 하나 생성하고 업데이트 내역을 기록한다.
    def create_tHist_PriceInfo(self, nStockID: int):
        con: Connection = None
        s_StockID = utils.getStringTick(nStockID)
        s_TableName = 'tHist' + s_StockID + 'PriceInfo'

        try:
            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            query = f"""CREATE TABLE IF NOT EXISTS {s_TableName} (
                       stockID INTEGER,
                       startPrice INTEGER NOT NULL,
                       endPrice INTEGER NOT NULL,
                       highestPrice INTEGER NOT NULL,
                       lowestPrice INTEGER NOT NULL,
                       stockVolume INTEGER NOT NULL,
                       dateFrom INTEGER PRIMARY KEY NOT NULL
                       )"""
            curs.execute(query)

            con.commit()
            con.close()
        except Exception as e:
            return self.exception_handling(e, con)
        return True


    #종목 추가될 때 테이블을 하나 생성하고 거래 내역을 기록한다.
    #stockID : 종목코드
    #typeTransaction : "Buy"/"Sell"
    #pricePoint: 가격
    #quantityAt: 수량
    #averagePrice: 보유 수량 평균가
    #totalQuantity: 총 보유 수량
    #dateAt: 성공시간 (milisec 단위)
    def create_tHist_Transaction(self, nStockID: int):
        con: Connection = None
        s_StockID = utils.getStringTick(nStockID)
        s_TableName = 'tHist' + s_StockID + 'Transaction'

        try:
            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            query = f"""CREATE TABLE IF NOT EXISTS {s_TableName} (
                       stockID INTEGER,
                       typeTransaction TEXT NOT NULL,
                       pricePoint INTEGER NOT NULL,
                       quantityAt INTEGER NOT NULL,
                       averagePrice REAL NOT NULL,
                       totalQuantity INTEGER NOT NULL,
                       dateAt TEXT PRIMARY KEY NOT NULL
                       )"""
            curs.execute(query)

            con.commit()
            con.close()
        except Exception as e:
            return self.exception_handling(e, con)
        return True


    #이미 저장된 값인지 확인
    def check_if_exists(self, con: Connection, curs: Cursor, sTableName: str, nDate: int) -> bool:
        query_CheckExists = f"""SELECT EXISTS(SELECT * FROM {sTableName} WHERE dateFrom={nDate})"""
        curs.execute(query_CheckExists)
        ret, = curs.fetchone()

        return ret != 0



    #일봉 데이터(시가, 종가, 최고가, 최저가), 거래량 개별로 db에 저장한다. update 2021.08.15 by taeyoung
    def add_candle_hist(self, nStockID: int, nStockVolume: int, dictDataSet: dict) -> bool:
        con: Connection = None
        # s_NowTime: str = str(datetime.now().strftime("%x"))  # 08/15/21

        s_StockID = utils.getStringTick(nStockID)
        s_TableName = 'tHist' + s_StockID + 'PriceInfo'

        try:
            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()

            if self.check_if_exists(con, curs, s_TableName, dictDataSet["date"]):
                con.close
                return False
            else:
                self.log.INFO("Updated", dictDataSet["date"], "Price Data on", s_TableName)

            query = f"""INSERT INTO {s_TableName} Values(?, ?, ?, ?, ?, ?, ?);"""
            curs.execute(query, 
                        (nStockID, 
                        dictDataSet["start"], 
                        dictDataSet["end"], 
                        dictDataSet["highest"],
                        dictDataSet["lowest"], 
                        nStockVolume,
                        dictDataSet["date"]))

            con.commit()
            con.close()
        except Exception as e:
            return self.exception_handling(e, con)
        return True

    #일봉 데이터(시가, 종가, 최고가, 최저가), 거래량 한 번에 공유메모리를 참조하여 db에 저장한다. update 2021.08.15 by taeyoung
    #deprecated
    def add_candle_hist_all(self) -> bool:
        con: Connection = None
        list_Info4Execute: list = self.__shared_mem.get_candle_info4sql()
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
            return self.exception_handling(e, con)
        return True

    # 거래 정보 업데이트
    # nQuantity: + 사자 - 팔자
    def add_transaction_hist(self, nStockID: int, sType: str, nPrice: int, nQuantity: int, nAvgPrice: int, nTotalQuantity: int) -> bool:
        con: Connection = None
        s_StockID = utils.getStringTick(nStockID)
        s_TableName = 'tHist' + s_StockID + 'Transaction'
        s_NowTime: str = str(datetime.now()) #2021-09-09 03:08:33,620

        try:
            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            query = f"""INSERT INTO {s_TableName} Values(?, ?, ?, ?, ?, ?, ?);"""
            curs.execute(query, (nStockID, nPrice, nQuantity, nAvgPrice, nTotalQuantity, s_NowTime))

            con.commit()
            con.close()
        except Exception as e:
            return self.exception_handling(e, con)
        return True

    # 거래내역 얻어오기
    def get_history_by_id(self, nStockID: int, nNumberFetch: int=10):
        con: Connection = None
        s_StockID = utils.getStringTick(nStockID)
        s_TableName = 'tHist' + s_StockID + 'Transaction'

        try:
            con = sqlite3.connect(self.__db_path)
            con.row_factory = sqlite3.Row
            curs = con.cursor()
            query = f"""SELECT * \
                FROM {s_TableName} \
                WHERE `stockID`=? \
                LIMIT ?"""
            curs.execute(query, (nStockID, nNumberFetch))
            rows = curs.fetchall()

            con.commit()
            con.close()
        except Exception as e:
            return self.exception_handling(e, con)
        return rows

    def exception_handling(self, error, connection, ret=False) -> False:
        self.log.ERROR('Exception Occured,', error)
        if connection is not None:
            connection.close()
        return ret



if __name__ == "__main__":
    from SharedMem import SharedMem
    sm = SharedMem([123, 123, 123])
    db = GetPutDB(sm)
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