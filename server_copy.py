from socket import *
from datetime import datetime, timedelta
import numpy as np
HOST = ""
PORT = 12000
s = socket(AF_INET, SOCK_STREAM)
print ('Socket created')
s.bind((HOST, PORT))
print ('Socket bind complete')
s.listen(1)
print ('Socket now listening')

while True:
   #접속 승인
    conn, addr = s.accept()
    print("Connected by ", addr)

   #데이터 수신
    rc = conn.recv(1024)
    rc = rc.decode("utf8").strip()
    if not rc: break
    print("Received: " + rc)
    date=rc[0:8]
    time=rc[8:]
    print('date:',date)
    print('time:',time)



    time1 = datetime.now() #현재 날짜 정보
    want_day_s = datetime(int(rc[0:4]),int(rc[4:6]),int(rc[6:8]),int(rc[8:10]),0,0) #원하는 날짜 정보 
    interval = (want_day_s - time1).days ## 오늘과 원하는 날짜의 차이 *2면 모레, 1이면 내일, 0이면 오늘 날씨 선택한 것
    if(interval == 2) and (int(time1[12:14])<=int(6)): #모레를 선택했는데 현재 시각이 새벽 여섯시 전이면 오류 메시지 보내기
        res = "새벽 6시 이후 모레 날씨 정보가 업데이트 됩니다!"
        conn.sendall(res.encode("utf-8"))
        conn.close()
        s.close()
        exit()
    if(interval !=1) and (interval !=0) and (interval !=2): #오늘, 내일, 모레 이외의 선택을 했을 시 오류 메시지 보내기
        res = "오늘, 내일, 모레의 예보만을 지원합니다!"
        conn.sendall(res.encode("utf-8"))
        conn.close()
        s.close()
        exit()
    pre_day_s = want_day_s + timedelta(days=-1) #하루 전날 날짜 정보 받기

    pre_day_s=str(pre_day_s)
    pre_day_s=pre_day_s[0:11]
    pre_day_s=pre_day_s.replace('-','')
    
    
    want_day_s=str(want_day_s)
    


    pre_day = pre_day_s + "00" #원하는 pre_day의 형태로 변환
    print('pre_day_s',pre_day_s)
    want_day = want_day_s[0:16] #원하는 want_day 형태로 변환
    print('want_day', want_day)

    ###########테스트 데이터 뽑기#################
    import pandas as pd
    from pandas import json_normalize
    import json
    import requests
    from bs4 import BeautifulSoup

    url = 'http://apis.data.go.kr/1360000/TourStnInfoService/getTourStnVilageFcst'

    x_test = pd.DataFrame(columns=['tm','spotName','th3','wd','ws','sky','rhm','pop'])

    for ID in range(1,439):
        No = [29, 248, 249, 250]
        if ID in No:
            continue
        course_id = str(ID)
        queryString = "?" + \
          "ServiceKey=" + "gc1Nbchq%2FAiQ%2FHHUN5pO8356kL4H%2FDGbVzxAWk3dJQu4fezp4AA%2B0aX0JaSTvuevF4OL9zOPj03OfxEh112utQ%3D%3D" + \
          "&pageNo=" + "1"+ \
          "&numOfRows=" + "140" + \
           "&dataType=" + "JSON" + \
           "&CURRENT_DATE=" + pre_day + \
          "&HOUR=" + "24" + \
          "&COURSE_ID=" + course_id
          
        queryURL = url + queryString
        response = requests.get(queryURL)

        #print(queryURL)
        r_dict = json.loads(response.content)
        data = json_normalize(r_dict['response']['body']['items']['item'])
        #print(data.info())

        li = ['tm','spotName','th3','wd','ws','sky','rhm','pop']
        
        #tm : 선택한 시각으로 부터 3시간 기온 (예 : 09면 09-12)
        #wd : 풍향
        #ws : 풍속
        #sky: 하늘 상태
        # 1: 맑음, 2: 구름 조금, 3: 구름많이, 4:흐림, 5: 비, 6:비눈, 7:눈비, 8:눈
        #rhm: 습도
        #pop: 강수확률

        #필요한 column만 data에 저장
        data = data.loc[:,li]
        #print(data.info())
        
        #오전 오후 저녁 시간선택에 맞는 데이터만 추출
        List = []
        for i in range(0,len(data['tm'])):
            if want_day not in data.loc[i,'tm']:
                    List.append(i)
        data = data.drop(List,axis = 0)
        #print(data.head())
        x_test = x_test.append(data,ignore_index=True)
        #print(x_test.head())
    x_test = x_test.drop_duplicates(['spotName'], keep='first')

   

    ############################################


    #############예측 모델 만들기################
    ############## test 데이터 달에 따라 다른 모델 load해서 예측 #####
    x_test_spotName = x_test['spotName']
    print(x_test_spotName)
    x_test = x_test.drop(['spotName','tm','wd'],axis=1)
    print(x_test.info())
    month = int(want_day[5:7])
    spring_m = [3,4,5]
    summer_m = [6,7,8]
    fall_m = [9,10,11]
    winter_m = [12,1,2]
  

    one = pd.read_csv('C:/Users/USER/Desktop/2021-1/전공심화공동체/one.csv',encoding='euc-kr')
    two = pd.read_csv('C:/Users/USER/Desktop/2021-1/전공심화공동체/two.csv',encoding='euc-kr')
    three = pd.read_csv('C:/Users/USER/Desktop/2021-1/전공심화공동체/three.csv',encoding='euc-kr')
    four = pd.read_csv('C:/Users/USER/Desktop/2021-1/전공심화공동체/four.csv',encoding='euc-kr')
    five = pd.read_csv('C:/Users/USER/Desktop/2021-1/전공심화공동체/five.csv',encoding='euc-kr')
    six = pd.read_csv('C:/Users/USER/Desktop/2021-1/전공심화공동체/six.csv',encoding='euc-kr')
    seven = pd.read_csv('C:/Users/USER/Desktop/2021-1/전공심화공동체/seven.csv',encoding='euc-kr')
    eight = pd.read_csv('C:/Users/USER/Desktop/2021-1/전공심화공동체/eight.csv',encoding='euc-kr')
    nine = pd.read_csv('C:/Users/USER/Desktop/2021-1/전공심화공동체/nine.csv',encoding='euc-kr')
    ten = pd.read_csv('C:/Users/USER/Desktop/2021-1/전공심화공동체/ten.csv',encoding='euc-kr')
    eleven = pd.read_csv('C:/Users/USER/Desktop/2021-1/전공심화공동체/eleven.csv',encoding='euc-kr')
    twelve = pd.read_csv('C:/Users/USER/Desktop/2021-1/전공심화공동체/twelve.csv',encoding='euc-kr')

    df_sp = pd.concat([three,four],ignore_index=True)
    df_sp = pd.concat([df_sp,five],ignore_index=True)

    #print(df_sp.info())

    df_su = pd.concat([six,seven],ignore_index=True)
    df_su = pd.concat([df_su,eight],ignore_index=True)

    #print(df_su.info())

    df_fa = pd.concat([nine,ten],ignore_index=True)
    df_fa = pd.concat([df_fa,eleven],ignore_index=True)

    #print(df_fa.info())

    df_wi = pd.concat([twelve,one],ignore_index=True)
    df_wi = pd.concat([df_wi,two],ignore_index=True)

    #print(df_wi.info())

    train_spring = df_sp.drop(['spotName','tm'], axis=1)
    train_summer = df_su.drop(['spotName','tm'], axis=1)
    train_fall = df_fa.drop(['spotName','tm'], axis=1)
    train_winter = df_wi.drop(['spotName','tm'], axis=1)
    print(train_spring.info())
    print(train_summer.info())
    y_label_spring=[0 for i in range(len(train_spring))]
    for i in range(len(train_spring)):
        if train_spring['th3'][i]>12:
          y_label_spring[i]+=1
        if train_spring['th3'][i]>15:
          y_label_spring[i]+=1
        if train_spring['ws'][i]<=6:
          y_label_spring[i]+=1
        if train_spring['ws'][i]<=3:
          y_label_spring[i]+=1
        if train_spring['sky'][i]==4:
          y_label_spring[i]+=1 
        if train_spring['sky'][i]==3:
          y_label_spring[i]+=2
        if train_spring['sky'][i]==2:
          y_label_spring[i]+=3 
        if train_spring['sky'][i]==1:
          y_label_spring[i]+=4
        if train_spring['rhm'][i]<60 and train_spring['rhm'][i]>=40:
          y_label_spring[i]+=1
        if train_spring['rhm'][i]<40 and train_spring['rhm'][i]>=20:
          y_label_spring[i]+=1
        if train_spring['rhm'][i]<20 and train_spring['rhm'][i]>=0:
          y_label_spring[i]+=1
        if train_spring['pop'][i]>=80:
          y_label_spring[i]+=1
        if train_spring['pop'][i]<80 and train_spring['rhm'][i]>=60:
          y_label_spring[i]+=1
        if train_spring['pop'][i]<60 and train_spring['rhm'][i]>=40:
          y_label_spring[i]+=1
        if train_spring['pop'][i]<40 and train_spring['rhm'][i]>=20:
          y_label_spring[i]+=1
        if train_spring['pop'][i]<20 and train_spring['rhm'][i]>=0:
          y_label_spring[i]+=1
          
    y_label_summer=[0 for i in range(len(train_summer['th3']))]
    for i in range(len(train_summer)):
        if train_summer['th3'][i]<=30:
          y_label_summer[i]+=1
        if train_summer['th3'][i]<=27:
          y_label_summer[i]+=1
        if train_summer['ws'][i]<=2:
          y_label_summer[i]+=1
        if train_summer['ws'][i]<=1:
          y_label_summer[i]+=2
        if train_summer['sky'][i]==4:
          y_label_summer[i]+=1 
        if train_summer['sky'][i]==3:
          y_label_summer[i]+=2
        if train_summer['sky'][i]==2:
          y_label_summer[i]+=3 
        if train_summer['sky'][i]==1:
          y_label_summer[i]+=4
        if train_summer['rhm'][i]<60 and train_summer['rhm'][i]>=40:
          y_label_summer[i]+=1
        if train_summer['rhm'][i]<40 and train_summer['rhm'][i]>=20:
          y_label_summer[i]+=1
        if train_summer['rhm'][i]<20 and train_summer['rhm'][i]>=0:
          y_label_summer[i]+=1
        if train_summer['pop'][i]>=80:
          y_label_summer[i]+=1
        if train_summer['pop'][i]<80 and train_summer['rhm'][i]>=60:
          y_label_summer[i]+=1
        if train_summer['pop'][i]<60 and train_summer['rhm'][i]>=40:
          y_label_summer[i]+=1
        if train_summer['pop'][i]<40 and train_summer['rhm'][i]>=20:
          y_label_summer[i]+=1
        if train_summer['pop'][i]<20 and train_summer['rhm'][i]>=0:
          y_label_summer[i]+=1

    y_label_fall=[0 for i in range(len(train_fall['th3']))]
    for i in range(len(train_fall)):
        if train_fall['th3'][i]>=10:
          y_label_fall[i]+=1
        if train_fall['th3'][i]>=15:
          y_label_fall[i]+=1
        if train_fall['ws'][i]<=2:
          y_label_fall[i]+=1
        if train_fall['ws'][i]<=1:
          y_label_fall[i]+=2
        if train_fall['sky'][i]==4:
          y_label_fall[i]+=1 
        if train_fall['sky'][i]==3:
          y_label_fall[i]+=2
        if train_fall['sky'][i]==2:
          y_label_fall[i]+=3 
        if train_fall['sky'][i]==1:
          y_label_fall[i]+=4
        if train_fall['rhm'][i]<60 and train_fall['rhm'][i]>=40:
          y_label_fall[i]+=1
        if train_fall['rhm'][i]<40 and train_fall['rhm'][i]>=20:
          y_label_fall[i]+=1
        if train_fall['rhm'][i]<20 and train_fall['rhm'][i]>=0:
          y_label_fall[i]+=1
        if train_fall['pop'][i]>=80:
          y_label_fall[i]+=1
        if train_fall['pop'][i]<80 and train_fall['rhm'][i]>=60:
          y_label_fall[i]+=1
        if train_fall['pop'][i]<60 and train_fall['rhm'][i]>=40:
          y_label_fall[i]+=1
        if train_fall['pop'][i]<40 and train_fall['rhm'][i]>=20:
          y_label_fall[i]+=1
        if train_fall['pop'][i]<20 and train_fall['rhm'][i]>=0:
          y_label_fall[i]+=1

    y_label_winter=[0 for i in range(len(train_winter['th3']))]
    for i in range(len(train_winter)):
        if train_winter['th3'][i]>=2:
          y_label_winter[i]+=1
        if train_winter['th3'][i]>=5:
          y_label_winter[i]+=1
        if train_winter['th3'][i]>=8:
          y_label_winter[i]+=1
        if train_winter['ws'][i]<=3:
          y_label_winter[i]+=1
        if train_winter['ws'][i]<=1:
          y_label_winter[i]+=2
        if train_winter['sky'][i]==4:
          y_label_winter[i]+=1 
        if train_winter['sky'][i]==3:
          y_label_winter[i]+=2
        if train_winter['sky'][i]==2:
          y_label_winter[i]+=3 
        if train_winter['sky'][i]==1:
          y_label_winter[i]+=4
        if train_winter['rhm'][i]<60 and train_winter['rhm'][i]>=40:
          y_label_winter[i]+=1
        if train_winter['rhm'][i]<40 and train_winter['rhm'][i]>=20:
          y_label_winter[i]+=1
        if train_winter['rhm'][i]<20 and train_winter['rhm'][i]>=0:
          y_label_winter[i]+=1
        if train_winter['pop'][i]>=80:
          y_label_winter[i]+=1
        if train_winter['pop'][i]<80 and train_winter['rhm'][i]>=60:
          y_label_winter[i]+=1
        if train_winter['pop'][i]<60 and train_winter['rhm'][i]>=40:
          y_label_winter[i]+=1
        if train_winter['pop'][i]<40 and train_winter['rhm'][i]>=20:
          y_label_winter[i]+=1
        if train_winter['pop'][i]<20 and train_winter['rhm'][i]>=0:
          y_label_winter[i]+=1
        

    #from joblib import dump, load
    if(month in spring_m):
        #automl = load('C:/Users/82102/OneDrive/바탕 화면/SJU/3학년/전공심화(두드림)/Spring.joblib')
        from sklearn.ensemble import RandomForestRegressor
        clf = RandomForestRegressor()
        clf.fit(train_spring, y_label_spring)
        y_predict = clf.predict(x_test)
        #y_predict = automl.predict(x_test)

    if(month in summer_m):
        #automl = load('C:/Users/82102/OneDrive/바탕 화면/SJU/3학년/전공심화(두드림)/Summer.joblib')
        from sklearn.ensemble import RandomForestRegressor
        clf = RandomForestRegressor()
        clf.fit(train_summer, y_label_summer)
        y_predict = clf.predict(x_test)
        #y_predict = automl.predict(x_test)

    if(month in fall_m):
        #automl = load('C:/Users/82102/OneDrive/바탕 화면/SJU/3학년/전공심화(두드림)/Fall.joblib')
        from sklearn.ensemble import RandomForestRegressor
        clf = RandomForestRegressor()
        clf.fit(train_fall, y_label_fall)
        y_predict = clf.predict(x_test)
        #y_predict = automl.predict(x_test)

    if(month in winter_m):
        #automl = load('C:/Users/82102/OneDrive/바탕 화면/SJU/3학년/전공심화(두드림)/Winter.joblib')
        from sklearn.ensemble import RandomForestRegressor
        clf = RandomForestRegressor()
        clf.fit(train_winter, y_label_winter)
        y_predict = clf.predict(x_test)
        #y_predict = automl.predict(x_test)
    Index = np.where(y_predict==max(y_predict))
    print(Index[0])
    #Index = y_predict.index(max(y_predict))
    res= x_test_spotName[Index[0][0]]


#--upgrade scikit-learn
#--user emlearn
    ##############################################

   #수신한 데이터 컨트롤 
    #res = "학습 모델에 테스트 데이터 넣어서 나온 추천 관광지 보내기"

    print("추천 지역 :" , res)

   #클라이언트에게 답을 보냄
    conn.sendall(res.encode("utf-8"))
   #연결 닫기
    conn.close()
    break
s.close()
