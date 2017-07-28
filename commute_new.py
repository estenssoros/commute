from __future__ import division

import datetime as dt
import json
import os
import sys
from pprint import pprint

import googlemaps
import requests
from astral import Astral

from parsers import parse_accu_json


def get_to_from():
    with open('addresses.json', 'r') as f:
        add_dict = json.load(f)
    if dt.datetime.today().hour < 12:
        return add_dict['home'], add_dict['work']
    else:
        return add_dict['work'], add_dict['home']


def get_coord(string):
    gmaps = googlemaps.Client(key=os.environ['GOOGLE_KEY'])
    resp = gmaps.geocode(string)
    lat_lng = resp[0]['geometry']['location']
    return lat_lng['lat'], lat_lng['lng']


def find_midpoint():
    home, work = get_to_from()
    home_coord = get_coord(home)
    work_coord = get_coord(work)
    return (home_coord[0] + work_coord[0]) / 2, (home_coord[1] + work_coord[1]) / 2


def get_accu_location_key():
    with open('addresses.json', 'r') as f:
        add_dict = json.load(f)
    if not add_dict.get('location_key'):
        lat, lng = find_midpoint()
        api_key = os.environ['ACCU_WEATHER_KEY']
        url = 'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search.json?q={0}, {1}&apikey={2}'
        resp = requests.get(url.format(lat, lng, api_key))
        add_dict['location_key'] = resp.json()['Key']
        with open('addresses.json', 'w') as f:
            json.dump(add_dict, f)
    return add_dict['location_key']


def accu_api():
    location_key = get_accu_location_key()
    url = 'http://dataservice.accuweather.com/currentconditions/v1/{0}?apikey={1}&details=true'
    resp = requests.get(url.format(location_key, os.environ['ACCU_WEATHER_KEY'])).json()[0]
    data = parse_accu_json(resp)
    return data


def distance_matrix_api():
    origin, destination = get_to_from()
    gmaps = googlemaps.Client(key=os.environ['GOOGLE_KEY'])
    args = {'mode': 'driving',
            'units': 'imperial',
            'departure_time': dt.datetime.today(),
            'traffic_model': 'best_guess',
            'avoid': 'tolls'}
    response = gmaps.distance_matrix(origin, destination, **args)
    elements = response['rows'][0]['elements'][0]
    duration = elements['duration_in_traffic']['value']
    distance = elements['distance']['value']
    traffic = duration - elements['duration']['value']
    data = {'distance': distance,
            'duration': duration,
            'origin': origin,
            'destination': destination,
            'traffic': traffic}
    return data


def sun_api():
    data = {}
    city_name = 'Denver'
    a = Astral()
    a.solar_depression = 'civil'
    city = a[city_name]
    sun = city.sun(date=dt.datetime.today(), local=True)
    data = {k: sun[k].hour * 60 + sun[k].minute for k in sun}
    data['moon_phase'] = city.moon_phase()
    return data


if __name__ == '__main__':
    pprint(accu_api())
