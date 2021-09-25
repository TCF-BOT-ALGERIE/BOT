import requests
from bs4 import BeautifulSoup
from time import sleep
from threading import Thread
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from datetime import datetime

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

threads_warehouse = []

file = open('result.txt', 'a', encoding='utf-8')


def Accounts():
    req = requests.get("http://127.0.0.1:5000/account")
    return req.json()


def TCF():
    req = requests.get("http://127.0.0.1:5000/not_full")
    return req.json()["uids"]


def login(email: str, password: str):

    time_shifts = []
    periods = []
    url = 'https://portail.if-algerie.com/login'
    s = requests.Session()
    while True:
        permission = requests.get("http://127.0.0.1:5000/not_full")
        if len(permission.json().get('uids')) != 0:
            while True:
                try:
                    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    print(f"{now}\t LOGIN ATTEMPT", end='\n')
                    del now
                    res_get = s.get(url, verify=False, timeout=30)
                    soup = BeautifulSoup(res_get.text, 'html.parser')
                    csrf = soup.find("meta", {"name": "csrf-token"})["content"]
                    header = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                      "like Gecko) "
                                      "Chrome/92.0.4515.159 Safari/537.36",
                        "X-CSRF-TOKEN": csrf,
                        "Referer": "https://portail.if-algerie.com/login",
                        "X-Requested-With": "XMLHttpRequest"
                    }
                    payload = {
                        "rt": "https://portail.if-algerie.com/",
                        "email": email,
                        "password": password,
                        "remember": "on"
                    }
                    res_post = s.post(url, headers=header, data=payload, verify=False, timeout=30)
                    if res_post.json().get('notification').get('importance') == 'success':
                        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        print(f'{now}\t{email} LOGGED IN', end='\n')
                        for uid in TCF():
                            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            print(f'{now}\tAttempting reservation for uid {uid}')
                            del now
                            x = s.get('https://portail.if-algerie.com/exams', verify=False, timeout=30)
                            csrf = BeautifulSoup(x.text, 'html.parser').find("meta", {"name": "csrf-token"})["content"]
                            head = s.headers.copy()
                            head['X-Requested-With'] = 'XMLHttpRequest'
                            head['X-CSRF-TOKEN'] = csrf
                            head['Referer'] = 'https://portail.if-algerie.com/exams'
                            data = {'uid': uid, 'service_type': 'EX'}
                            req = s.post('https://portail.if-algerie.com/exams/getdays', headers=head,
                                         data=data, timeout=30)
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
                                                     data=dataReserve,
                                                     timeout=30)
                                    _res = reserve.json()
                                    if _res['success']:
                                        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                        print(f'{now}\treservation placed {periods[i]}\t{time_shifts[i]}', end='\n')
                                        del now
                                        y = email + ' : Réservé' + '\n'
                                        file.write(y)
                                        return True
                                    else:
                                        sleep(1)
                            else:
                                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                print(f"{now}\tFailure")
                                del now
                                sleep(2)

                except Exception:
                    sleep(2)
        else:
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"{now}\tReservation Closed\n")
            del now
            sleep(10)



def threads():
    acc = Accounts()
    for _ in range(2):
        email = acc["email"]
        password = acc["password"]
        t = Thread(target=login, args=(email, password))
        threads_warehouse.append(t)
    del acc


def multi():
    i = 1
    for t in threads_warehouse:
        print(f"Starting thread num #{i}", end='\n')
        t.start()
        i += 1


def main():
    threads()
    multi()


if __name__ == "__main__":
    main()
