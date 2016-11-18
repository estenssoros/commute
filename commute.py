from __future__ import division
import googlemaps
import os
import time
import json
import datetime as dt
from astral import Astral
import requests
from time_functions import test_time, print_time, sleep_min
from parsers import parse_accu_json
from aws import *
import pandas as pd


def get_to_from():
    with open('addresses.json', 'r') as f:
        add_dict = json.load(f)
    if dt.datetime.today().hour < 12:
        return add_dict['home'], add_dict['work']
    else:
        return add_dict['work'], add_dict['home']


def get_coord(string):
    gmaps = googlemaps.Client(key=os.environ['GMAPS_API_KEY'])
    resp = gmaps.geocode(string)
    lat_lng = resp[0]['geometry']['location']
    return lat_lng['lat'], lat_lng['lng']


def find_midpoint():
    home, work = get_to_from()
    home_coord = get_coord(home)
    work_coord = get_coord(work)
    return (home_coord[0] + work_coord[0]) / 2, (home_coord[1] + work_coord[1]) / 2,


def get_accu_location_key():
    lat, lng = find_midpoint()
    api_key = os.environ['ACCU_WEATHER_KEY']
    url = 'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search.json?q={0}, {1}&apikey={2}'
    resp = requests.get(url.format(lat, lng, api_key))
    return resp.json()['Key']

location_key = get_accu_location_key()


def get_dm():
    '''
    api
    '''
    origin, destination = get_to_from()
    gmaps = googlemaps.Client(key=os.environ['GMAPS_API_KEY'])
    response = gmaps.distance_matrix(origin,
                                     destination,
                                     mode='driving',
                                     units='imperial',
                                     departure_time=dt.datetime.today(),
                                     traffic_model='best_guess')
    elements = response['rows'][0]['elements'][0]
    duration = elements['duration_in_traffic']
    distance = elements['distance']
    data = {'distance': distance['value'],
            'duration': duration['value'],
            'origin': origin,
            'destination': destination}
    return data


def accu_api():
    '''
    api
    '''
    url = 'http://dataservice.accuweather.com/currentconditions/v1/{0}?apikey={1}&details=true'
    try:
        resp = requests.get(url.format(location_key, os.environ[
                            'ACCU_WEATHER_KEY'])).json()[0]
        data = parse_accu_json(resp)
    except Exception as e:
        print 'Accuweather offline...'
        data = dict()
    return data


def get_sun():
    data = {}
    city_name = 'Denver'
    a = Astral()
    a.solar_depression = 'civil'
    city = a[city_name]
    sun = city.sun(date=dt.datetime.today(), local=True)
    data = {k: time.mktime(sun[k].timetuple()) for k in sun}
    data['moon_phase'] = city.moon_phase()
    return data


def get_accu_weather():
    '''
    generator
    '''
    i = 0
    data = accu_api()
    while True:
        if i < 5:
            i += 1
            yield data
        else:
            i = 0
            data = accu_api()
            yield data


def make_data_gen():
    '''
    generator
    '''
    accu_gen = get_accu_weather()
    while True:
        data = {'time': time.time()}
        data.update(get_dm())
        data.update(get_sun())
        data.update(accu_gen.next())
        yield data


def make_dynamodb_gen():
    '''
    generator
    '''
    data_gen = make_data_gen()
    table = connect_dynamodb()
    while True:
        data = data_gen.next()
        item = table.new_item(attrs=data)
        item.put()
        print 'Uploaded to dynamodb!'
        yield


def upload_data_s3():
    fname = 'commute_data.csv'
    table = connect_dynamodb()
    data = list(table.scan())
    df = pd.DataFrame(data)
    df.to_csv(fname)
    upload_s3(fname)
    os.remove(fname)


def commute_hours():
    dynamodb_gen = None
    while True:
        os.system('clear')
        while test_time():
            if dynamodb_gen is None:
                dynamodb_gen = make_dynamodb_gen()
            os.system('clear')
            print_time()
            print 'Pulling current traffic data...'
            dynamodb_gen.next()
            sleep_min()
        if not dynamodb_gen is None:
            upload_data_s3()
            dynamodb_gen = None
        print_time()
        print 'Not monitoring traffic conditions...'
        sleep_min()


if __name__ == '__main__':
    commute_hours()
