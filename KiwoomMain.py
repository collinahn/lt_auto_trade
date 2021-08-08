#-*- encoding: utf-8 -*-

# m: 클래스 멤버 변수
# i : 인스턴스 변수

## wriiten by: Jiuk Jang 2021-08-08
# 로그인 및 로그인 관련 정보, 주식기본정보요청, 체결정보요청(미완) 관련 함수 만듦
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
        list_login_data =  istr_login_state, istr__user_name, istr__user_id, istr__account_count, istr__account_list
        return list_login_data

    # OPT10001: 주식기본정보요청 관련 정보 Config.py에 있음 (종목명, 액면가, 자본금, 시가총액, 영업이익, PER, ROE ) 8/8일 작성
    def OPT10001(self, str_stock_code):
        self.kiwoom.output_list = output_list['OPT10001']

        self.kiwoom.SetInputValue("종목코드", str_stock_code)
        self.kiwoom.CommRqData("OPT10001", "OPT10001", 0, "0101")

        str_stock_name = self.kiwoom.rq_data['OPT10001']['Data'][0]['종목명']
        str_par_value = self.kiwoom.rq_data['OPT10001']['Data'][0]['액면가']
        str_capital = self.kiwoom.rq_data['OPT10001']['Data'][0]['자본금']
        str_market_cap = self.kiwoom.rq_data['OPT10001']['Data'][0]['시가총액']
        str_operating_profit = self.kiwoom.rq_data['OPT10001']['Data'][0]['영업이익']
        str_PER = self.kiwoom.rq_data['OPT10001']['Data'][0]['대용가PER']
        str_ROE = self.kiwoom.rq_data['OPT10001']['Data'][0]['ROE']
        
        list_OPT10001_data = [str_stock_name, str_par_value, str_capital, str_market_cap, str_operating_profit, str_PER, str_ROE]

        return list_OPT10001_data

    # OPT10003: 체결정보요청 관련 정보 Config.py에 있음 (현재가, 체결강도) 8/8일 작성
    def OPT10003(self, str_stock_code):
        self.kiwoom.output_list = output_list['OPT10003']

        self.kiwoom.SetInputValue("종목코드", str_stock_code)
        self.kiwoom.CommRqData("OPT10003", "OPT10003", 0, "0101")
        
        # str_
        return self.kiwoom.rq_data['OPT10003']

if __name__ == "__main__":
    app = QApplication(sys.argv)
    api_con = KiwoomMain()

    # 아래는 테스트를 위한 것이니 신경 쓰지 않아도 됨
    a, b, c, d= api_con.OPT10001('005930')
    print(a, b, c, d)

    result5 = api_con.OPT10003('035720')
    print(result5['Data'][0])