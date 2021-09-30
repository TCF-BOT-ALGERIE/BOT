import requests
from time import sleep
from json import load
from twilio.rest import Client
from datetime import datetime

print("#"*40)
print("""\nBot created by Amine :)\n\n'''made with <3\n'''""")
print('Make sure to add twilio auth to receive SMS Notify When Reservation are opened\n\n\t\tEnjoy :)\n')
sleep(2)
print('SVP Essaie de faire une reservation manuel aussi\n')
print('Please try to make a manual reservation\n')
print('Bon Courage\nGoodluck\n')
print('#'*40)
sleep(2)

with open('configs/sms.json', 'r', encoding='utf-8') as sms:
    twilio_config = load(sms)

twilio_account_number = twilio_config.get('twilio_account_number')
your_number = twilio_config.get('your_number')

del twilio_config, sms


def SMS_NOTIFICATION():
    with open('configs/sms.json', 'r') as config:
        '''Create config.json with account_sid and auth_token
                        Open a twilio account it's free'''
        x = load(config)
        account_sid, auth_token = x.get('account_sid'), x.get('auth_token')

        """making a connection to twilio api"""
        client = Client(account_sid, auth_token)
        del x
        return client


def updater():
    if len(requests.get("http://127.0.0.1:5000/not_full", timeout=5).json().get('uids')) != 0:
        requests.get("http://127.0.0.1:5000/reset")
    while True:
        try:
            r = requests.get("http://127.0.0.1:5000/not_full", timeout=5)
            if len(r.json().get('uids')) != 0:
                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                print(f'{now}\tReservation opened')
                del now
                break
            else:
                requests.get("http://127.0.0.1:5000/TCF", timeout=36)
                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                print(f'{now}\tEvents Fetched')
                del now
                sleep(1.5)

        except requests.ConnectionError:
            print("Please Start the server from events.py/.exe")
            sleep(1)
        except requests.ReadTimeout:
            print("Timeout")

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f'{now}\tNo Need to update Reservation are open')
    try:
        message = SMS_NOTIFICATION().messages.create(
                body="\nDe Amine\nRendez Vous TCF Sont Ouverts",
                from_=twilio_account_number,
                to=your_number
            )
        print(message.sid)
        del message, Client, load

    except Exception:
        pass
    sleep(3600)
    requests.get('http://127.0.0.1:5000/reset')
    while True:
        try:
            requests.get("http://127.0.0.1:5000/TCF", timeout=36)
            sleep(1)
        except requests.ConnectionError:
            sleep(1)
        except requests.ReadTimeout:
            sleep(1)


if __name__ == "__main__":
    updater()
