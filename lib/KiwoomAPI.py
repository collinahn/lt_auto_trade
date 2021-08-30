#-*- encoding: utf-8 -*-

# m: 클래스 멤버 변수
# i : 인스턴스 변수

## wriiten by: Jiuk Jang 
# 2021-08-08 키움 로그인, 조회와 실시간 데이터 처리 관련 APi정리 완료
# 2021-08-09 체결정보, 잔고처리, 주문 관련 API (미완)
# 2021-08-12 import 수정 완료, 매수/매도 함수 관련 api update (event_loop자리 이동, E_OnReceiveChejandata 함수 수정, Call_TR함수 살짝 수정) (미완)
# 2021-08-19 미체결정보 관련 함수 구현 완료
# 2021.08.26 updated by taeyoung: shared memory 업데이트 관련 기능 구현

## written by: ChanHyuk Jeon

import sys
import os
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop
from SharedMem import SharedMem
from LoggerLT import Logger
from datetime import datetime

class KiwoomAPI(QAxWidget):
    def __init__(self):
        super().__init__()
        self.log = Logger()
        self.login_event_loop = QEventLoop() #로그인 관련 이벤트 루프
        self.event_loop_CommRqData = QEventLoop()
        self.event_loop_SendOrder = QEventLoop()

        self.cls_SM = SharedMem()
        
        # 초기 작업 
        self.set_kiwoom_api() 
        self.set_event_slot()
        self.mdict_rq_data = {}
        self.mlist_output = []
        self.mlist_chejan_data = {}
        self.dict_not_signed_account = {}

        self.log.INFO("KiwoomAPI init")

    # 레지스트리에 저장된 키움 openAPI 모듈 불러오기
    def set_kiwoom_api(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        
    def set_event_slot(self):
        self.OnReceiveMsg.connect(self.E_OnReceiveMsg)

        # 로그인 버전처리
        self.OnEventConnect.connect(self.E_OnEventConnect)
        
        # 조회와 실시간 데이터 처리
        self.OnReceiveTrData.connect(self.E_OnReceiveTrData) 
        # self.OnReceiveRealData.connect(self.E_OnReceiveRealData)

        # 체결정보 / 잔고정보 처리
        self.OnReceiveChejanData.connect(self.E_OnReceiveChejanData)

    def E_OnReceiveMsg(self, sScrNo, sRQName, sTrCode, sMsg):
        self.log.INFO(sScrNo, sRQName, sTrCode, sMsg)

    # 로그인 성공했는지/실패했는지 여부 
    def E_OnEventConnect(self, err_code):
        if err_code == 0:
            self.log.INFO("Login Success")
        else:
            self.log.INFO("Login Failure", err_code)

        self.login_event_loop.exit()
    
    # 조회와 실시간 데이터 처리
    def E_OnReceiveTrData(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, nDataLength, sErrorCode, sMessage, sSplmMsg):
        # print(sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, nDataLength, sErrorCode, sMessage, sSplmMsg)    

        self.Call_TR(sTrCode, sRQName)
        self.update_shared_mem(sTrCode)

        self.event_loop_CommRqData.exit()    


    def E_OnReceiveRealData(self, sCode, sRealType, sRealData):
        # print(sCode, sRealType, sRealData)
        pass
    
    # 체결정보 / 잔고정보 처리
    def E_OnReceiveChejanData(self, sGubun, nItemCnt, sFidList):
        # sGubun = 0: 주문체결통보, 1:잔고통보, 3:특이신호
        if sGubun == 0: #주문번호, 주문수량, 주문가격,
            self.mlist_chejan_data["체결내용"].update({'종목코드': self.GetChejanData(9203)})
            self.mlist_chejan_data["체결내용"].update({'주문수량': self.GetChejanData(900)})
            self.mlist_chejan_data["체결내용"].update({'주문가격': self.GetChejanData(901)})
            
        elif sGubun == 1:
            self.mlist_chejan_data["잔고통보"] = [self.GetChejanData(9001), self.GetChejanData(930), self.GetChejanData(10)]

        self.event_loop_SendOrder.exit()
        # print(sGubun, nItemCnt, sFidList)

#-----------------#
# sharedmem 업데이트 함수 
    def update_shared_mem(self, sStockID: str) -> bool:
        try:
            n_StockID = int(sStockID)
        except Exception as e:
            self.log.ERROR("Cannot Update SharedMem", e)
            return False

        obj_StockInstance = self.cls_SM.get_instance(n_StockID)
        if obj_StockInstance is None:
            self.log.CRITICAL(n_StockID, "Stock Does Not Exists")
            return False

        #-----------여기서 업데이트------------
        obj_StockInstance.name              = self.mdict_rq_data['OPT10001']['Data'][0]['종목명']       # 종목이름
        obj_StockInstance.price             = self.mdict_rq_data['OPT10001']['Data'][0]['현재가']       # 현재가
        obj_StockInstance.stock_volume_q    = 0        # 하루에 한번 전체 거래량을 업데이트하라는 요청이 있으면

        obj_StockInstance.price_data_before = {
            "start":self.mdict_rq_data['OPT10001']['Data'][0]['시가'],              # 시가, 하루에 한번
            "end":self.mdict_rq_data['OPT10001']['Data'][0]['기준가'],              # 종가, 하루에 한번
            "highest":self.mdict_rq_data['OPT10001']['Data'][0]['고가'],            # 고가, 하루에 한번
            "lowest":self.mdict_rq_data['OPT10001']['Data'][0]['저가']              # 저가, 하루에 한번
        }
        obj_StockInstance.updated_time      = str(datetime.now())
        #===========업데이트 끝=============




    ## OpenAPI 함수 ##
    # 키움증권 로그인 
    def login(self):
        self.dynamicCall("CommConnect()")  # 시그널 함수 호출.
        self.login_event_loop.exec_()

    # 현재 계정 상태 표시    
    def print_login_connect_state(self):
        isLogin = self.dynamicCall("GetConnectState()")

        return 'Log in' if isLogin == 1 else 'Log out'

    # 내 정보 조회 기능 (이름, ID, 계좌개수, 계좌)
    def login_info(self):
        istr__user_name = self.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
        istr__user_id = self.dynamicCall("GetLoginInfo(QString)", "USER_ID")
        istr__account_count = self.dynamicCall("GetLoginInfo(QString)", "ACCOUNT_CNT")
        istr__account_list = self.dynamicCall("GetLoginInfo(Qstring)", "ACCLIST")
        return istr__user_name, istr__user_id, istr__account_count, istr__account_list

    # 조회 요청
    def CommRqData(self, sRQName, sTrCode, nPrevNext, sScreenNo):
        self.log.DEBUG("dynamicCalling CommRqData", sRQName, sTrCode)
        self.dynamicCall('CommRqData(String, String, int, String)', sRQName, sTrCode, nPrevNext, sScreenNo)
        return self.event_loop_CommRqData.exec_()

    # 조회 요청 시 TR의 Input 값을 지정
    def SetInputValue(self, sID, sValue):
        self.dynamicCall('SetInputValue(String, String)', sID, sValue)

    # 조회 수신한 멀티 데이터의 개수 (Max : 900개)
    def GetRepeatCnt(self, sTrCode, sRecordName):
        return self.dynamicCall('GetRepeatCnt(String, String)', sTrCode, sRecordName)

    # 조회 데이터 요청
    def GetCommData(self, strTrCode, strRecordName, nIndex, strItemName):
        idict_any_rq_data = self.dynamicCall('GetCommData(String, String, int, String)', strTrCode, strRecordName, nIndex, strItemName)

        # print(ret)
        return idict_any_rq_data.strip()

    # TR 요청
    def Call_TR(self, strTrCode, sRQName):
        if sRQName == "실시간미체결요청":
            cnt = self.dynamicCall(
                "GetRepeatCnt(QString, QString)", strTrCode, sRQName)

            for i in range(cnt):
                istr_stock_code = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", strTrCode, sRQName, i, "종목코드")
                istr_stock_code = istr_stock_code.strip()

                in_stock_order_number = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", strTrCode, sRQName, i, "주문번호")
                in_stock_order_number = int(in_stock_order_number)

                istr_stock_name = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", strTrCode, sRQName, i, "종목명")
                istr_stock_name = istr_stock_name.strip()

                istr_stock_order_type = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", strTrCode, sRQName, i, "주문구분")
                istr_stock_order_type = istr_stock_order_type.strip().lstrip('+').lstrip('-')

                in_stock_order_price = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", strTrCode, sRQName, i, "주문가격")
                in_stock_order_price = int(in_stock_order_price)

                in_stock_order_quantity = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", strTrCode, sRQName, i, "주문수량")
                in_stock_order_quantity = int(in_stock_order_quantity)

                in_stock_not_signed_quantity = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", strTrCode, sRQName, i, "미체결수량")
                in_stock_not_signed_quantity = int(in_stock_not_signed_quantity)

                in_stock_signed_quantity = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", strTrCode, sRQName, i, "체결량")
                in_stock_signed_quantity = int(in_stock_signed_quantity)

                istr_stock_present_price = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", strTrCode, sRQName, i, "현재가")
                istr_stock_present_price = int(
                    istr_stock_present_price.strip().lstrip('+').lstrip('-'))

                istr_stock_order_status = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", strTrCode, sRQName, i, "주문상태")
                istr_stock_order_status = istr_stock_order_status.strip()

                if not in_stock_order_number in self.dict_not_signed_account:
                    self.dict_not_signed_account[in_stock_order_number] = {}

                self.dict_not_signed_account[in_stock_order_number].update(
                    {'종목코드': istr_stock_code})
                self.dict_not_signed_account[in_stock_order_number].update(
                    {'종목명': istr_stock_name})
                self.dict_not_signed_account[in_stock_order_number].update(
                    {'주문구분': istr_stock_order_type})
                self.dict_not_signed_account[in_stock_order_number].update(
                    {'주문가격': in_stock_order_price})
                self.dict_not_signed_account[in_stock_order_number].update(
                    {'주문수량': in_stock_order_quantity})
                self.dict_not_signed_account[in_stock_order_number].update(
                    {'미체결수량': in_stock_not_signed_quantity})
                self.dict_not_signed_account[in_stock_order_number].update(
                    {'체결량': in_stock_signed_quantity})
                self.dict_not_signed_account[in_stock_order_number].update(
                    {'현재가': istr_stock_present_price})
                self.dict_not_signed_account[in_stock_order_number].update(
                    {'주문상태': istr_stock_order_status})

        else: 
            self.mdict_rq_data[strTrCode] = {}
            self.mdict_rq_data[strTrCode]['Data'] = {}
            
            self.mdict_rq_data[strTrCode]['TrCode'] = strTrCode

            count = self.GetRepeatCnt(strTrCode, sRQName)
            self.mdict_rq_data[strTrCode]['Count'] = count

            if count == 0:
                lst_temp_data_rq = []
                dict_temp_data_rq = {}
                for output in self.mlist_output:
                    any_mdict_rq_data = self.GetCommData(strTrCode, sRQName, 0, output)
                    dict_temp_data_rq[output] = any_mdict_rq_data

                lst_temp_data_rq.append(dict_temp_data_rq)
                
                self.mdict_rq_data[strTrCode]['Data'] = lst_temp_data_rq

            if count >= 1:
                lst_temp_data_rq = []
                for i in range(count):
                    dict_temp_data_rq = {}
                    for output in self.mlist_output:
                        any_mdict_rq_data = self.GetCommData(strTrCode, sRQName, i, output)
                        dict_temp_data_rq[output] = any_mdict_rq_data

                    lst_temp_data_rq.append(dict_temp_data_rq)
                
                self.mdict_rq_data[strTrCode]['Data'] = lst_temp_data_rq
    
    # 체결잔고 데이터 반환
    def GetChejanData(self, nFid):
        return self.dynamicCall('GetChejanData(int)', nFid)
    
    # 주식 주문을 서버로 전송, 에러코드 반환
    def SendOrder(self, sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo):
        self.dynamicCall('SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)', [sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo])
        self.event_loop_SendOrder.exec_()


        
