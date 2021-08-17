#-*- encoding: utf-8 -*-

# m: 클래스 멤버 변수
# i : 인스턴스 변수

## wriiten by: Jiuk Jang 
# 2021-08-08 로그인 및 로그인 관련 정보, 주식기본정보요청, 체결정보요청(미완) 관련 함수 만듦 
# 2021-08-09 체결정보요청 완성, 매수/매도 함수(미완)
# 2021-08-12 로거 추가, import 수정 완료, 매수/매도 함수 update (미완)
# 2021-08-17 함수 이름 수정, 전일거래량상위 가져오는 함수 구현, 시장가 매수 완성

## written by: ChanHyeok Jeon
# 2021-08-14 조건검색식 함수 update(미완)


## 설명: KiwoomAPI 파일에서 api관련 함수들을 다 다루고, KiwoomMain에서 실제 거래와 관련된 함수들을 만들어 다룬다.

import sys
# from LoggerLT import Logger
from KiwoomAPI import KiwoomAPI
from PyQt5.QtWidgets import QApplication
from TR_Code import output_list

class KiwoomMain:
    def __init__(self):
        self.kiwoom = KiwoomAPI()
        self.kiwoom.login()
        # self.log = Logger()
# ----------- #
    ##사용가능한 함수들
    # 내 로그인 정보 불러오기 (로그인 상태, 이름, ID, 계좌 개수, 계좌번호) 8/8일 작성
    def Get_Login_Info(self):
        istr_login_state = self.kiwoom.print_login_connect_state #
        istr__user_name, istr__user_id, istr__account_count, istr__account_list = self.kiwoom.login_info()
        list_login_data =  istr_login_state, istr__user_name, istr__user_id, istr__account_count, istr__account_list.rstrip(';')
        return list_login_data

    # OPT10001: 주식기본정보요청 관련 정보 TR_Code.py에 있음 (종목명, 액면가, 자본금, 시가총액, 영업이익, PER, ROE ) 8/8일 작성
    def Get_Basic_Stock_Info(self, istr_stock_code):
        self.kiwoom.output_list = output_list['OPT10001']
        self.kiwoom.SetInputValue("종목코드", istr_stock_code)
        self.kiwoom.CommRqData("OPT10001", "OPT10001", 0, "0101")

        return self.kiwoom.rq_data['OPT10001']['Data'][0]

    # OPT10003: 체결정보요청 관련 정보 TR_Code.py에 있음 (현재가, 체결강도) 8/8일 작성// 8/9일 수정 완료
    def Chegyul_Info(self, istr_stock_code):
        self.kiwoom.output_list = output_list['OPT10003']
        self.kiwoom.SetInputValue("종목코드", istr_stock_code)
        self.kiwoom.CommRqData("OPT10003", "OPT10003", 0, "0101")
    
        return self.kiwoom.rq_data['OPT10003']['Data'][0]

    # OPT10030: 당일거래량상위요청 8/17 시작 (미완)
    def Today_Volume_Top(self, str_market_choice, str_sort_volume, str_credential, str_trade_volume ):
        self.kiwoom.output_list = output_list['OPT10030']

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
        if True:
            pass
        
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
        


    # OPT10031: 전일거래량상위요청 8/17 완료
    def Yesterday_Volume_Top(self, str_market_choice, str_volume_choice, str_ranking):
        self.kiwoom.output_list = output_list['OPT10031']

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

        return self.kiwoom.rq_data['OPT10031']['Data']

    # 시장가 매수 (확인) 8/12 수정 // 8/17 수정완료
    def Stock_Buy_Marketprice(self, istr_stock_code, istr_account_number, in_quantity):
        self.kiwoom.SendOrder("시장가매수", "0101", istr_account_number, 1, istr_stock_code, in_quantity, 0, "03", "")
        # self.log.INFO("시장가매수: " + self.kiwoom.SendOrder("시장가매수", "0101", istr_account_number, 1, istr_stock_code, in_quantity, 0, "03", ""))
        return self.kiwoom.mlist_chejan_data


    # 시장가 매도 8/12 시작 // 8/18 수정 완료 (확인 x)
    def Stock_Sell_Marketprice(self, istr_stock_code, istr_account_number, in_quantity):
        self.kiwoom.SendOrder("시장가매도", "0101", istr_account_number, 2, istr_stock_code, in_quantity, 0, "03", "")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    api_con = KiwoomMain()
    # 아래는 테스트를 위한 것이니 신경 쓰지 않아도 됨

    # account = api_con.Get_Login_Info()
    # log.INFO(api_con.Stock_Buy_Marketprice('035720', account[4], 10))
    # a= api_con.OPT10001('005930')
    # print(a)
    # result5, result7= api_con.OPT10003('035720')
    # print(result5, result7)
    account = api_con.Get_Login_Info()
    # print(type(account[4]))

    # r = api_con.Stock_Buy_Marketprice('035720', account[4], 10)
    # print(r)
    # s = api_con.Stock_Buy_Marketprice('005930', account[4], 10)
    # print(s)
    # api_con.Stock_Sell_Marketprice('035720', account[4], 10)
    s = api_con.Yesterday_Volume_Top("코스피", "거래량", 100)
    print(s)
    # print(account)