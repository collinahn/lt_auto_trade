# 자료구조 및 유용한 함수들 공유해서 쓰기 위해 만든 파일들.

# 2021.08.12 created by taeyoung (Stocks.py에 있던 큐 자료구조 이관)
# 2021.08.20 modified by taeyoung 큐 이름을 같은 것으로 생성하면 동일한 인스턴스가 반환되도록 생성자 수정
# 2021.08.25 modified by taeyoung 큐에 푸시하고 테일포인트를 옮길 때 thread-safe하도록 수정

# 데이터 집어넣을 땐: push
# 데이터 가져올 땐: getHead & pull
# ** push/pull을 할 때 자체적으로 큐가 꽉 차있는지/비어있는지 확인한다.
# 이름이 같으면 크기를 다르게 설정하여 생성하여도 기존 생성된 인스턴스가 반환된다.

from LoggerLT import Logger
import threading
from datetime import datetime

class QueueLT:
    __mset_Instance = set()
    __mdict_MstInstance = {}

    def __new__(cls, nSize: int, sName: str):
        if hasattr(cls, "_instance") and sName in QueueLT.__mset_Instance:
            cls._instance = QueueLT.__mdict_MstInstance[sName]
        else:
            cls._instance = super().__new__(cls)
            QueueLT.__mdict_MstInstance[sName] = cls._instance
            cls.log = Logger()

        cls.log.INFO("Name:", sName, cls._instance)
        return cls._instance

    def __init__(self, nSize: int, sName: str):
        if sName not in QueueLT.__mset_Instance: 
            self.__is_Name = sName #디버깅 정보
            self.__iq_Queue = [None] * nSize
            self.__in_QueueSize = nSize
            self.__in_HeadPointIdx = 0
            self.__in_TailPointIdx = 0

            QueueLT.__mset_Instance.add(sName)

            self.lock = threading.Lock() # 서로 다른 스레드에서 푸시할 때 데이터의 경쟁상태 방지

            self.log.INFO(sName, "Queue init, size:", nSize)

        else: 
            self.log.WARNING(sName, "Queue Called Again")
        
    #큐에 데이터를 집어넣고 테일포인트를 옮긴다.
    def pushQueue(self, value: int or dict) -> bool:
        n_NextTailPointIdx = (self.__in_TailPointIdx +1) % self.__in_QueueSize

        if n_NextTailPointIdx is self.__in_HeadPointIdx:            # 테일+1 == 헤드(버퍼 full)
            self.log.WARNING(self.__is_Name, "Queue Full") 
            return False

        self.lock.acquire()
        self.__iq_Queue[self.__in_TailPointIdx] = value   # 테일포인터가 가르키는 자리에 value삽입
        self.__in_TailPointIdx = n_NextTailPointIdx             # 다음 자리로 테일포인터 이동.
        self.lock.release()

        return True
        
    #큐에서 데이터를 빼고(함수 앞에서 getHead로) 헤드포인트를 옮긴다.
    #받는 곳은 한 곳이라 스레드 락을 걸어줄 필욘 없음
    def pullQueue(self) -> bool:
        n_NextHeadPointIdx = (self.__in_HeadPointIdx+1) % self.__in_QueueSize

        if self.__in_HeadPointIdx == self.__in_TailPointIdx:        # 테일 == 헤드 (buffer empty)
            return False
        self.__in_HeadPointIdx = n_NextHeadPointIdx
        return True

    # pull oldest push
    def getHead(self) -> int or dict:
        return self.__iq_Queue[self.__in_HeadPointIdx]
        
    # pull latest push
    def getTail(self) -> int:
        #  테일포인트는 미리 데이터가 삽입될 곳을 가리키고 있음
        if self.__in_TailPointIdx == 0:
            return self.__iq_Queue[self.__in_QueueSize - 1]
        return self.__iq_Queue[self.__in_TailPointIdx -1] 

    def getHeadPoint(self) -> int:
        return self.__in_HeadPointIdx

    def getTailPoint(self) -> int:
        return self.__in_TailPointIdx

    def getQueue(self) -> list:
        return self.__iq_Queue

    #사용하기 쉽도록 정렬하여 리스트로 전달한다
    def getList(self) -> list:
        if self.__in_TailPointIdx == 0: #비어있거나 한바퀴 돈 것
            return self.__iq_Queue

        queue = self.__iq_Queue[:] #깊은 복사
        back = queue[:self.__in_TailPointIdx]
        front = queue[self.__in_TailPointIdx:]
        return front + back #넣은 순서대로 있는 리스트가 반환


    def isEmpty(self) -> bool:
        return self.__in_HeadPointIdx == self.__in_TailPointIdx

    def isFull(self) -> bool:
        n_NextTailPointIdx = (self.__in_TailPointIdx +1) % self.__in_QueueSize

        return n_NextTailPointIdx == self.__in_HeadPointIdx             # 테일+1 == 헤드 => 버퍼 full


def getIntLT(sData: str, sDebugData=None):
    try:
        return int(sData.strip().replace('+','').replace('-', ''))
    except ValueError as ve:
        Logger.CRITICAL("Cannot Convert Data to Int", sData, sDebugData, ve)
        return -1

def getStringTick(nStockID: int):
    if nStockID < 0 or nStockID > 999999:
        Logger.CRITICAL("Wrong StockID", nStockID)
        return '000000'

    return str(nStockID).zfill(6)

def getTodayYmdLT():
    return datetime.now().strftime("%Y%m%d")


if __name__ == "__main__":
    qu = QueueLT(10, "Example")

    bRet = qu.pullQueue()
    print("result of pulling an empty Queue:", bRet)
    qu.pushQueue(1)
    print(qu.getQueue())
    qu.pushQueue(2)
    qu.pushQueue(3)
    qu.pushQueue(4)
    qu.pushQueue(5)
    qu.pushQueue(6)
    qu.pushQueue(7)
    qu.pushQueue(8)
    qu.pushQueue(9)
    qu.pushQueue(10)
    print("is it full? >>", qu.isFull())
    qu.pullQueue()
    qu.pushQueue(11)
    qu.pullQueue()
    qu.pushQueue(12)
    qu.pullQueue()
    qu.pushQueue(13)
    qu.pullQueue()
    qu.pushQueue(14)
    qu.pullQueue()
    qu.pushQueue(15)
    print(qu.getQueue())

    queue2 = QueueLT(20, "Example")
    print(queue2.getQueue())

    print(queue2.getList())

    # queue3 = QueueLT(100, "Ex")
    # print(queue3.getQueue())
