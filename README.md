# 증권사API를 이용한 주식자동매매 시스템과 웹을 통한 모니터링 및 제어

### Description
* 주식 자동 매매 프로그램
  * 상시 돌아가며 자동 매매를 하고, 사용자가 원한다면 웹브라우져을 통해 개입하여 사거나 팔 수 있다.
  * 메인 스레드에서 Django 서버를 띄우고 서버를 띄우기 전 서브 스레드에서 시스템트레이딩 시스템을 가동한다. 

* 대상이 되는 종목의 수 만큼 객체를 생성하여 여러 스레드에서 활용하는 공유메모리로 사용한다.
  * 일정 주기로 키움증권api를 통해 객체 내부의 정보를 업데이트한다.
  * 이벤트가 발생할 때 공유메모리에 올라가있는 항목들을 DB에 저장한다.
  * 웹에서 요청이 있을 때, 상태 정보는 공유메모리에서, 거래 정보는 DB에서 읽어들인다.
  * DB는 프로그램을 재시작했을 시 공유메모리를 초기화하거나 대량의 정보를 처리할 때 사용한다.

### Environment
* Windows 10
* Python 3.8 interpreter

### Prerequisite
* Anaconda3 2021.05 (for python3.8) - 32비트 가상환경에서 실행
* 키움증권 API (32-bit python)

### Files
* Stocks.py
  * 최소 단위가 되는 클래스 파일
  * 주식 종목마다 인스턴스가 새로 생성이 되어야하고, 같은 종목이면 인스턴스가 하나여야 한다.
  * 생성자를 재정의해 중복으로 인스턴스를 생성했을 경우 기존의 인스턴스를 리턴하도록 하여 쉽게 메모리관리를 할 수 있도록 한다.
  * 초기화 시에도 클래스 변수에서 이미 생성된 인스턴스인지 확인하고 그렇지 않은 경우에만 초기화한다.
```python
class Stock(object):
    __mn_TotalStock = 0         #인스턴스 생성 카운트하기 위한 클래스 변수
    __mset_Stocks = set()       #매개변수로 들어온 값들 저장하기 위한 set 클래스 변수
    __mdict_Obj = {}            #생성된 인스턴스들 저장하기 위한 dict 클래스 변수 { nTick:_instance }
    __mdict_ObjCalled = {}      #각 인스턴스들 호출 내역 저장하기 위한 dict 클래스 변수 { nTick:True }
                                #value가 true : 현재 보유중 false : 현재보유중 아님. key가 없을 땐 보유했던 적 없음

    #생성자가 이미 생성된 종목의 인스턴스인지 판단하고 그에 따라 중복 없이 인스턴스 할당
    def __new__(cls, *args):
        if isinstance(args[0], int) == False:
            raise(ValueError)

        if hasattr(cls, "_instance") and args[0] in Stock.__mset_Stocks:
            cls._instance = Stock.__mdict_Obj[args[0]]
        else:
            cls._instance = super().__new__(cls)
            Stock.__mdict_Obj[args[0]] = cls._instance
            Stock.__mdict_ObjCalled[args[0]] = True

        return cls._instance

    #인스턴스 변수 초기화
    def __init__(self, *args):
        if {args[0]}.issubset(Stock.__mset_Stocks) == False:
            self.log = Logger()
            self.__in_Ticker = args[0]
            #나중에 완성된 키움 api wrapper 클래스로 여기서 초기화
            self.__is_StockName = ""
            self.__in_StockCurrentPrice = 0
            self.__iq_StockValues = QueueLT(const.STOCK_VALUE_QUEUE_SIZE, "StockValue") #주가 저장
            self.__in_StockQuantity = 0
            self.__iq_TotalTradeVolume = QueueLT(const.STOCK_TRADING_VOLUME_QUEUE_SIZE, "TradeVolumePerDay")
            self.__is_LastUpdated = ""
            self.__id_DayBought = time.strftime("%d", time.localtime(time.time())) #래리 윌리엄스 모듈에서만 사용
```
* SharedMem.py
  * 종목들의 Stock 인스턴스들을 관리하는 클래스 파일.
  * 싱글턴으로 작성되어 어디서 호출하든 관리 중인 공유메모리가 리턴되도록 설계되었다.
  * 보유중인 인스턴스들은 주식코드를 키 값으로 하는 사전형 클래스 변수에 추가하여 관리한다.
  * 초기화 시 증권사 API로부터 유저 정보를 받아와 리스트로 초기화하게 되고, 그 전에 호출되는 경우는 메모리 주소를 갖는 인스턴스만 할당이 되고 초기화되지 않는다. 
```python
class SharedMem(object):
    __mdict_MstObject = {}   # 보유하고 있는 객체들을 dict형 변수에 저장한다.

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls.log = Logger()
        cls.log.INFO(cls._instance)
        return cls._instance

    def __init__(self, *args, **kwargs):
        cls = type(self)
        #최초 한 번만 초기화를 진행한다, 인자 없이 호출되는 경우 객체만 반환하고 초기화는 하지 않는다. 초기화는 RunThread.__init__에서
        if not hasattr(cls, "_init") and not hasattr(cls, "__il_Account_Info") and args:
            cls._init = True
            # if문 내부에서 초기화 진행
            self.__il_AccountInfo = args # 최초 SharedMem 인스턴스를 호출할 때 어카운트 정보로 초기화한다.

            self.iq_RequestQueue = QueueLT(const.REQUEST_QUEUE_SIZE, "Queue4Request2Api")  #TradeLogic에서 의사결정을 하면 매도, 매수 주문을 큐에 등록함

            from GetPutDB import GetPutDB
            self.cls_DB = GetPutDB()

            self.log.INFO("SharedMem init:", self.__il_AccountInfo)
```

* utilsLT.py -> QueueLT Class
  * 스레드 간 주고받을 커스텀 큐 자료구조를 정의.
  * 인스턴스를 생성할 때 큐의 크기와 이름을 인자로 필요로한다.
  * 이미 있는 이름을 받으면 존재하는 인스턴스를 넘겨줌으로써 편리하게 사용할 수 있도록 설계.

```python
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
            self.__is_Name = sName 
            self.__iq_Queue = [None] * nSize
            self.__in_QueueSize = nSize
            self.__in_HeadPointIdx = 0
            self.__in_TailPointIdx = 0

            QueueLT.__mset_Instance.add(sName)

            self.lock = threading.Lock() # 서로 다른 스레드에서 푸시할 때 데이터의 경쟁상태 방지

            self.log.INFO(sName, "Queue init, size:", nSize)

        else: 
            self.log.WARNING(sName, "Queue Called Again")
```
        

### Usage
 * Anaconda3 32bit 가상환경 구성하기
```
 # conda prompt
 > set CONDA_FORCE_32BIT=1
 > conda create -n {가상환경이름} python=3.8
```

 * 가상환경 실행
```
 # conda prompt, cmd
 > conda activate {가상환경이름}
```

 * 패키지
```
 > pip install django
 > pip install django-cors-headers
 > pip install django-rest-framework
 
```


 * 프로그램 및 서버 실행
```
 > python manage.py runserver --noreload
```