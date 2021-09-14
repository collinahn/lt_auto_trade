#-*- encoding: utf-8 -*-

# m: 클래스 멤버 변수
# i : 인스턴스 변수

## wriiten by: Jiuk Jang 
# 2021-08-08 로그인 및 로그인 관련 정보, 주식기본정보요청, 체결정보요청(미완) 관련 함수 만듦 
# 2021-08-09 체결정보요청 완성, 매수/매도 함수(미완)
# 2021-08-12 로거 추가, import 수정 완료, 매수/매도 함수 update (미완)
# 2021-08-17 함수 이름 수정, 전일거래량상위 가져오는 함수 구현, 시장가 매수 완성
# 2021-08-18 당인거래량상위 함수 완성, 로거 부분적 추가, 계좌수익률요청 함수, 매수,매도 (지정, 정정, 취소) 구현 (미완)
# 2021-08-19 매수/매도 정정, 취소 구현 완료 (확인 o), 미체결정보 함수 완성

## written by: ChanHyeok Jeon
# 2021-08-14 조건검색식 함수 update(미완)
# 2021-08-22 Queue에 있는 정보를 바탕으로 실제로 API에 매수/매도 요청을 보내는 함수 작성
# 2021-08-23 Queue함수 간략하게 작성(보완 필요)

# 2021.09.05 일부 함수 리팩토링 및 주식 일봉차트조회요청함수 추가 by taeyoung


## 설명: KiwoomAPI 파일에서 api관련 함수들을 다 다루고, KiwoomMain에서 실제 거래와 관련된 함수들을 만들어 다룬다.

import sys
from datetime import datetime
from .LoggerLT import Logger
from .KiwoomAPI import KiwoomAPI
from .SharedMem import SharedMem
from PyQt5.QtWidgets import QApplication
from .TR_Code import output_list
from . import utilsLT as utils
from . import constantsLT as const
from .GetPutDB import GetPutDB

class KiwoomMain:
    def __new__(cls, *args):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls.log = Logger()
        cls.log.INFO(cls._instance)
        return cls._instance

    def __init__(self, *args):
        cls = type(self)
        if not hasattr(cls, "_init"):
            cls._init = True


            self.kiwoom = KiwoomAPI()
            self.cls_SM = SharedMem()
            self.cls_DB = GetPutDB(self.cls_SM)

            self.log.INFO("KiwoomMain init")



# ----------- #
    ##사용가능한 함수들
    # 내 로그인 정보 불러오기 (로그인 상태, 이름, ID, 계좌 개수, 계좌번호) 8.8일 작성
    def Get_Login_Info(self):
        s_login_state = self.kiwoom.print_login_connect_state() #
        __s_user_name, __s_user_id, __s_account_count, __s_account_list = self.kiwoom.login_info()
        
        return  s_login_state, __s_user_name, __s_user_id, __s_account_count, __s_account_list.rstrip(';')
        

    # OPT10085: 계좌수익률요청 
    def Get_Account_Info(self, sAccountNo):
        return self._Callback_Info('OPT10085', "계좌번호", sAccountNo)

    # OPT10001: 주식기본정보요청 관련 정보 TR_Code.py에 있음 (종목명, 액면가, 자본금, 시가총액, 영업이익, PER, ROE ) 8/8일 작성
    def Get_Basic_Stock_Info(self, sStockID, bMarketClosed=False):
        return self._Callback_Info('OPT10001', "종목코드", sStockID, bMarketClosed)

    # OPT10003: 체결정보요청 관련 정보 TR_Code.py에 있음 (현재가, 체결강도) 8.8일 작성// 8.9일 수정 완료
    def Chegyul_Info(self, sStockID):
        return self._Callback_Info('OPT10003', "종목코드", sStockID)

    def _Callback_Info(self, sTrCode, sFieldName, sFieldInfo, bMarketClosed=False):
        self.kiwoom.mlist_output = output_list[sTrCode]
        self.kiwoom.SetInputValue(sFieldName, sFieldInfo)
        nRet = self.kiwoom.CommRqData(sTrCode, sTrCode, 0, '0101')
        if nRet != 0:
            self.log.CRITICAL("Failed to Request Data From Api", sFieldInfo, sTrCode)
            return []

        if sFieldName == "종목코드":
            self._Update_SM(sFieldInfo, sTrCode, bMarketClosed)
            # self.log.DEBUG(self.kiwoom.mdict_rq_data[sTrCode]['Data'][0])

        return self.kiwoom.mdict_rq_data[sTrCode]['Data']


    def _Update_SM(self, sStockID: str, sTrCode: str, bIsMarketClosed: bool=False) -> bool:
        n_StockID = utils.getIntLT(sStockID)

        obj_StockInstance = self.cls_SM.get_instance(n_StockID)
        if obj_StockInstance is None:
            self.log.CRITICAL(n_StockID, "Stock Does Not Exists")
            return False

        if bIsMarketClosed:
            # 하루에 한 번 업데이트
            obj_StockInstance.stock_volume    = utils.getIntLT(self.kiwoom.mdict_rq_data[sTrCode]['Data'][0]['거래량'])        # 하루에 한번 전체 거래량을 업데이트하라는 요청이 있으면
            obj_StockInstance.price_data_before = {
                "start":    utils.getIntLT(self.kiwoom.mdict_rq_data[sTrCode]['Data'][0]['시가']),              # 시가, 하루에 한번
                "end":      utils.getIntLT(self.kiwoom.mdict_rq_data[sTrCode]['Data'][0]['현재가']),              # 종가, 하루에 한번
                "highest":  utils.getIntLT(self.kiwoom.mdict_rq_data[sTrCode]['Data'][0]['고가']),            # 고가, 하루에 한번
                "lowest":   utils.getIntLT(self.kiwoom.mdict_rq_data[sTrCode]['Data'][0]['저가']),              # 저가, 하루에 한번
                "date":     utils.getIntLT(utils.getTodayYmdLT()),
            }

            #이미 저장되어있어 db저장 안될경우 False 반환
            if self.cls_DB.add_candle_hist( n_StockID, \
                                            obj_StockInstance.stock_volume, 
                                            obj_StockInstance.price_data_before ) == True:
                self.log.INFO("Updated AfterClose Data")

        else: 
            # 상시 업데이트
            obj_StockInstance.name              = self.kiwoom.mdict_rq_data[sTrCode]['Data'][0]['종목명']       # 종목이름
            obj_StockInstance.price             = utils.getIntLT(self.kiwoom.mdict_rq_data[sTrCode]['Data'][0]['현재가'])       # 현재가
            obj_StockInstance.volume_rt         = utils.getIntLT(self.kiwoom.mdict_rq_data[sTrCode]['Data'][0]['거래량'])
            obj_StockInstance.updated_time      = str(datetime.now())

        return True

    #14영업일 이전부터 현재까지의 기록을 수정주가로 받아온다.
    def Get_Init_Info(self, sStockID) -> bool:
        return self._Callback_Init_Info('OPT10081', sStockID)


    def _Callback_Init_Info(self, sTrCode, sStockID) -> bool:
        self.kiwoom.mlist_output = output_list[sTrCode]
        self.kiwoom.SetInputValue("종목코드", sStockID)
        self.kiwoom.SetInputValue("기준일자", utils.getTodayYmdLT())
        self.kiwoom.SetInputValue("수정주가구분", "1")
        nRet = self.kiwoom.CommRqData(sTrCode, sTrCode, 0, '0101')
        if nRet != 0:
            self.log.CRITICAL("Failed to Request Init Data", sStockID, sTrCode)
            return False

        return self._Init_SM(sStockID, sTrCode)


    def _Init_SM(self, sStockID: str, sTrCode: str) -> bool:
        n_StockID = utils.getIntLT(sStockID)

        if len(self.kiwoom.mdict_rq_data[sTrCode]['Data']) < const.INIT_DATA_AMOUNT:
            self.log.CRITICAL("Fail to initialize, Deleting", sStockID, "From SharedMem")
            self.cls_SM.delete(n_StockID)
            return False

        obj_StockInstance = self.cls_SM.get_instance(n_StockID)
        if obj_StockInstance is None:
            self.log.CRITICAL(sStockID, "Stock Does Not Exists")
            return False

        lst_init_data = self.kiwoom.mdict_rq_data[sTrCode]['Data'][0:const.STOCK_COMMON_SIZE][::-1] #14일치 정보만 가져온다
        # self.log.INFO("reversed", lst_init_data)

        #가져온 14일치 정보로 초기화 해줌
        for dct_DayInfo in lst_init_data:
            obj_StockInstance.stock_volume = utils.getIntLT(dct_DayInfo['거래량'])
            obj_StockInstance.price_data_before = {
            "start":    utils.getIntLT(dct_DayInfo['시가']),
            "end":      utils.getIntLT(dct_DayInfo['현재가']),
            "highest":  utils.getIntLT(dct_DayInfo['고가']),     
            "lowest":   utils.getIntLT(dct_DayInfo['저가']),
            "date":     utils.getIntLT(dct_DayInfo['일자'])
            }
        
            self.cls_DB.add_candle_hist(n_StockID, \
                                        obj_StockInstance.stock_volume, 
                                        obj_StockInstance.price_data_before)

        self.log.INFO("Updated", len(lst_init_data), "Days of Data")

        return True

    # OPT10030: 당일거래량상위요청 8.18 완성
    def Today_Volume_Top(self, str_market_choice, str_sort_volume, str_credential, str_trade_volume):
        self.kiwoom.mlist_output = output_list['OPT10030']

        # 시장구분 = 전체(0), 코스피(1), 코스닥(101)
        if str_market_choice == "전체":
            self.kiwoom.SetInputValue("시장구분", "0")
        elif str_market_choice == "코스피":
            self.kiwoom.SetInputValue("시장구분", "1")
        elif str_market_choice == "코스닥":
            self.kiwoom.SetInputValue("시장구분", "101")

        # 정렬구분 = 거래량(1), 거래회전율(2), 거래대금(3)
        if str_sort_volume == "거래량":
            self.kiwoom.SetInputValue("정렬구분", "0")
        elif str_sort_volume == "거래대금":
            self.kiwoom.SetInputValue("정렬구분", "3")

        # 종목포함 = 관리종목 포함(0), 관리종목 미포함(1), 증100만보기(6), 증50만보기(12)
        self.kiwoom.SetInputValue("관리종목포함", "0") 
        
        # 신용구분 =  0:전체조회, 1:신용융자A군, 2:신용융자B군, 3:신용융자C군, 4:신용융자D군
        if str_credential == "전체조회":
            self.kiwoom.SetInputValue("신용구분", "0")
        elif str_credential == "A":
            self.kiwoom.SetInputValue("신용구분", "1")
        elif str_credential == "B":
            self.kiwoom.SetInputValue("신용구분", "2")
        elif str_credential == "C":
            self.kiwoom.SetInputValue("신용구분", "3")
        elif str_credential == "D":
            self.kiwoom.SetInputValue("신용구분", "4")

        # 거래량구분 = 0:전체조회, 100:10만주이상, 200:20만주이상, 300:30만주이상, 500:500만주이상, 1000:백만주이상
        if str_trade_volume == "전체조회":
            self.kiwoom.SetInputValue("신용구분", "0")
        else: 
            self.kiwoom.SetInputValue("신용구분", str_trade_volume)

        # 가격구분 =  0:전체조회, 1:1천원미만, 2:1천원이상, 3:1천원~2천원, 4:2천원~5천원, 5:5천원이상, 6:5천원~1만원, 10:1만원미만, 7:1만원이상, 8:5만원이상, 9:10만원이상
        self.kiwoom.SetInputValue("가격구분", 0)

        # 거래대금구분 = 0:전체조회, 1:1천만원이상, 3:3천만원이상, 4:5천만원이상, 10:1억원이상, 30:3억원이상, 50:5억원이상, 100:10억원이상, 300:30억원이상, 500:50억원이상, 1000:100억원이상, 3000:300억원이상, 5000:500억원이상
        self.kiwoom.SetInputValue("거래대금구분", 0)

        # 장운영구분 = 0:전체조회, 1:장중, 2:장전시간외, 3:장후시간외
        self.kiwoom.SetInputValue("장운영구분", 0)

        self.kiwoom.CommRqData("OPT10030", "OPT10030", 0, "0101")

        return self.kiwoom.mdict_rq_data['OPT10030']['Data']
        
    # OPT10031: 전일거래량상위요청 8/17 완료
    def Yesterday_Volume_Top(self, str_market_choice, str_volume_choice, str_ranking):
        self.kiwoom.mlist_output = output_list['OPT10031']

        # 시장구분 = 전체(0), 코스피(1), 코스닥(101)
        if str_market_choice == "전체":
            self.kiwoom.SetInputValue("시장구분", "0")
        elif str_market_choice == "코스피":
            self.kiwoom.SetInputValue("시장구분", "1")
        elif str_market_choice == "코스닥":
            self.kiwoom.SetInputValue("시장구분", "101")
        
        # 조회구분 = 전일거래량 상위100종목 (1), 전일거래대금 상위100종목 (2)
        if str_volume_choice == "거래량":
            self.kiwoom.SetInputValue("조회구분", "1")
        elif str_volume_choice == "거래대금":
            self.kiwoom.SetInputValue("조회구분", "2")
        
        self.kiwoom.SetInputValue("순위시작", "1")

        # 순위 끝 = 1 ~ 100 값 중에 조회를 원하는 순위 끝값
        self.kiwoom.SetInputValue("순위끝", str_ranking)

        self.kiwoom.CommRqData("OPT10031", "OPT10031", 0, "0101")

        self.log.INFO("전일거래량상위요청: ", self.kiwoom.mdict_rq_data['OPT10031']['Data'])
        return self.kiwoom.mdict_rq_data['OPT10031']['Data']


    # OPT10075: 미체결요청 완성 (8.19)
    def Not_Signed_Account(self, istr_account_number):
        self.kiwoom.SetInputValue("계좌번호", istr_account_number)
        self.kiwoom.SetInputValue("전체종목구분", "0")
        self.kiwoom.SetInputValue("매매구분", "0")
        self.kiwoom.SetInputValue("체결구분", "1")
        self.kiwoom.CommRqData("실시간미체결요청", "opt10075", 0, "0101")
        
        self.log.INFO("미체결정보: ", self.kiwoom.dict_not_signed_account)
        return self.kiwoom.dict_not_signed_account
#----------#

    #매매 체결 이후 공유메모리 및 db업데이트 
    #신뢰성을 위해 체결잔고내역 콜백데이터를 넣는다
    def _Update_Quantity(self, sStockID: str, nQuantity: int) -> None:
        nStockID = utils.getIntLT(sStockID)
        sType = "Buy" if nQuantity > 0 else "Sell"

        nUpdatedPrice = utils.getIntLT(self.kiwoom.mlist_chejan_data['체결내용']['주문가격'])
        nUpdatedQuantity = utils.getIntLT(self.kiwoom.mlist_chejan_data['체결내용']['주문수량'])
        
        if nQuantity < 0: nUpdatedQuantity = -nUpdatedQuantity #매도면 매도 처리

        obj_Instance = self.cls_SM.get_instance(nStockID)
        tup_Average = (nUpdatedPrice, nUpdatedQuantity, obj_Instance.quantity)
        obj_Instance.price_bought = tup_Average
        obj_Instance.quantity = nUpdatedQuantity

        self.cls_DB.add_transaction_hist(nStockID, \
                                         sType, 
                                         nUpdatedPrice, 
                                         nUpdatedQuantity, 
                                         obj_Instance.price_bought, 
                                         obj_Instance.quantity)



    # 시장가 매수 (확인) 8.12 수정 // 8.17 수정완료
    def Stock_Buy_Marketprice(self, istr_stock_code, istr_account_number, in_quantity):
        nRet = self.kiwoom.SendOrder("시장가매수", "0101", istr_account_number, 1, istr_stock_code, in_quantity, 0, "03", "")
        self.log.INFO("시장가매수: ", self.kiwoom.mlist_chejan_data)

        # 매수가 성공하면 보유수량 업데이트 
        if nRet == 0:
            self._Update_Quantity(istr_stock_code, in_quantity)

        return self.kiwoom.mlist_chejan_data

    # 지정가 매수 8.18 완료 
    def Stock_Buy_Certainprice(self, istr_stock_code, istr_account_number, in_quantity, in_price):
        self.kiwoom.SendOrder("지정가매수", "0101", istr_account_number, 1, istr_stock_code, in_quantity, in_price, "00", "")

        self.log.INFO("지정가매수: " , self.kiwoom.mlist_chejan_data)
        return self.kiwoom.mlist_chejan_data

    # 시장가 매도 8.12 시작 // 8.18 수정 완료 
    def Stock_Sell_Marketprice(self, istr_stock_code, istr_account_number, in_quantity):
        nRet = self.kiwoom.SendOrder("시장가매도", "0101", istr_account_number, 2, istr_stock_code, in_quantity, 0, "03", "")

        # 매도가 성공하면 보유수량 업데이트 
        if nRet == 0:
            self._Update_Quantity(istr_stock_code, -(in_quantity))

    # 지정가 매도 8.18 완료 
    def Stock_Sell_Certainprice(self, istr_stock_code, istr_account_number, in_quantity, in_price):
        self.kiwoom.SendOrder("지정가매도", "0101", istr_account_number, 2, istr_stock_code, in_quantity, in_price, "00", "")
     
    # 매수 취소 8.18 미완 // 8.19 완성 
    def Stock_Buy_Cancel(self, istr_stock_code, istr_account_number, in_quantity, istr_order_code):
        self.kiwoom.SendOrder("매수취소", "0101", istr_account_number, 3, istr_stock_code, in_quantity, 0, "00", istr_order_code)

    # 매수 정정 8.18 미완 // 8.19 완성
    def Stock_Buy_Update(self, istr_stock_code, istr_account_number, in_quantity, in_price, istr_order_code):
        self.kiwoom.SendOrder("매수정정", "0101", istr_account_number, 5, istr_stock_code, in_quantity, in_price, "00", istr_order_code)

    # 매도 취소 8.18 미완 // 8.19 완성
    def Stock_Sell_Cancel(self, istr_stock_code, istr_account_number, in_quantity, istr_order_code):
        self.kiwoom.SendOrder("매도취소", "0101", istr_account_number, 4, istr_stock_code, in_quantity, 0, "00", istr_order_code)

    # 매도 정정 8.18 미완 // 8.19 완성
    def Stock_Sell_Update(self, istr_stock_code, istr_account_number, in_quantity, in_price, istr_order_code):
        self.kiwoom.SendOrder("매도정정", "0101", istr_account_number, 6, istr_stock_code, in_quantity, in_price, "00", istr_order_code)




if __name__ == "__main__":
    # app = QApplication(sys.argv)
    # api_con = KiwoomMain()
    # 아래는 테스트를 위한 것이니 신경 쓰지 않아도 됨

    # lst_account = api_con.Get_Login_Info()
    # print(lst_account)
    # accountNo = lst_account[-1] if "," not in lst_account[-1] else lst_account[:8]
    # print("accountNo", accountNo)
    # api_con.Get_Account_Info(accountNo)

    # print(api_con.Get_Basic_Stock_Info('005930'))


    class Test(object):
        def __init__(self):

            self.q = QApplication(sys.argv)

            self.cls_KW = KiwoomMain()
            self.log = Logger()

            self.Loginfo = self.cls_KW.Get_Login_Info()

            self.cls_SM = SharedMem(self.Loginfo)
            from GetPutDB import GetPutDB
            self.cls_DB = GetPutDB(self.cls_SM)

            self.cls_SM.add(5930)

            from utilsLT import QueueLT
            self.iq_Threads = QueueLT(16, "Threads2Request")

            self.log.INFO("init")

        @property
        def account_info(self) -> list:
            return self.Loginfo

        def check_success(self):
            return self.cls_SM.get_instance(5930).name

        def simple_test(self):
            print(self.samsung())

        # @property
        def samsung(self):
            return self.cls_KW.Get_Basic_Stock_Info('005930')

        def callback(self):
            import time
            from threading import Thread, active_count
            lst_threads = [Thread(target=self.simple_test) for _ in range(3)]

            # Thread(target=self.dummy, daemon=True).run()
            for work in lst_threads:
                self.log.DEBUG("active thread count: ", active_count())
                self.log.DEBUG(work)
                work.run()

            self.log.DEBUG("active thread count: ", active_count())

        def call_concurrent(self):
            import time
            from concurrent import futures
            pool = futures.ThreadPoolExecutor(max_workers=16)

            for _ in range(10):
                self.iq_Threads.pushQueue(pool.submit(self.simple_test))


            print(self.iq_Threads.getList())
            for p in futures.as_completed(self.iq_Threads.getList()[6:]):
                p.result()

        def new_process(self, q, cKW, cSM):
            import os
            import sys
            pid = os.getpid()
            self.log.INFO("pid:", pid)

            cKW.Get_Basic_Stock_Info('005930')
            print(cSM.get_instance(5930).name)


        def call_process(self):
            from multiprocessing import Process
            lst_process = [
                Process(
                    target=self.new_process,
                    args=(
                        self.q,
                        self.cls_KW,
                        self.cls_SM,
                    ),
                )
                for _ in range(5)
            ]

            for work in lst_process:
                work.start()

            for work in lst_process:
                work.join()

        def dummy(self):
            import time
            while(True):
                print("check executed while callback")
                time.sleep(10)

    from threading import Thread

    test = Test()

    # test.simple_test()

    th_obj = Thread(target=test.call_concurrent)
    # test.call_process()



    th_obj.start()
    print(test.check_success())
    th_obj.join()

    print(test.check_success())


    # log.INFO(api_con.Stock_Buy_Marketprice('035720', account[4], 10))
    # a= api_con.OPT10001('005930')
    # print(a)
    # result5, result7= api_con.OPT10003('035720')
    # print(result5, result7)
    # account = api_con.Get_Login_Info()
    # print(account[4])

    # r = api_con.Stock_Buy_Marketprice('035720', account[4], 10)
    # print(r)
    # s = api_con.Stock_Buy_Marketprice('005930', account[4], 10)
    # print(s)
    # api_con.Stock_Sell_Marketprice('035720', account[4], 10)
    # s = api_con.Yesterday_Volume_Top("코스피", "거래량", 100)
    # print(s)
    # print(account)
    # api_con.Get_Account_Info('8005204311')
    # api_con.Stock_Buy_Marketprice('035720', '8005204311', 10)
    # api_con.Stock_Sell_Marketprice('035720', '8005204311', 3)
    # api_con.Stock_Buy_Certainprice('035720', '8005204311', 1, 140000)
    # api_con.Not_Signed_Account('8005204311')
    # api_con.Stock_Buy_Update('035720', '8005204311', 1, 141000, '179567')
    # api_con.Stock_Buy_Cancel('035720', '8005204311', 1, '192233')

