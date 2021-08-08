#-*- encoding: utf-8 -*-

# m: 클래스 멤버 변수
# i : 인스턴스 변수

## wriiten by: Jiuk Jang 
# 2021-08-08 키움 로그인, 조회와 실시간 데이터 처리 관련 APi정리 완료

## written by: ChanHyuk Jun

import sys
import os
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication


class KiwoomAPI(QAxWidget):
    def __init__(self):
        super().__init__()
        self.login_event_loop = QEventLoop() #로그인 관련 이벤트 루프
        
        # 초기 작업
        self.set_kiwoom_api() 
        self.set_event_slot()
        self.rq_data = {}
        self.output_list = []

    # 레지스트리에 저장된 키움 openAPI 모듈 불러오기
    def set_kiwoom_api(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        
    def set_event_slot(self):
        self.OnReceiveMsg.connect(self.E_OnReceiveMsg)

        # 로그인 버전처리
        self.OnEventConnect.connect(self.E_OnEventConnect)
        
        # 조회와 실시간 데이터 처리
        self.OnReceiveTrData.connect(self.E_OnReceiveTrData) 
        self.OnReceiveRealData.connect(self.E_OnReceiveRealData)

    def E_OnReceiveMsg(self, sScrNo, sRQName, sTrCode, sMsg):
        print(sScrNo, sRQName, sTrCode, sMsg)

    # 로그인 성공했는지/실패했는지 여부 
    def E_OnEventConnect(self, err_code):
        if err_code == 0:
            str__login_success = "로그인에 성공했습니다."
            print(str__login_success)
        else:
            str__login_failure = "로그인에 실패했습니다."
            print(str__login_failure)

        self.login_event_loop.exit()
    
    # 조회와 실시간 데이터 처리
    def E_OnReceiveTrData(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, nDataLength, sErrorCode, sMessage, sSplmMsg):
        print(sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, nDataLength, sErrorCode, sMessage, sSplmMsg)    

        self.Call_TR(sTrCode, sRQName)

        self.event_loop_CommRqData.exit()    

    def E_OnReceiveRealData(self, sCode, sRealType, sRealData):
        print(sCode, sRealType, sRealData)

#-----------------# 
    ## OpenAPI 함수 ##
    # 키움증권 로그인 
    def login(self):
        self.dynamicCall("CommConnect()")  # 시그널 함수 호출.
        self.login_event_loop.exec_()

    # 현재 계정 상태 표시    
    def print_login_connect_state(self):
        isLogin = self.dynamicCall("GetConnectState()")
        if isLogin == 1:
            istr__login_state_on = "현재 계정은 로그인 상태입니다."
            # print("\n현재 계정은 로그인 상태입니다.")
            return istr__login_state_on
        else:
            istr__login_state_off = "현재 계정은 로그아웃 상태입니다."
            # print("\n현재 계정은 로그아웃 상태입니다.")
            return istr__login_state_off

    # 내 정보 조회 기능 (이름, ID, 계좌개수, 계좌)
    def login_info(self):
        istr__user_name = self.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
        istr__user_id = self.dynamicCall("GetLoginInfo(QString)", "USER_ID")
        istr__account_count = self.dynamicCall("GetLoginInfo(QString)", "ACCOUNT_CNT")
        istr__account_list = self.dynamicCall("GetLoginInfo(Qstring)", "ACCLIST")
        return istr__user_name, istr__user_id, istr__account_count, istr__account_list

    # 조회 요청
    def CommRqData(self, sRQName, sTrCode, nPrevNext, sScreenNo):
        ret = self.dynamicCall('CommRqData(String, String, int, String)', sRQName, sTrCode, nPrevNext, sScreenNo)
        self.event_loop_CommRqData = QEventLoop()
        self.event_loop_CommRqData.exec_()

    # 조회 요청 시 TR의 Input 값을 지정
    def SetInputValue(self, sID, sValue):
        str_Input_value = self.dynamicCall('SetInputValue(String, String)', sID, sValue)

        # print(str_Input_value)

    # 조회 수신한 멀티 데이터의 개수 (Max : 900개)
    def GetRepeatCnt(self, sTrCode, sRecordName):
        cnt = self.dynamicCall('GetRepeatCnt(String, String)', sTrCode, sRecordName)

        # print(ret)
        return cnt

    # 조회 데이터 요청
    def GetCommData(self, strTrCode, strRecordName, nIndex, strItemName):
        any_rq_data = self.dynamicCall('GetCommData(String, String, int, String)', strTrCode, strRecordName, nIndex, strItemName)

        # print(ret)
        return any_rq_data.strip()

    # TR 요청
    def Call_TR(self, strTrCode, sRQName):
        self.rq_data[strTrCode] = {}
        self.rq_data[strTrCode]['Data'] = {}
        
        self.rq_data[strTrCode]['TrCode'] = strTrCode

        count = self.GetRepeatCnt(strTrCode, sRQName)
        self.rq_data[strTrCode]['Count'] = count

        if count == 0:
            lst_temp_data_rq = []
            dict_temp_data_rq = {}
            for output in self.output_list:
                any_rq_data = self.GetCommData(strTrCode, sRQName, 0, output)
                dict_temp_data_rq[output] = any_rq_data

            lst_temp_data_rq.append(dict_temp_data_rq)
            
            self.rq_data[strTrCode]['Data'] = lst_temp_data_rq

        if count >= 1:
            lst_temp_data_rq = []
            for i in range(count):
                dict_temp_data_rq = {}
                for output in self.output_list:
                    any_rq_data = self.GetCommData(strTrCode, sRQName, i, output)
                    dict_temp_data_rq[output] = any_rq_data

                lst_temp_data_rq.append(dict_temp_data_rq)
            
            self.rq_data[strTrCode]['Data'] = lst_temp_data_rq





