import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import re
import json
import time
from flask import jsonify, Flask

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

app = Flask(__name__)
# app.config["DEBUG"] = True
app.config["JSON_SORT_KEYS"] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

with open('configs/config.json', 'r', encoding='utf-8') as config:
    account = json.load(config)
with open('configs/types.json', 'r', encoding='utf-8') as types_config:
    types = json.load(types_config)
with open('configs/antenne.json', 'r', encoding='utf-8') as antennes_config:
    antennes = json.load(antennes_config)

# Type de TCF est configuré comme SO Par Défault
# Antenne d'Alger est configuré par défault

email = account.get('email')
password = account.get('password')
tcy_type = types.get(account.get("TCF_TYPE"))
antenne = antennes.get(account.get('antenne'))

not_full = []
full = []

cached_cookies = None
cached_header = None
csrf_tokens = []

def login(email: str, password: str, tcf_type: str, antenne: str):
    global cached_header, cached_cookies
    """Login In to the account and scrape DATES to use it on the schedule function"""

    regex = r"""\s*var\s*defaultEvents\s\W\s*\W\s*(.*)\]\;"""
    csrf_regex = r"""\<meta\sname\=\"csrf\-token\"\scontent="(.*?)\">"""
    rendez_vous = []
    choosed_type = []
    s = requests.Session()
    url = 'https://portail.if-algerie.com/login'
    success = False
    try:
        if cached_header is None and cached_cookies is None:
            res_get = s.get(url, verify=False, timeout=35)
            csrf = re.findall(csrf_regex, res_get.text)[0]
            csrf_tokens.append(csrf)
            header = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
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

            res_post = s.post(url, headers=header, data=payload, verify=False, timeout=35)
            exams = s.get('https://portail.if-algerie.com/exams', timeout=35)
            if exams.url == "https://portail.if-algerie.com/exams":
                success = True
                try:
                    cached_header = dict(s.headers)
                    cached_cookies = s.cookies.get_dict()
                except:
                    pass
            else:
                return {"error": "login failed"}
        else:
            exams = s.get('https://portail.if-algerie.com/exams',
                          cookies=cached_cookies, headers=s.headers, timeout=30)
            if exams.url == "https://portail.if-algerie.com/exams":
                success = True
        if success:
            exm = re.findall(regex, exams.text, re.DOTALL | re.MULTILINE | re.VERBOSE | re.IGNORECASE)
            exm = exm[0].replace('\n', '')
            exm = exm.replace(' ', '').rstrip(',')
            to_replaced = ["uid", "title", "start", "duration", "minutes", "className", "level", "price",
                           "antenna_name", "antenna_id", "local", "status", "full"]
            for i in to_replaced:
                exm = exm.replace(i, f'"{i}"')
            del to_replaced
            exm = re.sub(r'{"minutes":"[0-9]{0,3}"}', "0", exm)
            list_exm = exm.split('}')
            del exm
            for rdv in list_exm:
                rdv = rdv.lstrip(',').rstrip(',')
                rdv = rdv.lstrip('{').rstrip('}')
                rdv = '{' + rdv + '}'
                r = json.loads(rdv)
                if len(r) != 0:
                    rendez_vous.append(r)
            del list_exm
            for rdv in rendez_vous:
                if rdv['title'] == tcf_type and rdv['antenna_id'] == antenne:
                    choosed_type.append(rdv)
                    if rdv["full"] != "1":
                        if rdv.get('uid') not in not_full:
                            not_full.append(rdv.get('uid'))
                    elif rdv["full"] == "1":
                        if rdv.get('uid') not in full:
                            full.append(rdv.get('uid'))

            return choosed_type

        else:
            return {"error": "web site closed"}


    except Exception as e:
        print(e)
        time.sleep(5)


def main():
    @app.get('/')
    def home():
        return {"status": "bot is working"}

    @app.route('/not_full', methods=["GET"])
    def uid():
        return {"uids": not_full}

    @app.route('/full', methods=["GET"])
    def uid_full():
        return {"full": full}

    @app.route('/TCF', methods=["GET"])
    def so():
        try:
            return jsonify(results=login(email, password, tcy_type, antenne))
        except TypeError:
            return {"error": "parsing failed"}

    @app.route("/account", methods=["GET"])
    def show_current_accounts():
        return account

    @app.route('/cookies', methods=["GET"])
    def user_cookies():
        return jsonify(cookies=cached_cookies)

    @app.route('/headers', methods=["GET"])
    def user_headers():
        try:
            return jsonify(header=cached_header)
        except TypeError:
            return {"error": "type error"}

    @app.route('/csrf', methods=["GET"])
    def csrf_token():
        return {"csrf": csrf_tokens[0]}

    @app.route('/reset', methods=["GET"])
    def reset():
        global cached_header, cached_cookies
        not_full.clear()
        full.clear()
        cached_cookies = None
        cached_header = None
        return {"message": "reset successfully"}

    app.run(threaded=True, port=5000)


if __name__ == "__main__":
    main()
