#
# 주식매매 db 처리를 위한 클래스 및 sql문을 처리하는 메소드 관리 파일
#
# 2021.08.04 created by taeyoung
#

import sqlite3
import constantsLT as const
import SharedMem as sm

class GetPutDb(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, "_init"):
            cls._init = True
            # if문 내부에서 초기화 진행
            _db_path = const.DB_PATH
            print("Construct of GetPutDb")

    #메인 메모리 요소들을 DB에 저장
    #아직 테이블 및 칼럼 구조를 구상하는 중
    def UpdateStockProperties(self) -> None:
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            curs = conn.cursor()
            query = """UPDATE tStockProperties SET 
                ``=?, 
                ``=?, 
                ``=?, 
                ``=?
                WHERE ``=?"""
            curs.execute(query, ())

            conn.commit()
            conn.close()
        except Exception as e:
            print('GetPutDb::UpdateStockProperties >> exception occured ', e)

    # 추적하고 있는 지 여부를 업데이트한다
    def UpdateStockTrackInfo(self, nTick) -> None:
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            curs = conn.cursor()
            query = """UPDATE tStockProperties SET 
                ``=? 
                WHERE ``=?"""
            curs.execute(query, ())
            
            conn.commit()
            conn.close()
        except Exception as e:
            print('GetPutDb::UpdateStockTrackInfo >>  exception occured ', e)