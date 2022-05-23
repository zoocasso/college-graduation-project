import speech_recognition as sr
import requests
import json
import keyword
import datetime
from bs4 import BeautifulSoup
import bs4.element
import xmltodict
import os

### 토큰 저장 파일&경로
filename="kakao_token.json"
kakao_url = "https://kauth.kakao.com/oauth/token"
app_key ="5b2920d2bf03708e12c48e54c0e2e150"
r_token = "B6pHkSrPmP0A4UoOjgCoYxkTs4YTV2hC7OM_EgorDR4AAAGAmjwWlw"

#카카오 토큰을 받아오는 처음 시작 함수
def code():
    data = {
        "grant_type" : "authorization_code",
        "client_id" : app_key,
        "redirect_uri" : "https://localhost.com",
        "code" : "C14Tw4M1k74RKIOXH8rz85mG6H86fWB2IqVFCgtZyOfXBnhlDOqK0w-Nh3RRwk007d0ESwo9dZoAAAGAmjtIDw"
    }
    response = requests.post(kakao_url, data=data)
    tokens = response.json()

        # 요청에 실패했다면,
    if response.status_code != 200:
        print("error! because ", response.json())
    else: # 성공했다면,
        tokens = response.json()
        print(tokens)
    #카카오 토큰을 저장할 파일명
        KAKAO_TOKEN_FILENAME = "res/kakao_message/kakao_token.json"
        save_tokens(KAKAO_TOKEN_FILENAME,tokens)

# 저장하는 함수
def save_tokens(filename, tokens):
    with open(filename, "w") as fp:
        json.dump(tokens, fp)

 #읽어오는 함수
def load_tokens(filename):
    with open(filename) as fp:
        tokens = json.load(fp)

    return tokens

# refresh_token으로 access_token 갱신하는 함수
def update_tokens(app_key, filename) :
    tokens = load_tokens(filename)

    kakao_url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type" : "refresh_token",
        "client_id" : app_key,
        "refresh_token" : r_token
    }
    response = requests.post(kakao_url, data=data)

    # 요청에 실패했다면,
    if response.status_code != 200:
        print("error! because ", response.json())
    else: # 성공했다면,
        tokens = response.json()
        print(tokens)
 #카카오 토큰을 저장할 파일명
    KAKAO_TOKEN_FILENAME = "res/kakao_message/kakao_token.json"
    save_tokens(KAKAO_TOKEN_FILENAME,tokens)   
    return tokens


#############코로나 확진자 수#################################################################
def covid19():
    update_tokens(app_key, filename)
    service_KEY = "DEaTeAeMY+/ZCys9LTGzBk/MnsJg8VJSGr7h5yrG94i8/FSzVyxUgMsVAM1E3B4XEmYhiTRt5a/fxW+ODvMJ6w=="
    service_url = "http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson"

    Now_str = datetime.date.today().strftime('%Y%m%d')
    Now = int(Now_str)
    Now_minus2=(Now-2)
    Now_minus2_str=str(Now_minus2)
        #코로나 api에서 원하는 형태
    params = {
        "ServiceKey":service_KEY,
        "pageNo":"1",
        "numOfRows":"2",
        "startCreateDt":Now_minus2_str,
        "endCreateDt":Now_str
        }
        
    #data를 요청
    resp = requests.get(service_url, params=params)
    #요청된 data를 dictionary 형태로 저장
    parsed_content = xmltodict.parse(resp.content)
    json_string=json.loads(json.dumps(parsed_content))
            #daily_cnt: 일별 확진자수, stateDt: 기준일, decideCnt: 누적 확진자수 -> api에서 오는 정보는 list형태이기 때문
    daily_cnt = []
    stateDt = []
    decideCnt = []
            #response 안에 body 안에 items 안에 item
    items = json_string['response']['body']['items']['item']
            #items을 추출
    for i in items:
        stateDt.append(i['stateDt'][4:]) #연도는 제외하고 월,일 만 가져와서 stateDt(리스트)에 추가
        decideCnt.append(int(i['decideCnt'])) 

    #일일 확진자 수 구하기 ->  오늘 확진자 수를 알 수 없어서 1일 빼서 제외시키는 거임, #len 문자열 길이 구하기 함수
    for i in range(len(stateDt)-1):
        daily_cnt.append(decideCnt[i]-decideCnt[i+1])
    print ("오늘 확진자 수는 %d명 이고 누적 확진자 수는 %d명입니다." %(daily_cnt[0],decideCnt[0]))

    ## 저장된 토큰 정보를 읽어 옴    
    KAKAO_TOKEN_FILENAME = "res/kakao_message/kakao_token.json"
    tokens = load_tokens(KAKAO_TOKEN_FILENAME)
    ## 텍스트 메시지 url
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    ## request parameter 설정
    headers = {
        "Authorization" : "Bearer " + tokens['access_token']
    }
    data = {
        "template_object" : json.dumps({ "object_type" : "text",
                                        "text" : "일일 확진자 수: %d \n누적 확진자수: %d"%(daily_cnt[0],decideCnt[0]),
                                        "link" : {
                                            "mobile_web_url" : "http://ncov.mohw.go.kr"
                                        }
                                        })
    }

    ## 나에게 카카오톡 메시지 보내기 요청 (text)
    response = requests.post(url, headers=headers, data=data)
    print(response.status_code)

    ## 요청에 실패했다면,
    if response.status_code != 200:
        print("error! because ", response.json())

    else: # 성공했다면,
        print('메시지를 성공적으로 보냈습니다.')

##############################################################################

#########뉴스 크롤링
    # BeautifulSoup 객체 생성, url을 요청해서 beautifulsoup객체를 생성하는 함수, url을 input으로 받고 beautifulsoup객체를 output으로 전달, 
def get_soup_obj(url):
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.39'}
    res = requests.get(url, headers = headers)
    soup = BeautifulSoup(res.text,'lxml')
    return soup
    
    # # 뉴스의 기본 정보 가져오기, for문의 내용을 함수화, input=section id & section -> url을 구성하고 상위 3개 뉴스에 대한 메타 정보를 만든 후에 output으로 전달, 3개 뉴스에 대한 메타 정보를 모두 보내줘야하므로 리스트 형식으로 함, 
def get_top3_news_info(sec, sid):
    # 임시 이미지, 이미지가 없는 뉴스도 있기 때문에 설정
    default_img = "https://search.naver.com/search.naver?where=image&sm=tab_jum&query=naver#"

    # 해당 분야 상위 뉴스 목록 주소
    sec_url = "https://news.naver.com/main/list.nhn?mode=LSD&mid=sec" \
            + "&sid1=" \
            + sid
    print("section url : ", sec_url)

    # 해당 분야 상위 뉴스 HTML 가져오기
    soup = get_soup_obj(sec_url)

    # 해당 분야 상위 뉴스 3개 가져오기
    global news_list3
    news_list3 = []
    lis3 = soup.find('ul', class_='type06_headline').find_all("li", limit=3)
    for li in lis3:
        # title : 뉴스 제목, news_url : 뉴스 URL, image_url : 이미지 URL
        news_info = {
            "title" : li.img.attrs.get('alt') if li.img else li.a.text.replace("\n", "").replace("\t","").replace("\r","") ,
            "date" : li.find(class_="date").text,
            "news_url" : li.a.attrs.get('href'),
            "image_url" : li.img.attrs.get('src') if li.img else default_img
        }
        news_list3.append(news_info)
    return news_list3

    # 뉴스 본문 가져오기, input으로는 뉴스 본문이 있는 url을 전달받아, html구조에 맞춰 뉴스 본문을 output으로 전달,
def get_news_contents(url):
    soup = get_soup_obj(url)
    body = soup.find('div', class_="_article_body_contents")

    news_contents = ''
    #for content in body:
    #    if type(content) is bs4.element.NavigableString and len(content) > 50:
    #        # content.strip() : whitepace 제거 (참고 : https://www.tutorialspoint.com/python3/string_strip.htm)
    #        # 뉴스 요약을 위하여 '.' 마침표 뒤에 한칸을 띄워 문장을 구분하도록 함
    #        news_contents += content.strip() + ' '

    return news_contents

# '정치', '경제', '사회' 분야의 상위 3개 뉴스 크롤링, input은 없고 output은 3개의 섹션별 3개의 뉴스 정보 및 뉴스 본문을 news_dic을 output으로 전달, sod에 사용될 정보를 담고 67라인에서 반복하여 요청
def get_naver_news_top3():
    # 뉴스 결과를 담아낼 dictionary
    news_dic = dict()
    # sections : '정치', '경제', '사회'
    sections = ["pol", "eco","soc"]
    # section_ids : URL에 사용될 뉴스 각 부문 ID
    section_ids = ["100", "101","102"]

    for sec, sid in zip(sections, section_ids):
        # 뉴스의 기본 정보 가져오기
        news_info = get_top3_news_info(sec, sid)
        # 3개의 분야의 뉴스 정보(title, news_url, date, image_url) 가 나옴
        #print(news_info)
        for news in news_info:
            # 뉴스 본문 가져오기
            news_url = news['news_url']
            news_contents = get_news_contents(news_url)

            # 뉴스 정보를 저장하는 dictionary를 구성
            news['news_contents'] = news_contents

        news_dic[sec] = news_info

    return news_dic
#######################################################################

def start_news_kakao(): 
    # 함수 호출 - '정치', '경제', '사회' 분야의 상위 3개 뉴스 크롤링
    news_dic = get_naver_news_top3()
    # 경제의 첫번째 결과 확인하기
    news_dic   

    update_tokens(app_key, filename)

    KAKAO_TOKEN_FILENAME = "res/kakao_message/kakao_token.json"
    ## 저장된 토큰 정보를 읽어 옴
    tokens = load_tokens(KAKAO_TOKEN_FILENAME)
    ## 텍스트 메시지 url
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Authorization" : "Bearer " + tokens['access_token']
    }
    ##리스트 템플릿으로 뉴스 목록 전송하기
    # 네이버 뉴스 URL
    navernews_url = "https://news.naver.com/main/home.nhn"
    # 추후 각 리스트에 들어갈 내용(content) 만들기
    contents = []
    # 리스트 템플릿 형식 만들기
    template = {
        "object_type" : "list",
        "header_title" : "상위 뉴스 빅3",
        "header_link" : {
            "web_url": navernews_url,
            "mobile_web_url" : navernews_url
        },
        "contents" : contents,
        "button_title" : "네이버 뉴스 바로가기"
    }
    ## 내용 만들기
    # 각 리스트에 들어갈 내용(content) 만들기
    for news_info in news_list3:
        content = {
            "title" : news_info.get('title'),
            "description" : "작성일 : " + news_info.get('date'),
            "image_url" : news_info.get('image_url'),
            "image_width" : 50, "image_height" : 50,
            "link": {
                "web_url": news_info.get('news_url'),
                "mobile_web_url": news_info.get('news_url')
            }
        }
        contents.append(content)
    data = {
        'template_object':json.dumps(template)
    }
    # 카카오톡 메시지 전송
    res = requests.post(url,data=data, headers=headers)
    if res.json().get('result_code') == 0:
        print('뉴스를 성공적으로 보냈습니다.')
    else:
        print('뉴스를 성공적으로 보내지 못했습니다. 오류메시지 : ', res.json())

####################################################################################
def get_speech():
    #마이크에서 음성을 추출하는 객체
    recognizer = sr.Recognizer()
        #마이크 설정
    microphone = sr.Microphone(sample_rate=16000)
        #마이크 소음 수치 반영 _ 보류
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
    #    print("소음 수치를 반영하여 음성을 청취합니다.{}".format(recognizer.energy_threshold)) - 빼도 되는듯
        #음성수집
    with microphone as source:
        print("음성인식중")
        audio_data = recognizer.listen(source)
    audio = audio_data.get_raw_data()

    kakao_speech_url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"
    headers = {
        "Content-Type": "application/octet-stream",
        "X-DSS-Service": "DICTATION",
        "Authorization": "KakaoAK " + "793b6c9257acd09a4d5c279601b21f40",}

    res = requests.post(kakao_speech_url, headers=headers, data=audio)
    result = res.text[res.text.find('{"type":"finalResult"'):res.text.rindex('}')+1]
    global text 
    text = json.loads(result).get('value')
    print(text)

def START():
    get_speech()
    KEYWORD_NEWS = "뉴스"
    KEYWord_COVID= "코로나"
    if text in "자비스":
        print("무엇을 도와드릴까요?")
        START()
    elif KEYWORD_NEWS in text:
            print("뉴스 프로젝트 실행")
            start_news_kakao()
    elif KEYWord_COVID in text:
            print("코로나 프로젝트 실행")
            covid19()
    else:
        print("다시한번 말해주세요")
        START()
START()
