#!/usr/bin/env python3

import requests
from urllib.parse import urlencode, parse_qs, splitquery
from datetime import datetime
import json
from slacker import Slacker

with open('config.json') as json_file:
    config = json.load(json_file)

password = config['password']
username = config['username']
client_id = config['client_id']
client_secret = config['client_secret']
slack_api_token =  config['slack_api_token']
slack_user = config['slack_user']

slack = Slacker(slack_api_token)


def get_code(client_id, username, password):
    url = "https://api3.stromer-portal.ch/users/login/"
    s = requests.session()
    res = s.get(url)
    s.cookies

    qs = urlencode({
        "client_id":
        client_id,
        "response_type":
        "code",
        "redirect_url":
        "stromerauth://auth",
        "scope":
        "bikeposition bikestatus bikeconfiguration bikelock biketheft bikedata bikepin bikeblink userprofile",
    })

    data = {
        "password": password,
        "username": username,
        "csrfmiddlewaretoken": s.cookies.get("csrftoken"),
        "next": "/o/authorize/?" + qs,
    }

    res = s.post(url, data=data, headers=dict(Referer=url), allow_redirects=False)
    res = s.send(res.next, allow_redirects=False)
    _, qs = splitquery(res.headers["Location"])
    code = parse_qs(qs)["code"][0]
    return code


def get_access_token(client_id, client_secret, code):
    url = "https://api3.stromer-portal.ch//o/token/"
    params = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": "stromerauth://auth",
    }

    res = requests.post(url, params=params)
    return res.json()["access_token"]


def call_api(access_token, endpoint, params={}):
    url = "https://api3.stromer-portal.ch/rapi/mobile/v2/%s" % endpoint
    headers = {"Authorization": "Bearer %s" % access_token}
    res = requests.get(url, headers=headers, params={})
    data = res.json()["data"]
    if isinstance(data, list):
        return data[0]
    else:
        return data


def call_bike(access_token, bike, endpoint, cached="false"):
    endpoint = 'bike/%s/%s' % (bike["bikeid"], endpoint)
    params = {'cached': '%s' % cached}
    state = call_api(access_token, endpoint, params)
    return state


code = get_code(client_id, username, password)
access_token = get_access_token(client_id, client_secret, code)

bike = call_api(access_token, "bike")

state = call_bike(access_token, bike, 'state/')
average_speed = state['average_speed_trip']
distance = (int(state['total_distance']) - 1781) + 8343
battery = state['battery_SOC']
current_speed = state['bike_speed']

status_text = ':bicyclist: total: {} km, average {} km/h, battery: {} %, current: {} km/h :bicyclist:'.format(
    distance, average_speed, battery, current_speed)

slack.users.profile.set(user=slack_user, name='status_text', value=status_text)
