from __future__ import division
import googlemaps
import boto.dynamodb
import os
import re
import time
import datetime as dt
from astral import Astral
import requests
from time_functions import *
from parsers import *
import pandas as pd

def get_to_from():
    add_dict = {'home': '2665 Garfield Cir, Denver, CO 80210, USA',
                'work': '1800 Larimer St, Denver, CO 80202, USA'}
    if dt.datetime.today().hour < 12:
        return add_dict['home'], add_dict['work']
    else:
        return add_dict['work'], add_dict['home']


def get_dm():
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
    data = {'distance': distance['value'], 'duration': duration['value']}
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
    url = 'http://dataservice.accuweather.com/currentconditions/v1/347810?apikey={0}&details=true'
    resp = requests.get(url.format(os.environ['ACCU_WEATHER_KEY'])).json()[0]
    return parse_accu_json(resp)


def get_data():
    data = {'time': time.time()}
    data.update(get_dm())
    data.update(get_sun())
    data.update(get_accu_weather())
    return data


def insert_dynamodb():
    data = get_data()
    conn = boto.dynamodb.connect_to_region(
        'us-east-1', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    table = conn.get_table('commute')
    item = table.new_item(attrs=data)
    item.put()
    print 'Uploaded to dynamodb!'


def commute_hours():
    while True:
        os.system('clear')
        while test_time():

            os.system('clear')
            print_time()
            print 'Pulling current traffic data...'
            insert_dynamodb()
            sleep_min()

        print_time()
        print 'Not monitoring traffic conditions...'
        sleep_min()


def all_hours():
    while True:
        os.system('clear')
        print_time()
        print 'Pulling current traffic data...'
        insert_dynamodb()
        sleep_min()


def make_df():
    conn = boto.dynamodb.connect_to_region(
        'us-east-1', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    table = conn.get_table('commute')
    df = pd.DataFrame()
    for i in table.scan():
        df = df.append(i, ignore_index=True)
    return df

if __name__ == '__main__':
    commute_hours()
