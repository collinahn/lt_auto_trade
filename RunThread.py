#-*- encoding: utf-8 -*-

# auto trade를 구성하는 메인 로직 
# 스레드를 사용하여 일을 처리한다.
# 1. api 함수 사용하여 주기적으로 데이터 공유메모리에 업데이트
# 2. 매매알고리즘 의사결정 스레드
# 2. 공유메모리에 올라간 데이터들 주기적으로 DB 업데이트
# 3. 주고받은 json 문서들 MongoDB 업데이트
# 4. 서버 healthcheck(?)

# 2021.08.02 created by 태영


from KiwoomAPI import KiwoomAPI
import sys
from PyQt5.QtWidgets import QApplication
from KiwoomMain import KiwoomMain
from SharedMem import SharedMem
from LoggerLT import Logger
import threading

class RunThread(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, "_init"):
            cls._init = True
            # if문 내부에서 초기화 진행

            #키움 초기화 및 로그인 처리
            qapp = QApplication(sys.argv)
            kapi = KiwoomMain()
            
            #유저 정보를 받아와서 공유메모리 초기화
            lst_usr_info = kapi.Get_Login_Info()
            self.__shared_mem = SharedMem(lst_usr_info)

            self.log = Logger()
            self.log.INFO(self._instance)
