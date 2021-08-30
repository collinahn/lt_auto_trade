# TradeLogic에서 큐에 푸시해주는 주문들을 빼서 1초단위로 최대 4개씩 보내는 클래스.
# 기존 KiwoomMain의 로직에서 인스턴스 변수를 유저info로 초기화해줘야했고 다른 기능이므로 다른 클래스에 있는게 맞을 듯 해서 따로 빼왔다.

# 2021.08.24. created by taeyoung

import time
from LoggerLT import Logger
from SharedMem import SharedMem
from utilsLT import QueueLT
from datetime import datetime
from KiwoomMain import KiwoomMain
import constantsLT as const


class SendRequest2Api:
    
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

            self.lst_usr_info = args
            self.cls_SM = SharedMem()
            self.cls_KW = KiwoomMain()

            self.log.INFO("SendRequest2Api init")

    
    #queue에서 정보를 받아 실제 정보요청/매수/매도요청을 진행하는 함수 (종목코드, 계좌정보, 매수/매도 수량)
    #함수 이름 변경 Get_Queue_BuySell -> Send_Request 2021.08.23
    def Send_Request(self, queue4Request) -> int:
        #현재 처리중인 항목
        dict_Target = queue4Request.getHead()

        #매수매도에 필요한 정보 입력
        n_stockID = dict_Target["StockID"]
        n_accountnumber = self.lst_usr_info[-1] if "," in self.lst_usr_info[-1] else self.lst_usr_info[:8]
        

        if dict_Target["Buy"] == -1 and dict_Target["Sell"] == -1:
            self.log.DEBUG("요청 보내기 직전")
            nRet = self.cls_KW.Get_Basic_Stock_Info(str(n_stockID))
            self.log.DEBUG("요청 보낸 직후")
            self.log.INFO("Requesting Stock info ", n_stockID)
            return 1
        #매수매도 진행
        elif dict_Target["Buy"] > 0 and dict_Target["Sell"] == 0:
            n_quantity = dict_Target["Buy"]
            self.cls_KW.Stock_Buy_Marketprice( n_stockID , n_accountnumber, n_quantity)
            queue4Request.pullQueue()
            self.log.INFO("Bought", n_stockID , n_accountnumber, n_quantity)
            return 1

        elif dict_Target["Buy"] == 0 and dict_Target["Sell"] > 0:
            n_quantity = dict_Target["Sell"]
            self.cls_KW.Stock_Sell_Marketprice( n_stockID, n_accountnumber, n_quantity)
            queue4Request.pullQueue()
            self.log.INFO("Sold", n_stockID , n_accountnumber, n_quantity)
            return 1

        # 뭔가 했으면 1 리턴, 안했으면 0리턴(호출 카운트 세기 위함)
        return 0


    # 이 함수가 RunThread에서 호출된다
    def Send_Request_Throttle(self):
        q_RequestFmLogic = QueueLT(const.REQUEST_QUEUE_SIZE, "Queue4Request2Api")
        n_ApiCallCnt = 0
        t_ThrottleTime = datetime.now().timestamp()

        while True:
            #큐가 비어있다면 휴식
            if q_RequestFmLogic.isEmpty() == True:
                time.sleep(1)
                continue
        
            n_ApiCallCnt += self.Send_Request(q_RequestFmLogic)

            #api 요청 횟수가 과도하다면 api를 통한 요청이 씹히므로 충분히 쉰다.
            #timestamp를 호출하는데 드는 비용을 생각하면 1초 미만의 시간을 주는 것이 맞지만 일단 1초 줌
            if n_ApiCallCnt == const.API_CALL_LIMIT_PER_SEC:
                t_Now = datetime.now().timestamp()
                if t_Now - t_ThrottleTime < 1:
                    self.log.WARNING("THROTTLING API CALL !! SLEEPING 1 SEC")
                    time.sleep(1)
                n_ApiCallCnt = 0
                t_ThrottleTime = datetime.now().timestamp()

