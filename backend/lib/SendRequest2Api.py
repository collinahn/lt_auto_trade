# TradeLogic에서 큐에 푸시해주는 주문들을 빼서 1초단위로 최대 4개씩 보내는 클래스.
# 기존 KiwoomMain의 로직에서 인스턴스 변수를 유저info로 초기화해줘야했고 다른 기능이므로 다른 클래스에 있는게 맞을 듯 해서 따로 빼왔다.

# 2021.08.24. created by taeyoung


import sys
import time
import pythoncom
from .LoggerLT import Logger
from .SharedMem import SharedMem
from .utilsLT import QueueLT
from .KiwoomMain import KiwoomMain
from threading import Thread
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, QThread
from . import utilsLT as utils
from . import constantsLT as const



class SendRequest2Api(object):
    
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls.log = Logger()

        cls.log.INFO(cls._instance)
        return cls._instance

    def __init__(self, *args, **kwargs):
        cls = type(self)
        if not hasattr(cls, "_init"):

            cls._init = True
            super().__init__()

            # #키움 초기화 및 로그인 처리
            self.qapp = QApplication(sys.argv)

            self.iq_Threads = QueueLT(const.REQUEST_QUEUE_SIZE, "Threads4Request")

            self.log.INFO("SendRequest2Api Qthread init")

    def __del__(self):
        pythoncom.CoUninitialize()

    
    #queue에서 정보를 받아 실제 정보요청/매수/매도요청을 진행하는 함수 (종목코드, 계좌정보, 매수/매도 수량)
    #함수 이름 변경 Get_Queue_BuySell -> Send_Request 2021.08.23
    def Send_Request(self, queue4Request) -> int:
        #현재 처리중인 항목
        dict_Target = queue4Request.getHead()

        #필요한 정보 입력
        n_StockID = dict_Target["StockID"]
        s_StockID =  utils.getStringTick(n_StockID) #6자리로 고정
        s_AccountNo = self.lst_usr_info[-1] if "," not in self.lst_usr_info[-1] else self.lst_usr_info[:8]
        # self.log.DEBUG(self.lst_usr_info)
        # self.log.DEBUG("nStockID:", n_StockID, "sStockID:", s_StockID, "account:", s_AccountNo)
        try:
            if dict_Target["Buy"] == const.UPDATE_INFO:
                bInitAfterMarketClosed = None if dict_Target["Sell"] == const.UPDATE_BEFORE_CLOSED else True
                # self.iq_Threads.pushQueue(Thread(target=self.cls_KW.Get_Basic_Stock_Info, args=(s_StockID, bInitAfterMarketClosed, )))
                # self.iq_Threads.getTail().run()
                self.cls_KW.Get_Basic_Stock_Info(s_StockID, bInitAfterMarketClosed)
                self.log.INFO("Got Current Stock Info ", s_StockID)

            elif dict_Target["Buy"] == const.INITIALIZE_INFO:
                # self.iq_Threads.pushQueue(Thread(target=self.cls_KW.Get_Init_Info, args=(s_StockID, )))
                # self.iq_Threads.getTail().run()
                self.cls_KW.Get_Init_Info(s_StockID)
                self.log.INFO("Got Initial Stock Info ", s_StockID)

            elif dict_Target["Buy"] > 0 and dict_Target["Sell"] == 0:
                n_quantity = dict_Target["Buy"]
                self.cls_KW.Stock_Buy_Marketprice( s_StockID , s_AccountNo, n_quantity )
                self.log.INFO("Buy", s_StockID , s_AccountNo, n_quantity)

            elif dict_Target["Buy"] == 0 and dict_Target["Sell"] > 0:
                n_quantity = dict_Target["Sell"]
                self.cls_KW.Stock_Sell_Marketprice( s_StockID, s_AccountNo, n_quantity )
                self.log.INFO("Sell", s_StockID , s_AccountNo, n_quantity)



            else:
                # 뭔가 했으면 1 리턴, 안했으면 0리턴(호출 카운트 세기 위함)
                return 0
        except Exception as e:
            self.log.CRITICAL(e)
        finally:
            queue4Request.pullQueue()
            return 1

    # 이 함수가 RunThread에서 호출된다
    def Send_Request_Throttle(self):
        #타 스레드에서 호출할 때 com객체 초기화 필요
        nRet = pythoncom.CoInitialize()
        self.log.CRITICAL("Coinit:", nRet)
        self.cls_KW = KiwoomMain()
        self.lst_usr_info = self.cls_KW.Get_Login_Info()
        self.cls_SM = SharedMem(self.lst_usr_info)

        q_RequestFmLogic = QueueLT(const.REQUEST_QUEUE_SIZE, "Queue4Request2Api")
        n_ApiCallCnt = 0

        while True:
            #큐가 비어있다면 휴식하거나 스레드 자원 회수
            if q_RequestFmLogic.isEmpty():
                if not self.iq_Threads.isEmpty(): #and not self.iq_Threads.getHead().is_alive():
                    # self.iq_Threads.getHead().join(timeout=0.5)
                    self.iq_Threads.pullQueue()
                    self.log.INFO("Request Thread joined")

                else:
                    time.sleep(1)

                n_ApiCallCnt = 0
                continue
        
            n_ApiCallCnt += self.Send_Request(q_RequestFmLogic)

            #api 요청 횟수가 과도하다면 api를 통한 요청이 씹히므로 충분히 쉰다.
            #timestamp를 호출하는데 드는 비용을 생각하면 1초 미만의 시간을 주는 것이 맞지만 일단 1초 줌
            if n_ApiCallCnt == const.API_CALL_LIMIT_PER_SEC:
                if not q_RequestFmLogic.isEmpty():
                    self.log.WARNING("THROTTLING API CALL !! SLEEPING 1 SEC")
                    time.sleep(1)
                n_ApiCallCnt = 0
