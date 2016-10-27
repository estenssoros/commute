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
import matplotlib.pyplot as plt
plt.style.use('ggplot')


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


def accu_api():
    url = 'http://dataservice.accuweather.com/currentconditions/v1/347810?apikey={0}&details=true'
    try:
        resp = requests.get(url.format(os.environ['ACCU_WEATHER_KEY'])).json()[0]
        data = parse_accu_json(resp)
    except Exception as e:
        print 'Accuweather offline...'
        data = dict()
    return data


def get_accu_weather():
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


def get_data():
    accu_gen = get_accu_weather()
    while True:
        data = {'time': time.time()}
        data.update(get_dm())
        data.update(get_sun())
        data.update(accu_gen.next())
        yield data


def insert_dynamodb():
    data_gen = get_data()
    conn = boto.dynamodb.connect_to_region(
        'us-east-1', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    table = conn.get_table('commute')
    while True:
        data = data_gen.next()
        item = table.new_item(attrs=data)
        item.put()
        print 'Uploaded to dynamodb!'
        yield


def commute_hours():
    dynamodb_gen = None
    while True:
        os.system('clear')
        while test_time():
            if dynamodb_gen is None:
                dynamodb_gen = insert_dynamodb()
            os.system('clear')
            print_time()
            print 'Pulling current traffic data...'
            dynamodb_gen.next()
            sleep_min()
        if not dynamodb_gen is None:
            dynamodb_gen = None
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


def morning_afternoon(t):
    if t.hour < 12:
        return 'm'
    else:
        return 'a'


def make_df():
    conn = boto.dynamodb.connect_to_region(
        'us-east-1', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    table = conn.get_table('commute')
    df = pd.DataFrame()
    for i in table.scan():
        df = df.append(i, ignore_index=True)
    df['time'] = df.apply(lambda x:  dt.datetime.fromtimestamp(x['time']), axis=1)
    df['month_day'] = df.apply(lambda x: '{0}_{1}'.format(x['time'].month, x['time'].day), axis=1)
    df['m/a'] = df.apply(lambda x: morning_afternoon(x['time']), axis=1)
    return df


def graph():
    df = make_df()
    print 'gathered df'
    df.set_index('time', inplace=True)
    month_days = pd.unique(df['month_day'])
    for month_day in month_days:

        new_df = df[df['month_day'] == month_day]
        morning_df = new_df[new_df['m/a'] == 'm']
        afternoon_df = new_df[new_df['m/a'] == 'a']
        if len(morning_df) > 0 and len(afternoon_df) > 0:
            fig, axs = plt.subplots(2, 1)
            morning_df[['duration']].plot(ax=axs[0])
            afternoon_df[['duration']].plot(ax=axs[1])
            plt.title(month_day)
            plt.show()

if __name__ == '__main__':
    commute_hours()
    # pass
