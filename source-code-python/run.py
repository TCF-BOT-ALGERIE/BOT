import requests
from time import sleep
from re import findall
from json import load
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from datetime import datetime

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


file = open('result.txt', 'a', encoding='utf-8')
with open('configs/config.json', 'r', encoding='utf-8') as config:
    temp = load(config)
    email = temp.get('email')
    del temp, load

def Account():
    user_cookies = requests.get("http://127.0.0.1:5000/cookies")
    user_header = requests.get("http://127.0.0.1:5000/headers")
    return user_cookies.json().get('cookies'), user_header.json().get('headers')


def TCF():
    req = requests.get("http://127.0.0.1:5000/not_full")
    return req.json()["uids"]


def login(email: str):
    user_cookies, user_headers = Account()
    csrf_regex = r"""\<meta\sname\=\"csrf\-token\"\scontent="(.*?)\">"""
    time_shifts = []
    periods = []
    url = 'https://portail.if-algerie.com/'
    s = requests.Session()
    while True:
        permission = requests.get("http://127.0.0.1:5000/not_full")
        if len(permission.json().get('uids')) != 0:
            while True:
                try:
                    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    print(f"{now}\t LOGIN ATTEMPT", end='\n')
                    del now
                    res_post = s.get(url, headers=user_headers, cookies=user_cookies, verify=False, timeout=35)
                    print(res_post.url)
                    if res_post.url == 'https://portail.if-algerie.com/':
                        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        print(f'{now}\t{email} LOGGED IN', end='\n')
                        for uid in TCF():
                            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            print(f'{now}\tAttempting reservation for uid {uid}')
                            del now
                            x = s.get('https://portail.if-algerie.com/exams', verify=False, timeout=35)
                            csrf = findall(csrf_regex, x.text)[0]
                            head = s.headers.copy()
                            head['X-Requested-With'] = 'XMLHttpRequest'
                            head['X-CSRF-TOKEN'] = csrf
                            head['Referer'] = 'https://portail.if-algerie.com/exams'
                            data = {'uid': uid, 'service_type': 'EX'}
                            req = s.post('https://portail.if-algerie.com/exams/getdays', headers=head,
                                         data=data, cookies=user_cookies, timeout=35)
                            res = req.json()
                            if res['success']:
                                for i in range(len(res['dates'])):
                                    time_shifts.append(res['dates'][i]['timeShift']['uid'])
                                    periods.append(
                                        res['dates'][i]['info']['From'] + "-" + res['dates'][i]['info']['To'])
                                for i in range(len(time_shifts)):
                                    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                    print(f'{now}\t{uid}\t{periods[i]}\t{time_shifts[i]}')
                                    del now
                                    dataReserve = {
                                        'uid': uid,
                                        'motivation': "1",
                                        'timeshift': periods[i],
                                        'info': time_shifts[i]
                                    }
                                    print(f"Attempting a reservation for {email}", end='\n')
                                    reserve = s.post("https://portail.if-algerie.com/exams/reserve", headers=head,
                                                     data=dataReserve, cookies=user_cookies,
                                                     timeout=35)
                                    _res = reserve.json()
                                    if _res['success']:
                                        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                        print(f'{now}\treservation placed {periods[i]}\t{time_shifts[i]}', end='\n')
                                        del now
                                        y = email + ' : Réservé' + '\n'
                                        file.write(y)
                                        return True
                                    else:
                                        sleep(2.5)
                            else:
                                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                print(f"{now}\tFailure\t{res}")
                                del now
                                sleep(2.5)

                except Exception:
                    sleep(2.5)
        else:
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"{now}\tReservation Closed\n")
            del now
            sleep(15)


if __name__ == "__main__":
    login(email)
