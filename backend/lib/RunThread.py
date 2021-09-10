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


# 메인 스레드가 아니므로 사용 불가
# import signal
# signal.signal(signal.SIGINT, signal.SIG_DFL) # ctrl + c로 종료할 수 있도록

import sys
import time
from threading import Thread, Timer
from datetime import datetime
from .SendRequest2Api import SendRequest2Api
from .SharedMem import SharedMem
from .GetPutDB import GetPutDB
from .TradeLogic import TradeLogic
from .LoggerLT import Logger
from . import constantsLT as const
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, QObject, Qt

class RunThread(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls.log = Logger()

        cls.log.INFO(cls._instance)
        return cls._instance

    def __init__(self, parent=None):
        cls = type(self)
        if not hasattr(cls, "_init"):
            cls._init = True
            # super(self.__class__, self).__init__(parent)
            # if문 내부에서 초기화 진행

            # self.qth_Thread = QThread()
            self.cls_SR = SendRequest2Api()
            # self.cls_SR.moveToThread(self.qth_Thread)
            # # self.cls_SR.finished.connect(self.qth_Thread.quit)
            # self.qth_Thread.started.connect(self.cls_SR.run)
            # # self.qth_Thread.finished.connect(self.qapp.exit)
            # self.qth_Thread.start()

            self.cls_SM = SharedMem()
            self.cls_DB = GetPutDB(self.cls_SM)
            self.cls_TL = TradeLogic()
            
            self.lst_Threads = []

            self.log.INFO("RunThread init")

    #콘솔 창에 종목코드(int)입력하면 디버깅 정보를 출력하게해주는 스레드
    #단순 엔터: 보유종목 출력
    #종목코드 입력: 디버깅정보 조회 후 출력
    def _debug(self):
        while True:
            s_input = input()
            if s_input == '':
                print(self.cls_SM.get_current_possess(), self.cls_SM.get_current_ticks())
                continue

            try:
                int(s_input)
            except ValueError:
                self.log.DEBUG("enter int")
                continue

            obj = self.cls_SM.get_instance(int(s_input))
            if obj is None:
                self.log.DEBUG("ERROR: Non Existing Stock ID")
                self.cls_SM.add(int(s_input))
                continue

            print( \
            f'==============DEBUG_INFO {obj.ticker}====================\n', 
            f'\n', 
            f'\n', 
            f'name:  {obj.name} \n', 
            f'price: {obj.price} \n', 
            f'volume_realtime: {obj.volume_rt} \n', 
            f'logic_option: {obj.logic_option} \n', 
            f'day info: {obj.price_data_before} \n', 
            f'\n', 
            f'volume: {obj.stock_volume} \n', 
            f'price queue: {obj.price_q.getList()}\n', 
            f'volume queue: {obj.stock_volume_q.getList()}\n', 
            f'dayinfo queue: {obj.price_data_q.getList()}\n', 
            f'\n', 
            f'\n', 
            f'pricebought: {obj.price_bought} \n', 
            f'quantity: {obj.quantity} \n', 
            f'\n', 
            f'\n', 
            f'\n', 
            f'\n', 
            f'==============DEBUG_INFO {obj.ticker}====================', 
            )

    # 장마감 이후 18:00에 오늘의 정보로 공유메모리 인스턴스 내부의 정보 업데이트
    # 추후 db 새로운 테이블을 생성해 업데이트 예정 
    def _set_timer_initialize_info(self):
        #최초 실행시 하루 단위 타이머를 실행시키고 반복문을 벗어난다.
        Timer(const.SECONDS_DAY, self.cls_SM.init_after_market_closed()).start()


    #DB 업데이트 후 sharedMem 업데이트 요청 보내는 함수 호출, 60초에 한번
    def update_info(self):
        b_SetTimer = True
        t_LastUpdated = datetime.now()

        while True:
            t_Now = datetime.now()
            if t_Now.timestamp() - t_LastUpdated.timestamp() > const.SM_UPDATE_PERIOD:
                if b_SetTimer and t_Now.hour > 18:
                    self._set_timer_initialize_info()
                    b_SetTimer = False
            
                self.cls_DB.update_properties()
                self.cls_SM.update_request()

                t_LastUpdated = datetime.now()

            time.sleep(1)
            
    #매매의사결정 함수 호출
    def call_price(self):

        self.cls_TL.show_me_the_money()
    
    #의사결정 스레드의 요청대로 api호출하여 주문한다.
    #1초에 최대 5번까지 처리가 가능하다.
    def call_api(self):
        
        self.cls_SR.Send_Request_Throttle()

    #db의 tracking info 참조하여 공유메모리에 올림(실행 후 초기화시 실행)
    def load_db(self):
        pass

    #스레드를 가동한다.
    def run_system(self):
        self.load_db()

        #-----------스레드 등록-----------
        self.lst_Threads.append(Thread(target=self._debug))
        self.lst_Threads.append(Thread(target=self.update_info))
        self.lst_Threads.append(Thread(target=self.call_api))
        self.lst_Threads.append(Thread(target=self.call_price))
        #-----------스레드 등록-----------
        
        self.log.DEBUG("threads: ", self.lst_Threads)

        for work in self.lst_Threads:
            work.setDaemon(False)
            work.start()
            self.log.INFO("thread start: ", work)

        # self.call_api() #QThread

        
        #무한루프를 돌리기 때문에 이 이후로는 실행되지 않는다.
        for work in self.lst_Threads:
            work.join()
            self.log.CRITICAL("Thread Joined !", work)


if __name__ == "__main__":


    rt = RunThread()
    sm = SharedMem()
    sm.add(5930)
    sm.add(5360)
    sm.add(70)
    sm.add(80)
    sm.add(1040)
    sm.add(9415)
    sm.add(35720)
    sm.add(28260)
    sm.add(29460)
    sm.add(28050)

    rt.run_system()