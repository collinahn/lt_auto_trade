# 로그를 설정하고 생성하는 클래스(싱글턴)
# 로그를 기록할 사안들은 이 인스턴스로 기록한다
# 모듈 파일명, 함수명, 등의 정보를 포함하여 로그를 출력한다.
# 함수명 등의 디버그 정보는 Python3.8 이상에서 동작한다.

# 사용법
# 로그를 레벨별로 세분화한다.
"""
DEBUG   상세한 정보가 필요할 때, 보통 문제 분석, 디버깅할 때 사용
INFO    동작이 절차에 따라서 진행되고 있는지 관찰 할 때
WARNING 어떤 문제가 조만간 발생할 조짐이 있을 때. 예) 디스크 용량이 부족 할 때
ERROR   프로그램에 문제가 발생해서 기능의 일부가 동작하지 않을 때
CRITICAL    심각한 문제가 발생해서 도저히 시스템이 정상적으로 동작할 수 없을 때

출처: https://wikidocs.net/17747
"""

# 사용예
'''
from LoggerLT import Logger

#인스턴스 가져옴
log = Logger()

#로그 기록(로그 레벨에 따라 파일 및 콘솔 출력)
log.DEBUG("msg")
'''

# 2021.08.08. created by taeyoung


import os
import logging
import logging.handlers
from . import constantsLT as const

class Logger:

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            #폴더가 없는 경우
            if os.path.exists(const.LOG_FOLDER_PATH) == False:
                os.mkdir(const.LOG_FOLDER_PATH)
            #파일이 없는 경우
            if os.path.exists(const.LOG_FILE_PATH) == False:
                f = open(const.LOG_FILE_PATH, 'w', encoding='UTF-8')
                f.close()

        return cls._instance

  
    def __init__(self) :
        cls = type(self)
        if not hasattr(cls, "_init"):
            cls._init = True

            cls.__logger = logging.getLogger('LoggerLT')
            cls.__logger.setLevel(logging.DEBUG)

            cls.formatter = logging.Formatter('%(asctime)s [%(filename)-20s:%(funcName)-21s:%(lineno)-5s] [%(levelname)s] >> %(message)s')
            # cls.fileHandler = logging.FileHandler(const.LOG_FILE_PATH)
            cls.fileHandler = logging.handlers.RotatingFileHandler(const.LOG_FILE_PATH, maxBytes=const.MAX_BYTES, backupCount=const.BACKUP_CNT, encoding='UTF-8')
            cls.streamHandler = logging.StreamHandler()
            cls.fileHandler.setFormatter(cls.formatter)
            cls.streamHandler.setFormatter(cls.formatter)

            cls.__logger.addHandler(cls.fileHandler)
            cls.__logger.addHandler(cls.streamHandler)

            #콘솔엔 전부 출력하고 파일엔 info 이상부터 기록
            cls.fileHandler.setLevel(logging.INFO)
            cls.streamHandler.setLevel(logging.DEBUG)
            
            cls.__logger.info("Logger init", stacklevel=const.STACK_LV)
  

    @classmethod
    def DEBUG(cls, *message):
        ret = ''.join(str(word) + ' ' for word in message)
        cls.__logger.debug(ret, stacklevel=const.STACK_LV)

    @classmethod
    def INFO(cls, *message):
        if (len(message) == 1 and "object" in str(message[0])) \
            or (len(message) == 3 and "object" in str(message[2])): # 생성자 추적
            stacklv = const.STACK_LV_OBJ
        else:
            stacklv = const.STACK_LV

        ret = ''.join(str(word) + ' ' for word in message)
        cls.__logger.info(ret, stacklevel=stacklv)

    @classmethod
    def WARNING(cls, *message):
        ret = ''.join(str(word) + ' ' for word in message)
        cls.__logger.warning(ret, stacklevel=const.STACK_LV)

    @classmethod
    def ERROR(cls, *message):
        ret = ''.join(str(word) + ' ' for word in message)
        cls.__logger.error(ret, stacklevel=const.STACK_LV)

    @classmethod
    def CRITICAL(cls, *message):
        ret = ''.join(str(word) + ' ' for word in message)
        cls.__logger.critical(ret, stacklevel=const.STACK_LV)

    #logLv 10(debug) 20 30 40 50(critical)
    @classmethod
    def set_log_lv(cls, logLv: int):
        if logLv in {10, 20, 30, 40, 50}:
            cls.fileHandler.setLevel(logLv)

    @staticmethod
    def getInstance():
        return Logger()

if __name__ == "__main__":
    log = Logger()

    sMsg = "LogMessage"

    log.CRITICAL(sMsg, 1)
    log.ERROR(sMsg, 2)
    log.WARNING(sMsg, 3)
    log.INFO(sMsg, 4)
    log.DEBUG(sMsg, 5)