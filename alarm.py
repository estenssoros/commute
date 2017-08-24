import datetime as dt
import json
import os
import re
import sys
import time
import urllib

import googlemaps
import MySQLdb
import pytz
import requests
from tabulate import tabulate
from twilio.rest import Client

address_book = {
    'me': '13032299207',
}

GMAPS_API_KEY = os.environ['GMAPS_API_KEY']


def twilio_message(to, msg):
    account_sid = os.environ['TWILIO_ACT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)
    message = client.messages.create(to=to, from_='17206139570', body=msg)
    print message.sid


def distance_matrix_api(**kwargs):
    gmaps = googlemaps.Client(key=GMAPS_API_KEY)
    args = {'mode': 'driving',
            'units': 'imperial',
            'departure_time': dt.datetime.today(),
            'traffic_model': 'best_guess',
            'avoid': 'tolls',
            'origins': kwargs['origin'],
            'destinations': kwargs['destination']}
    response = gmaps.distance_matrix(**args)
    while response['status'] != 'OK':
        print 'bad response: {}'.format(response)
        time.sleep(1)
        response = gmaps.distance_matrix(**args)
    elements = response['rows'][0]['elements'][0]
    if elements.get('duration_in_traffic'):
        duration = elements['duration_in_traffic']['value']
    else:
        duration = 0
    distance = elements['distance']['value']
    traffic = duration - elements['duration']['value']
    data = {'distance': distance,
            'duration': duration,
            'origin': kwargs['origin'],
            'destination': kwargs['destination'],
            'traffic': traffic}
    return data


def create_url(**kwargs):
    dir_url = 'https://www.google.com/maps/dir/?api=1&'
    to_encode = {'origin': kwargs['origin'], 'destination': kwargs['destination']}
    url = dir_url + urllib.urlencode(to_encode)
    return url


def shorten_url(url):
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key={}'.format(GMAPS_API_KEY)
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    return r.json()


def seconds_to_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


def check_arrival_time(**kwargs):
    dm = distance_matrix_api(**kwargs)
    now = dt.datetime.utcnow()
    arrival = now + dt.timedelta(seconds=dm['duration'])
    if arrival >= kwargs['arrival_time']:
        msg_time = arrival - dt.timedelta(hours=6)
        msg = msg_time.strftime('Depart now to arrive at: %-I:%M:%S %p\n\n')
        if dm['traffic'] > 5 * 60:
            traffic_time = seconds_to_time(dm['traffic'])
            msg += 'Traffic: {}\n'.format(traffic_time)
        msg += kwargs['short_url']
        twilio_message(address_book['me'], msg)
        return False
    return True


time_re = re.compile(r'(?P<hour>[0-9]+):(?P<minute>[0-9]+)')


def string_to_datetime(s):
    '''
    converts mountains time time string to utc now time string
    '''
    t_dict = [m.groupdict() for m in time_re.finditer(s)][0]
    t_dict = {k: int(t_dict[k]) for k in t_dict}
    t_dict['hour'] += 6
    now = dt.datetime.utcnow()
    return dt.datetime(now.year, now.month, now.day, **t_dict)


def get_commute_pair():
    keys = ('host', 'user', 'passwd')
    db_conn = {k: os.environ[k] for k in keys}
    db_conn['db'] = 'commute'
    conn = MySQLdb.connect(**db_conn)
    curs = conn.cursor()
    curs.execute('SELECT * FROM commute_pair LIMIT 1')
    desc = [x[0] for x in curs.description]
    res = dict(zip(desc, curs.fetchone()))
    curs.close()
    conn.close()
    return res


def lookup_address(add):
    gmaps = googlemaps.Client(key=GMAPS_API_KEY)
    resp = gmaps.geocode(add)
    return respo[0]['formatted_address']


def main():
    commute_pair = get_commute_pair()
    commute_url = create_url(**commute_pair)
    commute_pair['short_url'] = shorten_url(commute_url)['id']
    commute_pair['arrival_time'] = string_to_datetime(commute_pair['arrival_time'])
    while check_arrival_time(**commute_pair):
        time.sleep(60)


if __name__ == '__main__':
    main()
