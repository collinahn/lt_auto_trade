#-*- encoding: utf-8 -*-

# auto trade를 구성하는 메인 로직 
# 스레드를 사용하여 일을 처리한다.
# 1. api 함수 사용하여 주기적으로 데이터 공유메모리에 업데이트
# 2. 매매알고리즘 의사결정 스레드
# 2. 공유메모리에 올라간 데이터들 주기적으로 DB 업데이트
# 3. 주고받은 json 문서들 MongoDB 업데이트
# 4. 서버 healthcheck(?)

#파이썬은 GIL정책으로 인해 스레드를 사용하는 효용이 그리 크지 않음..
#효용을 지켜보다가 결과가 좋지 않다 싶으면 추후 multiprocessing으로 리팩토링 예정

# 2021.08.02 created by 태영


import signal
signal.signal(signal.SIGINT, signal.SIG_DFL) # ctrl + c로 종료할 수 있도록

from SendRequest2Api import SendRequest2Api
import sys
import time
from threading import Thread, Timer
import constantsLT as const
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from KiwoomMain import KiwoomMain
from SharedMem import SharedMem
from GetPutDB import GetPutDB
from TradeLogic import TradeLogic
from LoggerLT import Logger
from utilsLT import QueueLT

class RunThread(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls.log = Logger()

        cls.log.INFO(cls._instance)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, "_init"):
            cls._init = True
            # if문 내부에서 초기화 진행

            #키움 초기화 및 로그인 처리
            self.qapp = QApplication(sys.argv)
            self.cls_KM = KiwoomMain()
            
            #유저 정보를 받아와서 공유메모리 초기화
            lst_usr_info = self.cls_KM.Get_Login_Info()
            self.cls_SM = SharedMem(lst_usr_info)
            self.cls_SR = SendRequest2Api(lst_usr_info)

            self.cls_DB = GetPutDB(self.cls_SM)
            self.cls_TL = TradeLogic()
            

            self.log.INFO("RunThread init")

    # 장마감 이후 18:00에 오늘의 정보로 공유메모리 인스턴스 내부의 정보 업데이트
    # 추후 db 새로운 테이블을 생성해 업데이트 예정 
    def initialize_info_timer(self):

        while True:
            #최초 실행시 하루 단위 타이머를 실행시키고 반복문을 벗어난다.
            if datetime.now().hour > 18:
                Timer(const.SECONDS_DAY, self.cls_SM.init_after_market_closed()).start()
                break

            time.sleep(const.LONG_SLEEP_TIME)


    #DB 업데이트 후 sharedMem 업데이트 요청 보내는 함수 호출, 60초에 한번
    def update_info(self):
        queue4Request = QueueLT(const.REQUEST_QUEUE_SIZE, "Queue4Request2Api")
        t_LastUpdated = datetime.now().timestamp()

        self.log.INFO("thread start")

        while True:
            t_Now = datetime.now().timestamp()
            if t_Now - t_LastUpdated > const.SM_UPDATE_PERIOD:
                self.cls_DB.update_properties()
                self.cls_SM.update_request(queue4Request)

                t_LastUpdated = datetime.now().timestamp()
            
            time.sleep(1)
            
    #매매의사결정 함수 호출
    def call_price(self):

        self.log.INFO("thread start")

        self.cls_TL.show_me_the_money()
    
    #의사결정 스레드의 요청대로 api호출하여 주문한다.
    #1초에 최대 4번까지 처리가 가능하다.
    def trade_stocks(self):
        
        self.log.INFO("thread start")
        
        self.cls_SR.Send_Request_Throttle()



    #스레드들을 가동한다.
    def run_thread(self):
        lst_Threads = []

        #-----------스레드 등록-----------
        lst_Threads.append(Thread(target=self.update_info))
        lst_Threads.append(Thread(target=self.call_price))
        lst_Threads.append(Thread(target=self.trade_stocks))
        #-----------스레드 등록-----------
        
        for work in lst_Threads:
            work.setDaemon(False)
            work.start()

        self.initialize_info_timer()
        
        #무한루프 스레드를 돌리기 때문에 이 이후로는 실행되지 않는다.
        for work in lst_Threads:
            work.join()
            self.log.CRITICAL("Thread Joined !", work)


if __name__ == "__main__":
    rt = RunThread()
    # rt.run_thread()