import requests
from time import sleep
from json import load
from twilio.rest import Client

logo = """Bot created by Amine :)\n\tmade with <3\n"""

print(logo)
del logo
print('Make sure to add twilio auth to receive SMS Notify When Reservation are opened\n\t\tEnjoy :)\n')
sleep(2)
print('SVP Essaie de faire une reservation manuel aussi\n')
print('Please try to make a manual reservation\n')
print('Bon Courage\nGoodluck\n')
sleep(5)

with open('sms.json', 'r', encoding='utf-8') as sms:
    twilio_config = load(sms)

twilio_account_number = twilio_config.get('twilio_account_number')
your_number = twilio_config.get('your_number')

del twilio_config, sms


def SMS_NOTIFICATION():
    with open('sms.json', 'r') as config:
        '''Create config.json with account_sid and auth_token
                        Open a twilio account it's free'''
        x = load(config)
        account_sid, auth_token = x.get('account_sid'), x.get('auth_token')

        """making a connection to twilio api"""
        client = Client(account_sid, auth_token)
        del x
        return client


def updater():
    while True:
        try:
            r = requests.get("http://127.0.0.1:5000/not_full", timeout=5)
            if len(r.json().get('uids')) != 0:
                print('Reservation opened')
                break
            else:
                print('Fetching eventz')
                requests.get("http://127.0.0.1:5000/TCF", timeout=30)
                sleep(10)

        except requests.ConnectionError:
            print("Please Start the server from events.py/.exe")
            sleep(5)
        except requests.ReadTimeout:
            print("Timeout")

    print('No Need to update Reservation are open')
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

    while True:
        try:
            requests.get("http://127.0.0.1:5000/TCF", timeout=30)
        except requests.ConnectionError:
            sleep(5)
        except requests.ReadTimeout:
            sleep(5)


if __name__ == "__main__":
    updater()
