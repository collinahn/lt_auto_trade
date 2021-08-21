#-*- encoding: utf-8 -*-

# 상수를 한 곳에서 관리하도록 하는 파이썬 파일
# 값은 변경하지 않는다. 
# 변수명은 반드시 대문자와 언더바로 구성한다.
# 사용예)
'''
import constantsLT as const

print(const.EXAMPLE_CONST)
'''

# 2021.08.01 created by taeyoung

#-----------Logger--------

LOG_PATH = './log/log.txt'

STACK_LV = 3

#-----------Logger--------


#------------DB-----------

DB_SHARED_PATH = './db/shared.sqlite3'

#------------DB-----------



#--------SharedMemory--------

STOCK_VALUE_QUEUE_SIZE = 20

# STOCK_TRADING_VOLUME_QUEUE_SIZE = 20

# PRICE_DATA = 100

STOCK_COMMON_SIZE = 64

SM_UPDATE_PERIOD = 60

SECONDS_DAY = 86400

LONG_SLEEP_TIME = 100

#--------SharedMemory--------



#-----------Trade------------

REQUEST_QUEUE_SIZE = 128

LOGIC_OPTION = { "LarryWilliams", "CandleTrade" }

TRADE_OPTION = { "MarketOrder", "PendingOrder", "OffHour" }

MFI_STANDARD = 14

#-----------Trade------------
