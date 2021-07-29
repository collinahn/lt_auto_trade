# System Trading

### Description
* 주식 자동 매매 프로그램
  * 상시 돌아가며 자동 매매를 하고, 사용자가 원한다면 웹을 통해 개입하여 사거나 팔 수 있다.
* 대상이 되는 종목의 수 만큼 객체를 생성하여 공유메모리로 사용한다.
  * 일정 주기로 api를 통해 객체 내부의 정보를 업데이트한다.
  * 일정 주기로 DB에 저장하고 웹에서 요청이 있을 때 공유메모리에서 값을 읽어들인다.

### Environment
* Windows
* Python 3.8 interpreter

### Prerequisite
* Anaconda3 2021.05 (for python3.8)
* 키움증권 api (32-bit python)


### Files
* Stocks.py
  * 최소 단위가 되는 클래스 파일
  * 생성자와 소멸자를 재정의해 중복으로 인스턴스를 생성했 경우 기존의 인스턴스를 리턴하도록 하여 중복을 피한다. 
```python
class Stock:
    __mn_TotalStock = 0         #인스턴스 생성 카운트하기 위한 클래스 변수
    __mset_Stocks = set()       #매개변수로 들어온 값들 저장하기 위한 set 클래스 변수
    __mdict_Obj = {}            #생성된 인스턴스들 저장하기 위한 dict 클래스 변수 { nTick:_instance }
    __mdict_ObjCalled = {}      #각 인스턴스들 호출 내역 저장하기 위한 dict 클래스 변수 { nTick:True }

    #생성자가 이미 생성된 종목의 인스턴스인지 판단하고 그에 따라 중복 없이 인스턴스 할당
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            Stock.__mdict_Obj[args[0]] = cls._instance
            Stock.__mdict_ObjCalled[args[0]] = True
        elif {args[0]}.issubset(Stock.__mset_Stocks) == False:
            cls._instance = super().__new__(cls)
            Stock.__mdict_Obj[args[0]] = cls._instance
            Stock.__mdict_ObjCalled[args[0]] = True
        else:
            cls._instance = Stock.__mdict_Obj[args[0]]
        return cls._instance

    #파이썬 gc 주기에 의해 바로 반영이 안 될수도 있음
    def __del__(self):
        Stock.__mn_TotalStock -= 1
        Stock.__mdict_ObjCalled[self.__in_Ticker] = False
```

### Usage
* 프로젝트 완료 후 완성 예정 
