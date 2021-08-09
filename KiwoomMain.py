#-*- encoding: utf-8 -*-

# m: 클래스 멤버 변수
# i : 인스턴스 변수

## wriiten by: Jiuk Jang 
# 2021-08-08 로그인 및 로그인 관련 정보, 주식기본정보요청, 체결정보요청(미완) 관련 함수 만듦 
# 2021-08-09 체결정보요청 완성, 매수/매도 함수(미완)

## written by: ChanHyuk Jun


## 설명: KiwoomAPI 파일에서 api관련 함수들을 다 다루고, KiwoomMain에서 실제 거래와 관련된 함수들을 만들어 다룬다.

import sys
from KiwoomAPI import KiwoomAPI
from PyQt5.QtWidgets import *
from TR_Code import *

class KiwoomMain:
    def __init__(self):
        self.kiwoom = KiwoomAPI()
        self.kiwoom.login()
# ----------- #
    ##사용가능한 함수들
    # 내 로그인 정보 불러오기 (로그인 상태, 이름, ID, 계좌 개수, 계좌번호) 8/8일 작성
    def Get_Login_Info(self):
        istr_login_state = self.kiwoom.print_login_connect_state #
        istr__user_name, istr__user_id, istr__account_count, istr__account_list = self.kiwoom.login_info()
        list_login_data =  istr_login_state, istr__user_name, istr__user_id, istr__account_count, istr__account_list.rstrip(';')
        return list_login_data

    # OPT10001: 주식기본정보요청 관련 정보 TR_Code.py에 있음 (종목명, 액면가, 자본금, 시가총액, 영업이익, PER, ROE ) 8/8일 작성
    def OPT10001(self, istr_stock_code):
        self.kiwoom.output_list = output_list['OPT10001']
        self.kiwoom.SetInputValue("종목코드", istr_stock_code)
        self.kiwoom.CommRqData("OPT10001", "OPT10001", 0, "0101")

        istr_stock_name = self.kiwoom.rq_data['OPT10001']['Data'][0]['종목명']
        istr_par_value = self.kiwoom.rq_data['OPT10001']['Data'][0]['액면가']
        istr_capital = self.kiwoom.rq_data['OPT10001']['Data'][0]['자본금']
        istr_market_cap = self.kiwoom.rq_data['OPT10001']['Data'][0]['시가총액']
        istr_operating_profit = self.kiwoom.rq_data['OPT10001']['Data'][0]['영업이익']
        istr_PER = self.kiwoom.rq_data['OPT10001']['Data'][0]['대용가PER']
        istr_ROE = self.kiwoom.rq_data['OPT10001']['Data'][0]['ROE']
        istr_volume = self.kiwoom.rq_data['OPT10001']['Data'][0]['거래량']

        list_OPT10001_data = [istr_stock_name.strip(), istr_par_value.strip(), istr_capital.strip(), istr_market_cap.strip(), istr_operating_profit.strip(), istr_PER.strip(), istr_ROE.strip(), istr_volume.strip()]
        return list_OPT10001_data

    # OPT10003: 체결정보요청 관련 정보 TR_Code.py에 있음 (현재가, 체결강도) 8/8일 작성// 8/9일 수정 완료
    def OPT10003(self, istr_stock_code):
        self.kiwoom.output_list = output_list['OPT10003']
        self.kiwoom.SetInputValue("종목코드", istr_stock_code)
        self.kiwoom.CommRqData("OPT10003", "OPT10003", 0, "0101")
        
        istr_current_price = self.kiwoom.rq_data['OPT10003']['Data'][0]['현재가']
        istr_volume_power = self.kiwoom.rq_data['OPT10003']['Data'][0]['체결강도']

        return istr_current_price, istr_volume_power

    def Stock_Buy_Marketprice(self, istr_stock_code, istr_account_number, in_quantity):
        self.kiwoom.SendOrder("시장가매수", "0101", istr_account_number, 1, istr_stock_code, in_quantity, 0, "03", "")

    # def stock_
if __name__ == "__main__":
    app = QApplication(sys.argv)
    api_con = KiwoomMain()
    # 아래는 테스트를 위한 것이니 신경 쓰지 않아도 됨
    a= api_con.OPT10001('005930')
    # print(a)
    result5, result7= api_con.OPT10003('035720')
    # print(result5, result7)
    account = api_con.Get_Login_Info()
    # print(type(account[4]))
    api_con.Stock_Buy_Marketprice('035720', account[4], 10)