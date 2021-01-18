
from flask import Flask
import requests
import datetime


app = Flask(__name__)


@app.route('/trends')
def hello_world():
    return 'Hello, World!'


@app.route('/')
def trends():
    try:
        current_date, t_minus_day = datetime.date.today(), datetime.timedelta(-30)
        thirty_days_ago = current_date + t_minus_day

        date, per_page = thirty_days_ago.strftime("%Y-%m-%d"), 100
        url = f'https://api.github.com/search/repositories?q=created:>{date}&sort=stars&order=desc&per_page={per_page}'

        # check if you're within your rate limit as this is an unauthenticated API
        rate_url = 'https://api.github.com/ratelimit/'
        rate_limit = requests.get(rate_url)
        rate = rate_limit.headers.get('X-RateLimit-Remaining')
        if int(rate) <= 0:
            raise TimeoutError("API rate Limit exceeded for an hour, please try again later!")

        # request to api.github.com/search and return response as json
        response = requests.get(url).json()

        obj, lan, arr = response['items'], [], []

        for i in range(len(obj)):
            for key, value in obj[i].items():
                if key == "language" and value is None:
                    if "None" not in lan:
                        lan.append("None")
                        repo = {"None": {"count": 0, "projects": []}}
                        arr.append(repo)

                    for x in range(len(arr)):
                        for k, v in arr[x].items():
                            if k == "None":
                                v['count'] += 1
                                v['projects'].append(obj[i])

                if key == "language" and value is not None:
                    if value not in lan:
                        lan.append(value)
                        repo = {value: {"count": 0, "projects": []}}
                        arr.append(repo)

                    for y in range(len(arr)):
                        for k, v in arr[y].items():
                            if k == value:
                                v['count'] += 1
                                v['projects'].append(obj[i])

        fields = {
            "List of Languages": lan,
            "Sorted languages, number of repo, repos attached to each": arr
        }

        return fields

    except ConnectionError or TimeoutError or KeyError:
        raise
