# 2021.08.04 created by taeyoung

# 민감한 정보가 포함된 채 github에 직접 올리지 않기 위해 사용하는 파일
# 상수는 Const.py로 가고 업데이트 될 때마다 커밋하고, 
# 이 파일은 각자 pull해서 각자 정보를 입력한 뒤 .gitignore에 본 파일명을 저장하세요
# 다른 소스에선 import 해서 변수단위로 사용

#다음과 같은 명령어를 사용해 추적을 중지한다.
'''
$ git update-index --assume-unchanged config.py
'''

# 예시

'''
tyIpAddr= 192.168.123.0
tyPort= 22932
dbID='admin'
dbPW='pw001'

사용시
import config

app.run(IP=config.tyIpAddr, PORT=config.tyPort)
'''

#############################


