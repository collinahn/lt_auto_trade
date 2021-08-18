# 자료구조 및 유용한 함수들 공유해서 쓰기 위해 만든 파일들.

# 2021.08.12 created by taeyoung (Stocks.py에 있던 큐 자료구조 이관)

# 데이터 집어넣을 땐: push
# 데이터 가져올 땐: getHead & pull
# ** push/pull을 할 때 자체적으로 큐가 꽉 차있는지/비어있는지 확인한다.

from LoggerLT import Logger

class QueueLT:

    def __init__(self, nSize: int, sName="Random"):
        self.__is_Name = sName #디버깅 정보
        self.__iq_Queue = [None] * nSize
        self.__in_QueueSize = nSize
        self.__in_HeadPointIdx = 0
        self.__in_TailPointIdx = 0

        self.log = Logger()
        self.log.INFO(sName, "Queue initiated, size:", nSize)
        
    #큐에 데이터를 집어넣고 테일포인트를 옮긴다.
    def pushQueue(self, value: int or dict) -> bool:
        n_NextTailPointIdx = (self.__in_TailPointIdx +1) % self.__in_QueueSize

        if n_NextTailPointIdx is self.__in_HeadPointIdx:            # 테일+1 == 헤드(버퍼 full)
            self.log.WARNING(self.__is_Name, "Queue Full") 
            return False
        self.__iq_Queue[self.__in_TailPointIdx] = value   # 테일포인터가 가르키는 자리에 value삽입
        self.__in_TailPointIdx = n_NextTailPointIdx             # 다음 자리로 테일포인터 이동.
        return True
        
    #큐에서 데이터를 빼고(함수 앞에서 getHead로) 헤드포인트를 옮긴다.
    def pullQueue(self) -> int:
        n_NextHeadPointIdx = (self.__in_HeadPointIdx+1) % self.__in_QueueSize

        if self.__in_HeadPointIdx is self.__in_TailPointIdx:        # 테일 == 헤드 (buffer empty)
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

    def isEmpty(self) -> bool:
        return self.__in_HeadPointIdx == self.__in_TailPointIdx

    def isFull(self) -> bool:
        n_NextTailPointIdx = (self.__in_TailPointIdx +1) % self.__in_QueueSize

        return n_NextTailPointIdx == self.__in_HeadPointIdx             # 테일+1 == 헤드 => 버퍼 full



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

    