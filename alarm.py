import datetime as dt
import json
import os
import re
import sys
import time

import googlemaps
import MySQLdb
import pytz
from twilio.rest import Client

address_book = {
    'seb': '13032299207',
}


def twilio_message(to, msg):
    account_sid = os.environ['TWILIO_ACT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)
    message = client.messages.create(to=to, from_='17206139570', body=msg)
    print message.sid


def distance_matrix_api(**kwargs):
    gmaps = googlemaps.Client(key=os.environ['GMAPS_API_KEY'])
    args = {'mode': 'driving',
            'units': 'imperial',
            'departure_time': dt.datetime.today(),
            'traffic_model': 'best_guess',
            'avoid': 'tolls',
            'origins': kwargs['origin'],
            'destinations': kwargs['destination']}
    response = gmaps.distance_matrix(**args)
    elements = response['rows'][0]['elements'][0]
    duration = elements['duration_in_traffic']['value']
    distance = elements['distance']['value']
    traffic = duration - elements['duration']['value']
    data = {'distance': distance,
            'duration': duration,
            'origin': kwargs['origin'],
            'destination': kwargs['destination'],
            'traffic': traffic}
    return data


def seconds_to_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


def check_arrival_time(**kwargs):
    dm = distance_matrix_api(**kwargs)
    now = dt.datetime.utcnow() - dt.timedelta(hours=6)
    arrival = now + dt.timedelta(seconds=dm['duration'])
    repeat = True
    if arrival >= kwargs['arrival_time']:
        msg = arrival.strftime('Depart now to arrive at: %-I:%M:%S %p\n\n')
        msg += 'origin: {}\n'.format(dm['origin'])
        msg += 'destination: {}'.format(dm['destination'])
        if dm['traffic'] > 5 * 60:
            traffic_time = seconds_to_time(dm['traffic'])
            msg += '\nTraffic: {}'.format(traffic_time)
        twilio_message(address_book['me'], msg)
        repeat = False
    else:
        print arrival.strftime('Current arrival time: %-I:%M:%S %p')
    return repeat


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


def main():
    commute_pair = get_commute_pair()
    commute_pair['arrival_time'] = string_to_datetime(commute_pair['arrival_time'])
    while check_arrival_time(**commute_pair):
        time.sleep(60)


if __name__ == '__main__':
    main()
