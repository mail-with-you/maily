from django.shortcuts import redirect, render
import requests
import pyperclip
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller
from django.contrib import messages
import pandas as pd
import numpy as np

# Create your views here.


def home(request):
    return render(request, 'home.html')


def login(request):
    return render(request, 'login.html')


def report(request):
    id = request.GET['id']
    pw = request.GET['pw']

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("disable-gpu")

    path = chromedriver_autoinstaller.install()
    driver = webdriver.Chrome(path, options=options)
    driver.implicitly_wait(5)
    driver.get('https://nid.naver.com/nidlogin.login')
    driver.implicitly_wait(5)

    # 아이디 입력, 패스워드 입력
    naver_id = driver.find_element_by_name('id')
    naver_id.clear()
    naver_id.click()
    user_id = id
    user_pw = pw
    pyperclip.copy(user_id)
    naver_id.send_keys(Keys.COMMAND, 'v')
    driver.implicitly_wait(5)

    naver_pw = driver.find_element_by_name('pw')
    naver_pw.clear()
    naver_pw.click()
    pyperclip.copy(user_pw)
    naver_pw.send_keys(Keys.COMMAND, 'v')
    driver.implicitly_wait(5)

    # 로그인 버튼 누르기
    login_btn = driver.find_element_by_id('log.login')
    login_btn.click()
    time.sleep(2)

    target_url = driver.current_url

    if target_url == 'https://nid.naver.com/nidlogin.login':
        messages.success(request, "아이디와 비밀번호가 일치하지 않습니다.")
        return redirect('login')

    else:
        # 메일 함 들어갔을 때 사용자의 쿠키 받아오기(cookie)
        cookies = driver.get_cookies()
        cookie = ''
        for i in cookies:
            cookie = cookie+(i)['name']+'='+(i)['value']+';'

        headers = {
            'cookie': cookie
        }
        params_mail = (
            ('page', '1'),
            ('u', id),
        )

        params_data = {
            'u': id
        }
        mail_list_name = []
        # 메일에 관련된 요청
        response_mail = requests.post(
            'https://mail.naver.com/json/list/', headers=headers, params=params_mail)
        arr = response_mail.json()
        totalCount = arr['totalCount']  # 총 메일갯수
        unreadCount = arr['unreadCount']  # 안 읽은 메일 갯수

        # 용량에 관련된 요청
        response_capacity = requests.post(
            'https://mail.naver.com/json/option/trash/get/', headers=headers, data=params_data)
        diskUsage = (response_capacity.json())['diskUsage']  # 총 사용 용량

    ##############################################################################
        headers = {
            'referer': 'https://mail.naver.com/',
            'cookie': cookie
        }

        data = {
            'listNum': '200',
            'u': id
        }

        requests.post('https://mail.naver.com/json/option/list/set/',
                      headers=headers, data=data)

        headers = {
            'cookie': cookie

        }
        params_mail = (
            ('page', '1'),
            ('u', id),
        )

        params_data = {
            'u': id
        }
        mail_list_name = []
        # 메일에 관련된 요청
        response_mail = requests.post(
            'https://mail.naver.com/json/list/', headers=headers, params=params_mail)
        arr = response_mail.json()

        # one_page_number = arr['listCount']  # 첫페이지 메일 갯수
        # restrict_num=one_page_number*50
        mail_size = 0
        for i in range(1, 51):
            headers = {
                'cookie': cookie

            }
            params_mail = (
                ('page', i),
                ('u', id),
            )

        # 메일에 관련된 요청
            response_mail = requests.post(
                'https://mail.naver.com/json/list/', headers=headers, params=params_mail, timeout=500)
            arr = response_mail.json()

            mail_data_list = arr['mailData']
            # 제목, 보낸이, 크기, 시리얼넘버, 보낸 시간, read(default:read), mark(default:mark) 딕션너리 생성
            for i in mail_data_list:
                mail_list_name.append([i['from']['name'], i['size']])
                mail_size += i['size']
        # result의 값은 보낸이를 내림차순으로 나타낸 리스트이다.
        result = sorted(mail_list_name, key=lambda x: x[1], reverse=True)
        g = pd.DataFrame(result)
        g = g.groupby(g[0]).sum()
        g = g.sort_values(by=1, ascending=False)
        g = g.iloc[1:4]
        g = g.reset_index()

        k = np.array((g.iloc[0].tolist()))
        l = np.array((g.iloc[1].tolist()))
        m = np.array((g.iloc[2].tolist()))

        first_name = k[0]
        first_capa = round(int(k[1]) / 1024, 2)
        first_carbon = round((int(k[1]) / 1024) *
                             0.0000030517819446 * 0.447755118655106, 4)
        second_name = l[0]
        second_capa = round(int(l[1]) / 1024, 2)
        second_carbon = round((int(l[1]) / 1024) *
                              0.0000030517819446 * 0.447755118655106, 4)
        third_name = m[0]
        third_capa = round(int(m[1]) / 1024, 2)
        third_carbon = round((int(m[1]) / 1024) *
                             0.0000030517819446 * 0.447755118655106, 4)
        readCount = totalCount - unreadCount
        unreadPersent = round(unreadCount/totalCount * 100, 2)

        expression = 'test2'

        mail_size = round(mail_size * 0.0000030517819446 *
                          0.447755118655106, 0)
        mail_money = mail_size * 20
        expression = ''
        if mail_money < 3000:
            expression = 'computer'
        elif mail_money < 5000:
            expression = 'coffee'
        elif mail_money < 10000:
            expression = 'mic'
        elif mail_money < 20000:
            expression = 'chicken'
        elif mail_money < 50000:
            expression = 'book'
        elif mail_money < 100000:
            expression = 'alchol'

        return render(request, 'report.html', {'id': id, 'mail_size': mail_size, 'first_carbon': first_carbon, 'second_carbon': second_carbon, 'third_carbon': third_carbon, 'expression': expression, 'readCount': readCount, 'unreadPersent': unreadPersent, 'unreadCount': unreadCount, 'diskUsage': diskUsage, 'cookie': cookie, 'totalCount': totalCount, 'first_name': first_name, 'first_capa': first_capa, 'second_name': second_name, 'second_capa': second_capa, 'third_name': third_name, 'third_capa': third_capa})


def delete(request):
    id = request.GET['id']
    cookie = request.GET['cookie']
    totalCount = request.GET['totalCount']
    mail_size = request.GET['mail_size']


###############################################################################

    return render(request, 'delete.html', {'mail_size': mail_size, 'id': id, 'cookie': cookie, 'totalCount': totalCount})


def confirm(request):
    mail_list = []
    read = request.GET['isRead']
    mark = request.GET['isMark']
    to_date = request.GET['to_date']
    from_date = request.GET['from_date']
    cookie = request.GET['cookie']
    id = request.GET['id']

##################[첫 페이지] #########################################

    headers = {
        'cookie': cookie
    }
    params = (
        ('page', '1'),
        ('u', id),
    )

    response_mail = requests.post(
        'https://mail.naver.com/json/list/', headers=headers, params=params, timeout=500)
    arr = response_mail.json()

    mail_data_list = arr['mailData']
    for i in mail_data_list:
        mail_list.append(
            {'name': (i['from'])['name'],
             'size': i['size'],
             'subject': i['subject'],
             'mailSN': i['mailSN'],
             'sentTime': i['sentTime'],
             'read': 'read',
             'mark': 'unmark',
             }
        )
        if len(mail_data_list) == 0:
            break
##############################################################################

#####################[두번쨰부터 끝까지]##########################################
    for i in range(2, 51):
        headers = {
            'cookie': cookie

        }
        params_mail = (
            ('page', i),
            ('u', id),
        )

    # 메일에 관련된 요청
        response_mail = requests.post(
            'https://mail.naver.com/json/list/', headers=headers, params=params_mail, timeout=500)
        arr = response_mail.json()
        mail_data_list = arr['mailData']
        # 제목, 보낸이, 크기, 시리얼넘버, 보낸 시간, read(default:read), mark(default:mark) 딕션너리 생성
        for i in mail_data_list:
            mail_list.append(
                {'name': (i['from'])['name'],
                 'size': i['size'],
                 'subject': i['subject'],
                 'mailSN': i['mailSN'],
                 'sentTime': i['sentTime'],
                 'read': 'read',
                 'mark': 'none'
                 }
            )
            if len(mail_data_list) == 0:
                break
#########################################################################################

############################안읽은메일 요청해서 read:read 값을 read:unread로 치환###############
    for i in range(1, 51):
        headers = {
            'cookie': cookie
        }
        params = (
            ('page', i),
            ('isUnread', 'true'),
            ('u', id),
        )

        response_mail = requests.post(
            'https://mail.naver.com/json/list/', headers=headers, params=params, timeout=500)
        arr = response_mail.json()

        mail_data_list = arr['mailData']  # 보낸 사람
        a = []
        for i in mail_data_list:
            a.append(i['mailSN'])
        for m in mail_list:
            if m['mailSN'] in a:
                m['read'] = 'unread'
        if len(mail_data_list) == 0:
            break

######################################################################################

#########################중요메일 표시된메일만 요청해서 mark:unmark 값을 mark:mark 로 치환#######
    for i in range(1, 51):
        headers = {
            'cookie': cookie
        }
        params = (
            ('page', i),
            ('type', 'mark'),
            ('u', id),
        )

        response_mail = requests.post(
            'https://mail.naver.com/json/list/', headers=headers, params=params, timeout=500)
        arr = response_mail.json()
        mail_data_list = arr['mailData']  # 보낸 사람
        a = []
        for i in mail_data_list:
            a.append(i['mailSN'])
        for m in mail_list:
            if m['mailSN'] in a:
                m['mark'] = 'mark'
        if len(mail_data_list) == 0:
            break

    if read == "both" and mark == "both":
        mail_list = mail_list
    elif read == "both" and mark != "both":
        mail_list = [x for x in mail_list
                     if x["mark"] == mark]
    elif read != "both" and mark == "both":
        mail_list = [x for x in mail_list
                     if x["read"] == read]
    else:
        mail_list = [x for x in mail_list
                     if x["mark"] == mark and x["read"] == read]

    from_date = time.mktime(datetime.strptime(
        from_date, '%Y-%m-%d').timetuple())
    to_date = time.mktime(datetime.strptime(
        to_date, '%Y-%m-%d').timetuple())

    mail_list = [x for x in mail_list
                 if from_date < int(x["sentTime"]) < to_date]

    mail_size = 0
    for m in mail_list:
        mail_size = + m['size']

    for i in mail_list:
        i['size'] = round(i['size'] / 1024, 2)
        i['sentTime'] = datetime.utcfromtimestamp(
            i['sentTime']).strftime('%Y. %m. %d')
    mail_size = round(mail_size * 0.0000030517819446 *
                      0.447755118655106, 2)
    return render(request, 'confirm.html', {'mail_size': mail_size, 'mail_list': mail_list, 'id': id})


def result(request):
    mailSN = request.GET.getlist('mailSN')
    id = request.GET['id']
    mail_list_length = request.GET['mail_list_length']
    mail_size = request.GET['mail_size']
    cookie = request.GET['cookie']
    # # 휴지통으로 보내기 위해
    delete = ''
    for i in mailSN:
        delete = delete+i+';'

    # # 휴지통으로 보내기
    headers = {
        'authority': 'mail.naver.com',
        'referer': 'https://mail.naver.com/',
        'cookie': cookie,
    }

    data = {
        'mailSNList': delete,
        'currentFolderType': 'etc',
        'u': id
    }

    requests.post(
        'https://mail.naver.com/json/select/delete/', headers=headers, data=data)
    return render(request, 'result.html',  {'mail_list_length': mail_list_length, 'mail_size': mail_size, 'mailSN': mailSN, 'id': id})
